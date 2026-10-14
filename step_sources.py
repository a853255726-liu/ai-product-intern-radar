"""Public StepFun campus board, using the same Moka UI contract as Kimi."""
from __future__ import annotations
import re
from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
from kimi_sources import parse_list_html, parse_detail_html
from candidate_scope import is_product_candidate

BASE = "https://app.mokahr.com/campus-recruitment/step/94905"
MAX_PAGES = 12


def list_url(page):
    return f"{BASE}#/jobs/?page={page}"


def collect_step(session=None):
    rows, expected, sizes = [], None, []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1390, "height": 900})
            page.set_default_timeout(20000)
            for index in range(1, MAX_PAGES + 1):
                url = list_url(index)
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.locator('div[class*="results-"] > div[class*="jobs-"] a[href*="#/job/"]').first.wait_for(timeout=20000)
                except BrowserTimeout as exc:
                    raise ValueError("StepFun public position list failed to render") from exc
                total, found = parse_list_html(page.content(), base=BASE)
                if expected is None:
                    expected = total
                elif expected != total:
                    raise ValueError("StepFun total changed during pagination")
                rows.extend(found)
                sizes.append(len(found))
                if len(rows) >= expected:
                    break
            ids = [x["id"] for x in rows]
            if not expected or len(ids) != expected or len(set(ids)) != expected:
                raise ValueError(f"StepFun incomplete: count={expected} rows={len(ids)} unique={len(set(ids))}")

            for row in rows:
                title, tags = row["title"], row["tags"]
                if not ("实习" in " ".join(tags) and is_product_candidate(title, row["description"], " ".join(tags))):
                    continue
                page.goto(row["url"], wait_until="domcontentloaded", timeout=30000)
                try:
                    page.locator('div[class*="job-description-"]').first.wait_for(timeout=20000)
                except BrowserTimeout as exc:
                    raise ValueError("StepFun detail failed to render: " + row["id"]) from exc
                row["description"] = parse_detail_html(page.content())
        finally:
            browser.close()
    return rows, {
        "reported": expected, "raw_records": len(ids), "unique_ids": len(set(ids)),
        "pages": len(sizes), "page_sizes": sizes, "failed_pages": 0,
        "status": "官网 Moka 公开列表全量 ID 校验通过",
        "scope": "阶跃星辰官网 campus/step/94905 校园招聘混合目录；需独立识别实习、北京与 AI 产品岗位",
        "capture": "阶跃星辰 Moka 校园招聘公开浏览器渲染",
    }


def normalize_step(rows, today):
    output = []
    for row in rows:
        title, tags, duty = row["title"], row["tags"], row["description"]
        tag_text = " ".join(tags)
        # Source labels win over suggestive title wording: full-time "实习生"
        # is not automatically treated as a valid internship.
        if "实习" not in tags[:1] or "全职" in tags[:1]:
            continue
        if not is_product_candidate(title, duty, tag_text):
            continue
        if not ("北京" in tag_text or re.search(r"(?:Base|工作地(?:点)?|办公地(?:点)?)\s*[：:\s]*北京", duty, re.I)):
            continue
        if re.search(r"(?:Base|工作地(?:点)?)\s*[：:\s]*(?:上海|深圳|杭州|广州)", duty, re.I):
            continue
        if not re.search(r"AI|Agent|Harness|大模型|智能体|评测|LLM|模型|智能", title+" "+duty, re.I):
            continue
        posted_match = re.search(r"\d{4}-\d{2}-\d{2}", row.get("date", ""))
        output.append({
            "id": "step-moka-" + row["id"], "company": "阶跃星辰",
            "title": title, "link": row["url"],
            "posted": posted_match.group() if posted_match else "",
            "date_type": "发布日期" if posted_match else "未提供",
            "group": "AI创业公司",
            "track": "AI Agent" if re.search(r"Agent|智能体", title+" "+duty, re.I) else "AI应用/体验",
            "fit": "优先关注" if "产品" in title else "可以尝试",
            "days": "≥4天" if re.search(r"每周.{0,15}4\s*天", duty) else "未注明",
            "duration": "未注明", "verify": "官网详情",
            "status": "官网公开实习；实时招聘名额未核",
            "team": "阶跃星辰官方校园招聘 · " + (tags[1] if len(tags)>1 else "团队未披露"),
            "summary": duty[:2300],
            "requirements": "见官方职位详细说明",
            "source": "阶跃星辰官网 Moka 校园职位目录",
            "note": "非 StepStar 专项项目；仅核实本校招入口，具体资格请参考原文。",
            "graduation": "未核实", "checked": today(),
            "source_post_id": row["id"],
        })
    return output
