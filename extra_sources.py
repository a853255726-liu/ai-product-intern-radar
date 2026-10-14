"""Additional official recruitment feeds. Only publish fully reconciled source scopes.

The feeds return mixed cities or recruitment types; only narrow in normalize_extra.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
import re
from urllib.parse import urlencode


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
    def xiaomi(session):
        # The job board's public jobs.js calls this official searchJobPage API.
        # type=3 is its "实习" tab, cityZhNames restricts Beijing.
        def one(page):
            query = urlencode({"keyword": "", "cityZhNames": "北京",
                               "pageSize": 100, "pageNum": page, "type": 3})
            data = fetch_json(session, "GET",
                "https://hr.xiaomi.com/website/api/agent/searchJobPage?" + query,
                None, "https://hr.xiaomi.com/website/opportunities.html")
            if data.get("code") != 0 or not isinstance(data.get("data"), dict):
                raise ValueError("Xiaomi official job API returned unsuccessful status")
            return data
        records, audit = paginate("xiaomi-beijing-internship", one,
            lambda x: (x["data"].get("list"), x["data"].get("total"), "jobPostId"))
        audit.update(capture="小米官网 searchJobPage 公开接口",
            scope="type=3实习，北京，所有关键词；不包括社招或其他项目",
            caveat="官方接口职位是岗位线索，不等于确认剩余招聘名额；部分含2027届或专项限制")
        return records, audit

    return {"快手": kuaishou, "米哈游": mihoyo, "小米": xiaomi}


def normalize_extra(company, rows, today):
    jobs = []
    for x in rows:
        if company == "小米":
            title = str(x.get("title") or "").strip()
            cities = "/".join(str(z) for z in x.get("cityZhNames", []) if z)
            summary = str(x.get("description") or "").strip()
            req = str(x.get("requirement") or "").strip()
            if "北京" not in cities or not x.get("jobPostId") or x.get("type") != 3:
                continue
            if not re.search(r"产品|用户研究|体验运营", title):
                continue
            if re.search(r"工程师|算法研究员|生产|售后|培训生", title):
                continue
            if not re.search(r"AI|大模型|Agent|智能体|小爱|TTS|语音|AIGC|自动驾驶|数据产品|推荐|搜索|人工智能", title+" "+summary, re.I):
                continue
            # "AI-assisted writing" alone is a lower-signal adjacent role,
            # but still a product internship lead for manual review.
            job_id = str(x["jobPostId"])
            code = str(x.get("larkJobCode") or "")
            link = str(x.get("url") or "")
            if not link.startswith("https://xiaomi.jobs.f.mioffice.cn/"):
                continue
            posted = str(x.get("publishTime") or "")[:10]
            track = ("AI Agent" if re.search(r"Agent|智能体", title+" "+summary, re.I)
                 else "AI数据/评测" if "用户研究" in title or "体验运营" in title
                 else "AI平台" if re.search(r"数据产品|平台", title)
                 else "AI应用/体验")
            fit = "优先投递" if re.search(r"AI|Agent|智能体|大模型|小爱|TTS|语音", title, re.I) else "可以尝试"
            if re.search(r"每周.{0,12}(?:至少|需|可到岗|稳定)?\s*5\s*天|每周.{0,12}5天|全职在岗", req):
                days = "≥5天"
            elif re.search(r"每周.{0,12}(?:至少|需|可到岗|稳定)?\s*4\s*天|每周.{0,12}4\s*[-～至]\s*5天|≥\s*4\s*天|实习≥\s*4\s*天", req):
                days = "≥4天"
            else:
                days = "未注明"
            duration = "≥6个月" if re.search(r"至少.{0,4}6个月|不少于6个月|实习6个月", req) else "≥3个月" if re.search(r"至少.{0,4}3个月|不少于3个月|实习期≥3", req) else "未注明"
            graduation = "2027届条件（需核实）" if re.search(r"(?:2027|27)届", title+" "+req) else "在校生或未明确"
            jobs.append({
                "id": "xiaomi-"+job_id, "company": "小米", "title": title,
                "link": link, "posted": posted, "date_type": "发布日期",
                "group": "大厂", "track": track, "fit": fit,
                "days": days, "duration": duration,
                "verify": "官网API（含JD，详情待复核）",
                "status": "小米官网实习类别有记录；具体名额待HR确认",
                "team": str(x.get("levelOneDeptName") or "未披露"),
                "summary": summary[:1800], "requirements": req[:1600],
                "note": "官方公开招聘接口北京实习，类型=3；毕业届次条件与可到岗天数以JD为准。",
                "source": "小米招聘官网公开 searchJobPage API",
                "graduation": graduation, "checked": today(),
                "source_job_code": code,
                "source_post_id": job_id
            })
            continue
        if company == "快手":
            if x.get("positionNatureCode") != "intern" or x.get("positionStatusCode") != "Release":
                continue
            title = str(x.get("name") or "").strip()
            # Retention projects are eligible candidates unless the JD explicitly
            # restricts applications to graduating students.
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
            # Keep general/special internship projects as lower-priority leads.
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
