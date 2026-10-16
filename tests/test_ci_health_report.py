"""Regression report must not claim scraping or deployment succeeded."""
import unittest
from ci_health_report import build_report, summarize_log


class CiHealthReportTests(unittest.TestCase):
    def test_passed_run_is_explicitly_offline_only(self):
        report = build_report(
            "success", "abc123", "Ran 42 tests in 0.1s\nOK", "992",
            checked_at="2026-10-16T00:00:00+00:00")
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["source_sha"], "abc123")
        self.assertIn("does not prove website scraping", report["disclaimer"])
        self.assertEqual(report["github_run_id"], "992")

    def test_failed_and_skipped_outcomes_are_distinct(self):
        failing = build_report(
            "failure", "def123",
            "ERROR: test_parser\nTraceback (most recent call last):\n"
            "ValueError: bad record\nFAILED (errors=1)")
        self.assertEqual(failing["status"], "failed")
        self.assertTrue(any("test_parser" in line
                            for line in failing["log_highlights"]))
        skipped = build_report("skipped", "def123")
        self.assertEqual(skipped["status"], "not_run")

    def test_log_highlights_are_bounded(self):
        log = "\n".join("FAIL: test_" + str(i) for i in range(60))
        self.assertLessEqual(len(summarize_log(log)), 12)


if __name__ == "__main__":
    unittest.main()
