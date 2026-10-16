"""Monitor *directory accessibility* for employers without verified job feeds.

A reachable careers homepage is NOT job availability, and this monitor never
adds, removes, or marks an internship as refreshed. It only records whether
the public employer recruitment entrance still has internship information.
"""
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
import requests

ROOT = Path(__file__).resolve().parent
ENTRANCES = {
    "华为": ("https://career.huawei.com/reccampportal/portal5/campus-recruitment.html",
             {"career.huawei.com"}, "实习"),
    "汽车之家": ("https://talent.autohome.com.cn/campus_index.html",
                 {"talent.autohome.com.cn"}, "实习"),
    "搜狐": ("https://campus.sohu.com/", {"campus.sohu.com"}, "实习"),
}
MAX_HTML_BYTES = 4_000_000

def check_entrance(session, url, allowed_hosts, marker):
    resp = session.get(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; BeijingAIInternRadar/1.1)",
        "Accept": "text/html,application/xhtml+xml",
    }, timeout=12, allow_redirects=True)
    resp.raise_for_status()
    parts = urlsplit(resp.url)
    if parts.scheme != "https" or parts.hostname not in allowed_hosts:
        raise ValueError("Recruitment page redirected outside verified official host")
    if len(resp.content) > MAX_HTML_BYTES or not resp.content:
        raise ValueError("Recruitment page response is empty or unexpectedly large")
    if marker not in resp.text:
        # A client-rendered recruiting site often serves an empty HTML shell.
        # This proves reachability, not that its internship content disappeared.
        return {
            "status": "招聘官网可访问；静态HTML未提供实习文案（待浏览器复核）",
            "internship_marker_in_html": False,
            "http_status": resp.status_code, "url": resp.url,
        }
    return {"status": "招聘官网入口可访问（非岗位核验）",
            "internship_marker_in_html": True,
            "http_status": resp.status_code, "url": resp.url}

def update_directory_audits(data, session=None, today=None):
    today = today or datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
    attempts = data.setdefault("directory_attempts", {})
    own_session = session is None
    session = session or requests.Session()
    try:
        for name, (url, hosts, marker) in ENTRANCES.items():
            try:
                result = check_entrance(session, url, hosts, marker)
                result["checked"] = today
                attempts[name] = result
                print("DIRECTORY OK:", name, url)
            except Exception as exc:
                # Failure isn't zero openings. Keep the employer source and
                # any previous job snapshot entirely unchanged.
                attempts[name] = {
                    "status": "公开招聘入口验证失败；岗位状态未知",
                    "checked": today, "url": url,
                    "error": f"{type(exc).__name__}: {str(exc)[:220]}",
                }
                print("DIRECTORY FAIL:", name, type(exc).__name__)
    finally:
        if own_session:
            session.close()
    return data

def main():
    path = ROOT / "jobs.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    update_directory_audits(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")

if __name__ == "__main__":
    main()
