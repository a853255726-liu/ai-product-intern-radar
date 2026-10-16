"""Offline contracts for newly discovered AI employer recruiting portals.

These fixtures test parsing and conservative candidate selection, NOT
successful cloud pagination. A live source remains pending until audited.
"""
import unittest

from feishu_sources import (
    PORTALS, COMPANY_CODES, list_url, parse_list_html, normalize_feishu
)
from official_links import classify_link


class AiEmployerExpansionTests(unittest.TestCase):
    EXPECTED = {
        "智平方": ("ai2robotics.jobs.feishu.cn", "ai2robotics"),
        "无问芯穹": ("infinigence.jobs.feishu.cn", "infinigence"),
        "星动纪元": ("k0fqxcszc9.jobs.feishu.cn", "robotera"),
    }

    def test_portals_have_distinct_identifiers(self):
        for company, (host, code) in self.EXPECTED.items():
            with self.subTest(company=company):
                self.assertEqual(PORTALS[company],
                                 ("https://" + host, "/index/position/list"))
                self.assertEqual(COMPANY_CODES[company], code)
                self.assertEqual(
                    list_url(company, 2, 10),
                    "https://" + host +
                    "/index/position/list?current=2&limit=10",
                )
                self.assertEqual(
                    classify_link("https://" + host + "/index/position/list"),
                    "official_list",
                )

    def test_ai2robotics_daily_intern_is_allowed(self):
        html = """
        <html><body><div>开启新的工作（1）</div>
        <a data-id="7611234567890123456"
           href="/index/position/7611234567890123456/detail">
          <div class="positionItem-title-text">产品实习生（具身智能软件平台方向）</div>
          <div class="positionItem-subTitle">
             <span>北京</span><span>实习</span>
          </div>
          <div class="positionItem-jobDesc">参与机器人云平台的需求调研、PRD及产品设计</div>
        </a></body></html>
        """
        total, records = parse_list_html(html, "https://ai2robotics.jobs.feishu.cn")
        self.assertEqual(total, 1)
        jobs = normalize_feishu("智平方", records, lambda: "2026-10-16")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], "feishu-ai2robotics-7611234567890123456")
        self.assertEqual(classify_link(jobs[0]["link"]), "official_detail")

    def test_no_full_time_or_other_city_is_published(self):
        for company in self.EXPECTED:
            for city_kind in ("北京 / 全职", "上海 / 实习"):
                with self.subTest(company=company, city_kind=city_kind):
                    row = {
                        "id": "7611234567890123456",
                        "title": "AI产品经理",
                        "subtitle": city_kind,
                        "description": "智能体与模型推理产品规划",
                        "url": PORTALS[company][0] +
                        "/index/position/7611234567890123456/detail",
                    }
                    self.assertEqual(
                        normalize_feishu(company, [row], lambda: "2026-10-16"),
                        [],
                    )


if __name__ == "__main__":
    unittest.main()
