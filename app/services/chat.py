# -*- coding: utf-8 -*-
"""AI 对话服务：结合八字、黄历、易经等工具结果进行多轮对话。"""

import datetime
import os
import re
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from app.prompts import get_system_prompt, build_tools_context
from app.services.bazi import bazi_service
from app.services.huangli import huangli_service
from app.services.iching import iching_service
from app.services.calendar import calendar_service


def _extract_date(text: str, today: Optional[datetime.date] = None) -> Optional[tuple]:
    """
    从文本中提取公历日期 (year, month, day)。
    支持 2020年1月1日、2020 年 1 月 1 日、2020-01-01、今天/明天/后天。
    """
    today = today or datetime.date.today()
    if re.search(r"今天|今日", text):
        return (today.year, today.month, today.day)
    if "明天" in text or "明日" in text:
        target = today + datetime.timedelta(days=1)
        return (target.year, target.month, target.day)
    if "后天" in text:
        target = today + datetime.timedelta(days=2)
        return (target.year, target.month, target.day)

    m = re.search(r"(\d{4})\s*[年\-/.]\s*(\d{1,2})\s*[月\-/.]\s*(\d{1,2})\s*(?:日|号)?", text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _valid_date(y, mo, d):
            return (y, mo, d)
    return None


def _extract_hour(text: str) -> Optional[int]:
    """提取时辰或小时 0-23。支持 13点、13:30、上午10点、下午3时、晚上8点。"""
    m = re.search(r"(凌晨|早上|上午|中午|下午|傍晚|晚上|晚间)?\s*(\d{1,2})\s*(?:点|时|:|：)\s*\d{0,2}", text)
    if m:
        period = m.group(1) or ""
        h = int(m.group(2))
        if period in ("下午", "傍晚", "晚上", "晚间") and 1 <= h <= 11:
            h += 12
        if period == "中午" and h == 12:
            h = 12
        if 0 <= h <= 23:
            return h
    return None


def _valid_date(year: int, month: int, day: int) -> bool:
    try:
        datetime.date(year, month, day)
    except ValueError:
        return False
    return 1900 <= year <= 2100


def _extract_date_range(text: str, today: Optional[datetime.date] = None) -> Optional[tuple[datetime.date, datetime.date]]:
    """提取择日用日期范围。"""
    today = today or datetime.date.today()
    dates = re.findall(
        r"(\d{4})\s*[年\-/.]\s*(\d{1,2})\s*[月\-/.]\s*(\d{1,2})\s*(?:日|号)?",
        text,
    )
    parsed: list[datetime.date] = []
    for y, mo, d in dates[:2]:
        yi, mi, di = int(y), int(mo), int(d)
        if _valid_date(yi, mi, di):
            parsed.append(datetime.date(yi, mi, di))
    if len(parsed) >= 2:
        start, end = parsed[0], parsed[1]
        return (start, end) if start <= end else (end, start)
    if len(parsed) == 1:
        start = parsed[0]
        return (start, start + datetime.timedelta(days=90))

    if re.search(r"下周|下星期|下个星期", text):
        days_until_next_monday = 7 - today.weekday()
        start = today + datetime.timedelta(days=days_until_next_monday)
        return (start, start + datetime.timedelta(days=6))
    if re.search(r"本周|这周|这个星期", text):
        start = today - datetime.timedelta(days=today.weekday())
        return (max(start, today), start + datetime.timedelta(days=6))
    if re.search(r"下个月|下月", text):
        year = today.year + (1 if today.month == 12 else 0)
        month = 1 if today.month == 12 else today.month + 1
        start = datetime.date(year, month, 1)
        end = _month_end(year, month)
        return (start, end)
    if re.search(r"本月|这个月|这月", text):
        start = max(today, datetime.date(today.year, today.month, 1))
        return (start, _month_end(today.year, today.month))

    m = re.search(r"(?:(\d{4})\s*年\s*)?(\d{1,2})\s*月", text)
    if m:
        year = int(m.group(1)) if m.group(1) else today.year
        month = int(m.group(2))
        if 1900 <= year <= 2100 and 1 <= month <= 12:
            start = datetime.date(year, month, 1)
            if year == today.year and month == today.month:
                start = max(start, today)
            return (start, _month_end(year, month))
    return None


def _month_end(year: int, month: int) -> datetime.date:
    if month == 12:
        return datetime.date(year, 12, 31)
    return datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)


def _detect_huangli_event(text: str) -> Optional[str]:
    """检测用户是否在问黄道吉日及事宜类型。"""
    text = text.strip()
    if not re.search(r"吉日|黄道|择日|选日|哪天好|什么时候好|宜不宜", text):
        return None
    if re.search(r"结婚|婚嫁|嫁娶|领证|办酒|婚礼", text):
        return "婚嫁"
    if re.search(r"订婚|纳采|提亲", text):
        return "订婚"
    if re.search(r"开业|开张|开市", text):
        return "开业"
    if re.search(r"搬家|入宅|乔迁|移徙", text):
        return "入宅"
    if re.search(r"动土|装修|修造", text):
        return "动土"
    if re.search(r"安葬|下葬", text):
        return "安葬"
    if re.search(r"出行|出门|远行", text):
        return "出行"
    if re.search(r"祭祀|祭祖", text):
        return "祭祀"
    if re.search(r"求嗣|求子|安床", text):
        return "求嗣"
    return "嫁娶"  # 默认常见


def _get_current_liunian_ref() -> Optional[str]:
    """获取当前公历日期与今年流年（岁干支），供谈及「今年」运势时使用，避免 AI 说错年份。"""
    today = datetime.date.today()
    bazi_today = bazi_service.get_si_zhu(today.year, today.month, today.day)
    if "error" in bazi_today:
        return None
    liunian = bazi_today.get("year")
    if not liunian:
        return None
    return f"今日公历{today.year}年{today.month}月{today.day}日，今年流年（岁干支）为{liunian}。"


def _extract_lunar_date(text: str) -> Optional[tuple]:
    """从文本中提取农历日期 (年, 月, 日, 是否闰月)。支持：农历1990年3月24日、农历生日1988.3.24。"""
    # 农历 / 农历生日 + 1988年3月24日 或 1988.3.24
    if not re.search(r"农历", text):
        return None
    m = re.search(r"农历\s*(?:生日)?\s*(\d{4})\s*[年\-/.]\s*(闰)?\s*(\d{1,2})\s*[月\-/.]\s*(\d{1,2})", text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(3)), int(m.group(4))
        leap = bool(m.group(2) or re.search(r"闰\s*\d*月", text))
        if 1900 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 30:
            return (y, mo, d, leap)
    return None


def _gather_tool_results(last_user_message: str) -> str:
    """
    根据最后一条用户消息，自动调用八字/黄历/起卦/公历农历转换，并返回要注入的上下文。
    用户给农历生日则按农历直接排八字；给公历则按公历排八字并附带农历对照。四柱均由程序计算，禁止 AI 自算。
    """
    ctx_parts: List[str] = []
    today = datetime.date.today()
    date = _extract_date(last_user_message, today)
    lunar_date = _extract_lunar_date(last_user_message)
    hour = _extract_hour(last_user_message)
    ask_bazi = bool(re.search(r"八字|取名|名字|命理|运势|生辰|出生|宝宝|孩子", last_user_message))
    ask_gua = bool(re.search(r"占|卦|起卦|算一卦|摇一卦|易经", last_user_message))

    # 1) 公历 -> 农历：用户明确问「农历生日/身份证日期对应农历/公历转农历」
    if date and re.search(r"农历生日|身份证|公历.*农历|阳历.*农历|转农历|换成农历|对应农历", last_user_message):
        y, mo, d = date
        cal = calendar_service.solar2lunar(y, mo, d)
        if "error" not in cal:
            ctx_parts.append(build_tools_context(calendar_result=cal))

    # 2) 农历 -> 公历：用户说「农历某年某月某日 公历是哪天」
    if lunar_date and re.search(r"公历|阳历|公历哪天|阳历是哪", last_user_message):
        ly, lm, ld, leap = lunar_date
        cal = calendar_service.lunar2solar(ly, lm, ld, leap)
        if "error" not in cal:
            ctx_parts.append(build_tools_context(calendar_result=cal))

    # 3) 八字（农历直接排盘）：用户给农历生日时，按农历直接排四柱（传统以农历排八字更常用）
    bazi_injected = False
    if lunar_date and ask_bazi:
        ly, lm, ld, leap = lunar_date
        bazi = bazi_service.get_si_zhu_from_lunar(ly, lm, ld, leap, hour)
        if "error" not in bazi:
            bazi_injected = True
            cal = calendar_service.lunar2solar(ly, lm, ld, leap)
            current_ref = _get_current_liunian_ref()
            ctx_parts.append(build_tools_context(
                calendar_result=cal if "error" not in cal else None,
                bazi_result=bazi,
                current_ref=current_ref,
            ))
        if ask_gua and not any("已起的卦象" in p for p in ctx_parts):
            gua = iching_service.draw_random()
            ctx_parts.append(build_tools_context(iching_result=gua))

    # 4) 八字（公历）：用户给的是公历日期且未在上一步注入八字
    if not bazi_injected and date and ask_bazi:
        y, mo, d = date
        cal = calendar_service.solar2lunar(y, mo, d)
        bazi = bazi_service.get_si_zhu(y, mo, d, hour)
        if "error" not in bazi or "error" not in cal:
            current_ref = _get_current_liunian_ref()
            ctx_parts.append(build_tools_context(
                calendar_result=cal if "error" not in cal else None,
                bazi_result=bazi if "error" not in bazi else None,
                current_ref=current_ref,
            ))
        if ask_gua and not any("已起的卦象" in p for p in ctx_parts):
            gua = iching_service.draw_random()
            ctx_parts.append(build_tools_context(iching_result=gua))

    # 黄道吉日：问某类事宜的吉日
    event = _detect_huangli_event(last_user_message)
    date_range = _extract_date_range(last_user_message, today)
    if event and date_range:
        start, end = date_range
        try:
            days = huangli_service.select_auspicious_days(start, end, event, max_days=15)
            if days and "error" not in days[0]:
                ctx_parts.append(build_tools_context(huangli_result={
                    "事宜": event,
                    "筛选范围": f"{start.isoformat()} 至 {end.isoformat()}",
                    "推荐吉日": days,
                }))
        except Exception:
            pass
    elif event:
        # 没给日期则查近期一个月
        start = today
        end = today + datetime.timedelta(days=60)
        try:
            days = huangli_service.select_auspicious_days(start, end, event, max_days=15)
            if days and "error" not in days[0]:
                ctx_parts.append(build_tools_context(huangli_result={"事宜": event, "推荐吉日": days}))
        except Exception:
            pass

    # 查某日宜忌（今日、明天、或具体日期）；同时注入该日公历→农历，便于说明「该日农历为…」
    if date and re.search(r"宜忌|宜什么|忌什么|这天怎么样|那天好不好", last_user_message):
        y, mo, d = date
        cal = calendar_service.solar2lunar(y, mo, d)
        try:
            day_info = huangli_service.get_day_info(y, mo, d)
            if "error" not in day_info or "error" not in cal:
                ctx_parts.append(build_tools_context(
                    calendar_result=cal if "error" not in cal else None,
                    huangli_result=day_info if "error" not in day_info else None,
                ))
        except Exception:
            if "error" not in cal:
                ctx_parts.append(build_tools_context(calendar_result=cal))

    # 六爻/起卦：仅当尚未在八字分支中注入卦象时
    if ask_gua and not any("已起的卦象" in p for p in ctx_parts):
        gua = iching_service.draw_random()
        ctx_parts.append(build_tools_context(iching_result=gua))

    return "\n\n".join(ctx_parts) if ctx_parts else ""


class ChatService:
    """对话服务。"""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url if base_url else None) if api_key else None
        self._model = os.getenv("OPENAI_MODEL", "deepseek-chat")
        self._api_key = api_key
        self._base_url = base_url

    async def reply(
        self,
        messages: List[Dict[str, str]],
        inject_tools: bool = True,
        master_id: Optional[str] = None,
        llm_config: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        根据历史消息回复。master_id 为角色 id，缺省为神算子。
        """
        client, model = self._resolve_llm(llm_config)
        if not client:
            return {
                "content": "请先配置 LLM API Key 后重试。可在右上角模型设置中填写，也可在项目根目录 .env 中设置 OPENAI_API_KEY。",
                "role": "assistant",
            }

        msgs = [{"role": m["role"], "content": m["content"]} for m in messages]
        last_user = next((m["content"] for m in reversed(msgs) if m["role"] == "user"), "")

        system = get_system_prompt(master_id)
        if inject_tools and last_user:
            extra = _gather_tool_results(last_user)
            if extra:
                system = system.rstrip() + "\n\n" + extra

        # 构造 API 消息：system + 历史
        api_messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
        for m in msgs:
            if m["role"] in ("user", "assistant"):
                api_messages.append({"role": m["role"], "content": m["content"]})

        try:
            r = await client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=0.7,
                max_tokens=2000,
            )
            choice = r.choices[0] if r.choices else None
            content = choice.message.content if choice else ""
            return {"content": content or "（暂无回复）", "role": "assistant"}
        except Exception as e:
            return {"content": f"调用模型时出错: {str(e)}", "role": "assistant"}

    async def reply_stream(
        self,
        messages: List[Dict[str, str]],
        inject_tools: bool = True,
        master_id: Optional[str] = None,
        llm_config: Optional[Dict[str, str]] = None,
    ):
        """
        流式回复：异步生成 content 片段。master_id 为角色 id。
        """
        client, model = self._resolve_llm(llm_config)
        if not client:
            yield {"content": "请先配置 LLM API Key 后重试。可在右上角模型设置中填写，也可在项目根目录 .env 中设置 OPENAI_API_KEY。", "done": True}
            return

        msgs = [{"role": m["role"], "content": m["content"]} for m in messages]
        last_user = next((m["content"] for m in reversed(msgs) if m["role"] == "user"), "")
        system = get_system_prompt(master_id)
        if inject_tools and last_user:
            extra = _gather_tool_results(last_user)
            if extra:
                system = system.rstrip() + "\n\n" + extra

        api_messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
        for m in msgs:
            if m["role"] in ("user", "assistant"):
                api_messages.append({"role": m["role"], "content": m["content"]})

        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True,
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if getattr(delta, "content", None):
                    yield {"content": delta.content, "done": False}
            yield {"content": "", "done": True}
        except Exception as e:
            yield {"content": f"调用模型时出错: {str(e)}", "done": True}

    def _resolve_llm(self, llm_config: Optional[Dict[str, str]]) -> tuple[Optional[AsyncOpenAI], str]:
        """按请求级配置选择 LLM；缺省回退到 .env。"""
        config = llm_config or {}
        api_key = (config.get("api_key") or config.get("apiKey") or self._api_key or "").strip()
        base_url = (config.get("base_url") or config.get("baseUrl") or self._base_url or "").strip()
        model = (config.get("model") or self._model or "deepseek-chat").strip()
        if not api_key:
            return None, model
        if (
            api_key == (self._api_key or "")
            and base_url == (self._base_url or "")
            and self._client
        ):
            return self._client, model
        return AsyncOpenAI(api_key=api_key, base_url=base_url or None), model


chat_service = ChatService()
