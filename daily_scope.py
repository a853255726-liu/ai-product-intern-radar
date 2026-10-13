"""Daily internship eligibility gate for published Beijing AI product vacancies.

Conservative by design: internship != verified day-to-day / rolling internship.
Only a company-defined daily stream, an official labeled daily posting, or a
specifically reviewed company daily-intern job can pass.
Keep excluded/unknown rows in the master database for audit, not on the site.
"""

DAILY_IQIYI = {"iqiyi-A01585", "iqiyi-A10460", "iqiyi-A15887"}
NON_DAILY_IDS = {
    "xhs-20413",  # Ace/RPT project rather than daily internship
    "tencent-1224696104600437761",
    "tencent-1188988696721092608",
    "tencent--3",
    "tencent-1153452731391100929",
    "tencent-1177660287764272128",
    "tencent-1212816229455368192",
    "tencent-1224696067023896576",
    "tencent-1226957086077102081",
    "kuaishou-30248",  # 可灵专项, project kind not daily
}
NON_DAILY_MARKERS = ("留用实习", "应届实习", "暑期实习", "转正专项", "实习专项", "2028届实习生招聘", "2027届实习项目")


def classify(job):
    """Return daily, non_daily, or unverified. Never extrapolate from graduation year alone."""
    key = str(job.get("id", ""))
    title = str(job.get("title", ""))
    team = str(job.get("team", ""))
    company = str(job.get("company", ""))
    if key in NON_DAILY_IDS or any(p in title for p in NON_DAILY_MARKERS):
        return "non_daily"
    if "培训生（Ace）" in title or "产品培训生（Ace）" in title:
        return "non_daily"
    if job.get("internship_kind") == "daily" and job.get("daily_evidence"):
        return "daily"
    if "日常实习" in title or "日常实习项目" in team:
        return "daily"
    if company == "腾讯":
        # Tencent's "应届实习" and "日常实习" are different official projects.
        return "unverified"
    if company == "百度" and key.startswith("baidu-J"):
        # These hand-inspected Baidu INTERN details identify 日常实习项目.
        return "daily"
    if company == "美团" and key.startswith("meituan-"):
        # Meituan official campus internship list classifies these as 日常实习.
        if "【2027】" in title or "专项" in title:
            return "unverified"
        return "daily"
    if key in DAILY_IQIYI:
        # Verified on official iQIYI "日常实习生招聘" /intern list or detail.
        return "daily"
    # "实习" alone or third-party unlabeled posting is not enough evidence.
    return "unverified"


def daily_jobs(jobs):
    return [j for j in jobs if classify(j) == "daily"]
