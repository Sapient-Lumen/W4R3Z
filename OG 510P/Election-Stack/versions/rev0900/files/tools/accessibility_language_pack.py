#!/usr/bin/env python3
"""Build the accessibility/language publication no-go pack.

Privacy review is necessary but not sufficient for voter-facing publication.
This tool turns the accessibility/language policy registry into deterministic
reports that block publication until public answers are usable, language-aware,
and locally reviewed.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
RELEASE_DATE = release_date(ROOT)
REG = ROOT / "artifacts" / "registries" / "accessibility-language-publication-policy.csv"
REPORTS = ROOT / "artifacts" / "reports"

BOUNDARY = (
    "Accessibility/language publication support only; not live election evidence, not current voter instruction, "
    "not public-release authorization, not certification, not formal WCAG/ADA conformance, not a Section 203 coverage determination, "
    "not a public-records ruling, and not legal advice."
)
DECISION = "NO_GO_PUBLIC_RELEASE_ACCESSIBILITY_LANGUAGE_REVIEW_INCOMPLETE"
TOKEN_RE = re.compile(r"^(?P<typ>[A-Z]+):(?P<path>.+)$")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def tokens(cell: str) -> list[str]:
    return [raw.strip() for raw in (cell or "").split(";") if raw.strip()]


def ref_status(ref: str) -> dict[str, Any]:
    m = TOKEN_RE.match(ref)
    if not m:
        return {"ref": ref, "parseable": False, "exists": False, "path": ""}
    rel = m.group("path")
    return {"ref": ref, "parseable": True, "exists": (ROOT / rel).exists(), "path": rel}


def next_action_for(row: dict[str, str]) -> str:
    family = row.get("public_surface_family", "")
    actions = {
        "public_notice_feed": "Create accessible text and plain-language copies before treating the notice as voter-ready.",
        "public_status_page": "Run keyboard/focus/heading/form/status-update checks before public promotion.",
        "language_access_coverage": "Confirm covered and locally supported languages, proofing, oral assistance, and correction parity.",
        "alternate_formats": "Publish alternate-format request paths and response expectations before relying on the artifact.",
        "assistive_technology_interoperability": "Run representative screen-reader, keyboard, zoom/reflow, and error-message smoke checks.",
        "hotline_and_human_help": "Verify human help routes, hours, fallback channels, and minimum-disclosure safety language.",
        "emergency_notice_parity": "Check emergency publication parity across channels, languages, accessible text, and fallback copies.",
        "translated_correction_notice": "Propagate supersession and correction status to translated and simplified versions.",
        "media_and_screenshot_accessibility": "Add captions, transcript, alt text, and body-text equivalent before public release.",
        "polling_location_and_map_accessibility": "Add text-list location fallback, accessible-route notes, date scope, and non-geolocation lookup.",
        "ai_assisted_translation_or_summary": "Record source text, human approval, PII discipline, and prohibited-use checks for AI-assisted output.",
        "intimidation_safety_public_answer": "Route help and preserve evidence while avoiding legal conclusions and unsafe disclosure requests.",
        "offline_low_bandwidth_copy": "Publish printable or low-bandwidth text with digest, check date, share-safe link, and fallback channel.",
        "accessibility_language_gate": "Keep public release blocked until each applicable row has local approval or documented exception.",
    }
    return actions.get(family, "Apply the accessibility/language usability floor and record local reviewer approval before publication.")


def build_matrix() -> dict[str, Any]:
    policies = read_csv(REG)
    rows: list[dict[str, Any]] = []
    missing_refs: list[str] = []
    for r in policies:
        template_refs = tokens(r.get("template_refs", ""))
        support_refs = tokens(r.get("support_refs", ""))
        template_status = [ref_status(x) for x in template_refs]
        support_status = [ref_status(x) for x in support_refs]
        for rs in template_status + support_status:
            if not rs.get("exists"):
                missing_refs.append(str(rs.get("ref") or ""))
        rows.append({
            "policy_id": r.get("policy_id"),
            "public_surface_family": r.get("public_surface_family"),
            "status": "MISSING_LOCAL_ACCESSIBILITY_LANGUAGE_APPROVAL",
            "voter_harm_risk": r.get("voter_harm_risk"),
            "usability_floor": r.get("usability_floor"),
            "required_checks": r.get("required_checks"),
            "reviewer_role": r.get("reviewer_role"),
            "release_gate": r.get("release_gate"),
            "template_refs": template_refs,
            "support_refs": support_refs,
            "template_ref_status": template_status,
            "support_ref_status": support_status,
            "synthetic_status": r.get("synthetic_status"),
            "public_boundary": r.get("public_boundary"),
            "non_claims": r.get("non_claims"),
            "next_action": next_action_for(r),
        })
    blocking = [r for r in rows if str(r.get("release_gate") or "").startswith("blocks")]
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "decision_id": f"ALP-{VERSION}",
        "decision": DECISION,
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "no_public_release_authorization": True,
        "no_current_voter_instruction_claim": True,
        "no_accessibility_conformance_certification": True,
        "no_language_coverage_determination": True,
        "policy_count": len(rows),
        "blocking_policy_count": len(blocking),
        "missing_local_approval_count": len(rows),
        "missing_support_ref_count": len([x for x in missing_refs if x]),
        "rows": rows,
        "boundary": BOUNDARY,
        "non_claims": [
            "This pack does not authorize public release of local voter-facing artifacts.",
            "This pack does not certify WCAG, ADA, HAVA, or Section 203 compliance.",
            "This pack does not decide current voter instructions, eligibility, rights, or legal obligations.",
            "This pack does not replace local accessibility, language-access, counsel, or public-records review.",
        ],
    }


def build_burndown(matrix: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in matrix.get("rows") or []:
        if isinstance(row, dict):
            grouped[str(row.get("release_gate") or "unknown")].append(row)
    rows = []
    for gate in sorted(grouped):
        vals = grouped[gate]
        rows.append({
            "release_gate": gate,
            "policy_count": len(vals),
            "missing_local_approval_count": sum(1 for r in vals if r.get("status") == "MISSING_LOCAL_ACCESSIBILITY_LANGUAGE_APPROVAL"),
            "public_surface_families": "; ".join(str(r.get("public_surface_family") or "") for r in vals),
            "first_next_action": str(vals[0].get("next_action") or "") if vals else "",
            "non_claims": BOUNDARY,
        })
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "decision": matrix.get("decision"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "gate_count": len(rows),
        "rows": rows,
        "boundary": BOUNDARY,
    }


def build_preview_index(matrix: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in matrix.get("rows") or []:
        out.append({
            "policy_id": str(row.get("policy_id") or ""),
            "public_surface_family": str(row.get("public_surface_family") or ""),
            "usable_after_review": str(row.get("usability_floor") or ""),
            "must_check_before_publication": str(row.get("required_checks") or ""),
            "public_boundary": str(row.get("public_boundary") or ""),
            "non_claims": str(row.get("non_claims") or ""),
        })
    return out


def notice_md(matrix: dict[str, Any], burndown: dict[str, Any]) -> str:
    lines = [
        "# Accessibility/language publication no-go notice",
        "",
        f"Archive version: `{matrix['archive_version']}`  ",
        f"Release date: `{matrix['release_date']}`  ",
        "",
        "**No-go for public release of local voter-facing artifacts until accessibility, language-access, plain-language, fallback, and human-help review is complete. Synthetic-only. This is not live election evidence, not current voter instruction, not public-release authorization, not formal accessibility certification, not a language-coverage determination, and not legal advice.**",
        "",
        "## Decision",
        "",
        f"`{matrix['decision']}`",
        "",
        "The synthetic archive can publish example outputs, but live or local voter-facing artifacts need a separate reviewer-approved usability path. This gate prevents digest-correct and privacy-reviewed evidence from being treated as voter-ready when it lacks accessible text, language parity, alternate formats, low-bandwidth fallback, or safe human help.",
        "",
        "## Current accessibility/language state",
        "",
        f"- Policies: `{matrix['policy_count']}`.",
        f"- Blocking policies: `{matrix['blocking_policy_count']}`.",
        f"- Missing local approval rows: `{matrix['missing_local_approval_count']}`.",
        f"- Release-gate families: `{burndown['gate_count']}`.",
        "",
        "## Promotion condition",
        "",
        "Regenerate this pack with local accessibility and language-access approvals, documented exceptions, source-text parity checks, public/private field separation, and verified human-help routes. Public release remains no-go until every applicable policy row is closed or an accountable local exception is recorded.",
        "",
        "## First actions",
        "",
    ]
    for r in matrix.get("rows") or []:
        lines.append(f"- `{r['policy_id']}` / `{r['public_surface_family']}` — {r['next_action']}")
    lines += ["", "## Boundary", "", BOUNDARY, ""]
    return "\n".join(lines)


def write_outputs() -> dict[str, Any]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()
    burndown = build_burndown(matrix)
    preview = build_preview_index(matrix)
    (REPORTS / "accessibility-language-matrix.json").write_text(json.dumps(matrix, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "accessibility-language-matrix.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "public_surface_family", "status", "release_gate", "template_refs", "support_refs", "next_action", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in matrix["rows"]:
            w.writerow({
                "policy_id": r["policy_id"],
                "public_surface_family": r["public_surface_family"],
                "status": r["status"],
                "release_gate": r["release_gate"],
                "template_refs": "; ".join(r["template_refs"]),
                "support_refs": "; ".join(r["support_refs"]),
                "next_action": r["next_action"],
                "public_boundary": r["public_boundary"],
                "non_claims": r["non_claims"],
            })
    (REPORTS / "accessibility-language-burndown.json").write_text(json.dumps(burndown, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "accessibility-language-burndown.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["release_gate", "policy_count", "missing_local_approval_count", "public_surface_families", "first_next_action", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(burndown["rows"])
    with (REPORTS / "public-accessibility-preview-index.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["policy_id", "public_surface_family", "usable_after_review", "must_check_before_publication", "public_boundary", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(preview)
    (REPORTS / "accessibility-language-no-go-notice.md").write_text(notice_md(matrix, burndown), encoding="utf-8")
    return {"accessibility_language_matrix": matrix, "accessibility_language_burndown": burndown, "public_accessibility_preview_index": preview}


def build_output() -> dict[str, Any]:
    matrix = build_matrix()
    return {"accessibility_language_matrix": matrix, "accessibility_language_burndown": build_burndown(matrix), "public_accessibility_preview_index": build_preview_index(matrix)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic accessibility/language no-go reports")
    ap.add_argument("--json", action="store_true", help="Print accessibility/language matrix JSON wrapper")
    args = ap.parse_args()
    out = write_outputs() if args.write else build_output()
    if args.json:
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    else:
        m = out["accessibility_language_matrix"]
        print(f"PASS: accessibility/language publication pack ({m['archive_version']}, policies={m['policy_count']}, decision={m['decision']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
