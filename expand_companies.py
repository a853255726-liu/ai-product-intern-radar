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
    "商汤科技": "https://hr-jobs.sensetime.com/edu/m/",
    "地平线机器人": "https://horizon-campus.hotjob.cn/",
    "蚂蚁集团": "https://talent.antgroup.com/campus/home",
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
    writer.writerow(["企业", "来源", "覆盖状态", "检查结果", "网址", "候选数量"])
    for name, info in coverage.items():
        writer.writerow([name, info.get("source", ""), info.get("level", ""),
                         info.get("coverage", ""), info.get("website", ""),
                         sum(row["company"] == name for row in eligible_jobs(db.get("jobs", [])))])
with (ROOT / "jobs.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    cols = ["company","title","group","track","fit","days","duration","posted",
            "date_type","verify","checked","team","summary","requirements",
            "note","link","official_detail_url","source_url","link_kind","link_label","id"]
    writer = csv.DictWriter(stream, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(eligible_jobs(db.get("jobs", [])))
print(len(coverage), "companies;", len(eligible_jobs(db.get("jobs", []))), "eligible internship leads")
