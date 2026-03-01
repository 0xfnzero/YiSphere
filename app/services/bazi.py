# -*- coding: utf-8 -*-
"""八字（四柱）计算服务，基于 sxtwl 获取年月日时干支。"""

from typing import Optional

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
            yg = get_year()
        except TypeError:
            yg = get_year(False)
        mg = get_month()
        dg = get_day()
        nian_zhu = f"{TIAN_GAN[yg.tg]}{DI_ZHI[yg.dz]}"
        yue_zhu = f"{TIAN_GAN[mg.tg]}{DI_ZHI[mg.dz]}"
        ri_zhu = f"{TIAN_GAN[dg.tg]}{DI_ZHI[dg.dz]}"

        if hour is not None and get_hour:
            hg = get_hour(hour)
            shi_zhu = f"{TIAN_GAN[hg.tg]}{DI_ZHI[hg.dz]}"
        else:
            shi_zhu = "未知"

        return {
            "year": nian_zhu,
            "month": yue_zhu,
            "day": ri_zhu,
            "hour": shi_zhu,
            "summary": f"年柱 {nian_zhu} 月柱 {yue_zhu} 日柱 {ri_zhu} 时柱 {shi_zhu}",
        }


bazi_service = BaziService()
