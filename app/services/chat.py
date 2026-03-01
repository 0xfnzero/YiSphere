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


def _extract_date(text: str) -> Optional[tuple]:
    """从文本中提取公历日期 (year, month, day)。支持 2020年1月1日、2020-01-01、2020.1.1。"""
    m = re.search(r"(\d{4})[年\-/.](\d{1,2})[月\-/.](\d{1,2})", text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1900 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 31:
            return (y, mo, d)
    return None


def _extract_hour(text: str) -> Optional[int]:
    """提取时辰或小时 0-23。支持 13点、13时、13:30、13：30。"""
    m = re.search(r"(\d{1,2})\s*[点时:：]\s*\d{0,2}", text)
    if m:
        h = int(m.group(1))
        if 0 <= h <= 23:
            return h
    return None


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
    m = re.search(r"农历\s*(?:生日)?\s*(\d{4})[年\-/.](\d{1,2})[月\-/.](\d{1,2})", text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        leap = bool(re.search(r"闰\s*\d*月", text))
        if 1900 <= y <= 2100 and 1 <= mo <= 12 and 1 <= d <= 30:
            return (y, mo, d, leap)
    return None


def _gather_tool_results(last_user_message: str) -> str:
    """
    根据最后一条用户消息，自动调用八字/黄历/起卦/公历农历转换，并返回要注入的上下文。
    用户给农历生日则按农历直接排八字；给公历则按公历排八字并附带农历对照。四柱均由程序计算，禁止 AI 自算。
    """
    ctx_parts: List[str] = []
    date = _extract_date(last_user_message)
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
    if event and date:
        import datetime
        y, mo, d = date
        start = datetime.date(y, mo, d)
        end = start + datetime.timedelta(days=90)
        try:
            days = huangli_service.select_auspicious_days(start, end, event, max_days=15)
            if days and "error" not in days[0]:
                ctx_parts.append(build_tools_context(huangli_result={"事宜": event, "推荐吉日": days}))
        except Exception:
            pass
    elif event:
        # 没给日期则查近期一个月
        import datetime
        today = datetime.date.today()
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

    async def reply(
        self,
        messages: List[Dict[str, str]],
        inject_tools: bool = True,
        master_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        根据历史消息回复。master_id 为角色 id，缺省为神算子。
        """
        if not self._client:
            return {
                "content": "请配置 OPENAI_API_KEY 后重试。可在项目根目录 .env 中设置。",
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
            r = await self._client.chat.completions.create(
                model=self._model,
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
    ):
        """
        流式回复：异步生成 content 片段。master_id 为角色 id。
        """
        if not self._client:
            yield {"content": "请配置 OPENAI_API_KEY 后重试。可在项目根目录 .env 中设置。", "done": True}
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
            stream = await self._client.chat.completions.create(
                model=self._model,
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


chat_service = ChatService()
