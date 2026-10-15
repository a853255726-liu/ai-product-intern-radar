"""Public Xiaomi recruitment website fallback for cloud HTTP 403/405.

Opens the official jobs page in ordinary Chromium and uses only the same
public, same-origin searchJobPage interface exposed by that page. Does not
log in, inject signatures, solve challenges, or bypass access controls.
Always reconcile every page and unique job ID before publication.
"""
from __future__ import annotations

from urllib.parse import urlencode, urlparse

PORTAL = "https://hr.xiaomi.com/website/opportunities.html"
API = "https://hr.xiaomi.com/website/api/agent/searchJobPage"
PAGE_SIZE = 100
MAX_PAGES = 30


def official_page():
    return PORTAL + "?" + urlencode({"project": "实习", "city": "北京"})


def api_page_url(page):
    if not 1 <= page <= MAX_PAGES:
        raise ValueError("Xiaomi page number outside safe bounds")
    return API + "?" + urlencode({
        "keyword": "", "cityZhNames": "北京",
        "pageSize": PAGE_SIZE, "pageNum": page, "type": 3,
    })


def validate_page(reply, expected_total=None):
    if not isinstance(reply, dict) or reply.get("code") != 0:
        raise ValueError("Xiaomi public browser API returned invalid status")
    data = reply.get("data")
    if not isinstance(data, dict):
        raise ValueError("Xiaomi public browser API missing data object")
    rows, total = data.get("list"), data.get("total")
    if not isinstance(total, int) or total <= 0 or not isinstance(rows, list):
        raise ValueError("Xiaomi public browser API missing valid list/count")
    if expected_total is not None and total != expected_total:
        raise ValueError("Xiaomi total changed between browser pages")
    if not rows or len(rows) > PAGE_SIZE:
        raise ValueError("Xiaomi public browser API returned invalid page length")
    if any(not isinstance(item, dict) or not str(item.get("jobPostId") or "").strip()
           for item in rows):
        raise ValueError("Xiaomi public browser API record missing jobPostId")
    return rows, total


def collect_xiaomi_browser():
    """Query the employer's documented visitor-facing endpoint from its page."""
    from playwright.sync_api import sync_playwright

    records, total, sizes = [], None, []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1280, "height": 900})
            response = page.goto(official_page(), wait_until="domcontentloaded", timeout=30000)
            if not response or response.status >= 400:
                raise ValueError("Xiaomi public careers page is not accessible to browser")
            if urlparse(page.url).hostname != "hr.xiaomi.com":
                raise ValueError("Xiaomi careers page redirected outside the official host")
            for num in range(1, MAX_PAGES + 1):
                # Same-origin browser fetch, as provided by Xiaomi's public jobs.js.
                # A 403/verification challenge must fail; no challenge is solved.
                result = page.evaluate("""async url => {
                    const response = await fetch(url, {
                        method: 'GET', credentials: 'same-origin',
                        headers: {Accept: 'application/json'}
                    });
                    return {status: response.status, text: await response.text()};
                }""", api_page_url(num))
                if not isinstance(result, dict) or result.get("status") != 200:
                    raise ValueError(
                        "Xiaomi browser public API HTTP " +
                        str(result.get("status") if isinstance(result, dict) else "unknown")
                    )
                import json
                reply = json.loads(result["text"])
                rows, current_total = validate_page(reply, total)
                if total is None:
                    total = current_total
                records.extend(rows)
                sizes.append(len(rows))
                if len(records) >= total:
                    break
        finally:
            browser.close()
    ids = [str(item["jobPostId"]) for item in records]
    if total is None or len(ids) != total or len(set(ids)) != total:
        raise ValueError(
            f"Xiaomi browser pagination incomplete: total={total}, "
            f"rows={len(ids)}, unique={len(set(ids))}"
        )
    return records, {
        "reported": total, "raw_records": len(ids),
        "unique_ids": len(ids), "pages": len(sizes),
        "page_sizes": sizes, "failed_pages": 0,
        "status": "小米公开官网普通浏览器全分页及唯一职位ID对账成功",
        "capture": "小米招聘官网标准浏览器公开同源搜索接口（无登录）",
        "scope": "type=3实习，北京；不含其他城市或招聘项目",
        "caveat": "官方目录有记录不等于HR确认在招；若网页/API限制访问则保留上次快照",
    }
