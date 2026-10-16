"""Huawei official campus public listing UI audit: real intern filter selection.

No application actions, login, resume upload, private APIs, session values or
applicant data. Only browser-visible job names and bounded public job-feed
response shape are recorded.
"""
from __future__ import annotations
import json,re
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

URL="https://career.huawei.com/cn/campus-recruitment-job-list"

def bounded_shape(obj,depth=0):
    """Record key names and public job summary only, not request credentials."""
    if depth>=3:
        return type(obj).__name__
    if isinstance(obj,dict):
        names=list(obj)[:18]
        res={"keys":names}
        for name in ("data","result","records","rows","list","items","total","totalCount",
                     "page","pageNum","pageSize","current","size"):
            if name in obj:
                res[name]=bounded_shape(obj[name],depth+1)
        return res
    if isinstance(obj,list):
        return {"length":len(obj),"first":bounded_shape(obj[0],depth+1) if obj else None}
    if isinstance(obj,(int,bool)):
        return obj
    return type(obj).__name__

def view(page):
    text=page.locator("body").inner_text()
    idx=text.find("在招职位")
    return {"count_hint":text[idx:idx+75],"first_results":text[idx:idx+1250],
            "intern_labels":text.count("实习生")}

def inspect():
    results={"official_url":URL,"job_feed_responses":[]}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            page=browser.new_page(locale="zh-CN",viewport={"width":1450,"height":950})
            def on_response(response):
                p=urlsplit(response.url)
                if not (p.hostname and p.hostname.endswith(".huawei.com")
                        and p.path.endswith("/pub/getJobPage")):
                    return
                item={"status":response.status,"method":response.request.method}
                try:
                    item["shape"]=bounded_shape(response.json())
                except Exception as e:
                    item["error"]=type(e).__name__
                results["job_feed_responses"].append(item)
            page.on("response",on_response)
            page.goto(URL,wait_until="domcontentloaded",timeout=30000)
            page.wait_for_timeout(2500)
            results["initial"]=view(page)
            groups=page.locator(".filter-item")
            results["groups"]=[x.inner_text()[:190] for x in groups.all()[:7]]
            group=groups.filter(has=page.locator(".filter-category",has_text="招聘类别"))
            if group.count()!=1:
                raise ValueError("Huawei public recruitment-category facet is not unique")
            option=group.locator(".categery-item").filter(
                has=page.locator('.categery-name[title="实习生"]'))
            results["matching_intern_controls"]=option.count()
            if option.count()!=1:
                raise ValueError("Huawei official intern facet is ambiguous")
            results["before_control"]=option.first.evaluate(
                "el => ({class:el.className,html:el.outerHTML.slice(0,1100)})")
            option.first.locator(".item-padding").first.click(timeout=7500)
            page.wait_for_timeout(3400)
            results["after_control"]=option.first.evaluate(
                "el => ({class:el.className,html:el.outerHTML.slice(0,1100)})")
            results["after_intern"]=view(page)
            # Only consider category correctly applied if selected control AND
            # actual job list change. Do not infer success from click alone.
            results["content_changed"]=results["initial"]["first_results"]!=results["after_intern"]["first_results"]
            # UI selection of Beijing occurs via nested country list; no
            # unsupported network POSTs or simulated hidden API calls.
        finally:
            browser.close()
    return results

if __name__=="__main__":
    print(json.dumps(inspect(),ensure_ascii=False,indent=2))
