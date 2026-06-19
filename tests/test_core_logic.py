import datetime
import unittest

from app.services.chat import _extract_date, _extract_date_range, _extract_hour, _extract_lunar_date
from app.services.iching import ICHING_64, IchingService


class IchingServiceTest(unittest.TestCase):
    def test_hexagrams_match_full_names(self):
        trigram_bits = {
            "天": "111",
            "泽": "011",
            "火": "101",
            "雷": "001",
            "风": "110",
            "水": "010",
            "山": "100",
            "地": "000",
            "乾": "111",
            "兑": "011",
            "离": "101",
            "震": "001",
            "巽": "110",
            "坎": "010",
            "艮": "100",
            "坤": "000",
        }
        for gua in ICHING_64:
            if "为" in gua["full"]:
                expected = trigram_bits[gua["full"][0]] * 2
            else:
                expected = trigram_bits[gua["full"][0]] + trigram_bits[gua["full"][1]]
            self.assertEqual(gua["hex"], expected, gua["full"])

    def test_draw_by_lines_returns_primary_moving_and_changed_hexagram(self):
        service = IchingService()
        result = service.draw_by_lines([9, 7, 7, 7, 7, 7])

        self.assertEqual(result["primary"]["full"], "乾为天")
        self.assertEqual(result["moving_lines"][0]["title"], "初爻九")
        self.assertEqual(result["changed"]["full"], "天风姤")
        self.assertIn("变卦为天风姤", result["summary"])

    def test_draw_by_lines_without_moving_line_has_no_changed_hexagram(self):
        service = IchingService()
        result = service.draw_by_lines([7, 7, 7, 7, 7, 7])

        self.assertEqual(result["primary"]["full"], "乾为天")
        self.assertEqual(result["moving_lines"], [])
        self.assertIsNone(result["changed"])


class ChatExtractionTest(unittest.TestCase):
    def test_extract_spaced_solar_date(self):
        self.assertEqual(_extract_date("2020 年 1 月 1 日上午 10 点"), (2020, 1, 1))

    def test_extract_relative_dates(self):
        today = datetime.date(2026, 6, 19)
        self.assertEqual(_extract_date("明天开业好吗", today), (2026, 6, 20))
        self.assertEqual(_extract_date("后天宜不宜出行", today), (2026, 6, 21))

    def test_extract_hour_periods(self):
        self.assertEqual(_extract_hour("上午10点出生"), 10)
        self.assertEqual(_extract_hour("下午3时出生"), 15)
        self.assertEqual(_extract_hour("晚上8:30出生"), 20)

    def test_extract_lunar_leap_month(self):
        self.assertEqual(_extract_lunar_date("农历2020年闰4月1日"), (2020, 4, 1, True))

    def test_extract_date_range_for_next_week(self):
        today = datetime.date(2026, 6, 19)
        start, end = _extract_date_range("下周开业哪天好", today)
        self.assertEqual(start, datetime.date(2026, 6, 22))
        self.assertEqual(end, datetime.date(2026, 6, 28))

    def test_extract_month_range(self):
        today = datetime.date(2026, 6, 19)
        start, end = _extract_date_range("今年 5 月想结婚，选几个吉日", today)
        self.assertEqual(start, datetime.date(2026, 5, 1))
        self.assertEqual(end, datetime.date(2026, 5, 31))


if __name__ == "__main__":
    unittest.main()
