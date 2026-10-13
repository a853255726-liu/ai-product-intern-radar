"""Regression tests: user explicitly wants only Beijing DAILY internships."""
import unittest

from daily_scope import classify, daily_jobs


class DailyScopeTest(unittest.TestCase):
    def test_excludes_retention_and_graduate_projects(self):
        self.assertEqual(classify({"id":"kuaishou-11245","company":"快手",
            "title":"【留用实习】AI Agent产品经理"}),"non_daily")
        self.assertEqual(classify({"id":"tencent-1224696104600437761","company":"腾讯",
            "title":"技术产品经理（应届实习）"}),"non_daily")
        self.assertEqual(classify({"id":"xhs-20413","company":"小红书",
            "title":"AI × 社区 RPT 产品培训生（Ace）"}),"non_daily")

    def test_accepts_explicit_daily_sources(self):
        self.assertEqual(classify({"id":"baidu-J103757","company":"百度","title":"AI产品经理实习生"}),"daily")
        self.assertEqual(classify({"id":"tencent-1284862486247711744","company":"腾讯",
            "title":"AI 产品经理（日常实习）"}),"daily")
        self.assertEqual(classify({"id":"iqiyi-A15887","company":"爱奇艺",
            "title":"海外后台产品设计实习生"}),"daily")

    def test_keeps_unlabeled_general_internships_off_public_site(self):
        self.assertEqual(classify({"id":"xhs-22507","company":"小红书",
            "title":"AI点点产品实习生"}),"unverified")
        self.assertEqual(classify({"id":"zhipu-7618869280079628554","company":"智谱",
            "title":"内部产品助理实习生"}),"unverified")
        self.assertEqual(len(daily_jobs([
            {"id":"kuaishou-11245","company":"快手","title":"留用实习AI产品"},
            {"id":"baidu-J103757","company":"百度","title":"AI产品实习"}
        ])),1)

    def test_new_daily_project_with_evidence(self):
        self.assertEqual(classify({"id":"bytedance-7673733057043712261",
           "company":"字节跳动","title":"AI产品实习",
           "internship_kind":"daily","daily_evidence":"第三方JD明确日常实习"}),"daily")
        self.assertEqual(classify({"id":"future","company":"XX","title":"AI产品实习",
           "internship_kind":"daily"}),"unverified")


if __name__ == "__main__":
    unittest.main()
