"""Internship screening: prefer daily internships; exclude explicit graduate-only roles.

Do not treat 'not explicitly daily' as ineligible. Keep the job/project label
visible for the user, and retain unqualified records in the audit archive.
"""

import re

DAILY_IQIYI = {"iqiyi-A01585", "iqiyi-A10460", "iqiyi-A15887"}
# Historic Tencent mapping=2 is the graduating-cohort intern route, unlike daily mapping=104.
TENCENT_GRADUATING_COHORT_IDS = {
    "tencent-1224696104600437761", "tencent-1188988696721092608",
    "tencent-1153452731391100929", "tencent-1177660287764272128",
    "tencent-1212816229455368192", "tencent-1224696067023896576",
    "tencent-1226957086077102081",
}
DAILY_NAMES = {
    "daily": "日常实习",
    "general": "普通实习／类型待核",
    "retention": "留用实习",
    "special": "专项实习",
    "unknown": "实习类型待核",
    "graduate_only": "仅限应届／校招（排除）",
}

# Explicit exclusivity is the exclusion criterion; preference for graduates
# or "2027届及以后" is NOT exclusivity.
GRAD_ONLY = re.compile(
    r"(?:仅|只)(?:限|招|面向|接受|考虑|招聘).{0,16}(?:应届(?:毕业生)?|毕业生|20\d{2}届)"
    r"|(?:20\d{2}届|应届(?:毕业生)?).{0,14}(?:限定|专属|仅招|仅限)"
    r"|(?:校招全职|正式校招|应届生专岗)"
)

def classify(job):
    """daily / general / retention / special / unknown / graduate_only."""
    key = str(job.get("id", ""))
    title = str(job.get("title") or "")
    team = str(job.get("team") or "")
    # Only the job title and substantive eligibility fields may establish
    # graduating-only restrictions. Reviewer notes like "未见仅限应届" must
    # NOT be parsed as positive evidence of a restriction.
    qualifications = []
    for field in ("graduation", "requirements"):
        value = str(job.get(field) or "")
        if re.search(r"未见|未明确|不确定|不限应届|并非仅限|不是仅限|无需应届|尚未核实", value):
            continue
        qualifications.append(value)
    terms = title + " " + team + " " + " ".join(qualifications)
    company = str(job.get("company") or "")
    if key in TENCENT_GRADUATING_COHORT_IDS or "（应届实习）" in title:
        return "graduate_only"
    # Avoid treating a negated phrase or preference as a strict restriction.
    if GRAD_ONLY.search(terms) and not re.search(r"非应届(?:生)?也可|不限应届|应届(?:生)?优先|20\d{2}届及以后", terms):
        return "graduate_only"
    if "校招正式" in title or "全职社招" in title:
        return "graduate_only"
    if job.get("internship_kind") == "daily" and job.get("daily_evidence"):
        return "daily"
    if "日常实习" in title or "日常实习项目" in team:
        return "daily"
    if company == "百度" and key.startswith("baidu-J"):
        return "daily"  # reviewed Baidu INTERN pages
    if company == "美团" and key.startswith("meituan-") and "【2027】" not in title and "专项" not in title:
        return "daily"  # previously checked company internship feed
    if key in DAILY_IQIYI:
        return "daily"
    if "留用实习" in title or "留用实习" in team:
        return "retention"
    if any(k in terms for k in ("专项", "培训生（Ace）", "RPT 产品培训", "暑期实习", "2028届实习生招聘", "【2027】")):
        return "special"
    if "实习" in terms or job.get("source") or job.get("verify"):
        return "general"
    return "unknown"

def is_product_candidate(job):
    """Keep the curated PM list broad, but not standalone technical engineers."""
    title = str(job.get("title") or "")
    if "工程师" in title and not re.search(r"产品经理|产品实习", title):
        return False
    return True

def eligible_jobs(jobs):
    """Published job pool: every candidate except explicitly graduation-only roles."""
    result = []
    for job in jobs:
        tag = classify(job)
        if tag == "graduate_only" or not is_product_candidate(job):
            continue
        row = dict(job)
        row["internship_scope"] = tag
        row["internship_label"] = DAILY_NAMES[tag]
        result.append(row)
    return result

# Old entry point still used by publishing and CSV scripts.
def daily_jobs(jobs):
    return eligible_jobs(jobs)
