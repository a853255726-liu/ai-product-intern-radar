"""Conservative discovery-level screening for AI/product internship candidates.

The source-specific collector should preserve the full raw feed first.  This
function admits PM/strategy roles and adjacent AI roles whose *duties* contain
concrete product work. It is not a final suitability judgment.
"""
import re

TITLE_PRODUCTS = re.compile(
    r"产品|用户研究|体验研究|产品策略|增长策略|体验运营|模型评测|Agent评测",
    re.I,
)
AI_SIGNALS = re.compile(
    r"\bAI\b|AIGC|Agent|LLM|RAG|MCP|大模型|生成式|智能体|模型评测|"
    r"机器学习|推荐系统|智能应用",
    re.I,
)
PRODUCT_WORK = re.compile(
    r"产品(?:需求|设计|规划|方案|迭代|功能|策略|体验|分析)|"
    r"需求(?:分析|调研|文档|梳理|评审)|"
    r"PRD|用户(?:调研|访谈|研究|体验|反馈)|"
    r"功能(?:设计|迭代|规划)|"
    r"原型设计|交互方案|体验评测|"
    r"产品经理|竞品分析|产品路线",
    re.I,
)
# Title exclusions are narrow, to avoid suppressing a legitimate AI PM role
# just because the JD discusses engineering collaboration.
NON_PRODUCT_TITLE = re.compile(
    r"工程师|前端实习|后端实习|PE实习|数据科学|算法|开发实习|测试开发|"
    r"数据标注|训练师|模型研究|配音导演|内容创意|"
    r"活动运营|商家及供给运营|销售专员|招聘专员|人力资源|"
    r"视觉设计师|平面设计师|法务|财务|行政实习",
    re.I,
)


def is_product_candidate(title, duty="", category=""):
    title, duty, category = str(title or ""), str(duty or ""), str(category or "")
    if NON_PRODUCT_TITLE.search(title):
        return False
    # Elite research programmes without a product title are R&D leads, not PM.
    if "Ace顶尖实习生" in title or ("Ace 顶尖实习生" in category and "产品" not in title):
        return False
    ai = bool(AI_SIGNALS.search(title + " " + duty))
    # Pure operations and generic growth roles require clear AI context.
    if re.search(r"产品运营|增长策略|体验运营", title) and not ai:
        return False
    if TITLE_PRODUCTS.search(title):
        return True
    # Do not treat a generic AI mention or the use of AI tools as PM work:
    # there must be explicit product responsibility, not just a model keyword.
    return bool(ai and PRODUCT_WORK.search(duty))
