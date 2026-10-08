#!/usr/bin/env python3
"""Build the adopter authority-capture no-go pack.

rev0868 quarantined mutable state/local rows so they cannot look like current
voter instruction.  This pack turns that watchlist into an adopter work queue:
every quarantined source must have local capture, hash, office routing, conflict
review, and human approval before it can be promoted into voter-facing guidance.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import tomllib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from release_context import archive_version, release_date

ROOT = Path(__file__).resolve().parents[1]
VERSION = archive_version(ROOT)
RELEASE_DATE = release_date(ROOT)
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
REPORTS = ROOT / "artifacts" / "reports"

BOUNDARY = (
    "Adopter authority-capture support only; not current voter instruction, not legal advice, "
    "not source-byte cache completeness, not publication authorization, not certification, "
    "not independent validation, and not live-pilot authorization."
)
DECISION = "NO_GO_PUBLIC_GUIDANCE_ADOPTER_AUTHORITY_CAPTURE_MISSING"
PDFISH_RE = re.compile(r"\.(pdf|txt|csv|json|xml)(\?|$)", re.I)
DOC_TAG_RE = re.compile(r"^doc(\d+)$")
REQUIRED_EVIDENCE = [
    "adopter_capture_id",
    "captured_at_utc",
    "captured_by_role",
    "source_url_or_official_channel_id",
    "byte_or_text_sha256",
    "responsible_office",
    "public_help_route",
    "jurisdiction_scope",
    "election_scope_or_effective_date",
    "conflict_check_status",
    "human_approver_role",
    "approved_at_utc",
]


def load_sources() -> list[dict[str, Any]]:
    with LOCK.open("rb") as f:
        return tomllib.load(f).get("source", [])


def tags_of(row: dict[str, Any]) -> list[str]:
    return [str(t).strip() for t in (row.get("tags") or []) if str(t).strip()]


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def is_quarantined(row: dict[str, Any]) -> bool:
    tags = set(tags_of(row))
    return {"jurisdiction_quarantine", "not_current_voter_instruction"} <= tags and not str(row.get("sha256") or "").strip()


def doc_ids_from(tags: list[str]) -> list[str]:
    vals = []
    for tag in tags:
        m = DOC_TAG_RE.match(tag)
        if m:
            vals.append(m.group(1))
    return sorted(vals, key=int)


def topic_from(tags: list[str]) -> str:
    preferred = [
        "registration_status", "vote_center", "provisional_ballot", "emergency_absentee",
        "felony_eligibility", "no_fixed_address", "confidential_registration",
        "in_custody_voting", "facility_assisted_voting", "college_student_voting",
        "guardianship", "tribal_voting", "disaster_displacement", "new_citizen",
        "signature_alternatives", "youth_preregistration", "voter_assistance",
        "ballot_handoff", "challenge", "accessibility",
    ]
    tagset = set(tags)
    for tag in preferred:
        if tag in tagset:
            return tag
    for tag in tags:
        if tag not in {"official_websites", "special_case_high_risk", "jurisdiction_quarantine", "not_current_voter_instruction", "pdf"} and not tag.startswith("doc"):
            return tag
    return "uncategorized"


def priority_for(row: dict[str, Any], ref_count: int) -> tuple[int, str]:
    tags = set(tags_of(row))
    url = str(row.get("url") or "")
    pin_first = bool(PDFISH_RE.search(url))
    if "special_case_high_risk" in tags and pin_first:
        return (1, "pin_first_high_risk_document")
    if "special_case_high_risk" in tags and ref_count >= 2:
        return (2, "high_risk_multi_surface_route")
    if "special_case_high_risk" in tags:
        return (3, "high_risk_single_surface_route")
    if pin_first:
        return (4, "pin_first_document")
    return (5, "ordinary_state_local_route")


def citation_counts(ids: set[str]) -> Counter[str]:
    counts: Counter[str] = Counter()
    roots = [ROOT / "docs", ROOT / "artifacts" / "checklists", ROOT / "artifacts" / "templates"]
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.md") if root.name != "templates" else root.rglob("*.json"):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for sid in ids:
                # Tight enough for this small quarantined set; avoids pulling in another parser.
                counts[sid] += text.count(f"`{sid}`")
    return counts


def build_matrix() -> dict[str, Any]:
    rows = [r for r in load_sources() if is_quarantined(r)]
    ids = {str(r.get("id") or "") for r in rows}
    ref_counts = citation_counts(ids)
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        sid = str(row.get("id") or "")
        url = str(row.get("url") or "")
        tags = tags_of(row)
        ref_count = int(ref_counts.get(sid, 0))
        priority_rank, priority_lane = priority_for(row, ref_count)
        out_rows.append({
            "source_id": sid,
            "url": url,
            "host": host_of(url),
            "retrieved": str(row.get("retrieved") or ""),
            "review_by": str(row.get("review_by") or ""),
            "pin_exemption": str(row.get("pin_exemption") or ""),
            "topic": topic_from(tags),
            "surface_doc_ids": doc_ids_from(tags),
            "source_ref_count": ref_count,
            "pin_first_candidate": bool(PDFISH_RE.search(url)),
            "priority_rank": priority_rank,
            "priority_lane": priority_lane,
            "source_role_before_promotion": "xref_only_example_route",
            "status": "MISSING_ADOPTER_SOURCE_CAPTURE",
            "promotion_allowed": False,
            "public_answer_gate": "blocks_public_guidance",
            "required_evidence": REQUIRED_EVIDENCE,
            "non_claims": "not current voter instruction; not legal advice; not source-byte cache completeness",
        })
    out_rows.sort(key=lambda r: (r["priority_rank"], -int(r["source_ref_count"]), r["host"], r["source_id"]))

    by_lane = Counter(str(r["priority_lane"]) for r in out_rows)
    by_host = Counter(str(r["host"]) for r in out_rows)
    by_topic = Counter(str(r["topic"]) for r in out_rows)
    return {
        "archive_version": VERSION,
        "release_date": RELEASE_DATE,
        "decision": DECISION,
        "synthetic_only": True,
        "no_current_voter_instruction_claim": True,
        "no_live_deployment_claim": True,
        "quarantined_source_count": len(out_rows),
        "missing_capture_count": sum(1 for r in out_rows if r["status"] == "MISSING_ADOPTER_SOURCE_CAPTURE"),
        "pin_first_candidate_count": sum(1 for r in out_rows if r["pin_first_candidate"]),
        "priority_lane_counts": dict(sorted(by_lane.items())),
        "top_hosts": by_host.most_common(12),
        "top_topics": by_topic.most_common(12),
        "required_evidence": REQUIRED_EVIDENCE,
        "rows": out_rows,
        "boundary": BOUNDARY,
        "next_action": "For the adopter jurisdiction, capture/pin each needed official source, record office/help routing and human approval, then promote only the captured row used by the public answer.",
    }


def build_summary(matrix: dict[str, Any]) -> dict[str, Any]:
    rows = matrix.get("rows") or []
    by_lane: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        by_lane[str(r.get("priority_lane") or "unknown")].append(r)
    lanes = []
    for lane, vals in sorted(by_lane.items(), key=lambda item: min(int(v.get("priority_rank") or 99) for v in item[1])):
        lanes.append({
            "priority_lane": lane,
            "count": len(vals),
            "pin_first_candidate_count": sum(1 for v in vals if v.get("pin_first_candidate")),
            "sample_source_ids": [str(v.get("source_id")) for v in vals[:8]],
            "required_first_action": "capture bytes/text and hash before public guidance" if "pin_first" in lane else "record adopter-specific official route, text capture, conflict check, and human approval",
        })
    return {
        "archive_version": matrix.get("archive_version"),
        "release_date": matrix.get("release_date"),
        "decision": matrix.get("decision"),
        "lane_count": len(lanes),
        "lanes": lanes,
        "boundary": BOUNDARY,
    }


def write_outputs() -> dict[str, Any]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()
    summary = build_summary(matrix)
    (REPORTS / "adopter-authority-capture-matrix.json").write_text(json.dumps(matrix, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (REPORTS / "adopter-authority-capture-matrix.csv").open("w", encoding="utf-8", newline="") as f:
        fields = [
            "source_id", "host", "topic", "surface_doc_ids", "source_ref_count",
            "pin_first_candidate", "priority_rank", "priority_lane", "status",
            "promotion_allowed", "public_answer_gate", "source_role_before_promotion",
            "retrieved", "review_by", "pin_exemption", "non_claims",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in matrix["rows"]:
            row = dict(r)
            row["surface_doc_ids"] = ";".join(row.get("surface_doc_ids") or [])
            w.writerow({k: row.get(k, "") for k in fields})
    (REPORTS / "adopter-authority-capture-summary.json").write_text(json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    return {"matrix": matrix, "summary": summary}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic adopter authority-capture reports")
    ap.add_argument("--json", action="store_true", help="Print generated JSON")
    args = ap.parse_args()
    out = write_outputs() if args.write else {"matrix": build_matrix()}
    if "summary" not in out:
        out["summary"] = build_summary(out["matrix"])
    if args.json:
        print(json.dumps(out, sort_keys=True, separators=(",", ":")))
    else:
        m = out["matrix"]
        print(
            f"decision={m['decision']} version={m['archive_version']} "
            f"sources={m['quarantined_source_count']} missing_capture={m['missing_capture_count']} "
            f"pin_first={m['pin_first_candidate_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
