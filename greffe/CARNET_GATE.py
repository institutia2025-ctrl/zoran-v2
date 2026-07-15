#!/usr/bin/env python3
# GUARD_IDS: CARNET_GATE_EXECUTABLE_V1, DEPOT_EXECUTION_GUARD_V1, FILE_GUARDS_REQUIRED_BLOCKING, SESSION_B_REPORTS_ONLY_V1
"""Fail-closed pre-write gate for the isolated Session B audit checkout."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
TICKET_PATH = ROOT / "greffe" / "WORK_TICKET.json"
GOVERNANCE_PATHS = {"greffe/CARNET_GATE.py", "greffe/WORK_TICKET.json"}
REQUIRED_GUARDS = {
    "CARNET_GATE_EXECUTABLE_V1",
    "DEPOT_EXECUTION_GUARD_V1",
    "FILE_GUARDS_REQUIRED_BLOCKING",
    "SESSION_B_REPORTS_ONLY_V1",
}


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8",
        errors="replace", capture_output=True, check=False,
    )


def load_ticket() -> dict[str, Any]:
    if not TICKET_PATH.is_file():
        return {}
    return json.loads(TICKET_PATH.read_text(encoding="utf-8"))


def check(name: str, ok: bool, detail: Any) -> dict[str, Any]:
    return {"id": name, "ok": bool(ok), "detail": detail}


def main() -> int:
    ticket = load_ticket()
    status = run_git("status", "--porcelain=v1", "--untracked-files=all")
    dirty = []
    for raw in status.stdout.splitlines():
        path = raw[3:].replace("\\", "/") if len(raw) >= 4 else raw
        dirty.append({"status": raw[:2], "path": path})
    dirty_paths = {row["path"] for row in dirty}
    head = run_git("rev-parse", "HEAD").stdout.strip()
    branch = run_git("branch", "--show-current").stdout.strip()
    tag = run_git("rev-parse", "certified/v2-integration-00-07-hardening^{}").stdout.strip()
    baseline = str(ticket.get("baseline_sha") or "")
    ancestor = run_git("merge-base", "--is-ancestor", baseline, "HEAD")
    guards = set(ticket.get("guard_ids") or [])
    allowed_branches = set(ticket.get("allowed_branches") or [])
    report_paths = set(ticket.get("allowed_write_paths") or [])
    def allowed_dirty(path: str) -> bool:
        return path in GOVERNANCE_PATHS or any(
            path == prefix.rstrip("/") or path.startswith(prefix)
            for prefix in report_paths
        )
    checks = [
        check("C0_WORK_TICKET_PRESENT", bool(ticket), str(TICKET_PATH)),
        check("C1_MISSION_BOUND", ticket.get("mission_id") == "TX_ZORAN_CODEX_SESSION_B_INDEPENDENT_CERTIFIER_V1", ticket.get("mission_id")),
        check("C2_GO_FRED", ticket.get("go_fred") is True, ticket.get("go_fred")),
        check("C3_DOUBLE_REGARD", bool(ticket.get("regard_A") and ticket.get("regard_B")), "regard_A + regard_B"),
        check("C4_GUARDS", REQUIRED_GUARDS.issubset(guards), sorted(guards)),
        check("C5_BASELINE_ANCESTOR", bool(baseline) and ancestor.returncode == 0, {"audit_sha": baseline, "report_head": head}),
        check("C6_CERTIFIED_TAG", tag == baseline, tag),
        check("C7_BRANCH", branch in allowed_branches, branch),
        check("C8_REPORTS_ONLY_DIRTY", status.returncode == 0 and all(allowed_dirty(path) for path in dirty_paths), dirty),
        check("C9_REPORTS_ONLY_SCOPE", report_paths == {"audits/codex_session_b/", "SYNC/CODEX_SESSION_B_CERTIFICATION_REPORT.md", "SYNC/mailbox/"}, sorted(report_paths)),
        check("C10_NO_PRODUCT_MUTATION", ticket.get("product_mutation") is False, ticket.get("product_mutation")),
        check("C11_ROLLBACK", bool(ticket.get("rollback")), ticket.get("rollback")),
    ]
    ok = all(item["ok"] for item in checks)
    payload = {
        "ok": ok,
        "status": "PASS" if ok else "BLOCKED",
        "policy": "STOP_ECRITURE" if not ok else "REPORTS_AND_EVIDENCE_ONLY",
        "mission_id": ticket.get("mission_id"),
        "repository": str(ROOT),
        "head_sha": head,
        "branch": branch,
        "ticket_sha256": hashlib.sha256(TICKET_PATH.read_bytes()).hexdigest() if TICKET_PATH.is_file() else None,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
