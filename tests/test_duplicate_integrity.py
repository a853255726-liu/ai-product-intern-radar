"""Test duplicated official job IDs without inventing missing vacancies."""
import unittest
from unittest.mock import patch

from refresh_sources import collect, duplicate_id_diagnostics, xhs, meituan


class DuplicateIdForensicsTests(unittest.TestCase):
    def test_same_page_identical_collision(self):
        a = {"positionId": "101", "title": "AI产品"}
        dup = duplicate_id_diagnostics([a, dict(a)], "positionId", [2])
        self.assertEqual(dup[0]["scope"], "same_page")
        self.assertTrue(dup[0]["identical_payload"])
        self.assertEqual((dup[0]["first_page"], dup[0]["again_page"]), (1, 1))
        with self.assertRaisesRegex(ValueError, r"same_page"):
            collect("sample", lambda i: None, lambda _: ([a, dict(a)], 2, "positionId"))

    def test_cross_page_nonidentical_collision(self):
        a = {"positionId": "101", "title": "old"}
        b = {"positionId": "101", "title": "changed"}
        dup = duplicate_id_diagnostics([a, b], "positionId", [1, 1])
        self.assertEqual(dup[0]["scope"], "cross_page")
        self.assertFalse(dup[0]["identical_payload"])
        def req(n):
            return ([a] if n == 1 else [b], 2, "positionId")
        with patch("refresh_sources.time.sleep", return_value=None):
            with self.assertRaisesRegex(ValueError, r"cross_page"):
                collect("sample", req, lambda v: v)

    def test_xiaohongshu_small_page_retry_must_be_unique(self):
        sizes = []
        def fake(session, method, url, body, referer):
            size, page = body["pageSize"], body["pageNum"]
            sizes.append(size)
            if size != 20:
                jobs = [{"positionId": "7"}, {"positionId": "7"}]
            else:
                jobs = [{"positionId": str(7+page)}]
            return {"data": {"list": jobs, "total": 2}}
        with patch("refresh_sources.request_json", fake):
            with patch("refresh_sources.time.sleep", return_value=None):
                jobs, audit = xhs(None)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(audit["unique_ids"], 2)
        self.assertEqual(audit["page_size"], 20)
        self.assertEqual([x["page_size"] for x in audit["retry_recovered"]], [50])
        self.assertIn(20, sizes)

    def test_persistent_xiaohongshu_collision_fails_closed(self):
        def fake(session, method, url, body, referer):
            return {"data": {"list": [{"positionId": "7"}, {"positionId": "7"}],
                             "total": 2}}
        with patch("refresh_sources.request_json", fake):
            with patch("refresh_sources.time.sleep", return_value=None):
                with self.assertRaisesRegex(ValueError, r"all pagination sizes failed"):
                    xhs(None)

    def test_meituan_still_fail_closed_and_reports_each_try(self):
        def fake(session, method, url, body, referer):
            return {"data": {"list": [{"jobUnionId": "7"}, {"jobUnionId": "7"}],
                             "page": {"totalCount": 2}}}
        with patch("refresh_sources.request_json", fake):
            with patch("refresh_sources.time.sleep", return_value=None):
                with self.assertRaisesRegex(ValueError, r"both 50- and 25-row pages failed"):
                    meituan(None)


if __name__ == "__main__":
    unittest.main()
