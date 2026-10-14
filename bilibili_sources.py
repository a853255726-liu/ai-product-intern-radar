"""Bilibili official *internship* (not graduates) public job feed.

Grounded in the public website's own anonymous XHR:
  GET  /api/auth/v1/csrf/token
  POST /api/campus/position/positionList
with x-appkey=ops.ehr-api.auth, x-channel=campus and x-usertype=2.
This is a public visitor session, not a logged-in account credential.
We never bypass challenges or mark a partial/duplicate result successful.
"""
from __future__ import annotations

import re
import time
from datetime import datetime
from candidate_scope import is_product_candidate

ROOT = "https://jobs.bilibili.com"
CATALOG = ROOT + "/campus/positions?type=0&page=1"
API = ROOT + "/api/campus/position/positionList"
TOKEN = ROOT + "/api/auth/v1/csrf/token"
PAGE_SIZE = 100
MAX_PAGES = 40

def headers(csrf=None):
    h = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "x-appkey": "ops.ehr-api.auth",
        "x-channel": "campus",
        "x-usertype": "2",
        "Origin": ROOT,
        "Referer": CATALOG,
    }
    if csrf:
        h["x-csrf"] = csrf
    return h

def internship_request(page, page_size=PAGE_SIZE):
    if not 1 <= page <= MAX_PAGES:
        raise ValueError("Bilibili page out of range")
    return {
        "pageSize": page_size,
        "pageNum": page,
        "positionName": "",
        "postCode": [],
        "postCodeList": [],
        "workLocationList": [],
        "workTypeList": ["0"],
        "positionTypeList": ["0"],
        "deptCodeList": [],
        "recruitType": None,
        "practiceTypes": [],
        "onlyHotRecruit": 0,
    }

def parse_response(obj):
    if not isinstance(obj, dict) or obj.get("code") != 0:
        raise ValueError("Bilibili public listing API returned unsuccessful response")
    data = obj.get("data")
    if not isinstance(data, dict):
        raise ValueError("Bilibili public API did not return a data object")
    total, records = data.get("total"), data.get("list")
    if not isinstance(total, int) or not total or not isinstance(records, list):
        raise ValueError("Bilibili count/records missing or zero")
    for rec in records:
        if (not isinstance(rec, dict)
                or not str(rec.get("id") or "").isdigit()
                or int(rec["id"]) <= 0
                or not rec.get("positionName")):
            raise ValueError("Bilibili job is missing stable numeric ID or title")
    return total, records

def collect_bilibili(session, page_size=PAGE_SIZE, max_pages=MAX_PAGES):
    """Reconcile all public internship positions and stable IDs before acceptance."""
    # An anonymous CSRF token is provided to every visitor by the employer's
    # site, and the public page uses it in its own HTTP request.
    res = session.get(TOKEN, headers=headers(), timeout=22)
    res.raise_for_status()
    token_response = res.json()
    token = token_response.get("data") if isinstance(token_response, dict) else None
    if (not isinstance(token_response, dict) or token_response.get("code") != 0 or not isinstance(token, str)
            or not re.fullmatch(r"[0-9a-fA-F-]{32,50}", token)):
        raise ValueError("Bilibili public anonymous CSRF unavailable")
    h = headers(token)
    rows, total, sizes = [], None, []
    for n in range(1, max_pages + 1):
        res = session.post(API, json=internship_request(n, page_size),
                           headers=h, timeout=26)
        res.raise_for_status()
        count, batch = parse_response(res.json())
        if total is None:
            total = count
        elif count != total:
            raise ValueError("Bilibili total changed during pagination")
        rows.extend(batch)
        sizes.append(len(batch))
        if len(rows) >= total:
            break
        if not batch:
            raise ValueError("Bilibili empty intermediate page")
        time.sleep(0.3)
    ids = [str(j["id"]) for j in rows]
    if total is None or len(ids) != total or len(set(ids)) != total:
        raise ValueError(
            f"Bilibili incomplete/duplicate: reported={total} "
            f"retrieved={len(ids)} unique={len(set(ids))}"
        )
    if any(str(j.get("positionTypeName") or "") != "实习"
           or j.get("recruitType") not in (None, 0, "0") for j in rows):
        raise ValueError("Bilibili internship feed unexpectedly contains non-internship roles")
    return rows, {
        "reported": total, "raw_records": len(rows), "unique_ids": len(set(ids)),
        "pages": len(sizes), "page_sizes": sizes, "failed_pages": 0,
        "status": "官网公开实习项目完整职位ID核验通过",
        "scope": "仅哔哩哔哩官网 type=0 实习生招聘（并非应届生 type=3）；全国全类别，另筛北京 AI 产品",
        "capture": "B站校园招聘官网匿名会话公开 JSON API",
        "page_size": page_size,
    }

def normalize_bilibili(records, today):
    out = []
    for r in records:
        name = str(r.get("positionName") or "")
        city = str(r.get("workLocation") or r.get("workCity") or "")
        duty = str(r.get("positionDescription") or "")
        category = str(r.get("postCodeName") or "")
        if r.get("positionTypeName") != "实习" or "北京" not in city:
            continue
        if not is_product_candidate(name, duty, category):
            continue
        # Mentioning AI tools incidentally is not an AI product business.
        if not re.search(
            r"\bAI\b|AIGC|Agent|大模型|智能体|模型评测|LLM|多模态|生成式|机器学习",
            name + " " + duty, re.I,
        ):
            continue
        jid = str(r["id"])
        posted = str(r.get("pushTime") or r.get("ctime") or "")[:10]
        posted = posted if re.fullmatch(r"\d{4}-\d{2}-\d{2}", posted) else ""
        days_match = re.search(r"每周.{0,18}([345])\s*天", duty)
        duration_match = re.search(r"(?:实习|持续).{0,18}([3-9])\s*个?月", duty)
        days = ("≥" + days_match.group(1) + "天") if days_match else "未注明"
        duration = ("≥" + duration_match.group(1) + "个月") if duration_match else "未注明"
        out.append({
            "id": "bilibili-" + jid, "company": "B站",
            "title": name,
            "link": ROOT + "/campus/positions/" + jid + "?type=0",
            "posted": posted, "date_type": "发布日期" if posted else "未提供",
            "group": "中厂", "track": "AI产品/策略",
            "fit": "优先关注" if re.search(r"产品经理|产品实习生", name) else "可以尝试",
            "days": days, "duration": duration,
            "verify": "官网API（公开职位详情路由）",
            "status": "官网实习项目有记录，仍需确认实时HC与投递资格",
            "team": "哔哩哔哩实习生招聘 · " + category,
            "summary": duty[:2100],
            "requirements": duty[:2200],
            "note": "仅官网实习项目；北京与AI产品职责均需明确，不推断应届校招资格",
            "source": "哔哩哔哩官方实习招聘公开API",
            "internship_kind": "general",
            "graduation": "未核实",
            "checked": today(),
            "source_post_id": jid,
        })
    return out
