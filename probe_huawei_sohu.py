"""Read-only public DOM / route reconnaissance for Huawei and Sohu careers.

Outputs bounded UI controls, official navigation and network-path metadata.
No login, application submission, resume upload or hidden recruitment API use.
"""
import argparse
import json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

SITES = {
    "huawei": "https://career.huawei.com/cn/campus-recruitment-job-list",
    "sohu": "https://campus.sohu.com/",
}
NEEDLES = {
    "huawei": ("实习生", "招聘类别", "应届生", "筛选", "搜索", "岗位类别", "研发类"),
    "sohu": ("招聘批次、岗位列表及申请入口", "立即投递", "立即申请",
             "实习生招聘", "应届生招聘", "最新动态"),
}

def remove_url_parameters(url):
    p = urlsplit(str(url))
    return (p.scheme + "://" + (p.hostname or "") + p.path)[:240]

def inspect_dom(page, site):
    needles = list(NEEDLES[site])
    return page.evaluate("""needles => {
        function basic(el) {
            const attrs = {};
            for(const a of [...el.attributes || []]) {
                if(["id","class","role","type","for","aria-label","aria-checked",
                    "aria-selected","data-state","href","target","onclick","style",
                    "tabindex"].includes(a.name)) {
                    attrs[a.name] = a.value.slice(0,250);
                }
            }
            return { tag: el.tagName, text: (el.innerText||el.textContent||"").trim().slice(0,160), attrs,
                     outer: el.outerHTML.slice(0,750) };
        }
        return needles.map(needle => {
            const hits = [...document.querySelectorAll("body *")].filter(el =>
                el.children.length <= 2 &&
                (el.innerText||el.textContent||"").trim() === needle
            );
            return {needle, count:hits.length, samples:hits.slice(0,4).map(el => {
                let cur=el, path=[];
                for(let depth=0;depth<5&&cur;depth++,cur=cur.parentElement)
                    path.push(basic(cur));
                return path;
            })};
        });
    }""", needles)

def scan(site):
    initial=SITES[site]
    result={"site":site,"initial":initial,"events":[],"responses":[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            page=browser.new_page(locale="zh-CN",viewport={"width":1450,"height":950})
            def observe(response):
                host=urlsplit(response.url).hostname or ""
                if not (host.endswith("huawei.com") or host.endswith("sohu.com") or
                        host.endswith("zhiye.com") or host.endswith("mokahr.com")):
                    return
                if len(result["responses"]) >= 65:
                    return
                path=urlsplit(response.url).path.lower()
                if any(k in path for k in ("position","job","intern","recruit","campus","query","search","list")):
                    result["responses"].append({
                        "method":response.request.method,"path":remove_url_parameters(response.url),
                        "status":response.status,
                        "type":response.headers.get("content-type","").split(";")[0][:50],
                    })
            page.on("response",observe)
            page.goto(initial,wait_until="domcontentloaded",timeout=30000)
            page.wait_for_timeout(2800)
            result["landing_url"]=remove_url_parameters(page.url)
            result["landing_title"]=page.title()
            result["dom_before"]=inspect_dom(page,site)
            if site=="huawei":
                matching=page.get_by_text("实习生",exact=True)
                result["intern_label_count"]=matching.count()
                # Avoid accidentally clicking a recommendation or a listing
                # label; target the exact label inside the 招聘类别 filter.
                for idx in range(min(matching.count(),3)):
                    node=matching.nth(idx)
                    root=node.evaluate("""el => {
                        let a=el;
                        return [...Array(5)].map(() => {const t={
                          tag:a.tagName,cls:String(a.className).slice(0,110),
                          text:(a.innerText||"").slice(0,130),
                          outer:a.outerHTML.slice(0,900)};
                          a=a.parentElement||a;return t;
                        });
                    }""")
                    result["intern_label_ancestors_"+str(idx)]=root
                # A filter selection must change rows/count: capture before/after.
                before=page.locator("body").inner_text()
                for i in range(min(matching.count(),2)):
                    try:
                        matching.nth(i).click(timeout=5500)
                        page.wait_for_timeout(2000)
                        after=page.locator("body").inner_text()
                        result["events"].append({"action":"select intern label "+str(i),
                          "before_count":before.split("在招职位",1)[-1][:65],
                          "after_count":after.split("在招职位",1)[-1][:65],
                          "rows_change":before!=after,
                          "after_excerpt":after[after.find("在招职位"):after.find("在招职位")+850]})
                        if before!=after:break
                    except Exception as e:
                        result["events"].append({"action":"select intern label "+str(i),
                                                 "error":type(e).__name__})
                result["dom_after"]=inspect_dom(page,site)
            else:
                # Homepage CTA is not a job application. Inspect linked
                # recruitment system without clicking any apply action.
                result["outbound_anchors"]=page.evaluate("""() =>
                  [...document.querySelectorAll('a[href]')].map(a=>({
                   text:(a.innerText||"").trim().slice(0,100),
                   href:a.getAttribute('href')?.slice(0,500),
                   target:a.getAttribute('target')||""}))
                  .filter(a => /招聘|职位|实习|立即|申请|投递|campus/i.test(a.text+" "+a.href))
                  .slice(0,30)""")
                result["buttons"]=page.evaluate("""() =>
                    [...document.querySelectorAll('button,[role=button]')]
                      .map(b=>({text:(b.innerText||"").slice(0,100),
                                 html:b.outerHTML.slice(0,650)})).slice(0,25)""")
            result["result_url"]=remove_url_parameters(page.url)
        finally:
            browser.close()
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--site",choices=sorted(SITES),required=True)
    args=parser.parse_args()
    print(json.dumps(scan(args.site),ensure_ascii=False,indent=2))
