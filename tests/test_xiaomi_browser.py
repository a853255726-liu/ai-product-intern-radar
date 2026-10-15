"""Offline contracts for the Xiaomi official public page fallback."""
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import requests
from xiaomi_browser import PAGE_SIZE, api_page_url, official_page, validate_page
from extra_sources import make_sources


class XiaomiBrowserTests(unittest.TestCase):
    def test_public_page_and_api_are_correctly_scoped(self):
        page = urlparse(official_page())
        self.assertEqual(page.hostname, "hr.xiaomi.com")
        self.assertEqual(parse_qs(page.query)["city"], ["北京"])
        self.assertEqual(parse_qs(page.query)["project"], ["实习"])
        api = urlparse(api_page_url(3))
        params = parse_qs(api.query)
        self.assertEqual(api.hostname, "hr.xiaomi.com")
        self.assertEqual(params["pageNum"], ["3"])
        self.assertEqual(params["pageSize"], [str(PAGE_SIZE)])
        self.assertEqual(params["type"], ["3"])
        self.assertEqual(params["cityZhNames"], ["北京"])

    def test_page_validation_rejects_missing_and_changing_data(self):
        valid = {"code": 0, "data": {"total": 2, "list": [{"jobPostId": "123"}]}}
        self.assertEqual(validate_page(valid), ([{"jobPostId": "123"}], 2))
        self.assertEqual(validate_page(valid, 2)[1], 2)
        with self.assertRaises(ValueError):
            validate_page(valid, 5)
        for broken in (
            {"code": 403, "data": valid["data"]},
            {"code": 0, "data": {"total": 0, "list": []}},
            {"code": 0, "data": {"total": 2, "list": [{}]}},
        ):
            with self.subTest(broken=broken):
                with self.assertRaises(ValueError):
                    validate_page(broken)

    def test_blocked_api_uses_public_browser_fallback(self):
        def blocked(*args, **kwargs):
            r = requests.Response()
            r.status_code = 403
            raise requests.HTTPError("blocked", response=r)

        def fake_paginate(*args, **kwargs):
            # Trigger a normal GET in the official-source caller.
            args[1](1)
            raise AssertionError("not reached")

        collect = make_sources(blocked, fake_paginate, lambda: "2026-10-15")["小米"]
        records = [{"jobPostId": "321"}]
        meta = {"reported": 1, "unique_ids": 1}
        with patch("extra_sources.collect_xiaomi_browser", return_value=(records, meta)) as fallback:
            out, audit = collect(object())
        fallback.assert_called_once()
        self.assertEqual(out, records)
        self.assertEqual(audit["direct_api_http_status"], 403)


if __name__ == "__main__":
    unittest.main()
