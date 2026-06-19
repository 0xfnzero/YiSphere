# -*- coding: utf-8 -*-
"""八字（四柱）计算服务，基于 sxtwl 获取年月日时干支。"""

from typing import Any, Optional

try:
    import sxtwl
except ImportError:
    sxtwl = None

# 天干、地支名称（与 sxtwl 文档一致）
TIAN_GAN = "甲乙丙丁戊己庚辛壬癸"
DI_ZHI = "子丑寅卯辰巳午未申酉戌亥"


def _get_gz_method(day_obj: "object", name: str):
    """兼容 sxtwl 的 getYearGZ / get_year_gz 两种命名。"""
    for method_name in (name, name.replace("GZ", "_gz").replace("Year", "year").replace("Month", "month").replace("Day", "day").replace("Hour", "hour")):
        m = getattr(day_obj, method_name, None)
        if callable(m):
            return m
    return None


def _gz_text(gz: Any) -> str:
    """将 sxtwl 的干支对象转为中文干支。"""
    return f"{TIAN_GAN[gz.tg]}{DI_ZHI[gz.dz]}"


def _validate_hour(hour: Optional[int]) -> Optional[str]:
    if hour is None:
        return None
    if not isinstance(hour, int) or not 0 <= hour <= 23:
        return "hour 必须是 0-23 的整数"
    return None


class BaziService:
    """八字计算服务。"""

    def get_si_zhu(
        self,
        year: int,
        month: int,
        day: int,
        hour: Optional[int] = None,
    ) -> dict:
        """
        根据公历年月日（及时辰）计算四柱八字。
        hour: 0-23，不传则只返回年月日三柱（时柱用「未知」表示）。
        """
        if not sxtwl:
            return {"error": "未安装 sxtwl，请执行: pip install sxtwl"}
        hour_error = _validate_hour(hour)
        if hour_error:
            return {"error": hour_error}
        try:
            day_obj = sxtwl.fromSolar(year, month, day)
        except Exception:
            return {"error": "日期无效或超出支持范围"}

        get_year = _get_gz_method(day_obj, "getYearGZ") or getattr(day_obj, "get_year_gz", None)
        get_month = _get_gz_method(day_obj, "getMonthGZ") or getattr(day_obj, "get_month_gz", None)
        get_day = _get_gz_method(day_obj, "getDayGZ") or getattr(day_obj, "get_day_gz", None)
        get_hour = _get_gz_method(day_obj, "getHourGZ") or getattr(day_obj, "get_hour_gz", None)

        if not all([get_year, get_month, get_day]):
            return {"error": "当前 sxtwl 版本不支持干支方法"}

        try:
            yg = get_year(False)
        except TypeError:
            yg = get_year()
        mg = get_month()
        dg = get_day()
        nian_zhu = _gz_text(yg)
        yue_zhu = _gz_text(mg)
        ri_zhu = _gz_text(dg)

        shi_zhu = "未知"
        if hour is not None:
            if not get_hour:
                return {"error": "当前 sxtwl 版本不支持时柱方法"}
            hg = get_hour(hour)
            shi_zhu = _gz_text(hg)

        return {
            "input": {"calendar": "solar", "year": year, "month": month, "day": day, "hour": hour},
            "year": nian_zhu,
            "month": yue_zhu,
            "day": ri_zhu,
            "hour": shi_zhu,
            "summary": f"年柱 {nian_zhu} 月柱 {yue_zhu} 日柱 {ri_zhu} 时柱 {shi_zhu}",
            "note": "年柱按节气年（立春）取法；时柱按 sxtwl 默认子时规则计算。",
        }

    def get_si_zhu_from_lunar(
        self,
        lunar_year: int,
        lunar_month: int,
        lunar_day: int,
        is_leap_month: bool = False,
        hour: Optional[int] = None,
    ) -> dict:
        """
        按农历年月日（及时辰）直接排四柱八字，不经过公历。
        传统以农历排盘更符合习惯；库内部仍对应到同一日再取干支。
        """
        if not sxtwl:
            return {"error": "未安装 sxtwl，请执行: pip install sxtwl"}
        hour_error = _validate_hour(hour)
        if hour_error:
            return {"error": hour_error}
        try:
            day_obj = sxtwl.fromLunar(lunar_year, lunar_month, lunar_day, is_leap_month)
        except Exception:
            return {"error": "农历日期无效或超出支持范围"}

        is_leap = getattr(day_obj, "isLunarLeap", None) or getattr(day_obj, "is_lunar_leap", None)
        if callable(is_leap):
            try:
                actual_leap = bool(is_leap())
                if actual_leap != bool(is_leap_month):
                    return {"error": "该农历日期的闰月标记不匹配，请确认是否为闰月"}
            except Exception:
                pass

        get_year = _get_gz_method(day_obj, "getYearGZ") or getattr(day_obj, "get_year_gz", None)
        get_month = _get_gz_method(day_obj, "getMonthGZ") or getattr(day_obj, "get_month_gz", None)
        get_day = _get_gz_method(day_obj, "getDayGZ") or getattr(day_obj, "get_day_gz", None)
        get_hour = _get_gz_method(day_obj, "getHourGZ") or getattr(day_obj, "get_hour_gz", None)

        if not all([get_year, get_month, get_day]):
            return {"error": "当前 sxtwl 版本不支持干支方法"}

        try:
            yg = get_year(False)
        except TypeError:
            yg = get_year()
        mg = get_month()
        dg = get_day()
        nian_zhu = _gz_text(yg)
        yue_zhu = _gz_text(mg)
        ri_zhu = _gz_text(dg)

        shi_zhu = "未知"
        if hour is not None:
            if not get_hour:
                return {"error": "当前 sxtwl 版本不支持时柱方法"}
            hg = get_hour(hour)
            shi_zhu = _gz_text(hg)

        return {
            "input": {"calendar": "lunar", "year": lunar_year, "month": lunar_month, "day": lunar_day, "is_leap_month": is_leap_month, "hour": hour},
            "year": nian_zhu,
            "month": yue_zhu,
            "day": ri_zhu,
            "hour": shi_zhu,
            "summary": f"年柱 {nian_zhu} 月柱 {yue_zhu} 日柱 {ri_zhu} 时柱 {shi_zhu}",
            "from_lunar": True,
            "note": "年柱按节气年（立春）取法；时柱按 sxtwl 默认子时规则计算。",
        }


bazi_service = BaziService()
