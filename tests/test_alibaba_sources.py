"""Alibaba job discovery contract tests: do not trust incomplete API results."""
import unittest
from alibaba_sources import (BATCH_ID, LIST_PAGE, TOKEN_RE, query_for_page,
                             parse_page, collect_alibaba, normalize_alibaba)
from refresh_sources import KEYS


class Resp:
    def __init__(self, text="", obj=None, status_code=200):
        self.text, self.obj, self.status_code = text, obj, status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise ValueError("HTTP " + str(self.status_code))

    def json(self):
        return self.obj


class Session:
    def __init__(self, jobs, total=None):
        self.jobs, self.total, self.last = jobs, total if total is not None else len(jobs), None

    def get(self, url, **kwargs):
        assert url == LIST_PAGE
        return Resp(text='<script>window.__sysconfig={__token__:"public-nonce"}</script>')

    def post(self, url, **kwargs):
        self.last = (url, kwargs)
        page = kwargs["json"]["pageIndex"]
        data = self.jobs[(page - 1) * 100:page * 100]
        return Resp(obj={"content": {"totalCount": self.total, "datas": data}})


class AlibabaFeedTests(unittest.TestCase):
    def test_public_batch_and_pagination_contract(self):
        self.assertEqual(KEYS["alibaba-public"], "阿里巴巴")
        self.assertEqual(BATCH_ID, 100000560002)
        self.assertIn("&lang=zh", LIST_PAGE)
        self.assertEqual(query_for_page(2)["pageIndex"], 2)
        self.assertEqual(query_for_page(2)["batchId"], BATCH_ID)
        self.assertEqual(query_for_page(2)["pageSize"], 100)
        self.assertIsNotNone(TOKEN_RE.search('__token__: "nonce"'))

    def test_full_pages_and_session_token(self):
        job = {"id": 199907740040, "name": "产品经理实习生"}
        session = Session([job])
        rows, meta = collect_alibaba(session)
        self.assertEqual(len(rows), 1)
        self.assertEqual(meta["unique_ids"], 1)
        self.assertEqual(session.last[1]["params"]["_csrf"], "public-nonce")
        with self.assertRaises(ValueError):
            collect_alibaba(Session([job, job], total=2))
        with self.assertRaises(ValueError):
            collect_alibaba(Session([], total=0))

    def test_missing_cookie_session_token_fails_closed(self):
        class BadSession(Session):
            def get(self, *args, **kwargs):
                return Resp(text="<html>Sign in required</html>")
        with self.assertRaises(ValueError):
            collect_alibaba(BadSession([]))

    def test_only_explicit_beijing_ai_internships(self):
        row = {
            "id": 199907740040, "name": "AI 产品经理",
            "projectName": "阿里巴巴日常实习生", "workLocations": ["北京", "上海"],
            "description": "负责千问 Agent 产品需求分析和迭代",
            "requirement": "在校实习每周4天", "circleNames": ["千问事业部"],
        }
        jobs = normalize_alibaba([row], lambda: "2026-10-14")
        self.assertEqual(len(jobs), 1)
        self.assertIn("/campus/position/199907740040", jobs[0]["link"])
        self.assertIn("千问", jobs[0]["summary"])
        row["projectName"] = "2027应届生招聘"
        self.assertEqual(normalize_alibaba([row], lambda: "2026-10-14"), [])
        row["projectName"] = "日常实习"
        row["workLocations"] = ["杭州"]
        self.assertEqual(normalize_alibaba([row], lambda: "2026-10-14"), [])
        row["workLocations"] = ["北京"]
        row["name"] = "大模型算法工程师"
        self.assertEqual(normalize_alibaba([row], lambda: "2026-10-14"), [])

    def test_reject_missing_job_schema(self):
        with self.assertRaises(ValueError):
            parse_page({"content": {"totalCount": 1, "datas": [{"name": "x"}]}})


    def test_diagnostic_reports_field_selection_without_full_jds(self):
        from alibaba_sources import diagnose_alibaba
        row = {"id": 199907740040, "name": "AI产品经理实习生",
               "workLocations": ["北京"], "projectName": "日常实习",
               "description": "AI Agent产品需求设计"}
        result = diagnose_alibaba([row])
        self.assertEqual(result["counts"]["beijing_internship_pm"], 1)
        self.assertIn("projectName", result["source_keys"])
        self.assertLess(len(str(result["sample"][0])), 800)

if __name__ == "__main__":
    unittest.main()
