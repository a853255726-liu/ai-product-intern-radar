"""Sohu official standalone DAILY internship directory, Moka programme 28313.

Programme ID 28313 comes from the exact '实习生职位' link on the employer's
campus.sohu.com homepage, NOT the graduate programme 5682. Reconcile all
public cards and UUIDs; only publish Beijing AI/product posts with a grounded
official city. No login, application action or private APIs.
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit
from candidate_scope import is_product_candidate
from tal_sources import explicit_grad_only
from kimi_sources import parse_list_html, parse_detail_html

BASE="https://app.mokahr.com/campus-recruitment/sohu/28313"
HOME="https://app.mokahr.com/campus_apply/sohu/28313#/"
PAGE_LIMIT=12
CARD_SELECTOR='div[class*="results-"] > div[class*="jobs-"] a[href*="#/job/"]'
JD_SELECTOR='div[class*="job-description-"]'
LOCATION_LINE=re.compile(r"^(?:北京市|上海市|天津市|广州市|深圳市|杭州市|中国)$")
DETAIL_WORTH=re.compile(r"产品|商业分析|用户研究|体验|评测|策略|AI|Agent|GEO|大模型|智能",re.I)
AI_ROLE=re.compile(r"(?<![A-Za-z])AI(?![A-Za-z])|AIGC|Agent|LLM|MCP|"
                   r"大模型|生成式|智能体|模型评测|模型效果|Prompt|提示词|"
                   r"内容质量评测|AI能力|智能推荐",re.I)

def list_url(i):
    if not 1<=i<=PAGE_LIMIT:
        raise ValueError("SOHU Moka page outside bounded public source")
    return BASE+"#/jobs/?page="+str(i)

def cities_from_home(text):
    """Employer's internship landing cards display title then literal city."""
    lines=[x.strip() for x in str(text).splitlines() if x.strip()]
    found={}
    for i,line in enumerate(lines):
        if LOCATION_LINE.fullmatch(line) and i:
            title=lines[i-1]
            if "实习" in title and title not in found:
                found[title]=line
    return found

def is_beijing(row):
    city=row.get("official_city") or ""
    text=row.get("description") or ""
    # A city in a general requirement such as 'Beijing universities
    # preferred' is NOT an official work location.
    if city:
        return city=="北京市"
    return bool(re.search(
        r"(?:工作地点|办公地点|工作城市|base)\s*[：:\n ]+\s*北京市?(?![^\n]{0,15}(?:或|/|、)(?:上海|广州|深圳))",
        text,re.I))

def normalize_sohu(rows,today):
    out=[]
    for row in rows:
        title=row.get("title","")
        duty=row.get("description","")
        if "实习" not in title or re.search(r"【2027】|【2026】|仅招20\d{2}届",title):
            continue
        if not is_beijing(row) or not is_product_candidate(title,duty):
            continue
        if not AI_ROLE.search(title+" "+duty):
            continue
        # Even if a role appears in a separate internship programme,
        # explicitly graduate-only eligibility remains disqualifying.
        grad=explicit_grad_only(title+" "+duty)
        if grad:
            continue
        posted=re.search(r"\d{4}-\d{2}-\d{2}",row.get("date",""))
        days=("≥5天" if re.search(r"每周.{0,12}5\s*天",duty)
              else "3–5天" if re.search(r"每周.{0,12}3\s*[-—至到]\s*5\s*天",duty)
              else "未注明")
        duration=("≥6个月" if re.search(r"(?:至少|连续|保证|持续)\s*6\s*个?月",duty)
                  else "≥3个月" if re.search(r"(?:至少|连续|保证|持续)\s*3\s*个?月",duty)
                  else "未注明")
        track=("AI评测/策略" if re.search(r"评测|评估|评测集",title+duty)
               else "AI数据产品" if "数据产品" in title
               else "AI应用/产品运营")
        out.append({
            "id":"sohu-moka-"+row["id"],"company":"搜狐",
            "title":title,"link":row["url"],
            "posted":posted.group() if posted else "",
            "date_type":"发布日期" if posted else "未提供",
            "group":"中型/行业科技","track":track,
            "fit":"优先关注" if re.search(r"AI|评测|数据产品",title,re.I) else "可以尝试",
            "days":days,"duration":duration,
            "verify":"搜狐官方Moka职位详情（剩余HC待核）",
            "status":"官方日常实习项目仍在列表中，具体HC待核",
            "team":"搜狐 · "+((row.get("tags") or ["业务团队未披露"])[0]),
            "summary":duty[:2300],
            "requirements":duty[:2300],
            "note":"工作地点依据搜狐官方实习项目公开城市标签或JD明确标注；AI职责来自官方详情",
            "source":"搜狐官方Moka日常实习项目",
            "graduation": "在校生日常实习（详情中无明确限届条件）",
            "graduation_restriction_confirmed":False,
            "checked":today(),"source_post_id":row["id"],
            "official_work_city":row.get("official_city",""),
        })
    return out

def collect_sohu(session=None):
    from playwright.sync_api import sync_playwright,TimeoutError as BrowserTimeout
    records=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            page=browser.new_page(locale="zh-CN",viewport={"width":1400,"height":930})
            page.goto(HOME,wait_until="domcontentloaded",timeout=30000)
            page.wait_for_timeout(1800)
            citymap=cities_from_home(page.locator("body").inner_text())
            if len(citymap)<3:
                raise ValueError("Sohu public internship landing city-label evidence did not render")
            total=None
            page_sizes=[]
            for idx in range(1,PAGE_LIMIT+1):
                page.goto(list_url(idx),wait_until="domcontentloaded",timeout=30000)
                try:
                    page.locator(CARD_SELECTOR).first.wait_for(timeout=17000)
                except BrowserTimeout as exc:
                    raise ValueError("Sohu dedicated internship public results did not render") from exc
                announced,rows=parse_list_html(page.content(),base=BASE)
                if total is None:
                    total=announced
                elif total!=announced:
                    raise ValueError("Sohu Moka total changed during pagination")
                for row in rows:
                    row["official_city"]=citymap.get(row["title"],"")
                page_sizes.append(len(rows))
                records.extend(rows)
                if len(records)>=total:
                    break
            ids=[r["id"] for r in records]
            if not total or len(ids)!=total or len(set(ids))!=total:
                raise ValueError(
                    f"Sohu daily internship incomplete: reported={total} "
                    f"retrieved={len(ids)} unique={len(set(ids))}")
            # Verify relevant official JDs, not merely job-title keywords.
            for row in records:
                if not DETAIL_WORTH.search(row["title"]):
                    continue
                page.goto(row["url"],wait_until="domcontentloaded",timeout=30000)
                try:
                    page.locator(JD_SELECTOR).first.wait_for(timeout=17000)
                except BrowserTimeout as exc:
                    raise ValueError("Sohu official product-related JD missing: "+row["id"]) from exc
                row["description"]=parse_detail_html(page.content())
        finally:
            browser.close()
    return records,{
        "reported":total,"raw_records":len(records),
        "unique_ids":len(set(ids)),"pages":len(page_sizes),
        "page_sizes":page_sizes,"failed_pages":0,
        "status":"搜狐官方独立日常实习Moka项目完整分页、唯一UUID及产品候选JD已对账",
        "scope":"仅搜狐官网实习生职位所指向的Moka 28313项目，非2027校招5682；北京AI产品再逐条筛选",
        "capture":"搜狐官方Moka独立实习项目（普通浏览器）",
        "caveat":"官网独立实习项目不等于所有产品职位与HC；城市缺官方证据者不发布",
        "location_labels_from_official_home":len(citymap),
    }
