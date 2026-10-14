"""Bilibili public internship (type=0) feed contract and fail-closed tests."""
import unittest
from unittest.mock import patch
from bilibili_sources import (
    CATALOG, API, TOKEN, headers, internship_request, parse_response,
    collect_bilibili, normalize_bilibili,
)
from refresh_sources import KEYS
from official_links import classify_link

def mkjob(jid=30101, title="AI 产品实习生", city="北京", description="负责 AI Agent 产品需求分析和迭代"):
    return {
        "id": jid, "positionName": title, "workLocation": city,
        "positionTypeName": "实习", "postCodeName": "产品运营类",
        "positionDescription": description, "recruitType": 0,
        "pushTime": "2026-10-14 08:00:00",
    }

class Response:
    def __init__(self, obj):
        self.obj = obj
    def raise_for_status(self):
        pass
    def json(self):
        return self.obj

class Session:
    def __init__(self, pages, total=None):
        self.pages = pages
        self.total = total if total is not None else sum(map(len, pages))
        self.requested = []
    def get(self, url, headers, timeout):
        self.requested.append(("GET", url, headers))
        return Response({"code": 0, "data": "ce2348f6-b1b4-47fa-9bff-a7f1b2722d99"})
    def post(self, url, json, headers, timeout):
        self.requested.append(("POST", url, headers, json))
        page = json["pageNum"]
        return Response({"code": 0, "data": {
            "list": self.pages[page - 1], "total": self.total,
        }})

class BilibiliTests(unittest.TestCase):
    def test_real_internship_query_and_listing(self):
        self.assertEqual(KEYS["bilibili-public"], "B站")
        self.assertIn("type=0", CATALOG)
        self.assertEqual(internship_request(1)["workTypeList"], ["0"])
        self.assertEqual(internship_request(1)["positionTypeList"], ["0"])
        self.assertIsNone(internship_request(1)["recruitType"])
        self.assertIn("x-appkey", headers("public_token"))

    def test_full_pages_and_anonymous_token(self):
        a, b = mkjob(), mkjob(30102, "产品实习生", "北京")
        session = Session([[a], [b]])
        with patch("bilibili_sources.time.sleep", return_value=None):
            result, audit = collect_bilibili(session, page_size=1)
        self.assertEqual(len(result), 2)
        self.assertEqual(audit["unique_ids"], 2)
        self.assertEqual(audit["page_sizes"], [1, 1])
        self.assertEqual(session.requested[0][0:2], ("GET", TOKEN))
        self.assertEqual(session.requested[1][1], API)
        self.assertTrue(session.requested[1][2]["x-csrf"])

    def test_duplicate_fails_closed(self):
        a = mkjob()
        with patch("bilibili_sources.time.sleep", return_value=None):
            with self.assertRaisesRegex(ValueError, "duplicate"):
                collect_bilibili(Session([[a], [a]]), page_size=1)

    def test_rejects_graduate_or_bad_response(self):
        with self.assertRaises(ValueError):
            parse_response({"code": -101, "message": "请重新登录"})
        with self.assertRaises(ValueError):
            collect_bilibili(Session([[mkjob(title="AI 产品经理", city="上海")]],
                                     total=0))
        rows, audit = collect_bilibili(
            Session([[dict(mkjob(), positionTypeName="全职")]]))
        self.assertEqual(audit["non_internship_rows"], 1)
        self.assertEqual(audit["explicit_internships"], 0)
        self.assertEqual(audit["position_type_counts"], {"全职": 1})
        self.assertEqual(normalize_bilibili(rows, lambda:"2026-10-14"), [])

    def test_mixed_public_listing_only_publishes_actual_interns(self):
        rows=[mkjob(30111), dict(mkjob(30112), positionTypeName="全职")]
        _, audit=collect_bilibili(Session([rows]))
        self.assertEqual(audit["unique_ids"], 2)
        self.assertEqual(audit["explicit_internships"], 1)
        self.assertEqual(audit["non_internship_rows"], 1)
        self.assertEqual(len(normalize_bilibili(rows,lambda:"2026-10-14")),1)

    def test_beijing_ai_pm_and_official_detail_only(self):
        rows = [
            mkjob(),
            mkjob(30102, "大模型算法工程师实习生", "北京"),
            mkjob(30103, "AI 产品实习生", "上海"),
            mkjob(30104, "普通内容运营实习生", "北京", "使用 AI 文案工具做日常工作"),
        ]
        found = normalize_bilibili(rows, lambda: "2026-10-14")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["title"], "AI 产品实习生")
        self.assertEqual(found[0]["link"], "https://jobs.bilibili.com/campus/positions/30101?type=0")
        self.assertEqual(classify_link(found[0]["link"]), "official_detail")
        self.assertNotEqual(classify_link(CATALOG), "official_detail")
        self.assertNotEqual(classify_link("https://jobs.bilibili.com/campus/positions"), "official_detail")

if __name__ == "__main__":
    unittest.main()
