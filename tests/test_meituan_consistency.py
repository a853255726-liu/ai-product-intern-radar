"""Meituan's moving pages must be retried, never made complete by dropping IDs."""
import unittest
from unittest.mock import patch
from refresh_sources import meituan


class MeituanConsistencyTests(unittest.TestCase):
    def test_first_duplicate_retries_full_snapshot(self):
        with patch("refresh_sources.collect", side_effect=[
                ValueError("美团: reported=363 retrieved=363 unique=362"),
                ([{"jobUnionId": "1"}], {
                    "reported": 1, "unique_ids": 1, "pages": 1})
        ]) as collector, patch("refresh_sources.time.sleep") as sleeper:
            records, audit = meituan(object())
        self.assertEqual([x["jobUnionId"] for x in records], ["1"])
        self.assertEqual(audit["unique_ids"], 1)
        self.assertEqual(collector.call_count, 2)
        sleeper.assert_called_once()

    def test_persistent_duplicate_fails_closed(self):
        with patch("refresh_sources.collect", side_effect=ValueError(
                "美团: reported=363 retrieved=363 unique=362")) as collector, (
                patch("refresh_sources.time.sleep")):
            with self.assertRaises(ValueError):
                meituan(object())
        self.assertEqual(collector.call_count, 3)

    def test_other_invalid_schema_not_retried(self):
        with patch("refresh_sources.collect",
                   side_effect=ValueError("美团: missing list")) as collector:
            with self.assertRaises(ValueError):
                meituan(object())
        collector.assert_called_once()


if __name__ == "__main__":
    unittest.main()
