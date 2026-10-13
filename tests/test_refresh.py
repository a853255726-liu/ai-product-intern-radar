"""Pure offline tests: no external recruitment website requests."""
import unittest
from refresh_sources import collect, normalize

class CollectionTests(unittest.TestCase):
    def test_complete_page(self):
        rows, audit = collect("test", lambda page: {},
            lambda raw: ([{"id":1},{"id":2}], 2, "id"))
        self.assertEqual(len(rows), 2)
        self.assertEqual(audit["unique_ids"], 2)

    def test_duplicate_ids_are_not_complete(self):
        with self.assertRaises(ValueError):
            collect("test", lambda page: {}, lambda raw: ([{"id":1},{"id":1}],2,"id"))

    def test_missing_total_is_not_complete(self):
        with self.assertRaises(ValueError):
            collect("test",lambda page: {},lambda raw: ([{"id":1}],None,"id"))

    def test_beijing_and_product_filter(self):
        records = [{"positionId":101,"positionName":"AI Agent 产品实习生",
            "workplace":"北京市","publishTime":"2026-10-13",
            "jobProjectName":"日常实习项目","recruitStatus":"in_recruitment",
            "duty":"大模型产品设计与评测","qualification":"Python"},
            {"positionId":102,"positionName":"算法工程师实习生",
            "workplace":"北京市","jobProjectName":"其他项目","recruitStatus":"in_recruitment"},
            {"positionId":103,"positionName":"AI 产品实习生",
            "workplace":"上海市","jobProjectName":"其他项目","recruitStatus":"in_recruitment"}]
        results = normalize("小红书", records)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "xhs-101")

if __name__ == "__main__":
    unittest.main()
