#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
CREATED_AT = "2026-06-16T11:42:00Z"

try:
    from jsonschema import Draft202012Validator
except Exception:
    Draft202012Validator = None


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def load_mod(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


ingress_mod = load_mod("prepare_live_receipt_late_change_ingress_record", "tools/prepare_live_receipt_late_change_ingress_record.py")
rollback_mod = load_mod("prepare_live_receipt_publication_rollback_adjudication", "tools/prepare_live_receipt_publication_rollback_adjudication.py")

base_ref = f"examples/live-receipt-publication-rollback-adjudication-{REV}-zero-floor-stayed.json"
base = load(base_ref)

no_signal = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-no-signal",
    created_at=CREATED_AT,
    revision=REV,
)
if no_signal["decision"]["late_change_state"] != "monitoring-no-signal":
    raise SystemExit("no-signal ingress did not remain monitoring-only")
if no_signal["decision"]["may_publish_or_continue_snapshot"] is not False or no_signal["no_direct_floor_effect"] is not True:
    raise SystemExit("no-signal ingress acquired publication/floor effect")

live_revocation = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-live-revocation",
    created_at=CREATED_AT,
    revision=REV,
    signal_type="revocation",
    source_actor_class="counterparty",
    source_identity_ref="org:external-counterparty-a",
    target_ref=base_ref,
    nonhost_retention_ref="nonhost-vault:late-signal-a:sha256:" + "a" * 64,
    public_summary_ref="failed-gate-public-summary:late-revocation-a",
    signal_artifact="revocation says the receipt is withdrawn",
    supersedes_or_revokes_refs=[base_ref],
    signature_or_contact_channel_captured=True,
    independent_timestamp_present=True,
)
if live_revocation["decision"]["late_change_state"] != "opened-publication-rollback-required":
    raise SystemExit("live revocation did not open publication rollback")
if live_revocation["publication_freeze_locks"]["may_continue_reliance_from_ingress"] is not False:
    raise SystemExit("late-change ingress allowed reliance continuation")

blocked_retention = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-unretained",
    created_at=CREATED_AT,
    revision=REV,
    signal_type="challenge",
    source_actor_class="auditor",
    source_identity_ref="auditor:external",
    public_summary_ref="failed-gate-public-summary:late-challenge",
    signature_or_contact_channel_captured=True,
    independent_timestamp_present=True,
)
if blocked_retention["decision"]["late_change_state"] != "blocked-unretained-signal":
    raise SystemExit("unretained late signal did not block")

blocked_private = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-private-leak",
    created_at=CREATED_AT,
    revision=REV,
    signal_type="hash-mismatch",
    source_actor_class="verifier",
    source_identity_ref="verifier:external",
    nonhost_retention_ref="nonhost-vault:hash-mismatch:sha256:" + "b" * 64,
    public_summary_ref="private-vault://do-not-publish/raw-hash-mismatch",
    signature_or_contact_channel_captured=True,
    independent_timestamp_present=True,
    private_locator_leak=True,
)
if blocked_private["decision"]["late_change_state"] != "blocked-private-material-in-public-ingress":
    raise SystemExit("private locator leak did not block")

blocked_supersession = ingress_mod.build(
    publication_adjudication=base,
    publication_adjudication_ref=base_ref,
    receipt_id=f"{REV}-audit-unrouted-supersession",
    created_at=CREATED_AT,
    revision=REV,
    signal_type="supersession",
    source_actor_class="counterparty",
    source_identity_ref="org:external-counterparty-b",
    nonhost_retention_ref="nonhost-vault:supersession:sha256:" + "c" * 64,
    public_summary_ref="failed-gate-public-summary:supersession",
    signature_or_contact_channel_captured=True,
    independent_timestamp_present=True,
    route_supersession=False,
)
if blocked_supersession["decision"]["late_change_state"] != "blocked-supersession-unrouted":
    raise SystemExit("unrouted supersession did not block")

if Draft202012Validator is not None:
    schema = load("schemas/live-receipt-late-change-ingress-record.schema.json")
    Draft202012Validator.check_schema(schema)
    for label, obj in [("no_signal", no_signal), ("live_revocation", live_revocation), ("blocked_retention", blocked_retention), ("blocked_private", blocked_private), ("blocked_supersession", blocked_supersession)]:
        errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: list(e.path))
        if errors:
            raise SystemExit(f"{label} ingress fails schema: {errors[0].message}")

# The publication rollback adjudicator must block an unresolved live late-change ingress.
blocked_publication = rollback_mod.build(
    recompute_receipt=load(base["linked_floor_recompute_receipt_ref"]),
    recompute_receipt_ref=base["linked_floor_recompute_receipt_ref"],
    snapshot=load(base["linked_computed_snapshot_ref"]),
    snapshot_ref=base["linked_computed_snapshot_ref"],
    snapshot_hash=base["computed_snapshot_sha256"],
    challenges=[],
    challenge_refs=[],
    signal_ingresses=[live_revocation],
    signal_refs=["embedded:audit-live-revocation"],
    receipt_id=f"{REV}-audit-signal-blocks-publication",
    created_at=CREATED_AT,
    revision=REV,
)
if blocked_publication["decision"]["publication_adjudication_state"] != "blocked-late-change-ingress-open":
    raise SystemExit("publication rollback adjudication did not block unresolved late-change ingress")

print("audit_live_receipt_late_change_ingress_record: OK")
