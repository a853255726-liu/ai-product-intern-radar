"""New automated discovery needs stronger PM screening than older reviewed leads."""
import unittest
from daily_scope import eligible_jobs

class PublicationQualityTests(unittest.TestCase):
    def test_new_engineering_and_generic_ops_remain_archive_only(self):
        cases = [
            {"id": "xhs-fake-front", "company": "小红书", "title": "前端实习生",
             "summary": "AI小工具平台产品能力开发", "source": "官网API",
             "first_seen": "2026-10-14"},
            {"id": "meituan-fake-ops", "company": "美团", "title": "零售产品运营实习生",
             "summary": "官方列表已有职位，详情尚待核验", "source": "官网API",
             "first_seen": "2026-10-14"},
            {"id": "feishu-good", "company": "爱奇艺", "title": "AI产品经理实习生",
             "summary": "负责产品需求分析和Agent评测", "source": "官网公开列表",
             "first_seen": "2026-10-14"},
        ]
        selected = eligible_jobs(cases)
        self.assertEqual([x["id"] for x in selected], ["feishu-good"])
        self.assertEqual(len(cases), 3)  # The archived source feed is intact.

    def test_previously_reviewed_candidate_is_not_silently_removed(self):
        older = {"id": "manually-reviewed", "company": "美团",
                 "title": "产品运营实习生", "summary": "人工核实为相邻岗位",
                 "source": "企业官网"}
        self.assertEqual(len(eligible_jobs([older])), 1)

if __name__ == "__main__":
    unittest.main()
