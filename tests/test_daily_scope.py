"""Regression tests for daily-FIRST, not daily-ONLY, recruitment."""
import unittest
from daily_scope import classify, eligible_jobs

class ScopeTests(unittest.TestCase):
    def test_daily_priority(self):
        self.assertEqual(classify({"id":"tencent-1284862486247711744","company":"腾讯",
            "title":"AI 产品经理（日常实习）"}),"daily")
        self.assertEqual(classify({"id":"baidu-J103757","company":"百度","title":"AI 产品实习"}),"daily")

    def test_retention_and_special_visible(self):
        self.assertEqual(classify({"id":"kuaishou-11245","company":"快手",
            "title":"【留用实习】AI Agent产品经理"}),"retention")
        self.assertEqual(classify({"id":"xhs-20413","company":"小红书",
            "title":"AI × 社区 RPT 产品培训生（Ace）"}),"special")
        self.assertEqual(classify({"id":"xhs-22507","company":"小红书",
            "title":"AI产品实习生","source":"企业官网"}),"general")
        self.assertEqual(classify({"id":"meituan-4691986310","company":"美团",
            "title":"【2027】Keeta-产品实习生"}),"special")

    def test_exclude_only_explicit_graduates(self):
        for req in ["仅招2027届应届毕业生", "只面向应届生", "仅限应届毕业生"]:
            self.assertEqual(classify({"id":"x","title":"AI产品实习生",
                "requirements":req}),"graduate_only")
        self.assertEqual(classify({"id":"tencent-1188988696721092608",
          "title":"产品策划（应届实习）","company":"腾讯"}),"graduate_only")
        for req in ["2027届及以后均可", "2028届实习专项", "应届生优先"]:
            self.assertNotEqual(classify({"id":"x","title":"产品实习生",
                "requirements":req}),"graduate_only")

    def test_negative_eligibility_notes_cannot_exclude(self):
        # The record saying "no graduate-only requirement seen" is not such a requirement.
        from daily_scope import eligible_jobs
        examples=[
            {"id":"xiaomi-a","company":"小米","title":"语音产品实习生",
             "graduation":"未见仅限应届", "verify":"第三方招聘平台"},
            {"id":"siliconflow-a","company":"硅基流动","title":"AIGC产品实习生",
             "graduation":"本科在读；未见只招应届",
             "note":"是否接受其他毕业年份需复核"},
            {"id":"zeroone-a","company":"零一万物","title":"Agent产品实习生",
             "graduation":"写2027届在读，非2027届资格待确认",
             "requirements":"2027届本科及以上在读",
             "note":"未写『仅限』，需联系HR"},
        ]
        self.assertEqual(len(eligible_jobs(examples)),3)

    def test_curated_visibility_and_technical_filter(self):
        rows=[
            {"id":"1","title":"AI 产品（日常实习）","company":"腾讯"},
            {"id":"2","title":"【留用实习】AI Agent 产品经理","company":"快手"},
            {"id":"3","title":"产品实习生","company":"小红书","graduation":"仅限应届毕业生"},
            {"id":"4","title":"LLM算法工程师实习生","company":"米哈游"},
        ]
        shown=eligible_jobs(rows)
        self.assertEqual([x["id"] for x in shown],["1","2"])
        self.assertEqual(shown[0]["internship_label"],"日常实习")
        self.assertEqual(shown[1]["internship_label"],"留用实习")

if __name__=="__main__":
    unittest.main()
