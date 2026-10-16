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
            # The employer Moka frontend has a distinct 实习生职位 navigation.
            # It is NOT safe to assume a job labelled 2027 is a daily intern.
            # Verify the actual listing behind that public navigation.
            try:
                page.goto(APPLY_BASE,wait_until="domcontentloaded",timeout=30000)
                page.wait_for_timeout(1900)
                nav=page.get_by_text("实习生职位",exact=True)
                result["intern_nav_count"]=nav.count()
                result["intern_nav_html"]=[
                    x.evaluate("el=>el.outerHTML.slice(0,650)")
                    for x in nav.all()[:4]
                ]
                if nav.count():
                    nav.first.click(timeout=9000)
                    page.wait_for_timeout(3000)
                    fragment=urlsplit(page.url)
                    result["intern_nav_resolved"]=(fragment.scheme+"://"+
                        (fragment.hostname or "")+fragment.path+"#"+fragment.fragment[:180])
                    result["intern_listing_text"]=page.locator("body").inner_text()[:3600]
                    try:
                        count,rows=parse_list_html(page.content(),base=BASE)
                        result["intern_parser"]={"reported":count,"cards":len(rows),
                            "titles":[{"title":row["title"],"tags":row["tags"]}
                                      for row in rows[:15]]}
                    except Exception as exc:
                        result["intern_parser_error"]=type(exc).__name__+": "+str(exc)[:260]
                    result["more_jobs_links"]=page.evaluate("""() => [...document.querySelectorAll('a[href]')]
                      .filter(a => /更多职位|校招职位|实习生职位/.test(a.innerText || ''))
                      .map(a => ({text:(a.innerText||'').slice(0,80),
                                  href:(a.getAttribute('href')||'').slice(0,250)}))
                      .slice(0,12)""")
                    # The employer's new Moka internship programme has a
                    # dedicated project identifier. Inspect the ordinary job
                    # list, not a hiring application or external lead.
                    intern_base="https://app.mokahr.com/campus-recruitment/sohu/28313"
                    page.goto(intern_base+"#/jobs/?page=1",
                              wait_until="domcontentloaded",timeout=30000)
                    page.wait_for_timeout(2800)
                    result["dedicated_listing_url"]=page.url
                    result["dedicated_listing_excerpt"]=page.locator("body").inner_text()[:4300]
                    try:
                        num,items=parse_list_html(page.content(),base=intern_base)
                        result["dedicated_listing"]={
                            "reported":num,"cards":len(items),
                            "first_rows":[{"title":row["title"],"tags":row["tags"],
                                           "id":row["id"]} for row in items[:23]]
                        }
                        # Confirm official detail includes usable nature/city
                        # evidence for product internships; do not submit any
                        # application, and never guess a direct job URL.
                        result["candidate_detail_evidence"]=[]
                        targets=[r for r in items if (
                            "产品" in r["title"] or "AI " in r["title"] or
                            "商业分析" in r["title"])][:7]
                        from kimi_sources import parse_detail_html
                        for row in targets:
                            evidence={"title":row["title"],"id":row["id"]}
                            try:
                                page.goto(row["url"],wait_until="domcontentloaded",timeout=30000)
                                page.locator('div[class*="job-description-"]').first.wait_for(timeout=14000)
                                evidence["url"]=page.url
                                evidence["body"]=page.locator("body").inner_text()[:3000]
                                evidence["jd"]=parse_detail_html(page.content())[:1750]
                            except Exception as exc:
                                evidence["error"]=type(exc).__name__+": "+str(exc)[:150]
                            result["candidate_detail_evidence"].append(evidence)
                    except Exception as exc:
                        result["dedicated_listing_error"]=type(exc).__name__+": "+str(exc)[:300]
            except Exception as exc:
                result["intern_nav_error"]=type(exc).__name__+": "+str(exc)[:260]
        finally:
            browser.close()
    return result

if __name__=="__main__":
    print(json.dumps(inspect(),ensure_ascii=False,indent=2))
