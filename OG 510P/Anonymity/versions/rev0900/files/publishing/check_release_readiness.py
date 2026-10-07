#!/usr/bin/env python3
"""Audit Candidate and Published-ready sources for static release readiness.

This is a release-lane visibility check, not a publication command.  It binds
queue rows to exact ``source_tex`` paths, records source hashes, checks static
citation/reference closure, detects obvious placeholders, and recommends a
low-friction candidate only as an operator starting point.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import release_preflight as rp  # noqa: E402
import publication_target as pt  # noqa: E402

CHECKED_STATES = ["published_ready", "candidate"]
EVIDENCE_PACK_WARNING = {
    "category": "evidence_pack_review_needed",
    "detail": "Source text likely makes artifact/provenance/evidence claims; publication freeze should attach or explicitly waive a minimal evidence pack.",
}
ARTIFACT_NEEDLES = re.compile(
    r"\b(artifact|receipt|manifest|provenance|evidence|validator|verification|verifier|notary|certificate|ledger|audit|support bundle|digest|hash|trace|budget|DHT)\b",
    re.IGNORECASE,
)
MALFORMED_BIB_COMMAND_RE = re.compile(r"(?m)^\s*(ibitem|ewblock)\b")
QUEUE_BOUND_SOURCE_HASH_RE = re.compile(r"sha256:([0-9a-f]{64})")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def source_family(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "series":
        return parts[1]
    if len(parts) >= 2 and parts[0] == "published":
        return "published"
    return "unknown"


def queue_items(queue_index: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for state in CHECKED_STATES:
        for ordinal, item in enumerate(queue_index.get("states", {}).get(state, [])):
            if not isinstance(item, dict):
                continue
            merged = dict(item)
            merged["queue_state"] = state
            merged["queue_order_in_state"] = ordinal
            out.append(merged)
    return out


def exact_source_state_map(queue_index: dict[str, Any]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = collections.defaultdict(list)
    for state, items in queue_index.get("states", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and item.get("source_tex"):
                mapping[str(item["source_tex"])].append(str(state))
    return {src: sorted(states) for src, states in mapping.items()}


def duplicate_source_bindings(queue_index: dict[str, Any]) -> list[dict[str, Any]]:
    bindings: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for state, items in queue_index.get("states", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and item.get("source_tex"):
                bindings[str(item["source_tex"])].append({"queue_state": str(state), "item_id": str(item.get("item_id", "")), "decision_note": str(item.get("path", ""))})
    return [
        {"source_tex": src, "bindings": rows}
        for src, rows in sorted(bindings.items())
        if len(rows) > 1
    ]


def prospective_target(item: dict[str, Any]) -> str:
    date = str(item.get("date") or "YYYY.MM.DD")
    title = str(item.get("title") or "Untitled")
    try:
        return pt.portable_published_path(date, title)
    except ValueError:
        return "published/__invalid_publication_target__"


def source_needs_evidence_review(text: str) -> bool:
    # The warning is deliberately advisory.  A future release can satisfy it by
    # attaching the minimal evidence pack or by recording an explicit waiver.
    return bool(ARTIFACT_NEEDLES.search(text))


def malformed_bibliography_commands(text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        match = MALFORMED_BIB_COMMAND_RE.match(line)
        if match:
            findings.append({"line": line_no, "command_fragment": match.group(1), "text": line.strip()[:160]})
    return findings



def decision_note_source_hashes(root: pathlib.Path, note_rel: str) -> list[str]:
    """Return sha256 hex values carried by a queue decision note.

    The queue note is a human governance object.  Release readiness should fail
    closed when it no longer names the exact source bytes being audited.
    """
    if not note_rel:
        return []
    path = root / note_rel
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    return sorted(set(QUEUE_BOUND_SOURCE_HASH_RE.findall(text)))


def hash_binding_status(root: pathlib.Path, note_rel: str, current_hash: str) -> dict[str, Any]:
    values = decision_note_source_hashes(root, note_rel)
    return {
        "decision_note_source_sha256_values": values,
        "decision_note_source_sha256_current_match": current_hash in values,
        "decision_note_source_sha256_value_count": len(values),
    }

def audit_item(root: pathlib.Path, item: dict[str, Any], source_states: dict[str, list[str]]) -> dict[str, Any]:
    rel = str(item.get("source_tex") or "")
    state = str(item.get("queue_state") or item.get("state") or "unknown")
    src = root / rel if rel else root / "__missing_source_tex__"
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    details: dict[str, Any] = {
        "exact_queue_states": source_states.get(rel, []),
        "queue_record_count_for_source": len(source_states.get(rel, [])),
        "prospective_target": prospective_target(item),
    }

    text = ""
    if not rel:
        blockers.append({"category": "missing_source_tex", "detail": "queue item has no source_tex field"})
    elif not src.exists():
        blockers.append({"category": "missing_source_file", "detail": rel})
    elif src.suffix != ".tex":
        blockers.append({"category": "source_not_tex", "detail": rel})
    else:
        text = src.read_text(encoding="utf-8", errors="replace")
        details["source_sha256"] = sha256_file(src)
        details["source_bytes"] = src.stat().st_size
        details.update(hash_binding_status(root, str(item.get("path", "")), details["source_sha256"]))
        closure = rp.citation_and_reference_closure(src, text)
        details["citation_reference_closure"] = closure
        placeholders = rp.placeholder_findings(text)
        details["placeholder_findings"] = placeholders
        malformed = malformed_bibliography_commands(text)
        details["malformed_bibliography_commands"] = malformed
        details["artifact_governance_likely"] = source_needs_evidence_review(text)

        if closure["missing_bibliography_files"]:
            blockers.append({"category": "missing_bibliography_files", "detail": closure["missing_bibliography_files"]})
        if closure["undefined_citations"]:
            blockers.append({"category": "undefined_citations", "count": len(closure["undefined_citations"]), "detail": closure["undefined_citations"][:60]})
        if closure["undefined_references"]:
            blockers.append({"category": "undefined_references", "count": len(closure["undefined_references"]), "detail": closure["undefined_references"][:60]})
        if placeholders:
            blockers.append({"category": "placeholder_markers", "count": len(placeholders), "detail": placeholders[:10]})
        if details.get("malformed_bibliography_commands"):
            blockers.append({"category": "malformed_bibliography_commands", "count": len(details["malformed_bibliography_commands"]), "detail": details["malformed_bibliography_commands"][:20]})
        if not details.get("decision_note_source_sha256_values"):
            blockers.append({"category": "decision_note_missing_source_sha256", "detail": str(item.get("path", ""))})
        elif not details.get("decision_note_source_sha256_current_match"):
            blockers.append({"category": "decision_note_source_sha256_mismatch", "detail": {"decision_note": str(item.get("path", "")), "current_source_sha256": details.get("source_sha256"), "note_values": details.get("decision_note_source_sha256_values")}})
        if details["artifact_governance_likely"]:
            warnings.append(dict(EVIDENCE_PACK_WARNING))

    if rel.startswith("published/"):
        blockers.append({"category": "already_under_published", "detail": rel})

    exact_states = source_states.get(rel, [])
    if rel and state not in exact_states:
        blockers.append({"category": "queue_binding_missing", "detail": {"expected_state": state, "exact_queue_states": exact_states}})
    if rel and len(exact_states) != 1:
        blockers.append({"category": "non_singleton_queue_binding", "detail": {"exact_queue_states": exact_states}})

    if rel.startswith("series/synthesis/paper17_"):
        warnings.append({"category": "freeze_churn_review_needed", "detail": "Worked example has repeated support-surface churn; verify true freeze before publication."})
    elif rel.startswith("series/synthesis/"):
        m = re.match(r"series/synthesis/paper(\d+)_", rel)
        if m and int(m.group(1)) >= 31:
            warnings.append({"category": "late_synthesis_defer_by_default", "detail": "Late synthesis paper; default posture is defer unless stabilization is recorded."})

    if blockers:
        readiness = "blocked"
    elif state == "published_ready":
        readiness = "static_preflight_pass"
    else:
        readiness = "not_a_release_target"

    return {
        "item_id": str(item.get("item_id", "")),
        "queue_state": state,
        "queue_order_in_state": item.get("queue_order_in_state", None),
        "source_tex": rel,
        "title": str(item.get("title", "")),
        "decision_note": str(item.get("path", "")),
        "source_family": source_family(rel),
        "release_readiness": readiness,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "warnings": warnings,
        "details": details,
    }


def evidence_pack_sources(root: pathlib.Path) -> set[str]:
    """Return sources that already have a materialized evidence-pack lane.

    The source hash inside an older pack may be stale after a claim-narrowing
    edit; the builder can refresh it.  The selector uses this only as a
    sequencing preference so a downstream paper without the required card does
    not accidentally displace the already-staged first-card lane.
    """
    out: set[str] = set()
    pack_root = root / "release_queue" / "evidence_packs"
    if not pack_root.exists():
        return out
    for manifest_path in sorted(pack_root.glob("*/EVIDENCE_PACK_MANIFEST.json")):
        try:
            manifest = load_json(manifest_path)
        except Exception:
            continue
        source = str(manifest.get("source_tex", "")).strip()
        if source:
            out.add(source)
    return out


CONCEPTUAL_RELEASE_SEQUENCE_RANKS = {
    # Congestion-family order is security-relevant: publish the theorem/accountant
    # root before mechanism knobs, and publish the replay/checker companion last.
    "series/congestion_series/paper1_congestion_eq/paper.tex": 10,
    "series/congestion_series/paper2_psc_q/paper.tex": 11,
    "series/congestion_series/paper3_w_congestion_eq/paper.tex": 12,
    # State-family order is similarly release-relevant: publish the generic
    # state accountant before the DHT-specific MUCC floor, then monitoring/support.
    "series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex": 20,
    "series/anondht_state_series/paper2_mucc_committee_contact_privacy/paper.tex": 21,
    "series/anondht_state_series/paper3_closed_view_auditing_cppc/paper.tex": 22,
    "series/anondht_state_series/paper1A_state_dependent_anonymity_calibration_addendum/paper.tex": 23,
    "series/anondht_state_series/paper3A_cppc_addendum/paper.tex": 24,
}


def release_sequence_rank(source: str) -> int:
    """Smallest known conceptual release-order rank for a source."""
    return CONCEPTUAL_RELEASE_SEQUENCE_RANKS.get(source, 10_000)


def choose_recommendation(items: list[dict[str, Any]], root: pathlib.Path | None = None) -> dict[str, Any]:
    candidates = [
        item for item in items
        if item.get("queue_state") == "published_ready" and item.get("release_readiness") == "static_preflight_pass"
    ]
    if not candidates:
        return {"status": "none", "reason": "No Published-ready item passed static preflight."}

    staged_evidence_sources = evidence_pack_sources(root) if root is not None else set()

    def sort_key(item: dict[str, Any]) -> tuple[int, int, int, int, int, int, int, str]:
        details = item.get("details", {})
        closure = details.get("citation_reference_closure", {})
        source = str(item.get("source_tex", ""))
        is_synthesis = 1 if source.startswith("series/synthesis/") else 0
        lacks_staged_pack = 0 if source in staged_evidence_sources else 1
        return (
            is_synthesis,
            release_sequence_rank(source),
            int(item.get("queue_order_in_state", 10**9)),
            lacks_staged_pack,
            len(item.get("warnings", [])),
            int(details.get("source_bytes", 10**12)),
            int(closure.get("citation_key_count", 10**9)),
            source,
        )

    item = sorted(candidates, key=sort_key)[0]
    details = item.get("details", {})
    source = str(item.get("source_tex", ""))
    staged = source in staged_evidence_sources
    return {
        "status": "static_pass_candidate_available",
        "source_tex": item.get("source_tex"),
        "title": item.get("title"),
        "decision_note": item.get("decision_note"),
        "source_sha256": details.get("source_sha256"),
        "warning_count": len(item.get("warnings", [])),
        "evidence_pack_lane_already_staged": staged,
        "release_sequence_rank": release_sequence_rank(source),
        "reason": "Static-pass Published-ready recommendation, preferring explicit conceptual release-sequence roots before staged evidence-pack accidents, then queue order, warning count, source size, and citation-edge count. This avoids publishing a downstream checker before its theorem/accountant root; it does not authorize publication.",
    }


def check(root: pathlib.Path) -> dict[str, Any]:
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    states_by_source = exact_source_state_map(queue_index)
    items = [audit_item(root, item, states_by_source) for item in queue_items(queue_index)]

    state_counts: collections.Counter[str] = collections.Counter(item["queue_state"] for item in items)
    readiness_counts: collections.Counter[str] = collections.Counter(item["release_readiness"] for item in items)
    family_counts: collections.Counter[str] = collections.Counter(item["source_family"] for item in items)
    blocker_counts: collections.Counter[str] = collections.Counter()
    malformed_count = 0
    source_hash_bound_count = 0
    source_hash_missing_count = 0
    source_hash_mismatch_count = 0
    for item in items:
        details = item.get("details", {})
        malformed_count += len(details.get("malformed_bibliography_commands", []))
        if details.get("source_sha256"):
            if details.get("decision_note_source_sha256_current_match"):
                source_hash_bound_count += 1
            elif details.get("decision_note_source_sha256_values"):
                source_hash_mismatch_count += 1
            else:
                source_hash_missing_count += 1
        for blocker in item.get("blockers", []):
            blocker_counts[str(blocker.get("category", "unknown"))] += 1

    duplicates = duplicate_source_bindings(queue_index)
    published_ready_blocked = [item for item in items if item["queue_state"] == "published_ready" and item["release_readiness"] != "static_preflight_pass"]
    checked_state_blocked = [item for item in items if item["release_readiness"] == "blocked"]
    expected_counts_ok = all(state_counts.get(state, 0) == int(queue_index.get("summary", {}).get(state, 0)) for state in CHECKED_STATES)
    malformed_count = sum(len(item.get("details", {}).get("malformed_bibliography_commands", [])) for item in items)

    status = "pass" if not published_ready_blocked and not checked_state_blocked and not duplicates and expected_counts_ok and malformed_count == 0 and source_hash_missing_count == 0 and source_hash_mismatch_count == 0 else "fail"
    return {
        "status": status,
        "generated_for_revision": release_manifest["revision"],
        "checked_bundle": release_manifest["bundle"],
        "checked_states": CHECKED_STATES,
        "publication_authorized": False,
        "items": items,
        "summary": {
            "checked_item_count": len(items),
            "state_counts": dict(sorted(state_counts.items())),
            "release_readiness_counts": dict(sorted(readiness_counts.items())),
            "source_family_counts": dict(sorted(family_counts.items())),
            "blocker_category_counts": dict(sorted(blocker_counts.items())),
            "duplicate_source_binding_count": len(duplicates),
            "expected_counts_match_queue_index": expected_counts_ok,
            "malformed_bibliography_command_count": malformed_count,
            "source_hash_bound_count": source_hash_bound_count,
            "source_hash_missing_count": source_hash_missing_count,
            "source_hash_mismatch_count": source_hash_mismatch_count,
        },
        "duplicate_source_bindings": duplicates,
        "next_release_recommendation": choose_recommendation(items, root),
        "fail_closed_rule": "This audit never authorizes publication. A selected source still needs an explicit decision, a decision-note source-hash match, and a clean per-paper release_preflight.py run before freeze.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
