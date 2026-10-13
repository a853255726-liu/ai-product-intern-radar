import unittest

from extra_sources import make_sources, normalize_extra


class ExtraSourceTests(unittest.TestCase):
    def setUp(self):
        self.today = lambda: "2026-10-13"

    def test_kuaishou_core_product_only(self):
        rows = [
            {"id": 11245, "name": "【留用实习】AI Agent产品经理",
             "positionNatureCode": "intern", "positionStatusCode": "Release",
             "workLocationDicts": [{"name": "北京"}],
             "description": "负责Agent产品规划、知识库和模型效果评测", "positionDemand": "本科及以上",
             "releaseTime": "2026-03-06 20:21:50"},
            {"id": 11453, "name": "【留用实习】平台产品经理-AI平台",
             "positionNatureCode": "intern", "positionStatusCode": "Release",
             "workLocationDicts": [{"name": "北京"}], "description": "AI平台产品"},
            {"id": 999, "name": "【留用实习】算法工程师-AI平台",
             "positionNatureCode": "intern", "positionStatusCode": "Release",
             "workLocationDicts": [{"name": "北京"}]},
            {"id": 998, "name": "产品经理-AI",
             "positionNatureCode": "fulltime", "positionStatusCode": "Release",
             "workLocationDicts": [{"name": "北京"}]},
            {"id": 997, "name": "产品经理-AI",
             "positionNatureCode": "intern", "positionStatusCode": "Release",
             "workLocationDicts": [{"name": "深圳"}]}
        ]
        result = normalize_extra("快手", rows, self.today)
        # The old retention-intern jobs must not pass the daily-only gate.
        self.assertEqual(result, [])
        daily = dict(rows[0], id=333, name="【日常实习】AI Agent产品经理")
        result = normalize_extra("快手", [daily], self.today)
        self.assertEqual([x["id"] for x in result], ["kuaishou-333"])
        self.assertEqual(result[0]["posted"], "2026-03-06")

    def test_mihoyo_excludes_algorithm(self):
        rows = [
            {"id": "1", "jobNatureId": 3, "title": "LLM算法实习生",
             "addressDetailList": [{"addressDetail": "北京"}]},
            {"id": "2", "jobNatureId": 1, "title": "AI产品经理",
             "addressDetailList": [{"addressDetail": "北京"}]},
            {"id": "3", "jobNatureId": 3, "title": "AI产品实习生",
             "addressDetailList": [{"addressDetail": "北京"}]}
        ]
        found = normalize_extra("米哈游", rows, self.today)
        self.assertEqual(found, [])  # Project type is not verified daily.
        daily = dict(rows[2], projectName="日常实习")
        self.assertEqual([x["id"] for x in normalize_extra("米哈游", [daily], self.today)], ["mihoyo-3"])

    def test_sources_reconcile_counts(self):
        def fetch_json(session, method, url, payload, ref):
            if "kuaishou.cn" in url:
                page = payload["pageNum"]
                return {"code": 0, "result": {
                    "total": 2, "list": [{"id": 1}] if page == 1 else [{"id": 2}]}}
            return {"success": True, "data": {"total": 0, "list": []}}
        def collect(name, one, unpack, max_pages=200):
            all_rows = []
            total = None
            for page in range(1, 4):
                records, n, pk = unpack(one(page))
                total = n
                all_rows.extend(records)
                if len(all_rows) == total:
                    break
            self.assertEqual(len({x[pk] for x in all_rows}), total)
            return all_rows, {"reported": total, "unique_ids": total,
                              "raw_records": total, "pages": page}
        feeds = make_sources(fetch_json, collect, self.today)
        rows, audit = feeds["快手"](None)
        self.assertEqual(len(rows), 2)
        self.assertEqual(audit["reported"], 2)
        rows, audit = feeds["米哈游"](None)
        self.assertEqual(rows, [])
        self.assertEqual(audit["reported"], 0)


if __name__ == "__main__":
    unittest.main()
