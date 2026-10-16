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


    def test_refreshed_tal_graduation_limit_replaces_stale_auto_import(self):
        from daily_scope import eligible_jobs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            key = "tal-moka-123e4567-e89b-12d3-a456-426614174000"
            original = {
                "id": key, "company": "好未来", "first_seen": "2026-10-14",
                "checked": "2026-10-14", "title": "AI产品实习生",
                "source": "好未来官网 Moka 校园招聘",
                "verify": "官网详情（剩余名额待确认）",
                "graduation": "未核实", "requirements": "待核",
            }
            (root / "jobs.json").write_text(
                json.dumps({"snapshot": "2026-10-14", "jobs": [original],
                            "source_attempts": {}, "source_audits": {}}),
                encoding="utf-8",
            )
            records = [{"id": "123e4567-e89b-12d3-a456-426614174000"}]
            meta = {"reported": 1, "raw_records": 1, "unique_ids": 1}
            updated = dict(original, graduation="仅招2027届毕业生",
                           requirements="仅招2027届毕业生")
            with (
                patch.object(refresh_sources, "ROOT", root),
                patch.object(refresh_sources, "SOURCES",
                             {"好未来": lambda session: (records, meta)}),
                patch.object(refresh_sources, "normalize", return_value=[updated]),
                patch("sys.argv", ["refresh_sources.py", "--sources", "tal-moka"]),
            ):
                refresh_sources.main()
            data = json.loads((root / "jobs.json").read_text(encoding="utf-8"))
            self.assertEqual(data["jobs"][0]["graduation"], "仅招2027届毕业生")
            self.assertEqual(eligible_jobs(data["jobs"]), [])
            self.assertEqual(data["source_attempts"]["好未来"]["candidate_count"], 1)


    def test_complete_tal_capture_hides_missing_autojob_and_reactivates(self):
        from daily_scope import eligible_jobs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            key = "tal-moka-123e4567-e89b-12d3-a456-426614174000"
            original = {
                "id": key, "company": "好未来", "first_seen": "2026-10-14",
                "source": "好未来官网 Moka 校园招聘",
                "verify": "官网详情（剩余名额待确认）",
                "title": "AI教育产品实习生", "summary": "大模型产品设计",
                "graduation": "未核实",
            }
            (root / "jobs.json").write_text(json.dumps({
                "snapshot": "2026-10-14", "jobs": [original],
                "source_attempts": {}, "source_audits": {},
            }), encoding="utf-8")
            meta = {"reported": 1, "raw_records": 1, "unique_ids": 1}
            collector = {"好未来": lambda session: ([{"id": key[9:]}], meta)}
            with (
                patch.object(refresh_sources, "ROOT", root),
                patch.object(refresh_sources, "SOURCES", collector),
                patch.object(refresh_sources, "normalize", return_value=[]),
                patch("sys.argv", ["refresh_sources.py", "--sources", "tal-moka"]),
            ):
                refresh_sources.main()
            db = json.loads((root / "jobs.json").read_text(encoding="utf-8"))
            self.assertTrue(db["jobs"][0]["listing_inactive"])
            self.assertEqual(eligible_jobs(db["jobs"]), [])
            self.assertEqual(db["source_attempts"]["好未来"]["reported"], 1)

            with (
                patch.object(refresh_sources, "ROOT", root),
                patch.object(refresh_sources, "SOURCES", collector),
                patch.object(refresh_sources, "normalize",
                             return_value=[original.copy()]),
                patch("sys.argv", ["refresh_sources.py", "--sources", "tal-moka"]),
            ):
                refresh_sources.main()
            db = json.loads((root / "jobs.json").read_text(encoding="utf-8"))
            self.assertNotIn("listing_inactive", db["jobs"][0])
            self.assertEqual(len(eligible_jobs(db["jobs"])), 1)


if __name__ == "__main__":
    unittest.main()
