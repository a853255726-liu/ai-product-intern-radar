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

    def test_model_research_and_frontend_roles_are_not_product(self):
        self.assertFalse(is_product_candidate(
            "前端实习生（AI开放平台）", "参与AI辅助创建链路的产品化"))
        self.assertFalse(is_product_candidate(
            "大模型评测研究与模型研究实习生", ""))

    def test_pure_ops_requires_ai_product_scope(self):
        self.assertFalse(is_product_candidate("零售产品运营实习生"))
        self.assertFalse(is_product_candidate("活动运营实习生", "AI工具协助制作活动物料"))

    def test_ai_product_operations_remain_eligible(self):
        self.assertTrue(is_product_candidate(
            "AI 产品运营实习生", "参与智能体产品需求设计与效果评测"))

    def test_kimi_r_and_d_and_design_are_not_pm(self):
        for title in (
            "后端研发实习生（Agent 产品工程方向）",
            "【实习生】Research Scientist, Life Sciences",
            "ai for engineering eval intern（汽车方向）",
            "增长团队管培生",
            "设计实习生",
        ):
            with self.subTest(title=title):
                self.assertFalse(is_product_candidate(
                    title, "参与 Agent 产品需求分析和用户调研"))

    def test_kimi_agent_and_eval_product_roles_survive(self):
        self.assertTrue(is_product_candidate(
            "AI harness 产品实习生", "负责 Agent 产品设计、评测和需求分析"))
        self.assertTrue(is_product_candidate(
            "体验运营实习生（Harness业务方向）",
            "使用 Agent 平台做产品体验分析和需求反馈"))

if __name__ == "__main__":
    unittest.main()
