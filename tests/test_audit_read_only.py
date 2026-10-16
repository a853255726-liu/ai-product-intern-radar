"""Ensure audit-only probes never overwrite committed or cached job data."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import refresh_sources


class AuditModeTests(unittest.TestCase):
    def test_successful_audit_does_not_write_jobs_or_raw_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            jobs_path = root / "jobs.json"
            original = {"snapshot": "2026-01-01", "jobs": [], "source_audits": {}}
            jobs_path.write_text(json.dumps(original), encoding="utf-8")
            before = jobs_path.read_bytes()
            meta = {
                "reported": 0, "raw_records": 0, "unique_ids": 0,
                "pages": 1, "page_sizes": [0], "failed_pages": 0,
            }
            fake_sources = {"小米": lambda _: ([], meta)}
            with (
                patch.object(refresh_sources, "ROOT", root),
                patch.object(refresh_sources, "SOURCES", fake_sources),
                patch("sys.argv", ["refresh_sources.py", "--sources", "xiaomi", "--audit-only"]),
            ):
                refresh_sources.main()
            self.assertEqual(jobs_path.read_bytes(), before)
            self.assertFalse((root / "data").exists())


    def test_failed_normalizer_must_not_record_a_valid_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "jobs.json").write_text(
                json.dumps({"snapshot": "2026-01-01", "jobs": [],
                            "source_attempts": {}, "source_audits": {}}),
                encoding="utf-8",
            )
            valid_meta = {"reported": 1, "raw_records": 1, "unique_ids": 1}
            with (
                patch.object(refresh_sources, "ROOT", root),
                patch.object(refresh_sources, "SOURCES",
                             {"OPPO": lambda session: ([{"id": "123"}], valid_meta)}),
                patch.object(refresh_sources, "normalize",
                             side_effect=ValueError("bad job record")),
                patch("sys.argv", ["refresh_sources.py", "--sources", "oppo-daily"]),
            ):
                with self.assertRaises(SystemExit):
                    refresh_sources.main()
            db = json.loads((root / "jobs.json").read_text(encoding="utf-8"))
            self.assertNotIn("OPPO", db["source_audits"])
            self.assertTrue(db["source_attempts"]["OPPO"]["status"].startswith("失败"))
            self.assertFalse((root / "data" / "raw" / "OPPO_latest.json").exists())


if __name__ == "__main__":
    unittest.main()
