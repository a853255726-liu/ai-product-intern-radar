"""Alibaba public campus job-board JSON, with normal anonymous browser session.

Uses only the public recruitment page's first-party SESSION/CSRF metadata;
never uses a login credential or attempts to defeat a challenge.  An
unexpected response or partial page fails closed, preserving prior data.
"""
from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
import re
from candidate_scope import is_product_candidate

SITE = "https://campus-talent.alibaba.com"
BATCH_ID = 100000760001  # Current official campus page as observed 2026-10-14.
LIST_PAGE = SITE + "/campus/position?batchId=" + str(BATCH_ID)
API = SITE + "/position/search"
PAGE_SIZE = 100
MAX_PAGES = 25

TOKEN_RE = re.compile(r'__token__\s*:\s*["\x27]([^"\x27]+)["\x27]')


def query_for_page(page):
    if page < 1:
        raise ValueError("Alibaba job page starts at one")
    return {
        "batchId": BATCH_ID,
        "pageIndex": page,
        "pageSize": PAGE_SIZE,
        "channel": "new_campus_group_official_site",
        "language": "zh",
    }


def parse_page(data):
    if not isinstance(data, dict):
        raise ValueError("Alibaba API response is not an object")
    payload = data.get("content")
    if not isinstance(payload, dict):
        raise ValueError("Alibaba API missing public content payload")
    total, jobs = payload.get("totalCount"), payload.get("datas")
    if not isinstance(total, int) or total < 1 or not isinstance(jobs, list):
        raise ValueError("Alibaba API count or public listing missing")
    if any(not isinstance(job, dict) or not str(job.get("id", "")).isdigit()
           or int(str(job["id"])) <= 0 for job in jobs):
        raise ValueError("Alibaba API result missing positive job ID")
    return total, jobs


def collect_alibaba(session):
    # The first-party campus web page issues an anonymous session and
    # standard CSRF token. Do not accept cookie-less/challenged responses.
    first = session.get(
        LIST_PAGE, headers={"Accept-Language": "zh-CN,zh;q=0.9",
                            "User-Agent": "Mozilla/5.0"},
        timeout=28,
    )
    first.raise_for_status()
    match = TOKEN_RE.search(first.text)
    if not match:
        raise ValueError("Alibaba public session token unavailable; not attempting API")
    token = match.group(1)
    headers = {"Content-Type": "application/json", "Origin": SITE,
               "Referer": LIST_PAGE, "Accept-Language": "zh-CN,zh;q=0.9",
               "User-Agent": "Mozilla/5.0"}
    records, expected, sizes = [], None, []
    for page in range(1, MAX_PAGES + 1):
        response = session.post(API, params={"_csrf": token},
                                headers=headers, json=query_for_page(page), timeout=28)
        response.raise_for_status()
        count, found = parse_page(response.json())
        if expected is None:
            expected = count
        elif count != expected:
            raise ValueError("Alibaba total changed between pages")
        records.extend(found)
        sizes.append(len(found))
        if len(records) >= expected:
            break
        if not found:
            raise ValueError("Alibaba returned empty intermediate page")
    ids = [str(v["id"]) for v in records]
    if expected is None or len(ids) != expected or len(set(ids)) != expected:
        raise ValueError(
            f"Alibaba incomplete pages: reported={expected} "
            f"fetched={len(ids)} unique={len(set(ids))}"
        )
    return records, {
        "screening_diagnostics": diagnose_alibaba(records),
        "reported": expected, "raw_records": len(records),
        "unique_ids": len(set(ids)), "pages": len(sizes),
        "page_sizes": sizes, "failed_pages": 0,
        "status": "公开会话职位接口完整性校验通过",
        "scope": ("阿里巴巴 campus-talent 官网 batchId=" + str(BATCH_ID)
                  + " 的当前混合校园招聘目录，不能等同全部业务或日常实习岗位"),
        "capture": "阿里巴巴官方匿名网页会话与职位列表 JSON",
    }


def _flat(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " / ".join(str(value[k]) for k in ("name", "cnName", "cityName", "label")
                          if value.get(k))
    if isinstance(value, list):
        return " / ".join(_flat(v) for v in value)
    return ""


def _posted(row):
    for key in ("updateTime", "publishTime", "createTime"):
        value = row.get(key)
        if isinstance(value, str) and re.match(r"\d{4}-\d{2}-\d{2}", value):
            return value[:10]
        if isinstance(value, (int, float)) and value > 0:
            secs = value / 1000 if value > 1e11 else value
            return datetime.fromtimestamp(secs, ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
    return ""


def _has_internship_evidence(row):
    # Mixed campus results can include graduating full-time jobs. Demand an
    # explicit internship term in the job title or hiring programme fields.
    title = str(row.get("name") or "")
    terms = " ".join(_flat(row.get(k)) for k in (
        "batchName", "projectName", "projectType", "recruitmentType",
        "recruitType", "positionNature", "positionType", "jobType",
        "recruitmentCategory", "tags", "tagNames",
    ))
    if re.search(r"全职|正式校招|社招", terms) and not re.search(r"实习", terms + title):
        return False
    return bool(re.search(r"实习|intern", title + " " + terms, re.I))


def diagnose_alibaba(records):
    """Small audit-only data footprint to diagnose underselection by schema."""
    source_keys = set()
    counts = {"with_beijing": 0, "explicit_internship": 0,
              "beijing_internship": 0, "beijing_internship_pm": 0,
              "pm_titles": 0}
    interesting = []
    for row in records:
        source_keys.update(row.keys())
        title = str(row.get("name") or "")
        loc = _flat(row.get("workLocations"))
        is_intern = _has_internship_evidence(row)
        is_beijing = "北京" in loc
        pm = is_product_candidate(title, str(row.get("description") or ""))
        if is_beijing:
            counts["with_beijing"] += 1
        if is_intern:
            counts["explicit_internship"] += 1
        if is_beijing and is_intern:
            counts["beijing_internship"] += 1
        if pm:
            counts["pm_titles"] += 1
        if is_beijing and is_intern and pm:
            counts["beijing_internship_pm"] += 1
        if len(interesting) < 5 and ("产品" in title or "评测" in title):
            interesting.append({
                "id": str(row.get("id") or ""),
                "title": title[:90],
                "location_value": str(row.get("workLocations"))[:220],
                "type_value": str({k: row.get(k) for k in (
                    "batchName", "projectName", "projectType",
                    "recruitmentType", "recruitType", "positionNature",
                    "positionType", "jobType", "tags",
                ) if k in row})[:280],
                "description_start": str(row.get("description") or "")[:130],
            })
    batch_names = {}
    for row in records:
        name = str(row.get("batchName") or "未标注")
        batch_names[name] = batch_names.get(name, 0) + 1
    return {"source_keys": sorted(source_keys)[:80],
            "counts": counts, "batch_names": batch_names,
            "recruitment_scope": ("仅已识别应届校招批次，未覆盖日常实习"
                if batch_names and all("应届" in name for name in batch_names)
                else "混合批次，逐条检查实习证据"),
            "sample": interesting}


def normalize_alibaba(records, today):
    found = []
    for row in records:
        title = str(row.get("name") or "").strip()
        duty = str(row.get("description") or "")
        requirements = str(row.get("requirement") or "")
        cities = _flat(row.get("workLocations"))
        if not (_has_internship_evidence(row) and "北京" in cities):
            continue
        if not is_product_candidate(title, duty):
            continue
        if not re.search(r"\bAI\b|AIGC|Agent|LLM|MCP|RAG|大模型|"
                         r"人工智能|智能体|千问|通义|生成式|模型评测",
                         title + " " + duty, re.I):
            continue
        jid = str(row["id"])
        post_date = _posted(row)
        found.append({
            "id": "alibaba-public-" + jid, "company": "阿里巴巴",
            "title": title,
            "link": SITE + "/campus/position/" + jid,
            "posted": post_date, "date_type": "更新时间" if post_date else "未提供",
            "group": "大厂", "track": "AI 产品/策略", "fit": "优先关注",
            "days": "未注明", "duration": "未注明",
            "verify": "官网API（含JD，详情待复核）",
            "status": "当前校招批次官网有职位记录，实时名额未确认",
            "team": _flat(row.get("circleNames")) or "业务集团待核实",
            "summary": duty[:2100],
            "requirements": requirements[:1500] or "请查看官方岗位详情",
            "source": "阿里巴巴校园招聘公开职位列表",
            "graduation": "未核实", "checked": today(),
            "source_post_id": jid,
            "note": ("来自当前校招混合目录，筛选要求职位标题或招聘项目"
                     "明确为实习；具体投递资格需按官方详情核验。"),
        })
    return found
