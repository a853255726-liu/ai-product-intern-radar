import unittest
from unittest.mock import patch
from refresh_sources import meituan


class MeituanBoundaryTests(unittest.TestCase):
    def test_full_unique_retry_when_first_page_has_duplicate(self):
        seen=[]
        def api(session, method, url, payload, referer):
            size = payload["page"]["pageSize"]
            page = payload["page"]["pageNo"]
            seen.append(size)
            if size == 100:
                rows=[{"jobUnionId": 101}, {"jobUnionId": 101}]
            else:
                rows=[{"jobUnionId": 101 if page == 1 else 102}]
            return {"data": {"list": rows, "page": {"totalCount": 2}}}
        with patch("refresh_sources.request_json", api):
            with patch("refresh_sources.time.sleep", return_value=None):
                rows, audit=meituan(None)
        self.assertEqual([r["jobUnionId"] for r in rows], [101,102])
        self.assertEqual(audit["unique_ids"],2)
        self.assertEqual(audit["page_size"],50)
        self.assertTrue(audit["recovered_from_boundary_duplicate"])
        self.assertIn(100, seen)

    def test_persistent_duplicate_fails_closed(self):
        def api(session, method, url, payload, referer):
            return {"data": {"list": [{"jobUnionId": 101}, {"jobUnionId": 101}],
                             "page": {"totalCount": 2}}}
        with patch("refresh_sources.request_json", api):
            with patch("refresh_sources.time.sleep", return_value=None):
                with self.assertRaises(ValueError):
                    meituan(None)


if __name__=="__main__":
    unittest.main()
