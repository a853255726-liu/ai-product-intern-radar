"""Read-only validation of the Sohu-operated Moka recruiting directory.

Origin grounded in the campus.sohu.com official employer link.
No forms, submissions, logins, applications, or credentials.
"""
from __future__ import annotations
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from kimi_sources import parse_list_html

BASE="https://app.mokahr.com/campus-recruitment/sohu/5682"
APPLY_BASE="https://app.mokahr.com/campus_apply/sohu/5682#/jobs"

def inspect():
    result={"official_homepage_link":APPLY_BASE}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            page=browser.new_page(locale="zh-CN",viewport={"width":1400,"height":920})
            for entry in (APPLY_BASE,BASE+"#/jobs/?page=1"):
                item={"entry":entry}
                try:
                    page.goto(entry,wait_until="domcontentloaded",timeout=30000)
                    page.wait_for_timeout(3000)
                    p=urlsplit(page.url)
                    if p.scheme!="https" or p.hostname!="app.mokahr.com":
                        raise ValueError("Sohu Moka navigation left official recruiting host")
                    item["resolved_url"]=p.scheme+"://"+p.hostname+p.path+"#"+p.fragment[:140]
                    item["title"]=page.title()[:140]
                    body=page.locator("body").inner_text(timeout=12000)
                    item["body_head"]=body[:3000]
                    item["result_cards"]=page.locator(
                        'div[class*="results-"] > div[class*="jobs-"] > div[class*="container-"]'
                    ).count()
                    item["job_anchors"]=page.locator('a[href*="#/job/"]').count()
                    item["sample_links"]=[
                        x.get_attribute("href")[:240]
                        for x in page.locator('a[href*="#/job/"]').all()[:8]
                    ]
                    try:
                        total,rows=parse_list_html(page.content(),base=BASE)
                        item["parser_ok"]=True
                        item["count"]=total
                        item["rows_on_page"]=len(rows)
                        item["sample_titles"]=[{"title":r["title"],"tags":r["tags"]} for r in rows[:8]]
                    except Exception as e:
                        item["parser_ok"]=False
                        item["parser_error"]=type(e).__name__+": "+str(e)[:320]
                except Exception as e:
                    item["page_error"]=type(e).__name__+": "+str(e)[:290]
                result.setdefault("entries",[]).append(item)
        finally:
            browser.close()
    return result

if __name__=="__main__":
    print(json.dumps(inspect(),ensure_ascii=False,indent=2))
