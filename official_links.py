"""Conservative direct-to-official-JD link policy.

A valid company domain or home/list page is NOT a specific job detail page.
Never generate an official job URL for a third-party-only record without a
grounded employer-side job ID. The URL route is checked structurally here;
a structural match does not prove that the position is currently open.
"""
from __future__ import annotations
import re
from urllib.parse import urlsplit, parse_qs

UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F-]{20,40}"
POSITIVE = r"[1-9]\d*"

def _safe_url(value):
    if not isinstance(value, str) or not value.startswith("https://"):
        return False
    try:
        u = urlsplit(value)
        return bool(u.hostname and not u.username and not u.password)
    except ValueError:
        return False

def _specific_official(url):
    """Official *job-detail routes* only, never generic home/list pages."""
    if not _safe_url(url):
        return False
    u = urlsplit(url)
    h, p, f = u.hostname.lower(), u.path, u.fragment
    q = parse_qs(u.query)
    if h == "zhaopin.meituan.com":
        return p == "/web/position/detail" and any(re.fullmatch(POSITIVE, v) for v in q.get("jobUnionId", []))
    if h == "job.xiaohongshu.com":
        return re.fullmatch(r"/(?:campus|intern|social)/position/"+POSITIVE+r"/?",p) is not None
    if h == "join.qq.com":
        return p == "/post_detail.html" and any(re.fullmatch(POSITIVE, v) for v in q.get("postid", []))
    if h == "talent.baidu.com":
        return re.fullmatch(r"/jobs/detail/INTERN/"+UUID+r"/?",p) is not None
    if h == "campus.jd.com":
        return f.startswith("/details?") and any(re.fullmatch(POSITIVE,v) for v in parse_qs(f.partition("?")[2]).get("id",[]))
    if h == "campus.kuaishou.cn":
        return f.startswith("/campus/jobs?") and any(re.fullmatch(POSITIVE,v) for v in parse_qs(f.partition("?")[2]).get("positionId",[]))
    if h == "jobs.mihoyo.com":
        return re.fullmatch(r"/campus/position/"+POSITIVE+r"/?",f) is not None
    if h == "hr.meitu.com":
        return re.fullmatch(r"/(?:en/)?jobIntern/"+UUID+r"/?",p) is not None
    if h in {"careers.iqiyi.com", "iq.jobs.feishu.cn"}:
        return re.fullmatch(r"/(?:intern|index)/position/"+POSITIVE+r"/detail/?",p) is not None
    if h == "xiaomi.jobs.f.mioffice.cn":
        return re.fullmatch(r"/(?:internship|topintern)/position/"+POSITIVE+r"/detail/?",p) is not None
    if h == "app.mokahr.com":
        # Handle each employer's Moka path before rejecting other Moka pages.
        if p in ("/campus-recruitment/moonshot/148507",
                 "/campus-recruitment/step/94905"):
            return re.fullmatch(r"/job/[0-9a-f]{8}-[0-9a-f-]{27,36}", f) is not None
        return False
    if h == "campus-talent.alibaba.com":
        return re.fullmatch(r"/campus/position/" + POSITIVE + r"/?", p) is not None
    if h == "jobs.bilibili.com":
        return re.fullmatch(r"/campus/positions/" + POSITIVE + r"/?", p) is not None
    if h == "jobs.bytedance.com":
        return re.fullmatch(r"/(?:campus|experienced)/position/"+POSITIVE+r"/detail/?",p) is not None
    if h == "hr-jobs.sensetime.com":
        return re.fullmatch(r"/edu/m/position/"+POSITIVE+r"/detail/?",p) is not None
    if h.endswith(".jobs.feishu.cn") and h != "jobs.feishu.cn":
        return re.fullmatch(r"/(?:[^/]+/){1,3}position/"+POSITIVE+r"/detail/?",p) is not None
    return False

def _official_listing(url):
    if not _safe_url(url):
        return False
    host = urlsplit(url).hostname.lower()
    return host in {"talent.baidu.com","campus.jd.com","join.qq.com","ke.zhiye.com",
        "careers.iqiyi.com","job.xiaohongshu.com","jobs.bytedance.com",
        "zhaopin.meituan.com","campus.kuaishou.cn","app.mokahr.com",
        "campus-talent.alibaba.com","jobs.bilibili.com","hr-jobs.sensetime.com"} or host.endswith(".jobs.feishu.cn")

def classify_link(url):
    if _specific_official(url):
        return "official_detail"
    # Broken detail endpoints are not valid official *listing* URLs.
    if re.fullmatch(r"https://join\.qq\.com/post_detail\.html\?postid=-\d+", str(url)):
        return "invalid"
    if not _safe_url(url):
        return "invalid"
    if _official_listing(url):
        return "official_list"
    return "external_source"

def enrich_job(job):
    """Idempotent: retain independent original evidence URL and official URL."""
    obj = dict(job)
    source = obj.get("source_url") or obj.get("link") or ""
    current = obj.get("official_detail_url") or obj.get("link") or ""
    # Migrate a legacy JD hash route. This format was proven to show a 404.
    jd = re.fullmatch(r"https://campus\.jd\.com/#/job/detail\?publishId=("+POSITIVE+r")", current)
    if jd:
        old_route = current
        current = "https://campus.jd.com/#/details?id="+jd.group(1)
        obj["legacy_link_url"] = old_route
        # Never expose the proven-404 legacy URL as the secondary source link.
        if source == old_route:
            source = current
    if classify_link(current) == "official_detail":
        obj["official_detail_url"] = current
        obj["link"] = current
        obj["link_kind"] = "official_detail"
        obj["link_label"] = "官网职位详情"
        # A successful route-format validation is NOT an uptime/HC verification.
        obj["link_check"] = "职位专属URL；实时可访问性及HC未逐条确认"
    else:
        obj.pop("official_detail_url", None)
        obj["link_kind"] = classify_link(source)
        if obj["link_kind"] == "official_list":
            obj["link_label"] = "仅官网招聘列表"
        elif obj["link_kind"] == "external_source":
            obj["link_label"] = "第三方职位线索"
        else:
            obj["link_label"] = "暂无有效链接"
        obj["link_check"] = "未取得可核实的对应官网职位详情ID"
        obj["link"] = source if _safe_url(source) else ""
    obj["source_url"] = source if _safe_url(source) else ""
    return obj

def enrich_jobs(jobs):
    return [enrich_job(x) for x in jobs]
