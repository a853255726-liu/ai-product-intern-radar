"""Offline contract tests for the public ByteDance browser fallback."""
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import requests
from bytedance_browser import (
    BEIJING, CATEGORY_IDS, DAILY_ID, PAGE_SIZE,
    public_page_url, validate_request_scope,
)
from bytedance_sources import bytedance


class BrowserFallbackContractTests(unittest.TestCase):
    def request_body(self, page):
        return {
            "recruitment_id_list": ["202"],
            "subject_id_list": [DAILY_ID],
            "location_code_list": [BEIJING],
            "job_category_id_list": list(CATEGORY_IDS),
            "offset": (page - 1) * PAGE_SIZE,
            "limit": PAGE_SIZE,
        }

    def test_public_url_pins_internship_scope(self):
        parsed = urlparse(public_page_url(3))
        params = parse_qs(parsed.query)
        self.assertEqual(parsed.hostname, "jobs.bytedance.com")
        self.assertEqual(params["type"], ["3"])
        self.assertEqual(params["location"], [BEIJING])
        self.assertEqual(params["project"], [DAILY_ID])
        self.assertEqual(params["current"], ["3"])
        self.assertEqual(params["limit"], [str(PAGE_SIZE)])
        self.assertEqual(set(params["category"][0].split(",")), set(CATEGORY_IDS))

    def test_page_and_filter_contract(self):
        self.assertIsNone(validate_request_scope(self.request_body(2), 2))
        for changed in (
            {"recruitment_id_list": ["201"]},
            {"subject_id_list": []},
            {"location_code_list": ["CT_2"]},
            {"job_category_id_list": []},
            {"offset": 0},
            {"limit": 50},
        ):
            with self.subTest(changed=changed):
                body = dict(self.request_body(2))
                body.update(changed)
                with self.assertRaises(ValueError):
                    validate_request_scope(body, 2)

    def test_public_browser_fallback_only_after_blocked_http(self):
        response = requests.Response()
        response.status_code = 405
        failure = requests.HTTPError("blocked", response=response)
        rows, audit = [{"id": "123"}], {"reported": 1}
        with patch("bytedance_sources.bytedance_direct", side_effect=failure):
            with patch("bytedance_sources.collect_bytedance_browser",
                       return_value=(rows, audit)) as fallback:
                result_rows, result_audit = bytedance(object())
        fallback.assert_called_once()
        self.assertEqual(result_rows, rows)
        self.assertEqual(result_audit["direct_api_http_status"], 405)

    def test_unrelated_errors_do_not_trigger_browser(self):
        response = requests.Response()
        response.status_code = 500
        failure = requests.HTTPError("server error", response=response)
        with patch("bytedance_sources.bytedance_direct", side_effect=failure):
            with patch("bytedance_sources.collect_bytedance_browser") as fallback:
                with self.assertRaises(requests.HTTPError):
                    bytedance(object())
                fallback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
