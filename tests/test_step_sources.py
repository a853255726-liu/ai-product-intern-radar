import unittest
from kimi_sources import parse_list_html
from step_sources import BASE, normalize_step
from official_links import classify_link
from refresh_sources import KEYS

UID = "38407e0b-85e3-47b8-b8de-e58904f3825e"
URL = BASE + "#/job/" + UID

class StepMokaTests(unittest.TestCase):
    def test_official_route(self):
        self.assertEqual(KEYS["step-moka"], "阶跃星辰")
        self.assertEqual(classify_link(URL), "official_detail")
        self.assertNotEqual(classify_link(BASE+"#/jobs/?page=1"), "official_detail")

    def test_uses_shared_moka_parser(self):
        html = ('<div>已选 0 条件 | 1 结果</div>'
                '<div class="results-X"><div class="jobs-Y">'
                '<div class="container-A"><a href="#/job/'+UID+'">'
                '<span class="title-ab target-color-container">AI 产品实习生</span>'
                '<div class="sd-Ellipsis-hiddenContent-a">实习</div>'
                '<div class="sd-Ellipsis-hiddenContent-a">产品/运营</div>'
                '<div class="sd-Ellipsis-hiddenContent-a">北京市</div>'
                '</a></div></div></div>')
        count, rows = parse_list_html(html, base=BASE)
        self.assertEqual(count, 1)
        self.assertEqual(rows[0]["url"], URL)

    def test_full_time_and_wrong_city_excluded(self):
        row = dict(id=UID,title="AI 产品设计师（实习生）", url=URL,
                   tags=["全职","设计/视觉","北京市"],date="",
                   description="负责 Agent 产品功能设计，用户调研与需求分析。")
        self.assertEqual(normalize_step([row], lambda:"2026-10-14"), [])
        row.update(tags=["实习","产品/运营","上海市"])
        self.assertEqual(normalize_step([row], lambda:"2026-10-14"), [])
        row.update(tags=["实习","产品/运营","北京市"])
        self.assertEqual(len(normalize_step([row],lambda:"2026-10-14")),1)

if __name__=="__main__":
    unittest.main()
