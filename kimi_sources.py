"""Moonshot AI / Kimi official MokaHR campus jobs.

Read the employer's public browser UI rather than unofficial API signatures.
A count mismatch, missing page, duplicate ID, or inaccessible details fails
closed: the caller retains its last complete successful snapshot.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from candidate_scope import is_product_candidate

BASE = "https://app.mokahr.com/campus-recruitment/moonshot/148507"
JOB_RE = re.compile(r"^/job/([0-9a-f-]{36})$")
RESULT_RE = re.compile(r"已选\s*\d+\s*条件\s*[|｜]\s*(\d+)\s*结果")
MAX_PAGES = 20


def list_url(index):
    return f"{BASE}#/jobs/?page={index}"


def parse_list_html(html):
    soup = BeautifulSoup(html, "html.parser")
    full_text = soup.get_text(" ", strip=True)
    m = RESULT_RE.search(full_text)
    if not m or int(m.group(1)) == 0:
        raise ValueError("Moka results count missing/zero; page may not have rendered")
    total = int(m.group(1))
    rows = []
    # Scope to actual search results. Related/recommended jobs outside these
    # cards must not be mistaken for results, or the total would be wrong.
    cards = soup.select(
        'div[class*="results-"] > div[class*="jobs-"] > div[class*="container-"]'
    )
    for card in cards:
        anchor = card.select_one('a[href*="#/job/"]')
        title_el = card.select_one('span[class*="target-color-container"]')
        if not anchor or not title_el:
            raise ValueError("Moka result card has no official link or title")
        url = anchor.get("href", "").strip()
        parsed = urlparse(url)
        match = JOB_RE.fullmatch(parsed.fragment)
        if not (parsed.scheme == "https" and parsed.netloc == "app.mokahr.com"
                and parsed.path == "/campus-recruitment/moonshot/148507" and match):
            raise ValueError("Moka unexpected job detail route: " + url)
        details = [el.get_text(" ", strip=True) for el in
                   card.select('div[class*="sd-Ellipsis-hiddenContent-"]')]
        # Duplicates hidden in responsive tooltips shouldn't be used as tags.
        posted = card.select_one('span[class*="published-at-"]')
        body = card.select_one('div[class*="job-description-"]')
        rows.append({
            "id": match.group(1),
            "url": url,
            "title": title_el.get_text(" ", strip=True),
            "tags": details[:3],
            "date": (posted.get_text(" ", strip=True) if posted else ""),
            "description": body.get_text("\n", strip=True) if body else "",
        })
    if not rows:
        raise ValueError("Moka shows a count but result cards are absent")
    return total, rows


def parse_detail_html(html):
    soup = BeautifulSoup(html, "html.parser")
    description = soup.select_one('div[class*="job-description-"]')
    if not description:
        raise ValueError("Moka detail page did not render a job description")
    detail = description.get_text("\n", strip=True)
    if len(detail) < 35:
        raise ValueError("Moka detail description implausibly short")
    return detail


def _worth_detail(row):
    title = row["title"]
    tag = " ".join(row["tags"])
    return ("实习" in tag
            and is_product_candidate(title, row["description"], tag))


def collect_kimi(session=None, max_pages=MAX_PAGES):
    """Full public list plus enriched JDs for potential product interns."""
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout

    rows, expected, page_sizes = [], None, []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1390, "height": 900})
            page.set_default_timeout(20000)
            for index in range(1, max_pages + 1):
                page.goto(list_url(index), wait_until="domcontentloaded", timeout=30000)
                try:
                    page.locator(
                        'div[class*="results-"] > div[class*="jobs-"] a[href*="#/job/"]'
                    ).first.wait_for(timeout=20000)
                except BrowserTimeout as exc:
                    raise ValueError("Moka job list did not render") from exc
                total, found = parse_list_html(page.content())
                if expected is None:
                    expected = total
                elif expected != total:
                    raise ValueError("Moka listing count changed during pagination")
                rows.extend(found)
                page_sizes.append(len(found))
                if len(rows) >= total:
                    break

            ids = [row["id"] for row in rows]
            if expected is None or len(ids) != expected or len(set(ids)) != expected:
                raise ValueError(
                    f"Moka incomplete listing reported={expected}, "
                    f"retrieved={len(ids)}, unique={len(set(ids))}"
                )
            # Fetch full job descriptions to confirm Beijing when the job
            # listing omits city but the actual JD explicitly says 'Base 北京'.
            for row in rows:
                if not _worth_detail(row):
                    continue
                page.goto(row["url"], wait_until="domcontentloaded", timeout=30000)
                try:
                    page.locator('div[class*="job-description-"]').first.wait_for(
                        timeout=20000
                    )
                except BrowserTimeout as exc:
                    raise ValueError("Moka job detail did not render: " + row["id"]) from exc
                row["description"] = parse_detail_html(page.content())
        finally:
            browser.close()
    return rows, {
        "reported": expected, "raw_records": len(rows), "unique_ids": len(set(ids)),
        "pages": len(page_sizes), "page_sizes": page_sizes, "failed_pages": 0,
        "status": "公开浏览器页面完整性校验通过",
        "scope": "月之暗面 Moka 官方校园招聘全部职位；先筛实习再筛北京 AI 产品",
        "capture": "官网 Moka 招聘公开浏览器渲染（无登录）",
    }


def normalize_kimi(rows, today):
    output = []
    for row in rows:
        title = row["title"]
        tags = row["tags"]
        duty = row["description"]
        if "实习" not in " ".join(tags):
            continue
        if not is_product_candidate(title, duty, " ".join(tags)):
            continue
        # Missing city in the card is common. Require either a literal
        # Beijing in the official listing OR 'Base 北京' in the official JD.
        if not ("北京" in " ".join(tags)
                or re.search(r"(?:Base|工作地(?:点)?|办公地(?:点)?|坐标)\s*[：:\s]*北京", duty, re.I)):
            continue
        # Reject explicit non-Beijing exclusivity if present.
        if re.search(r"(?:Base|工作地(?:点)?)\s*[：:\s]*(?:上海|深圳|杭州|广州)", duty, re.I):
            continue
        strong = bool(re.search(
            r"\bAI\b|Agent|Harness|大模型|智能体|Kimi|Coding|评测|LLM|模型",
            title + " " + duty, re.I,
        ))
        if not strong:
            continue
        release = re.search(r"(\d{4}-\d{2}-\d{2})", row.get("date", ""))
        posted = release.group(1) if release else ""
        days = ("≥5天" if re.search(r"每周.{0,12}(?:至少|需|保证)?\s*5\s*天", duty)
                else "≥4天" if re.search(r"每周.{0,12}(?:至少|需|保证)?\s*4\s*天", duty)
                else "未注明")
        duration = ("≥6个月" if re.search(r"(?:至少|持续|不少于)\s*6\s*个?月", duty)
                    else "≥4个月" if re.search(r"(?:至少|持续|不少于)\s*4\s*个?月", duty)
                    else "未注明")
        track = ("AI Agent" if re.search(r"Agent|Harness|KimiCode|Coding", title + " " + duty, re.I)
                 else "AI数据/评测" if re.search(r"评测|Eval", title + " " + duty, re.I)
                 else "AI应用/体验")
        output.append({
            "id": "kimi-moka-" + row["id"], "company": "月之暗面",
            "title": title, "link": row["url"],
            "posted": posted, "date_type": "发布日期" if posted else "未提供",
            "group": "AI创业公司", "track": track,
            "fit": "优先关注" if "产品" in title else "可以尝试",
            "days": days, "duration": duration,
            "verify": "官网详情",
            "status": "官方校园招聘详情公开展示；剩余名额未确认",
            "team": "Kimi 官方校园招聘 · " + (tags[1] if len(tags) > 1 else "业务团队未披露"),
            "summary": duty[:2500],
            "requirements": "详情原文包含岗位要求，参见职位摘要及官方详情。",
            "note": "官方职位详情显示实习与北京；需自行确认 HC 与资格。",
            "source": "月之暗面官方 Moka 招聘页面",
            "graduation": "未核实",
            "checked": today(),
            "source_post_id": row["id"],
        })
    return output
