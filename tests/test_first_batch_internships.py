"""Offline regression cases for the TAL Moka and OPPO daily channels."""
import unittest
from oppo_sources import parse_public_listing, normalize_oppo, URL as OPPO_URL
from tal_sources import (
    BASE as TAL_BASE, list_url, is_intern, normalize_tal, explicit_grad_only,
)
from official_links import classify_link
from daily_scope import eligible_jobs


class TalOpPoTests(unittest.TestCase):
    def test_tal_official_route_is_a_direct_job_detail(self):
        job = TAL_BASE + "#/job/123e4567-e89b-12d3-a456-426614174000"
        self.assertEqual(classify_link(job), "official_detail")
        self.assertEqual(list_url(2), TAL_BASE + "#/jobs/?page=2")

    def test_tal_daily_beijing_ai_product_candidate(self):
        candidate = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "AI教育产品实习生",
            "url": TAL_BASE + "#/job/123e4567-e89b-12d3-a456-426614174000",
            "tags": ["实习", "教育科技", "北京"],
            "description": "负责九章大模型AI教育产品需求调研、PRD及智能体方案设计；工作地点：北京",
            "date": "2026-10-15",
        }
        jobs = normalize_tal([candidate], lambda: "2026-10-16")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "好未来")
        self.assertEqual(jobs[0]["link"], candidate["url"])
        self.assertEqual(jobs[0]["source_post_id"], candidate["id"])
        self.assertFalse(is_intern({**candidate, "tags": ["全职", "北京"]}))
        self.assertEqual(normalize_tal([{**candidate, "tags": ["全职", "北京"]}],
                                       lambda: "2026-10-16"), [])
        self.assertEqual(normalize_tal([{**candidate, "tags": ["实习", "上海"],
                                        "description": "上海办公，大模型产品需求"}],
                                       lambda: "2026-10-16"), [])

    def test_tal_explicit_2027_only_is_not_published(self):
        row = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "AI教育产品实习生", "tags": ["实习", "教育", "北京"],
            "url": TAL_BASE + "#/job/123e4567-e89b-12d3-a456-426614174000",
            "description": "九章大模型AI产品需求调研。仅招2027届毕业生。工作地点：北京。",
            "date": "2026-10-15",
        }
        captured = normalize_tal([row], lambda: "2026-10-16")
        self.assertEqual(len(captured), 1)
        self.assertEqual(eligible_jobs(captured), [])

    def test_grad_only_qualification_is_retained_beyond_ui_excerpt(self):
        long_duty = "AI产品设计、PRD。" + ("项目协作。" * 700) + "仅招2027届毕业生。工作地点：北京。"
        row = {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "title": "AI教育产品实习生", "tags": ["实习", "教育", "北京"],
            "url": TAL_BASE + "#/job/123e4567-e89b-12d3-a456-426614174001",
            "description": long_duty, "date": "2026-10-16",
        }
        output = normalize_tal([row], lambda: "2026-10-16")
        self.assertEqual(len(output), 1)
        self.assertTrue(output[0]["graduation"].startswith("仅招2027届"))
        self.assertEqual(eligible_jobs(output), [])
        self.assertEqual(explicit_grad_only("2027届及以后均可报名"), "")
        self.assertEqual(explicit_grad_only("仅招2027届及以后在校生"), "")
        self.assertIn("仅招2027届", explicit_grad_only(
            "仅招2027届毕业生。" + "其他业务条件。" * 100 +
            "另一个岗位注明2028届及以后也可以申请。"
        ))

    def test_oppo_full_visible_list_reconciles_job_ids(self):
        text = """岗位列表
在招职位(2)
AI产品经理实习生
2026-10-15 发布
北京市
产品及运营类
日常实习生招聘
本科及以上
经验不限
职位ID：J251114000002
负责小布AI智能体PRD、需求分析与用户调研。
产品经理实习生
2026-10-14 发布
上海市
产品及运营类
日常实习生招聘
本科及以上
经验不限
职位ID：J251114000003
负责内容运营与功能设计。
"""
        rows, audit = parse_public_listing(text)
        self.assertEqual(audit["reported"], 2)
        self.assertEqual(audit["unique_ids"], 2)
        self.assertEqual(rows[0]["city"], "北京市")
        self.assertEqual(rows[0]["title"], "AI产品经理实习生")
        jobs = normalize_oppo(rows, lambda: "2026-10-16")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["link"], OPPO_URL)
        self.assertEqual(classify_link(jobs[0]["link"]), "official_list")

    def test_oppo_graduation_only_excluded_even_after_long_description(self):
        rows = [{
            "id": "J251114000002", "title": "AI产品经理实习生",
            "city": "北京市", "posted": "2026-10-16",
            "description": "小布智能体PRD需求调研。" + "产品需求。" * 700
                           + "仅招2027届毕业生。",
        }]
        captured = normalize_oppo(rows, lambda: "2026-10-16")
        self.assertEqual(len(captured), 1)
        self.assertIn("仅招2027届", captured[0]["graduation"])
        self.assertEqual(eligible_jobs(captured), [])

    def test_oppo_nongraduate_cohort_is_not_excluded(self):
        rows = [{
            "id": "J251114000003", "title": "AI产品经理实习生",
            "city": "北京市", "posted": "2026-10-16",
            "description": "小布智能体用户研究，2027届及以后均可申请。",
        }]
        captured = normalize_oppo(rows, lambda: "2026-10-16")
        self.assertEqual(len(captured), 1)
        self.assertEqual(len(eligible_jobs(captured)), 1)

    def test_oppo_rejects_partial_or_mixed_hiring(self):
        short = """在招职位(2)
产品实习生
2026-10-15 发布
北京市
产品类
日常实习生招聘
职位ID：J251114000001
大模型AI应用产品需求分析
"""
        with self.assertRaises(ValueError):
            parse_public_listing(short)
        full_time = short.replace("在招职位(2)", "在招职位(1)").replace(
            "日常实习生招聘", "2027届应届生招聘")
        with self.assertRaises(ValueError):
            parse_public_listing(full_time)


if __name__ == "__main__":
    unittest.main()
