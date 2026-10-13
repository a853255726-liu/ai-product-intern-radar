"""Reusable PUBLIC HTML/SSR adapter for Feishu-hosted recruiting portals.

This adapter does not recreate proprietary request signatures or use credentials.
If a site serves only a JS skeleton / blocks ordinary GETs, fail closed and retain
the previous successful snapshot. Tenant-specific internship taxonomy is audited.
"""
from __future__ import annotations
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

PORTALS = {
    "零一万物": ("https://01ai.jobs.feishu.cn", "/index/position/list"),
    "MiniMax": ("https://vrfi1sk8a0.jobs.feishu.cn", "/index/position/list"),
    "智谱": ("https://zhipu-ai.jobs.feishu.cn", "/index/position/list"),
    "RealAI": ("https://realai.jobs.feishu.cn", "/272867/"),
}
JOB_COUNT = re.compile(r"开启新的工作\s*[（(]\s*(\d+)\s*[）)]")
MAX_PAGES = 50

def parse_list_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    raw = soup.get_text(" ", strip=True)
    m = JOB_COUNT.search(raw)
    if not m:
        raise ValueError("Feishu SSR missing advertised job count; possible JS skeleton")
    total = int(m.group(1))
    # A zero-page result is ambiguous when a signed API fails or SSR is absent.
    # It is not evidence a company's positions are zero.
    if total == 0:
        raise ValueError("Feishu SSR reports zero; cannot distinguish empty scope from blocked rendering")
    records = []
    origin = urlparse(base_url)
    for a in soup.select("a[data-id]"):
        jid = str(a.get("data-id") or "").strip()
        href = urljoin(base_url, str(a.get("href") or ""))
        destination = urlparse(href)
        if not jid.isdigit() or destination.scheme != "https" or destination.hostname != origin.hostname:
            continue
        if not re.search(r"/position/\d+/detail", destination.path):
            continue
        title_el = a.select_one(".positionItem-title-text")
        subtitle = a.select_one(".positionItem-subTitle")
        desc = a.select_one(".positionItem-jobDesc")
        if not title_el or not subtitle:
            continue
        parts = list(subtitle.stripped_strings)
        records.append({
            "id": jid,
            "title": title_el.get_text(" ", strip=True),
            "subtitle": " / ".join(parts),
            "description": desc.get_text("\n", strip=True) if desc else "",
            "url": href,
        })
    return total, records

def collect_feishu_browser(company, page_size=10, max_pages=MAX_PAGES):
    """Render only the employer's public job-board UI using ordinary Chromium.

    This does not emulate internal signed APIs, solve challenges, or use login.
    Stop on blocked scripts, a challenge, missing count, or partial pagination.
    """
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    base, path = PORTALS[company]
    rows_all, expected, page_sizes = [], None, []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1250, "height": 900})
            page.set_default_timeout(18000)
            for index in range(1, max_pages + 1):
                page.goto(f"{base}{path}?current={index}&limit={page_size}",
                          wait_until="domcontentloaded", timeout=30000)
                try:
                    page.locator("a[data-id]").first.wait_for(timeout=18000)
                except BrowserTimeout as exc:
                    raise ValueError("Feishu browser did not render a public position list") from exc
                total, rows = parse_list_html(page.content(), base)
                if expected is None:
                    expected = total
                elif total != expected:
                    raise ValueError("Feishu browser total changed during pagination")
                rows_all.extend(rows)
                page_sizes.append(len(rows))
                if len(rows_all) >= expected:
                    break
                if not rows:
                    raise ValueError("Feishu browser returned an empty intermediate page")
        finally:
            browser.close()
    ids = [x["id"] for x in rows_all]
    if len(ids) != expected or len(set(ids)) != expected:
        raise ValueError(f"Feishu browser incomplete {company}: total={expected}, returned={len(ids)}, unique={len(set(ids))}")
    return rows_all, {
        "reported": expected, "raw_records": len(ids), "unique_ids": len(set(ids)),
        "pages": len(page_sizes), "page_sizes": page_sizes, "failed_pages": 0,
        "status": "公开浏览器页面完整性校验通过",
        "scope": f"{company} 飞书官方招聘门户 {path}，所有招聘类型（需筛实习）",
        "capture": "官网公开职位页面标准浏览器渲染（无登录）"
    }


def collect_feishu(session, company, page_size=10, max_pages=MAX_PAGES):
    if company not in PORTALS:
        raise ValueError("Unconfigured Feishu employer")
    base, path = PORTALS[company]
    all_rows, total, sizes = [], None, []
    for page in range(1, max_pages+1):
        url = f"{base}{path}?current={page}&limit={page_size}"
        response = session.get(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; AIInternshipRadar/1.1)",
            "Accept": "text/html,application/xhtml+xml",
        }, timeout=28)
        response.raise_for_status()
        try:
            reported, rows = parse_list_html(response.text, base)
        except ValueError as exc:
            if page == 1:
                # Standard browser rendering is a fallback for publicly accessible JS
                # sites, never a workaround for login/verification/access challenges.
                return collect_feishu_browser(company, page_size, max_pages)
            raise
        if total is None:
            total = reported
        elif reported != total:
            raise ValueError("Feishu reported total changed between pages")
        all_rows.extend(rows)
        sizes.append(len(rows))
        if len(all_rows) >= total:
            break
        if len(rows) == 0:
            raise ValueError("Feishu pagination returned an empty intermediate page")
    ids = [x["id"] for x in all_rows]
    if len(ids) != total or len(set(ids)) != total:
        raise ValueError(f"Feishu pagination incomplete for {company}: total={total} rows={len(ids)} unique={len(set(ids))}")
    return all_rows, {
        "reported": total, "raw_records": len(ids), "unique_ids": len(set(ids)),
        "pages": len(sizes), "page_sizes": sizes, "failed_pages": 0,
        "status": "公开HTML分页数量一致",
        "scope": f"{company} 飞书官网 {path} 展示的全部类别（包含正式岗）",
        "capture": "官网公开服务端渲染HTML（不调用动态签名接口）",
    }

def normalize_feishu(company, records, today):
    if company not in PORTALS:
        raise ValueError("Unknown Feishu employer")
    jobs = []
    for row in records:
        title = row["title"]
        sub = row["subtitle"]
        duty = row["description"]
        # First select the company-confirmed internship and Beijing, then PM scope.
        if "北京" not in sub or "实习" not in sub:
            continue
        if not re.search(r"产品|策略|用户研究|体验研究|体验运营", title):
            continue
        if re.search(r"算法工程师|研发工程师|全栈.*工程|开发工程|招聘实习|销售运营", title):
            continue
        strong = bool(re.search(r"AI|Agent|智能体|大模型|RAG|LLM|模型评测", title+" "+duty, re.I))
        if not strong and company not in ("零一万物","智谱","MiniMax"):
            continue
        if company == "零一万物" and row["id"] == "7640037085303474458":
            # Existing, manually inspected official role has full details. Don't
            # downgrade manually verified detail into weaker list-only source.
            continue
        if company == "零一万物" and row["id"] == "7667504757090732298":
            continue
        track = "AI Agent" if re.search(r"Agent|智能体", title+" "+duty,re.I) else "AI应用/体验"
        jobs.append({
            "id": "feishu-"+re.sub(r"[^a-z0-9]+","-",company.lower()).strip("-")+"-"+row["id"],
            "company": company, "title": title, "link": row["url"],
            "posted": "", "date_type": "未提供", "group": "AI创业公司",
            "track": track, "fit": "优先关注" if "产品" in title else "可以尝试",
            "days": "未注明", "duration": "未注明",
            "verify": "官网列表（需核对详情）",
            "status": "飞书官网列表显示实习；具体职位限制和名额需确认",
            "team": "企业AI招聘官网 · 具体团队未核",
            "summary": duty[:1600], "requirements": "官网列表未完整披露职位要求；请查看详情。",
            "source": "企业飞书官网公开职位列表（SSR）",
            "note": "此职位来自官网列表、非完整 JD；公开显示不等于确认仍有名额。",
            "graduation": "未核实", "checked": today(),
            "source_post_id": row["id"]
        })
    return jobs
