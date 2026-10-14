import unittest
from candidate_scope import is_product_candidate


class CandidateScopeTests(unittest.TestCase):
    def test_regular_pm_title_is_preserved(self):
        self.assertTrue(is_product_candidate("搜索平台产品实习生"))

    def test_ai_adjacent_role_with_product_work_is_discovered(self):
        self.assertTrue(is_product_candidate(
            "Agent 效果分析实习生", "负责产品需求分析、PRD 撰写与用户调研"))

    def test_generic_ai_tools_do_not_make_an_ops_role_pm(self):
        self.assertFalse(is_product_candidate(
            "行政实习生", "使用 AI 工具整理资料"))

    def test_engineering_is_not_relabelled_as_product(self):
        self.assertFalse(is_product_candidate(
            "AI 算法工程师", "与产品经理协同梳理产品需求"))

    def test_no_passing_ai_mention(self):
        self.assertFalse(is_product_candidate(
            "海外内容运营实习生", "熟练使用 AI 工具，更新排播表"))

    def test_user_research_adjacent(self):
        self.assertTrue(is_product_candidate("用户研究实习生"))

if __name__ == "__main__":
    unittest.main()
