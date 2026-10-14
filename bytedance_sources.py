"""Public ByteDance campus recruitment API: Beijing daily internships.

The selected four categories are a deliberately bounded query, NOT a
claim of complete coverage across all ByteDance teams and hiring channels.
Only standard publicly accessible endpoints are used, without auth/bypass.
"""
from __future__ import annotations
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from candidate_scope import is_product_candidate

API = "https://jobs.bytedance.com/api/v1/search/job/posts"
CAMPUS = "https://jobs.bytedance.com/campus/position"
DAILY_ID = "7194661644654577981"
CATEGORY_IDS = [
    "6704215864629004552",  # product parent
    "6704216057269192973",  # product operations
    "6709824272996501772",  # user research
    "6704216232129726734",  # strategy
]
PAGE_SIZE = 100
MAX_PAGES = 100


def payload_for_page(page):
    if page < 1:
        raise ValueError("page starts at one")
    return {
        "keyword": "", "limit": PAGE_SIZE, "offset": (page - 1) * PAGE_SIZE,
        "portal_type": 3, "portal_entrance": 1, "language": "zh",
        "recruitment_id_list": ["202"],
        "subject_id_list": [DAILY_ID],
        "location_code_list": ["CT_11"],
        "job_category_id_list": CATEGORY_IDS,
    }


def bytedance(session):
    """Check API count, all pages and unique IDs before accepting any update."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; InternshipRadar/1.0)",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "portal-channel": "campus",
        "portal-platform": "pc",
        "website-path": "campus",
        "Origin": "https://jobs.bytedance.com",
        "Referer": CAMPUS,
    }
    output, total, sizes = [], None, []
    for page in range(1, MAX_PAGES + 1):
        response = session.post(API, json=payload_for_page(page), headers=headers,
                                timeout=28)
        response.raise_for_status()
        obj = response.json()
        body = obj.get("data") or {}
        rows = body.get("job_post_list")
        current = body.get("count")
        if obj.get("code") != 0 or not isinstance(rows, list) or not isinstance(current, int):
            raise ValueError("ByteDance API returned invalid status/records/count")
        if total is None:
            total = current
            if total <= 0:
                # A 0 response can mean invalid filters or an upstream change.
                # Never silently label the company as having no positions.
                raise ValueError("ByteDance bounded query returned zero; filters need checking")
        elif current != total:
            raise ValueError("ByteDance total changed within pagination")
        if any(not isinstance(x, dict) or not str(x.get("id") or "").isdigit()
               or int(str(x["id"])) <= 0 for x in rows):
            raise ValueError("ByteDance returned missing/bad job ID")
        output.extend(rows)
        sizes.append(len(rows))
        if len(output) >= total:
            break
        if not rows:
            raise ValueError("ByteDance returned empty intermediate page")
    ids = [str(x["id"]) for x in output]
    if total is None or len(ids) != total or len(set(ids)) != total:
        raise ValueError(
            f"ByteDance incomplete results reported={total} "
            f"retrieved={len(ids)} unique={len(set(ids))}"
        )
    return output, {
        "reported": total, "raw_records": len(ids),
        "unique_ids": len(set(ids)), "pages": len(sizes),
        "page_sizes": sizes, "failed_pages": 0,
        "status": "公开接口分页数量一致",
        "scope": ("仅实习 recruitment=202；日常实习 subject=" + DAILY_ID
                  + "；北京 CT_11；产品、产品运营、用户研究、策略四类"),
        "capture": "字节跳动官方校园招聘公开职位 API",
    }


def _city_text(row):
    cities = row.get("city_list") or []
    if not cities and isinstance(row.get("city_info"), dict):
        cities = [row["city_info"]]
    return "/".join(x.get("name") or "" for x in cities if isinstance(x, dict))


def _posted(value):
    if isinstance(value, (int, float)) and value > 0:
        ts = value / 1000 if value > 1e11 else value
        return datetime.fromtimestamp(ts, ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
    if isinstance(value, str):
        return value[:10] if re.match(r"\d{4}-\d{2}-\d{2}", value) else ""
    return ""


def normalize_bytedance(rows, today):
    output = []
    for row in rows:
        title = str(row.get("title") or "").strip()
        duty = str(row.get("description") or "")
        requirements = str(row.get("requirement") or "")
        city = _city_text(row)
        if "北京" not in city or not is_product_candidate(title, duty):
            continue
        if not re.search(
            r"\bAI\b|AIGC|Agent|LLM|RAG|MCP|大模型|智能体|人工智能|豆包|"
            r"火山引擎|机器学习|多模态|模型评测|AI Native|生成式",
            title + " " + duty, re.I,
        ):
            continue
        jid = str(row["id"])
        job = row.get("job_category") or {}
        category = str(job.get("name") or "")
        posted = _posted(row.get("publish_time"))
        days = "≥4天" if re.search(r"每周.{0,12}(?:至少|需|可到岗)?\s*4\s*天", requirements) else "未注明"
        output.append({
            "id": "bytedance-api-" + jid,
            "company": "字节跳动",
            "title": title, "link": CAMPUS + "/" + jid + "/detail",
            "posted": posted, "date_type": "发布日期" if posted else "未提供",
            "group": "大厂", "track": ("AI Agent" if re.search(
                r"Agent|智能体", title + duty, re.I) else "AI 产品/策略"),
            "fit": "优先关注",
            "days": days, "duration": "未注明",
            "verify": "官网API（含JD，详情待复核）",
            "status": "官网当前接口有记录，名额及资格未获HR确认",
            "team": "日常实习 · " + category,
            "summary": duty[:1900] or "官网列表有职位，详细职责请查看官网",
            "requirements": requirements[:1700] or "官网职位资格待核",
            "note": "仅指定四类北京日常实习，不代表字节其他招聘项目完整覆盖",
            "source": "字节跳动官方校园招聘 API",
            "graduation": "未核实",
            "checked": today(), "source_post_id": jid,
        })
    return output
