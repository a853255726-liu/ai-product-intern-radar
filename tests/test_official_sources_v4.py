"""Regression tests for corrected JD/Baidu public APIs and Feishu SSR."""
import unittest
from unittest.mock import patch
from refresh_sources import jd, baidu, normalize
from feishu_sources import parse_list_html, collect_feishu, normalize_feishu

def feishu_fixture(total, *jobs):
    cards = ""
    for id_, title, place, nature, desc in jobs:
        cards += (f'<a data-id="{id_}" href="/index/position/{id_}/detail">'
                  f'<span class="positionItem-title-text">{title}</span>'
                  f'<div class="positionItem-subTitle"><span>{place}</span>'
                  f'<span>{nature}</span></div>'
                  f'<div class="positionItem-jobDesc">{desc}</div></a>')
    return f"<html><body>开启新的工作（{total}）{cards}</body></html>"

class FakeResponse:
    status_code = 200
    def __init__(self, value, json_mode=True): self.value=value; self.json_mode=json_mode
    def raise_for_status(self): return None
    def json(self): return self.value
    @property
    def text(self): return self.value if isinstance(self.value,str) else ""

class OfficialSourcesTests(unittest.TestCase):
    def test_jd_internship_type_and_nested_city(self):
        call=[]
        def api(session,method,url,payload,ref):
            call.append(url)
            return {"body":{"totalNumber":1,"items":[{
                "publishId":7641,"positionName":"AI 技术产品经理",
                "workContent":"负责AI产品效果评测","qualification":"每周4天",
                "requirementVoList":[{"workCity":"北京市-北京市"}],
                "publishTime":1775009610000,"jobDirection":"产品"}]}}
        with patch("refresh_sources.request_json",api):
            rows,audit=jd(None)
        self.assertIn("type=internship",call[0])
        self.assertEqual(audit["unique_ids"],1)
        posts=normalize("京东",rows)
        self.assertEqual(len(posts),1)
        self.assertEqual(posts[0]["id"],"jd-7641")
        self.assertIn("北京",rows[0]["requirementVoList"][0]["workCity"])
        self.assertIn("job/detail?publishId=7641",posts[0]["link"])
        self.assertIn("AI产品",posts[0]["summary"])

    def test_baidu_encoded_form_and_product_city(self):
        class Session:
            def post(self,url,data,headers,timeout):
                self.url=url; self.data=data; self.headers=headers
                return FakeResponse({"status":"ok","data":{"total":"1","list":[{
                    "postId":"uuid-123","name":"AI产品经理实习生（J106390）",
                    "workPlace":"北京市","workContent":"大模型效果评测与产品设计",
                    "serviceCondition":"在校生每周4天",
                    "publishDate":"2026-10-09"}]}})
        sess=Session()
        rows,meta=baidu(sess)
        self.assertEqual(sess.data["curPage"],"1")
        self.assertEqual(sess.data["postType"],"2")
        self.assertIn("form-urlencoded",sess.headers["Content-Type"])
        self.assertEqual(meta["reported"],1)
        self.assertEqual(normalize("百度",rows)[0]["id"],"baidu-uuid-123")

    def test_feishu_ssr_reconcile(self):
        html=feishu_fixture(2,
            ("123","AI Agent产品实习生","北京","实习","面向AI Agent产品设计"),
            ("124","研发工程师","北京","实习","模型开发"))
        count,rows=parse_list_html(html,"https://01ai.jobs.feishu.cn")
        self.assertEqual(count,2);self.assertEqual(len(rows),2)
        jobs=normalize_feishu("零一万物",rows,lambda:"2026-10-13")
        self.assertEqual(len(jobs),1)
        class Session:
            def get(self,url,headers,timeout):
                self.url=url
                return FakeResponse(html)
        result,audit=collect_feishu(Session(),"零一万物")
        self.assertEqual(audit["reported"],2)
        self.assertEqual(len(result),2)

    def test_feishu_fail_closed_on_duplicates_and_zero(self):
        html=feishu_fixture(2,("11","AI产品实习","北京","实习","AI Agent"))
        class Session:
            def get(self,url,headers,timeout):return FakeResponse(html)
        with self.assertRaises(ValueError):
            collect_feishu(Session(),"MiniMax",max_pages=2)
        with self.assertRaises(ValueError):
            parse_list_html("<html>开启新的工作（0）</html>", "https://01ai.jobs.feishu.cn")

    def test_feishu_no_external_links(self):
        html='<html>开启新的工作（1）<a data-id="123" href="https://evil.example/position/123/detail"><span class="positionItem-title-text">AI产品实习</span><div class="positionItem-subTitle">北京 实习</div></a></html>'
        count,rows=parse_list_html(html,"https://01ai.jobs.feishu.cn")
        self.assertEqual(count,1)
        self.assertEqual(rows,[])

if __name__=="__main__":
    unittest.main()
