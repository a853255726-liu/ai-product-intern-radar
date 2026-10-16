"""Conservative Huawei public campus page audit and internship scope contracts."""
import unittest
from huawei_sources import URL, parse_job_page, normalize_huawei
from refresh_sources import KEYS, SOURCES
from official_links import classify_link


def page(payload_id="103891", page=1, total=1, job_type="0",
         title="AI产品经理实习生", place="北京"):
    return {
        "status": 0,
        "data": {
            "pageVO": {
                "totalRows":total,"totalPages":total,
                "curPage":page,"pageSize":1,
            },
            "result": [{
                "jobId":payload_id,"jobName":title,
                "jobType":job_type,"workPlace":place,
                "categoryName":"产品类",
                "jobDesc":"负责大模型AI产品需求调研、PRD和Agent体验优化",
                "jobRequire":"每周4天在校生实习",
            }],
        },
    }


class HuaweiSourceTests(unittest.TestCase):
    def test_only_real_public_page_pagination_and_ids(self):
        jobs,info=parse_job_page(page(),expected_page=1)
        self.assertEqual(info["reported"],1)
        self.assertEqual(info["current_page"],1)
        self.assertEqual(jobs[0]["id"],"103891")
        with self.assertRaises(ValueError):
            parse_job_page(page(page=1,total=2),expected_page=2)
        with self.assertRaises(ValueError):
            parse_job_page(page(payload_id="unknown"))
        with self.assertRaises(ValueError):
            parse_job_page(page(total=800))

    def test_graduate_and_tech_posts_never_relabelled_as_intern(self):
        examples=[
            page()["data"]["result"][0],
        ]
        graduate={**examples[0],"jobName":"AI产品经理实习生","jobType":"0"}
        self.assertEqual(normalize_huawei([
            {"id":"123","title":graduate["jobName"],"jobType":"0",
             "workPlace":"北京","jobDesc":graduate["jobDesc"],
             "jobRequire":"测试"}],lambda:"2026-10-16"),[])
        candidate={
            "id":"123","title":"AI产品经理实习生","jobType":"1",
            "workPlace":"北京","jobDesc":"负责大模型Agent产品PRD",
            "jobRequire":"在校生实习"
        }
        good=normalize_huawei([candidate],lambda:"2026-10-16")
        self.assertEqual(len(good),1)
        self.assertEqual(good[0]["link"],URL)
        self.assertEqual(classify_link(good[0]["link"]),"official_list")
        self.assertEqual(normalize_huawei([
            {**candidate,"workPlace":"上海"}],lambda:"2026-10-16"),[])
        self.assertEqual(normalize_huawei([
            {**candidate,"title":"AI算法工程师实习生"}],lambda:"2026-10-16"),[])

    def test_not_marked_complete_integration(self):
        self.assertEqual(KEYS["huawei-browser"],"华为")
        self.assertIn("华为",SOURCES)
        self.assertEqual(classify_link(URL),"official_list")


if __name__=="__main__":
    unittest.main()
