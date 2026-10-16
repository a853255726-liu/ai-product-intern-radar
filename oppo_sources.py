"""OPPO public *daily* internship board (not 2027 cohort campus hiring).

Reads the plain public browser view and reconciles the announced position
count to job codes. Never guesses proprietary numeric detail-route IDs.
"""
from __future__ import annotations
import re
from urllib.parse import urlparse
from candidate_scope import is_product_candidate

URL = "https://career.oppo.com/official/oppo/recruitment/post?recruitType=OFFEN-RECRUITMENT"
COUNT = re.compile(r"在招职位\s*[（(]\s*(\d+)\s*[）)]")
POST_ID = re.compile(r"^职位\s*ID\s*[：:]\s*(J\d{8,14})$", re.I)
DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})\s*发布$")
MAX_LIST = 200

def parse_public_listing(text):
    """Fail closed if the visible browser listing is paginated or truncated."""
    if not isinstance(text, str):
        raise ValueError("OPPO visible listing is missing")
    match = COUNT.search(text)
    if match is None:
        raise ValueError("OPPO public listing count missing")
    total = int(match.group(1))
    if total <= 0 or total > MAX_LIST:
        raise ValueError("OPPO count zero or beyond auditable bound")
    lines = [s.strip() for s in text[match.end():].splitlines() if s.strip()]
    id_indices = [(idx, POST_ID.fullmatch(line).group(1)) for idx, line in enumerate(lines)
                  if POST_ID.fullmatch(line)]
    if len(id_indices) != total:
        raise ValueError(f"OPPO incomplete visible listing: reported={total} IDs={len(id_indices)}")
    codes = [code for _, code in id_indices]
    if len(set(codes)) != total:
        raise ValueError("OPPO repeated job IDs in public listing")
    rows, previous_end = [], 0
    for offset, (index, code) in enumerate(id_indices):
        before = lines[previous_end:index]
        dates = [(k, m.group(1)) for k, line in enumerate(before)
                 if (m := DATE.fullmatch(line))]
        if len(dates) != 1:
            raise ValueError("OPPO card missing unique publication date: " + code)
        date_index, date = dates[0]
        if date_index == 0:
            raise ValueError("OPPO job card has no title: " + code)
        title = before[date_index - 1]
        attrs = before[date_index + 1:]
        if len(attrs) < 3 or not any("日常实习生招聘" in line for line in attrs):
            raise ValueError("OPPO listing contains non-daily or ambiguous role: " + code)
        city = attrs[0]
        # Text between this card's code and the next dated role contains the JD.
        next_boundary = len(lines)
        if offset + 1 < len(id_indices):
            next_id = id_indices[offset + 1][0]
            for date_row in range(index + 1, next_id):
                if DATE.fullmatch(lines[date_row]):
                    next_boundary = max(index + 1, date_row - 1)
                    break
        else:
            next_boundary = min(len(lines), index + 30)
        duty = "\n".join(lines[index + 1:next_boundary])[:3000]
        rows.append({"id": code, "title": title, "city": city,
                     "posted": date, "description": duty})
        previous_end = next_boundary
    return rows, {"reported": total, "raw_records": total, "unique_ids": total,
                  "pages": 1, "page_sizes": [total], "failed_pages": 0,
                  "status": "OPPO官网公开日常实习列表数量及职位代码对账通过",
                  "capture": "OPPO官方日常实习公开招聘页面",
                  "scope": "仅OPPO官网OFFEN-RECRUITMENT日常实习，不包括限定毕业届次的寻梦/应届招聘",
                  "caveat": "仅当公开页面展示全部职位而非分页时适用；没有职位专属数字ID时不伪造直达URL"}

def collect_oppo(session=None):
    from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page(locale="zh-CN", viewport={"width": 1400, "height": 1000})
            page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            if urlparse(page.url).hostname not in ("career.oppo.com", "careers.oppo.com"):
                raise ValueError("OPPO careers URL redirected to unknown host")
            try:
                page.get_by_text(COUNT).first.wait_for(timeout=25000)
            except BrowserTimeout as exc:
                raise ValueError("OPPO public daily internship list did not render") from exc
            # A visible enabled Next control invalidates a single-page audit.
            pager = page.locator(
                'button[aria-label="Next"],button[aria-label="下一页"],'
                '.ant-pagination-next:not(.ant-pagination-disabled)'
            )
            if pager.count() and any(pager.nth(i).is_enabled() for i in range(pager.count())):
                raise ValueError("OPPO listing has additional uncollected pages")
            return parse_public_listing(page.locator("body").inner_text())
        finally:
            browser.close()

def normalize_oppo(rows, today):
    out = []
    for row in rows:
        title = row["title"]
        duty = row["description"]
        if "北京" not in row["city"] or not is_product_candidate(title, duty):
            continue
        if not re.search(
            r"\bAI\b|Agent|AIGC|LLM|大模型|智能体|机器学习|语音助手|"
            r"AI产品|生成式|小布助手|小布|智能搜索|智能推荐",
            title + " " + duty, re.I):
            continue
        out.append({
            "id": "oppo-daily-" + row["id"], "company": "OPPO",
            "title": title, "link": URL,
            "posted": row["posted"], "date_type": "发布日期",
            "group": "大厂", "track": "AI产品/策略",
            "fit": "优先关注", "days": "未注明", "duration": "未注明",
            "verify": "官网职位列表（专属详情链接待核）",
            "status": "OPPO日常实习列表公开显示；剩余名额待核",
            "team": "OPPO官网日常实习 · " + row["id"],
            "summary": duty[:2000] or "详情请见官方列表",
            "requirements": "官网公开列表；详细条件须逐条核验",
            "note": "职位ID已核验，但未取得与其一一对应的数字详情URL，不虚构职位直达",
            "source": "OPPO官方日常实习官网",
            "graduation": "在校生日常实习（细则待核）",
            "checked": today(), "source_post_id": row["id"],
        })
    return out
