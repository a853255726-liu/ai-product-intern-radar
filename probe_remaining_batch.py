"""Read-only probes for verified employer-operated internship list pages.

This tool is not a collector. It never logs in, clicks application buttons,
submits data, or publishes jobs. Its output is a bounded public DOM snapshot
that helps identify usable recruitment filters, links and pagination.
"""
from __future__ import annotations

import argparse
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

SITES = {
    "autohome": {
        "url": "https://talent.autohome.com.cn/campus-recruit-list.html",
        "host": "talent.autohome.com.cn",
        "keywords": ("实习", "职位", "北京", "产品"),
    },
    "huawei": {
        "url": "https://career.huawei.com/reccampportal/portal5/campus-recruitment-detail.html?jobType=0&recruitType=CR",
        "host": "career.huawei.com",
        "keywords": ("实习", "职位", "北京", "产品"),
    },
    "sohu": {
        "url": "https://campus.sohu.com/",
        "host": "campus.sohu.com",
        "keywords": ("实习", "职位", "岗位", "立即投递"),
    },
}

def safe_link(link, expected_host):
    """Include only public employer-host navigation (without query values)."""
    u = urlsplit(str(link))
    return (u._replace(query="", fragment="").geturl()
            if u.scheme == "https" and u.hostname == expected_host else "")

def inspect(site):
    cfg = SITES[site]
    result = {"company": site, "requested_url": cfg["url"], "events": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1340, "height": 900})
            page.goto(cfg["url"], wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2300)  # public frontend hydration
            destination = urlsplit(page.url)
            if destination.scheme != "https" or destination.hostname != cfg["host"]:
                raise ValueError("Unexpected employer recruitment redirect: " + str(destination.hostname))
            result["resolved_url"] = safe_link(page.url, cfg["host"])
            result["title"] = page.title()[:140]
            visible = page.locator("body").inner_text(timeout=12000)
            result["visible_text_excerpt"] = visible[:4800]
            result["keywords_present"] = [word for word in cfg["keywords"] if word in visible]
            # Use only the employer's public navigation. Never click
            # an application or login button while inspecting job lists.
            links = []
            for entry in page.locator("a[href]").all()[:160]:
                url = safe_link(entry.get_attribute("href") or "", cfg["host"])
                if not url:
                    continue
                label = (entry.inner_text(timeout=1500) or "").strip()[:85]
                if any(k in label or k in url for k in ("实习","职位","岗位","招聘","job","campus","position","recruit")):
                    obj = {"label": label, "url": url}
                    if obj not in links:
                        links.append(obj)
                if len(links) >= 28:
                    break
            result["public_navigation_links"] = links
            result["pagination_visible"] = any(
                word in visible for word in ("下一页", "共3页", "共 3 页", "末页")
            )
            result["job_like_cards"] = {
                ".job-card": page.locator(".job-card").count(),
                "[class*=job-item]": page.locator('[class*="job-item"]').count(),
                "[class*=position-item]": page.locator('[class*="position-item"]').count(),
            }
            result["status"] = (
                "public_page_renders_recruiting_content"
                if result["keywords_present"] else "visible_recruiting_content_not_found"
            )
        finally:
            browser.close()
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", choices=sorted(SITES), required=True)
    args = ap.parse_args()
    print(json.dumps(inspect(args.site), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
