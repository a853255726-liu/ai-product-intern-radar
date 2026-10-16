"""Directory health checks must never become job availability claims."""
import unittest
from directory_monitor import (
    ENTRANCES, check_entrance, update_directory_audits,
)


class FakeResponse:
    def __init__(self, url, body="官方校园招聘｜实习生计划"):
        self.url = url
        self.content = body.encode("utf-8")
        self.text = body
        self.status_code = 200
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP failed")


class FakeSession:
    def __init__(self, response):
        self.response = response
    def get(self, *args, **kwargs):
        return self.response


class DirectoryMonitorTests(unittest.TestCase):
    def test_good_official_page_is_only_a_directory_status(self):
        for name, (url, hosts, marker) in ENTRANCES.items():
            with self.subTest(name=name):
                result = check_entrance(FakeSession(FakeResponse(url)), url, hosts, marker)
                self.assertIn("非岗位核验", result["status"])

    def test_external_redirect_rejected(self):
        url, hosts, marker = ENTRANCES["汽车之家"]
        session = FakeSession(FakeResponse("https://other.example/jobs"))
        with self.assertRaises(ValueError):
            check_entrance(session, url, hosts, marker)

    def test_missing_marker_is_unverified_not_unreachable(self):
        url, hosts, marker = ENTRANCES["搜狐"]
        result = check_entrance(
            FakeSession(FakeResponse(url, "普通公开招聘页面，岗位动态加载")),
            url, hosts, marker,
        )
        self.assertFalse(result["internship_marker_in_html"])
        self.assertIn("待浏览器复核", result["status"])
        self.assertEqual(result["http_status"], 200)

    def test_monitor_does_not_change_jobs_and_existing_source_attempts(self):
        original_job = {"id": "stored-job", "status": "历史已核验"}
        existing_attempt = {"status": "成功（当前接口）", "checked": "2026-10-14"}
        data = {"jobs": [original_job.copy()], "source_attempts": {
            "腾讯": existing_attempt.copy()
        }}
        # All check a generic marker and official destination.
        class MatchSession:
            def get(self, url, **kwargs):
                return FakeResponse(url)
        update_directory_audits(data, session=MatchSession(), today="2026-10-16")
        self.assertEqual(data["jobs"], [original_job])
        self.assertEqual(data["source_attempts"]["腾讯"], existing_attempt)
        self.assertEqual(set(data["directory_attempts"]), set(ENTRANCES))
        self.assertFalse(any("在招职位" in x.get("status", "")
                             for x in data["directory_attempts"].values()))


if __name__ == "__main__":
    unittest.main()
