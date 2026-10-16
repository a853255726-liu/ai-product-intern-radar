"""Offline safety contracts for Sohu's actual Moka internship programme 28313."""
import unittest
from sohu_sources import (
    BASE, HOME, list_url, cities_from_home, is_beijing, normalize_sohu,
)
from official_links import classify_link
from refresh_sources import KEYS, SOURCES
from daily_scope import eligible_jobs

UUID="7e078123-8764-4b6c-8a21-905680360bd5"

def candidate(title="AI 产品实习生（评测方向）",city="北京市",description=None):
    return {
        "id":UUID,"url":BASE+"#/job/"+UUID,"title":title,
        "tags":["产品技术中心"],"official_city":city,
        "description":description or
            "参与AIGC评测集的筛选、构建与维护；大模型AI自动评估，"
            "编写产品调研分析。本科及以上在校生，熟悉模型评测。",
        "date":"2026-10-15",
    }

class SohuSourceTests(unittest.TestCase):
    def test_employer_programme_is_not_2027_graduate_batch(self):
        self.assertEqual(BASE,
                         "https://app.mokahr.com/campus-recruitment/sohu/28313")
        self.assertIn("/28313",HOME)
        self.assertIn("/28313",list_url(2))
        self.assertEqual(KEYS["sohu-moka"],"搜狐")
        self.assertIn("搜狐",SOURCES)
        self.assertEqual(classify_link(BASE+"#/job/"+UUID),"official_detail")

    def test_landing_city_labels_are_official_evidence(self):
        text=("热招职位\n急\n数据产品实习生\n北京市\n"
              "急\n华东销售实习生\n上海市\n"
              "急\nAI 产品实习生（评测方向）\n北京市\n")
        result=cities_from_home(text)
        self.assertEqual(result["数据产品实习生"],"北京市")
        self.assertEqual(result["华东销售实习生"],"上海市")

    def test_beijing_ai_eval_intern_is_publishable(self):
        jobs=normalize_sohu([candidate()],lambda:"2026-10-16")
        self.assertEqual(len(jobs),1)
        self.assertEqual(jobs[0]["id"],"sohu-moka-"+UUID)
        self.assertEqual(len(eligible_jobs(jobs)),1)
        self.assertEqual(jobs[0]["link"],BASE+"#/job/"+UUID)
        self.assertIn("评测",jobs[0]["track"])

    def test_no_city_assumption_from_beijing_university_preference(self):
        row=candidate(city="",description="AI 产品评测。北京本地高校优先。")
        self.assertFalse(is_beijing(row))
        self.assertEqual(normalize_sohu([row],lambda:"2026-10-16"),[])
        self.assertEqual(normalize_sohu(
            [candidate(city="上海市")],lambda:"2026-10-16"),[])

    def test_graduate_restrictions_and_non_ai_roles_fail_closed(self):
        sample=[
            candidate(title="【2027】AI 产品实习生"),
            candidate(description="负责AI大模型评测。仅招2027届毕业生。"),
            candidate(title="普通产品实习生",description="只参与基本后台功能文档整理"),
            candidate(title="AI算法工程师实习生"),
        ]
        self.assertEqual(normalize_sohu(sample,lambda:"2026-10-16"),[])

if __name__=="__main__":
    unittest.main()
