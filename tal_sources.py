"""TAL (好未来) public Moka campus recruitment, bounded internship collection.

Uses the employer's ordinary, no-login Moka pages and the already audited
Kimi-style list/detail parser. Never relabels a graduate hire as an internship.
"""
from __future__ import annotations

import re
from candidate_scope import is_product_candidate
from daily_scope import GRAD_ONLY
from kimi_sources import parse_list_html, parse_detail_html

BASE = "https://app.mokahr.com/campus-recruitment/tal/95443"
MAX_PAGES = 40
DETAIL_MARKER = 'div[class*="job-description-"]'
LIST_MARKER = 'div[class*="results-"] > div[class*="jobs-"] a[href*="#/job/"]'

def list_url(index):
    if not 1 <= index <= MAX_PAGES:
        raise ValueError("TAL requested page out of bounds")
    return f"{BASE}#/jobs/?page={index}"

def is_intern(row):
    tags = row.get("tags") or []
    # The first Moka label is the recruitment type. Do not accept a full-time
    # job just because its title or description mentions an intern.
    label = str(tags[0]) if tags else ""
    return "实习" in label and "全职" not in label and "应届" not in label

def is_beijing(row):
    tags = " ".join(row.get("tags") or [])
    duty = row.get("description") or ""
    if re.search(r"(?:Base|工作地(?:点)?|办公地(?:点)?)\s*[：:\s]*(?:上海|深圳|杭州|广州|武汉|南京)", duty, re.I):
        return False
    return ("北京" in tags or bool(re.search(
        r"(?:Base|工作地(?:点)?|办公地(?:点)?|坐标)\s*[：:\s]*北京", duty, re.I)))

def is_ai_product(row):
    title = row.get("title") or ""
    desc = row.get("description") or ""
    if not is_product_candidate(title, desc, " ".join(row.get("tags") or [])):
        return False
    return bool(re.search(
        r"(?<![A-Za-z])AI(?![A-Za-z])|Agent|智能体|大模型|AIGC|生成式|九章|学习智能|学而思智能|"
        r"机器学习|智能教育|自适应学习|LLM|模型评测|教育大模型",
        title + " " + desc, re.I))

def explicit_grad_only(text):
    """Keep exclusion evidence even when a lengthy JD is truncated for UI.

    Mentions of a graduating cohort or non-exclusive preference are not proof
    that other current students are ineligible.
    """
    text = str(text or "")
    for match in GRAD_ONLY.finditer(text):
        # A broad non-exclusive statement elsewhere in a long JD must not
        # silently erase a distinct explicit restriction. Negation applies
        # only when near the particular cohort-only phrase.
        nearby = text[max(0, match.start() - 16): min(len(text), match.end() + 18)]
        if re.search(r"20\d{2}届及以后|非应届(?:生)?也可|不限应届|应届(?:生)?优先", nearby):
            continue
        return match.group(0)
    return ""


def collect_tal(session=None):
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    rows, expected, sizes = [], None, []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1390, "height": 900})
            page.set_default_timeout(20000)
            for index in range(1, MAX_PAGES + 1):
                page.goto(list_url(index), wait_until="domcontentloaded", timeout=30000)
                try:
                    page.locator(LIST_MARKER).first.wait_for(timeout=20000)
                except BrowserTimeout as exc:
                    # Diagnose public client rendering without solving access
                    # challenges, emitting any personal data or accepting a
                    # partial listing.
                    import json
                    evidence = {
                        "page_index": index, "url": page.url,
                        "title": page.title(),
                        "job_anchors": page.locator('a[href*="#/job/"]').count(),
                        "body_preview": page.locator("body").inner_text()[:650],
                    }
                    raise ValueError(
                        "TAL public Moka job list did not render; evidence="
                        + json.dumps(evidence, ensure_ascii=False)
                    ) from exc
                total, found = parse_list_html(page.content(), base=BASE)
                if expected is None:
                    expected = total
                elif total != expected:
                    raise ValueError("TAL count changed between pages")
                rows.extend(found)
                sizes.append(len(found))
                if len(rows) >= total:
                    break
            ids = [r["id"] for r in rows]
            if not expected or len(ids) != expected or len(set(ids)) != expected:
                raise ValueError(
                    f"TAL incomplete list expected={expected}, "
                    f"retrieved={len(ids)}, unique={len(set(ids))}")
            # Listing descriptions can omit city or AI remit. Read the full JD
            # for every clearly labelled product-related internship candidate.
            for row in rows:
                if not is_intern(row) or not is_product_candidate(
                    row["title"], row["description"], " ".join(row["tags"])
                ):
                    continue
                page.goto(row["url"], wait_until="domcontentloaded", timeout=30000)
                try:
                    page.locator(DETAIL_MARKER).first.wait_for(timeout=20000)
                except BrowserTimeout as exc:
                    raise ValueError("TAL candidate official JD did not render: " + row["id"]) from exc
                row["description"] = parse_detail_html(page.content())
        finally:
            browser.close()
    return rows, {
        "reported": expected, "raw_records": len(ids),
        "unique_ids": len(set(ids)), "pages": len(sizes),
        "page_sizes": sizes, "failed_pages": 0,
        "status": "好未来公开Moka页面全分页和职位ID校验通过",
        "capture": "好未来官方Moka校招公开职位及候选JD（普通浏览器）",
        "scope": "仅好未来 tal/95443 校园招聘目录；再独立筛选实习、北京及AI产品",
        "caveat": "官网职位展示不等于仍有HC；届次与日常实习资格以JD为准",
    }

def normalize_tal(rows, today):
    output = []
    for row in rows:
        if not is_intern(row) or not is_beijing(row) or not is_ai_product(row):
            continue
        title = row["title"]
        text = row["description"]
        tags = row.get("tags") or []
        posted = re.search(r"\d{4}-\d{2}-\d{2}", row.get("date", ""))
        days = ("≥5天" if re.search(r"每周.{0,12}(?:至少|需)?\s*5\s*天", text)
                else "≥4天" if re.search(r"每周.{0,12}(?:至少|需)?\s*4\s*天", text)
                else "未注明")
        output.append({
            "id": "tal-moka-" + row["id"], "company": "好未来",
            "title": title, "link": row["url"],
            "posted": posted.group() if posted else "",
            "date_type": "发布日期" if posted else "未提供",
            "group": "中型/行业科技",
            "track": "AI Agent" if re.search(r"Agent|智能体", title + text, re.I)
                     else "AI教育/应用",
            "fit": "优先关注", "days": days, "duration": "未注明",
            "verify": "官网详情（剩余名额待确认）",
            "status": "官网公开实习职位；具体资格/HC待核",
            "team": "好未来官方校园招聘 · " + (tags[1] if len(tags) > 1 else "团队未披露"),
            "summary": text[:2400],
            # Pass actual official eligibility text to daily_scope so
            # explicit graduation-only restrictions are excluded at publish.
            "requirements": text[:2400],
            "note": "仅北京AI产品相关实习；暑期或定向实习的届次限制仍须核查",
            "source": "好未来官网 Moka 校园招聘",
            "graduation_restriction_confirmed": bool(explicit_grad_only(title + " " + text)),
            "graduation": explicit_grad_only(title + " " + text) or
                          ("2027届条件需核实" if "2027届" in title + " " + text else "未核实"),
            "checked": today(),
            "source_post_id": row["id"],
        })
    return output
