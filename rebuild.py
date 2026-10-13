"""Generate a standalone dashboard from reviewed JSON data and HTML template."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "jobs.json").read_text(encoding="utf-8"))
jobs = data.get("jobs", [])
assert jobs and all(all(key in row for key in ("id", "company", "title", "link")) for row in jobs)
assert len(jobs) == len({str(row["id"]) for row in jobs}), "Duplicate job IDs"
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\/")
html = (ROOT / "template.html").read_text(encoding="utf-8")
assert "__DATA__" in html, "Missing source data placeholder"
(ROOT / "index.html").write_text(html.replace("__DATA__", payload), encoding="utf-8")
print("Rebuilt dashboard with", len(jobs), "candidate jobs")
