"""Write a small machine-readable CI health report from GitHub Actions.

This is CI evidence, not a claim that any employer has current open positions.
The report includes the tested source commit SHA so stale evidence is obvious.
"""
from __future__ import annotations
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "ci_health.json"


def summarize_log(log: str, max_lines=12):
    lines = [x.strip() for x in log.splitlines()]
    interesting = []
    signature = re.compile(
        r"^(?:FAIL:|ERROR:|FAILED\b|Ran \d+ tests?|OK\b|"
        r"Traceback \(most recent call last\):|"
        r"ImportError:|ModuleNotFoundError:|SyntaxError:|AssertionError:)",
        re.I,
    )
    for index, line in enumerate(lines):
        if signature.search(line):
            interesting.append(line[:300])
            if line.startswith(("ERROR:", "FAIL:")):
                interesting.extend(x[:300] for x in lines[index + 1:index + 4]
                                   if x.strip())
    return list(dict.fromkeys(interesting))[-max_lines:]


def build_report(outcome, sha, log="", run_id="", checked_at=None):
    outcome = str(outcome or "not_run")
    return {
        "kind": "offline_python_regression",
        "source_sha": str(sha or ""),
        "github_run_id": str(run_id or ""),
        "checked_at_utc": checked_at or datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "status": ("passed" if outcome == "success"
                   else "not_run" if outcome in ("skipped", "not_run", "")
                   else "failed"),
        "github_step_outcome": outcome,
        "log_highlights": summarize_log(log),
        "disclaimer": ("Only Python compilation and offline regression tests; "
                       "does not prove website scraping or Pages deployment."),
    }


def main():
    logpath = ROOT / "source-tests.log"
    log = logpath.read_text(encoding="utf-8", errors="replace") if logpath.exists() else ""
    report = build_report(
        os.environ.get("CI_TEST_OUTCOME"),
        os.environ.get("GITHUB_SHA"),
        log,
        os.environ.get("GITHUB_RUN_ID"),
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("CI health:", report["status"], "source", report["source_sha"])


if __name__ == "__main__":
    main()
