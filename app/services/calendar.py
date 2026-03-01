# -*- coding: utf-8 -*-
"""公历与农历日期双向转换。"""

from typing import Optional, Any

try:
    import sxtwl
except ImportError:
    sxtwl = None

# 农历月、日中文名（与 sxtwl 文档一致）
YMC = ["十一", "十二", "正", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
RMC = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十", "卅一",
]
SHX = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]


def _get_lunar(day_obj: Any) -> Optional[tuple]:
    """从 sxtwl 日对象取农历 (年, 月, 日, 是否闰月)。农历年以春节为界。"""
    get_ly = getattr(day_obj, "getLunarYear", None) or getattr(day_obj, "get_lunar_year", None)
    get_lm = getattr(day_obj, "getLunarMonth", None) or getattr(day_obj, "get_lunar_month", None)
    get_ld = getattr(day_obj, "getLunarDay", None) or getattr(day_obj, "get_lunar_day", None)
    is_leap = getattr(day_obj, "isLunarLeap", None) or getattr(day_obj, "is_lunar_leap", None)
    if not all(callable(x) for x in (get_ly, get_lm, get_ld)):
        return None
    try:
        try:
            ly = get_ly(True)
        except TypeError:
            ly = get_ly()
        lm = get_lm()
        ld = get_ld()
        leap = is_leap() if is_leap and callable(is_leap) else False
        return (ly, lm, ld, leap)
    except Exception:
        return None


def _get_solar(day_obj: Any) -> Optional[tuple]:
    """从 sxtwl 日对象取公历 (年, 月, 日)。"""
    get_sy = getattr(day_obj, "getSolarYear", None) or getattr(day_obj, "get_solar_year", None)
    get_sm = getattr(day_obj, "getSolarMonth", None) or getattr(day_obj, "get_solar_month", None)
    get_sd = getattr(day_obj, "getSolarDay", None) or getattr(day_obj, "get_solar_day", None)
    if not all(callable(x) for x in (get_sy, get_sm, get_sd)):
        return None
    try:
        return (get_sy(), get_sm(), get_sd())
    except Exception:
        return None


def _lunar_month_cn(month: int) -> str:
    """农历月份数字转中文（正月、二月…十二月）。"""
    if 1 <= month <= 12:
        return YMC[(month + 1) % 12] + "月"
    return str(month) + "月"


def _lunar_day_cn(day: int) -> str:
    """农历日 1–31 转中文。"""
    if 1 <= day <= 31:
        return RMC[day - 1]
    return str(day)


def _shengxiao(year: int) -> str:
    """公历年份对应生肖（以春节为界需农历年，这里用公历近似；更准可用日对象 getYearGZ(True).dz）。"""
    # 1900 鼠年，地支 0 子鼠
    base = 1900
    idx = (year - base) % 12
    return SHX[idx]


class CalendarService:
    """公历与农历转换服务。"""

    def __init__(self) -> None:
        self._sxtwl = sxtwl

    def solar2lunar(self, year: int, month: int, day: int) -> dict:
        """
        公历 -> 农历。
        返回：公历日期、农历年月日、是否闰月、农历中文表示、生肖等。
        """
        if not self._sxtwl:
            return {"error": "未安装 sxtwl，请执行: pip install sxtwl"}
        try:
            day_obj = sxtwl.fromSolar(year, month, day)
        except Exception:
            return {"error": "日期无效或超出支持范围"}
        lunar = _get_lunar(day_obj)
        if not lunar:
            return {"error": "无法获取农历信息"}
        ly, lm, ld, leap = lunar
        solar = _get_solar(day_obj)
        solar_str = f"{solar[0]}年{solar[1]}月{solar[2]}日" if solar else f"{year}年{month}月{day}日"
        leap_str = "闰" if leap else ""
        lunar_cn = f"农历{ly}年{leap_str}{_lunar_month_cn(lm)}{_lunar_day_cn(ld)}"
        # 生肖以农历年为标准更准确，这里用农历年
        sx = _shengxiao(ly) if ly else ""
        return {
            "公历": solar_str,
            "公历数字": {"年": year, "月": month, "日": day},
            "农历数字": {"年": ly, "月": lm, "日": ld, "闰月": leap},
            "农历": lunar_cn,
            "农历简短": f"{ly}年{leap_str}{lm}月{ld}日",
            "生肖": sx,
        }

    def lunar2solar(
        self,
        lunar_year: int,
        lunar_month: int,
        lunar_day: int,
        is_leap_month: bool = False,
    ) -> dict:
        """
        农历 -> 公历。
        is_leap_month: 是否为闰月（如闰四月）。
        """
        if not self._sxtwl:
            return {"error": "未安装 sxtwl，请执行: pip install sxtwl"}
        try:
            day_obj = sxtwl.fromLunar(lunar_year, lunar_month, lunar_day, is_leap_month)
        except Exception as e:
            try:
                day_obj = sxtwl.fromLunar(lunar_year, lunar_month, lunar_day)
            except Exception:
                return {"error": f"农历日期无效或超出范围: {e}"}
        solar = _get_solar(day_obj)
        if not solar:
            return {"error": "无法得到公历日期"}
        sy, sm, sd = solar
        lunar_cn = f"农历{lunar_year}年{'闰' if is_leap_month else ''}{_lunar_month_cn(lunar_month)}{_lunar_day_cn(lunar_day)}"
        return {
            "农历": lunar_cn,
            "农历数字": {"年": lunar_year, "月": lunar_month, "日": lunar_day, "闰月": is_leap_month},
            "公历": f"{sy}年{sm}月{sd}日",
            "公历数字": {"年": sy, "月": sm, "日": sd},
        }


calendar_service = CalendarService()
