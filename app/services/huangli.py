# -*- coding: utf-8 -*-
"""黄历 / 黄道吉日服务：宜忌、吉神凶神、按事宜选吉日（婚嫁、开业、入宅等）。"""

import datetime
from typing import List, Optional, Any

try:
    import cnlunar
except ImportError:
    cnlunar = None

# 事宜类型 -> 黄历「宜」中对应的关键词（满足其一即视为该日适合）
EVENT_YI_KEYWORDS = {
    "婚嫁": ["嫁娶", "结婚", "婚嫁"],
    "嫁娶": ["嫁娶"],
    "订婚": ["纳采", "订婚"],
    "纳采": ["纳采"],
    "开业": ["开市", "开业", "开张"],
    "开市": ["开市"],
    "入宅": ["入宅", "移徙", "搬家"],
    "搬家": ["移徙", "入宅"],
    "移徙": ["移徙"],
    "动土": ["动土"],
    "安葬": ["安葬", "破土"],
    "出行": ["出行"],
    "祭祀": ["祭祀"],
    "求嗣": ["求嗣"],
    "装修": ["修造", "动土"],
    "修造": ["修造"],
    "安床": ["安床"],
    "嫁娶_纳采": ["嫁娶", "纳采"],
}


def _lunar_to_dict(a: Any) -> dict:
    """将 cnlunar.Lunar 对象转为可序列化的字典。"""
    if a is None:
        return {}
    good = getattr(a, "goodThing", None) or []
    bad = getattr(a, "badThing", None) or []
    if isinstance(good, str):
        good = [good] if good else []
    if isinstance(bad, str):
        bad = [bad] if bad else []
    return {
        "公历": getattr(a, "date", str(a)) if hasattr(a, "date") else None,
        "农历": getattr(a, "lunarYearCn", "") and f"{getattr(a, 'lunarYearCn', '')} {getattr(a, 'lunarMonthCn', '')} {getattr(a, 'lunarDayCn', '')}",
        "八字": " ".join([
            getattr(a, "year8Char", ""),
            getattr(a, "month8Char", ""),
            getattr(a, "day8Char", ""),
            getattr(a, "twohour8Char", ""),
        ]) if getattr(a, "year8Char", None) else None,
        "星期": getattr(a, "weekDayCn", None),
        "宜": good,
        "忌": bad,
        "今日吉神": getattr(a, "goodGodName", None),
        "今日凶煞": getattr(a, "badGodName", None),
        "宜忌等第": getattr(a, "todayLevelName", None),
        "十二建星": getattr(a, "get_today12DayOfficer", lambda: None)(),
        "彭祖百忌": getattr(a, "get_pengTaboo", lambda: None)(),
        "冲煞": getattr(a, "chineseZodiacClash", None),
    }


class HuangliService:
    """黄历 / 黄道吉日服务。"""

    def __init__(self) -> None:
        self._cnlunar = cnlunar

    def get_day_info(self, year: int, month: int, day: int, hour: int = 12) -> dict:
        """查询某日的黄历信息（宜忌、吉神凶神、八字等）。"""
        if not self._cnlunar:
            return {"error": "未安装 cnlunar，请执行: pip install cnlunar"}
        try:
            dt = datetime.datetime(year, month, day, hour)
            a = self._cnlunar.Lunar(dt, godType="8char")
            return _lunar_to_dict(a)
        except Exception as e:
            return {"error": f"日期无效或超出范围: {e}"}

    def _yi_contains_keywords(self, good_thing: Any, keywords: List[str]) -> bool:
        if not keywords:
            return False
        if isinstance(good_thing, str):
            good_thing = [good_thing] if good_thing else []
        good_str = " ".join(good_thing) if good_thing else ""
        return any(kw in good_str for kw in keywords)

    def select_auspicious_days(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        event_type: str,
        max_days: int = 30,
    ) -> List[dict]:
        """
        在日期范围内筛选适合某类事宜的黄道吉日。
        event_type: 婚嫁/嫁娶、开业/开市、入宅/搬家/移徙、动土、安葬、订婚/纳采、出行、祭祀、求嗣、装修/修造、安床 等。
        """
        if not self._cnlunar:
            return [{"error": "未安装 cnlunar，请执行: pip install cnlunar"}]
        keywords = EVENT_YI_KEYWORDS.get(event_type)
        if not keywords:
            # 尝试模糊匹配
            for k, v in EVENT_YI_KEYWORDS.items():
                if event_type in k or k in event_type:
                    keywords = v
                    break
        if not keywords:
            keywords = [event_type]
        result: List[dict] = []
        current = start_date
        while current <= end_date and len(result) < max_days:
            try:
                dt = datetime.datetime(current.year, current.month, current.day, 12)
                a = self._cnlunar.Lunar(dt, godType="8char")
                good = getattr(a, "goodThing", None) or []
                if self._yi_contains_keywords(good, keywords):
                    result.append({
                        "date": current.isoformat(),
                        "农历": f"{getattr(a, 'lunarYearCn', '')} {getattr(a, 'lunarMonthCn', '')} {getattr(a, 'lunarDayCn', '')}",
                        "星期": getattr(a, "weekDayCn", None),
                        "宜": good,
                    })
            except Exception:
                pass
            current += datetime.timedelta(days=1)
        return result


huangli_service = HuangliService()
