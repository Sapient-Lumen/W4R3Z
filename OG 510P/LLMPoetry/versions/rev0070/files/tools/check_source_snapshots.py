#!/usr/bin/env python3
"""Validate lightweight source snapshots for the current external-material head.

This gate prevents the P0002 source layer from becoming receipt theater: every
current-head fact that claims a source snapshot must point to an existing,
hashed snapshot file and a registered source. It does not judge poem quality and
it does not pretend that excerpt snapshots are full archival captures.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


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


def declares_capture_limit(text: str) -> bool:
    """Recognize an explicit bounded-excerpt limit without magic wording."""
    lower = " ".join(text.lower().split())
    return any(marker in lower for marker in (
        "not a full",
        "not complete",
        "not a complete",
        "bounded source note",
        "bounded documentation note",
        "bounded excerpt",
    ))


def declares_quality_limit(text: str) -> bool:
    """Require quality language to sit inside an explicit negated non-claim."""
    lower = " ".join(text.lower().split())
    return "quality" in lower and any(marker in lower for marker in ("not ", "no ", "does not "))


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    registry_path = root / "registries/source_snapshot_registry.json"
    add(checks, "source_snapshot_registry_present", registry_path.exists(), registry_path.as_posix())
    if not registry_path.exists():
        return checks

    try:
        registry = load_json(registry_path)
        add(checks, "source_snapshot_registry_parse", True)
    except Exception as exc:
        add(checks, "source_snapshot_registry_parse", False, str(exc))
        return checks

    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    proof = load_json(root / "registries/proof_status.json")
    source_registry = load_json(root / "registries/source_registry.json")
    source_receipts = load_json(root / "registries/source_receipts.json")
    source_ids = {s.get("source_id") for s in source_registry.get("sources", [])}
    receipt_by_claim = {r.get("claim_id"): r for r in source_receipts.get("receipts", []) if r.get("claim_id")}
    receipt_by_id = {r.get("receipt_id"): r for r in source_receipts.get("receipts", []) if r.get("receipt_id")}

    add(checks, "source_snapshot_schema", registry.get("schema") == "llmpoetry-source-snapshot-registry-v1", registry.get("schema"))
    add(checks, "source_snapshot_revision_matches_state", registry.get("revision") == state.get("revision"), registry.get("revision"))
    current_head = surface.get("current_head") or proof.get("current_head") or proof.get("current_draft")
    add(checks, "source_snapshot_current_head_matches_surface", registry.get("current_head") == current_head, f"registry={registry.get('current_head')} surface={current_head}")
    packet_rel = registry.get("current_head_packet")
    packet_path = root / packet_rel if packet_rel else None
    add(checks, "source_snapshot_current_packet_present", bool(packet_rel and packet_path and packet_path.exists()), str(packet_rel))
    registry_non_claim = registry.get("non_claim", "")
    add(
        checks,
        "source_snapshot_non_claim_limits_capture",
        declares_capture_limit(registry_non_claim) and declares_quality_limit(registry_non_claim),
        registry_non_claim,
    )

    snapshots = registry.get("snapshots", [])
    add(checks, "source_snapshots_present", len(snapshots) >= 1, f"count={len(snapshots)}")
    snapshot_ids = [s.get("snapshot_id") for s in snapshots]
    add(checks, "source_snapshot_ids_unique", len(snapshot_ids) == len(set(snapshot_ids)), f"count={len(snapshot_ids)} unique={len(set(snapshot_ids))}")
    by_id = {s.get("snapshot_id"): s for s in snapshots if s.get("snapshot_id")}

    allowed_kinds = {"source_excerpt", "local_runtime_attempt", "api_response", "wacz_capture", "screenshot", "manual_transcription_excerpt"}
    for snap in snapshots:
        sid = snap.get("snapshot_id", "UNKNOWN")
        src = snap.get("source_id")
        rel = snap.get("path")
        path = root / rel if rel else None
        add(checks, f"snapshot_source_registered:{sid}", src in source_ids, str(src))
        add(checks, f"snapshot_path_exists:{sid}", bool(path and path.exists()), str(rel))
        add(checks, f"snapshot_has_capture_time:{sid}", bool(snap.get("captured_at")), str(snap.get("captured_at")))
        add(checks, f"snapshot_has_evidence_ref:{sid}", bool(snap.get("evidence_ref")), str(snap.get("evidence_ref")))
        add(checks, f"snapshot_capture_kind_known:{sid}", snap.get("capture_kind") in allowed_kinds, str(snap.get("capture_kind")))
        if path and path.exists():
            add(checks, f"snapshot_sha256_matches:{sid}", sha256_file(path) == snap.get("sha256"), str(rel))
            text = path.read_text(encoding="utf-8", errors="replace")
            if snap.get("capture_kind") == "source_excerpt":
                add(checks, f"source_excerpt_declares_limit:{sid}", declares_capture_limit(text), str(rel))
            if snap.get("capture_kind") == "local_runtime_attempt":
                add(checks, f"local_attempt_nonclaim:{sid}", "not noaa data" in text.lower() and "not inferred" in text.lower(), str(rel))

    if not (packet_path and packet_path.exists()):
        return checks
    try:
        packet = load_json(packet_path)
        add(checks, "source_snapshot_current_packet_parse", True)
    except Exception as exc:
        add(checks, "source_snapshot_current_packet_parse", False, str(exc))
        return checks

    add(checks, "current_packet_matches_current_head", packet.get("draft_id") == current_head, f"packet={packet.get('draft_id')} current={current_head}")
    packet_source_ids = set(packet.get("source_ids", []))
    snapshot_source_ids = {s.get("source_id") for s in snapshots if s.get("supports_current_head") is True}
    missing_packet_sources = sorted(packet_source_ids - snapshot_source_ids)
    add(checks, "current_packet_sources_have_snapshots", not missing_packet_sources, f"missing={missing_packet_sources}")

    facts = packet.get("facts", [])
    current_fact_snapshot_ids = {f.get("source_snapshot_id") for f in facts if f.get("source_snapshot_id")}
    current_support_snapshot_ids = {s.get("snapshot_id") for s in snapshots if s.get("supports_current_head") is True}
    add(checks, "source_snapshot_current_support_exact_current_facts", current_support_snapshot_ids == current_fact_snapshot_ids, f"support={sorted(current_support_snapshot_ids)} facts={sorted(current_fact_snapshot_ids)}")

    anchor_facts = [f for f in facts if f.get("required_in_draft", True)]
    context_facts = [f for f in facts if not f.get("required_in_draft", True)]
    add(checks, "current_packet_facts_present", len(facts) >= 1, f"count={len(facts)}")
    add(checks, "current_packet_anchor_facts_present", len(anchor_facts) >= 1, f"count={len(anchor_facts)}")

    # Rev0028: snapshot coverage follows all current-head packet facts, not only
    # facts printed literally in the poem.  This lets the poem compress the
    # source table while the packet remains auditable.
    policy = packet.get("source_to_surface_policy") or {}
    if policy:
        add(checks, "source_to_surface_policy_seen_by_snapshot_gate", policy.get("mode") == "anchor_context_compression", str(policy.get("mode")))
        add(checks, "source_to_surface_context_facts_have_snapshot_scope", len(context_facts) >= policy.get("min_context_facts", 0), f"context={len(context_facts)}")

    for fact in facts:
        fid = fact.get("fact_id", "UNKNOWN")
        visibility = fact.get("fact_visibility") or ("draft_anchor" if fact.get("required_in_draft", True) else "packet_context")
        add(checks, f"fact_visibility_known:{fid}", visibility in {"draft_anchor", "packet_context", "disclosure_anchor"}, str(visibility))
        snap_id = fact.get("source_snapshot_id")
        add(checks, f"fact_has_source_snapshot:{fid}", bool(snap_id), str(snap_id))
        snap = by_id.get(snap_id)
        add(checks, f"fact_snapshot_registered:{fid}", snap is not None, str(snap_id))
        if snap:
            add(checks, f"fact_snapshot_supports_current_head:{fid}", snap.get("supports_current_head") is True, str(snap_id))
            add(checks, f"fact_source_matches_snapshot:{fid}", fact.get("source_id") == snap.get("source_id"), f"fact={fact.get('source_id')} snap={snap.get('source_id')}")
        claim_id = fact.get("claim_id")
        receipt = receipt_by_claim.get(claim_id) or receipt_by_id.get(fact.get("source_receipt_id"))
        add(checks, f"fact_receipt_present:{fid}", receipt is not None, str(claim_id or fact.get("source_receipt_id")))
        if receipt:
            add(checks, f"fact_receipt_snapshot_matches:{fid}", receipt.get("source_snapshot_id") == snap_id, f"receipt={receipt.get('source_snapshot_id')} fact={snap_id}")
            add(checks, f"fact_receipt_source_matches:{fid}", receipt.get("source_id") == fact.get("source_id"), f"receipt={receipt.get('source_id')} fact={fact.get('source_id')}")
            add(checks, f"fact_receipt_required_flag_matches:{fid}", receipt.get("required_in_draft") == fact.get("required_in_draft"), f"receipt={receipt.get('required_in_draft')} fact={fact.get('required_in_draft')}")
            add(checks, f"fact_receipt_visibility_matches:{fid}", receipt.get("fact_visibility") == visibility, f"receipt={receipt.get('fact_visibility')} fact={visibility}")
            add(checks, f"fact_receipt_draft_exact_matches:{fid}", receipt.get("draft_exact_string") == fact.get("draft_exact_string"), f"receipt={receipt.get('draft_exact_string')} fact={fact.get('draft_exact_string')}")

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
