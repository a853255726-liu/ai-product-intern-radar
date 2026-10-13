"""Offline tests for official Xiaomi public vacancy feed."""
import unittest
from extra_sources import make_sources, normalize_extra

class XiaomiOfficialTests(unittest.TestCase):
    def test_pagination_scope(self):
        calls = []
        def fake_fetch(sess, method, url, body, referer):
            calls.append((method, url, referer))
            self.assertEqual(method, "GET")
            self.assertIn("cityZhNames=%E5%8C%97%E4%BA%AC", url)
            self.assertIn("type=3", url)
            page = 1 if "pageNum=1" in url else 2
            return {"code": 0, "data": {
                "total": 2,
                "list": [{"jobPostId": "101"}] if page == 1 else [{"jobPostId": "102"}]}}
        def fake_collect(label, one, unpack, max_pages=200):
            rows = []
            for page in (1, 2):
                rec, total, pk = unpack(one(page))
                rows.extend(rec)
            self.assertEqual(total, len(rows))
            self.assertEqual(len({r[pk] for r in rows}), total)
            return rows, {"reported":total, "unique_ids":total,"pages":2}
        src = make_sources(fake_fetch, fake_collect, lambda: "2026-10-13")
        rows, audit = src["小米"](None)
        self.assertEqual(audit["reported"],2)
        self.assertEqual(len(rows),2)
        self.assertEqual(len(calls),2)

    def test_ai_product_filter(self):
        base = dict(cityZhNames=["北京"], type=3,
            levelOneDeptName="集团技术委员会", publishTime="2026-10-12",
            requirement="每周至少到岗4天，实习6个月",
            description="参与小爱大模型与Agent功能的产品定义、模型效果测试",
            larkJobCode="A123", url="https://xiaomi.jobs.f.mioffice.cn/internship/position/123/detail",
            jobPostId="123")
        good = dict(base, title="AI产品经理实习生")
        engineer = dict(base, jobPostId="124", title="AI大模型算法工程师")
        outside = dict(base, jobPostId="125", title="AI产品经理", cityZhNames=["深圳"])
        results = normalize_extra("小米", [good, engineer, outside], lambda:"2026-10-13")
        self.assertEqual([r["id"] for r in results], ["xiaomi-123"])
        self.assertEqual(results[0]["days"], "≥4天")
        self.assertEqual(results[0]["source_job_code"], "A123")
        self.assertEqual(results[0]["posted"], "2026-10-12")

    def test_no_unverified_or_invalid_urls(self):
        sample = dict(cityZhNames=["北京"], type=3, title="AI产品实习生",
            description="Agent", requirement="", jobPostId="123",
            url="https://evil.invalid/123")
        self.assertEqual(normalize_extra("小米",[sample],lambda:"2026-10-13"), [])

if __name__ == "__main__":
    unittest.main()
