#!/usr/bin/env python3
"""Validate preserved P0002-D010 candidate-pressure surfaces.

Rev0042 allows P0002-D011 to become the global current head through a bounded fallback override, while D010 remains a preserved candidate-pressure object.

Rev0041 adds a poem-facing adversarial read and a fallback revision brief after
several infrastructure turns around reader handoff.  This gate blocks the two
risks found in that pass: stale candidate draft hashes and internal critique
being mistaken for a reader response, evidence, or admission.
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

CANDIDATE_HEAD = "P0002-D010"
CURRENT_FALLBACK_HEAD = "P0002-D011"
def is_candidate_successor_head(head: str | None) -> bool:
    if not isinstance(head, str) or not head.startswith("P0002-D"):
        return False
    try:
        return int(head.split("-D", 1)[1]) >= 11
    except ValueError:
        return False
DRAFT = Path("poems/P0002/draft_010.md")
CANDIDATE = Path("anthology/candidates/P0002-D010_candidate_packet.json")
ADVERSARIAL_MD = Path("anthology/candidates/P0002-D010_adversarial_candidate_read_rev0041.md")
ADVERSARIAL_JSON = Path("anthology/candidates/P0002-D010_adversarial_candidate_read_rev0041.json")
FALLBACK_MD = Path("anthology/candidates/P0002-D010_fallback_revision_brief_rev0041.md")
FALLBACK_JSON = Path("anthology/candidates/P0002-D010_fallback_revision_brief_rev0041.json")
RESPONSE_LOG = Path("anthology/candidates/P0002-D010_reader_responses.json")
HANDOFF_BUNDLE = Path("anthology/candidates/P0002-D010_reader_handoff_bundle.zip")


def add(checks: list[dict], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    rev = state.get("revision")
    current_head = surface.get("current_head")
    add(checks, "candidate_pressure_global_head_allowed", current_head == CANDIDATE_HEAD or is_candidate_successor_head(current_head) or not str(current_head).startswith("P0002-D"), str(current_head))

    for rel in (DRAFT, CANDIDATE, ADVERSARIAL_MD, ADVERSARIAL_JSON, FALLBACK_MD, FALLBACK_JSON, RESPONSE_LOG):
        add(checks, f"candidate_pressure_path_exists:{rel.as_posix()}", (root / rel).exists(), rel.as_posix())
    if not (root / CANDIDATE).exists() or not (root / DRAFT).exists():
        return checks

    actual_hash = sha256_file(root / DRAFT)
    candidate = load_json(root / CANDIDATE)
    add(checks, "candidate_pressure_candidate_hash_matches_draft", candidate.get("draft_sha256") == actual_hash, f"candidate={candidate.get('draft_sha256')} actual={actual_hash}")
    add(checks, "candidate_pressure_candidate_not_admitted", candidate.get("not_admitted") is True and candidate.get("not_evidence_candidate") is True, str(candidate.get("status")))
    add(checks, "candidate_pressure_quality_claims_empty", candidate.get("quality_claims", []) == [] or "quality_claims" not in candidate, str(candidate.get("quality_claims", [])))
    for key, rel in {
        "adversarial_candidate_read": ADVERSARIAL_JSON.as_posix(),
        "adversarial_candidate_read_markdown": ADVERSARIAL_MD.as_posix(),
        "fallback_revision_brief": FALLBACK_JSON.as_posix(),
        "fallback_revision_brief_markdown": FALLBACK_MD.as_posix(),
    }.items():
        add(checks, f"candidate_pressure_candidate_declares:{key}", candidate.get(key) == rel or rel in candidate.get("basis", []), f"{key}={candidate.get(key)}")

    meta = load_json(root / "poems/P0002/metadata.json")
    d010 = next((d for d in meta.get("drafts", []) if d.get("draft_id") == CANDIDATE_HEAD), {})
    add(checks, "candidate_pressure_metadata_hash_matches_draft", d010.get("draft_sha256") == actual_hash, f"metadata={d010.get('draft_sha256')} actual={actual_hash}")
    add(checks, "candidate_pressure_metadata_status_candidate", "candidate" in str(d010.get("status", "")).lower() and d010.get("admitted") is False and d010.get("evidence_candidate") is False, str(d010.get("status")))

    adv = load_json(root / ADVERSARIAL_JSON) if (root / ADVERSARIAL_JSON).exists() else {}
    adv_md = text(root / ADVERSARIAL_MD)
    add(checks, "candidate_pressure_adversarial_revision_matches", adv.get("revision") in {rev, "rev0041"}, adv.get("revision"))
    add(checks, "candidate_pressure_adversarial_draft_matches", adv.get("draft_id") == CANDIDATE_HEAD, adv.get("draft_id"))
    add(checks, "candidate_pressure_adversarial_not_reader_response", adv.get("not_reader_response") is True and adv.get("not_evidence") is True and adv.get("not_admission") is True, str(adv))
    add(checks, "candidate_pressure_adversarial_verdict_hold_only", adv.get("verdict") == "keep_candidate_hold_not_admit", adv.get("verdict"))
    add(checks, "candidate_pressure_adversarial_line_level_findings", len(adv.get("line_level_findings", [])) >= 8, f"count={len(adv.get('line_level_findings', []))}")
    add(checks, "candidate_pressure_adversarial_has_reader_trigger", bool(adv.get("reader_triggered_decision_rules")), "reader_triggered_decision_rules")
    required_md = ["not a reader response", "Line-level findings", "Fallback revision brief", "Do not admit"]
    missing_md = [s for s in required_md if s.lower() not in adv_md.lower()]
    add(checks, "candidate_pressure_adversarial_markdown_required_sections", not missing_md, missing_md)

    fallback = load_json(root / FALLBACK_JSON) if (root / FALLBACK_JSON).exists() else {}
    fallback_md = text(root / FALLBACK_MD)
    add(checks, "candidate_pressure_fallback_revision_matches", fallback.get("revision") in {rev, "rev0041"}, fallback.get("revision"))
    add(checks, "candidate_pressure_fallback_not_current_draft", fallback.get("not_created_as_d011") is True, str(fallback.get("not_created_as_d011")))
    add(checks, "candidate_pressure_fallback_blocks_inertia_d011", fallback.get("requires_reader_rejection_or_project_owner_override") is True, str(fallback))
    constraints = fallback.get("d011_constraints_if_triggered", [])
    add(checks, "candidate_pressure_fallback_constraints_substantive", len(constraints) >= 6, f"count={len(constraints)}")
    add(checks, "candidate_pressure_fallback_markdown_mentions_no_d011", "no d011 is created" in fallback_md.lower(), FALLBACK_MD.as_posix())
    add(checks, "candidate_pressure_triggered_fallback_draft_preserved", (root / "poems/P0002/draft_011.md").exists(), "poems/P0002/draft_011.md")

    log = load_json(root / RESPONSE_LOG) if (root / RESPONSE_LOG).exists() else {}
    dumped_log = json.dumps(log, ensure_ascii=False).lower()
    add(checks, "candidate_pressure_adversarial_not_in_reader_log", "adversarial_candidate_read" not in dumped_log and "fallback_revision_brief" not in dumped_log, "response log contains internal critique leakage" if "adversarial_candidate_read" in dumped_log else "")

    if (root / HANDOFF_BUNDLE).exists():
        with zipfile.ZipFile(root / HANDOFF_BUNDLE) as z:
            names = [n.lower() for n in z.namelist()]
            add(checks, "candidate_pressure_handoff_excludes_internal_pressure_files", not any("adversarial" in n or "fallback" in n for n in names), names)
    return checks


def main(root: str = ".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
