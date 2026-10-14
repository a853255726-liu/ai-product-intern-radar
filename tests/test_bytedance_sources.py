"""Tests for conservative ByteDance Beijing daily internship query contract."""
import unittest
from bytedance_sources import payload_for_page, normalize_bytedance, _posted
from refresh_sources import KEYS


class ByteDanceFeedTests(unittest.TestCase):
    def test_query_is_bounded_to_beijing_daily_internships(self):
        self.assertEqual(KEYS["bytedance-daily"], "字节跳动")
        payload = payload_for_page(2)
        self.assertEqual(payload["offset"], 100)
        self.assertEqual(payload["recruitment_id_list"], ["202"])
        self.assertEqual(payload["subject_id_list"], ["7194661644654577981"])
        self.assertEqual(payload["location_code_list"], ["CT_11"])
        self.assertEqual(len(payload["job_category_id_list"]), 4)

    def test_no_graduate_or_outside_beijing(self):
        sample = {
            "id": "7673733057043712261", "title": "AI产品实习生",
            "description": "负责 Agent 产品功能和模型评测方案", "requirement": "每周至少4天",
            "city_list": [{"name": "北京"}],
            "job_category": {"name": "产品经理"}, "publish_time": 1790000000000,
        }
        jobs = normalize_bytedance([sample], lambda: "2026-10-14")
        self.assertEqual(len(jobs), 1)
        self.assertIn("7673733057043712261/detail", jobs[0]["link"])
        self.assertEqual(jobs[0]["days"], "≥4天")
        sample["city_list"] = [{"name": "上海"}]
        self.assertEqual(normalize_bytedance([sample], lambda: "2026-10-14"), [])

    def test_no_generic_operations_or_engineering(self):
        case = {"id": "1234567", "title": "AI算法工程师实习生",
                "description": "参与 Agent 产品需求讨论",
                "city_info": {"name": "北京"}}
        self.assertEqual(normalize_bytedance([case], lambda: "2026-10-14"), [])
        case["title"] = "零售产品运营实习生"
        case["description"] = "普通店铺商品管理"
        self.assertEqual(normalize_bytedance([case], lambda: "2026-10-14"), [])

    def test_publish_time_with_milliseconds(self):
        self.assertRegex(_posted(1790000000000), r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(_posted("2026-10-14T14:00"), "2026-10-14")

if __name__ == "__main__":
    unittest.main()
