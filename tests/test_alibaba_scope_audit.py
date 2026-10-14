import unittest
from alibaba_sources import diagnose_alibaba

class AlibabaScopeAuditTests(unittest.TestCase):
    def test_graduate_only_feed_not_labelled_daily_internship(self):
        rows=[{"id":"100", "name":"AI产品经理", "batchName":"阿里巴巴2027届应届生",
               "workLocations":["北京"], "description":"负责Agent产品规划"}]
        report=diagnose_alibaba(rows)
        self.assertEqual(report["counts"]["explicit_internship"], 0)
        self.assertEqual(report["batch_names"]["阿里巴巴2027届应届生"], 1)
        self.assertIn("未覆盖日常实习",report["recruitment_scope"])

if __name__=="__main__":
    unittest.main()
