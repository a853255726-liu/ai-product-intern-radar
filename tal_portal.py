"""TAL's NEW public campus portal, introduced after the Moka redirect.

Strictly audits the public '日常实习' project. Reads all displayed cards,
opens their own official UUID pages, validates job nature twice, and rejects
partial pagination. Never uses internal API signatures or candidate accounts.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

LIST_URL = "https://job.tal.com/campus/positions"
JOB_COUNT = re.compile(r"共\s*(\d+)\s*个职位")
UUID_ROUTE = re.compile(
    r"^/campus/positions/([0-9a-fA-F]{8}-[0-9a-fA-F-]{27,36})/?$")
MAX_DAILY_JOBS = 20  # No multi-page daily list verified yet; fail closed above it.


def parse_card(text):
    lines = [x.strip() for x in str(text).splitlines() if x.strip()]
    if len(lines) < 4:
        raise ValueError("TAL new portal card missing title, nature or location")
    title = lines[0]
    nature_and_category = next(
        (line for line in lines
         if re.match(r"^(?:实习|全职|兼职|其他)(?:\s|$)", line)),
        None,
    )
    date_match = re.search(r"发布于\s*(\d{4}-\d{2}-\d{2})", text)
    cities = re.findall(r"(?m)^([^\n]*?(?:市|自治区|特别行政区))$", text)
    if not nature_and_category or not date_match:
        raise ValueError("TAL new portal card lacks verified job nature or date")
    label, _, category = nature_and_category.partition(" ")
    city = next((x for x in cities if x.endswith("市")), "")
    if not city:
        raise ValueError("TAL new portal card missing city, cannot assert Beijing")
    return {
        "title": title, "nature": label,
        "category": category.strip(), "city": city,
        "date": date_match.group(1),
    }


def parse_detail(url, body, expected):
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "job.tal.com":
        raise ValueError("TAL new portal left the official recruiting host")
    match = UUID_ROUTE.fullmatch(parts.path)
    if not match:
        raise ValueError("TAL job detail has no verified employer UUID")
    if expected["title"] not in body or "职位描述" not in body:
        raise ValueError("TAL new portal detail did not load job description")
    prefix = body.split("职位描述", 1)[0]
    natures = re.findall(r"(?m)^\s*(实习|全职|兼职)\s*$", prefix)
    if not natures or natures[0] != expected["nature"]:
        raise ValueError("TAL detail job nature contradicts the public listing")
    return {
        "id": match.group(1).lower(),
        "url": "https://job.tal.com" + parts.path,
        "title": expected["title"],
        "tags": [expected["nature"], expected["category"], expected["city"]],
        "date": expected["date"],
        "description": body,
        "subtitle": expected["nature"] + " / " + expected["city"],
    }


def open_daily_directory(page):
    from playwright.sync_api import TimeoutError as BrowserTimeout
    page.goto(LIST_URL, wait_until="domcontentloaded", timeout=30000)
    try:
        # Establish the unfiltered catalog baseline before selecting a
        # project. Otherwise the SPA can still display all 132 vacancies
        # after the checkbox click, with a temporarily misleading count.
        page.locator(".job-card").first.wait_for(timeout=16000)
        initial_body = page.locator("body").inner_text()
        original = re.search(r"全部在招职位[（(]\\s*(\\d+)\\s*[）)]", initial_body)
        if not original:
            raise ValueError("TAL all-jobs baseline missing, cannot prove filter scope")
        unfiltered_count = int(original.group(1))
        page.get_by_text("日常实习", exact=True).first.click(timeout=14000)
        # The filter must ACTUALLY change the employer's visible source scope,
        # not merely show a clickable label while all-job cards remain.
        page.wait_for_function("""baseline => {
            const t = document.body?.innerText || "";
            const result = t.match(/共\\s*(\\d+)\\s*个职位/);
            return Boolean(result && Number(result[1]) > 0
                && Number(result[1]) < baseline
                && document.querySelectorAll(".job-card").length === Number(result[1]));
        }""", arg=unfiltered_count, timeout=18000)
    except BrowserTimeout as exc:
        raise ValueError("TAL daily filter did not finish updating the public cards") from exc
    body = page.locator("body").inner_text()
    m = JOB_COUNT.search(body)
    if not m:
        raise ValueError("TAL official daily-project count missing")
    count = int(m.group(1))
    cards = page.locator(".job-card")
    if count <= 0 or count > MAX_DAILY_JOBS or cards.count() != count:
        raise ValueError(
            f"TAL daily project list incomplete: reported={count}, "
            f"visible={cards.count()}, max={MAX_DAILY_JOBS}"
        )
    return count, [parse_card(x) for x in cards.all_inner_texts()]


def collect_tal(session=None):
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    records = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1400, "height": 950})
            count, expected_cards = open_daily_directory(page)
            for i, expected in enumerate(expected_cards):
                # Repeat only the employer's ordinary public navigation.
                # Rechecking list stability avoids silently pairing details
                # with a different card after a recruiter changes the list.
                if i:
                    current_count, current_cards = open_daily_directory(page)
                    if current_count != count or current_cards != expected_cards:
                        raise ValueError("TAL daily listing changed between detail visits")
                page.locator(".job-card").nth(i).click(timeout=12000)
                try:
                    page.wait_for_url(re.compile(
                        r"^https://job\.tal\.com/campus/positions/[0-9a-fA-F-]{36}/?$"),
                        timeout=14000)
                    page.get_by_text("职位描述", exact=True).first.wait_for(timeout=12000)
                except BrowserTimeout as exc:
                    raise ValueError(
                        "TAL official job UUID detail did not render: "
                        + expected["title"]
                    ) from exc
                records.append(parse_detail(
                    page.url, page.locator("body").inner_text(), expected
                ))
        finally:
            browser.close()
    ids = [x["id"] for x in records]
    if not ids or len(ids) != count or len(set(ids)) != count:
        raise ValueError(
            f"TAL new daily project incomplete: reported={count}, "
            f"retrieved={len(ids)}, unique={len(set(ids))}"
        )
    return records, {
        "reported": count, "raw_records": count,
        "unique_ids": count, "pages": 1, "page_sizes": [count],
        "failed_pages": 0,
        "status": "好未来新版官网日常实习项目全量卡片及专属UUID详情已对账",
        "scope": "仅job.tal.com公开日常实习项目，岗位性质须为实习，北京AI产品另筛",
        "capture": "好未来新版招聘官网公开项目筛选及职位详情（无登录）",
        "caveat": "全职性质的实习转正或产品岗位不可当作普通实习；官网有职位不保证HC",
    }
