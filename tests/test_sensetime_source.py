"""Offline contract checks for SenseTime's public campus job board."""
import unittest

from feishu_sources import (
    COMPANY_CODES, PORTALS, list_url, parse_list_html, normalize_feishu,
)
from official_links import classify_link


class SenseTimeSourceTests(unittest.TestCase):
    def test_official_custom_domain_is_registered(self):
        self.assertEqual(
            PORTALS["商汤科技"],
            ("https://hr-jobs.sensetime.com", "/edu/m/"),
        )
        self.assertEqual(COMPANY_CODES["商汤科技"], "sensetime")
        self.assertEqual(classify_link("https://hr-jobs.sensetime.com/edu/m/"), "official_list")
        self.assertEqual(
            list_url("商汤科技", 3, 10),
            "https://hr-jobs.sensetime.com/edu/m/?current=3&limit=10",
        )

    def test_parse_and_filter_official_job_record(self):
        body = """
        <html><body><div>开启新的工作（1）</div>
          <a data-id="7611234567890123456"
             href="/edu/m/position/7611234567890123456/detail">
            <div class="positionItem-title-text">AI产品实习生</div>
            <div class="positionItem-subTitle">
              <span>北京</span><span>校招实习</span><span>产品</span>
            </div>
            <div class="positionItem-jobDesc">负责AI产品用户研究、PRD设计与需求分析</div>
          </a>
        </body></html>
        """
        total, rows = parse_list_html(body, PORTALS["商汤科技"][0])
        self.assertEqual(total, 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["url"],
            "https://hr-jobs.sensetime.com/edu/m/position/7611234567890123456/detail",
        )
        jobs = normalize_feishu("商汤科技", rows, lambda: "2026-10-16")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "商汤科技")
        self.assertEqual(jobs[0]["source_post_id"], "7611234567890123456")
        self.assertEqual(classify_link(jobs[0]["link"]), "official_detail")

    def test_non_beijing_and_non_intern_excluded(self):
        for subtitle in ("上海 / 校招实习 / 产品", "北京 / 校招正式 / 产品"):
            with self.subTest(subtitle=subtitle):
                row = {
                    "id": "7611234567890123456",
                    "title": "AI产品经理",
                    "subtitle": subtitle,
                    "description": "大模型产品设计",
                    "url": "https://hr-jobs.sensetime.com/edu/m/position/7611234567890123456/detail",
                }
                self.assertEqual(normalize_feishu("商汤科技", [row], lambda: "2026-10-16"), [])


if __name__ == "__main__":
    unittest.main()
