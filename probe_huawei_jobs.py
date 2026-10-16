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
                    obj=response.json()
                    item["shape"]=bounded_shape(obj)
                    body=obj.get("data",{}) if isinstance(obj,dict) else {}
                    rows=body.get("result",[]) if isinstance(body,dict) else []
                    pagevo=body.get("pageVO",{}) if isinstance(body,dict) else {}
                    if isinstance(pagevo,dict):
                        item["public_page_fields"]={
                            k:v for k,v in pagevo.items()
                            if isinstance(v,(str,int,float,bool)) and len(str(v))<90}
                    if isinstance(rows,list) and rows and isinstance(rows[0],dict):
                        item["public_record_keys"]=list(rows[0])[:65]
                        item["sample_job_fields"]={
                            k:str(v)[:180] for k,v in rows[0].items()
                            if any(t in k.lower() for t in (
                                "jobid","positionid","postid","jobname",
                                "positionname","jobtype","recruittype",
                                "city","workplace","postname","category"
                            )) and isinstance(v,(str,int,float,bool))}
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
            # Inspect ordinary public pagination without hidden endpoint
            # calls; record whether page 2 really updates the public feed.
            result_pagination=page.evaluate("""() => [...document.querySelectorAll('*')]
                .filter(el => el.children.length<=1 && el.textContent.trim()==='2')
                .slice(0,8).map(el=>el.outerHTML.slice(0,500))""")
            results["page_two_controls"]=result_pagination
            try:
                page.get_by_text("2",exact=True).first.click(timeout=6000)
                page.wait_for_timeout(1900)
                results["page_two_view"]=view(page)
            except Exception as e:
                results["page_two_error"]=type(e).__name__+": "+str(e)[:180]
            # UI selection of Beijing occurs via nested country list; no
            # unsupported network POSTs or simulated hidden API calls.
        finally:
            browser.close()
    return results

if __name__=="__main__":
    print(json.dumps(inspect(),ensure_ascii=False,indent=2))
