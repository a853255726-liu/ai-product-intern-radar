"""Offline contract tests for the public Kimi MokaHR campus source."""
import unittest
from kimi_sources import parse_list_html, parse_detail_html, normalize_kimi, list_url, BASE
from refresh_sources import KEYS
from official_links import classify_link

UUID = "83c7d619-4b46-4fc7-9490-9b5d0171a5a7"
URL = BASE + "#/job/" + UUID


def card(title, kind, city="", uuid=UUID):
    loc = (f'<div class="sd-Ellipsis-hiddenContent-12YAZ">{city}</div>'
           if city else "")
    return (
        '<div class="container-aOp138AX_X normal-TBuWTpDMcE card-BtpcjTxIfE">'
        f'<a href="{BASE}#/job/{uuid}">'
        f'<span class="title-u2qk9xX9Ie target-color-container">{title}</span>'
        '<span class="published-at-PQ5IBWmbJV">发布于 2026-10-10</span>'
        f'<div class="sd-Ellipsis-hiddenContent-12YAZ">{kind}</div>'
        '<div class="sd-Ellipsis-hiddenContent-12YAZ">产品类/Product</div>'
        + loc + '</a></div>'
    )


class KimiMokaTests(unittest.TestCase):
    def test_registered_and_direct_link(self):
        self.assertEqual(KEYS["kimi-moka"], "月之暗面")
        self.assertTrue(list_url(2).endswith("#/jobs/?page=2"))
        self.assertEqual(classify_link(URL), "official_detail")
        self.assertNotEqual(classify_link(BASE + "#/jobs/?page=1"),
                            "official_detail")

    def test_list_parses_only_actual_cards(self):
        html = ('<div>已选 <span>0</span> 条件 | <span>2</span> 结果</div>'
                '<div class="results-X"><div class="jobs-Y">'
                + card("AI harness 产品实习生", "实习")
                + card("产品实习生", "全职", "北京市",
                       "f287f352-5561-4d86-bb85-552b0283854c")
                + '</div></div>'
                '<div class="recommendations">' + card("误入推荐", "实习")
                + '</div>')
        total, rows = parse_list_html(html)
        self.assertEqual(total, 2)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["id"], UUID)
        self.assertEqual(rows[0]["date"], "发布于 2026-10-10")

    def test_missing_count_fails_closed(self):
        with self.assertRaises(ValueError):
            parse_list_html('<div>已选 0 条件 | 0 结果</div>')

    def test_detail_and_base_beijing(self):
        detail_html = (
            '<div class="job-description-VvfEUGocNE">'
            '<p>负责 Agent Harness 产品设计、用户调研和评测体系迭代。</p>'
            '<p>实习时间至少 4 个月，每周至少 4 天，Base 北京。</p>'
            '</div>'
        )
        description = parse_detail_html(detail_html)
        item = dict(id=UUID, title="AI harness 产品实习生", url=URL,
                    tags=["实习", "产品类/Product"], date="发布于 2026-10-10",
                    description=description)
        rows = normalize_kimi([item], lambda: "2026-10-14")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["days"], "≥4天")
        self.assertEqual(rows[0]["duration"], "≥4个月")
        self.assertEqual(rows[0]["posted"], "2026-10-10")
        self.assertEqual(rows[0]["link"], URL)

    def test_city_uncertain_and_full_time_rejected(self):
        item = dict(id=UUID, title="KimiCode 产品实习生", url=URL,
                    tags=["实习", "产品类/Product"], date="",
                    description="做 Agent 产品体验评测和版本迭代。")
        self.assertEqual(normalize_kimi([item], lambda: "2026-10-14"), [])
        item["tags"] = ["全职", "产品类/Product", "北京市"]
        self.assertEqual(normalize_kimi([item], lambda: "2026-10-14"), [])

    def test_engineering_role_rejected(self):
        row = dict(id=UUID, title="Agent 产品工程师实习生", url=URL,
                   tags=["实习", "产品类/Product", "北京市"], date="",
                   description="负责产品功能实现和研发。")
        self.assertEqual(normalize_kimi([row], lambda: "2026-10-14"), [])

if __name__ == "__main__":
    unittest.main()
