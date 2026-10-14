"""Offline regression fixtures for the official iQIYI internship board."""
import unittest

from feishu_sources import PORTALS, list_url, parse_list_html, normalize_feishu
from official_links import classify_link
from refresh_sources import KEYS

URL = "https://iq.jobs.feishu.cn/intern/position/7685308564290357513/detail"

class IqiyiBoardTests(unittest.TestCase):
    def test_board_is_registered_in_scheduled_source_map(self):
        self.assertIn("爱奇艺", PORTALS)
        self.assertEqual(KEYS["feishu-iqiyi"], "爱奇艺")
        self.assertIn("/intern/m/?current=2&limit=10", list_url("爱奇艺", 2, 10))

    def test_public_list_html_has_stable_post_id_and_detail(self):
        html = """<div>开启新的工作（1）</div>
        <a data-id="7685308564290357513"
           href="/intern/position/7685308564290357513/detail">
          <span class="positionItem-title-text">海外后台产品设计实习生</span>
          <div class="positionItem-subTitle">
            <span>北京</span><span>校招</span><span>实习</span>
            <span>产品</span><span>日常实习生招聘</span>
            <span>职位 ID：A15887</span>
          </div>
          <div class="positionItem-jobDesc">AI大模型应用，撰写产品方案与PRD。</div>
        </a>"""
        count, records = parse_list_html(html, "https://iq.jobs.feishu.cn")
        self.assertEqual(count, 1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["url"], URL)
        self.assertEqual(classify_link(URL), "official_detail")

    def test_normalization_retains_evidence_and_city(self):
        rows = [{
            "id": "7685308564290357513",
            "title": "海外后台产品设计实习生",
            "subtitle": "北京 / 校招 / 实习 / 产品 / 日常实习生招聘 / 职位 ID：A15887",
            "description": "分析AI大模型能力，撰写产品方案、需求文档与PRD，支持产品迭代。",
            "url": URL,
        }, {
            "id": "7000000000000000000",
            "title": "AI算法工程师",
            "subtitle": "北京 / 实习 / 职位 ID：A23232",
            "description": "模型优化与开发。",
            "url": "https://iq.jobs.feishu.cn/intern/position/7000000000000000000/detail",
        }, {
            "id": "7000000000000000001",
            "title": "AI产品经理实习生",
            "subtitle": "上海 / 实习 / 职位 ID：A55555",
            "description": "负责产品需求与用户调研。",
            "url": "https://iq.jobs.feishu.cn/intern/position/7000000000000000001/detail",
        }]
        jobs = normalize_feishu("爱奇艺", rows, lambda: "2026-10-14")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], "feishu-iqiyi-7685308564290357513")
        self.assertEqual(jobs[0]["source_job_code"], "A15887")
        self.assertEqual(jobs[0]["link"], URL)

if __name__ == "__main__":
    unittest.main()
