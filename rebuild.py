"""Generate a standalone dashboard from reviewed JSON data and HTML template."""
from pathlib import Path
import json
from copy import deepcopy
from daily_scope import daily_jobs

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "jobs.json").read_text(encoding="utf-8"))
jobs = data.get("jobs", [])
assert jobs and all(all(key in row for key in ("id", "company", "title", "link")) for row in jobs)
assert len(jobs) == len({str(row["id"]) for row in jobs}), "Duplicate job IDs"
master_count = len(jobs)
publication = deepcopy(data)
publication['jobs'] = daily_jobs(jobs)
publication['published_scope'] = '北京 AI 产品相关日常实习（有招聘项目证据），其他项目及属性不明的历史记录不会展示'
publication['excluded_from_publication'] = master_count - len(publication['jobs'])
publication['version'] = 'V3.2 日常实习专版'
payload = json.dumps(publication, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = (ROOT / "template.html").read_text(encoding="utf-8")
assert "__DATA__" in html, "Missing source data placeholder"
(ROOT / "index.html").write_text(html.replace("__DATA__", payload), encoding="utf-8")
print("Rebuilt dashboard:", len(publication["jobs"]), "daily jobs from", master_count, "total archive jobs")
