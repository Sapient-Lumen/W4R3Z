#!/usr/bin/env python3
"""Build rev0834 external rights-evidence candidate ledger.

This is intentionally *not* a license grant.  It records a narrow online lead
for the single local README phrase that references a LICENSE file not shipped
beside it, so a human owner can pin the exact upstream commit before deciding
whether to include a third-party license notice in a canonical release.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "RIGHTS" / "external_license_evidence_candidates_rev0834.json"
MD_OUT = ROOT / "RIGHTS" / "external_license_evidence_candidates_rev0834.md"
LOCAL_README = "sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md"
LOCAL_MISSING_LICENSE = "sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE"
PHRASE = "This project is licensed under the Apache License, Version 2.0 for new contributions, with existing code under MIT - see the [LICENSE](LICENSE) file for details."


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_local_context() -> dict[str, Any]:
    path = ROOT / LOCAL_README
    text = path.read_text(encoding="utf-8")
    line_no = None
    for i, line in enumerate(text.splitlines(), start=1):
        if PHRASE in line:
            line_no = i
            break
    return {
        "path": LOCAL_README,
        "exists": path.is_file(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "license_phrase_found": line_no is not None,
        "license_phrase_line": line_no,
        "referenced_license_path": LOCAL_MISSING_LICENSE,
        "referenced_license_file_shipped": (ROOT / LOCAL_MISSING_LICENSE).is_file(),
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    local = read_local_context()
    candidate = {
        "candidate_id": "pact-mcp-servers-readme-missing-license-candidate",
        "status": "candidate_unpinned_external_evidence_do_not_treat_as_grant",
        "local_evidence": local,
        "external_research_observed_at": "2026-06-09",
        "external_repository": {
            "name": "modelcontextprotocol/servers",
            "repository_url": "https://github.com/modelcontextprotocol/servers",
            "license_file_url": "https://github.com/modelcontextprotocol/servers/blob/main/LICENSE",
            "readme_license_section_url": "https://github.com/modelcontextprotocol/servers#license",
            "commit_pinned": False,
        },
        "external_observation_summary": [
            "The current GitHub repository README contains the same Apache-2.0/MIT transition phrase as the shipped servers_README.md snapshot.",
            "The current GitHub repository has a LICENSE file describing a transition from MIT to Apache-2.0, with documentation excluding specifications under CC-BY-4.0.",
            "Because this archive does not ship the referenced LICENSE file or an upstream commit identifier for the README snapshot, this observation is a candidate lead only.",
        ],
        "required_owner_actions": [
            "Identify the exact upstream commit or release used to produce sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md.",
            "Retrieve the LICENSE file from that exact commit or release, not from a mutable branch head.",
            "Add the verified third-party license/notice material to a canonical rights surface only after matching the source snapshot.",
            "Keep PACT component license conclusions as NOASSERTION until that evidence is pinned and reviewed.",
        ],
    }
    return {
        "version": 1,
        "revision_context": "rev0834-session-patch-over-rev0833-over-rev0826",
        "status": "external_candidate_recorded_no_license_conclusion_changed",
        "does_not_grant_license": True,
        "does_not_change_spdx_conclusions": True,
        "does_not_change_ro_crate_license": True,
        "candidate_count": 1,
        "candidates": [candidate],
        "local_phrase_sha256": sha256_text(PHRASE),
        "builder": "scripts/build_external_license_evidence_candidates_rev0834.py",
        "validator": "scripts/validate_external_license_evidence_candidates_rev0834.py",
    }


def render_markdown(data: dict[str, Any]) -> str:
    c = data["candidates"][0]
    local = c["local_evidence"]
    lines = [
        "# External license evidence candidates rev0834",
        "",
        "This file records an online evidence lead for human rights review. It does **not** grant a license, does **not** alter SPDX conclusions, and does **not** change the RO-Crate root license from `NOASSERTION`.",
        "",
        f"- Status: `{data['status']}`",
        f"- Candidate count: **{data['candidate_count']}**",
        "",
        f"## `{c['candidate_id']}`",
        "",
        f"- Candidate status: `{c['status']}`",
        f"- Local README: `{local['path']}`",
        f"- Local phrase found: `{str(local['license_phrase_found']).lower()}` at line `{local['license_phrase_line']}`",
        f"- Referenced local license file shipped: `{str(local['referenced_license_file_shipped']).lower()}`",
        f"- Referenced local license path: `{local['referenced_license_path']}`",
        f"- External repository: `{c['external_repository']['name']}`",
        f"- External commit pinned: `{str(c['external_repository']['commit_pinned']).lower()}`",
        "",
        "## External observation summary",
        "",
    ]
    for item in c["external_observation_summary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Required owner actions", ""])
    for item in c["required_owner_actions"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print("external-license-evidence-candidates-build: OK (1 candidate, conclusions unchanged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
