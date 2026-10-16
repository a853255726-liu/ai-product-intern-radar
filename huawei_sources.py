"""Audit Huawei's public campus listing through its own ordinary browser UI.

This covers the PUBLIC default campus catalogue, which currently shows 102
mostly graduating-cohort jobs. Recruitment-category controls have not yet
been verified to filter internships, so this does NOT claim to cover every
Huawei internship. Each page is fetched only by clicking official pagination.
Never replay undocumented API requests, log in or create an application.
"""
from __future__ import annotations
import re
from urllib.parse import urlsplit
from candidate_scope import is_product_candidate

URL="https://career.huawei.com/cn/campus-recruitment-job-list"
ENDPOINT="/pub/getJobPage"
MAX_PAGES=25
MAX_RECORDS=500

def parse_job_page(payload, expected_page=None):
    if not isinstance(payload,dict) or not isinstance(payload.get("data"),dict):
        raise ValueError("Huawei employer public job feed has no data dictionary")
    block=payload["data"]
    rows=block.get("result")
    meta=block.get("pageVO")
    if not isinstance(rows,list) or not isinstance(meta,dict):
        raise ValueError("Huawei public job cards/pageVO absent")
    total,pages,current,size=[meta.get(k) for k in
                             ("totalRows","totalPages","curPage","pageSize")]
    if any(not isinstance(n,int) for n in (total,pages,current,size)):
        raise ValueError("Huawei job counts are not integers")
    if (not 1<=total<=MAX_RECORDS or not 1<=pages<=MAX_PAGES or
            size<=0 or not 1<=current<=pages or
            pages!=(total+size-1)//size):
        raise ValueError("Huawei public job listing invalid page bounds")
    if expected_page is not None and current!=expected_page:
        raise ValueError("Huawei job listing did not advance to requested page")
    if len(rows)!=min(size,total-(current-1)*size):
        raise ValueError("Huawei reported page rows mismatch")
    output=[]
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("Huawei public job row is not a dictionary")
        code=str(row.get("jobId") or "").strip()
        title=str(row.get("jobName") or "").strip()
        if not code.isdigit() or not title:
            raise ValueError("Huawei job has no stable jobId/title")
        output.append({
            "id":code,"title":title,
            "jobType":str(row.get("jobType") if row.get("jobType") is not None else ""),
            "workPlace":str(row.get("workPlace") or ""),
            "department":str(row.get("deptNameCn") or row.get("deptName") or ""),
            "categoryName":str(row.get("categoryName") or ""),
            "jobDesc":str(row.get("jobDesc") or ""),
            "jobRequire":str(row.get("jobRequire") or ""),
            "releaseDate":str(row.get("releaseDate") or row.get("lastUpdateDate") or ""),
        })
    return output, {"reported":total,"total_pages":pages,"current_page":current,
                    "page_size":size}

def collect_huawei(session=None):
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    captures=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            page=browser.new_page(locale="zh-CN",viewport={"width":1400,"height":940})
            def is_jobs(response):
                parsed=urlsplit(response.url)
                return (parsed.hostname and parsed.hostname.endswith(".huawei.com")
                        and parsed.path.endswith(ENDPOINT)
                        and response.request.method=="POST")
            with page.expect_response(is_jobs,timeout=28000) as initial:
                page.goto(URL,wait_until="domcontentloaded",timeout=30000)
            first,meta=parse_job_page(initial.value.json(),expected_page=1)
            captures.extend(first)
            sizes=[len(first)]
            total=meta["reported"]
            for number in range(2,meta["total_pages"]+1):
                # The Vue pagination control is public and uses an exact
                # numbered <li data-tag="pager-item-pager"> element.
                target=page.locator('li[data-tag="pager-item-pager"]').filter(
                    has_text=re.compile(r"^"+str(number)+r"$"))
                if target.count()!=1:
                    raise ValueError(
                        f"Huawei page {number} is not reachable by verified public pagination")
                try:
                    with page.expect_response(is_jobs,timeout=14000) as next_response:
                        target.first.click(timeout=7000)
                except BrowserTimeout as exc:
                    raise ValueError("Huawei public pagination did not fetch new page") from exc
                rows,info=parse_job_page(next_response.value.json(),expected_page=number)
                if (info["reported"]!=total or
                    info["total_pages"]!=meta["total_pages"] or
                    info["page_size"]!=meta["page_size"]):
                    raise ValueError("Huawei public count changed during page scan")
                captures.extend(rows)
                sizes.append(len(rows))
        finally:
            browser.close()
    ids=[x["id"] for x in captures]
    if len(ids)!=total or len(set(ids))!=total:
        raise ValueError(
            f"Huawei default campus list incomplete reported={total}, "
            f"rows={len(ids)}, unique={len(set(ids))}")
    return captures,{
        "reported":total,"raw_records":len(ids),"unique_ids":len(set(ids)),
        "pages":len(sizes),"page_sizes":sizes,"failed_pages":0,
        "status":"华为官网默认公开校招页完整分页和职位ID已核验；不代表全部实习项目",
        "scope":"仅career.huawei.com默认公开校招列表；实习生筛选控件暂未实际生效，可能遗漏其他实习；绝不将应届生职位计入日常实习",
        "capture":"华为官方公开校招职位UI及浏览器响应（无登录）",
        "caveat":"不是华为全部实习职位完整覆盖；无正式官方详情链接验证时仅展示官网列表",
        "job_type_distribution":{
            code:sum(x["jobType"]==code for x in captures)
            for code in sorted({x["jobType"] for x in captures})
        },
    }

def normalize_huawei(rows,today):
    out=[]
    for row in rows:
        title=row["title"]
        duty=(row.get("jobDesc") or "")+"\n"+(row.get("jobRequire") or "")
        # We have positively verified that jobType '0' is 应届生.
        # Other type codes alone are NOT enough evidence of a daily internship.
        if row.get("jobType")=="0" or "实习" not in title:
            continue
        if "北京" not in row.get("workPlace",""):
            continue
        if not is_product_candidate(title,duty,row.get("categoryName","")):
            continue
        if not re.search(r"(?<![A-Za-z])AI(?![A-Za-z])|Agent|大模型|AIGC|"
                         r"智能体|生成式|LLM|模型评测|智能应用",title+" "+duty,re.I):
            continue
        posted=str(row.get("releaseDate",""))[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",posted):
            posted=""
        out.append({
            "id":"huawei-browser-"+row["id"],"company":"华为",
            "title":title,"link":URL,
            "posted":posted,"date_type":"发布日期" if posted else "未提供",
            "group":"大厂","track":"AI产品/策略","fit":"可以尝试",
            "days":"未注明","duration":"未注明",
            "verify":"华为公开校招列表（专属JD链接未核）",
            "status":"公开默认校招列表识别到实习标题；具体项目和名额待核",
            "team":row.get("department") or "团队未披露",
            "summary":duty[:1800],
            "requirements":(row.get("jobRequire") or "")[:1700],
            "note":"只采公开默认校招列表；未核实实习筛选是否覆盖全渠道，不伪造直达职位链接",
            "source":"华为公开校招职位浏览器列表",
            "graduation":"实习性质需在华为官网再次确认",
            "checked":today(),"source_post_id":row["id"],
        })
    return out
