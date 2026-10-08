#!/usr/bin/env python3
"""Validate source-bound external-material poem packets.

The check is intentionally narrow: it verifies that factual material and
anti-house-diction constraints survive into the draft. It does not judge poem quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

WORD_BOUNDARY = r"(?<![A-Za-z0-9_-]){term}(?![A-Za-z0-9_-])"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def add(checks: list[dict], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def extract_section(text: str, start_heading: str, end_heading: str | None = None) -> str:
    """Return markdown section content between headings, or empty string.

    This deliberately stays simple and dependency-free.  It is a validation aid,
    not a Markdown parser.
    """
    start = text.find(start_heading)
    if start < 0:
        return ""
    start = text.find("\n", start)
    if start < 0:
        return ""
    if end_heading:
        end = text.find(end_heading, start)
        if end >= 0:
            return text[start:end]
    return text[start:]


def numeric_tokens(text: str) -> list[str]:
    return re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?![A-Za-z])", text)


def disclaims_live_reading(text: str) -> bool:
    """Accept bounded non-claims by meaning, not one frozen sentence.

    Historical drafts usually say ``no current/live reading is claimed``.
    Domain-specific successors may instead disclaim a live value, status,
    observation, or measurement.  Require the negation, the current/live
    qualifier, a reading-like noun, and claim language in the same sentence.
    """
    for sentence in re.split(r"[.!?]", text.lower()):
        if "current/live" not in sentence or "claim" not in sentence:
            continue
        if not re.search(r"\b(?:no|not)\b", sentence):
            continue
        if any(term in sentence for term in ("reading", "value", "status", "observation", "measurement")):
            return True
    return False


def packet_paths(root: Path) -> list[Path]:
    return sorted(root.glob("poems/P[0-9][0-9][0-9][0-9]/material/source_material_packet_*.json"))


def indexed_packet_paths(root: Path) -> set[str]:
    """Collect packet paths from all current and historical index surfaces.

    Rev0026 refactor: a poem can keep older material packets after a successor
    draft exists. The root poem index should point at the current packet, while
    draft-level metadata/draft_index preserve prior packets. Validation should
    require every packet to be indexed somewhere, not only in the root current
    head row.
    """
    paths: set[str] = set()
    for rel in ("registries/poem_index.json", "registries/draft_index.json"):
        p = root / rel
        if not p.exists():
            continue
        obj = load_json(p)
        records = obj.get("poems", []) if rel.endswith("poem_index.json") else obj.get("drafts", [])
        for rec in records:
            if rec.get("external_material_packet"):
                paths.add(rec["external_material_packet"])
            for old in rec.get("previous_external_material_packets", []) or []:
                paths.add(old)
    for meta_path in sorted(root.glob("poems/P[0-9][0-9][0-9][0-9]/metadata.json")):
        meta = load_json(meta_path)
        for dr in meta.get("drafts", []) or []:
            if dr.get("external_material_packet"):
                paths.add(dr["external_material_packet"])
        for rel in meta.get("verification_receipts", []) or []:
            if "source_material_packet_" in rel:
                paths.add(rel)
    for idx_path in sorted(root.glob("poems/P[0-9][0-9][0-9][0-9]/INDEX.json")):
        idx = load_json(idx_path)
        if idx.get("source_material_packet"):
            paths.add(idx["source_material_packet"])
        for rel in idx.get("source_material_packets", []) or []:
            paths.add(rel)
    return paths


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    packets = packet_paths(root)
    add(checks, "external_material_packets_present", len(packets) >= 1, f"count={len(packets)}")
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    proof = load_json(root / "registries/proof_status.json")
    current_head = surface.get("current_head") or proof.get("current_head") or proof.get("current_draft")
    current_revision = state.get("revision")
    source_ids = {s.get("source_id") for s in load_json(root / "registries/source_registry.json").get("sources", [])}
    source_receipts_obj = load_json(root / "registries/source_receipts.json")
    receipt_ids = {r.get("receipt_id") for r in source_receipts_obj.get("receipts", [])}
    receipt_claim_ids = {r.get("claim_id") for r in source_receipts_obj.get("receipts", [])}
    receipt_by_claim = {r.get("claim_id"): r for r in source_receipts_obj.get("receipts", []) if r.get("claim_id")}
    receipt_by_id = {r.get("receipt_id"): r for r in source_receipts_obj.get("receipts", []) if r.get("receipt_id")}
    snapshot_registry_path = root / "registries/source_snapshot_registry.json"
    snapshot_by_id = {}
    if snapshot_registry_path.exists():
        snapshot_by_id = {s.get("snapshot_id"): s for s in load_json(snapshot_registry_path).get("snapshots", []) if s.get("snapshot_id")}
    indexed_packets = indexed_packet_paths(root)
    packet_by_draft: dict[str, str] = {}

    for packet_path in packets:
        rel_packet = packet_path.relative_to(root).as_posix()
        try:
            packet = load_json(packet_path)
            add(checks, f"packet_parse:{rel_packet}", True)
        except Exception as exc:
            add(checks, f"packet_parse:{rel_packet}", False, str(exc))
            continue
        pid = packet.get("poem_id")
        draft_id = packet.get("draft_id")
        draft_rel = packet.get("draft_path") or f"poems/{pid}/draft_001.md"
        draft_path = root / draft_rel
        add(checks, f"packet_schema:{rel_packet}", packet.get("schema") == "llmpoetry-external-material-packet-v1", packet.get("schema"))
        add(checks, f"packet_indexed:{rel_packet}", rel_packet in indexed_packets, rel_packet)
        if draft_id:
            packet_by_draft[draft_id] = rel_packet
        if draft_id == current_head:
            posture = state.get("current_posture") if isinstance(state.get("current_posture"), dict) else {}
            review_rel = state.get("current_judgment")
            reviewed = None
            if posture.get("lineage_frozen") is True and isinstance(review_rel, str) and (root / review_rel).exists():
                try:
                    reviewed = load_json(root / review_rel)
                except Exception:
                    reviewed = None
            if isinstance(reviewed, dict) and reviewed.get("draft_id") == draft_id:
                target_revision = reviewed.get("target_created_revision") or reviewed.get("reviewed_revision")
                expected_hash = (reviewed.get("reviewed_hashes") or {}).get("packet_sha256")
                add(checks, f"current_head_packet_creation_revision:{draft_id}", packet.get("revision") == target_revision, {"packet": packet.get("revision"), "target": target_revision})
                add(checks, f"current_head_packet_frozen_hash:{draft_id}", isinstance(expected_hash, str) and sha256_file(packet_path) == expected_hash, expected_hash)
                add(checks, f"current_head_packet_review_later_turn:{draft_id}", int(reviewed.get("created_turn", 0)) > int(reviewed.get("target_created_turn", 0)), review_rel)
            else:
                add(checks, f"current_head_packet_revision:{draft_id}", packet.get("revision") == current_revision, packet.get("revision"))
        add(checks, f"packet_quality_claims_empty:{rel_packet}", packet.get("quality_claims") == [], str(packet.get("quality_claims")))
        add(checks, f"packet_non_claim_mentions_quality:{rel_packet}", "quality" in packet.get("non_claim", "").lower(), packet.get("non_claim", ""))
        add(checks, f"draft_exists:{draft_rel}", draft_path.exists(), draft_rel)
        if not draft_path.exists():
            continue
        draft = draft_path.read_text(encoding="utf-8", errors="replace")
        lower = draft.lower()
        add(checks, f"draft_contains_disclosure:{draft_id}", "disclosure:" in lower and "machine-drafted" in lower, draft_id)
        add(checks, f"draft_disclaims_live_reading:{draft_id}", disclaims_live_reading(lower), draft_id)
        for sid in packet.get("source_ids", []):
            add(checks, f"source_registered:{rel_packet}:{sid}", sid in source_ids, sid)
        facts = packet.get("facts", [])
        add(checks, f"facts_present:{rel_packet}", len(facts) >= 5, f"count={len(facts)}")

        # Rev0028 refactor: P0002 exposed a literary failure in the validator itself.
        # Requiring every source fact to survive literally in the poem rewards
        # fact-card drafts.  Current packets may therefore declare a
        # source_to_surface_policy where only a small set of anchor facts must
        # appear in the poem; the rest remain packet-context facts that still
        # need receipts/snapshots.
        policy = packet.get("source_to_surface_policy") or {}
        required_facts = [f for f in facts if f.get("required_in_draft", True)]
        context_facts = [f for f in facts if not f.get("required_in_draft", True)]
        if policy:
            add(checks, f"source_to_surface_policy_mode:{rel_packet}", policy.get("mode") == "anchor_context_compression", str(policy.get("mode")))
            max_required = policy.get("max_required_in_draft")
            min_context = policy.get("min_context_facts")
            if isinstance(max_required, int):
                add(checks, f"source_to_surface_required_fact_cap:{rel_packet}", len(required_facts) <= max_required, f"required={len(required_facts)} cap={max_required}")
            if isinstance(min_context, int):
                add(checks, f"source_to_surface_context_floor:{rel_packet}", len(context_facts) >= min_context, f"context={len(context_facts)} floor={min_context}")
            add(checks, f"source_to_surface_has_rationale:{rel_packet}", bool(policy.get("rationale")), str(policy.get("rationale", "")))

        # Rev0029: anchor/context compression alone can still hide a fact-card poem.
        # A current packet may add a surface_burden_policy that counts source load
        # only inside the poem body, excluding disclosure and packet surfaces.
        burden = packet.get("surface_burden_policy") or {}
        if burden:
            body_start = burden.get("poem_body_start_heading", "## Poem")
            disclosure_start = burden.get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            add(checks, f"surface_burden_mode:{rel_packet}", burden.get("mode") == "poem_body_source_burden_cap", str(burden.get("mode")))
            add(checks, f"surface_burden_body_present:{rel_packet}", bool(body.strip()), body_start)
            add(checks, f"surface_burden_disclosure_split:{rel_packet}", disclosure_start in draft and "disclosure:" not in body.lower(), disclosure_start)
            nums = numeric_tokens(body)
            digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
            nonblank_lines = [ln for ln in body.splitlines() if ln.strip()]
            max_nums = burden.get("max_body_numeric_tokens")
            max_digit_lines = burden.get("max_body_digit_lines")
            max_noaa = burden.get("max_body_noaa_mentions")
            min_lines = burden.get("min_body_nonblank_lines")
            if isinstance(max_nums, int):
                add(checks, f"surface_burden_numeric_token_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            if isinstance(max_digit_lines, int):
                add(checks, f"surface_burden_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            if isinstance(max_noaa, int):
                add(checks, f"surface_burden_noaa_mention_cap:{rel_packet}", body.lower().count("noaa") <= max_noaa, f"noaa={body.lower().count('noaa')} cap={max_noaa}")
            if isinstance(min_lines, int):
                add(checks, f"surface_burden_min_body_lines:{rel_packet}", len(nonblank_lines) >= min_lines, f"lines={len(nonblank_lines)} floor={min_lines}")
            banned_table_markers = ["Max Tide Date & Time", "Tidal Datum Analysis", "95% confidence interval", "date=latest retrieves"]
            hits = [m for m in banned_table_markers if m.lower() in body.lower()]
            add(checks, f"surface_burden_table_markers_absent:{rel_packet}", not hits, ", ".join(hits))
            add(checks, f"surface_burden_has_rationale:{rel_packet}", bool(burden.get("rationale")), str(burden.get("rationale", "")))


        # Rev0030: a successor draft can still regress by keeping all source
        # coverage while merely rearranging the fact card.  Current packets may
        # therefore declare a revision_delta_policy that compares the current
        # poem body to the previous head and blocks stale station-led/fact-row
        # surfaces.
        delta = packet.get("revision_delta_policy") or {}
        if delta:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            add(checks, f"revision_delta_mode:{rel_packet}", delta.get("mode") == "previous_head_surface_compression_delta", str(delta.get("mode")))
            prev_rel = delta.get("previous_draft_path")
            prev_path = root / prev_rel if prev_rel else None
            add(checks, f"revision_delta_previous_draft_exists:{rel_packet}", bool(prev_path and prev_path.exists()), str(prev_rel))
            if prev_path and prev_path.exists():
                prev_text = prev_path.read_text(encoding="utf-8", errors="replace")
                prev_body = extract_section(prev_text, body_start, disclosure_start)
                current_nums = numeric_tokens(body)
                prev_nums = numeric_tokens(prev_body)
                if delta.get("require_numeric_token_reduction"):
                    add(checks, f"revision_delta_numeric_reduction:{rel_packet}", len(current_nums) < len(prev_nums), f"current={len(current_nums)} previous={len(prev_nums)} current_tokens={current_nums} previous_tokens={prev_nums}")
                max_current = delta.get("max_current_body_numeric_tokens")
                if isinstance(max_current, int):
                    add(checks, f"revision_delta_current_numeric_cap:{rel_packet}", len(current_nums) <= max_current, f"numeric={len(current_nums)} cap={max_current}")
            first_nonblank = next((ln.strip() for ln in body.splitlines() if ln.strip()), "")
            forbidden_prefixes = delta.get("forbid_body_prefixes", []) or []
            bad_prefixes = [p for p in forbidden_prefixes if first_nonblank.startswith(p)]
            add(checks, f"revision_delta_forbidden_prefix_absent:{rel_packet}", not bad_prefixes, f"first={first_nonblank} bad={bad_prefixes}")
            forbidden_phrases = delta.get("forbidden_current_body_phrases", []) or []
            bad_phrases = [p for p in forbidden_phrases if p.lower() in body.lower()]
            add(checks, f"revision_delta_forbidden_body_phrases_absent:{rel_packet}", not bad_phrases, ", ".join(bad_phrases))
            add(checks, f"revision_delta_has_rationale:{rel_packet}", bool(delta.get("rationale")), str(delta.get("rationale", "")))


        # Rev0031: source compression can become too metaphor-ready.  Current
        # packets may therefore require a source-definition anchor: exact source
        # definition phrases must remain in the body while the prior conceit and
        # numeric hinge stay out.  This is still not a quality judgment; it only
        # blocks retreat from material definition into generic explanation.
        definition = packet.get("definition_anchor_policy") or {}
        if definition:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            add(checks, f"definition_anchor_mode:{rel_packet}", definition.get("mode") == "source_definition_anchor", str(definition.get("mode")))
            for phrase in definition.get("required_body_strings", []) or []:
                add(checks, f"definition_anchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = definition.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body.lower()]
            add(checks, f"definition_anchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            max_nums = definition.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"definition_anchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            snap_id = definition.get("source_snapshot_id")
            if snap_id:
                add(checks, f"definition_anchor_snapshot_registered:{rel_packet}", snap_id in snapshot_by_id, str(snap_id))
            add(checks, f"definition_anchor_has_rationale:{rel_packet}", bool(definition.get("rationale")), str(definition.get("rationale", "")))



        # Rev0032: the live-data gap is now material, not a footnote.
        # A current packet may require a local runtime-gap anchor so the poem
        # cannot pass by hiding failed current-source reach in disclosure only.
        runtime_gap = packet.get("runtime_gap_policy") or {}
        if runtime_gap:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            disclosure = extract_section(draft, disclosure_start, None)
            allowed_runtime_modes = {"local_runtime_gap_anchor", "local_runtime_gap_compressed_anchor", "local_runtime_gap_scene_subsurface"}
            add(checks, f"runtime_gap_mode:{rel_packet}", runtime_gap.get("mode") in allowed_runtime_modes, str(runtime_gap.get("mode")))
            for phrase in runtime_gap.get("required_body_strings", []) or []:
                add(checks, f"runtime_gap_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            for phrase in runtime_gap.get("required_disclosure_strings", []) or []:
                add(checks, f"runtime_gap_required_disclosure_string:{rel_packet}:{phrase}", phrase in disclosure, phrase)
            forbidden = runtime_gap.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body.lower()]
            add(checks, f"runtime_gap_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            local_facts = [f for f in facts if str(f.get("source_id", "")).startswith("LOCAL-")]
            add(checks, f"runtime_gap_local_fact_present:{rel_packet}", bool(local_facts), f"count={len(local_facts)}")
            snap_id = runtime_gap.get("local_runtime_snapshot_id")
            snap = snapshot_by_id.get(snap_id)
            add(checks, f"runtime_gap_snapshot_registered:{rel_packet}", snap is not None, str(snap_id))
            if snap:
                add(checks, f"runtime_gap_snapshot_kind:{rel_packet}", snap.get("capture_kind") == "local_runtime_attempt", str(snap.get("capture_kind")))
                # Historical runtime-gap packets keep their original local receipts,
                # but only the current-head packet's runtime snapshot should be
                # marked as supporting the current head.  Earlier revisions remain
                # valid history rather than being forced to masquerade as current.
                supports_current = (snap.get("supports_current_head") is True)
                add(checks, f"runtime_gap_snapshot_supports_current:{rel_packet}", draft_id != current_head or supports_current, str(snap.get("supports_current_head")))
            add(checks, f"runtime_gap_has_rationale:{rel_packet}", bool(runtime_gap.get("rationale")), str(runtime_gap.get("rationale", "")))

        # Rev0034: D009 solved infrastructure overexposure but still let the
        # poem narrate its own archival honesty (poem/file/proof/source-prose).
        # A current packet may therefore cap self-reference in the poem body
        # while requiring material/place terms to carry the disclosure load.
        self_ref = packet.get("self_reference_burden_policy") or {}
        if self_ref:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"self_reference_burden_mode:{rel_packet}", self_ref.get("mode") == "poem_body_self_reference_burden_cap", str(self_ref.get("mode")))
            count_terms = self_ref.get("count_terms", {}) or {}
            for term, cap in count_terms.items():
                if isinstance(cap, int):
                    count = body_lower.count(str(term).lower())
                    add(checks, f"self_reference_burden_term_cap:{rel_packet}:{term}", count <= cap, f"count={count} cap={cap}")
            forbidden = self_ref.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"self_reference_burden_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            for phrase in self_ref.get("required_body_strings", []) or []:
                add(checks, f"self_reference_burden_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            min_material_terms = self_ref.get("min_material_terms")
            if isinstance(min_material_terms, int):
                material_terms = self_ref.get("material_terms", []) or []
                hits = [t for t in material_terms if str(t).lower() in body_lower]
                add(checks, f"self_reference_burden_material_term_floor:{rel_packet}", len(hits) >= min_material_terms, f"hits={hits} floor={min_material_terms}")
            add(checks, f"self_reference_burden_has_rationale:{rel_packet}", bool(self_ref.get("rationale")), str(self_ref.get("rationale", "")))

        # Rev0042: D011 is allowed only as a fallback/subtraction draft under a
        # logged project-owner-delegated override. This policy verifies that the
        # new current body preserves the source/runtime hinge while cutting D010's
        # technical noun and terminal explanatory stanzas.
        fallback_sub = packet.get("fallback_subtraction_policy") or {}
        if fallback_sub:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            add(checks, f"fallback_subtraction_mode:{rel_packet}", fallback_sub.get("mode") == "owner_override_subtraction_fallback", str(fallback_sub.get("mode")))
            trigger = str(fallback_sub.get("trigger_record", ""))
            add(checks, f"fallback_subtraction_trigger_record:{rel_packet}", "HI-REV0042-OWNER-DELEGATED-OVERRIDE" in trigger, trigger)
            forbidden = fallback_sub.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body.lower()]
            add(checks, f"fallback_subtraction_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            for phrase in fallback_sub.get("required_body_strings", []) or []:
                add(checks, f"fallback_subtraction_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            max_words = fallback_sub.get("max_body_word_count")
            if isinstance(max_words, int):
                add(checks, f"fallback_subtraction_body_word_cap:{rel_packet}", len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", body)) <= max_words, f"words={len(re.findall(r'[A-Za-z0-9]+(?:[-\'][A-Za-z0-9]+)?', body))} cap={max_words}")
            max_lines = fallback_sub.get("max_body_nonblank_lines")
            if isinstance(max_lines, int):
                lines = [ln for ln in body.splitlines() if ln.strip()]
                add(checks, f"fallback_subtraction_body_line_cap:{rel_packet}", len(lines) <= max_lines, f"lines={len(lines)} cap={max_lines}")
            add(checks, f"fallback_subtraction_not_candidate_flag:{rel_packet}", fallback_sub.get("must_not_be_candidate") is True, str(fallback_sub.get("must_not_be_candidate")))
            add(checks, f"fallback_subtraction_has_rationale:{rel_packet}", bool(fallback_sub.get("rationale")), str(fallback_sub.get("rationale", "")))

        # Rev0043: D011 solved technical authority partly by subtracting it,
        # but drifted toward generic harbor realism. A successor packet can
        # require a route/place re-anchor from the benchmark sheet while still
        # keeping source tables out of the poem body.
        reanchor = packet.get("post_fallback_reanchor_policy") or {}
        if reanchor:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"post_fallback_reanchor_mode:{rel_packet}", reanchor.get("mode") == "route_specificity_rebound", str(reanchor.get("mode")))
            review_path = reanchor.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"post_fallback_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"post_fallback_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in reanchor.get("required_body_strings", []) or []:
                add(checks, f"post_fallback_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = reanchor.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"post_fallback_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            generic_terms = reanchor.get("generic_harbor_terms", []) or []
            max_generic = reanchor.get("max_generic_harbor_term_hits")
            if isinstance(max_generic, int):
                hits = [t for t in generic_terms if str(t).lower() in body_lower]
                add(checks, f"post_fallback_reanchor_generic_harbor_cap:{rel_packet}", len(hits) <= max_generic, f"hits={hits} cap={max_generic}")
            place_terms = reanchor.get("place_terms", []) or []
            min_place = reanchor.get("min_place_terms")
            if isinstance(min_place, int):
                hits = [t for t in place_terms if str(t).lower() in body_lower]
                add(checks, f"post_fallback_reanchor_place_term_floor:{rel_packet}", len(hits) >= min_place, f"hits={hits} floor={min_place}")
            max_words = reanchor.get("max_body_word_count")
            if isinstance(max_words, int):
                count = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", body))
                add(checks, f"post_fallback_reanchor_body_word_cap:{rel_packet}", count <= max_words, f"words={count} cap={max_words}")
            add(checks, f"post_fallback_reanchor_has_rationale:{rel_packet}", bool(reanchor.get("rationale")), str(reanchor.get("rationale", "")))

        # Rev0044: D012 repaired D011's generic harbor drift by adding route
        # specificity, but the route itself could become clever directions and
        # abstract closure.  A successor packet may therefore require a smaller
        # benchmark object anchor: disk / loading dock / guard house, with the
        # no-value hinge preserved and route-setpiece rhetoric capped.  This is
        # still not a poem-quality judgment; it only prevents a successor from
        # passing while losing the resistant object named in the source.
        object_reanchor = packet.get("benchmark_object_reanchor_policy") or {}
        if object_reanchor:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"benchmark_object_reanchor_mode:{rel_packet}", object_reanchor.get("mode") == "benchmark_object_reanchor", str(object_reanchor.get("mode")))
            review_path = object_reanchor.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"benchmark_object_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"benchmark_object_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in object_reanchor.get("required_body_strings", []) or []:
                add(checks, f"benchmark_object_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = object_reanchor.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"benchmark_object_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            object_terms = object_reanchor.get("object_terms", []) or []
            min_object_terms = object_reanchor.get("min_object_terms")
            if isinstance(min_object_terms, int):
                hits = [t for t in object_terms if str(t).lower() in body_lower]
                add(checks, f"benchmark_object_reanchor_object_term_floor:{rel_packet}", len(hits) >= min_object_terms, f"hits={hits} floor={min_object_terms}")
            abstract_terms = object_reanchor.get("abstract_closure_terms", []) or []
            max_abstract = object_reanchor.get("max_abstract_closure_term_hits")
            if isinstance(max_abstract, int):
                hits = [t for t in abstract_terms if str(t).lower() in body_lower]
                add(checks, f"benchmark_object_reanchor_abstract_term_cap:{rel_packet}", len(hits) <= max_abstract, f"hits={hits} cap={max_abstract}")
            max_words = object_reanchor.get("max_body_word_count")
            if isinstance(max_words, int):
                count = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", body))
                add(checks, f"benchmark_object_reanchor_body_word_cap:{rel_packet}", count <= max_words, f"words={count} cap={max_words}")
            add(checks, f"benchmark_object_reanchor_has_rationale:{rel_packet}", bool(object_reanchor.get("rationale")), str(object_reanchor.get("rationale", "")))


        # Rev0045: D013 found the benchmark object but closed as an abstract
        # thesis. A successor packet may allow a tiny numeric exception only
        # for the stamped primary benchmark name while blocking a return to
        # route lyric, datum-table display, or D013's conceptual closure. This
        # checks material-risk regression only; it does not judge poem quality.
        stamped = packet.get("stamped_mark_reanchor_policy") or {}
        if stamped:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"stamped_mark_reanchor_mode:{rel_packet}", stamped.get("mode") == "benchmark_stamped_mark_reanchor", str(stamped.get("mode")))
            review_path = stamped.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"stamped_mark_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"stamped_mark_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in stamped.get("required_body_strings", []) or []:
                add(checks, f"stamped_mark_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = stamped.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"stamped_mark_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            allowed = str(stamped.get("allowed_numeric_body_string", ""))
            nums = numeric_tokens(body.replace(allowed, "")) if allowed else numeric_tokens(body)
            add(checks, f"stamped_mark_reanchor_no_extra_numeric_tokens:{rel_packet}", not nums, f"extra_numeric={nums} allowed={allowed}")
            max_nums = stamped.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                all_nums = numeric_tokens(body)
                add(checks, f"stamped_mark_reanchor_numeric_cap:{rel_packet}", len(all_nums) <= max_nums, f"numeric={len(all_nums)} cap={max_nums} tokens={all_nums}")
            add(checks, f"stamped_mark_reanchor_has_rationale:{rel_packet}", bool(stamped.get("rationale")), str(stamped.get("rationale", "")))

        # Rev0046: D014 used the stamped mark precisely, but the pun/no-object
        # pressure could become too clever and self-sealing. A successor packet
        # may therefore re-anchor in the source contradiction that the mark for
        # water is fixed above ground and outside the water. This checks a
        # material regression boundary only; it does not judge poem quality.
        above_ground = packet.get("above_ground_reanchor_policy") or {}
        if above_ground:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"above_ground_reanchor_mode:{rel_packet}", above_ground.get("mode") == "benchmark_above_ground_reanchor", str(above_ground.get("mode")))
            review_path = above_ground.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"above_ground_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"above_ground_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in above_ground.get("required_body_strings", []) or []:
                add(checks, f"above_ground_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = above_ground.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"above_ground_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            max_nums = above_ground.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"above_ground_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            object_terms = above_ground.get("object_terms", []) or []
            min_object_terms = above_ground.get("min_object_terms")
            if isinstance(min_object_terms, int):
                hits = [t for t in object_terms if str(t).lower() in body_lower]
                add(checks, f"above_ground_reanchor_object_term_floor:{rel_packet}", len(hits) >= min_object_terms, f"hits={hits} floor={min_object_terms}")
            add(checks, f"above_ground_reanchor_has_rationale:{rel_packet}", bool(above_ground.get("rationale")), str(above_ground.get("rationale", "")))




        # Rev0047: D015 found the above-ground contradiction but turned it into
        # a thesis/aphorism. A successor packet may therefore re-anchor in the
        # benchmark sheet's dry corner-offset syntax: the water mark is found by
        # building and guard-house corners before it is found by water. This is
        # a regression guard only, not poem-quality validation.
        corner_offset = packet.get("corner_offset_reanchor_policy") or {}
        if corner_offset:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"corner_offset_reanchor_mode:{rel_packet}", corner_offset.get("mode") == "benchmark_corner_offset_reanchor", str(corner_offset.get("mode")))
            review_path = corner_offset.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"corner_offset_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"corner_offset_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in corner_offset.get("required_body_strings", []) or []:
                add(checks, f"corner_offset_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = corner_offset.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"corner_offset_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            max_nums = corner_offset.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"corner_offset_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            corner_terms = corner_offset.get("corner_terms", []) or []
            min_corner_terms = corner_offset.get("min_corner_terms")
            if isinstance(min_corner_terms, int):
                hits = [t for t in corner_terms if str(t).lower() in body_lower]
                add(checks, f"corner_offset_reanchor_corner_term_floor:{rel_packet}", len(hits) >= min_corner_terms, f"hits={hits} floor={min_corner_terms}")
            direction_words = corner_offset.get("direction_words", []) or []
            max_direction_words = corner_offset.get("max_direction_words")
            if isinstance(max_direction_words, int):
                hits = [t for t in direction_words if str(t).lower() in body_lower]
                add(checks, f"corner_offset_reanchor_direction_word_cap:{rel_packet}", len(hits) <= max_direction_words, f"hits={hits} cap={max_direction_words}")
            add(checks, f"corner_offset_reanchor_has_rationale:{rel_packet}", bool(corner_offset.get("rationale")), str(corner_offset.get("rationale", "")))


        # Rev0048: D016 made the corner-offset source active but too instructional.
        # Current packets may require a borrowed-corner reanchor that preserves
        # east/SW/corner facts while blocking directions/procedural language.
        borrowed = packet.get("borrowed_corner_reanchor_policy") or {}
        if borrowed:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"borrowed_corner_reanchor_mode:{rel_packet}", borrowed.get("mode") == "benchmark_borrowed_corner_reanchor", str(borrowed.get("mode")))
            review_path = borrowed.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"borrowed_corner_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"borrowed_corner_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in borrowed.get("required_body_strings", []) or []:
                add(checks, f"borrowed_corner_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = borrowed.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"borrowed_corner_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            max_nums = borrowed.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"borrowed_corner_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            borrowed_terms = borrowed.get("borrowed_terms", []) or []
            min_borrowed_terms = borrowed.get("min_borrowed_terms")
            if isinstance(min_borrowed_terms, int):
                hits = [t for t in borrowed_terms if str(t).lower() in body_lower]
                add(checks, f"borrowed_corner_reanchor_term_floor:{rel_packet}", len(hits) >= min_borrowed_terms, f"hits={hits} floor={min_borrowed_terms}")
            instruction_terms = borrowed.get("instruction_terms", []) or []
            max_instruction_terms = borrowed.get("max_instruction_terms")
            if isinstance(max_instruction_terms, int):
                hits = [t for t in instruction_terms if str(t).lower() in body_lower]
                add(checks, f"borrowed_corner_reanchor_instruction_cap:{rel_packet}", len(hits) <= max_instruction_terms, f"hits={hits} cap={max_instruction_terms}")
            max_words = borrowed.get("max_body_word_count")
            if isinstance(max_words, int):
                count = len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", body))
                add(checks, f"borrowed_corner_reanchor_body_word_cap:{rel_packet}", count <= max_words, f"words={count} cap={max_words}")
            add(checks, f"borrowed_corner_reanchor_has_rationale:{rel_packet}", bool(borrowed.get("rationale")), str(borrowed.get("rationale", "")))

        # Rev0049: D017 made benchmark location syntactically active but risked
        # turning the poem into a clean borrowed-corner conceit. A successor
        # packet may therefore re-anchor in the benchmark elevation table
        # while allowing only a bounded numeric table hinge. This is a
        # material regression guard only, not poem-quality validation.
        elevation = packet.get("benchmark_elevation_reanchor_policy") or {}
        if elevation:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"benchmark_elevation_reanchor_mode:{rel_packet}", elevation.get("mode") == "benchmark_elevation_table_reanchor", str(elevation.get("mode")))
            review_path = elevation.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"benchmark_elevation_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"benchmark_elevation_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in elevation.get("required_body_strings", []) or []:
                add(checks, f"benchmark_elevation_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = elevation.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"benchmark_elevation_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            scrubbed = body
            for allowed in elevation.get("allowed_numeric_body_strings", []) or []:
                scrubbed = scrubbed.replace(str(allowed), "")
            extra_nums = numeric_tokens(scrubbed)
            add(checks, f"benchmark_elevation_reanchor_no_extra_numeric_tokens:{rel_packet}", not extra_nums, f"extra_numeric={extra_nums}")
            max_nums = elevation.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"benchmark_elevation_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = elevation.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"benchmark_elevation_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = elevation.get("elevation_terms", []) or []
            min_terms = elevation.get("min_elevation_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"benchmark_elevation_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            corner_terms = elevation.get("corner_terms", []) or []
            max_corner_terms = elevation.get("max_corner_terms")
            if isinstance(max_corner_terms, int):
                hits = [t for t in corner_terms if str(t).lower() in body_lower]
                add(checks, f"benchmark_elevation_reanchor_corner_term_cap:{rel_packet}", len(hits) <= max_corner_terms, f"hits={hits} cap={max_corner_terms}")
            add(checks, f"benchmark_elevation_reanchor_has_rationale:{rel_packet}", bool(elevation.get("rationale")), str(elevation.get("rationale", "")))


        # Rev0050: D018 showed that even bounded official elevation numbers can
        # pull the poem back into a table demonstration. A current packet may
        # therefore declare an above_question_reanchor_policy that allows only
        # the stamped object number while requiring the official heights to move
        # into packet/disclosure context.
        aboveq = packet.get("above_question_reanchor_policy") or {}
        if aboveq:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"above_question_reanchor_mode:{rel_packet}", aboveq.get("mode") == "benchmark_above_question_reanchor", str(aboveq.get("mode")))
            review_path = aboveq.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"above_question_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"above_question_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in aboveq.get("required_body_strings", []) or []:
                add(checks, f"above_question_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = aboveq.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"above_question_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            scrubbed = body
            for allowed in aboveq.get("allowed_numeric_body_strings", []) or []:
                scrubbed = scrubbed.replace(str(allowed), "")
            extra_nums = numeric_tokens(scrubbed)
            add(checks, f"above_question_reanchor_no_extra_numeric_tokens:{rel_packet}", not extra_nums, f"extra_numeric={extra_nums}")
            max_nums = aboveq.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"above_question_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = aboveq.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"above_question_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = aboveq.get("above_question_terms", []) or []
            min_terms = aboveq.get("min_above_question_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"above_question_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            table_terms = aboveq.get("table_display_terms", []) or []
            max_table_terms = aboveq.get("max_table_display_terms")
            if isinstance(max_table_terms, int):
                hits = [t for t in table_terms if str(t).lower() in body_lower]
                add(checks, f"above_question_reanchor_table_display_cap:{rel_packet}", len(hits) <= max_table_terms, f"hits={hits} cap={max_table_terms}")
            add(checks, f"above_question_reanchor_has_rationale:{rel_packet}", bool(aboveq.get("rationale")), str(aboveq.get("rationale", "")))


        # Rev0051: D019 showed that removing the body-level elevation numbers can
        # over-smooth the source into abstraction. A current packet may therefore
        # require the named datum waters themselves to carry the difference while
        # exact official heights remain in packet/disclosure space.
        named = packet.get("named_datum_difference_policy") or {}
        if named:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"named_datum_difference_mode:{rel_packet}", named.get("mode") == "benchmark_named_datum_difference_reanchor", str(named.get("mode")))
            review_path = named.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"named_datum_difference_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"named_datum_difference_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in named.get("required_body_strings", []) or []:
                add(checks, f"named_datum_difference_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = named.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"named_datum_difference_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            scrubbed = body
            for allowed in named.get("allowed_numeric_body_strings", []) or []:
                scrubbed = scrubbed.replace(str(allowed), "")
            extra_nums = numeric_tokens(scrubbed)
            add(checks, f"named_datum_difference_no_extra_numeric_tokens:{rel_packet}", not extra_nums, f"extra_numeric={extra_nums}")
            max_nums = named.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"named_datum_difference_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = named.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"named_datum_difference_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = named.get("datum_terms", []) or []
            min_terms = named.get("min_datum_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"named_datum_difference_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            table_terms = named.get("table_display_terms", []) or []
            max_table_terms = named.get("max_table_display_terms")
            if isinstance(max_table_terms, int):
                hits = [t for t in table_terms if str(t).lower() in body_lower]
                add(checks, f"named_datum_difference_table_display_cap:{rel_packet}", len(hits) <= max_table_terms, f"hits={hits} cap={max_table_terms}")
            add(checks, f"named_datum_difference_has_rationale:{rel_packet}", bool(named.get("rationale")), str(named.get("rationale", "")))


        # Rev0052: D020 showed that named datum waters can restore source
        # resistance while still becoming a lesson. A current packet may instead
        # require a no-column-for-rain reanchor: official table columns stay
        # source-bound while the poem body tests the table's absence.
        raincol = packet.get("rain_column_reanchor_policy") or {}
        if raincol:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"rain_column_reanchor_mode:{rel_packet}", raincol.get("mode") == "benchmark_rain_column_reanchor", str(raincol.get("mode")))
            review_path = raincol.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"rain_column_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"rain_column_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in raincol.get("required_body_strings", []) or []:
                add(checks, f"rain_column_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = raincol.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"rain_column_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            scrubbed = body
            for allowed in raincol.get("allowed_numeric_body_strings", []) or []:
                scrubbed = scrubbed.replace(str(allowed), "")
            extra_nums = numeric_tokens(scrubbed)
            add(checks, f"rain_column_reanchor_no_extra_numeric_tokens:{rel_packet}", not extra_nums, f"extra_numeric={extra_nums}")
            max_nums = raincol.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"rain_column_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = raincol.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"rain_column_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = raincol.get("rain_column_terms", []) or []
            min_terms = raincol.get("min_rain_column_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"rain_column_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            datum_terms = raincol.get("datum_display_terms", []) or []
            max_datum_terms = raincol.get("max_datum_display_terms")
            if isinstance(max_datum_terms, int):
                hits = [t for t in datum_terms if str(t).lower() in body_lower]
                add(checks, f"rain_column_reanchor_datum_display_cap:{rel_packet}", len(hits) <= max_datum_terms, f"hits={hits} cap={max_datum_terms}")
            add(checks, f"rain_column_reanchor_has_rationale:{rel_packet}", bool(raincol.get("rationale")), str(raincol.get("rationale", "")))



        # Rev0053: D021's rain/no-column pressure solved D020's datum lesson
        # but softened the source into weather. A current packet may require a
        # stamping/designation reanchor: the NOAA table's own naming grammar must
        # carry the pressure while rain/weather terms are capped out of the body.
        stamping = packet.get("stamping_designation_reanchor_policy") or {}
        if stamping:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"stamping_designation_reanchor_mode:{rel_packet}", stamping.get("mode") == "benchmark_stamping_designation_reanchor", str(stamping.get("mode")))
            review_path = stamping.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"stamping_designation_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"stamping_designation_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in stamping.get("required_body_strings", []) or []:
                add(checks, f"stamping_designation_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = stamping.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"stamping_designation_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            scrubbed = body
            for allowed in stamping.get("allowed_numeric_body_strings", []) or []:
                scrubbed = scrubbed.replace(str(allowed), "")
            extra_nums = numeric_tokens(scrubbed)
            add(checks, f"stamping_designation_reanchor_no_extra_numeric_tokens:{rel_packet}", not extra_nums, f"extra_numeric={extra_nums}")
            max_nums = stamping.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                nums = numeric_tokens(body)
                add(checks, f"stamping_designation_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = stamping.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"stamping_designation_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = stamping.get("designation_terms", []) or []
            min_terms = stamping.get("min_designation_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"stamping_designation_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            rain_terms = stamping.get("rain_weather_terms", []) or []
            max_rain = stamping.get("max_rain_weather_terms")
            if isinstance(max_rain, int):
                hits = [t for t in rain_terms if str(t).lower() in body_lower]
                add(checks, f"stamping_designation_reanchor_rain_weather_cap:{rel_packet}", len(hits) <= max_rain, f"hits={hits} cap={max_rain}")
            add(checks, f"stamping_designation_reanchor_has_rationale:{rel_packet}", bool(stamping.get("rationale")), str(stamping.get("rationale", "")))

        # Rev0033: D008 exposed another failure mode: making the runtime
        # apparatus itself too legible can feel clever but inert.  A current
        # packet may therefore cap infrastructure diction in the poem body while
        # preserving the same local runtime receipt in disclosure/packet space.
        infra = packet.get("infrastructure_burden_policy") or {}
        if infra:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"infrastructure_burden_mode:{rel_packet}", infra.get("mode") == "runtime_gap_infrastructure_burden_cap", str(infra.get("mode")))
            count_terms = infra.get("count_terms", {}) or {}
            for term, cap in count_terms.items():
                if isinstance(cap, int):
                    count = body_lower.count(str(term).lower())
                    add(checks, f"infrastructure_burden_term_cap:{rel_packet}:{term}", count <= cap, f"count={count} cap={cap}")
            for phrase in infra.get("required_body_strings", []) or []:
                add(checks, f"infrastructure_burden_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = infra.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"infrastructure_burden_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            min_place_terms = infra.get("min_place_terms")
            if isinstance(min_place_terms, int):
                place_terms = infra.get("place_terms", []) or []
                hits = [t for t in place_terms if str(t).lower() in body_lower]
                add(checks, f"infrastructure_burden_place_term_floor:{rel_packet}", len(hits) >= min_place_terms, f"hits={hits} floor={min_place_terms}")
            add(checks, f"infrastructure_burden_has_rationale:{rel_packet}", bool(infra.get("rationale")), str(infra.get("rationale", "")))



        blank = packet.get("blank_stamping_reanchor_policy") or {}
        if blank:
            add(checks, f"blank_stamping_reanchor_mode:{rel_packet}", blank.get("mode") == "benchmark_blank_stamping_reanchor", str(blank.get("mode")))
            review_path = blank.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"blank_stamping_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"blank_stamping_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in blank.get("required_body_strings", []) or []:
                add(checks, f"blank_stamping_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = blank.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"blank_stamping_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            allowed = set(blank.get("allowed_numeric_body_strings", []) or [])
            nums = re.findall(r"\b\d+(?:\.\d+)?\b", body)
            allowed_nums = set()
            for allowed_phrase in allowed:
                allowed_nums.update(re.findall(r"\b\d+(?:\.\d+)?\b", str(allowed_phrase)))
            extra_nums = [n for n in nums if n not in allowed_nums]
            add(checks, f"blank_stamping_reanchor_no_extra_numeric_tokens:{rel_packet}", not extra_nums, f"extra_numeric={extra_nums}")
            max_nums = blank.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                add(checks, f"blank_stamping_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
            max_digit_lines = blank.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                add(checks, f"blank_stamping_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = blank.get("blank_stamping_terms", []) or []
            min_terms = blank.get("min_blank_stamping_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"blank_stamping_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            max_weather = blank.get("max_rain_weather_terms")
            if isinstance(max_weather, int):
                hits = [t for t in (blank.get("rain_weather_terms", []) or []) if str(t).lower() in body_lower]
                add(checks, f"blank_stamping_reanchor_rain_weather_cap:{rel_packet}", len(hits) <= max_weather, f"hits={hits} cap={max_weather}")
            add(checks, f"blank_stamping_reanchor_has_rationale:{rel_packet}", bool(blank.get("rationale")), str(blank.get("rationale", "")))


        fifth = packet.get("fifth_step_reanchor_policy") or {}
        if fifth:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"fifth_step_reanchor_mode:{rel_packet}", fifth.get("mode") == "benchmark_fifth_step_reanchor", str(fifth.get("mode")))
            review_path = fifth.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"fifth_step_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"fifth_step_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in fifth.get("required_body_strings", []) or []:
                add(checks, f"fifth_step_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = fifth.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"fifth_step_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            nums = numeric_tokens(body)
            max_nums = fifth.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                add(checks, f"fifth_step_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = fifth.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"fifth_step_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = fifth.get("fifth_step_terms", []) or []
            min_terms = fifth.get("min_fifth_step_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"fifth_step_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            designation_terms = fifth.get("designation_terms", []) or []
            max_designation = fifth.get("max_designation_terms")
            if isinstance(max_designation, int):
                hits = [t for t in designation_terms if str(t).lower() in body_lower]
                add(checks, f"fifth_step_reanchor_designation_term_cap:{rel_packet}", len(hits) <= max_designation, f"hits={hits} cap={max_designation}")
            add(checks, f"fifth_step_reanchor_has_rationale:{rel_packet}", bool(fifth.get("rationale")), str(fifth.get("rationale", "")))


        shoe = packet.get("shoe_passage_reanchor_policy") or {}
        if shoe:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"shoe_passage_reanchor_mode:{rel_packet}", shoe.get("mode") == "benchmark_shoe_passage_reanchor", str(shoe.get("mode")))
            review_path = shoe.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"shoe_passage_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"shoe_passage_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in shoe.get("required_body_strings", []) or []:
                add(checks, f"shoe_passage_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = shoe.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"shoe_passage_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            nums = numeric_tokens(body)
            max_nums = shoe.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                add(checks, f"shoe_passage_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = shoe.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"shoe_passage_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = shoe.get("shoe_passage_terms", []) or []
            min_terms = shoe.get("min_shoe_passage_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"shoe_passage_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            designation_terms = shoe.get("designation_terms", []) or []
            max_designation = shoe.get("max_designation_terms")
            if isinstance(max_designation, int):
                hits = [t for t in designation_terms if str(t).lower() in body_lower]
                add(checks, f"shoe_passage_reanchor_designation_term_cap:{rel_packet}", len(hits) <= max_designation, f"hits={hits} cap={max_designation}")
            add(checks, f"shoe_passage_reanchor_has_rationale:{rel_packet}", bool(shoe.get("rationale")), str(shoe.get("rationale", "")))


        horiz = packet.get("horizontal_bolt_reanchor_policy") or {}
        if horiz:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"horizontal_bolt_reanchor_mode:{rel_packet}", horiz.get("mode") == "benchmark_horizontal_bolt_reanchor", str(horiz.get("mode")))
            review_path = horiz.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"horizontal_bolt_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"horizontal_bolt_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in horiz.get("required_body_strings", []) or []:
                add(checks, f"horizontal_bolt_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = horiz.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"horizontal_bolt_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            nums = numeric_tokens(body)
            max_nums = horiz.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                add(checks, f"horizontal_bolt_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = horiz.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"horizontal_bolt_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = horiz.get("horizontal_bolt_terms", []) or []
            min_terms = horiz.get("min_horizontal_bolt_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"horizontal_bolt_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            designation_terms = horiz.get("designation_terms", []) or []
            max_designation = horiz.get("max_designation_terms")
            if isinstance(max_designation, int):
                hits = [t for t in designation_terms if str(t).lower() in body_lower]
                add(checks, f"horizontal_bolt_reanchor_designation_term_cap:{rel_packet}", len(hits) <= max_designation, f"hits={hits} cap={max_designation}")
            add(checks, f"horizontal_bolt_reanchor_has_rationale:{rel_packet}", bool(horiz.get("rationale")), str(horiz.get("rationale", "")))


        northcurb = packet.get("north_curb_reanchor_policy") or {}
        if northcurb:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"north_curb_reanchor_mode:{rel_packet}", northcurb.get("mode") == "benchmark_north_curb_reanchor", str(northcurb.get("mode")))
            review_path = northcurb.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"north_curb_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"north_curb_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in northcurb.get("required_body_strings", []) or []:
                add(checks, f"north_curb_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = northcurb.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"north_curb_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            nums = numeric_tokens(body)
            max_nums = northcurb.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                add(checks, f"north_curb_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = northcurb.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"north_curb_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = northcurb.get("north_curb_terms", []) or []
            min_terms = northcurb.get("min_north_curb_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"north_curb_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            designation_terms = northcurb.get("designation_terms", []) or []
            max_designation = northcurb.get("max_designation_terms")
            if isinstance(max_designation, int):
                hits = [t for t in designation_terms if str(t).lower() in body_lower]
                add(checks, f"north_curb_reanchor_designation_term_cap:{rel_packet}", len(hits) <= max_designation, f"hits={hits} cap={max_designation}")
            add(checks, f"north_curb_reanchor_has_rationale:{rel_packet}", bool(northcurb.get("rationale")), str(northcurb.get("rationale", "")))


        current_reanchor = packet.get("current_reanchor_policy") or {}
        if current_reanchor:
            body_start = (packet.get("surface_burden_policy") or {}).get("poem_body_start_heading", "## Poem")
            disclosure_start = (packet.get("surface_burden_policy") or {}).get("disclosure_start_heading", "## Disclosure")
            body = extract_section(draft, body_start, disclosure_start)
            body_lower = body.lower()
            add(checks, f"current_reanchor_mode:{rel_packet}", current_reanchor.get("mode") == "generic_current_reanchor", str(current_reanchor.get("mode")))
            add(checks, f"current_reanchor_policy_id_present:{rel_packet}", bool(current_reanchor.get("policy_id")), str(current_reanchor.get("policy_id", "")))
            review_path = current_reanchor.get("requires_prior_cold_review")
            if review_path:
                rp = root / review_path
                add(checks, f"current_reanchor_review_exists:{rel_packet}", rp.exists(), review_path)
                if rp.exists():
                    rtxt = rp.read_text(encoding="utf-8", errors="replace")
                    add(checks, f"current_reanchor_review_verdict:{rel_packet}", "revise_not_promote" in rtxt, review_path)
            for phrase in current_reanchor.get("required_body_strings", []) or []:
                add(checks, f"current_reanchor_required_body_string:{rel_packet}:{phrase}", phrase in body, phrase)
            forbidden = current_reanchor.get("forbidden_body_strings", []) or []
            bad = [phrase for phrase in forbidden if phrase.lower() in body_lower]
            add(checks, f"current_reanchor_forbidden_body_strings_absent:{rel_packet}", not bad, ", ".join(bad))
            nums = numeric_tokens(body)
            max_nums = current_reanchor.get("max_body_numeric_tokens")
            if isinstance(max_nums, int):
                add(checks, f"current_reanchor_numeric_cap:{rel_packet}", len(nums) <= max_nums, f"numeric={len(nums)} cap={max_nums} tokens={nums}")
            max_digit_lines = current_reanchor.get("max_body_digit_lines")
            if isinstance(max_digit_lines, int):
                digit_lines = [ln for ln in body.splitlines() if re.search(r"\d", ln)]
                add(checks, f"current_reanchor_digit_line_cap:{rel_packet}", len(digit_lines) <= max_digit_lines, f"digit_lines={len(digit_lines)} cap={max_digit_lines}")
            terms = current_reanchor.get("focus_terms", []) or []
            min_terms = current_reanchor.get("min_focus_terms")
            if isinstance(min_terms, int):
                hits = [t for t in terms if str(t).lower() in body_lower]
                add(checks, f"current_reanchor_term_floor:{rel_packet}", len(hits) >= min_terms, f"hits={hits} floor={min_terms}")
            capped = current_reanchor.get("capped_terms", []) or []
            max_capped = current_reanchor.get("max_capped_terms")
            if isinstance(max_capped, int):
                hits = [t for t in capped if str(t).lower() in body_lower]
                add(checks, f"current_reanchor_capped_term_cap:{rel_packet}", len(hits) <= max_capped, f"hits={hits} cap={max_capped}")
            add(checks, f"current_reanchor_has_rationale:{rel_packet}", bool(current_reanchor.get("rationale")), str(current_reanchor.get("rationale", "")))

        for fact in facts:
            fid = fact.get("fact_id", "UNKNOWN")
            exact = fact.get("draft_exact_string")
            required_in_draft = fact.get("required_in_draft", True)
            visibility = fact.get("fact_visibility") or ("draft_anchor" if required_in_draft else "packet_context")
            add(checks, f"fact_visibility_known:{draft_id}:{fid}", visibility in {"draft_anchor", "packet_context", "disclosure_anchor"}, str(visibility))
            if required_in_draft:
                add(checks, f"fact_in_draft:{draft_id}:{fid}", bool(exact and exact in draft), str(exact))
            sid = fact.get("source_id")
            add(checks, f"fact_source_registered:{draft_id}:{fid}", sid in source_ids, str(sid))
            cid = fact.get("claim_id")
            rid = fact.get("source_receipt_id")
            add(checks, f"fact_has_source_receipt:{draft_id}:{fid}", cid in receipt_claim_ids or rid in receipt_ids, str(cid or rid))
            if draft_id == current_head:
                snap_id = fact.get("source_snapshot_id")
                add(checks, f"current_fact_has_snapshot:{draft_id}:{fid}", bool(snap_id), str(snap_id))
                snap = snapshot_by_id.get(snap_id)
                add(checks, f"current_fact_snapshot_registered:{draft_id}:{fid}", snap is not None, str(snap_id))
                if snap:
                    add(checks, f"current_fact_snapshot_source_matches:{draft_id}:{fid}", snap.get("source_id") == sid, f"fact={sid} snapshot={snap.get('source_id')}")
                receipt = receipt_by_claim.get(cid) or receipt_by_id.get(rid)
                if receipt:
                    add(checks, f"current_fact_receipt_snapshot_matches:{draft_id}:{fid}", receipt.get("source_snapshot_id") == snap_id, f"receipt={receipt.get('source_snapshot_id')} fact={snap_id}")
        forbidden = packet.get("diction_firewall", {}).get("forbidden_terms", [])
        hits = []
        for term in forbidden:
            pattern = WORD_BOUNDARY.format(term=re.escape(term.lower()))
            if re.search(pattern, lower):
                hits.append(term)
        add(checks, f"house_codework_terms_absent:{draft_id}", not hits, ", ".join(hits))
        required_phrases = packet.get("diction_firewall", {}).get("required_counter_pressure", [])
        for phrase in required_phrases:
            add(checks, f"counter_pressure_present:{draft_id}:{phrase}", phrase.lower() in lower, phrase)

    add(checks, "current_head_has_external_material_packet", bool(current_head and current_head in packet_by_draft), str(current_head))
    if current_head and current_head in packet_by_draft:
        add(checks, "current_head_packet_indexed", packet_by_draft[current_head] in indexed_packets, packet_by_draft[current_head])
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    checks = run(Path(args.root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
