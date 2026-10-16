"""Guard the visible distinction between coverage and collection freshness."""
import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SourceCoverageExportTests(unittest.TestCase):
    def test_csv_reports_last_attempt_separately(self):
        with (ROOT / "company_coverage.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            reader = csv.DictReader(stream)
            self.assertIn("覆盖状态", reader.fieldnames)
            self.assertIn("最近自动采集状态", reader.fieldnames)
            self.assertIn("最近自动采集日期", reader.fieldnames)
            rows = list(reader)
        self.assertGreaterEqual(len(rows), 25)
        keyed = {row["企业"]: row for row in rows}
        for name in ("美团", "智谱", "好未来", "OPPO"):
            self.assertIn(name, keyed)
            self.assertTrue(keyed[name]["最近自动采集状态"])
        self.assertEqual(len(keyed), len(rows))


if __name__ == "__main__":
    unittest.main()
