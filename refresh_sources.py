"""Audit official recruitment APIs and append Beijing AI/product internship candidates.
An incomplete source never removes or overwrites existing manually verified jobs.
Run: python refresh_sources.py --sources meituan xhs tencent jd
"""
import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from extra_sources import make_sources, normalize_extra
from feishu_sources import PORTALS as FEISHU_PORTALS, collect_feishu, normalize_feishu
from candidate_scope import is_product_candidate
from kimi_sources import collect_kimi, normalize_kimi, BASE as KIMI_BASE
from bytedance_sources import bytedance, normalize_bytedance
from alibaba_sources import collect_alibaba, normalize_alibaba
from step_sources import collect_step, normalize_step, BASE as STEP_BASE

ROOT = Path(__file__).resolve().parent
TODAY = lambda: datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
HEADERS = {"user-agent": "Mozilla/5.0 (compatible; PersonalInternshipRadar/1.0)",
           "accept": "application/json,text/plain,*/*", "content-type": "application/json;charset=UTF-8"}

def request_json(session, method, url, payload=None, referer=None):
    headers = dict(HEADERS)
    if referer:
        headers["Referer"] = referer
        headers["Origin"] = "/".join(referer.split("/")[:3])
    for attempt in range(3):
        try:
            res = session.request(method, url, json=payload, headers=headers, timeout=22)
            if res.status_code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            res.raise_for_status()
            return res.json()
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))

def collect(label, page_request, unpack, max_pages=200):
    result, total, seen_pages = [], None, []
    for page in range(1, max_pages + 1):
        raw = page_request(page)
        records, count, id_field = unpack(raw)
        if not isinstance(records, list) or not isinstance(count, int) or count < 0:
            raise ValueError(label + ": missing list or valid reported count")
        if total is None:
            total = count
        if total != count:
            raise ValueError(label + ": count changed during pagination")
        if any(not isinstance(x, dict) or not x.get(id_field) for x in records):
            raise ValueError(label + ": records without stable job ID")
        result.extend(records)
        seen_pages.append(len(records))
        if len(result) >= total:
            break
        if not records:
            raise ValueError(label + ": early empty page")
        time.sleep(0.55)
    ids = [str(x[id_field]) for x in result]
    if len(result) != total or len(set(ids)) != total:
        raise ValueError("%s: reported=%s retrieved=%s unique=%s" %
                         (label, total, len(result), len(set(ids))))
    return result, {"reported": total, "raw_records": len(result), "unique_ids": len(set(ids)),
                    "pages": len(seen_pages), "failed_pages": 0, "page_sizes": seen_pages,
                    "status": "分页数量一致", "last_checked": TODAY()}

def meituan(s):
    def one(page):
        return request_json(s, "POST", "https://zhaopin.meituan.com/api/official/job/getJobList",
            {"page": {"pageNo": page, "pageSize": 100}, "jobShareType": "1",
             "keywords": "", "cityList": [], "department": [], "jfJgList": [],
             "jobType": [{"code": "2", "subCode": []}], "typeCode": [], "specialCode": []},
            "https://zhaopin.meituan.com/web/campus")
    records, meta = collect("美团", one,
                           lambda x: (x.get("data", {}).get("list"),
                                      x.get("data", {}).get("page", {}).get("totalCount"), "jobUnionId"))
    meta["scope"] = "官网校招实习类别，不代表其他渠道"
    return records, meta

def xhs(s):
    def one(page):
        return request_json(s, "POST",
            "https://job.xiaohongshu.com/websiterecruit/position/pageQueryPosition",
            {"recruitType": "campus", "positionName": "", "pageNum": page, "pageSize": 100},
            "https://job.xiaohongshu.com/campus/position")
    records, meta = collect("小红书", one,
                           lambda x: (x.get("data", {}).get("list"),
                                      x.get("data", {}).get("total"), "positionId"))
    meta["scope"] = "校园招聘混合目录，含非实习职位"
    return records, meta

def tencent(s):
    all_records, segments, sub = [], {}, []
    for mapping, name in ((104, "日常实习"),):
        def one(page):
            body = {"projectIdList": [], "projectMappingIdList": [mapping], "keyword": "",
                    "bgList": [], "workCountryType": 1, "workCityList": ["2"],
                    "recruitCityList": [], "positionFidList": [],
                    "pageIndex": page, "pageSize": 20}
            return request_json(s, "POST",
                "https://join.qq.com/api/v1/position/searchPosition?timestamp=" +
                str(round(time.time() * 1000)), body, "https://join.qq.com/post.html")
        records, audit = collect("腾讯" + name, one,
                                lambda x: (x.get("data", {}).get("positionList"),
                                           x.get("data", {}).get("count"), "postId"))
        all_records.extend(records)
        segments[name] = audit["reported"]
        sub.append(audit)
    ids = [str(x["postId"]) for x in all_records]
    if len(ids) != len(set(ids)):
        raise ValueError("腾讯招聘项目间发现重复职位 ID")
    meta = {"reported": sum(segments.values()), "raw_records": len(ids),
            "unique_ids": len(set(ids)), "pages": sum(x["pages"] for x in sub),
            "failed_pages": 0, "by_project": segments,
            "status": "分页数量一致", "last_checked": TODAY(),
            "scope": "仅北京日常实习项目 mapping=104，不包括应届实习/青云/部门直招"}
    return all_records, meta

def baidu(s):
    """Baidu internship vacancies, form-encoded public API with 10 records per page."""
    def one(page):
        form = {"recruitType": "INTERN", "pageSize": "10", "keyWord": "",
                "curPage": str(page), "projectType": "", "workPlace": "1100",
                "postType": "2"}
        headers = dict(HEADERS)
        headers.update({"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                        "Origin": "https://talent.baidu.com",
                        "Referer": "https://talent.baidu.com/jobs/intern-list?dev=0"})
        response = s.post("https://talent.baidu.com/httservice/getPostListNew",
                          data=form, headers=headers, timeout=22)
        response.raise_for_status()
        reply = response.json()
        if reply.get("status") != "ok":
            raise ValueError("Baidu response status is not ok")
        return reply
    records, meta = collect("百度INTERN北京产品", one,
        lambda x: ((x.get("data") or {}).get("list"),
                   int((x.get("data") or {}).get("total", -1)), "postId"))
    meta.update(scope="仅 INTERN，北京市 workPlace=1100，产品类别 postType=2",
                capture="百度官网表单职位 API")
    return records, meta

def jd(s):
    def one(page):
        return request_json(s, "POST",
            "https://campus.jd.com/api/wx/position/page?type=internship",
            {"pageSize": 50, "pageIndex": page - 1,
             "parameter": {"positionName": "", "planIdList": [],
                           "jobDirectionCodeList": [], "workCityCodeList": [],
                           "positionDeptList": []}}, "https://campus.jd.com/")
    records, meta = collect("京东internship", one,
                           lambda x: (x.get("body", {}).get("items"),
                                      x.get("body", {}).get("totalNumber"), "publishId"))
    meta["scope"] = "京东官方 type=internship 实习类别（全城市），与正式校招类型不同"
    return records, meta

SOURCES = {"美团": meituan, "小红书": xhs, "腾讯": tencent, "京东": jd, "百度": baidu}
SOURCES.update(make_sources(request_json, collect, TODAY))
SOURCES.update({name: (lambda session, company=name: collect_feishu(session, company)) for name in FEISHU_PORTALS})
SOURCES["月之暗面"] = collect_kimi
SOURCES["字节跳动"] = bytedance
SOURCES["阿里巴巴"] = collect_alibaba
SOURCES["阶跃星辰"] = collect_step
KEYS = {"meituan": "美团", "xhs": "小红书", "tencent": "腾讯", "jd": "京东", "baidu": "百度", "kuaishou": "快手", "mihoyo": "米哈游", "xiaomi": "小米", "feishu-zeroone": "零一万物", "feishu-minimax": "MiniMax", "feishu-zhipu": "智谱", "feishu-realai": "RealAI", "feishu-baichuan": "百川智能", "feishu-iqiyi": "爱奇艺", "feishu-shengshu": "生数科技", "feishu-modelbest": "面壁智能", "kimi-moka": "月之暗面", "bytedance-daily": "字节跳动", "alibaba-public": "阿里巴巴", "step-moka": "阶跃星辰"}

def normalize(company, records):
    if company in ('快手', '米哈游', '小米'):
        return normalize_extra(company, records, TODAY)
    if company in FEISHU_PORTALS:
        return normalize_feishu(company, records, TODAY)
    if company == "月之暗面":
        return normalize_kimi(records, TODAY)
    if company == "字节跳动":
        return normalize_bytedance(records, TODAY)
    if company == "阿里巴巴":
        return normalize_alibaba(records, TODAY)
    if company == "阶跃星辰":
        return normalize_step(records, TODAY)
    out = []
    for r in records:
        name, city, key, url, team, date, date_type, duty, requirements = (
            "", "", "", "", "", "", "未提供", "", "")
        if company == "美团":
            name = r.get("name") or ""
            city = "/".join(x.get("name", "") for x in (r.get("cityList") or []) if isinstance(x, dict))
            key = str(r.get("jobUnionId"))
            url = "https://zhaopin.meituan.com/web/position/detail?highlightType=campus&jobUnionId=" + key
            team = r.get("jobFamily") or ""
            date = r.get("refreshTime") or ""
            date_type = "更新时间"
            if team != "产品类" and not is_product_candidate(name):
                continue
        elif company == "小红书":
            name = r.get("positionName") or ""
            city = r.get("workplace") or ""
            key = str(r.get("positionId"))
            url = "https://job.xiaohongshu.com/campus/position/" + key
            team = r.get("jobProjectName") or ""
            date = r.get("publishTime") or ""
            date_type = "发布日期"
            duty, requirements = r.get("duty") or "", r.get("qualification") or ""
            if r.get("recruitStatus") != "in_recruitment":
                continue
            # Campus projects are eligible leads if confirmed internship;
            # only explicitly graduate-only positions are excluded downstream.
            if "实习" not in name and "实习" not in team:
                continue
            if "校招" in team and "实习" not in team:
                continue
        elif company == "腾讯":
            name = r.get("positionTitle") or ""
            city = r.get("workCities") or ""
            key = str(r.get("postId"))
            url = "https://join.qq.com/post_detail.html?postid=" + key
            team = str(r.get("bgs") or "")
        elif company == "百度":
            name = r.get("name") or ""
            city = r.get("workPlace") or ""
            key = str(r.get("postId") or "")
            url = "https://talent.baidu.com/jobs/detail/INTERN/" + key + "?dev=0"
            team = str(r.get("orgName") or r.get("bgShortName") or "")
            duty = r.get("workContent") or ""
            requirements = r.get("serviceCondition") or ""
            date = r.get("publishDate") or ""
            date_type = "发布日期"
        elif company == "京东":
            name = r.get("positionName") or ""
            city = "/".join(str(x.get("workCity") or "") for x in (r.get("requirementVoList") or []) if isinstance(x, dict))
            key = str(r.get("publishId") or "")
            url = "https://campus.jd.com/#/details?id=" + key
            team = r.get("jobDirection") or ""
            duty = r.get("workContent") or ""
            requirements = r.get("qualification") or ""
            date = r.get("publishTime") or ""
            date_type = "发布日期"
        # A provider occasionally returned placeholder postId=-3; never
        # publish a link that cannot open an actual detail page.
        if company == "腾讯" and (not key.isdigit() or int(key) <= 0):
            continue
        if "北京" not in str(city):
            continue
        if re.search("工程师|算法|人力资源|招聘专员|招聘HR|数据标注", name, re.I):
            continue
        if not is_product_candidate(name, duty, team):
            continue
        content = " ".join([name, duty, requirements])
        ai = bool(re.search("AI|Agent|智能|大模型|LLM|RAG|MCP|AIGC|模型|推荐|搜索|评测|数据产品",
                            content, re.I))
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date / 1000, ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
        date = str(date or "")[:10]
        ident = {"美团": "meituan", "小红书": "xhs", "腾讯": "tencent", "京东": "jd", "百度": "baidu"}[company] + "-" + key
        out.append({"id": ident, "company": company, "title": name, "link": url,
            "posted": date, "date_type": date_type, "group": "大厂",
            "track": "AI 产品/策略" if ai else "相邻产品",
            "fit": "优先关注" if ai else "可以尝试", "days": "未注明",
            "duration": "未注明", "verify": "官网API（详情待复核）", "status": "接口有记录",
            "team": team, "summary": duty[:1400] if duty else "官方列表已有职位，详情尚待核验",
            "requirements": requirements[:1000] if requirements else "需打开官网 JD 核对",
            "note": "当前 API 记录不等于独立 HC；需要核对毕业届次、工作城市和投递状态",
            "source": "企业招聘官网公开 API", "graduation": "未核实", "checked": TODAY()})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+", choices=["meituan", "xhs", "tencent", "jd", "baidu", "kuaishou", "mihoyo", "xiaomi", "feishu-zeroone", "feishu-minimax", "feishu-zhipu", "feishu-realai", "feishu-baichuan", "feishu-iqiyi", "feishu-shengshu", "feishu-modelbest", "kimi-moka", "bytedance-daily", "alibaba-public", "step-moka", "all"],
                    default=["meituan", "xhs", "tencent"])
    ap.add_argument("--audit-only", action="store_true")
    args = ap.parse_args()
    selected = list(SOURCES) if "all" in args.sources else [KEYS[k] for k in args.sources]
    dbpath = ROOT / "jobs.json"
    data = json.loads(dbpath.read_text(encoding="utf-8"))
    all_jobs = {str(x["id"]): x for x in data["jobs"]}
    audits = data.setdefault("source_audits", {})
    attempts = data.setdefault("source_attempts", {})
    errors, successes = [], 0
    rawdir = ROOT / "data" / "raw"
    rawdir.mkdir(parents=True, exist_ok=True)
    for company in selected:
        try:
            with requests.Session() as session:
                records, meta = SOURCES[company](session)
            (rawdir / (company + "_latest.json")).write_text(
                json.dumps({"checked": TODAY(), "records": records}, ensure_ascii=False), encoding="utf-8")
            meta.setdefault("last_checked", TODAY())
            audits[company] = meta
            if company in ("快手", "米哈游", "小米", "月之暗面", "字节跳动", "阿里巴巴", "阶跃星辰") or company in FEISHU_PORTALS:
                info = data.setdefault("company_coverage", {}).setdefault(company, {})
                info.update({"source": meta.get("capture", "官方公开招聘接口"),
                             "level": "complete_public_html" if company in FEISHU_PORTALS or company in ("月之暗面","阶跃星辰") else "partial" if company in ("字节跳动", "阿里巴巴") else "complete_api",
                             "coverage": f"已核对本接口 {meta['unique_ids']} 个唯一职位 ID；企业其他渠道尚未全量核验",
                             "website": (FEISHU_PORTALS[company][0] + FEISHU_PORTALS[company][1]) if company in FEISHU_PORTALS else (KIMI_BASE+"#/jobs" if company == "月之暗面" else STEP_BASE+"#/jobs" if company == "阶跃星辰" else "https://jobs.bytedance.com/campus/position" if company == "字节跳动" else "https://campus-talent.alibaba.com/campus/position?batchId=100000560002&lang=zh" if company == "阿里巴巴" else "https://campus.kuaishou.cn/" if company == "快手" else "https://jobs.mihoyo.com/" if company == "米哈游" else "https://hr.xiaomi.com/website/opportunities.html")})
            attempts[company] = {"status": "成功（当前接口）", "checked": TODAY(),
                                 "reported": meta["reported"], "unique_ids": meta["unique_ids"]}
            successes += 1
            found, new = normalize(company, records), 0
            if not args.audit_only:
                for job in found:
                    ident = job["id"]
                    # Link a previously researched third-party Xiaomi vacancy to
                    # its official larkJobCode; avoid double-counting the same job.
                    if company == "小米" and job.get("source_job_code"):
                        code = job["source_job_code"]
                        prior_id = next((k for k, v in all_jobs.items()
                            if k.startswith("xiaomi-") and k != ident
                            and (v.get("source_job_code") == code or k.endswith("-"+code))), None)
                        if prior_id:
                            existing = all_jobs[prior_id]
                            existing.update(job)
                            existing["id"] = prior_id
                            existing["note"] += " 已根据官方职位编号 "+code+" 与历史第三方线索合并。"
                            existing["last_seen"] = TODAY()
                            continue
                    # Preserve manually verified details when an official
                    # list contains the same post under a different ID format.
                    duplicate = None
                    if company == "百度":
                        m = re.search(r"J\d+", job.get("title", ""))
                        if m:
                            code = m.group()
                            duplicate = next((k for k, v in all_jobs.items()
                                if v.get("company") == company and k != ident
                                and (k == "baidu-"+code
                                     or re.search(r"\b"+code+r"\b", v.get("title","")))), None)
                    elif company in FEISHU_PORTALS or company in ("月之暗面", "字节跳动", "阿里巴巴", "阶跃星辰"):
                        sid = str(job.get("source_post_id") or "")
                        code = str(job.get("source_job_code") or "")
                        if sid:
                            duplicate = next((k for k,v in all_jobs.items()
                                if v.get("company") == company and k != ident
                                and (str(v.get("source_post_id") or "") == sid
                                     or ("/position/"+sid+"/detail") in str(v.get("link") or "")
                                     or (company in ("月之暗面","阶跃星辰") and "/job/"+sid in str(v.get("link") or ""))
                                     or (company == "字节跳动" and "/position/"+sid+"/detail" in str(v.get("link") or ""))
                                     or (company == "阿里巴巴" and "/campus/position/"+sid in str(v.get("link") or ""))
                                     or (code and (str(v.get("source_job_code") or "") == code
                                        or k.endswith("-"+code))))), None)
                    if duplicate:
                        existing = all_jobs[duplicate]
                        existing["checked"] = TODAY()
                        existing["last_seen"] = TODAY()
                        # A previously discovered listing/third-party lead can gain
                        # an actual official detail URL, without overwriting verified JD.
                        from official_links import classify_link
                        if (classify_link(job.get("link")) == "official_detail"
                                and classify_link(existing.get("link")) != "official_detail"):
                            existing["link"] = job["link"]
                            existing["source_url"] = job["link"]
                            existing["verify"] = job["verify"]
                            existing["summary"] = job.get("summary") or existing.get("summary", "")
                            existing["requirements"] = job.get("requirements") or existing.get("requirements", "")
                            existing["source_post_id"] = job.get("source_post_id")
                            existing["source_job_code"] = job.get("source_job_code")
                    elif ident not in all_jobs:
                        job["first_seen"] = TODAY()
                        job["last_seen"] = TODAY()
                        all_jobs[ident] = job
                        new += 1
                    else:
                        existing = all_jobs[ident]
                        existing["checked"] = TODAY()
                        existing["last_seen"] = TODAY()
                        # Fresh official Alibaba batch evidence improves the
                        # system-generated fit and time metadata on later runs.
                        # Never rewrite a separately curated historical lead.
                        if (company == "阿里巴巴"
                                and existing.get("first_seen")
                                and existing.get("source") == job.get("source")):
                            for field in ("fit", "days", "duration",
                                          "internship_kind", "daily_evidence"):
                                existing[field] = job.get(field, existing.get(field))
            print(company, "reported", meta["reported"], "unique", meta["unique_ids"],
                  "candidates", len(found), "new", new)
        except Exception as exc:
            message = company + ": " + type(exc).__name__ + ": " + str(exc)
            errors.append(message)
            attempts[company] = {"status": "失败；保留上次完整快照",
                                 "checked": TODAY(), "error": str(exc)[:320]}
            print("FAIL:", message)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "last_errors.json").write_text(
        json.dumps({"date": TODAY(), "errors": errors}, ensure_ascii=False, indent=2), encoding="utf-8")
    data["jobs"] = list(all_jobs.values())
    data["snapshot"] = TODAY()
    dbpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if not successes:
        raise SystemExit("No sources completed; retain previous published site")
    if errors:
        print("WARNING: partial failures, no delisting inferred.")

if __name__ == "__main__":
    main()
