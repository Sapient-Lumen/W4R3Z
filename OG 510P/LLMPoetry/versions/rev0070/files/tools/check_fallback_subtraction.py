#!/usr/bin/env python3
"""Validate the D011 fallback-subtraction boundary after rev0042.

This gate exists because rev0042 deliberately crossed the rev0041 reader-first
hold under a bounded project-owner-delegated override. After a later successor
draft exists, this remains a historical boundary check: D011 must stay logged,
non-candidate, non-evidence, cold-reviewable, and firewalled from D010 reader
response surfaces. It does not judge poem quality.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

FALLBACK_HEAD = "P0002-D011"
def is_fallback_or_successor_head(head: str | None) -> bool:
    if not isinstance(head, str) or not head.startswith("P0002-D"):
        return False
    try:
        return int(head.split("-D", 1)[1]) >= 11
    except ValueError:
        return False
PREVIOUS_CANDIDATE = "P0002-D010"
DRAFT = Path("poems/P0002/draft_011.md")
PACKET = Path("poems/P0002/material/source_material_packet_011.json")
D010_CANDIDATE = Path("anthology/candidates/P0002-D010_candidate_packet.json")
D010_RESPONSE_LOG = Path("anthology/candidates/P0002-D010_reader_responses.json")
HUMAN_LOG = Path("registries/human_intervention_log.json")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def add(checks: list[dict], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def poem_body(raw: str) -> str:
    if "## Poem" not in raw or "## Disclosure" not in raw:
        return ""
    return raw.split("## Poem", 1)[1].split("## Disclosure", 1)[0].strip("\n")


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    proof = load_json(root / "registries/proof_status.json")
    rev = state.get("revision")
    current = surface.get("current_head")
    add(checks, "fallback_subtraction_current_head_allowed", is_fallback_or_successor_head(current) or not str(current).startswith("P0002-D"), str(current))
    add(checks, "fallback_subtraction_proof_current_matches_surface", proof.get("current_head") == current and proof.get("current_draft") == current and proof.get("latest_draft") == current, f"{proof.get('current_head')} {proof.get('current_draft')} {proof.get('latest_draft')} surface={current}")

    for rel in (DRAFT, PACKET, D010_CANDIDATE, D010_RESPONSE_LOG, HUMAN_LOG):
        add(checks, f"fallback_subtraction_path_exists:{rel.as_posix()}", (root / rel).exists(), rel.as_posix())
    if not (root / DRAFT).exists() or not (root / PACKET).exists():
        return checks

    raw = text(root / DRAFT)
    body = poem_body(raw)
    disclosure = raw.split("## Disclosure", 1)[1] if "## Disclosure" in raw else ""
    add(checks, "fallback_subtraction_body_present", bool(body.strip()), f"chars={len(body)}")
    add(checks, "fallback_subtraction_disclosure_present", "Disclosure:" in disclosure, "## Disclosure")
    add(checks, "fallback_subtraction_disclosure_names_override", "project-owner-delegated override" in disclosure and "not reader evidence" in disclosure, disclosure[:200])
    add(checks, "fallback_subtraction_disclaims_live_reading", "no current/live reading is claimed" in disclosure, "no current/live reading is claimed")
    add(checks, "fallback_subtraction_status_nonclaim", all(s in disclosure for s in ["not admitted", "not evidence-ready"]), disclosure[:200])

    required = [
        "Behind the Marine Inspection Office,",
        "the pier kept a ruler",
        "with its first zero",
        "No value came back.",
        "Water did.",
        "It knocks.",
        "inside the old holes.",
    ]
    for phrase in required:
        add(checks, f"fallback_subtraction_required_body_string:{phrase}", phrase in body, phrase)

    forbidden = [
        "Station Datum",
        "Not the tide.",
        "The rule\nfor saying tide.",
        "Its zero remains.",
        "Height does not.",
        "A beginning was set\nlower than water\nwas expected to reach.",
        "cloudtainer",
        "NOAA",
        "date=latest",
        "DNS",
    ]
    bad = [phrase for phrase in forbidden if phrase.lower() in body.lower()]
    add(checks, "fallback_subtraction_forbidden_body_strings_absent", not bad, bad)
    body_words = WORD_RE.findall(body)
    nonblank = [ln for ln in body.splitlines() if ln.strip()]
    nums = re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?![A-Za-z])", body)
    add(checks, "fallback_subtraction_body_word_cap", len(body_words) <= 170, f"words={len(body_words)}")
    add(checks, "fallback_subtraction_body_line_cap", len(nonblank) <= 45, f"lines={len(nonblank)}")
    add(checks, "fallback_subtraction_body_no_numbers", not nums, nums)
    add(checks, "fallback_subtraction_body_no_banlist_house_terms", not any(term in body.lower() for term in ["pinhole", "voltage", "motors", "coded air", "parity", "glyph", "syntax", "spool"]), "house terms")

    packet = load_json(root / PACKET)
    expected_packet_revision = rev if current == FALLBACK_HEAD else "rev0042"
    add(checks, "fallback_subtraction_packet_revision_historical_or_current", packet.get("revision") == expected_packet_revision, f"packet={packet.get('revision')} expected={expected_packet_revision}")
    add(checks, "fallback_subtraction_packet_draft", packet.get("draft_id") == FALLBACK_HEAD, packet.get("draft_id"))
    add(checks, "fallback_subtraction_packet_quality_claims_empty", packet.get("quality_claims") == [], str(packet.get("quality_claims")))
    add(checks, "fallback_subtraction_packet_not_candidate", packet.get("constraints", {}).get("not_anthology_candidate") is True and "not an anthology candidate" in packet.get("non_claim", "").lower(), packet.get("non_claim", ""))
    policy = packet.get("fallback_subtraction_policy") or {}
    add(checks, "fallback_subtraction_policy_mode", policy.get("mode") == "owner_override_subtraction_fallback", str(policy.get("mode")))
    add(checks, "fallback_subtraction_policy_trigger_record", "HI-REV0042-OWNER-DELEGATED-OVERRIDE" in str(policy.get("trigger_record", "")), str(policy.get("trigger_record")))
    for phrase in policy.get("forbidden_body_strings", []) or []:
        add(checks, f"fallback_subtraction_policy_forbidden_absent:{phrase}", phrase.lower() not in body.lower(), phrase)
    for phrase in policy.get("required_body_strings", []) or []:
        add(checks, f"fallback_subtraction_policy_required_present:{phrase}", phrase in body, phrase)

    human = load_json(root / HUMAN_LOG)
    entries = human.get("entries", []) + human.get("interventions", [])
    override = next((e for e in entries if e.get("entry_id") == "HI-REV0042-OWNER-DELEGATED-OVERRIDE" or e.get("intervention_id") == "HI-REV0042-OWNER-DELEGATED-OVERRIDE"), None)
    add(checks, "fallback_subtraction_override_logged", override is not None, "HI-REV0042-OWNER-DELEGATED-OVERRIDE")
    if override:
        add(checks, "fallback_subtraction_override_boundary", override.get("not_reader_response") is True and override.get("not_admission") is True and override.get("not_evidence") is True, str(override))
        add(checks, "fallback_subtraction_override_bounded", override.get("bounded_override") is True, str(override))

    candidate = load_json(root / D010_CANDIDATE)
    add(checks, "fallback_subtraction_d010_candidate_preserved", candidate.get("draft_id") == PREVIOUS_CANDIDATE and candidate.get("not_admitted") is True and candidate.get("not_evidence_candidate") is True, str(candidate.get("status")))
    add(checks, "fallback_subtraction_d010_candidate_not_current", candidate.get("superseded_by_fallback_draft") == FALLBACK_HEAD or is_fallback_or_successor_head(candidate.get("current_head_after_fallback")), str(candidate.get("current_head_after_fallback")))

    # Rev0043: if a successor has been created, D011 must have received the later-turn
    # cold review that rev0042 required before any further drafting.
    review_json = root / "poems/P0002/judgments/cold_review_011_on_D011.json"
    review_md = root / "poems/P0002/judgments/cold_review_011_on_D011.md"
    add(checks, "fallback_subtraction_d011_cold_review_exists_after_successor", is_fallback_or_successor_head(current) and current == FALLBACK_HEAD or (review_json.exists() and review_md.exists()), "cold_review_011_on_D011")
    if review_json.exists():
        review = load_json(review_json)
        add(checks, "fallback_subtraction_d011_cold_review_verdict", review.get("verdict") == "revise_not_promote", review.get("verdict"))
        add(checks, "fallback_subtraction_d011_review_not_evidence", review.get("not_admission") is True and review.get("not_evidence") is True, str(review))
    log = load_json(root / D010_RESPONSE_LOG)
    add(checks, "fallback_subtraction_no_reader_response_fabricated", log.get("response_count") == len(log.get("responses", [])) == 0, f"count={log.get('response_count')}")
    dumped_log = json.dumps(log, ensure_ascii=False).lower()
    add(checks, "fallback_subtraction_override_not_in_reader_log", "owner" not in dumped_log and "override" not in dumped_log and "d011" not in dumped_log, "reader log leaked override" if any(s in dumped_log for s in ["owner", "override", "d011"]) else "")
    return checks


def main(root: str = ".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
