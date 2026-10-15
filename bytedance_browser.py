"""Strict, visitor-facing ByteDance campus browser fallback.

Only observes API responses produced by the employer's standard public page.
Never forges a signed request, bypasses challenges, or treats partial pages as complete.
"""
from __future__ import annotations

from urllib.parse import urlencode, urlparse

CAMPUS = "https://jobs.bytedance.com/campus/position"
API_PATH = "/api/v1/search/job/posts"
DAILY_ID = "7194661644654577981"
CATEGORY_IDS = [
    "6704215864629004552",  # product
    "6704216057269192973",  # product operations
    "6709824272996501772",  # user research
    "6704216232129726734",  # strategy
]
BEIJING = "CT_11"
PAGE_SIZE = 10
MAX_PAGES = 100


def public_page_url(page):
    if not 1 <= page <= MAX_PAGES:
        raise ValueError("Page out of range")
    params = {
        "keywords": "",
        "category": ",".join(CATEGORY_IDS),
        "location": BEIJING,
        "project": DAILY_ID,
        "type": "3",
        "current": str(page),
        "limit": str(PAGE_SIZE),
    }
    return CAMPUS + "?" + urlencode(params)


def validate_request_scope(body, page):
    """Prevent accidental publication of unrelated campus/new-grad roles.

    The public website must actually apply the requested filters. Merely seeing
    some API data in the browser, or an apparent UI filter, is insufficient.
    """
    if not isinstance(body, dict):
        raise ValueError("ByteDance browser request had no readable JSON filters")
    required = {
        "recruitment_id_list": {"202"},
        "subject_id_list": {DAILY_ID},
        "location_code_list": {BEIJING},
        "job_category_id_list": set(CATEGORY_IDS),
    }
    for field, expected in required.items():
        actual = body.get(field)
        if not isinstance(actual, list) or set(map(str, actual)) != expected:
            raise ValueError("ByteDance browser did not apply expected filter: " + field)
    try:
        limit = int(body.get("limit"))
        offset = int(body.get("offset"))
    except (TypeError, ValueError) as exc:
        raise ValueError("ByteDance browser request missing pagination") from exc
    if limit != PAGE_SIZE or offset != (page - 1) * PAGE_SIZE:
        raise ValueError("ByteDance browser ignored requested page/limit")


def _job_api_response(response):
    parsed = urlparse(response.url)
    return (
        parsed.hostname == "jobs.bytedance.com"
        and parsed.path == API_PATH
        and response.request.method == "POST"
    )


def collect_bytedance_browser():
    """Use the real publicly accessible campus UI; fail closed on blocks."""
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout

    all_rows, total, sizes = [], None, []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1280, "height": 900})
            page.set_default_timeout(25000)
            for page_num in range(1, MAX_PAGES + 1):
                try:
                    with page.expect_response(_job_api_response, timeout=30000) as observed:
                        page.goto(public_page_url(page_num),
                                  wait_until="domcontentloaded", timeout=30000)
                    response = observed.value
                except BrowserTimeout as exc:
                    raise ValueError("Public ByteDance browser did not load its job API") from exc
                if response.status != 200:
                    raise ValueError("Public ByteDance browser API HTTP " + str(response.status))
                validate_request_scope(response.request.post_data_json, page_num)
                payload = response.json()
                data = payload.get("data") or {}
                count, rows = data.get("count"), data.get("job_post_list")
                if payload.get("code") != 0 or not isinstance(count, int) or not isinstance(rows, list):
                    raise ValueError("Invalid ByteDance browser API status/count/records")
                if count <= 0:
                    raise ValueError("Empty browser results cannot prove complete source coverage")
                if total is None:
                    total = count
                elif count != total:
                    raise ValueError("ByteDance browser total changed during pagination")
                if not rows or len(rows) > PAGE_SIZE:
                    raise ValueError("ByteDance browser returned bad page size")
                if any(not isinstance(item, dict) or not str(item.get("id") or "").isdigit()
                       or int(str(item["id"])) <= 0 for item in rows):
                    raise ValueError("ByteDance browser returned invalid job IDs")
                all_rows.extend(rows)
                sizes.append(len(rows))
                if len(all_rows) >= total:
                    break
        finally:
            browser.close()
    ids = [str(row["id"]) for row in all_rows]
    if total is None or len(ids) != total or len(set(ids)) != total:
        raise ValueError(
            f"ByteDance browser incomplete: total={total}, "
            f"rows={len(ids)}, unique={len(set(ids))}"
        )
    return all_rows, {
        "reported": total, "raw_records": len(ids), "unique_ids": len(ids),
        "pages": len(sizes), "page_sizes": sizes, "failed_pages": 0,
        "status": "官网普通浏览器公开职位接口分页及唯一ID对账通过",
        "capture": "字节跳动官网普通访客页面网络响应（无登录）",
        "scope": "招聘202实习、日常项目、北京、产品/运营/研究/策略四类的有限范围",
        "caveat": "仅网页实际应用过滤条件后方可入库；不代表全公司岗位或HR确认在招",
    }
