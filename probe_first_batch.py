"""Read-only browser probe for changing public TAL and OPPO recruitment portals.

Collect bounded diagnostics only. No credentials, signatures, submissions,
application actions, browser storage or raw API response bodies are used.
"""
from __future__ import annotations

import argparse
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

TAL = "https://job.tal.com/campus/home"
OPPO = "https://career.oppo.com/official/oppo/recruitment/post?recruitType=OFFEN-RECRUITMENT"

def safe_url(value):
    parts = urlsplit(value)
    return parts._replace(query="", fragment="").geturl()

def probe(source):
    public_url = TAL if source == "tal-moka" else OPPO
    allowed_hosts = {"job.tal.com"} if source == "tal-moka" else {"career.oppo.com"}
    result = {"source": source, "initial_url": public_url, "events": [], "observed_responses": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1400, "height": 950})
            def on_response(response):
                parts = urlsplit(response.url)
                # Public employer calls only. Exclude query strings, cookies,
                # credentials and response bodies from logs.
                if (parts.hostname in allowed_hosts
                        and ("job" in parts.path.lower() or "position" in parts.path.lower()
                             or "recruit" in parts.path.lower())):
                    if len(result["observed_responses"]) < 30:
                        result["observed_responses"].append({
                            "method": response.request.method,
                            "path": parts.path[:160],
                            "status": response.status,
                        })
            page.on("response", on_response)
            page.goto(public_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2500)
            result["events"].append("opened public employer site")
            if source == "tal-moka":
                try:
                    link = page.get_by_text("全部职位", exact=True)
                    if link.count() > 0:
                        link.first.click(timeout=8000)
                        page.wait_for_timeout(2500)
                        result["events"].append("clicked public 全部职位 navigation")
                except Exception as exc:
                    result["events"].append("navigation not clickable: " + type(exc).__name__)
            result["final_url"] = safe_url(page.url)
            result["title"] = page.title()[:160]
            body = page.locator("body").inner_text(timeout=10000)
            result["body_preview"] = body[:1800]
            anchors = page.locator("a[href]")
            result["link_count"] = anchors.count()
            link_rows = []
            for i in range(min(anchors.count(), 160)):
                link = anchors.nth(i)
                href = link.get_attribute("href") or ""
                name = (link.inner_text(timeout=2000) or "").strip()[:75]
                if any(part in href.lower() for part in (
                    "job", "position", "detail", "intern", "campus",
                    "recruit", "实习",
                )) or any(part in name for part in ("职位", "实习", "产品")):
                    link_rows.append({"href": safe_url(href)[:200], "label": name})
                if len(link_rows) == 35:
                    break
            result["candidate_links"] = link_rows
        finally:
            browser.close()
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["tal-moka", "oppo-daily"], required=True)
    args = parser.parse_args()
    print(json.dumps(probe(args.source), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
