"""Basic structural checks for site publishing."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class DashboardTests(unittest.TestCase):
    def test_jobs_have_unique_ids(self):
        jobs = json.loads((ROOT/"jobs.json").read_text("utf-8"))["jobs"]
        self.assertTrue(jobs)
        self.assertEqual(len(jobs),len({str(j["id"]) for j in jobs}))

    def test_site_has_data(self):
        html=(ROOT/"index.html").read_text("utf-8")
        self.assertIn("INITIAL_DATA=",html)
        self.assertIn("北京 AI 产品实习",html)
        self.assertNotIn("__DATA__",html)

    def test_template_not_overwritten(self):
        self.assertIn("__DATA__",(ROOT/"template.html").read_text("utf-8"))

if __name__ == "__main__":
    unittest.main()
