"""Contracts for the new TAL campus site, replacing redirected Moka cards."""
import unittest

from tal_portal import LIST_URL, parse_card, parse_detail
from tal_sources import normalize_tal
from official_links import classify_link


class TalNewPortalTests(unittest.TestCase):
    UUID = "0e93fea4-922e-4ad9-98a9-04691cfd412f"

    def test_new_job_card_and_direct_link(self):
        card = ("产品实习生\n发布于 2026-07-31\n"
                "全职 互联网产品\n北京市\n"
                "岗位职责：参与AI Agent产品PRD撰写")
        parsed = parse_card(card)
        self.assertEqual(parsed["title"], "产品实习生")
        self.assertEqual(parsed["nature"], "全职")
        self.assertEqual(parsed["city"], "北京市")
        detail_url = LIST_URL + "/" + self.UUID
        body = ("产品实习生\n全职\n互联网产品\n校招\n北京市\n"
                "职位描述\n负责AI Agent产品规划和用户研究。\n"
                "任职要求\n每周4天")
        row = parse_detail(detail_url, body, parsed)
        self.assertEqual(row["id"], self.UUID)
        self.assertEqual(classify_link(row["url"]), "official_detail")
        # Project '日常实习' does not override job nature: this is full-time.
        self.assertEqual(normalize_tal([row], lambda: "2026-10-16"), [])

    def test_matching_intern_job_can_enter_product_screening(self):
        parsed = parse_card(
            "AI产品实习生\n发布于 2026-10-16\n"
            "实习 互联网产品\n北京市\n大模型产品需求调研")
        row = parse_detail(
            LIST_URL + "/" + self.UUID,
            "AI产品实习生\n实习\n互联网产品\n北京市\n"
            "职位描述\nAI Agent产品PRD、用户访谈和大模型应用设计。\n"
            "任职要求\n本科及以上在校生。",
            parsed,
        )
        jobs = normalize_tal([row], lambda: "2026-10-16")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["source_post_id"], self.UUID)
        self.assertEqual(jobs[0]["link"], row["url"])

    def test_cross_host_and_nature_mismatch_fail(self):
        card = parse_card(
            "产品实习生\n发布于 2026-10-16\n"
            "实习 互联网产品\n北京市\nAI产品需求")
        with self.assertRaises(ValueError):
            parse_detail(
                "https://external.example/campus/positions/" + self.UUID,
                "产品实习生\n实习\n职位描述\nAI产品设计",
                card,
            )
        with self.assertRaises(ValueError):
            parse_detail(
                LIST_URL + "/" + self.UUID,
                "产品实习生\n全职\n职位描述\nAI产品设计",
                card,
            )


if __name__ == "__main__":
    unittest.main()
