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
            with patch.object(refresh_sources, "ROOT", root), \\
                 patch.object(refresh_sources, "SOURCES", fake_sources), \\
                 patch("sys.argv", ["refresh_sources.py", "--sources", "xiaomi", "--audit-only"]):
                refresh_sources.main()
            self.assertEqual(jobs_path.read_bytes(), before)
            self.assertFalse((root / "data").exists())


if __name__ == "__main__":
    unittest.main()
