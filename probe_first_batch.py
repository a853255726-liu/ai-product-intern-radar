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
                employer_domain = (
                    parts.hostname in allowed_hosts
                    or (source == "tal-moka" and bool(parts.hostname)
                        and parts.hostname.endswith(".tal.com"))
                )
                media_type = response.headers.get("content-type", "").lower()
                if (employer_domain and (
                        "json" in media_type
                        or "job" in parts.path.lower()
                        or "position" in parts.path.lower()
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
            if source == "tal-moka":
                # The redesigned site renders clickable job cards without
                # <a> tags. Inspect only public DOM structure, not applicant
                # data, to support a future robust adapter.
                result["card_dom_samples"] = page.evaluate("""() => {
                    const needles = ["27实习转正-AI动画设计实习生",
                                     "英文动画视频实习生",
                                     "AI Agent 儿童智能硬件产品经理"];
                    return needles.map(needle => {
                        const matches = [...document.querySelectorAll("body *")]
                            .filter(el => el.children.length === 0
                                      && (el.textContent || "").includes(needle));
                        return {needle, ancestors: matches.slice(0, 1).map(el => {
                            const path = [];
                            for (let i = 0; i < 5 && el; i++, el = el.parentElement) {
                                path.push({
                                    tag: el.tagName, class: String(el.className).slice(0, 190),
                                    role: el.getAttribute("role"),
                                    dataId: el.getAttribute("data-id"),
                                    html: el.outerHTML.slice(0, 550)
                                });
                            }
                            return path;
                        })};
                    });
                }""")
                result["pagination_text"] = body[-750:]
                # Explore the site's public 日常实习 filter, then open
                # one visible card only to discover the new official
                # detail URL format. Never click '申请/投递'.
                try:
                    filt = page.get_by_text("日常实习", exact=True)
                    if filt.count():
                        filt.first.click(timeout=6000)
                        page.wait_for_timeout(2000)
                        result["daily_filter_probe"] = {
                            "url": safe_url(page.url),
                            "text": page.locator("body").inner_text()[:1750],
                            "visible_cards": page.locator(".job-card").count(),
                        }
                        cards = page.locator(".job-card")
                        if cards.count():
                            result["daily_filter_probe"]["card_preview"] = (
                                cards.first.inner_text()[:550]
                            )
                            cards.first.click(timeout=6000)
                            page.wait_for_timeout(1250)
                            result["daily_filter_probe"]["first_detail_url"] = (
                                safe_url(page.url)
                            )
                            result["daily_filter_probe"]["first_detail_text"] = (
                                page.locator("body").inner_text()[:1800]
                            )
                except Exception as exc:
                    result["daily_filter_probe_error"] = type(exc).__name__ + ": " + str(exc)[:180]


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
