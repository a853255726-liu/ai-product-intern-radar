"""Shengshu and ModelBest official Feishu recruiting scope tests."""
import unittest
from feishu_sources import PORTALS, COMPANY_CODES, list_url, parse_list_html, normalize_feishu
from refresh_sources import KEYS
from official_links import classify_link


class StartupPortalsTests(unittest.TestCase):
    def test_registered_portals_and_employer_scoped_urls(self):
        for name, selector, code, path in [
            ("生数科技", "feishu-shengshu", "shengshu", "/index/position/list"),
            ("面壁智能", "feishu-modelbest", "modelbest", "/campus/m/position/list"),
        ]:
            with self.subTest(name=name):
                self.assertEqual(KEYS[selector], name)
                self.assertEqual(COMPANY_CODES[name], code)
                self.assertIn(path + "?current=2&limit=10", list_url(name, 2, 10))

    def test_official_detail_and_beijing_internship(self):
        for name, path in [
            ("生数科技", "index"),
            ("面壁智能", "campus/m"),
        ]:
            with self.subTest(name=name):
                base = PORTALS[name][0]
                url = base + "/" + path + "/position/7695630162042325302/detail"
                html = ('<div>开启新的工作（1）</div>'
                    + '<a data-id="7695630162042325302" href="' + url + '">'
                    + '<span class="positionItem-title-text">AI产品经理实习生</span>'
                    + '<div class="positionItem-subTitle">北京 / 实习 / 产品 / 职位 ID：A25887</div>'
                    + '<div class="positionItem-jobDesc">负责大模型产品调研、需求分析、Agent评测。</div>'
                    + '</a>')
                total, records = parse_list_html(html, base)
                self.assertEqual((total, len(records)), (1, 1))
                self.assertEqual(classify_link(records[0]["url"]), "official_detail")
                jobs = normalize_feishu(name, records, lambda: "2026-10-14")
                self.assertEqual(len(jobs), 1)
                self.assertTrue(jobs[0]["id"].startswith("feishu-" + COMPANY_CODES[name]))
                self.assertEqual(jobs[0]["source_job_code"], "A25887")

    def test_no_social_full_time_or_out_of_beijing(self):
        for name in ("生数科技", "面壁智能"):
            base = PORTALS[name][0]
            for subtitle in ("北京 / 社招 / 全职", "上海 / 实习"):
                fake = [{"id": "7681234567890123456", "title": "AI产品实习生",
                         "subtitle": subtitle, "description": "AI产品规划",
                         "url": base + "/index/position/7681234567890123456/detail"}]
                self.assertEqual(normalize_feishu(name, fake, lambda: "2026-10-14"), [])

if __name__ == "__main__":
    unittest.main()
