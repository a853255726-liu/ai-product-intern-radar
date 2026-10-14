"""Direct official-detail links are a separate guarantee from source provenance."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

from official_links import classify_link, enrich_job, enrich_jobs, _specific_official

ROOT=Path(__file__).resolve().parent.parent

class OfficialJobLinkTests(unittest.TestCase):
    def test_verified_patterns(self):
        examples=[
            "https://zhaopin.meituan.com/web/position/detail?jobUnionId=4138099640&highlightType=campus",
            "https://job.xiaohongshu.com/campus/position/22656",
            "https://talent.baidu.com/jobs/detail/INTERN/0ad545f8-07df-42f1-9a10-28e79d5dc407",
            "https://join.qq.com/post_detail.html?postid=1284862486247711744",
            "https://campus.jd.com/#/details?id=4910",
            "https://campus.kuaishou.cn/recruit/campus/e/#/campus/jobs?positionId=11462",
            "https://jobs.mihoyo.com/#/campus/position/12345678",
            "https://careers.iqiyi.com/intern/position/7684155985208953134/detail",
            "https://xiaomi.jobs.f.mioffice.cn/internship/position/7687421651307219238/detail",
            "https://zhipu-ai.jobs.feishu.cn/index/position/7614090220368152874/detail",
            "https://realai.jobs.feishu.cn/272867/position/7208016656676669707/detail",
            "https://jobs.bytedance.com/campus/position/7673733057043712261/detail",
            "https://hr.meitu.com/en/jobIntern/d21c3fc8-d9dc-43ee-b71b-b3d59dca7517"
        ]
        for url in examples:
            with self.subTest(url=url):
                self.assertEqual(classify_link(url),"official_detail")

    def test_bad_links_never_appear_as_direct_job_detail(self):
        examples=[
            "https://campus.jd.com/#/job/detail?publishId=4910",
            "https://join.qq.com/post_detail.html?postid=-3",
            "https://talent.baidu.com/jobs/list?recruitType=INTERN",
            "https://iq.jobs.feishu.cn/intern/m/",
            "https://ke.zhiye.com/jobs",
            "https://agechild.com/company/360",
            "https://example.com/position/777/detail",
            "javascript:alert(1)",
            "https://join.qq.com.evil.invalid/post_detail.html?postid=123",
        ]
        for url in examples:
            with self.subTest(url=url):
                self.assertNotEqual(classify_link(url),"official_detail")

    def test_jd_404_route_migrated(self):
        old="https://campus.jd.com/#/job/detail?publishId=4910"
        row=enrich_job({"id":"jd-4910","title":"技术产品经理","link":old})
        new="https://campus.jd.com/#/details?id=4910"
        self.assertEqual(row["official_detail_url"],new)
        self.assertEqual(row["link"],new)
        self.assertEqual(enrich_job(row)["official_detail_url"],new)

    def test_provenance_not_camouflaged(self):
        src="https://www.nowcoder.com/jobs/detail/456133"
        row=enrich_job({"id":"siliconflow-1","title":"产品实习生","link":src})
        self.assertNotIn("official_detail_url",row)
        self.assertEqual(row["source_url"],src)
        self.assertEqual(row["link_kind"],"external_source")
        row=enrich_job({"id":"baidu-J106390","title":"AI产品实习","link":"https://talent.baidu.com/jobs/list?recruitType=INTERN"})
        self.assertNotIn("official_detail_url",row)
        self.assertEqual(row["link_kind"],"official_list")

    def test_real_master_urls_are_properly_typed(self):
        data=json.loads((ROOT/"jobs.json").read_text("utf-8"))
        rows=enrich_jobs(data["jobs"])
        self.assertEqual(len(rows),len(data["jobs"]))
        for row in rows:
            with self.subTest(id=row["id"]):
                self.assertIn(row["link_kind"],{"official_detail","official_list","external_source","invalid"})
                if row["link_kind"]=="official_detail":
                    self.assertTrue(_specific_official(row["official_detail_url"]))
                    self.assertEqual(row["link"],row["official_detail_url"])
                else:
                    self.assertFalse(row.get("official_detail_url"))
                    self.assertTrue(row["link_check"])
        self.assertGreaterEqual(sum(x["link_kind"]=="official_detail" for x in rows), 200)

    @unittest.skipUnless(shutil.which("node"),"Node.js not installed")
    def test_inline_dashboard_javascript_is_syntactically_valid(self):
        html=(ROOT/"index.html").read_text("utf-8")
        matches=re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>",html)
        self.assertTrue(matches,"No inline script")
        for script in matches:
            check=subprocess.run(["node","--check","-"],input=script,
                                 text=True,capture_output=True)
            self.assertEqual(check.returncode,0,check.stderr[:1200])

if __name__=="__main__":
    unittest.main()
