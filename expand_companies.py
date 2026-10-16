"""Keep the company watchlist and CSV exports in sync with the JSON database."""
import csv
import json
from pathlib import Path
from daily_scope import eligible_jobs
from official_links import enrich_jobs

ROOT = Path(__file__).resolve().parent
dbpath = ROOT / "jobs.json"
db = json.loads(dbpath.read_text(encoding="utf-8"))
# Every build updates link metadata and repairs recognized legacy routes.
db["jobs"] = enrich_jobs(db.get("jobs", []))
extra = {
 "携程集团":"https://www.ctrip.com", "网易":"https://hr.163.com",
 "爱奇艺":"https://careers.iqiyi.com", "金山办公":"https://www.wps.cn",
 "小米":"https://www.mi.com", "蚂蚁集团":"https://talent.antgroup.com",
 "美图":"https://www.meitu.com", "昆仑万维":"https://www.kunlun.com",
 "百川智能":"https://www.baichuan-ai.com", "零一万物":"https://www.lingyiwanwu.com",
 "硅基流动":"https://siliconflow.cn", "DeepSeek":"https://www.deepseek.com",
 "合合信息":"https://www.intsig.com", "出门问问":"https://www.mobvoi.com",
 "猎户星空":"https://www.orionstar.com", "云知声":"https://www.unisound.com",
 "金蝶":"https://www.kingdee.com", "用友":"https://www.yonyou.com",
 "明略科技":"https://www.mininglamp.com", "值得买":"https://www.smzdm.com",
 "联想":"https://www.lenovo.com", "神州数码":"https://www.digitalchina.com",
 "万兴科技":"https://www.wondershare.cn"
}
coverage = db.setdefault("company_coverage", {})
for name, website in extra.items():
    coverage.setdefault(name, {
        "source": "企业网站（招聘接口尚未定位）", "level": "todo",
        "coverage": "尚未核验北京AI产品实习岗位，也未完成官网招聘子系统检索",
        "website": website
    })
# Official entry points: the website column should go to recruitment, not
# the corporate homepage. These are watchlist entries until a tested collector
# has proven complete pagination and stable official position IDs.
official_directories = {
    "爱奇艺": "https://iq.jobs.feishu.cn/intern/m/",
    "阿里巴巴": "https://campus-talent.alibaba.com/campus/position?batchId=100000560002&lang=zh",
    "月之暗面": "https://careers.kimi.com/campus",
    "字节跳动": "https://jobs.bytedance.com/campus/position",
    "阶跃星辰": "https://app.mokahr.com/campus-recruitment/step/94905#/jobs",
    "B站": "https://jobs.bilibili.com/campus/positions?type=0&page=1",
    "智平方": "https://ai2robotics.jobs.feishu.cn/",
    "无问芯穹": "https://infinigence.jobs.feishu.cn/",
    "星动纪元": "https://k0fqxcszc9.jobs.feishu.cn/",
    "清程极智": "https://chitu-ai.jobs.feishu.cn/",

    "商汤科技": "https://hr-jobs.sensetime.com/edu/m/",
    "地平线机器人": "https://horizon-campus.hotjob.cn/",
    "蚂蚁集团": "https://talent.antgroup.com/campus/home",
    "华为": "https://career.huawei.com/reccampportal/portal5/campus-recruitment.html",
    "OPPO": "https://career.oppo.com/official/oppo/recruitment/post?recruitType=OFFEN-RECRUITMENT",
    "汽车之家": "https://talent.autohome.com.cn/campus-recruit-list.html",
    "好未来": "https://job.tal.com/campus/positions",
    "搜狐": "https://campus.sohu.com/",
}
for name, url in official_directories.items():
    info = coverage.setdefault(name, {
        "source": "招聘官网目录（尚未自动采集）",
        "level": "todo",
        "coverage": "官方招聘入口已定位，尚未完成稳定职位分页核验",
    })
    if not ((name == "月之暗面" and str(info.get("level")) == "complete_public_html")
            or (name == "字节跳动" and "字节跳动官方" in str(info.get("source")))
            or (name == "B站" and str(info.get("source", "")).startswith("B站校园招聘官网"))):
        info["website"] = url


# Ant Group's official campus homepage explicitly lists 日常实习 for all
# current students, without a graduation-year limit. Its job list still has
# no verified paginated collector: do not mark the channel automated or live.
ant = coverage.get("蚂蚁集团")
if ant and ant.get("level") not in ("complete_api", "complete_public_html"):
    ant["source"] = "蚂蚁集团官方日常实习入口（职位接口待核验）"
    ant["level"] = "partial"
    ant["coverage"] = (
        "2026-10-15 官方校园招聘首页确认日常实习面向全体在校生、"
        "毕业时间不限；尚未取得可稳定分页的官方职位ID，"
        "不能宣称北京AI产品实习岗位已自动采集。"
    )



# Newly confirmed employer-operated recruiting directories. Discovery of an
# official board does not imply a successful full pagination scan.
sensetime = coverage.setdefault("商汤科技", {})
if sensetime.get("level", "todo") in ("todo", "partial"):
    sensetime.update({
        "source": "商汤官方校园与实习职位目录（全量采集待验收）",
        "level": "partial",
        "coverage": "2026-10-16 确认官方实习频道面向在校生，官网职位目录可按北京/实习/产品筛选；自动分页及唯一职位ID仍须以 source_attempts 实际成功为准",
        "website": "https://hr-jobs.sensetime.com/edu/m/",
    })
horizon = coverage.setdefault("地平线机器人", {})
if horizon.get("level", "todo") in ("todo", "partial"):
    horizon.update({
        "source": "地平线官方校园招聘入口（日常实习职位待核验）",
        "level": "partial",
        "coverage": "2026-10-16 已确认官方校园招聘入口及日常实习计划，北京为招聘城市之一；未取得完整可稳定分页的北京AI产品实习记录",
        "website": "https://horizon-campus.hotjob.cn/",
    })



# New official employer directories are discoverable, but a source is not
# "complete" until the current job-ID/page audit passes in cloud execution.
new_ai_watch = {
    "智平方": (
        "具身智能软件平台；官网已列出北京日常产品实习（每周4–5天，≥3个月）；"
        "已配置公开职位采集，待完成首次完整分页与唯一ID云端验收",
        "https://ai2robotics.jobs.feishu.cn/",
    ),
    "无问芯穹": (
        "官方职位目录可访问，包含北京及产品职能；当前可见产品岗以全职为主；"
        "已配置采集，仅明确北京实习职位入库，首次全量验收待完成",
        "https://infinigence.jobs.feishu.cn/",
    ),
    "星动纪元": (
        "官方招聘目录可访问，北京机器人/技术产品方向以全职为主；"
        "已配置采集，仅明确北京实习职位入库，首次全量验收待完成",
        "https://k0fqxcszc9.jobs.feishu.cn/",
    ),
    "清程极智": (
        "官网确认在北京招聘，并有飞书雇主招聘主页；"
        "具体可分页职位目录和北京AI产品日常实习尚未核验，不自动采集",
        "https://chitu-ai.jobs.feishu.cn/",
    ),
}
for name, (description, website) in new_ai_watch.items():
    info = coverage.setdefault(name, {})
    if info.get("level") not in ("complete_api", "complete_public_html"):
        info.update({
            "source": "AI企业公开招聘官网（职位采集待核验）",
            "level": "partial",
            "coverage": "2026-10-16：" + description,
            "website": website,
        })

# First-batch company coverage: an official internship entry is not a
# confirmed paginated feed or an available Beijing AI product vacancy.
first_batch = {
    "华为": ("华为勇敢星实习生计划与官网实习生职位搜索入口已核实；页面依赖客户端渲染，尚未定位可稳定复现完整分页的官方职位接口", "https://career.huawei.com/reccampportal/portal5/campus-recruitment.html"),
    "OPPO": ("日常实习为独立公开职位列表（区别2027届寻梦项目）；已配置普通浏览器职位ID和公开记录总数校验，尚待云端首次验收；已查看的北京职位以算法类为主", "https://career.oppo.com/official/oppo/recruitment/post?recruitType=OFFEN-RECRUITMENT"),
    "汽车之家": ("已定位官方职位目录，提供实习生、北京和产品类别筛选；搜索页目前混合校招/实习，尚未验证完整分页和职位专属ID，不将普通产品运营误标为AI产品", "https://talent.autohome.com.cn/campus-recruit-list.html"),
    "好未来": ("2026-10-16 旧Moka官网已跳转到新job.tal.com招聘站；新站职位总数与招聘性质可见，但职位卡片、分页和ID采集器仍在适配，不宣称正式自动采集成功", "https://job.tal.com/campus/positions"),
    "搜狐": ("官网校园招聘明确有面向在校生的实习项目，但2027秋招FAQ只对2026/2027届开放；独立日常实习职位详情和可分页接口尚未核实", "https://campus.sohu.com/"),
}
for name, (detail, url) in first_batch.items():
    info = coverage.setdefault(name, {})
    last_attempt = (db.get("source_attempts") or {}).get(name) or {}
    last_audit = (db.get("source_audits") or {}).get(name) or {}
    if (name in ("OPPO", "好未来")
            and str(last_attempt.get("status") or "").startswith("成功")
            and last_audit.get("last_checked") == last_attempt.get("checked")
            and isinstance(last_audit.get("unique_ids"), int)):
        # A formerly pending source has now passed live, complete validation.
        # Keep OPPO 'partial' (verified listing, not direct job detail links),
        # TAL 'complete_public_html' (each official UUID JD audited).
        info.update({
            "source": last_audit.get("capture") or "已验收的招聘官网公开职位列表",
            "level": "complete_public_html" if name == "好未来" else "partial",
            "coverage": (
                f"{last_attempt['checked']} 本入口已验收 "
                f"{last_audit['unique_ids']} 个唯一职位ID；"
                f"北京AI产品候选 {last_attempt.get('eligible_candidate_count', '未提供')}；"
                f"范围：{last_audit.get('scope', '本公开招聘项目')}"
            ),
            "website": url,
        })
        continue
    if info.get("level") not in ("complete_api", "complete_public_html"):
        info.update({
            "source": "雇主官方实习入口" + ("（已配置采集器，待验收）" if name in ("OPPO", "好未来") else "（未上线采集）"),
            "level": "partial",
            "coverage": "2026-10-16：" + detail,
            "website": url,
        })

# Use the current successful audit to replace stale human-written claims
# about raw result counts. Do not overwrite a source's last good evidence
# when its latest scheduled attempt failed.
attempts = db.get("source_attempts", {})
for name, audit in db.get("source_audits", {}).items():
    attempt = attempts.get(name) or {}
    if not str(attempt.get("status", "")).startswith("成功"):
        continue
    if audit.get("last_checked") != attempt.get("checked"):
        continue
    count = audit.get("unique_ids")
    if not isinstance(count, int):
        continue
    info = coverage.setdefault(name, {
        "source": audit.get("capture", "企业招聘公开入口"),
        "level": "partial",
    })
    scope = str(audit.get("scope") or "此已核验公开查询入口")
    info["coverage"] = (
        f"{attempt['checked']} 核验本入口 {count} 个唯一职位 ID；"
        f"范围：{scope}；企业其他招聘项目仍可能存在遗漏"
    )

dbpath.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
with (ROOT / "company_coverage.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["企业", "来源", "覆盖状态", "检查结果", "网址", "候选数量",
                     "最近自动采集状态", "最近自动采集日期"])
    for name, info in coverage.items():
        latest = attempts.get(name) or {}
        # Source coverage is historical scope, while the last attempt is a
        # separate freshness signal. A past complete scan must not disguise
        # the fact that today's official source failed.
        latest_status = latest.get("status") or "无自动采集记录（可能仅登记官网入口）"
        writer.writerow([name, info.get("source", ""), info.get("level", ""),
                         info.get("coverage", ""), info.get("website", ""),
                         sum(row["company"] == name for row in eligible_jobs(db.get("jobs", []))),
                         latest_status, latest.get("checked", "")])
with (ROOT / "jobs.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    cols = ["company","title","group","track","fit","days","duration","posted",
            "date_type","verify","checked","team","summary","requirements",
            "note","link","official_detail_url","source_url","link_kind","link_label","id"]
    writer = csv.DictWriter(stream, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(eligible_jobs(db.get("jobs", [])))
print(len(coverage), "companies;", len(eligible_jobs(db.get("jobs", []))), "eligible internship leads")
