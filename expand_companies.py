"""Keep the company watchlist and CSV exports in sync with the JSON database."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
dbpath = ROOT / "jobs.json"
db = json.loads(dbpath.read_text(encoding="utf-8"))
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
dbpath.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
with (ROOT / "company_coverage.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["企业", "来源", "覆盖状态", "检查结果", "网址", "候选数量"])
    for name, info in coverage.items():
        writer.writerow([name, info.get("source", ""), info.get("level", ""),
                         info.get("coverage", ""), info.get("website", ""),
                         sum(row["company"] == name for row in db.get("jobs", []))])
with (ROOT / "jobs.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    cols = ["company","title","group","track","fit","days","duration","posted",
            "date_type","verify","checked","team","summary","requirements",
            "note","link","id"]
    writer = csv.DictWriter(stream, fieldnames=cols, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(db.get("jobs", []))
print(len(coverage), "companies;", len(db.get("jobs", [])), "jobs")
