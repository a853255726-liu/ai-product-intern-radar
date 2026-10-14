"""DP Technology Feishu public recruitment source contracts."""
import unittest
from feishu_sources import PORTALS, COMPANY_CODES, list_url, parse_list_html, normalize_feishu
from refresh_sources import KEYS
from official_links import classify_link

JOB = "7611105993640741170"
BASE = "https://dptechnology.jobs.feishu.cn"

class DPTechnologyTests(unittest.TestCase):
    def test_official_source_registered(self):
        self.assertEqual(KEYS["feishu-dptechnology"], "深势科技")
        self.assertEqual(COMPANY_CODES["深势科技"], "dptechnology")
        self.assertEqual(PORTALS["深势科技"][1], "/index/position/list")
        self.assertIn("current=2&limit=10", list_url("深势科技", 2, 10))
        self.assertEqual(classify_link(BASE + "/index/position/" + JOB + "/detail"),
                         "official_detail")

    def test_product_intern_in_beijing_not_engineer(self):
        html = ('<html><body>开启新的工作（2）'
                '<a data-id="'+JOB+'" href="/index/position/'+JOB+'/detail">'
                '<span class="positionItem-title-text">产品实习生</span>'
                '<div class="positionItem-subTitle"><span>北京</span><span>实习</span></div>'
                '<div class="positionItem-jobDesc">围绕AI for Science科研教育场景，参与用户研究、PRD 和产品设计</div></a>'
                '<a data-id="7611105993640741171" href="/index/position/7611105993640741171/detail">'
                '<span class="positionItem-title-text">AI4S算法工程师实习生</span>'
                '<div class="positionItem-subTitle"><span>北京</span><span>实习</span></div>'
                '<div class="positionItem-jobDesc">AI模型训练工程开发</div></a>'
                '</body></html>')
        total,records = parse_list_html(html, BASE)
        self.assertEqual(total,2)
        self.assertEqual(len(records),2)
        accepted = normalize_feishu("深势科技",records,lambda:"2026-10-14")
        self.assertEqual(len(accepted),1)
        self.assertEqual(accepted[0]["title"],"产品实习生")
        self.assertIn("/index/position/"+JOB+"/detail",accepted[0]["link"])
        # The same employer publishes contest-only roles, which must not be
        # advertised as generally open daily internships.
        contest = dict(records[0])
        contest["id"] = "7611105993640741172"
        contest["title"] = "【比赛专用】产品实习生"
        contest["url"] = BASE + "/index/position/7611105993640741172/detail"
        self.assertEqual(normalize_feishu("深势科技", [contest], lambda:"2026-10-14"), [])

if __name__ == "__main__":
    unittest.main()
