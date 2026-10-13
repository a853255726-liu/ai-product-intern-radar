"""Additional official recruitment feeds. Only publish fully reconciled source scopes.

The feeds return mixed cities or recruitment types; only narrow in normalize_extra.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
import re


def make_sources(fetch_json, paginate, today):
    def kuaishou(session):
        url = "https://campus.kuaishou.cn/recruit/campus/e/api/v1/open/positions/simple"
        def one(page):
            data = fetch_json(
                session, "POST", url,
                {"pageNum": page, "pageIndex": page, "pageSize": 50,
                 "positionNatureCode": "intern"},
                "https://campus.kuaishou.cn/recruit/campus/e/"
            )
            if data.get("code") != 0:
                raise ValueError("Kuaishou API response not successful")
            return data
        rows, audit = paginate(
            "kuaishou-intern", one,
            lambda x: ((x.get("result") or {}).get("list"),
                       (x.get("result") or {}).get("total"),
                       "id")
        )
        audit.update(
            capture="官方校园招聘公开职位 API",
            scope="positionNatureCode=intern，实习类别全部城市",
            caveat="分页完整性仅适用于此接口；Release 不等于 HR 确认尚有 HC"
        )
        return rows, audit

    def mihoyo(session):
        url = "https://ats.openout.mihoyo.com/ats-portal/v1/job/list"
        def one(page):
            data = fetch_json(
                session, "POST", url,
                {"pageNo": page, "pageSize": 50,
                 "channelDetailIds": [1], "hireType": 1},
                "https://jobs.mihoyo.com/"
            )
            if not data.get("success", True):
                raise ValueError("miHoYo API response not successful")
            return data
        rows, audit = paginate(
            "mihoyo-campus", one,
            lambda x: ((x.get("data") or {}).get("list"),
                       (x.get("data") or {}).get("total"),
                       "id")
        )
        audit.update(
            capture="官方 ATS 公开职位 API",
            scope="channelDetailIds=1、hireType=1；混合校招正式与实习",
            caveat="岗位入库仅接受 jobNatureId=3 实习；此渠道之外未核查"
        )
        return rows, audit
    return {"快手": kuaishou, "米哈游": mihoyo}


def normalize_extra(company, rows, today):
    jobs = []
    for x in rows:
        if company == "快手":
            if x.get("positionNatureCode") != "intern" or x.get("positionStatusCode") != "Release":
                continue
            title = str(x.get("name") or "").strip()
            cities = "/".join(str(z.get("name") or "") for z in (x.get("workLocationDicts") or []) if isinstance(z, dict))
            summary = str(x.get("description") or "")
            req = str(x.get("positionDemand") or "")
            if "北京" not in cities or not re.search(r"产品|用户研究", title):
                continue
            if re.search(r"工程师|算法工程|开发", title):
                continue
            # Strong AI signal, not generic "AI tools" or a passing mention of industry trends.
            strong = bool(re.search(r"AI|Agent|大模型|智能体", title, re.I))
            strong = strong or bool(re.search(r"AI\s*创新|AI\s*类平台|AI\s*产品建设|AI\s*产品能力", summary, re.I))
            if not strong:
                continue
            job_id = str(x.get("id") or "")
            link = "https://campus.kuaishou.cn/recruit/campus/e/#/campus/jobs?positionId=" + job_id
            posted = str(x.get("releaseTime") or "")[:10]
            track = "AI Agent" if re.search(r"Agent|智能体", title, re.I) else "AI平台" if "平台" in title else "AI工具落地"
            fit = "优先投递" if track in ("AI Agent", "AI平台") else "优先关注"
            team = "快手校园招聘 · 留用实习项目（具体业务团队未披露）"
            group = "大厂"
            source = "快手官方校园招聘 API（实习类别）"
            ident = "kuaishou-" + job_id
            status = "官网接口 Release；具体招聘名额待确认"
        elif company == "米哈游":
            if x.get("jobNatureId") != 3:
                continue
            title = str(x.get("title") or "").strip()
            cities = "/".join(str(z.get("addressDetail") or "") for z in (x.get("addressDetailList") or []) if isinstance(z, dict))
            if "北京" not in cities or not re.search(r"产品经理|产品实习|用户研究", title):
                continue
            # Do not confuse AI algorithm / annotation / trainer roles with product management.
            if re.search(r"工程师|算法|标注|训练师|研究员", title):
                continue
            job_id = str(x.get("id") or "")
            link = "https://jobs.mihoyo.com/#/campus/position/" + job_id
            posted = ""
            track = "AI 产品/策略"
            fit = "可以尝试"
            summary = "官网岗位列表证实存在；具体 JD 尚未核验。"
            req = "请查看官网详情和实习到岗要求。"
            team = str(x.get("projectName") or "校园实习")
            group = "中型/行业科技"
            source = "米哈游官网公开 ATS"
            ident = "mihoyo-" + job_id
            status = "官网接口有记录；JD 待核验"
        else:
            continue
        if not job_id:
            continue
        jobs.append({
            "id": ident, "company": company, "title": title, "link": link,
            "posted": posted, "date_type": "发布日期" if posted else "未提供",
            "group": group, "track": track, "fit": fit,
            "days": "未注明", "duration": "未注明",
            "verify": "官网API（含JD，详情待复核）" if company == "快手" else "官网API（详情待复核）",
            "status": status, "team": team,
            "summary": summary[:1600], "requirements": req[:1200],
            "note": "官网列示岗位不等于剩余招聘名额；请确认届次、到岗要求和投递状态",
            "source": source, "graduation": "未核实", "checked": today()
        })
    return jobs
