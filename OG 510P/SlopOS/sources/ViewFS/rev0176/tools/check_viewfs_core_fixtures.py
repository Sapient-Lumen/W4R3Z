#!/usr/bin/env python3
"""Deterministic checker for the ViewFS core v0 fixture corpus.

This is intentionally not a filesystem emulator. It is a small executable
anti-collapse model: paths, digests, refs, receipts, prompts, semantic cards,
restore tokens, stale bases, shell cards, delegation ledgers, and clicks may
select or explain things, but they cannot become authority unless a fixture
names the current live carrier and the cut that admits the operation.
"""
from __future__ import annotations

import json
import posixpath
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "viewfs-core-v0"
from fixture_schema import RECORD_KEYS, SCHEMA, TOP_KEYS


class FixtureError(Exception):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FixtureError(message)



def require_string(value: Any, context: str) -> str:
    require(isinstance(value, str) and value, f"{context} must be a non-empty string")
    return value


def time_reached(now: Any, bound: Any, context: str) -> bool:
    require(isinstance(now, str) and isinstance(bound, str), f"{context} needs ISO-like string times")
    # Fixtures use fixed-width UTC ISO strings, so lexical order is deterministic.
    return now >= bound


def as_number(value: Any, context: str) -> float:
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{context} must be numeric")
    return float(value)

def as_list(value: Any, context: str) -> list[Any]:
    require(isinstance(value, list), f"{context} must be a list")
    return value


def string_set(value: Any, context: str) -> set[str]:
    items = as_list(value, context)
    require(all(isinstance(i, str) for i in items), f"{context} entries must be strings")
    return set(items)


def index(records: dict[str, list[dict[str, Any]]], family: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in records.get(family, []):
        require(isinstance(item, dict), f"{family}: items must be objects")
        ident = item.get("id")
        require(isinstance(ident, str) and ident, f"{family}: item missing stable id")
        require(ident not in result, f"{family}: duplicate id {ident}")
        result[ident] = item
    return result


def normalize_under(root: str, relpath: str) -> str | None:
    require(root.startswith("/"), "compat root must be absolute")
    require(not relpath.startswith("/"), "fixture path must be relative to the compat root")
    candidate = posixpath.normpath(posixpath.join(root, relpath))
    if candidate == root or candidate.startswith(root.rstrip("/") + "/"):
        return candidate
    return None


def has_live_right(handles: dict[str, dict[str, Any]], handle_id: str, right: str) -> bool:
    h = handles.get(handle_id)
    return bool(h and h.get("status") == "live" and right in h.get("rights", []))


def has_any_live_right(handles: dict[str, dict[str, Any]], handle_id: str) -> bool:
    h = handles.get(handle_id)
    return bool(h and h.get("status") == "live" and h.get("rights"))


def object_for_handle(handles: dict[str, dict[str, Any]], handle_id: str) -> str | None:
    h = handles.get(handle_id)
    obj = h.get("object") if h else None
    return obj if isinstance(obj, str) else None


def handle_has_any_right(handles: dict[str, dict[str, Any]], handle_id: Any, rights: set[str]) -> bool:
    if not isinstance(handle_id, str):
        return False
    h = handles.get(handle_id)
    if not h or h.get("status") != "live":
        return False
    return bool(string_set(h.get("rights", []), f"handles.{handle_id}.rights") & rights)


def record_fields(record: dict[str, Any], key: str, context: str) -> set[str]:
    value = record.get(key, [])
    if value is None:
        value = []
    return string_set(value, context)


def redaction_view_check(
    redactions: dict[str, dict[str, Any]],
    view_id: Any,
    fields: set[str],
    context: str,
) -> tuple[bool, str]:
    if not isinstance(view_id, str):
        return False, f"{context}-lacks-redaction"
    view = redactions.get(view_id)
    if view is None or view.get("status") != "active":
        return False, "redaction-view-not-active"
    redacted = record_fields(view, "redacted_fields", f"redaction_views.{view_id}.redacted_fields")
    if fields & redacted:
        return False, "redaction-view-blocks-field"
    allowed = record_fields(view, "allowed_fields", f"redaction_views.{view_id}.allowed_fields")
    if allowed and not fields.issubset(allowed):
        return False, "redaction-view-field-not-allowed"
    return True, "redaction-view-allows-fields"


def eval_read_handle(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    via = op.get("via")
    want = op.get("want", "read")
    handles = index(records, "handles")
    if via == "handle":
        hid = op.get("handle")
        h = handles.get(hid)
        if not isinstance(hid, str) or h is None:
            return "deny", "handle-missing-or-lacks-right", None
        if h.get("status") != "live":
            return "deny", "handle-not-live", None
        if want in h.get("rights", []):
            return "allow", "live-handle-with-right", hid
        return "deny", "handle-missing-or-lacks-right", None
    if via == "receipt":
        return "deny", "receipt-not-authority", None
    if via == "digest":
        return "deny", "digest-not-authority", None
    if via == "ref":
        return "deny", "ref-not-authority", None
    return "deny", "unknown-read-carrier", None


def eval_attenuate_handle(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    handles = index(records, "handles")
    source_id = op.get("source")
    result_id = op.get("result")
    source = handles.get(source_id)
    result = handles.get(result_id)
    require(isinstance(source_id, str) and isinstance(result_id, str), "attenuate_handle needs source and result ids")
    if source is None or source.get("status") != "live":
        return "deny", "source-handle-not-live", None
    if result is None or result.get("status") != "live":
        return "deny", "result-handle-not-live", None
    if source.get("object") != result.get("object"):
        return "deny", "attenuation-object-mismatch", None
    source_rights = string_set(source.get("rights", []), f"handles.{source_id}.rights")
    result_rights = string_set(result.get("rights", []), f"handles.{result_id}.rights")
    if not result_rights.issubset(source_rights):
        return "deny", "attenuation-would-widen-rights", None
    return "allow", "attenuated-handle-rights-subset", result_id


def path_node_for(records: dict[str, list[dict[str, Any]]], view_id: str, path: str) -> dict[str, Any] | None:
    for node in index(records, "path_nodes").values():
        if node.get("view") == view_id and node.get("path") == path:
            return node
    return None


def eval_compat_pathwalk(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    views = index(records, "views")
    handles = index(records, "handles")
    view_id = op.get("view")
    view = views.get(view_id)
    require(view is not None, f"unknown view {op.get('view')}")
    root = op.get("root")
    path = op.get("path")
    want = op.get("want", "read")
    flags = string_set(op.get("flags", []), "operation.flags")
    require(isinstance(root, str) and isinstance(path, str), "compat pathwalk needs string root and path")
    normalized = normalize_under(root, path)
    if normalized is None:
        return "deny", "escape-from-view-root", None

    node = path_node_for(records, str(view_id), normalized)
    if node is not None:
        kind = node.get("kind")
        if kind == "symlink" and ({"no_symlinks", "no_symlink"} & flags):
            return "deny", "symlink-crossing-refused", None
        if kind in {"magic", "magic_link"} and ({"no_magic", "no_magiclinks"} & flags):
            return "deny", "magic-link-crossing-refused", None
        if kind in {"mount", "xdev"} and "no_xdev" in flags:
            return "deny", "mount-crossing-refused", None
        if node.get("status") == "blocked":
            return "deny", "blocked-path-node", None

    for bind in view.get("binds", []):
        if bind.get("path") == normalized:
            hid = bind.get("handle")
            if isinstance(hid, str) and has_live_right(handles, hid, want):
                return "allow", "resolved-bound-live-handle", hid
            return "deny", "bound-handle-missing-or-lacks-right", None
    return "deny", "not-bound-in-view", None


def eval_portal_redeem(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    grants = index(records, "portal_grants")
    handles = index(records, "handles")
    grant = grants.get(op.get("grant"))
    require(grant is not None, f"unknown portal grant {op.get('grant')}")
    status = grant.get("status")
    if status == "spent":
        return "deny", "portal-grant-already-spent", None
    if status == "expired":
        return "deny", "portal-grant-expired", None
    if status == "revoked":
        return "deny", "portal-grant-revoked", None
    if status != "accepted":
        return "deny", "portal-grant-not-accepted", None
    hid = grant.get("result_handle")
    want = op.get("want", "read")
    if isinstance(hid, str) and has_live_right(handles, hid, want):
        return "allow", "accepted-portal-grant-with-live-result-handle", hid
    return "deny", "portal-grant-lacks-live-result-handle", None


def eval_semantic_open(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    artifacts = index(records, "derived_artifacts")
    handles = index(records, "handles")
    artifact = artifacts.get(op.get("artifact"))
    require(artifact is not None, f"unknown artifact {op.get('artifact')}")
    hid = artifact.get("current_handle")
    want = op.get("want", "read")
    if isinstance(hid, str) and has_live_right(handles, hid, want):
        return "allow", "artifact-carried-current-handle", hid
    return "deny", "derived-artifact-not-authority", None


def eval_consent_export(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    chains = index(records, "consent_chains")
    handles = index(records, "handles")
    chain = chains.get(op.get("chain"))
    require(chain is not None, f"unknown consent chain {op.get('chain')}")
    cut = chain.get("approval_cut")
    if not isinstance(cut, dict):
        return "deny", "missing-approval-cut", None
    if cut.get("approved") is not True:
        return "deny", "approval-cut-not-approved", None
    candidate = chain.get("candidate") or {}
    summary = chain.get("summary") or {}
    if cut.get("summary_digest") != candidate.get("summary_digest") or summary.get("digest") != candidate.get("summary_digest"):
        return "deny", "summary-mismatch", None
    for hid in cut.get("authority_slots", []):
        if isinstance(hid, str) and has_live_right(handles, hid, op.get("want", "export")):
            return "allow", "approved-cut-with-live-export-handle", hid
    return "deny", "approval-cut-lacks-live-export-handle", None


def eval_retain_source_via_index(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    artifacts = index(records, "derived_artifacts")
    artifact = artifacts.get(op.get("artifact"))
    require(artifact is not None, f"unknown artifact {op.get('artifact')}")
    if artifact.get("retention") == "source-retention-root":
        return "allow", "artifact-explicit-retention-root", None
    return "deny", "derived-artifact-not-retention-root", None


def eval_commit_mutable_session(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    sessions = index(records, "mutable_sessions")
    handles = index(records, "handles")
    objects = index(records, "objects")
    session = sessions.get(op.get("session"))
    require(session is not None, f"unknown mutable session {op.get('session')}")
    hid = session.get("write_handle")
    if not isinstance(hid, str) or not has_live_right(handles, hid, "write"):
        return "deny", "commit-cut-lacks-live-write-handle", None
    cut = session.get("commit_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "commit-cut-not-approved", None
    if cut.get("observed_base") != session.get("current_head"):
        return "deny", "stale-observed-base", None
    new_object = cut.get("new_object")
    if not isinstance(new_object, str) or new_object not in objects:
        return "deny", "new-object-missing", None
    return "allow", "commit-cut-over-current-base", hid


def eval_reacquire_from_restore_token(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    refs = index(records, "refs")
    handles = index(records, "handles")
    revocations = index(records, "revocations")
    token_id = op.get("token")
    require(isinstance(token_id, str), "reacquire_from_restore_token needs token id")
    token = refs.get(token_id)
    require(token is not None, f"unknown restore token {token_id}")
    for revocation in revocations.values():
        targets = set()
        if isinstance(revocation.get("target"), str):
            targets.add(revocation["target"])
        if isinstance(revocation.get("targets"), list):
            targets.update(i for i in revocation["targets"] if isinstance(i, str))
        if token_id in targets and revocation.get("restore_allowed") is False:
            return "deny", "revocation-death-verdict-stale-brake", None
    if token.get("status") != "live":
        return "deny", "restore-token-not-live", None
    hid = token.get("result_handle")
    want = op.get("want", "read")
    if isinstance(hid, str) and has_live_right(handles, hid, want):
        return "allow", "restore-token-currently-redeemable", hid
    return "deny", "restore-token-lacks-live-result", None


def eval_sweep_decision(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    obj = op.get("object")
    require(isinstance(obj, str), "sweep_decision needs object id")
    handles = index(records, "handles")
    roots = index(records, "retention_roots")
    for h in handles.values():
        if h.get("object") == obj and h.get("status") == "live":
            return "allow", "retained-by-live-handle-root", h.get("id")
    for root in roots.values():
        if root.get("object") == obj and root.get("status") == "active":
            return "allow", "retained-by-explicit-root", None
    return "deny", "no-authoritative-retention-root", None


def eval_tool_invocation(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "prompt_text":
        return "deny", "prompt-text-not-action-plan", None
    plans = index(records, "action_plans")
    handles = index(records, "handles")
    plan = plans.get(op.get("plan"))
    require(plan is not None, f"unknown action plan {op.get('plan')}")
    if plan.get("typed") is not True:
        return "deny", "action-plan-not-typed", None
    cut = plan.get("approval_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "action-plan-not-approved", None
    want = op.get("want", plan.get("effect", "write"))
    for hid in cut.get("authority_slots", []):
        if isinstance(hid, str) and has_live_right(handles, hid, want):
            return "allow", "approved-action-plan-with-live-authority", hid
    return "deny", "action-plan-lacks-live-authority", None


def eval_delegate_handle(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    delegations = index(records, "delegations")
    handles = index(records, "handles")
    delegation = delegations.get(op.get("delegation"))
    require(delegation is not None, f"unknown delegation {op.get('delegation')}")
    if delegation.get("status") == "revoked":
        return "deny", "delegation-revoked", None
    if delegation.get("status") not in {"issued", "live"}:
        return "deny", "delegation-not-issued", None
    lease = delegation.get("lease") or {}
    if not isinstance(lease, dict) or lease.get("status") != "live":
        return "deny", "delegation-lease-not-live", None
    source_id = delegation.get("source_handle")
    child_id = delegation.get("child_handle")
    require(isinstance(source_id, str) and isinstance(child_id, str), "delegate_handle needs source_handle and child_handle")
    source = handles.get(source_id)
    child = handles.get(child_id)
    if source is None or source.get("status") != "live":
        return "deny", "delegation-source-not-live", None
    if child is None or child.get("status") != "live":
        return "deny", "delegation-child-not-live", None
    if source.get("object") != child.get("object"):
        return "deny", "delegation-object-mismatch", None
    source_rights = string_set(source.get("rights", []), f"handles.{source_id}.rights")
    child_rights = string_set(child.get("rights", []), f"handles.{child_id}.rights")
    envelope = delegation.get("attenuation_envelope") or {}
    require(isinstance(envelope, dict), "delegation attenuation_envelope must be object")
    envelope_rights = string_set(envelope.get("rights", []), f"delegations.{delegation.get('id')}.attenuation_envelope.rights")
    if not envelope_rights.issubset(source_rights) or not child_rights.issubset(envelope_rights):
        return "deny", "delegation-would-widen-rights", None
    want = op.get("want", "read")
    if want not in child_rights:
        return "deny", "delegation-child-lacks-requested-right", None
    return "allow", "delegated-handle-within-envelope", child_id


def eval_render_shell_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "shell_cards")
    handles = index(records, "handles")
    card = cards.get(op.get("card"))
    require(card is not None, f"unknown shell card {op.get('card')}")
    badge = card.get("authority_badge")
    slot = card.get("authority_slot")
    has_live = isinstance(slot, str) and has_any_live_right(handles, slot)
    if badge == "live" and not has_live:
        return "deny", "shell-card-authority-badge-lie", None
    if badge == "inert" and has_live and card.get("subject_class") != "receipt-history":
        return "deny", "shell-card-hides-live-authority", slot
    retention_badge = card.get("retention_badge")
    if retention_badge == "retained":
        obj = card.get("object")
        roots = index(records, "retention_roots")
        retained = any(root.get("object") == obj and root.get("status") == "active" for root in roots.values())
        if not retained:
            return "deny", "shell-card-retention-badge-lie", None
    return "allow", "shell-card-authority-badge-honest", slot if has_live else None


def eval_forget_source(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    source = op.get("source")
    require(isinstance(source, str), "forget_source needs source object id")
    artifacts = index(records, "derived_artifacts")
    inventories = index(records, "copy_inventories")
    cleanup_by_artifact: dict[str, str] = {}
    for inventory in inventories.values():
        if inventory.get("source") != source:
            continue
        for entry in inventory.get("entries", []):
            if not isinstance(entry, dict):
                continue
            artifact = entry.get("artifact")
            state = entry.get("cleanup_state")
            if isinstance(artifact, str) and isinstance(state, str):
                cleanup_by_artifact[artifact] = state
    found = False
    for artifact_id, artifact in artifacts.items():
        if artifact.get("source") != source:
            continue
        found = True
        if artifact.get("retention") == "source-retention-root":
            return "deny", "derived-artifact-retains-source", artifact_id
        state = cleanup_by_artifact.get(artifact_id, artifact.get("cleanup_state", artifact.get("status", "live")))
        if state not in {"deleted", "minimized", "tombstoned", "not-materialized"}:
            return "deny", "derived-artifact-still-live", artifact_id
    if not found and op.get("require_inventory") is True:
        return "deny", "copy-inventory-missing", None
    return "allow", "derived-artifacts-accounted-for", None


def eval_quarantine_open(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    capsules = index(records, "quarantine_capsules")
    handles = index(records, "handles")
    capsule = capsules.get(op.get("capsule"))
    require(capsule is not None, f"unknown quarantine capsule {op.get('capsule')}")
    mode = op.get("mode", "direct")
    want = op.get("want", "read")
    if mode == "direct" and capsule.get("status") != "cleared":
        return "deny", "quarantine-not-cleared", None
    if mode == "safe_viewer":
        viewer = capsule.get("safe_viewer_handle")
        if not isinstance(viewer, str) or not has_live_right(handles, viewer, "read"):
            return "deny", "safe-viewer-handle-missing", None
        rights = string_set(handles[viewer].get("rights", []), f"handles.{viewer}.rights")
        if not rights.issubset({"read", "inspect"}):
            return "deny", "safe-viewer-handle-too-powerful", viewer
        return "allow", "safe-viewer-read-only-handle", viewer
    result = capsule.get("result_handle")
    if isinstance(result, str) and has_live_right(handles, result, want):
        return "allow", "cleared-quarantine-live-handle", result
    return "deny", "cleared-quarantine-lacks-live-handle", None


def eval_trust_transition_release(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    transitions = index(records, "trust_transitions")
    evidence = index(records, "origin_evidence")
    capsules = index(records, "quarantine_capsules")
    handles = index(records, "handles")
    transition = transitions.get(op.get("transition"))
    require(transition is not None, f"unknown trust transition {op.get('transition')}")
    capsule = capsules.get(transition.get("capsule"))
    require(capsule is not None, f"trust transition missing capsule {transition.get('capsule')}")
    ev = evidence.get(transition.get("origin_evidence"))
    if ev is None:
        return "deny", "origin-evidence-missing", None
    if ev.get("status") != "verified" or ev.get("evidence_class") in {"summary", "receipt", "claim-only"}:
        return "deny", "origin-evidence-not-verifying", None
    verdict = transition.get("scanner_verdict")
    if verdict != "clean":
        return "deny", "scanner-verdict-not-clean", None
    cut = transition.get("policy_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "trust-transition-not-approved", None
    result = transition.get("result_handle", capsule.get("result_handle"))
    want = op.get("want", "read")
    if isinstance(result, str) and has_live_right(handles, result, want):
        return "allow", "approved-trust-transition-with-live-handle", result
    return "deny", "trust-transition-lacks-live-result-handle", None


def eval_render_authority_diff(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    diffs = index(records, "authority_diffs")
    diff = diffs.get(op.get("diff"))
    require(diff is not None, f"unknown authority diff {op.get('diff')}")
    before = string_set(diff.get("before_rights", []), f"authority_diffs.{diff.get('id')}.before_rights")
    after = string_set(diff.get("after_rights", []), f"authority_diffs.{diff.get('id')}.after_rights")
    declared_added = string_set(diff.get("declared_added", []), f"authority_diffs.{diff.get('id')}.declared_added")
    declared_removed = string_set(diff.get("declared_removed", []), f"authority_diffs.{diff.get('id')}.declared_removed")
    actual_added = after - before
    actual_removed = before - after
    if actual_added != declared_added:
        return "deny", "authority-diff-hides-widening", None
    if actual_removed != declared_removed:
        return "deny", "authority-diff-removal-mismatch", None
    if actual_added and diff.get("widening_badge") != "visible":
        return "deny", "authority-diff-widening-not-badged", None
    if actual_added:
        return "allow", "authority-diff-widening-visible", None
    return "allow", "authority-diff-accounted", None


def eval_export_plan(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "receipt-not-export-authority", None
    plans = index(records, "export_plans")
    handles = index(records, "handles")
    capsules = index(records, "quarantine_capsules")
    plan = plans.get(op.get("plan"))
    require(plan is not None, f"unknown export plan {op.get('plan')}")
    if plan.get("typed") is not True:
        return "deny", "export-plan-not-typed", None
    cut = plan.get("approval_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "export-plan-not-approved", None
    hid = plan.get("authority_handle")
    if not isinstance(hid, str) or not has_live_right(handles, hid, "export"):
        return "deny", "export-plan-lacks-live-export-authority", None
    source = plan.get("source")
    for capsule in capsules.values():
        if capsule.get("source") == source and capsule.get("status") != "cleared" and plan.get("quarantine_clearance") is not True:
            return "deny", "export-blocked-by-quarantine", None
    sink = plan.get("sink")
    if not isinstance(sink, str) or not sink:
        return "deny", "export-plan-missing-sink", None
    return "allow", "approved-export-plan-with-live-authority", hid



def eval_policy_decision(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "receipt-not-policy-authority", None
    decisions = index(records, "policy_decisions")
    bundles = index(records, "policy_bundles")
    handles = index(records, "handles")
    decision = decisions.get(op.get("decision"))
    require(decision is not None, f"unknown policy decision {op.get('decision')}")
    bundle = bundles.get(decision.get("bundle"))
    if bundle is None:
        return "deny", "policy-bundle-missing", None
    if bundle.get("status") != "active":
        return "deny", "policy-bundle-not-active", None
    if decision.get("policy_digest") != bundle.get("digest"):
        return "deny", "policy-digest-mismatch", None
    if decision.get("decision_class") != "enforced":
        return "deny", "policy-decision-not-enforcing", None
    if decision.get("effect") != "allow":
        return "deny", "policy-decision-denies", None
    hid = decision.get("authority_handle", op.get("handle"))
    want = op.get("want", decision.get("required_right", "read"))
    if not isinstance(hid, str) or not has_live_right(handles, hid, want):
        return "deny", "policy-decision-not-authority", None
    resource = decision.get("resource")
    if isinstance(resource, str) and object_for_handle(handles, hid) != resource:
        return "deny", "policy-resource-handle-mismatch", None
    return "allow", "policy-allow-plus-live-authority", hid


def eval_witness_bundle_verify(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("replay_effect") is True:
        return "deny", "witness-not-effect-authority", None
    witnesses = index(records, "witness_bundles")
    decisions = index(records, "policy_decisions")
    bundles = index(records, "policy_bundles")
    witness = witnesses.get(op.get("witness"))
    require(witness is not None, f"unknown witness bundle {op.get('witness')}")
    if witness.get("status") != "complete":
        return "deny", "witness-bundle-not-complete", None
    decision = decisions.get(witness.get("decision"))
    if decision is None:
        return "deny", "witness-decision-missing", None
    bundle = bundles.get(witness.get("policy_bundle"))
    if bundle is None:
        return "deny", "witness-policy-bundle-missing", None
    if bundle.get("status") != "active":
        return "deny", "witness-policy-bundle-not-active", None
    subject = op.get("subject")
    if isinstance(subject, str) and witness.get("subject") != subject:
        return "deny", "witness-subject-mismatch", None
    policy_digest = witness.get("policy_digest")
    if policy_digest != bundle.get("digest") or policy_digest != decision.get("policy_digest"):
        return "deny", "witness-policy-digest-mismatch", None
    required = string_set(op.get("requires", []), "operation.requires")
    included = string_set(witness.get("includes", []), f"witness_bundles.{witness.get('id')}.includes")
    if not required.issubset(included):
        return "deny", "witness-required-facts-missing", None
    return "allow", "witness-bundle-binds-decision-facts", None


def eval_scenario_replay(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    scenarios = index(records, "scenario_replays")
    scenario = scenarios.get(op.get("scenario"))
    require(scenario is not None, f"unknown scenario replay {op.get('scenario')}")
    if scenario.get("status") != "sealed":
        return "deny", "scenario-not-sealed", None
    steps = as_list(scenario.get("steps", []), f"scenario_replays.{scenario.get('id')}.steps")
    if not steps:
        return "deny", "scenario-has-no-steps", None
    has_denial = False
    for step in steps:
        require(isinstance(step, dict), "scenario replay steps must be objects")
        result = step.get("result")
        reason = step.get("reason")
        if result not in {"allow", "deny"} or not isinstance(reason, str) or not reason:
            return "deny", "scenario-step-malformed", None
        if result == "deny":
            has_denial = True
        if op.get("require_witnesses", True) and not step.get("witness"):
            return "deny", "scenario-step-missing-witness", None
    if op.get("require_negative_evidence", True) and not has_denial:
        return "deny", "scenario-lacks-denial-evidence", None
    return "allow", "scenario-replay-accounted", None


def eval_override_grant(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    warrants = index(records, "override_warrants")
    handles = index(records, "handles")
    warrant = warrants.get(op.get("warrant"))
    require(warrant is not None, f"unknown override warrant {op.get('warrant')}")
    if warrant.get("status") != "approved":
        return "deny", "override-not-approved", None
    if warrant.get("steward_signature") != "verified":
        return "deny", "override-warrant-not-verified", None
    if not warrant.get("audit_sink"):
        return "deny", "override-audit-sink-missing", None
    expires_at = warrant.get("expires_at")
    context_time = op.get("context_time")
    if isinstance(expires_at, str) and isinstance(context_time, str) and context_time >= expires_at:
        return "deny", "override-expired", None
    hid = warrant.get("authority_handle")
    want = op.get("want", warrant.get("right", "read"))
    if not isinstance(hid, str) or not has_live_right(handles, hid, want):
        return "deny", "override-lacks-live-authority", None
    scope = warrant.get("scope")
    if isinstance(scope, str) and object_for_handle(handles, hid) != scope:
        return "deny", "override-scope-mismatch", None
    return "allow", "verified-override-plus-live-authority", hid


def eval_renew_lease(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "receipt-not-lease-authority", None
    leases = index(records, "authority_leases")
    handles = index(records, "handles")
    revocations = index(records, "revocations")
    lease_id = op.get("lease")
    lease = leases.get(lease_id)
    require(lease is not None, f"unknown authority lease {lease_id}")
    targets: set[str] = set()
    for revocation in revocations.values():
        if isinstance(revocation.get("target"), str):
            targets.add(revocation["target"])
        if isinstance(revocation.get("targets"), list):
            targets.update(i for i in revocation["targets"] if isinstance(i, str))
    handle_id = lease.get("handle")
    if lease_id in targets or handle_id in targets:
        return "deny", "lease-revoked-by-wavefront", None
    if lease.get("status") != "live":
        return "deny", "lease-not-live", None
    context_time = require_string(op.get("context_time"), "renew_lease.context_time")
    expires_at = require_string(lease.get("expires_at"), f"authority_leases.{lease_id}.expires_at")
    if time_reached(context_time, expires_at, "renew_lease.expiry"):
        return "deny", "lease-expired", None
    if op.get("observed_epoch") != lease.get("epoch"):
        return "deny", "lease-epoch-mismatch", None
    cut = lease.get("renewal_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "lease-renewal-cut-missing", None
    want = op.get("want", lease.get("right", "read"))
    if not isinstance(handle_id, str) or not has_live_right(handles, handle_id, want):
        return "deny", "lease-lacks-live-authority", None
    return "allow", "lease-renewed-current-epoch", handle_id


def eval_publish_offline_branch(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    branches = index(records, "offline_branches")
    handles = index(records, "handles")
    branch_id = op.get("branch")
    branch = branches.get(branch_id)
    require(branch is not None, f"unknown offline branch {branch_id}")
    if op.get("via") in {"local_commit", "receipt"}:
        return "deny", "offline-local-commit-not-publish-authority", None
    if branch.get("status") != "ready":
        return "deny", "offline-branch-not-ready", None
    if branch.get("remote_current_head") != branch.get("observed_remote_head"):
        return "deny", "offline-branch-stale-remote-head", None
    cut = branch.get("revalidation_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "offline-branch-revalidation-missing", None
    hid = branch.get("write_handle")
    if not isinstance(hid, str) or not has_live_right(handles, hid, "write"):
        return "deny", "offline-branch-lacks-live-write-authority", None
    if cut.get("remote_head") != branch.get("remote_current_head"):
        return "deny", "offline-branch-revalidation-head-mismatch", None
    return "allow", "offline-branch-published-after-revalidation", hid


def eval_reconcile_merge(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt" or op.get("replay_effect") is True:
        return "deny", "merge-record-not-authority", None
    plans = index(records, "merge_plans")
    handles = index(records, "handles")
    plan_id = op.get("merge")
    plan = plans.get(plan_id)
    require(plan is not None, f"unknown merge plan {plan_id}")
    if plan.get("status") not in {"fast_forward", "resolved"}:
        return "deny", "merge-plan-not-ready", None
    conflicts = as_list(plan.get("conflicts", []), f"merge_plans.{plan_id}.conflicts")
    if conflicts:
        cut = plan.get("resolution_cut")
        if not isinstance(cut, dict) or cut.get("approved") is not True:
            return "deny", "merge-conflict-unresolved", None
        witnesses = as_list(plan.get("resolution_witnesses", []), f"merge_plans.{plan_id}.resolution_witnesses")
        if not witnesses:
            return "deny", "merge-resolution-witness-missing", None
    hid = plan.get("authority_handle")
    if not isinstance(hid, str) or not has_live_right(handles, hid, "write"):
        return "deny", "merge-lacks-live-write-authority", None
    if plan.get("status") == "fast_forward" and not conflicts:
        return "allow", "merge-fast-forward-current-base", hid
    return "allow", "merge-resolution-approved", hid


def eval_verify_remote_attestation(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("replay_effect") is True or op.get("via") == "attestation_as_authority":
        return "deny", "remote-attestation-not-authority", None
    attestations = index(records, "remote_attestations")
    att_id = op.get("attestation")
    att = attestations.get(att_id)
    require(att is not None, f"unknown remote attestation {att_id}")
    if att.get("status") != "valid" or att.get("signature") != "verified":
        return "deny", "remote-attestation-not-verified", None
    if att.get("revocation_status") not in {"good", "not_revoked", "none"}:
        return "deny", "remote-attestation-revoked", None
    context_time = require_string(op.get("context_time"), "verify_remote_attestation.context_time")
    expires_at = att.get("expires_at")
    if isinstance(expires_at, str) and time_reached(context_time, expires_at, "remote_attestation.expiry"):
        return "deny", "remote-attestation-expired", None
    expected_subject = op.get("subject")
    if isinstance(expected_subject, str) and att.get("subject") != expected_subject:
        return "deny", "remote-attestation-subject-mismatch", None
    expected_digest = op.get("statement_digest")
    if isinstance(expected_digest, str) and att.get("statement_digest") != expected_digest:
        return "deny", "remote-attestation-statement-mismatch", None
    return "allow", "remote-attestation-verified", None


def eval_check_freshness_fence(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    fences = index(records, "freshness_fences")
    fence_id = op.get("fence")
    fence = fences.get(fence_id)
    require(fence is not None, f"unknown freshness fence {fence_id}")
    if fence.get("status") not in {"valid", "sealed"}:
        return "deny", "freshness-fence-not-valid", None
    context_time = require_string(op.get("context_time"), "check_freshness_fence.context_time")
    valid_until = require_string(fence.get("valid_until"), f"freshness_fences.{fence_id}.valid_until")
    if time_reached(context_time, valid_until, "freshness_fence.valid_until"):
        return "deny", "freshness-fence-expired", None
    if op.get("epoch") != fence.get("epoch"):
        return "deny", "freshness-epoch-mismatch", None
    if op.get("require_linearized") is True and fence.get("uncertainty_state") != "settled":
        return "deny", "freshness-uncertainty-open", None
    return "allow", "freshness-fence-current", None


def eval_checkpoint_journal(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "receipt-not-checkpoint-authority", None
    checkpoints = index(records, "journal_checkpoints")
    objects = index(records, "objects")
    handles = index(records, "handles")
    checkpoint_id = op.get("checkpoint")
    checkpoint = checkpoints.get(checkpoint_id)
    require(checkpoint is not None, f"unknown journal checkpoint {checkpoint_id}")
    if checkpoint.get("status") != "ready":
        return "deny", "journal-checkpoint-not-ready", None
    if checkpoint.get("flush_proof") != "verified":
        return "deny", "journal-flush-proof-missing", None
    target = checkpoint.get("target_object")
    if not isinstance(target, str) or target not in objects:
        return "deny", "checkpoint-target-missing", None
    hid = checkpoint.get("finalizer_handle")
    if not isinstance(hid, str) or not (has_live_right(handles, hid, "finalize") or has_live_right(handles, hid, "write")):
        return "deny", "checkpoint-lacks-live-finalizer", None
    return "allow", "journal-checkpoint-finalized", hid


def eval_redaction_view_read(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"redaction_view_only", "receipt"}:
        return "deny", "redaction-view-not-authority", None
    redactions = index(records, "redaction_views")
    handles = index(records, "handles")
    view_id = op.get("view")
    view = redactions.get(view_id)
    require(view is not None, f"unknown redaction view {view_id}")
    fields = string_set(op.get("fields", []), "operation.fields")
    ok, reason = redaction_view_check(redactions, view_id, fields, "redaction-view-read")
    if not ok:
        return "deny", reason, None
    hid = op.get("handle", view.get("authority_handle"))
    if not handle_has_any_right(handles, hid, {"read", "inspect"}):
        return "deny", "redaction-view-lacks-live-authority", None
    source = view.get("source")
    if isinstance(source, str) and object_for_handle(handles, hid) != source:
        return "deny", "redaction-view-source-mismatch", None
    return "allow", "redaction-view-read-with-live-authority", hid


def eval_render_audit_projection(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    projections = index(records, "audit_projections")
    redactions = index(records, "redaction_views")
    handles = index(records, "handles")
    projection_id = op.get("projection")
    projection = projections.get(projection_id)
    require(projection is not None, f"unknown audit projection {projection_id}")
    if op.get("replay_effect") is True:
        return "deny", "audit-projection-not-authority", None
    authority_slot = projection.get("authority_slot")
    has_live_slot = handle_has_any_right(handles, authority_slot, {"read", "write", "export", "observe", "audit_raw"})
    if projection.get("authority_badge") == "live" and not has_live_slot:
        return "deny", "audit-projection-authority-badge-lie", None
    if projection.get("status") != "sealed":
        return "deny", "audit-projection-not-sealed", None
    observer = op.get("observer_handle", projection.get("observer_handle"))
    if not handle_has_any_right(handles, observer, {"observe", "audit"}):
        return "deny", "audit-projection-lacks-observe-authority", None
    fields = string_set(op.get("fields", projection.get("included_fields", [])), "audit-projection.fields")
    redaction_id = projection.get("redaction_view")
    if projection.get("projection_class") == "raw":
        if not handle_has_any_right(handles, op.get("raw_handle", projection.get("raw_handle")), {"audit_raw", "read_raw"}):
            return "deny", "audit-raw-projection-lacks-live-authority", None
        return "allow", "audit-raw-projection-rendered-with-authority", op.get("raw_handle", projection.get("raw_handle"))
    ok, reason = redaction_view_check(redactions, redaction_id, fields, "audit-projection")
    if not ok:
        if reason == "audit-projection-lacks-redaction":
            return "deny", "audit-projection-lacks-redaction", None
        return "deny", reason, None
    return "allow", "audit-projection-rendered-with-redaction", observer if isinstance(observer, str) else None


def eval_disclose_package(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "receipt-not-disclosure-authority", None
    packages = index(records, "disclosure_packages")
    redactions = index(records, "redaction_views")
    handles = index(records, "handles")
    package_id = op.get("package")
    package = packages.get(package_id)
    require(package is not None, f"unknown disclosure package {package_id}")
    if package.get("status") != "ready":
        return "deny", "disclosure-package-not-ready", None
    cut = package.get("approval_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "disclosure-package-not-approved", None
    source = op.get("source", package.get("source"))
    if isinstance(source, str) and package.get("source") != source:
        return "deny", "disclosure-scope-mismatch", None
    sink = op.get("sink", package.get("sink"))
    if not isinstance(sink, str) or not sink:
        return "deny", "disclosure-package-missing-sink", None
    hid = op.get("handle", package.get("authority_handle"))
    payload_class = package.get("payload_class", "redacted")
    if payload_class == "raw":
        if not handle_has_any_right(handles, hid, {"export_raw"}):
            return "deny", "disclosure-raw-lacks-live-authority", None
    else:
        if not handle_has_any_right(handles, hid, {"export", "disclose"}):
            return "deny", "disclosure-lacks-live-authority", None
        if package.get("redaction_applied") is not True:
            return "deny", "disclosure-package-lacks-redaction", None
        fields = string_set(package.get("fields", []), f"disclosure_packages.{package_id}.fields")
        ok, reason = redaction_view_check(redactions, package.get("redaction_view"), fields, "disclosure-package")
        if not ok:
            if reason == "disclosure-package-lacks-redaction":
                return "deny", "disclosure-package-lacks-redaction", None
            return "deny", reason, None
    if isinstance(package.get("source"), str) and object_for_handle(handles, hid) != package.get("source"):
        return "deny", "disclosure-scope-mismatch", None
    return "allow", "approved-disclosure-package-with-live-authority", hid if isinstance(hid, str) else None


def eval_deliver_notification(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"notification_as_authority", "receipt"} or op.get("replay_effect") is True:
        return "deny", "notification-not-object-authority", None
    cursors = index(records, "subscription_cursors")
    envelopes = index(records, "notification_envelopes")
    redactions = index(records, "redaction_views")
    handles = index(records, "handles")
    cursor_id = op.get("cursor")
    cursor = cursors.get(cursor_id)
    require(cursor is not None, f"unknown subscription cursor {cursor_id}")
    envelope_id = op.get("envelope")
    envelope = envelopes.get(envelope_id)
    require(envelope is not None, f"unknown notification envelope {envelope_id}")
    if cursor.get("status") != "live":
        return "deny", "subscription-cursor-not-live", None
    context_time = op.get("context_time")
    expires_at = cursor.get("expires_at")
    if isinstance(context_time, str) and isinstance(expires_at, str) and time_reached(context_time, expires_at, "subscription_cursor.expiry"):
        return "deny", "subscription-cursor-expired", None
    hid = cursor.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"observe"}):
        return "deny", "subscription-lacks-live-observe-authority", None
    subjects = set(i for i in cursor.get("subjects", []) if isinstance(i, str))
    subject = envelope.get("subject")
    if subjects and subject not in subjects:
        return "deny", "subscription-scope-mismatch", None
    fields = string_set(envelope.get("fields", []), f"notification_envelopes.{envelope_id}.fields")
    if envelope.get("payload_class") != "metadata":
        if envelope.get("redaction_applied") is not True:
            return "deny", "notification-redaction-leak", None
        ok, reason = redaction_view_check(redactions, cursor.get("redaction_view"), fields, "notification")
        if not ok:
            return "deny", "notification-redaction-leak" if reason == "redaction-view-blocks-field" else reason, None
    return "allow", "notification-delivered-with-observe-authority", hid if isinstance(hid, str) else None


def eval_subject_access_export(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "receipt-not-subject-access-authority", None
    requests = index(records, "subject_access_requests")
    packages = index(records, "disclosure_packages")
    redactions = index(records, "redaction_views")
    handles = index(records, "handles")
    request_id = op.get("request")
    request = requests.get(request_id)
    require(request is not None, f"unknown subject access request {request_id}")
    if request.get("status") != "approved":
        return "deny", "subject-access-not-approved", None
    cut = request.get("review_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "subject-access-review-cut-missing", None
    subject = op.get("subject", request.get("subject"))
    if request.get("subject") != subject:
        return "deny", "subject-access-subject-mismatch", None
    package = packages.get(request.get("disclosure_package"))
    if package is None or package.get("status") != "ready":
        return "deny", "subject-access-package-not-ready", None
    scope = set(i for i in request.get("scope_objects", []) if isinstance(i, str))
    if scope and package.get("source") not in scope:
        return "deny", "subject-access-scope-mismatch", None
    if package.get("subject") != request.get("subject"):
        return "deny", "subject-access-subject-mismatch", None
    fields = string_set(package.get("fields", []), f"disclosure_packages.{package.get('id')}.fields")
    ok, reason = redaction_view_check(redactions, package.get("redaction_view", request.get("redaction_view")), fields, "subject-access")
    if not ok:
        if reason == "redaction-view-blocks-field":
            return "deny", "subject-access-redaction-leak", None
        return "deny", reason, None
    hid = request.get("authority_handle", package.get("authority_handle"))
    if not handle_has_any_right(handles, hid, {"subject_access", "export"}):
        return "deny", "subject-access-lacks-live-authority", None
    if isinstance(package.get("source"), str) and object_for_handle(handles, hid) != package.get("source"):
        return "deny", "subject-access-scope-mismatch", None
    return "allow", "subject-access-export-with-redaction-and-live-authority", hid if isinstance(hid, str) else None


def eval_compose_shared_view(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"room_badge", "presence_card", "collaboration_card"}:
        return "deny", "collaboration-badge-not-authority", None
    rooms = index(records, "shared_rooms")
    edges = index(records, "mount_edges")
    handles = index(records, "handles")
    room_id = op.get("room")
    room = rooms.get(room_id)
    require(room is not None, f"unknown shared room {room_id}")
    if room.get("status") != "active":
        return "deny", "shared-room-not-active", None
    context_epoch = op.get("context_epoch")
    if isinstance(context_epoch, str) and room.get("state_epoch") != context_epoch:
        return "deny", "shared-room-epoch-mismatch", None
    principal = op.get("principal")
    participants = set(i for i in room.get("participants", []) if isinstance(i, str))
    if isinstance(principal, str) and participants and principal not in participants:
        return "deny", "shared-room-principal-not-member", None
    edge_id = op.get("edge")
    edge = edges.get(edge_id)
    require(edge is not None, f"unknown mount edge {edge_id}")
    if edge.get("status") != "live":
        return "deny", "mount-edge-not-live", None
    if edge.get("target_room") != room_id:
        return "deny", "mount-edge-room-mismatch", None
    propagation = edge.get("propagation", "private")
    if propagation in {"shared", "peer", "propagating"}:
        gate = edge.get("propagation_gate")
        if not isinstance(gate, dict) or gate.get("approved") is not True:
            return "deny", "mount-propagation-not-approved", None
    source_id = edge.get("source_handle")
    if not isinstance(source_id, str) or source_id not in handles or handles[source_id].get("status") != "live":
        return "deny", "mount-edge-lacks-live-source-handle", None
    source_rights = string_set(handles[source_id].get("rights", []), f"handles.{source_id}.rights")
    edge_rights = string_set(edge.get("rights", []), f"mount_edges.{edge_id}.rights")
    if not edge_rights.issubset(source_rights):
        return "deny", "mount-edge-would-widen-rights", None
    want = op.get("want", "read")
    if want not in edge_rights:
        return "deny", "mount-edge-lacks-requested-right", None
    return "allow", "shared-view-composed-from-live-mount-edge", source_id


def eval_group_bound_authority(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"group_label", "directory_card", "membership_badge"}:
        return "deny", "group-label-not-authority", None
    groups = index(records, "group_memberships")
    handles = index(records, "handles")
    group_id = op.get("group")
    group = groups.get(group_id)
    require(group is not None, f"unknown group membership {group_id}")
    if group.get("status") != "active":
        return "deny", "group-membership-not-active", None
    context_epoch = op.get("context_epoch")
    if isinstance(context_epoch, str) and context_epoch != group.get("epoch"):
        return "deny", "group-membership-epoch-mismatch", None
    principal = op.get("principal")
    if isinstance(principal, str) and principal in set(i for i in group.get("denied_members", []) if isinstance(i, str)):
        return "deny", "principal-explicitly-denied", None
    members = set(i for i in group.get("members", []) if isinstance(i, str))
    if isinstance(principal, str) and principal not in members:
        return "deny", "principal-not-group-member", None
    hid = op.get("handle", group.get("authority_handle"))
    want = op.get("want", group.get("right", "read"))
    if not isinstance(hid, str) or not has_live_right(handles, hid, want):
        return "deny", "group-membership-not-authority", None
    scope = group.get("scope")
    if isinstance(scope, str) and object_for_handle(handles, hid) != scope:
        return "deny", "group-scope-handle-mismatch", None
    return "allow", "group-membership-plus-live-authority", hid


def eval_resolve_label_overlay(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    overlays = index(records, "label_overlays")
    handles = index(records, "handles")
    overlay_id = op.get("overlay")
    overlay = overlays.get(overlay_id)
    require(overlay is not None, f"unknown label overlay {overlay_id}")
    if overlay.get("status") != "active":
        return "deny", "label-overlay-not-active", None
    obj = op.get("object")
    if isinstance(obj, str) and overlay.get("object") != obj:
        return "deny", "label-overlay-object-mismatch", None
    conflicts = as_list(overlay.get("conflicts", []), f"label_overlays.{overlay_id}.conflicts")
    if conflicts:
        cut = overlay.get("resolution_cut")
        if not isinstance(cut, dict) or cut.get("approved") is not True:
            return "deny", "label-overlay-conflict-unresolved", None
    if op.get("want") == "authorize" or op.get("claims_live") is True or overlay.get("authority_badge") == "live":
        hid = overlay.get("authority_handle")
        if not isinstance(hid, str) or not has_any_live_right(handles, hid):
            return "deny", "label-overlay-not-authority", None
        if isinstance(overlay.get("object"), str) and object_for_handle(handles, hid) != overlay.get("object"):
            return "deny", "label-overlay-scope-mismatch", None
        if conflicts:
            return "allow", "label-overlay-rendered-with-conflict-witness", hid
        return "allow", "label-overlay-rendered-with-live-badge", hid
    if conflicts:
        return "allow", "label-overlay-rendered-with-conflict-witness", None
    return "allow", "label-overlay-rendered-inert", None


def eval_handoff_packet(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "handoff-receipt-not-authority", None
    packets = index(records, "handoff_packets")
    packet_id = op.get("packet")
    packet = packets.get(packet_id)
    require(packet is not None, f"unknown handoff packet {packet_id}")
    if packet.get("status") != "accepted":
        return "deny", "handoff-not-accepted", None
    cut = packet.get("acceptance_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "handoff-not-accepted", None
    target = op.get("target_principal", op.get("target"))
    if isinstance(target, str) and packet.get("target_principal") != target:
        return "deny", "handoff-target-mismatch", None
    delegation_id = packet.get("delegation")
    if not isinstance(delegation_id, str):
        return "deny", "handoff-delegation-missing", None
    result, reason, handle = eval_delegate_handle({"delegation": delegation_id, "want": op.get("want", packet.get("right", "read"))}, records)
    if result != "allow":
        if reason == "delegation-would-widen-rights":
            return "deny", "handoff-delegation-would-widen-rights", None
        return "deny", "handoff-delegation-invalid", None
    child = packet.get("child_handle")
    if isinstance(child, str) and child != handle:
        return "deny", "handoff-child-handle-mismatch", None
    return "allow", "accepted-handoff-with-delegated-live-authority", handle


def eval_render_collaboration_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "collaboration_cards")
    rooms = index(records, "shared_rooms")
    handles = index(records, "handles")
    card_id = op.get("card")
    card = cards.get(card_id)
    require(card is not None, f"unknown collaboration card {card_id}")
    if card.get("status") != "sealed":
        return "deny", "collaboration-card-not-sealed", None
    room_id = card.get("room")
    room = rooms.get(room_id) if isinstance(room_id, str) else None
    if isinstance(room_id, str):
        if room is None or room.get("status") != "active":
            return "deny", "collaboration-card-room-not-active", None
    slot = card.get("authority_slot")
    has_live = isinstance(slot, str) and has_any_live_right(handles, slot)
    if card.get("authority_badge") == "live" and not has_live:
        return "deny", "collaboration-card-authority-badge-lie", None
    if has_live:
        visible = set(i for i in card.get("visible_rights", []) if isinstance(i, str))
        actual = string_set(handles[slot].get("rights", []), f"handles.{slot}.rights")
        if visible and visible != actual:
            return "deny", "collaboration-card-rights-mismatch", None
    principal = op.get("principal", card.get("principal"))
    claimed_role = card.get("claimed_role")
    if isinstance(claimed_role, str) and room is not None and isinstance(principal, str):
        roles = room.get("roles", {})
        require(isinstance(roles, dict), f"shared_rooms.{room_id}.roles must be an object when present")
        actual_role = roles.get(principal)
        if actual_role != claimed_role:
            return "deny", "collaboration-card-role-lie", None
    return "allow", "collaboration-card-rendered-honest", slot if has_live else None



def object_retention_blockers(records: dict[str, list[dict[str, Any]]], obj: str) -> tuple[str | None, str | None]:
    handles = index(records, "handles")
    roots = index(records, "retention_roots")
    pins = index(records, "snapshot_pins")
    holds = index(records, "archive_holds")
    backups = index(records, "backup_sets")
    for h in handles.values():
        if h.get("object") == obj and h.get("status") == "live" and h.get("rights"):
            return "object-has-live-handle-root", h.get("id") if isinstance(h.get("id"), str) else None
    for root in roots.values():
        if root.get("object") == obj and root.get("status") == "active":
            return "object-has-retention-root", root.get("id") if isinstance(root.get("id"), str) else None
    for pin in pins.values():
        if pin.get("object") == obj and pin.get("status") == "active":
            return "object-pinned-by-snapshot", pin.get("id") if isinstance(pin.get("id"), str) else None
    for hold in holds.values():
        objects = set(i for i in hold.get("objects", []) if isinstance(i, str))
        if (hold.get("object") == obj or obj in objects) and hold.get("status") == "active":
            return "object-under-archive-hold", hold.get("id") if isinstance(hold.get("id"), str) else None
    for backup in backups.values():
        objects = set(i for i in backup.get("objects", []) if isinstance(i, str))
        if obj in objects and backup.get("status") in {"protected", "retention_required", "verified-protected"}:
            return "object-retained-by-backup-set", backup.get("id") if isinstance(backup.get("id"), str) else None
    return None, None


def derived_copy_blocker(records: dict[str, list[dict[str, Any]]], obj: str, require_inventory: bool) -> tuple[str | None, str | None]:
    artifacts = index(records, "derived_artifacts")
    inventories = index(records, "copy_inventories")
    cleanup_by_artifact: dict[str, str] = {}
    inventory_seen = False
    for inventory in inventories.values():
        if inventory.get("source") != obj:
            continue
        inventory_seen = True
        for entry in inventory.get("entries", []):
            if not isinstance(entry, dict):
                continue
            artifact = entry.get("artifact")
            state = entry.get("cleanup_state")
            if isinstance(artifact, str) and isinstance(state, str):
                cleanup_by_artifact[artifact] = state
    found_artifact = False
    for artifact_id, artifact in artifacts.items():
        if artifact.get("source") != obj:
            continue
        found_artifact = True
        state = cleanup_by_artifact.get(artifact_id, artifact.get("cleanup_state", artifact.get("status", "live")))
        if state not in {"deleted", "minimized", "tombstoned", "not-materialized"}:
            return "derived-copy-inventory-open", artifact_id
    if require_inventory and found_artifact and not inventory_seen:
        return "copy-inventory-missing", None
    return None, None


def eval_collect_gc_candidate(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "gc-receipt-not-authority", None
    candidates = index(records, "gc_candidates")
    handles = index(records, "handles")
    candidate_id = op.get("candidate")
    candidate = candidates.get(candidate_id)
    require(candidate is not None, f"unknown gc candidate {candidate_id}")
    obj = candidate.get("object")
    require(isinstance(obj, str), "gc candidate needs object")
    reason, blocker = object_retention_blockers(records, obj)
    if reason is not None:
        return "deny", reason, blocker
    if candidate.get("require_copy_inventory") is True:
        reason, blocker = derived_copy_blocker(records, obj, True)
        if reason is not None:
            return "deny", reason, blocker
    if candidate.get("status") != "ready":
        return "deny", "gc-candidate-not-ready", None
    if candidate.get("tombstone") != "written":
        return "deny", "tombstone-not-written", None
    cut = candidate.get("sweep_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "sweep-cut-not-approved", None
    handle_id = candidate.get("collector_handle", op.get("handle"))
    if not isinstance(handle_id, str) or not has_live_right(handles, handle_id, "gc"):
        return "deny", "gc-lacks-live-collector-authority", None
    return "allow", "gc-candidate-collectable", handle_id


def eval_prune_snapshot(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "snapshot-prune-receipt-not-authority", None
    pins = index(records, "snapshot_pins")
    handles = index(records, "handles")
    backups = index(records, "backup_sets")
    pin_id = op.get("pin")
    pin = pins.get(pin_id)
    require(pin is not None, f"unknown snapshot pin {pin_id}")
    for backup in backups.values():
        pins_in_backup = set(i for i in backup.get("snapshot_pins", []) if isinstance(i, str))
        if pin_id in pins_in_backup and backup.get("status") in {"protected", "retention_required", "verified-protected"}:
            return "deny", "snapshot-retained-by-backup-set", backup.get("id") if isinstance(backup.get("id"), str) else None
    if pin.get("status") != "active":
        return "deny", "snapshot-pin-not-active", None
    if pin.get("hold") == "active" or pin.get("legal_hold") is True:
        return "deny", "snapshot-pin-under-hold", None
    cut = pin.get("prune_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "snapshot-prune-cut-missing", None
    handle_id = pin.get("prune_handle", op.get("handle"))
    if not isinstance(handle_id, str) or not (has_live_right(handles, handle_id, "prune_snapshot") or has_live_right(handles, handle_id, "gc")):
        return "deny", "snapshot-prune-lacks-live-authority", None
    return "allow", "snapshot-pin-pruned-with-cut", handle_id


def eval_release_archive_hold(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "archive-hold-receipt-not-authority", None
    holds = index(records, "archive_holds")
    handles = index(records, "handles")
    hold_id = op.get("hold")
    hold = holds.get(hold_id)
    require(hold is not None, f"unknown archive hold {hold_id}")
    if hold.get("status") != "active":
        return "deny", "archive-hold-not-active", None
    if hold.get("mode") == "compliance":
        now = op.get("now", hold.get("now"))
        until = hold.get("retain_until")
        if isinstance(now, str) and isinstance(until, str) and now < until:
            return "deny", "compliance-retention-not-expired", None
    cut = hold.get("release_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "archive-hold-release-cut-missing", None
    steward = cut.get("steward")
    if not isinstance(steward, str) or not steward:
        return "deny", "archive-hold-missing-steward", None
    handle_id = cut.get("authority_handle", hold.get("release_handle", op.get("handle")))
    if not isinstance(handle_id, str) or not has_live_right(handles, handle_id, "release_hold"):
        return "deny", "archive-hold-release-lacks-live-authority", None
    return "allow", "archive-hold-released-by-stewarded-cut", handle_id


def eval_restore_from_backup(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"backup_manifest", "receipt", "snapshot_label"}:
        return "deny", "backup-manifest-not-authority", None
    backups = index(records, "backup_sets")
    plans = index(records, "restore_plans")
    handles = index(records, "handles")
    objects = index(records, "objects")
    plan_id = op.get("plan")
    plan = plans.get(plan_id)
    require(plan is not None, f"unknown restore plan {plan_id}")
    backup = backups.get(plan.get("backup"))
    require(backup is not None, f"unknown backup set {plan.get('backup')}")
    if backup.get("verification") != "verified" or backup.get("status") not in {"available", "verified", "protected", "verified-protected"}:
        return "deny", "backup-set-not-verified", None
    obj = plan.get("object")
    if not isinstance(obj, str) or obj not in objects or obj not in set(i for i in backup.get("objects", []) if isinstance(i, str)):
        return "deny", "restore-object-not-in-backup", None
    cut = plan.get("approval_cut")
    if plan.get("status") != "approved" or not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "restore-plan-not-approved", None
    handle_id = cut.get("authority_handle", plan.get("restore_handle", op.get("handle")))
    if not isinstance(handle_id, str) or not (has_live_right(handles, handle_id, "restore") or has_live_right(handles, handle_id, "write")):
        return "deny", "restore-lacks-live-authority", None
    return "allow", "restore-plan-approved-with-live-authority", handle_id


def eval_verify_deletion_claim(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("intent") in {"open", "reopen", "read"}:
        return "deny", "deletion-claim-not-authority", None
    claims = index(records, "deletion_claims")
    proofs = index(records, "sanitization_proofs")
    backups = index(records, "backup_sets")
    pins = index(records, "snapshot_pins")
    holds = index(records, "archive_holds")
    claim_id = op.get("claim")
    claim = claims.get(claim_id)
    require(claim is not None, f"unknown deletion claim {claim_id}")
    obj = claim.get("object")
    require(isinstance(obj, str), "deletion claim needs object")
    for backup in backups.values():
        if obj in set(i for i in backup.get("objects", []) if isinstance(i, str)) and backup.get("status") in {"protected", "retention_required", "verified-protected"}:
            return "deny", "deletion-claim-contradicted-by-retained-copy", backup.get("id") if isinstance(backup.get("id"), str) else None
    for pin in pins.values():
        if pin.get("object") == obj and pin.get("status") == "active":
            return "deny", "deletion-claim-contradicted-by-retained-copy", pin.get("id") if isinstance(pin.get("id"), str) else None
    for hold in holds.values():
        objects = set(i for i in hold.get("objects", []) if isinstance(i, str))
        if (hold.get("object") == obj or obj in objects) and hold.get("status") == "active":
            return "deny", "deletion-claim-contradicted-by-retained-copy", hold.get("id") if isinstance(hold.get("id"), str) else None
    proof_id = claim.get("sanitization_proof")
    proof = proofs.get(proof_id) if isinstance(proof_id, str) else None
    if proof is None or proof.get("status") != "verified":
        return "deny", "deletion-proof-missing", None
    if proof.get("object") != obj:
        return "deny", "deletion-proof-subject-mismatch", None
    claimed_level = claim.get("claimed_level", "tombstone")
    actual_level = proof.get("level", "tombstone")
    order = {"tombstone": 0, "clear": 1, "crypto_erase": 2, "purge": 3, "destroy": 4}
    if order.get(actual_level, -1) < order.get(claimed_level, 99):
        return "deny", "sanitization-level-mismatch", proof.get("id") if isinstance(proof.get("id"), str) else None
    if claim.get("status") not in {"evidence_complete", "verified"}:
        return "deny", "deletion-claim-not-complete", None
    return "allow", "deletion-claim-evidence-complete", None



def verifier_root_trusted(
    roots: dict[str, dict[str, Any]],
    root_id: Any,
    context_time: Any = None,
    purpose: str = "transparency_log",
) -> tuple[bool, str]:
    if not isinstance(root_id, str):
        return False, "verifier-root-not-trusted"
    root = roots.get(root_id)
    if root is None or root.get("status") not in {"trusted", "active"}:
        return False, "verifier-root-not-trusted"
    purposes = set(i for i in root.get("purposes", [purpose]) if isinstance(i, str))
    if purpose not in purposes:
        return False, "verifier-root-purpose-mismatch"
    not_after = root.get("not_after")
    if isinstance(context_time, str) and isinstance(not_after, str) and time_reached(context_time, not_after, "verifier_root.not_after"):
        return False, "verifier-root-expired"
    return True, "verifier-root-trusted"


def eval_resolve_dependency_pin(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"name", "version_range", "range", "manifest_only"}:
        return "deny", "dependency-range-not-pin", None
    pins = index(records, "dependency_pins")
    pin_id = op.get("pin")
    pin = pins.get(pin_id)
    require(pin is not None, f"unknown dependency pin {pin_id}")
    if pin.get("status") != "pinned":
        return "deny", "dependency-not-pinned", None
    if pin.get("advisory_status") in {"malicious", "revoked", "blocked"}:
        return "deny", "dependency-advisory-blocked", None
    if op.get("source") is not None and op.get("source") != pin.get("source"):
        return "deny", "dependency-source-mismatch", None
    expected = op.get("resolved_digest", pin.get("resolved_digest"))
    digest = pin.get("digest", pin.get("pinned_digest"))
    if not isinstance(digest, str) or expected != digest or pin.get("resolved_digest", digest) != digest:
        return "deny", "dependency-digest-mismatch", None
    return "allow", "dependency-pin-resolved-exactly", None


def eval_verify_transparency_entry(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("replay_effect") is True or op.get("intent") in {"authorize", "install", "invoke"}:
        return "deny", "transparency-entry-not-authority", None
    entries = index(records, "transparency_entries")
    roots = index(records, "verifier_roots")
    packages = index(records, "package_envelopes")
    attestations = index(records, "provenance_attestations")
    entry_id = op.get("entry")
    entry = entries.get(entry_id)
    require(entry is not None, f"unknown transparency entry {entry_id}")
    if entry.get("status") != "included" or entry.get("inclusion_proof") != "verified":
        return "deny", "transparency-entry-not-included", None
    ok, reason = verifier_root_trusted(roots, entry.get("log_root"), op.get("context_time"), "transparency_log")
    if not ok:
        return "deny", reason, None
    subject_digest = op.get("subject_digest")
    package_id = op.get("package")
    if not isinstance(subject_digest, str) and isinstance(package_id, str) and package_id in packages:
        subject_digest = packages[package_id].get("digest")
    attestation_id = op.get("attestation")
    if not isinstance(subject_digest, str) and isinstance(attestation_id, str) and attestation_id in attestations:
        subject_digest = attestations[attestation_id].get("subject_digest")
    if not isinstance(subject_digest, str) or entry.get("subject_digest") != subject_digest:
        return "deny", "transparency-subject-mismatch", None
    return "allow", "transparency-entry-inclusion-verified", None


def eval_verify_package_install(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"package_name", "sbom", "bom", "provenance", "transparency_entry", "receipt"}:
        return "deny", "package-metadata-not-install-authority", None
    plans = index(records, "install_plans")
    packages = index(records, "package_envelopes")
    attestations = index(records, "provenance_attestations")
    entries = index(records, "transparency_entries")
    roots = index(records, "verifier_roots")
    pins = index(records, "dependency_pins")
    sandboxes = index(records, "sandbox_profiles")
    handles = index(records, "handles")
    plan_id = op.get("plan")
    plan = plans.get(plan_id)
    require(plan is not None, f"unknown install plan {plan_id}")
    if plan.get("status") not in {"approved", "admitted"}:
        return "deny", "install-plan-not-approved", None
    cut = plan.get("approval_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "install-plan-not-approved", None
    authority = cut.get("authority_handle", plan.get("authority_handle"))
    if not isinstance(authority, str) or not has_live_right(handles, authority, "install"):
        return "deny", "install-plan-lacks-live-authority", None
    package_id = plan.get("package")
    package = packages.get(package_id)
    require(package is not None, f"install plan missing package {package_id}")
    digest = package.get("digest")
    if not isinstance(digest, str) or plan.get("digest", digest) != digest:
        return "deny", "package-digest-mismatch", None
    if package.get("signature") != "verified":
        return "deny", "package-signature-not-verified", None
    attestation = attestations.get(plan.get("provenance"))
    if attestation is None or attestation.get("status") != "verified":
        return "deny", "provenance-not-verified", None
    if attestation.get("subject_digest") != digest:
        return "deny", "provenance-subject-mismatch", None
    trusted_builders = set(i for i in plan.get("trusted_builders", []) if isinstance(i, str))
    if trusted_builders and attestation.get("builder") not in trusted_builders:
        return "deny", "provenance-builder-not-trusted", None
    entry = entries.get(plan.get("transparency_entry"))
    if entry is None or entry.get("status") != "included" or entry.get("inclusion_proof") != "verified":
        return "deny", "transparency-entry-not-included", None
    if entry.get("subject_digest") != digest:
        return "deny", "transparency-subject-mismatch", None
    ok, reason = verifier_root_trusted(roots, entry.get("log_root"), op.get("context_time"), "transparency_log")
    if not ok:
        return "deny", reason, None
    for dep_id in plan.get("dependency_pins", []):
        if not isinstance(dep_id, str) or dep_id not in pins:
            return "deny", "dependency-pin-missing", None
        dep = pins[dep_id]
        if dep.get("status") != "pinned":
            return "deny", "dependency-not-pinned", dep_id
        if dep.get("advisory_status") in {"malicious", "revoked", "blocked"}:
            return "deny", "dependency-advisory-blocked", dep_id
        digest_pin = dep.get("digest", dep.get("pinned_digest"))
        if dep.get("resolved_digest", digest_pin) != digest_pin:
            return "deny", "dependency-digest-mismatch", dep_id
    if plan.get("scanner_verdict") not in {"clean", "accepted"}:
        return "deny", "package-admission-not-clean", None
    requested_effects = set(i for i in package.get("requested_effects", []) if isinstance(i, str))
    if "postinstall_execute" in requested_effects and plan.get("postinstall_enabled") is not True:
        return "deny", "postinstall-effect-not-approved", None
    sandbox_id = plan.get("sandbox_profile")
    sandbox = sandboxes.get(sandbox_id)
    if sandbox is None or sandbox.get("status") != "active":
        return "deny", "sandbox-profile-not-active", None
    allowed_effects = set(i for i in sandbox.get("allowed_effects", []) if isinstance(i, str))
    if not requested_effects.issubset(allowed_effects):
        return "deny", "sandbox-profile-blocks-effect", None
    return "allow", "package-install-admitted-with-live-authority", authority


def eval_admit_verifier_root(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"root_claim", "receipt", "transparency_entry"}:
        return "deny", "verifier-root-claim-not-authority", None
    roots = index(records, "verifier_roots")
    root_id = op.get("root")
    root = roots.get(root_id)
    require(root is not None, f"unknown verifier root {root_id}")
    if root.get("status") not in {"candidate", "trusted"}:
        return "deny", "verifier-root-not-candidate", None
    purpose = op.get("purpose", "transparency_log")
    purposes = set(i for i in root.get("purposes", []) if isinstance(i, str))
    if purpose not in purposes:
        return "deny", "verifier-root-purpose-mismatch", None
    warrant = root.get("rotation_warrant")
    if not isinstance(warrant, dict) or warrant.get("approved") is not True:
        return "deny", "verifier-root-rotation-not-approved", None
    threshold = warrant.get("threshold")
    signatures = warrant.get("signatures")
    require(isinstance(threshold, int) and isinstance(signatures, int), "verifier root rotation threshold/signatures must be integers")
    if signatures < threshold:
        return "deny", "verifier-root-threshold-not-met", None
    not_after = root.get("not_after")
    context_time = op.get("context_time")
    if isinstance(not_after, str) and isinstance(context_time, str) and time_reached(context_time, not_after, "verifier_root.not_after"):
        return "deny", "verifier-root-expired", None
    return "allow", "verifier-root-admitted-by-threshold-warrant", None


def eval_bind_extension_tool(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"manifest", "extension_badge", "installed_badge"}:
        return "deny", "extension-manifest-not-tool-authority", None
    manifests = index(records, "extension_manifests")
    schemas = index(records, "tool_schemas")
    bindings = index(records, "tool_bindings")
    plans = index(records, "install_plans")
    sandboxes = index(records, "sandbox_profiles")
    handles = index(records, "handles")
    binding_id = op.get("binding")
    binding = bindings.get(binding_id)
    require(binding is not None, f"unknown tool binding {binding_id}")
    if binding.get("status") != "bound":
        return "deny", "tool-binding-not-bound", None
    manifest = manifests.get(binding.get("manifest"))
    if manifest is None or manifest.get("status") not in {"installed", "verified"} or manifest.get("signature") != "verified":
        return "deny", "extension-manifest-not-verified", None
    schema = schemas.get(binding.get("schema"))
    if schema is None or schema.get("status") != "active":
        return "deny", "tool-schema-not-active", None
    if manifest.get("schema_digest") != schema.get("digest") or binding.get("schema_digest") != schema.get("digest"):
        return "deny", "tool-schema-digest-mismatch", None
    plan = plans.get(manifest.get("install_plan"))
    if plan is None or plan.get("status") not in {"approved", "admitted"}:
        return "deny", "extension-install-not-admitted", None
    manifest_rights = set(i for i in manifest.get("declared_rights", []) if isinstance(i, str))
    approved_rights = set(i for i in plan.get("approved_rights", []) if isinstance(i, str))
    if approved_rights and not manifest_rights.issubset(approved_rights):
        return "deny", "extension-rights-exceed-admission", None
    required_rights = set(i for i in schema.get("required_rights", []) if isinstance(i, str))
    if not required_rights.issubset(manifest_rights):
        return "deny", "tool-schema-effect-not-declared", None
    sandbox = sandboxes.get(binding.get("sandbox_profile", manifest.get("sandbox_profile", plan.get("sandbox_profile"))))
    if sandbox is None or sandbox.get("status") != "active":
        return "deny", "sandbox-profile-not-active", None
    allowed_effects = set(i for i in sandbox.get("allowed_effects", []) if isinstance(i, str))
    schema_effects = set(i for i in schema.get("effects", []) if isinstance(i, str))
    if not schema_effects.issubset(allowed_effects):
        return "deny", "sandbox-profile-blocks-effect", None
    authority = binding.get("authority_handle")
    if not isinstance(authority, str) or not has_live_right(handles, authority, "bind_tool"):
        return "deny", "tool-binding-lacks-live-authority", None
    return "allow", "extension-tool-bound-to-verified-schema", authority


def eval_invoke_extension_tool(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"installed_tool", "tool_schema", "manifest", "palette_card", "receipt"}:
        return "deny", "tool-metadata-not-invocation-authority", None
    bindings = index(records, "tool_bindings")
    schemas = index(records, "tool_schemas")
    manifests = index(records, "extension_manifests")
    plans = index(records, "action_plans")
    sandboxes = index(records, "sandbox_profiles")
    handles = index(records, "handles")
    binding_id = op.get("binding")
    binding = bindings.get(binding_id)
    require(binding is not None, f"unknown tool binding {binding_id}")
    if binding.get("status") != "bound":
        return "deny", "tool-binding-not-bound", None
    manifest = manifests.get(binding.get("manifest"))
    if manifest is None or manifest.get("status") not in {"installed", "verified"}:
        return "deny", "extension-manifest-not-verified", None
    schema = schemas.get(binding.get("schema"))
    if schema is None or schema.get("status") != "active":
        return "deny", "tool-schema-not-active", None
    if binding.get("schema_digest") != schema.get("digest"):
        return "deny", "tool-schema-digest-mismatch", None
    sandbox = sandboxes.get(binding.get("sandbox_profile", manifest.get("sandbox_profile")))
    if sandbox is None or sandbox.get("status") != "active":
        return "deny", "sandbox-profile-not-active", None
    effects = set(i for i in schema.get("effects", []) if isinstance(i, str))
    allowed = set(i for i in sandbox.get("allowed_effects", []) if isinstance(i, str))
    if not effects.issubset(allowed):
        return "deny", "sandbox-profile-blocks-effect", None
    plan = plans.get(op.get("plan"))
    require(plan is not None, f"unknown action plan {op.get('plan')}")
    if plan.get("typed") is not True:
        return "deny", "action-plan-not-typed", None
    if plan.get("tool_binding") != binding_id:
        return "deny", "action-plan-tool-mismatch", None
    cut = plan.get("approval_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "action-plan-not-approved", None
    want = op.get("want")
    if not isinstance(want, str):
        rights = [r for r in schema.get("required_rights", []) if isinstance(r, str)]
        want = rights[0] if rights else plan.get("effect", "execute")
    for hid in cut.get("authority_slots", []):
        if isinstance(hid, str) and has_live_right(handles, hid, want):
            return "allow", "approved-tool-invocation-with-live-authority", hid
    return "deny", "tool-invocation-lacks-live-authority", None


def eval_reserve_budget(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"quota_card", "budget_card", "metering_receipt", "receipt"}:
        return "deny", "budget-metadata-not-authority", None
    budgets = index(records, "resource_budgets")
    reservations = index(records, "spend_reservations")
    handles = index(records, "handles")
    budget_id = op.get("budget")
    budget = budgets.get(budget_id)
    require(budget is not None, f"unknown resource budget {budget_id}")
    reservation_id = op.get("reservation")
    reservation = reservations.get(reservation_id)
    require(reservation is not None, f"unknown spend reservation {reservation_id}")
    if budget.get("status") != "active":
        return "deny", "budget-not-active", None
    context_time = op.get("context_time")
    expires_at = budget.get("period_expires_at")
    if isinstance(context_time, str) and isinstance(expires_at, str) and time_reached(context_time, expires_at, "resource_budget.period"):
        return "deny", "budget-window-expired", None
    if reservation.get("status") != "pending":
        return "deny", "reservation-not-pending", None
    if reservation.get("budget") != budget_id or reservation.get("scope") != budget.get("scope"):
        return "deny", "budget-scope-mismatch", None
    amount = as_number(op.get("amount", reservation.get("amount")), "reservation.amount")
    remaining = as_number(budget.get("limit", 0), "resource_budget.limit") - as_number(budget.get("spent", 0), "resource_budget.spent") - as_number(budget.get("reserved", 0), "resource_budget.reserved")
    if amount > remaining:
        return "deny", "budget-exceeded", None
    hid = reservation.get("authority_handle", budget.get("authority_handle"))
    if not handle_has_any_right(handles, hid, {"reserve_budget", "spend"}):
        return "deny", "reservation-payer-handle-revoked", None
    return "allow", "budget-reservation-admitted", hid if isinstance(hid, str) else None


def eval_admit_rate_limit(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"receipt", "rate_limit_receipt", "rate_card"}:
        return "deny", "rate-limit-receipt-not-authority", None
    limiters = index(records, "rate_limiters")
    handles = index(records, "handles")
    limiter_id = op.get("limiter")
    limiter = limiters.get(limiter_id)
    require(limiter is not None, f"unknown rate limiter {limiter_id}")
    if limiter.get("status") != "active":
        return "deny", "rate-limit-not-active", None
    context_time = op.get("context_time")
    expires_at = limiter.get("window_expires_at")
    if isinstance(context_time, str) and isinstance(expires_at, str) and time_reached(context_time, expires_at, "rate_limiter.window"):
        return "deny", "rate-limit-window-stale", None
    tokens = as_number(limiter.get("tokens", 0), "rate_limiter.tokens")
    if tokens <= 0:
        return "deny", "rate-limit-exhausted", None
    hid = limiter.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"invoke", "schedule"}):
        return "deny", "rate-limit-lacks-live-authority", None
    return "allow", "rate-limit-token-admitted", hid if isinstance(hid, str) else None


def eval_start_background_job(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"queued_job", "job_card", "receipt"} or op.get("replay_effect") is True:
        return "deny", "queued-job-not-authority", None
    jobs = index(records, "background_jobs")
    reservations = index(records, "spend_reservations")
    limiters = index(records, "rate_limiters")
    plans = index(records, "action_plans")
    handles = index(records, "handles")
    job_id = op.get("job")
    job = jobs.get(job_id)
    require(job is not None, f"unknown background job {job_id}")
    if job.get("status") != "queued":
        return "deny", "background-job-not-queued", None
    context_time = op.get("context_time")
    lease_expires = job.get("queue_lease_expires_at")
    if isinstance(context_time, str) and isinstance(lease_expires, str) and time_reached(context_time, lease_expires, "background_job.queue_lease"):
        return "deny", "job-queue-lease-expired", None
    reservation = reservations.get(job.get("budget_reservation"))
    if reservation is None or reservation.get("status") not in {"reserved", "approved"}:
        return "deny", "background-job-lacks-budget-reservation", None
    limiter_id = job.get("rate_limiter")
    if isinstance(limiter_id, str):
        limiter = limiters.get(limiter_id)
        if limiter is None or limiter.get("status") != "active" or as_number(limiter.get("tokens", 0), "rate_limiter.tokens") <= 0:
            return "deny", "background-job-rate-limit-blocked", None
    plan = plans.get(job.get("plan", op.get("plan")))
    require(plan is not None, f"unknown action plan for background job {job_id}")
    if plan.get("typed") is not True:
        return "deny", "action-plan-not-typed", None
    cut = plan.get("approval_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "action-plan-not-approved", None
    want = job.get("required_right", op.get("want", plan.get("effect", "execute")))
    for hid in cut.get("authority_slots", []):
        if isinstance(hid, str) and has_live_right(handles, hid, want):
            return "allow", "background-job-started-with-live-authority", hid
    return "deny", "background-job-lacks-live-authority", None


def eval_hydrate_cache_entry(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"cache_entry", "cache_card", "receipt"}:
        return "deny", "cache-entry-not-authority", None
    entries = index(records, "cache_entries")
    handles = index(records, "handles")
    entry_id = op.get("cache_entry")
    entry = entries.get(entry_id)
    require(entry is not None, f"unknown cache entry {entry_id}")
    if entry.get("status") == "evicted":
        return "deny", "cache-entry-evicted", None
    if entry.get("status") not in {"warm", "cold", "resident"}:
        return "deny", "cache-entry-not-usable", None
    if entry.get("source_epoch") != entry.get("observed_epoch"):
        return "deny", "cache-source-epoch-mismatch", None
    if entry.get("pressure_status") == "above_limit" and entry.get("pin") != "active":
        return "deny", "cache-pressure-without-pin", None
    hid = entry.get("source_handle", op.get("handle"))
    if not handle_has_any_right(handles, hid, {"read", "hydrate"}):
        return "deny", "cache-entry-lacks-live-source-authority", None
    return "allow", "cache-hydrated-with-live-source-authority", hid if isinstance(hid, str) else None


def eval_emit_capacity_signal(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"capacity_signal", "capacity_meter", "receipt"} or op.get("as_authority") is True:
        return "deny", "capacity-signal-not-authority", None
    signals = index(records, "capacity_signals")
    handles = index(records, "handles")
    signal_id = op.get("signal")
    signal = signals.get(signal_id)
    require(signal is not None, f"unknown capacity signal {signal_id}")
    if signal.get("status") not in {"sealed", "ready"}:
        return "deny", "capacity-signal-not-sealed", None
    cut = signal.get("approval_cut")
    if not isinstance(cut, dict) or cut.get("approved") is not True:
        return "deny", "capacity-signal-not-approved", None
    if signal.get("includes_private_ids") is True:
        return "deny", "capacity-signal-leaks-private-membership", None
    if signal.get("granularity") in {"exact", "per_object", "per_principal"} and signal.get("exact_allowed") is not True:
        return "deny", "capacity-signal-too-precise", None
    hid = signal.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"observe_capacity"}):
        return "deny", "capacity-signal-lacks-live-observe-authority", None
    return "allow", "coarse-capacity-signal-emitted", hid if isinstance(hid, str) else None


def eval_settle_metering_receipt(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"metering_receipt", "receipt", "charge_card"} or op.get("replay_effect") is True:
        return "deny", "metering-receipt-not-authority", None
    receipts = index(records, "metering_receipts")
    reservations = index(records, "spend_reservations")
    handles = index(records, "handles")
    receipt_id = op.get("receipt")
    receipt = receipts.get(receipt_id)
    require(receipt is not None, f"unknown metering receipt {receipt_id}")
    if receipt.get("status") in {"settled", "spent"}:
        return "deny", "metering-receipt-already-settled", None
    if receipt.get("status") != "prepared":
        return "deny", "metering-receipt-not-prepared", None
    reservation = reservations.get(receipt.get("reservation"))
    if reservation is None or reservation.get("status") not in {"reserved", "approved"}:
        return "deny", "metering-reservation-not-live", None
    if op.get("event_digest", receipt.get("event_digest")) != receipt.get("event_digest"):
        return "deny", "metering-event-mismatch", None
    amount = as_number(receipt.get("amount", 0), "metering_receipt.amount")
    reserved = as_number(reservation.get("amount", 0), "spend_reservation.amount")
    if amount > reserved:
        return "deny", "metering-overcharge", None
    hid = receipt.get("authority_handle", reservation.get("authority_handle"))
    if not handle_has_any_right(handles, hid, {"charge", "settle_budget"}):
        return "deny", "metering-lacks-live-charge-authority", None
    return "allow", "metering-settled-against-reservation", hid if isinstance(hid, str) else None



def assurance_rank(value: Any) -> int:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, str):
        upper = value.upper()
        if upper.startswith("AAL") and upper[3:].isdigit():
            return int(upper[3:])
        if upper.startswith("IAL") and upper[3:].isdigit():
            return int(upper[3:])
    return 0


def eval_verify_identity_session(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"login_badge", "identity_badge", "receipt", "session_card"}:
        return "deny", "identity-badge-not-authority", None
    assertions = index(records, "identity_assertions")
    sessions = index(records, "session_bindings")
    handles = index(records, "handles")
    assertion_id = op.get("assertion")
    session_id = op.get("session")
    assertion = assertions.get(assertion_id)
    session = sessions.get(session_id)
    require(assertion is not None, f"unknown identity assertion {assertion_id}")
    require(session is not None, f"unknown session binding {session_id}")
    if assertion.get("status") != "verified":
        return "deny", "identity-assertion-not-verified", None
    if session.get("status") != "live":
        return "deny", "session-not-live", None
    if session.get("identity_assertion") != assertion_id:
        return "deny", "identity-session-mismatch", None
    subject = op.get("subject", assertion.get("subject"))
    if session.get("subject") != assertion.get("subject") or subject != assertion.get("subject"):
        return "deny", "identity-subject-mismatch", None
    now = op.get("now", session.get("checked_at", ""))
    expires = session.get("expires_at")
    if isinstance(expires, str) and time_reached(now, expires, "session expiry"):
        return "deny", "session-expired", None
    required_aal = op.get("required_aal")
    if required_aal is not None and assurance_rank(session.get("assurance_level")) < assurance_rank(required_aal):
        return "deny", "session-assurance-too-low", None
    hid = session.get("authority_handle")
    want = op.get("want", "authenticate")
    if not handle_has_any_right(handles, hid, {want, "authenticate", "identity"}):
        return "deny", "session-lacks-live-authority", None
    return "allow", "verified-session-with-live-authority", hid if isinstance(hid, str) else None


def eval_redeem_credential_token(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"bearer_token", "token_string", "receipt", "refresh_receipt"}:
        return "deny", "credential-token-not-authority", None
    tokens = index(records, "credential_tokens")
    handles = index(records, "handles")
    token_id = op.get("token")
    token = tokens.get(token_id)
    require(token is not None, f"unknown credential token {token_id}")
    if token.get("status") in {"spent", "revoked", "expired"}:
        return "deny", "credential-token-not-live", None
    now = op.get("now", token.get("checked_at", ""))
    expires = token.get("expires_at")
    if isinstance(expires, str) and time_reached(now, expires, "credential token expiry"):
        return "deny", "credential-token-expired", None
    requested = op.get("scope", token.get("scope"))
    scopes = string_set(token.get("scopes", []), f"credential_tokens.{token_id}.scopes")
    if isinstance(requested, str) and requested not in scopes:
        return "deny", "credential-scope-mismatch", None
    proof = op.get("presented_proof")
    if token.get("sender_constrained") is not True or proof != token.get("proof_key"):
        return "deny", "credential-token-lacks-proof", None
    hid = token.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"use_credential", "external_api", "invoke"}):
        return "deny", "credential-lacks-live-authority", None
    return "allow", "bound-credential-token-with-proof", hid if isinstance(hid, str) else None


def eval_open_encryption_envelope(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"ciphertext", "digest", "receipt", "encrypted_blob"}:
        return "deny", "ciphertext-not-authority", None
    envelopes = index(records, "encryption_envelopes")
    keys = index(records, "key_versions")
    handles = index(records, "handles")
    envelope_id = op.get("envelope")
    envelope = envelopes.get(envelope_id)
    require(envelope is not None, f"unknown encryption envelope {envelope_id}")
    key = keys.get(envelope.get("key_version"))
    if key is None:
        return "deny", "key-version-missing", None
    if envelope.get("algorithm_status") in {"deprecated", "broken"} or key.get("algorithm_status") in {"deprecated", "broken"}:
        return "deny", "algorithm-deprecated", None
    if key.get("status") not in {"active", "primary", "decrypt_only"}:
        return "deny", "key-version-not-active", None
    if key.get("id") != envelope.get("key_version"):
        return "deny", "envelope-key-mismatch", None
    hid = envelope.get("authority_handle", key.get("authority_handle"))
    if not handle_has_any_right(handles, hid, {"decrypt", "read_cleartext"}):
        return "deny", "decryption-lacks-live-authority", None
    return "allow", "decryption-authorized-by-key-and-live-handle", hid if isinstance(hid, str) else None


def eval_rotate_key_version(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"receipt", "rotation_receipt", "key_version"}:
        return "deny", "key-rotation-receipt-not-authority", None
    plans = index(records, "key_rotation_plans")
    keys = index(records, "key_versions")
    handles = index(records, "handles")
    plan_id = op.get("plan")
    plan = plans.get(plan_id)
    require(plan is not None, f"unknown key rotation plan {plan_id}")
    if plan.get("status") != "approved":
        return "deny", "key-rotation-not-approved", None
    if plan.get("rewrap_plan_complete") is not True:
        return "deny", "key-rotation-missing-rewrap-plan", None
    old_key = keys.get(plan.get("old_key"))
    new_key = keys.get(plan.get("new_key"))
    if old_key is None or new_key is None:
        return "deny", "key-rotation-key-missing", None
    if new_key.get("status") not in {"active", "primary"}:
        return "deny", "key-rotation-new-key-not-active", None
    hid = plan.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"rotate_key", "admin_key"}):
        return "deny", "key-rotation-lacks-live-authority", None
    return "allow", "approved-key-rotation-with-rewrap", hid if isinstance(hid, str) else None


def eval_lease_secret(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"vault_row", "secret_descriptor", "receipt", "secret_name"}:
        return "deny", "secret-descriptor-not-authority", None
    leases = index(records, "secret_leases")
    handles = index(records, "handles")
    lease_id = op.get("lease")
    lease = leases.get(lease_id)
    require(lease is not None, f"unknown secret lease {lease_id}")
    if lease.get("status") != "active":
        return "deny", "secret-lease-not-active", None
    now = op.get("now", lease.get("checked_at", ""))
    expires = lease.get("expires_at")
    if isinstance(expires, str) and time_reached(now, expires, "secret lease expiry"):
        return "deny", "secret-lease-expired", None
    scope = op.get("scope", lease.get("scope"))
    if isinstance(scope, str) and scope != lease.get("scope"):
        return "deny", "secret-scope-mismatch", None
    hid = lease.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"use_secret", "read_secret"}):
        return "deny", "secret-lease-lacks-live-authority", None
    return "allow", "secret-lease-current-with-live-authority", hid if isinstance(hid, str) else None


def eval_inject_secret(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"tool_schema", "manifest", "receipt", "env_shadow"}:
        return "deny", "secret-injection-plan-not-authority", None
    plans = index(records, "secret_injection_plans")
    leases = index(records, "secret_leases")
    handles = index(records, "handles")
    plan_id = op.get("plan")
    plan = plans.get(plan_id)
    require(plan is not None, f"unknown secret injection plan {plan_id}")
    if plan.get("status") != "approved":
        return "deny", "secret-injection-not-approved", None
    if plan.get("delivery_slot") == "env" and plan.get("env_shadow") == "unredacted" and plan.get("env_allowed") is not True:
        return "deny", "secret-injection-env-shadow-leak", None
    lease = leases.get(plan.get("secret_lease"))
    if lease is None or lease.get("status") != "active":
        return "deny", "secret-injection-lease-not-active", None
    now = op.get("now", plan.get("checked_at", lease.get("checked_at", "")))
    expires = lease.get("expires_at")
    if isinstance(expires, str) and time_reached(now, expires, "secret lease expiry"):
        return "deny", "secret-lease-expired", None
    if plan.get("scope") != lease.get("scope"):
        return "deny", "secret-scope-mismatch", None
    hid = plan.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"inject_secret", "use_secret"}):
        return "deny", "secret-injection-lacks-live-authority", None
    target = plan.get("target_handle")
    if target is not None and not handle_has_any_right(handles, target, {"receive_secret", "invoke"}):
        return "deny", "secret-injection-target-not-live", None
    return "allow", "approved-secret-injection-with-live-lease", hid if isinstance(hid, str) else None


def eval_recover_escrow(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") in {"escrow_ticket", "receipt", "recovery_label"}:
        return "deny", "escrow-ticket-not-authority", None
    warrants = index(records, "escrow_recovery_warrants")
    sessions = index(records, "session_bindings")
    handles = index(records, "handles")
    warrant_id = op.get("warrant")
    warrant = warrants.get(warrant_id)
    require(warrant is not None, f"unknown escrow recovery warrant {warrant_id}")
    if warrant.get("status") != "approved":
        return "deny", "escrow-recovery-not-approved", None
    if warrant.get("quorum_verified") is not True:
        return "deny", "escrow-quorum-missing", None
    now = op.get("now", warrant.get("checked_at", ""))
    expires = warrant.get("expires_at")
    if isinstance(expires, str) and time_reached(now, expires, "escrow warrant expiry"):
        return "deny", "escrow-session-stale", None
    session = sessions.get(warrant.get("session"))
    if session is None or session.get("status") != "live" or session.get("subject") != warrant.get("subject"):
        return "deny", "escrow-session-stale", None
    hid = warrant.get("authority_handle")
    if not handle_has_any_right(handles, hid, {"recover_secret", "decrypt"}):
        return "deny", "escrow-lacks-live-authority", None
    return "allow", "escrow-recovery-quorum-with-live-authority", hid if isinstance(hid, str) else None


def eval_render_secret_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "secret_cards")
    handles = index(records, "handles")
    card_id = op.get("card")
    card = cards.get(card_id)
    require(card is not None, f"unknown secret card {card_id}")
    if card.get("sealed") is not True:
        return "deny", "secret-card-not-sealed", None
    if card.get("includes_secret_material") is True:
        return "deny", "secret-card-leaks-material", None
    slot = card.get("authority_slot")
    has_live = isinstance(slot, str) and handle_has_any_right(handles, slot, {"use_secret", "inject_secret", "decrypt", "recover_secret"})
    if card.get("authority_badge") == "live" and not has_live:
        return "deny", "secret-card-authority-badge-lie", None
    if card.get("redaction") != "redacted":
        return "deny", "secret-card-unredacted", None
    return "allow", "secret-card-redacted-honest", slot if has_live else None


def eval_verify_runtime_posture(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    postures = index(records, "runtime_postures")
    handles = index(records, "handles")
    if op.get("via") == "runtime_posture_only":
        return "deny", "runtime-posture-not-authority", None
    posture_id = op.get("posture")
    posture = postures.get(posture_id)
    if not isinstance(posture_id, str) or posture is None:
        return "deny", "runtime-posture-missing", None
    if posture.get("status") != "active":
        return "deny", "runtime-posture-not-active", None
    if posture.get("attestation_status") != "verified":
        return "deny", "runtime-attestation-not-verified", None
    expected_epoch = op.get("expected_epoch")
    if expected_epoch is not None and posture.get("epoch") != expected_epoch:
        return "deny", "runtime-epoch-mismatch", None
    if posture.get("debug_enabled") is True and op.get("requires_locked_runtime", True):
        return "deny", "runtime-debug-unsealed", None
    authority = op.get("authority")
    if not handle_has_any_right(handles, authority, {"inspect_runtime", "admit_runtime"}):
        return "deny", "runtime-live-authority-missing", None
    return "allow", "runtime-posture-verified", authority if isinstance(authority, str) else None


def eval_admit_network_connector(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    connectors = index(records, "network_connectors")
    handles = index(records, "handles")
    if op.get("via") == "connector_metadata":
        return "deny", "connector-metadata-not-authority", None
    connector_id = op.get("connector")
    connector = connectors.get(connector_id)
    if not isinstance(connector_id, str) or connector is None:
        return "deny", "network-connector-missing", None
    if connector.get("status") != "admitted":
        return "deny", "network-connector-not-admitted", None
    if connector.get("policy_status") != "active":
        return "deny", "network-policy-not-active", None
    if connector.get("dns_proof") != "fresh":
        return "deny", "dns-proof-not-fresh", None
    if connector.get("endpoint") != op.get("endpoint"):
        return "deny", "network-endpoint-mismatch", None
    requested_effects = string_set(op.get("effects", []), "operation.effects")
    allowed_effects = record_fields(connector, "allowed_effects", f"network_connectors.{connector_id}.allowed_effects")
    if not requested_effects.issubset(allowed_effects):
        return "deny", "network-effect-not-allowed", None
    authority = op.get("authority")
    if not handle_has_any_right(handles, authority, {"network_connect", "egress"}):
        return "deny", "network-live-authority-missing", None
    return "allow", "network-connector-admitted", authority if isinstance(authority, str) else None


def eval_redeem_clipboard_parcel(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    parcels = index(records, "clipboard_parcels")
    handles = index(records, "handles")
    if op.get("via") == "clipboard_parcel_only":
        return "deny", "clipboard-parcel-not-authority", None
    parcel_id = op.get("parcel")
    parcel = parcels.get(parcel_id)
    if not isinstance(parcel_id, str) or parcel is None:
        return "deny", "clipboard-parcel-missing", None
    if parcel.get("status") != "fresh":
        return "deny", "clipboard-parcel-not-fresh", None
    now = op.get("now")
    expires_at = parcel.get("expires_at")
    if now is not None and expires_at is not None and time_reached(now, expires_at, "clipboard expiry"):
        return "deny", "clipboard-parcel-expired", None
    if parcel.get("classification") in {"secret", "raw_secret"} or (parcel.get("contains_secret") is True and parcel.get("redacted") is not True):
        return "deny", "clipboard-secret-leak-denied", None
    expected_source_epoch = op.get("expected_source_epoch")
    if expected_source_epoch is not None and parcel.get("source_epoch") != expected_source_epoch:
        return "deny", "clipboard-source-epoch-mismatch", None
    authority = op.get("authority")
    if not handle_has_any_right(handles, authority, {"clipboard_paste", "read_clipboard"}):
        return "deny", "clipboard-live-authority-missing", None
    target = op.get("target")
    if target is not None and not handle_has_any_right(handles, target, {"write", "paste_target"}):
        return "deny", "clipboard-target-authority-missing", None
    return "allow", "clipboard-parcel-redeemed", authority if isinstance(authority, str) else None


def eval_redeem_dragdrop_parcel(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    parcels = index(records, "dragdrop_parcels")
    handles = index(records, "handles")
    if op.get("via") == "dragdrop_parcel_only":
        return "deny", "dragdrop-parcel-not-authority", None
    parcel_id = op.get("parcel")
    parcel = parcels.get(parcel_id)
    if not isinstance(parcel_id, str) or parcel is None:
        return "deny", "dragdrop-parcel-missing", None
    if parcel.get("status") != "fresh":
        return "deny", "dragdrop-parcel-not-fresh", None
    now = op.get("now")
    expires_at = parcel.get("expires_at")
    if now is not None and expires_at is not None and time_reached(now, expires_at, "drag/drop expiry"):
        return "deny", "dragdrop-parcel-expired", None
    if parcel.get("trusted_path") is not True or parcel.get("overlay_suspected") is True:
        return "deny", "dragdrop-trusted-path-missing", None
    if parcel.get("gesture_status") != "valid":
        return "deny", "dragdrop-gesture-not-valid", None
    authority = op.get("authority")
    if not handle_has_any_right(handles, authority, {"drop_import", "import"}):
        return "deny", "dragdrop-live-authority-missing", None
    return "allow", "dragdrop-parcel-redeemed", authority if isinstance(authority, str) else None


def eval_bind_peripheral_device(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    grants = index(records, "peripheral_grants")
    attestations = index(records, "device_attestations")
    handles = index(records, "handles")
    if op.get("via") == "device_descriptor_only":
        return "deny", "device-descriptor-not-authority", None
    grant_id = op.get("grant")
    grant = grants.get(grant_id)
    if not isinstance(grant_id, str) or grant is None:
        return "deny", "peripheral-grant-missing", None
    if grant.get("status") != "approved":
        return "deny", "peripheral-grant-not-approved", None
    attestation = attestations.get(grant.get("device_attestation"))
    if attestation is None or attestation.get("status") != "verified":
        return "deny", "device-attestation-not-verified", None
    if attestation.get("revoked") is True:
        return "deny", "device-attestation-revoked", None
    requested_class = op.get("device_class")
    if requested_class != grant.get("device_class") or requested_class != attestation.get("device_class"):
        return "deny", "peripheral-class-mismatch", None
    if grant.get("sandbox_fit") is not True:
        return "deny", "peripheral-sandbox-fit-missing", None
    authority = op.get("authority")
    if not handle_has_any_right(handles, authority, {"peripheral_bind", "device_use"}):
        return "deny", "peripheral-live-authority-missing", None
    return "allow", "peripheral-device-bound", authority if isinstance(authority, str) else None


def eval_observe_sensor_sample(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    observations = index(records, "sensor_observations")
    handles = index(records, "handles")
    if op.get("via") == "sensor_sample_only":
        return "deny", "sensor-sample-not-authority", None
    sample_id = op.get("sample")
    sample = observations.get(sample_id)
    if not isinstance(sample_id, str) or sample is None:
        return "deny", "sensor-sample-missing", None
    if sample.get("status") != "current":
        return "deny", "sensor-sample-not-current", None
    if sample.get("consent_status") != "active":
        return "deny", "sensor-consent-not-active", None
    if sample.get("precision") == "exact" or sample.get("includes_identifier") is True:
        return "deny", "sensor-precision-leaks-identity", None
    purpose = op.get("purpose")
    allowed_purposes = record_fields(sample, "allowed_purposes", f"sensor_observations.{sample_id}.allowed_purposes")
    if purpose not in allowed_purposes:
        return "deny", "sensor-purpose-not-allowed", None
    if sample.get("over_rate") is True:
        return "deny", "sensor-rate-limit-exceeded", None
    authority = op.get("authority")
    if not handle_has_any_right(handles, authority, {"observe_sensor", "read_sensor"}):
        return "deny", "sensor-live-authority-missing", None
    return "allow", "sensor-observation-redeemed", authority if isinstance(authority, str) else None


def eval_apply_transform_plan(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    plans = index(records, "transform_plans")
    handles = index(records, "handles")
    if op.get("via") == "recipe":
        return "deny", "transform-recipe-not-authority", None
    plan_id = op.get("plan")
    plan = plans.get(plan_id)
    if not isinstance(plan_id, str) or plan is None:
        return "deny", "transform-plan-missing", None
    if plan.get("status") != "approved" or plan.get("approved_cut") is not True:
        return "deny", "transform-plan-not-approved", None
    source_handle = plan.get("source_handle", op.get("source_handle"))
    if not handle_has_any_right(handles, source_handle, {"read", "transform"}):
        return "deny", "transform-source-authority-missing", None
    if plan.get("output_claims_source_authority") is True:
        return "deny", "transform-output-claims-source-authority", None
    if plan.get("lossy") is True and plan.get("loss_disclosed") is not True:
        return "deny", "lossy-transform-undisclosed", None
    result_handle = plan.get("result_handle")
    if not isinstance(result_handle, str) or not has_any_live_right(handles, result_handle):
        return "deny", "transform-result-handle-missing", None
    return "allow", "transform-plan-approved", result_handle


def eval_decode_codec_payload(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    codecs = index(records, "codec_profiles")
    handles = index(records, "handles")
    if op.get("via") == "profile_metadata":
        return "deny", "codec-profile-not-authority", None
    profile_id = op.get("profile")
    profile = codecs.get(profile_id)
    if not isinstance(profile_id, str) or profile is None or profile.get("status") != "active":
        return "deny", "codec-profile-not-active", None
    if profile.get("handler_pinned") is not True:
        return "deny", "codec-handler-not-pinned", None
    media_type = op.get("media_type")
    accepted = record_fields(profile, "accepted_media_types", f"codec_profiles.{profile_id}.accepted_media_types")
    if media_type not in accepted:
        return "deny", "codec-media-type-mismatch", None
    if op.get("active_content") is True and profile.get("allow_active_content") is not True:
        return "deny", "codec-active-content-denied", None
    authority = op.get("authority")
    if not handle_has_any_right(handles, authority, {"read", "decode"}):
        return "deny", "codec-source-authority-missing", None
    return "allow", "codec-safe-preview-rendered", authority if isinstance(authority, str) else None


def eval_apply_schema_migration(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    migrations = index(records, "schema_migrations")
    handles = index(records, "handles")
    if op.get("via") == "receipt":
        return "deny", "migration-receipt-not-authority", None
    migration_id = op.get("migration")
    migration = migrations.get(migration_id)
    if not isinstance(migration_id, str) or migration is None:
        return "deny", "schema-migration-missing", None
    if migration.get("status") != "verified":
        return "deny", "schema-migration-not-verified", None
    if migration.get("current_validator") != op.get("validator"):
        return "deny", "schema-validator-not-current", None
    authority = migration.get("source_handle", op.get("authority"))
    if not handle_has_any_right(handles, authority, {"read", "migrate"}):
        return "deny", "migration-source-authority-missing", None
    if migration.get("lossy") is True and migration.get("loss_disclosed") is not True:
        return "deny", "migration-loss-undisclosed", None
    result_handle = migration.get("result_handle")
    if not isinstance(result_handle, str) or not has_any_live_right(handles, result_handle):
        return "deny", "migration-result-handle-missing", None
    return "allow", "schema-migration-verified", result_handle


def eval_apply_patch_set(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    patches = index(records, "patch_sets")
    handles = index(records, "handles")
    patch_id = op.get("patch")
    patch = patches.get(patch_id)
    if not isinstance(patch_id, str) or patch is None:
        return "deny", "patch-set-missing", None
    if patch.get("summary_only") is True or op.get("via") == "summary":
        return "deny", "patch-summary-not-patch", None
    if patch.get("status") != "verified":
        return "deny", "patch-set-not-verified", None
    if patch.get("observed_base") != patch.get("current_base"):
        return "deny", "patch-base-stale", None
    if patch.get("expands_authority") is True:
        return "deny", "patch-expands-authority", None
    authority = patch.get("source_handle", op.get("authority"))
    if not handle_has_any_right(handles, authority, {"write", "patch"}):
        return "deny", "patch-source-authority-missing", None
    result_handle = patch.get("result_handle")
    if not isinstance(result_handle, str) or not has_any_live_right(handles, result_handle):
        return "deny", "patch-result-handle-missing", None
    return "allow", "patch-current-base-applied", result_handle


def eval_attach_annotation_layer(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    annotations = index(records, "annotation_layers")
    handles = index(records, "handles")
    layer_id = op.get("layer")
    layer = annotations.get(layer_id)
    if not isinstance(layer_id, str) or layer is None:
        return "deny", "annotation-layer-missing", None
    if layer.get("label_claims_policy") is True:
        return "deny", "annotation-label-not-policy", None
    if layer.get("selector_status") != "current":
        return "deny", "annotation-target-drift", None
    if layer.get("sensitive_selector") is True and layer.get("redaction_view") is None:
        return "deny", "annotation-selector-leaks-secret", None
    authority = layer.get("authority", op.get("authority"))
    if not handle_has_any_right(handles, authority, {"annotate", "write_annotation"}):
        return "deny", "annotation-authority-missing", None
    return "allow", "annotation-layer-attached", authority if isinstance(authority, str) else None


def eval_verify_lineage_link(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    links = index(records, "lineage_links")
    handles = index(records, "handles")
    if op.get("via") == "receipt":
        return "deny", "lineage-receipt-not-authority", None
    link_id = op.get("lineage")
    link = links.get(link_id)
    if not isinstance(link_id, str) or link is None:
        return "deny", "lineage-link-missing", None
    if link.get("complete") is not True or link.get("source_hashes_match") is not True:
        return "deny", "lineage-source-missing", None
    if link.get("ambiguous_transform") is True:
        return "deny", "lineage-transform-ambiguous", None
    if link.get("claims_authority") is True:
        return "deny", "lineage-claims-authority", None
    authority = op.get("authority", link.get("authority"))
    if not handle_has_any_right(handles, authority, {"inspect_lineage", "read"}):
        return "deny", "lineage-inspection-authority-missing", None
    return "allow", "lineage-chain-verified", authority if isinstance(authority, str) else None


def eval_render_preview_artifact(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    previews = index(records, "preview_artifacts")
    redactions = index(records, "redaction_views")
    handles = index(records, "handles")
    preview_id = op.get("preview")
    preview = previews.get(preview_id)
    if not isinstance(preview_id, str) or preview is None:
        return "deny", "preview-artifact-missing", None
    if preview.get("claims_source_authority") is True or op.get("via") == "preview_artifact":
        return "deny", "preview-not-source-authority", None
    fields = record_fields(preview, "fields", f"preview_artifacts.{preview_id}.fields")
    if preview.get("requires_redaction") is True:
        ok, reason = redaction_view_check(redactions, preview.get("redaction_view"), fields, "preview")
        if not ok:
            return "deny", reason, None
    authority = preview.get("source_handle", op.get("authority"))
    if not handle_has_any_right(handles, authority, {"read", "preview"}):
        return "deny", "preview-source-authority-missing", None
    return "allow", "preview-redacted-rendered", authority if isinstance(authority, str) else None


def eval_admit_canonicalization_claim(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    profiles = index(records, "canonicalization_profiles")
    handles = index(records, "handles")
    profile_id = op.get("profile")
    profile = profiles.get(profile_id)
    if not isinstance(profile_id, str) or profile is None or profile.get("status") != "active":
        return "deny", "canonicalization-profile-not-active", None
    if profile.get("confusable_collision") is True:
        return "deny", "canonicalization-confusable-collision", None
    if profile.get("equivalence_witness") is not True:
        return "deny", "canonicalization-equivalence-missing", None
    if profile.get("claims_original_digest") is True:
        return "deny", "canonical-digest-not-original", None
    authority = op.get("authority", profile.get("source_handle"))
    if not handle_has_any_right(handles, authority, {"read", "canonicalize"}):
        return "deny", "canonicalization-authority-missing", None
    return "allow", "canonicalization-equivalence-admitted", authority if isinstance(authority, str) else None



def eval_evaluate_classification_mark(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    marks = index(records, "classification_marks")
    handles = index(records, "handles")
    if op.get("via") == "label":
        return "deny", "classification-label-not-authority", None
    if op.get("via") == "receipt":
        return "deny", "classification-receipt-not-authority", None
    mark_id = op.get("mark")
    mark = marks.get(mark_id)
    if not isinstance(mark_id, str) or mark is None:
        return "deny", "classification-mark-missing", None
    if mark.get("status") != "verified":
        return "deny", "classification-mark-not-verified", None
    if mark.get("classifier_status") != "current":
        return "deny", "classification-classifier-stale", None
    if mark.get("conflict") is True:
        return "deny", "classification-conflict-unresolved", None
    subject = op.get("subject")
    if isinstance(subject, str) and mark.get("subject") != subject:
        return "deny", "classification-subject-mismatch", None
    if mark.get("clearance_claims_access") is True:
        return "deny", "classification-clearance-not-authority", None
    authority = op.get("authority", mark.get("authority"))
    if not handle_has_any_right(handles, authority, {"inspect_classification", "classify", "read"}):
        return "deny", "classification-authority-missing", None
    return "allow", "classification-mark-accounted", authority if isinstance(authority, str) else None


def eval_authorize_license_use(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    terms = index(records, "license_terms")
    handles = index(records, "handles")
    if op.get("via") in {"license_text", "spdx_id", "label"}:
        return "deny", "license-label-not-authority", None
    if op.get("via") == "receipt":
        return "deny", "license-receipt-not-use-authority", None
    term_id = op.get("license")
    term = terms.get(term_id)
    if not isinstance(term_id, str) or term is None:
        return "deny", "license-term-missing", None
    if term.get("status") != "active":
        return "deny", "license-term-not-active", None
    use = op.get("use")
    permitted = record_fields(term, "permitted_uses", f"license_terms.{term_id}.permitted_uses")
    prohibited = record_fields(term, "prohibited_uses", f"license_terms.{term_id}.prohibited_uses")
    if isinstance(use, str) and use in prohibited:
        return "deny", "license-use-prohibited", None
    if not isinstance(use, str) or use not in permitted:
        return "deny", "license-use-not-permitted", None
    if term.get("accepted_terms") is not True:
        return "deny", "license-terms-not-accepted", None
    required = record_fields(term, "required_obligations", f"license_terms.{term_id}.required_obligations")
    satisfied = record_fields(term, "satisfied_obligations", f"license_terms.{term_id}.satisfied_obligations") | string_set(op.get("satisfied_obligations", []), "operation.satisfied_obligations")
    if not required.issubset(satisfied):
        return "deny", "license-obligation-unsatisfied", None
    authority = op.get("authority", term.get("authority"))
    required_right = term.get("required_right", use)
    if not isinstance(required_right, str) or not handle_has_any_right(handles, authority, {required_right, "use", use}):
        return "deny", "license-live-authority-missing", None
    subject = term.get("subject")
    if isinstance(subject, str) and object_for_handle(handles, authority) != subject:
        return "deny", "license-subject-handle-mismatch", None
    return "allow", "license-use-authorized", authority if isinstance(authority, str) else None


def eval_check_jurisdiction_fence(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    fences = index(records, "jurisdiction_fences")
    handles = index(records, "handles")
    if op.get("via") in {"region_label", "jurisdiction_label", "badge"}:
        return "deny", "jurisdiction-label-not-authority", None
    fence_id = op.get("fence")
    fence = fences.get(fence_id)
    if not isinstance(fence_id, str) or fence is None:
        return "deny", "jurisdiction-fence-missing", None
    if fence.get("status") != "active":
        return "deny", "jurisdiction-fence-not-active", None
    source_realm = op.get("source_realm")
    if isinstance(source_realm, str) and fence.get("source_realm") != source_realm:
        return "deny", "jurisdiction-source-mismatch", None
    destination = op.get("destination")
    allowed = record_fields(fence, "allowed_destinations", f"jurisdiction_fences.{fence_id}.allowed_destinations")
    if not isinstance(destination, str) or destination not in allowed:
        return "deny", "jurisdiction-destination-denied", None
    if fence.get("route_status") != "approved" or fence.get("route_epoch") != fence.get("current_epoch"):
        return "deny", "jurisdiction-route-not-current", None
    if fence.get("export_controlled") is True and fence.get("license_required") is True and fence.get("license_granted") is not True:
        return "deny", "jurisdiction-export-license-missing", None
    authority = op.get("authority", fence.get("authority"))
    if not handle_has_any_right(handles, authority, {"export", "egress", "disclose"}):
        return "deny", "jurisdiction-egress-authority-missing", None
    return "allow", "jurisdiction-fence-passed", authority if isinstance(authority, str) else None


def eval_enforce_compliance_obligation(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    obligations = index(records, "compliance_obligations")
    handles = index(records, "handles")
    if op.get("via") == "receipt" or op.get("discharge_by") == "receipt":
        return "deny", "obligation-receipt-not-discharge", None
    obligation_id = op.get("obligation")
    obligation = obligations.get(obligation_id)
    if not isinstance(obligation_id, str) or obligation is None:
        return "deny", "obligation-missing", None
    if obligation.get("status") != "active":
        return "deny", "obligation-not-active", None
    required = record_fields(obligation, "required_artifacts", f"compliance_obligations.{obligation_id}.required_artifacts")
    provided = record_fields(obligation, "satisfied_artifacts", f"compliance_obligations.{obligation_id}.satisfied_artifacts") | string_set(op.get("provided_artifacts", []), "operation.provided_artifacts")
    if not required.issubset(provided):
        return "deny", "obligation-artifact-missing", None
    required_sink = obligation.get("required_sink")
    if isinstance(required_sink, str) and op.get("sink") != required_sink:
        return "deny", "obligation-sink-mismatch", None
    authority = op.get("authority", obligation.get("authority"))
    required_right = obligation.get("required_right", "export")
    if not isinstance(required_right, str) or not handle_has_any_right(handles, authority, {required_right, "comply", "export", "publish"}):
        return "deny", "obligation-authority-missing", None
    return "allow", "compliance-obligation-satisfied", authority if isinstance(authority, str) else None


def eval_approve_public_release(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    reviews = index(records, "public_release_reviews")
    redactions = index(records, "redaction_views")
    handles = index(records, "handles")
    if op.get("via") == "public_label":
        return "deny", "public-label-not-release", None
    if op.get("via") == "receipt":
        return "deny", "public-release-receipt-not-authority", None
    review_id = op.get("review")
    review = reviews.get(review_id)
    if not isinstance(review_id, str) or review is None:
        return "deny", "public-release-review-missing", None
    if review.get("status") != "approved":
        return "deny", "public-release-not-approved", None
    if review.get("reviewer_verified") is not True:
        return "deny", "public-reviewer-not-verified", None
    if review.get("review_epoch") != review.get("current_epoch"):
        return "deny", "public-release-review-stale", None
    if review.get("classification") != "public" and review.get("declassified") is not True:
        return "deny", "public-release-classification-blocked", None
    if review.get("requires_redaction") is True:
        fields = record_fields(review, "fields", f"public_release_reviews.{review_id}.fields")
        ok, reason = redaction_view_check(redactions, review.get("redaction_view"), fields, "public-release")
        if not ok:
            return "deny", reason, None
    if review.get("obligations_satisfied") is not True:
        return "deny", "public-release-obligations-unsatisfied", None
    authority = op.get("authority", review.get("authority"))
    if not handle_has_any_right(handles, authority, {"export", "publish", "disclose"}):
        return "deny", "public-release-authority-missing", None
    return "allow", "public-release-approved", authority if isinstance(authority, str) else None


def eval_bind_purpose_use(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    bindings = index(records, "purpose_bindings")
    handles = index(records, "handles")
    if op.get("via") == "purpose_statement":
        return "deny", "purpose-statement-not-authority", None
    binding_id = op.get("binding")
    binding = bindings.get(binding_id)
    if not isinstance(binding_id, str) or binding is None:
        return "deny", "purpose-binding-missing", None
    if binding.get("status") != "active":
        return "deny", "purpose-binding-not-active", None
    purpose = op.get("purpose")
    allowed = record_fields(binding, "allowed_purposes", f"purpose_bindings.{binding_id}.allowed_purposes")
    if not isinstance(purpose, str) or purpose not in allowed:
        return "deny", "purpose-not-allowed", None
    if op.get("secondary_use") is True and binding.get("secondary_approved") is not True:
        return "deny", "secondary-purpose-not-approved", None
    if binding.get("retention_budget_status") != "active":
        return "deny", "purpose-retention-budget-missing", None
    authority = op.get("authority", binding.get("authority"))
    required_right = binding.get("required_right", "use")
    if not isinstance(required_right, str) or not handle_has_any_right(handles, authority, {required_right, "use", purpose}):
        return "deny", "purpose-authority-missing", None
    return "allow", "purpose-use-bound", authority if isinstance(authority, str) else None


def eval_render_compliance_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "compliance_cards")
    handles = index(records, "handles")
    reviews = index(records, "public_release_reviews")
    card_id = op.get("card")
    card = cards.get(card_id)
    if not isinstance(card_id, str) or card is None:
        return "deny", "compliance-card-missing", None
    if card.get("status") != "renderable":
        return "deny", "compliance-card-not-renderable", None
    if card.get("exposes_blocked_fields") is True:
        return "deny", "compliance-card-redaction-leak", None
    if card.get("claims_live_authority") is True:
        backing = card.get("backing_handle")
        if not isinstance(backing, str) or not has_any_live_right(handles, backing):
            return "deny", "compliance-card-claims-live", None
    if card.get("claims_clear_to_export") is True:
        review = reviews.get(card.get("release_review"))
        if review is None or review.get("status") != "approved":
            return "deny", "compliance-card-clearance-unbacked", None
    return "allow", "compliance-card-honest", None


def eval_admit_query_scope(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    specs = index(records, "query_specs")
    handles = index(records, "handles")
    if op.get("via") in {"query_text", "saved_query", "result_card"}:
        return "deny", "query-text-not-authority", None
    spec_id = op.get("query")
    spec = specs.get(spec_id)
    if not isinstance(spec_id, str) or spec is None:
        return "deny", "query-spec-missing", None
    if spec.get("status") != "active":
        return "deny", "query-spec-not-active", None
    requested_sources = string_set(op.get("sources", spec.get("requested_sources", [])), "operation.sources")
    allowed_sources = record_fields(spec, "allowed_sources", f"query_specs.{spec_id}.allowed_sources")
    if not requested_sources or not requested_sources.issubset(allowed_sources):
        return "deny", "query-scope-widening", None
    requested_fields = string_set(op.get("fields", spec.get("requested_fields", [])), "operation.fields")
    allowed_fields = record_fields(spec, "allowed_fields", f"query_specs.{spec_id}.allowed_fields")
    if allowed_fields and not requested_fields.issubset(allowed_fields):
        return "deny", "query-field-widening", None
    authority = op.get("authority", spec.get("authority"))
    if not handle_has_any_right(handles, authority, {"query", "read", "search"}):
        return "deny", "query-authority-missing", None
    if spec.get("requires_current_index") is True and spec.get("index_epoch") != spec.get("current_epoch"):
        return "deny", "query-index-stale", None
    return "allow", "query-scope-admitted", authority if isinstance(authority, str) else None


def eval_admit_planner_trace(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    traces = index(records, "planner_traces")
    handles = index(records, "handles")
    if op.get("via") in {"plan_text", "model_proposal", "trace_summary"}:
        return "deny", "planner-proposal-not-authority", None
    trace_id = op.get("trace")
    trace = traces.get(trace_id)
    if not isinstance(trace_id, str) or trace is None:
        return "deny", "planner-trace-missing", None
    if trace.get("status") != "verified":
        return "deny", "planner-trace-not-verified", None
    if trace.get("approved_cut") is not True:
        return "deny", "planner-approval-cut-missing", None
    proposed = record_fields(trace, "proposed_rights", f"planner_traces.{trace_id}.proposed_rights")
    allowed = record_fields(trace, "allowed_rights", f"planner_traces.{trace_id}.allowed_rights")
    if proposed and allowed and not proposed.issubset(allowed):
        return "deny", "planner-rights-widening", None
    if trace.get("scope_widened") is True or trace.get("hidden_effects") is True:
        return "deny", "planner-hidden-widening", None
    authority = op.get("authority", trace.get("authority"))
    if not handle_has_any_right(handles, authority, {"plan", "approve", "invoke"}):
        return "deny", "planner-authority-missing", None
    return "allow", "planner-trace-admitted", authority if isinstance(authority, str) else None


def eval_open_result_member(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    results = index(records, "result_sets")
    handles = index(records, "handles")
    if op.get("via") in {"ranked_hit", "result_id", "answer_snippet"}:
        return "deny", "result-member-not-authority", None
    result_id = op.get("result_set")
    result = results.get(result_id)
    if not isinstance(result_id, str) or result is None:
        return "deny", "result-set-missing", None
    if result.get("status") != "fresh":
        return "deny", "result-set-not-fresh", None
    if result.get("summary_only") is True or result.get("claims_raw_access") is True:
        return "deny", "result-set-summary-not-raw", None
    member = op.get("member")
    members = result.get("members", [])
    require(isinstance(members, list), f"result_sets.{result_id}.members must be a list")
    selected = None
    for row in members:
        if isinstance(row, dict) and row.get("id") == member:
            selected = row
            break
    if selected is None:
        return "deny", "result-member-missing", None
    if selected.get("redaction_status") not in {None, "ok"}:
        return "deny", "result-member-redaction-blocked", None
    handle = selected.get("handle")
    if not handle_has_any_right(handles, handle, {"read", "open"}):
        return "deny", "result-member-handle-missing", None
    return "allow", "result-member-backed-by-live-handle", handle if isinstance(handle, str) else None


def eval_render_aggregation_view(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    views = index(records, "aggregation_views")
    handles = index(records, "handles")
    view_id = op.get("view")
    view = views.get(view_id)
    if not isinstance(view_id, str) or view is None:
        return "deny", "aggregation-view-missing", None
    if view.get("status") != "computed":
        return "deny", "aggregation-view-not-computed", None
    if view.get("raw_rows_exposed") is True:
        return "deny", "aggregation-raw-rows-exposed", None
    if view.get("claims_exact_membership") is True or view.get("membership_oracle") is True:
        return "deny", "aggregation-membership-oracle", None
    count = as_number(view.get("cohort_count", 0), f"aggregation_views.{view_id}.cohort_count")
    threshold = as_number(view.get("k_threshold", 0), f"aggregation_views.{view_id}.k_threshold")
    if count < threshold:
        return "deny", "aggregation-threshold-not-met", None
    authority = op.get("authority", view.get("authority"))
    if not handle_has_any_right(handles, authority, {"aggregate", "read_aggregate", "inspect"}):
        return "deny", "aggregation-authority-missing", None
    return "allow", "aggregation-view-rendered", authority if isinstance(authority, str) else None


def eval_admit_evaluation_set(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    sets = index(records, "evaluation_sets")
    handles = index(records, "handles")
    if op.get("via") in {"eval_label", "benchmark_name", "leaderboard"}:
        return "deny", "eval-set-label-not-authority", None
    set_id = op.get("eval_set")
    ev = sets.get(set_id)
    if not isinstance(set_id, str) or ev is None:
        return "deny", "eval-set-missing", None
    if ev.get("status") != "active":
        return "deny", "eval-set-not-active", None
    if ev.get("holdout_sealed") is not True:
        return "deny", "eval-set-holdout-not-sealed", None
    if ev.get("contamination_status") == "contaminated":
        return "deny", "eval-set-contaminated", None
    if ev.get("license_ok") is not True or ev.get("purpose_ok") is not True:
        return "deny", "eval-set-use-not-cleared", None
    authority = op.get("authority", ev.get("authority"))
    if not handle_has_any_right(handles, authority, {"evaluate", "read", "use"}):
        return "deny", "eval-set-authority-missing", None
    return "allow", "evaluation-set-admitted", authority if isinstance(authority, str) else None


def eval_record_benchmark_run(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    runs = index(records, "benchmark_runs")
    handles = index(records, "handles")
    if op.get("via") in {"score", "leaderboard", "badge"}:
        return "deny", "benchmark-score-not-deploy-authority", None
    run_id = op.get("run")
    run = runs.get(run_id)
    if not isinstance(run_id, str) or run is None:
        return "deny", "benchmark-run-missing", None
    if run.get("status") != "complete":
        return "deny", "benchmark-run-not-complete", None
    if run.get("run_epoch") != run.get("current_epoch"):
        return "deny", "benchmark-run-stale", None
    if run.get("reproducible") is not True:
        return "deny", "benchmark-run-not-reproducible", None
    if run.get("eval_set_status") != "admitted" or run.get("rubric_status") != "active":
        return "deny", "benchmark-input-not-admitted", None
    authority = op.get("authority", run.get("authority"))
    if not handle_has_any_right(handles, authority, {"evaluate", "record", "audit"}):
        return "deny", "benchmark-authority-missing", None
    return "allow", "benchmark-run-recorded", authority if isinstance(authority, str) else None


def eval_apply_scoring_rubric(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    rubrics = index(records, "scoring_rubrics")
    handles = index(records, "handles")
    if op.get("via") in {"rubric_text", "metric_name", "policy_label"}:
        return "deny", "rubric-not-policy-authority", None
    rubric_id = op.get("rubric")
    rubric = rubrics.get(rubric_id)
    if not isinstance(rubric_id, str) or rubric is None:
        return "deny", "scoring-rubric-missing", None
    if rubric.get("status") != "active":
        return "deny", "scoring-rubric-not-active", None
    if rubric.get("calibrated") is not True:
        return "deny", "scoring-rubric-uncalibrated", None
    if rubric.get("metric_gaming_detected") is True:
        return "deny", "scoring-metric-gaming-detected", None
    if rubric.get("rubric_epoch") != rubric.get("current_epoch"):
        return "deny", "scoring-rubric-stale", None
    authority = op.get("authority", rubric.get("authority"))
    if not handle_has_any_right(handles, authority, {"score", "evaluate", "audit"}):
        return "deny", "scoring-authority-missing", None
    return "allow", "scoring-rubric-applied", authority if isinstance(authority, str) else None


def eval_render_model_selection_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "model_selection_cards")
    handles = index(records, "handles")
    card_id = op.get("card")
    card = cards.get(card_id)
    if not isinstance(card_id, str) or card is None:
        return "deny", "model-selection-card-missing", None
    if card.get("status") != "renderable":
        return "deny", "model-selection-card-not-renderable", None
    if card.get("claims_deploy_authority") is True:
        backing = card.get("backing_handle")
        if not isinstance(backing, str) or not has_live_right(handles, backing, "deploy"):
            return "deny", "model-card-claims-deploy-authority", None
    if card.get("claims_production_ready") is True and card.get("approval_cut") is not True:
        return "deny", "model-card-production-claim-unbacked", None
    if card.get("hides_tradeoffs") is True or card.get("single_score_only") is True:
        return "deny", "model-card-hides-tradeoffs", None
    return "allow", "model-selection-card-honest", None

def eval_admit_alert_signal(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    alerts = index(records, "alert_signals")
    handles = index(records, "handles")
    alert = alerts.get(op.get("alert"))
    require(alert is not None, f"unknown alert signal {op.get('alert')}")
    subject = op.get("subject")
    if isinstance(subject, str) and alert.get("subject") != subject:
        return "deny", "alert-subject-mismatch", None
    if alert.get("claims_authority") is True or alert.get("claims_access") is True:
        return "deny", "alert-signal-claims-authority", None
    if alert.get("status") != "active":
        return "deny", "alert-signal-not-active", None
    hid = alert.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"observe", "security", "incident_intake"}):
        return "deny", "alert-signal-missing-observe-authority", None
    return "allow", "alert-signal-admitted", hid if isinstance(hid, str) else None


def eval_open_incident_case(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    incidents = index(records, "incident_cases")
    alerts = index(records, "alert_signals")
    handles = index(records, "handles")
    case = incidents.get(op.get("case"))
    require(case is not None, f"unknown incident case {op.get('case')}")
    subject = op.get("subject")
    if isinstance(subject, str) and case.get("subject") != subject:
        return "deny", "incident-subject-mismatch", None
    if case.get("claims_remediation_authority") is True:
        return "deny", "incident-case-claims-remediation-authority", None
    if case.get("status") not in {"new", "open", "investigating"}:
        return "deny", "incident-case-not-open", None
    alert = alerts.get(case.get("alert"))
    if alert is None or alert.get("status") != "active":
        return "deny", "incident-case-lacks-active-alert", None
    hid = case.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"incident", "case", "triage"}):
        return "deny", "incident-case-missing-authority", None
    return "allow", "incident-case-opened", hid if isinstance(hid, str) else None


def eval_apply_triage_verdict(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    verdicts = index(records, "triage_verdicts")
    handles = index(records, "handles")
    verdict = verdicts.get(op.get("verdict"))
    require(verdict is not None, f"unknown triage verdict {op.get('verdict')}")
    if verdict.get("claims_execution_authority") is True:
        return "deny", "triage-verdict-claims-execution", None
    if verdict.get("status") != "current":
        return "deny", "triage-verdict-not-current", None
    confidence = as_number(verdict.get("confidence", 0), f"triage_verdicts.{op.get('verdict')}.confidence")
    min_confidence = as_number(op.get("min_confidence", 0.7), "operation.min_confidence")
    if confidence < min_confidence:
        return "deny", "triage-confidence-too-low", None
    hid = verdict.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"triage", "incident"}):
        return "deny", "triage-verdict-missing-authority", None
    return "allow", "triage-verdict-applied", hid if isinstance(hid, str) else None


def eval_capture_forensic_snapshot(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    snapshots = index(records, "forensic_snapshots")
    handles = index(records, "handles")
    redactions = index(records, "redaction_views")
    snapshot = snapshots.get(op.get("snapshot"))
    require(snapshot is not None, f"unknown forensic snapshot {op.get('snapshot')}")
    if snapshot.get("claims_live_access") is True:
        return "deny", "forensic-snapshot-claims-live-access", None
    if snapshot.get("status") != "sealed":
        return "deny", "forensic-snapshot-not-sealed", None
    if snapshot.get("raw_fields_exposed") is True:
        return "deny", "forensic-snapshot-redaction-leak", None
    fields = string_set(op.get("fields", snapshot.get("fields", [])), "operation.fields")
    view_id = snapshot.get("redaction_view")
    if isinstance(view_id, str):
        ok, reason = redaction_view_check(redactions, view_id, fields, "forensic-snapshot")
        if not ok:
            if "field" in reason or "redaction" in reason:
                return "deny", "forensic-snapshot-redaction-leak", None
            return "deny", reason, None
    hid = snapshot.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"forensic_capture", "snapshot"}):
        return "deny", "forensic-snapshot-missing-authority", None
    return "allow", "forensic-snapshot-captured", hid if isinstance(hid, str) else None


def eval_verify_evidence_chain(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    chains = index(records, "evidence_chains")
    handles = index(records, "handles")
    chain = chains.get(op.get("chain"))
    require(chain is not None, f"unknown evidence chain {op.get('chain')}")
    if chain.get("claims_causal_truth") is True or chain.get("claims_subject_truth") is True:
        return "deny", "evidence-chain-claims-truth", None
    if chain.get("status") != "verified" or chain.get("complete") is not True or chain.get("tamper_evident") is not True:
        return "deny", "evidence-chain-incomplete", None
    digest = op.get("digest")
    if isinstance(digest, str) and chain.get("digest") != digest:
        return "deny", "evidence-chain-digest-mismatch", None
    hid = chain.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"evidence_verify", "forensic_read", "incident"}):
        return "deny", "evidence-chain-missing-authority", None
    return "allow", "evidence-chain-verified", hid if isinstance(hid, str) else None


def eval_approve_containment_plan(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    plans = index(records, "containment_plans")
    handles = index(records, "handles")
    plan = plans.get(op.get("plan"))
    require(plan is not None, f"unknown containment plan {op.get('plan')}")
    if plan.get("status") != "approved" or plan.get("approval_cut") is not True:
        return "deny", "containment-plan-unapproved", None
    if plan.get("claims_broad_authority") is True:
        return "deny", "containment-plan-scope-widening", None
    allowed = record_fields(plan, "allowed_effects", f"containment_plans.{op.get('plan')}.allowed_effects")
    requested = string_set(op.get("effects", plan.get("requested_effects", [])), "operation.effects")
    if requested and not requested.issubset(allowed):
        return "deny", "containment-plan-scope-widening", None
    if plan.get("blast_radius_review") is not True:
        return "deny", "containment-plan-missing-blast-radius-review", None
    hid = plan.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"contain", "quarantine", "network_isolate"}):
        return "deny", "containment-plan-missing-authority", None
    return "allow", "containment-plan-approved", hid if isinstance(hid, str) else None


def eval_execute_remediation_plan(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    if op.get("via") == "receipt":
        return "deny", "remediation-receipt-not-authority", None
    plans = index(records, "remediation_plans")
    handles = index(records, "handles")
    plan = plans.get(op.get("plan"))
    require(plan is not None, f"unknown remediation plan {op.get('plan')}")
    if plan.get("status") != "approved" or plan.get("approval_cut") is not True:
        return "deny", "remediation-plan-unapproved", None
    if plan.get("preconditions_met") is not True:
        return "deny", "remediation-preconditions-missing", None
    if plan.get("claims_closure") is True:
        return "deny", "remediation-plan-claims-closure", None
    hid = plan.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"remediate", "write", "patch"}):
        return "deny", "remediation-plan-missing-authority", None
    return "allow", "remediation-plan-executable", hid if isinstance(hid, str) else None


def eval_execute_recovery_rollback(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    rollbacks = index(records, "recovery_rollbacks")
    handles = index(records, "handles")
    rollback = rollbacks.get(op.get("rollback"))
    require(rollback is not None, f"unknown recovery rollback {op.get('rollback')}")
    if rollback.get("status") != "approved" or rollback.get("approval_cut") is not True:
        return "deny", "rollback-unapproved", None
    if rollback.get("claims_erases_incident") is True:
        return "deny", "rollback-claims-erasure", None
    if rollback.get("base_epoch") != rollback.get("current_epoch"):
        return "deny", "rollback-stale-base", None
    hid = rollback.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"rollback", "restore", "write"}):
        return "deny", "rollback-missing-authority", None
    return "allow", "recovery-rollback-executable", hid if isinstance(hid, str) else None


def eval_render_postmortem_record(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    postmortems = index(records, "postmortem_records")
    handles = index(records, "handles")
    redactions = index(records, "redaction_views")
    record = postmortems.get(op.get("postmortem"))
    require(record is not None, f"unknown postmortem record {op.get('postmortem')}")
    if record.get("status") not in {"renderable", "publishable"}:
        return "deny", "postmortem-record-not-renderable", None
    if record.get("claims_live_authority") is True:
        return "deny", "postmortem-claims-live-authority", None
    if record.get("claims_no_recurrence") is True or record.get("claims_closure") is True:
        return "deny", "postmortem-claims-closure", None
    if record.get("raw_fields_exposed") is True:
        return "deny", "postmortem-redaction-leak", None
    fields = string_set(op.get("fields", record.get("fields", [])), "operation.fields")
    view_id = record.get("redaction_view")
    if isinstance(view_id, str):
        ok, reason = redaction_view_check(redactions, view_id, fields, "postmortem")
        if not ok:
            if "field" in reason or "redaction" in reason:
                return "deny", "postmortem-redaction-leak", None
            return "deny", reason, None
    if record.get("claims_public_release") is True:
        release_handle = record.get("release_handle")
        if not has_live_right(handles, release_handle, "publish"):
            return "deny", "postmortem-public-release-unbacked", None
    return "allow", "postmortem-record-rendered", None


def eval_admit_change_proposal(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    proposals = index(records, "change_proposals")
    handles = index(records, "handles")
    proposal = proposals.get(op.get("proposal"))
    require(proposal is not None, f"unknown change proposal {op.get('proposal')}")
    if proposal.get("claims_authority") is True:
        return "deny", "change-proposal-claims-authority", None
    if proposal.get("status") not in {"ready", "proposed"}:
        return "deny", "change-proposal-not-ready", None
    if proposal.get("basis_epoch") != proposal.get("current_epoch"):
        return "deny", "change-proposal-stale-basis", None
    if proposal.get("scope_widened") is True and proposal.get("widening_review") is not True:
        return "deny", "change-proposal-scope-widening", None
    hid = proposal.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"change", "govern", "review"}):
        return "deny", "change-proposal-missing-authority", None
    return "allow", "change-proposal-admitted", hid if isinstance(hid, str) else None


def eval_record_decision(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    decisions = index(records, "decision_records")
    proposals = index(records, "change_proposals")
    handles = index(records, "handles")
    decision = decisions.get(op.get("decision"))
    require(decision is not None, f"unknown decision record {op.get('decision')}")
    if decision.get("claims_execution_authority") is True:
        return "deny", "decision-record-claims-execution", None
    if decision.get("status") != "recorded":
        return "deny", "decision-record-not-recorded", None
    proposal_id = decision.get("proposal")
    proposal = proposals.get(proposal_id) if isinstance(proposal_id, str) else None
    if proposal is None or proposal.get("status") not in {"ready", "proposed"}:
        return "deny", "decision-record-lacks-proposal", None
    if decision.get("proposal_digest") != proposal.get("digest"):
        return "deny", "decision-record-proposal-digest-mismatch", None
    if decision.get("decision") not in {"approve", "reject", "defer"}:
        return "deny", "decision-record-invalid-verdict", None
    hid = decision.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"decide", "govern", "review"}):
        return "deny", "decision-record-missing-authority", None
    return "allow", "decision-recorded", hid if isinstance(hid, str) else None


def eval_verify_approval_quorum(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    quorums = index(records, "approval_quorums")
    handles = index(records, "handles")
    quorum = quorums.get(op.get("quorum"))
    require(quorum is not None, f"unknown approval quorum {op.get('quorum')}")
    if quorum.get("claims_authority") is True:
        return "deny", "quorum-claims-authority", None
    if quorum.get("status") != "current":
        return "deny", "quorum-not-current", None
    required = int(as_number(quorum.get("required", 0), "approval_quorums.required"))
    approvals = as_list(quorum.get("approvals", []), "approval_quorums.approvals")
    if len(approvals) < required:
        return "deny", "quorum-insufficient", None
    if quorum.get("steward_required") is True and quorum.get("steward_present") is not True:
        return "deny", "quorum-missing-steward", None
    hid = quorum.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"approve", "govern", "review"}):
        return "deny", "quorum-missing-authority", None
    return "allow", "approval-quorum-verified", hid if isinstance(hid, str) else None


def eval_start_rollout_plan(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    rollouts = index(records, "rollout_plans")
    handles = index(records, "handles")
    plan = rollouts.get(op.get("rollout"))
    require(plan is not None, f"unknown rollout plan {op.get('rollout')}")
    if plan.get("claims_complete") is True:
        return "deny", "rollout-claims-completion", None
    if plan.get("status") != "approved" or plan.get("approval_cut") is not True:
        return "deny", "rollout-not-approved", None
    if plan.get("guardrails_ok") is not True or plan.get("blast_radius_reviewed") is not True:
        return "deny", "rollout-guardrails-failed", None
    target_ring = op.get("target_ring", plan.get("target_ring"))
    allowed_rings = string_set(plan.get("allowed_rings", []), "rollout_plans.allowed_rings")
    if isinstance(target_ring, str) and allowed_rings and target_ring not in allowed_rings:
        return "deny", "rollout-ring-not-admitted", None
    hid = plan.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"rollout", "deploy", "govern"}):
        return "deny", "rollout-missing-authority", None
    return "allow", "rollout-started", hid if isinstance(hid, str) else None


def eval_evaluate_feature_flag(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    flags = index(records, "feature_flags")
    handles = index(records, "handles")
    flag = flags.get(op.get("flag"))
    require(flag is not None, f"unknown feature flag {op.get('flag')}")
    if flag.get("claims_authority") is True:
        return "deny", "feature-flag-claims-authority", None
    if flag.get("status") != "active":
        return "deny", "feature-flag-not-active", None
    scope = op.get("scope", flag.get("scope"))
    allowed_scopes = string_set(flag.get("allowed_scopes", []), "feature_flags.allowed_scopes")
    if isinstance(scope, str) and allowed_scopes and scope not in allowed_scopes:
        return "deny", "feature-flag-scope-denied", None
    if flag.get("policy_epoch") != flag.get("current_epoch"):
        return "deny", "feature-flag-stale-policy", None
    hid = flag.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"feature", "configure", "rollout"}):
        return "deny", "feature-flag-missing-authority", None
    return "allow", "feature-flag-evaluated", hid if isinstance(hid, str) else None


def eval_enforce_deprecation_notice(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    notices = index(records, "deprecation_notices")
    handles = index(records, "handles")
    notice = notices.get(op.get("notice"))
    require(notice is not None, f"unknown deprecation notice {op.get('notice')}")
    if notice.get("claims_removal") is True:
        return "deny", "deprecation-notice-claims-removal", None
    if notice.get("status") != "active":
        return "deny", "deprecation-notice-not-active", None
    if not notice.get("migration_path"):
        return "deny", "deprecation-notice-missing-migration", None
    if not time_reached(notice.get("now"), notice.get("effective_after"), "deprecation notice effective_after"):
        return "deny", "deprecation-window-not-reached", None
    hid = notice.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"deprecate", "govern", "notify"}):
        return "deny", "deprecation-missing-authority", None
    return "allow", "deprecation-notice-enforced", hid if isinstance(hid, str) else None


def eval_check_compatibility_contract(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    contracts = index(records, "compatibility_contracts")
    handles = index(records, "handles")
    contract = contracts.get(op.get("contract"))
    require(contract is not None, f"unknown compatibility contract {op.get('contract')}")
    if contract.get("claims_compatibility") is True:
        return "deny", "compat-contract-claims-compatibility", None
    if contract.get("status") != "active":
        return "deny", "compat-contract-not-active", None
    if op.get("from_version") != contract.get("from_version") or op.get("to_version") != contract.get("to_version"):
        return "deny", "compat-contract-version-mismatch", None
    if contract.get("breaking_change") is True and contract.get("waiver") is not True:
        return "deny", "compat-contract-breaking-change", None
    hid = contract.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"compat", "govern", "review"}):
        return "deny", "compat-contract-missing-authority", None
    return "allow", "compatibility-contract-checked", hid if isinstance(hid, str) else None


def eval_execute_migration_run(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    runs = index(records, "migration_runs")
    handles = index(records, "handles")
    run = runs.get(op.get("migration"))
    require(run is not None, f"unknown migration run {op.get('migration')}")
    if run.get("claims_success") is True:
        return "deny", "migration-run-claims-success", None
    if run.get("status") != "approved" or run.get("approval_cut") is not True:
        return "deny", "migration-run-not-approved", None
    if run.get("current_schema") != run.get("source_schema"):
        return "deny", "migration-run-stale-source-schema", None
    if run.get("precheck_ok") is not True or not run.get("rollback_plan"):
        return "deny", "migration-run-precheck-missing", None
    hid = run.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"migrate", "write", "govern"}):
        return "deny", "migration-run-missing-authority", None
    return "allow", "migration-run-executable", hid if isinstance(hid, str) else None


def eval_render_governance_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "governance_cards")
    quorums = index(records, "approval_quorums")
    card = cards.get(op.get("card"))
    require(card is not None, f"unknown governance card {op.get('card')}")
    if card.get("status") != "sealed":
        return "deny", "governance-card-not-sealed", None
    if card.get("claims_live_authority") is True:
        return "deny", "governance-card-claims-live-authority", None
    if card.get("exposes_private_votes") is True:
        return "deny", "governance-card-privacy-leak", None
    quorum_id = card.get("quorum")
    quorum = quorums.get(quorum_id) if isinstance(quorum_id, str) else None
    if card.get("claims_unanimity") is True:
        approvals = as_list(quorum.get("approvals", []) if quorum else [], "governance_cards.quorum.approvals")
        eligible = as_list(quorum.get("eligible", []) if quorum else [], "governance_cards.quorum.eligible")
        if not eligible or set(approvals) != set(eligible):
            return "deny", "governance-card-claims-unanimity", None
    return "allow", "governance-card-rendered", None


def eval_admit_event_envelope(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    events = index(records, "event_envelopes")
    handles = index(records, "handles")
    event = events.get(op.get("event"))
    require(event is not None, f"unknown event envelope {op.get('event')}")
    if event.get("claims_authority") is True:
        return "deny", "event-envelope-claims-authority", None
    if event.get("status") != "received":
        return "deny", "event-envelope-not-received", None
    if event.get("source_trusted") is not True:
        return "deny", "event-envelope-untrusted-source", None
    if event.get("schema_valid") is not True:
        return "deny", "event-envelope-schema-invalid", None
    expected_subject = op.get("subject", event.get("subject"))
    if expected_subject != event.get("subject"):
        return "deny", "event-envelope-subject-mismatch", None
    hid = event.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"event", "observe", "workflow"}):
        return "deny", "event-envelope-missing-authority", None
    return "allow", "event-envelope-admitted", hid if isinstance(hid, str) else None


def eval_evaluate_trigger_rule(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    rules = index(records, "trigger_rules")
    events = index(records, "event_envelopes")
    handles = index(records, "handles")
    rule = rules.get(op.get("rule"))
    require(rule is not None, f"unknown trigger rule {op.get('rule')}")
    if rule.get("claims_authority") is True:
        return "deny", "trigger-rule-claims-authority", None
    if rule.get("status") != "active":
        return "deny", "trigger-rule-not-active", None
    if rule.get("rule_epoch") != rule.get("current_epoch"):
        return "deny", "trigger-rule-stale", None
    event_id = op.get("event", rule.get("event"))
    event = events.get(event_id) if isinstance(event_id, str) else None
    if event is None or event.get("status") != "received":
        return "deny", "trigger-rule-missing-event", None
    if event.get("type") != rule.get("event_type"):
        return "deny", "trigger-rule-event-type-mismatch", None
    hid = rule.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"trigger", "workflow", "event"}):
        return "deny", "trigger-rule-missing-authority", None
    return "allow", "trigger-rule-matched", hid if isinstance(hid, str) else None


def eval_fire_schedule_window(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    schedules = index(records, "schedule_windows")
    handles = index(records, "handles")
    window = schedules.get(op.get("schedule"))
    require(window is not None, f"unknown schedule window {op.get('schedule')}")
    if window.get("claims_authority") is True:
        return "deny", "schedule-window-claims-authority", None
    if window.get("status") != "active":
        return "deny", "schedule-window-not-active", None
    now = window.get("now")
    not_before = window.get("not_before")
    not_after = window.get("not_after")
    if not time_reached(now, not_before, "schedule window not_before"):
        return "deny", "schedule-window-too-early", None
    if isinstance(now, str) and isinstance(not_after, str) and now > not_after:
        return "deny", "schedule-window-expired", None
    if window.get("approval_cut") is not True:
        return "deny", "schedule-window-missing-approval-cut", None
    hid = window.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"schedule", "workflow", "trigger"}):
        return "deny", "schedule-window-missing-authority", None
    return "allow", "schedule-window-fired", hid if isinstance(hid, str) else None


def eval_start_workflow_run(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    runs = index(records, "workflow_runs")
    handles = index(records, "handles")
    run = runs.get(op.get("workflow"))
    require(run is not None, f"unknown workflow run {op.get('workflow')}")
    if run.get("claims_authority") is True:
        return "deny", "workflow-run-claims-authority", None
    if run.get("status") != "ready":
        return "deny", "workflow-run-not-ready", None
    if run.get("approval_cut") is not True:
        return "deny", "workflow-run-missing-approval-cut", None
    if run.get("lease_valid") is not True:
        return "deny", "workflow-run-lease-invalid", None
    if run.get("basis_epoch") != run.get("current_epoch"):
        return "deny", "workflow-run-stale-basis", None
    hid = run.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"workflow", "start", "execute"}):
        return "deny", "workflow-run-missing-authority", None
    return "allow", "workflow-run-started", hid if isinstance(hid, str) else None


def eval_execute_workflow_step(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    steps = index(records, "step_invocations")
    runs = index(records, "workflow_runs")
    handles = index(records, "handles")
    step = steps.get(op.get("step"))
    require(step is not None, f"unknown workflow step {op.get('step')}")
    if step.get("claims_completion") is True:
        return "deny", "workflow-step-claims-completion", None
    if step.get("status") != "ready":
        return "deny", "workflow-step-not-ready", None
    run_id = step.get("workflow")
    run = runs.get(run_id) if isinstance(run_id, str) else None
    if run is None or run.get("status") not in {"ready", "running"}:
        return "deny", "workflow-step-run-not-active", None
    if step.get("approval_cut") is not True:
        return "deny", "workflow-step-missing-approval-cut", None
    target_handle = step.get("target_handle")
    required_right = step.get("required_right", op.get("want", "write"))
    if not isinstance(required_right, str) or not has_live_right(handles, target_handle, required_right):
        return "deny", "workflow-step-missing-target-authority", None
    hid = step.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"step", "execute", "workflow"}):
        return "deny", "workflow-step-missing-authority", None
    return "allow", "workflow-step-executed", hid if isinstance(hid, str) else None


def eval_apply_idempotency_key(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    keys = index(records, "idempotency_keys")
    handles = index(records, "handles")
    key = keys.get(op.get("key"))
    require(key is not None, f"unknown idempotency key {op.get('key')}")
    if key.get("claims_effect") is True:
        return "deny", "idempotency-key-claims-effect", None
    if key.get("status") == "spent":
        return "deny", "idempotency-key-replay-effect", None
    if key.get("status") != "unused":
        return "deny", "idempotency-key-not-usable", None
    if op.get("fingerprint") != key.get("request_fingerprint"):
        return "deny", "idempotency-key-fingerprint-mismatch", None
    hid = key.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"dedupe", "workflow", "execute"}):
        return "deny", "idempotency-key-missing-authority", None
    return "allow", "idempotency-key-admitted", hid if isinstance(hid, str) else None


def eval_apply_retry_policy(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    policies = index(records, "retry_policies")
    handles = index(records, "handles")
    policy = policies.get(op.get("retry"))
    require(policy is not None, f"unknown retry policy {op.get('retry')}")
    if policy.get("claims_authority") is True:
        return "deny", "retry-policy-claims-authority", None
    if policy.get("status") != "active":
        return "deny", "retry-policy-not-active", None
    attempt = int(as_number(policy.get("attempt", 0), "retry_policies.attempt"))
    max_attempts = int(as_number(policy.get("max_attempts", 0), "retry_policies.max_attempts"))
    if attempt > max_attempts:
        return "deny", "retry-policy-attempts-exceeded", None
    if not time_reached(policy.get("now"), policy.get("backoff_until"), "retry policy backoff_until"):
        return "deny", "retry-policy-backoff-not-reached", None
    if policy.get("budget_ok") is not True:
        return "deny", "retry-policy-budget-missing", None
    hid = policy.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"retry", "workflow", "execute"}):
        return "deny", "retry-policy-missing-authority", None
    return "allow", "retry-policy-admitted", hid if isinstance(hid, str) else None


def eval_execute_compensation_plan(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    plans = index(records, "compensation_plans")
    handles = index(records, "handles")
    plan = plans.get(op.get("compensation"))
    require(plan is not None, f"unknown compensation plan {op.get('compensation')}")
    if plan.get("receipt_replay") is True:
        return "deny", "compensation-receipt-replay", None
    if plan.get("claims_erasure") is True:
        return "deny", "compensation-claims-erasure", None
    if plan.get("status") != "approved" or plan.get("approval_cut") is not True:
        return "deny", "compensation-not-approved", None
    if plan.get("reversible") is not True:
        return "deny", "compensation-not-reversible", None
    hid = plan.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"compensate", "workflow", "write"}):
        return "deny", "compensation-missing-authority", None
    return "allow", "compensation-executed", hid if isinstance(hid, str) else None


def eval_complete_human_task(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    tasks = index(records, "human_tasks")
    handles = index(records, "handles")
    task = tasks.get(op.get("task"))
    require(task is not None, f"unknown human task {op.get('task')}")
    if task.get("claims_authority") is True:
        return "deny", "human-task-claims-authority", None
    if task.get("status") != "ready":
        return "deny", "human-task-not-ready", None
    if task.get("trusted_path") is not True:
        return "deny", "human-task-untrusted-path", None
    if task.get("approval_cut") is not True:
        return "deny", "human-task-missing-approval-cut", None
    if task.get("assignee") != op.get("actor", task.get("assignee")):
        return "deny", "human-task-assignee-mismatch", None
    hid = task.get("authority") or op.get("authority")
    if not handle_has_any_right(handles, hid, {"approve", "human", "workflow"}):
        return "deny", "human-task-missing-authority", None
    return "allow", "human-task-completed", hid if isinstance(hid, str) else None


def eval_render_workflow_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "workflow_cards")
    runs = index(records, "workflow_runs")
    card = cards.get(op.get("card"))
    require(card is not None, f"unknown workflow card {op.get('card')}")
    if card.get("status") != "sealed":
        return "deny", "workflow-card-not-sealed", None
    if card.get("claims_live_authority") is True:
        return "deny", "workflow-card-claims-live-authority", None
    if card.get("leaks_hidden_steps") is True:
        return "deny", "workflow-card-hidden-step-leak", None
    if card.get("claims_completion") is True:
        run_id = card.get("workflow")
        run = runs.get(run_id) if isinstance(run_id, str) else None
        if run is None or run.get("status") != "complete":
            return "deny", "workflow-card-claims-completion", None
    return "allow", "workflow-card-rendered", None


def eval_verify_user_profile(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    profiles = index(records, "user_profiles")
    handles = index(records, "handles")
    profile = profiles.get(op.get("profile"))
    require(profile is not None, f"unknown user profile {op.get('profile')}")
    if profile.get("claims_authority") is True:
        return "deny", "user-profile-claims-authority", None
    if profile.get("status") != "active":
        return "deny", "user-profile-inactive", None
    if profile.get("subject") != op.get("subject"):
        return "deny", "user-profile-subject-mismatch", None
    if profile.get("identity") != op.get("identity") or profile.get("session") != op.get("session"):
        return "deny", "user-profile-binding-mismatch", None
    if profile.get("policy_epoch") != profile.get("current_epoch"):
        return "deny", "user-profile-stale-policy", None
    hid = profile.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "profile"):
        return "allow", "user-profile-bound", hid
    return "deny", "user-profile-missing-live-authority", None


def eval_apply_preference_set(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    prefs = index(records, "preference_sets")
    handles = index(records, "handles")
    pref = prefs.get(op.get("preference"))
    require(pref is not None, f"unknown preference set {op.get('preference')}")
    if pref.get("claims_policy") is True:
        return "deny", "preference-set-claims-policy", None
    if pref.get("claims_consent") is True:
        return "deny", "preference-set-claims-consent", None
    if pref.get("status") != "active":
        return "deny", "preference-set-inactive", None
    if pref.get("policy_epoch") != pref.get("current_epoch"):
        return "deny", "preference-set-stale-policy", None
    scope = op.get("scope", pref.get("scope"))
    allowed = string_set(pref.get("allowed_scopes", []), "preference.allowed_scopes")
    if scope not in allowed:
        return "deny", "preference-scope-not-allowed", None
    hid = pref.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "preference"):
        return "allow", "preference-set-applied", hid
    return "deny", "preference-missing-live-authority", None


def eval_admit_personalization_model(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    models = index(records, "personalization_models")
    handles = index(records, "handles")
    model = models.get(op.get("model"))
    require(model is not None, f"unknown personalization model {op.get('model')}")
    if model.get("claims_authority") is True:
        return "deny", "personalization-model-claims-authority", None
    if model.get("status") != "active":
        return "deny", "personalization-model-inactive", None
    if model.get("model_epoch") != model.get("current_epoch"):
        return "deny", "personalization-model-stale-epoch", None
    if model.get("training_purpose_ok") is not True:
        return "deny", "personalization-model-purpose-missing", None
    if model.get("source_minimized") is not True:
        return "deny", "personalization-model-source-not-minimized", None
    hid = model.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "personalize"):
        return "allow", "personalization-model-admitted", hid
    return "deny", "personalization-model-missing-live-authority", None


def eval_render_recommendation_set(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    recs = index(records, "recommendation_sets")
    models = index(records, "personalization_models")
    handles = index(records, "handles")
    rec = recs.get(op.get("recommendation"))
    require(rec is not None, f"unknown recommendation set {op.get('recommendation')}")
    if rec.get("claims_authority") is True:
        return "deny", "recommendation-set-claims-authority", None
    if rec.get("leaks_private_features") is True:
        return "deny", "recommendation-private-feature-leak", None
    if rec.get("status") != "ready":
        return "deny", "recommendation-set-not-ready", None
    model_id = rec.get("source_model")
    model = models.get(model_id) if isinstance(model_id, str) else None
    if model is None or model.get("status") != "active":
        return "deny", "recommendation-source-model-not-active", None
    if rec.get("scoped") is not True:
        return "deny", "recommendation-set-unscoped", None
    hid = rec.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "recommend"):
        return "allow", "recommendation-set-rendered", hid
    return "deny", "recommendation-missing-live-authority", None


def eval_execute_shortcut_binding(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    shortcuts = index(records, "shortcut_bindings")
    handles = index(records, "handles")
    shortcut = shortcuts.get(op.get("shortcut"))
    require(shortcut is not None, f"unknown shortcut binding {op.get('shortcut')}")
    if shortcut.get("claims_authority") is True:
        return "deny", "shortcut-binding-claims-authority", None
    if shortcut.get("status") != "active":
        return "deny", "shortcut-binding-inactive", None
    if shortcut.get("approval_cut") is not True:
        return "deny", "shortcut-binding-missing-approval-cut", None
    target = shortcut.get("target_handle")
    required = shortcut.get("required_right", op.get("required_right", "write"))
    if not (isinstance(target, str) and isinstance(required, str) and has_live_right(handles, target, required)):
        return "deny", "shortcut-target-lacks-required-right", None
    hid = shortcut.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "shortcut"):
        return "allow", "shortcut-binding-executed", target
    return "deny", "shortcut-missing-live-authority", None


def eval_accept_autofill_proposal(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    proposals = index(records, "autofill_proposals")
    handles = index(records, "handles")
    proposal = proposals.get(op.get("proposal"))
    require(proposal is not None, f"unknown autofill proposal {op.get('proposal')}")
    if proposal.get("claims_write_authority") is True:
        return "deny", "autofill-claims-write-authority", None
    if proposal.get("status") != "offered":
        return "deny", "autofill-proposal-not-offered", None
    if proposal.get("approval_cut") is not True:
        return "deny", "autofill-missing-approval-cut", None
    if proposal.get("secret_fields") and proposal.get("redacted") is not True:
        return "deny", "autofill-secret-leak", None
    target = proposal.get("target_handle")
    required = proposal.get("required_right", op.get("required_right", "write"))
    if not (isinstance(target, str) and isinstance(required, str) and has_live_right(handles, target, required)):
        return "deny", "autofill-target-lacks-required-right", None
    hid = proposal.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "autofill"):
        return "allow", "autofill-proposal-accepted", target
    return "deny", "autofill-missing-live-authority", None


def eval_apply_experiment_assignment(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    assignments = index(records, "experiment_assignments")
    handles = index(records, "handles")
    assignment = assignments.get(op.get("assignment"))
    require(assignment is not None, f"unknown experiment assignment {op.get('assignment')}")
    if assignment.get("claims_policy_override") is True:
        return "deny", "experiment-claims-policy-override", None
    if assignment.get("status") != "active":
        return "deny", "experiment-assignment-inactive", None
    if assignment.get("policy_epoch") != assignment.get("current_epoch"):
        return "deny", "experiment-assignment-stale-epoch", None
    scope = op.get("scope", assignment.get("scope"))
    allowed = string_set(assignment.get("allowed_scopes", []), "experiment.allowed_scopes")
    if scope not in allowed:
        return "deny", "experiment-scope-not-allowed", None
    hid = assignment.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "experiment"):
        return "allow", "experiment-assignment-applied", hid
    return "deny", "experiment-missing-live-authority", None


def eval_record_feedback_signal(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    signals = index(records, "feedback_signals")
    handles = index(records, "handles")
    signal = signals.get(op.get("signal"))
    require(signal is not None, f"unknown feedback signal {op.get('signal')}")
    if signal.get("claims_training_consent") is True:
        return "deny", "feedback-claims-training-consent", None
    if signal.get("status") != "ready":
        return "deny", "feedback-signal-not-ready", None
    purpose = op.get("purpose", signal.get("purpose"))
    allowed = string_set(signal.get("allowed_purposes", []), "feedback.allowed_purposes")
    if purpose not in allowed:
        return "deny", "feedback-purpose-not-allowed", None
    if purpose == "training" and signal.get("consent_for_training") is not True:
        return "deny", "feedback-training-consent-missing", None
    hid = signal.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "feedback"):
        return "allow", "feedback-signal-recorded", hid
    return "deny", "feedback-missing-live-authority", None


def eval_render_personalization_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "personalization_cards")
    card = cards.get(op.get("card"))
    require(card is not None, f"unknown personalization card {op.get('card')}")
    if card.get("status") != "renderable":
        return "deny", "personalization-card-not-renderable", None
    if card.get("claims_live_authority") is True:
        return "deny", "personalization-card-claims-live-authority", None
    if card.get("exposes_sensitive_features") is True:
        return "deny", "personalization-card-sensitive-feature-leak", None
    if card.get("claims_deterministic") is True:
        return "deny", "personalization-card-claims-determinism", None
    return "allow", "personalization-card-rendered", None


def eval_bind_namespace_context(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    bindings = index(records, "namespace_bindings")
    handles = index(records, "handles")
    binding = bindings.get(op.get("binding"))
    require(binding is not None, f"unknown namespace binding {op.get('binding')}")
    if binding.get("claims_authority") is True:
        return "deny", "namespace-binding-claims-authority", None
    if binding.get("status") != "active":
        return "deny", "namespace-binding-inactive", None
    if binding.get("policy_epoch") != binding.get("current_epoch"):
        return "deny", "namespace-binding-stale-policy", None
    prefix = op.get("prefix", binding.get("prefix"))
    if prefix in string_set(binding.get("blocked_prefixes", []), "namespace_binding.blocked_prefixes"):
        return "deny", "namespace-prefix-collision", None
    allowed = string_set(binding.get("allowed_prefixes", []), "namespace_binding.allowed_prefixes")
    if allowed and prefix not in allowed:
        return "deny", "namespace-prefix-not-allowed", None
    expected_digest = op.get("context_digest", binding.get("context_digest"))
    if binding.get("context_digest") != expected_digest:
        return "deny", "namespace-context-digest-mismatch", None
    hid = binding.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "namespace"):
        return "allow", "namespace-context-bound", hid
    return "deny", "namespace-missing-live-authority", None


def eval_resolve_external_reference(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    refs = index(records, "external_references")
    handles = index(records, "handles")
    ref = refs.get(op.get("reference"))
    require(ref is not None, f"unknown external reference {op.get('reference')}")
    if ref.get("claims_authority") is True:
        return "deny", "external-reference-claims-authority", None
    if ref.get("status") != "active":
        return "deny", "external-reference-inactive", None
    scheme = op.get("scheme", ref.get("scheme"))
    allowed = string_set(ref.get("allowed_schemes", []), "external_reference.allowed_schemes")
    if allowed and scheme not in allowed:
        return "deny", "external-reference-scheme-not-allowed", None
    if ref.get("resolver_epoch") != ref.get("current_epoch"):
        return "deny", "external-reference-stale-resolver", None
    expected_digest = op.get("target_digest", ref.get("target_digest"))
    if ref.get("target_digest") != expected_digest:
        return "deny", "external-reference-target-digest-mismatch", None
    hid = ref.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "reference"):
        return "allow", "external-reference-resolved", hid
    return "deny", "external-reference-missing-live-authority", None


def eval_admit_vocabulary_term(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    terms = index(records, "vocabulary_terms")
    namespaces = index(records, "namespace_bindings")
    handles = index(records, "handles")
    term = terms.get(op.get("term"))
    require(term is not None, f"unknown vocabulary term {op.get('term')}")
    if term.get("claims_policy") is True:
        return "deny", "vocabulary-term-claims-policy", None
    if term.get("status") != "active":
        return "deny", "vocabulary-term-inactive", None
    if term.get("deprecated") is True:
        return "deny", "vocabulary-term-deprecated", None
    namespace = namespaces.get(term.get("namespace"))
    if namespace is None or namespace.get("status") != "active":
        return "deny", "vocabulary-namespace-not-bound", None
    hid = term.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "vocabulary"):
        return "allow", "vocabulary-term-admitted", hid
    return "deny", "vocabulary-term-missing-live-authority", None


def eval_apply_crosswalk_mapping(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    mappings = index(records, "crosswalk_mappings")
    terms = index(records, "vocabulary_terms")
    handles = index(records, "handles")
    mapping = mappings.get(op.get("mapping"))
    require(mapping is not None, f"unknown crosswalk mapping {op.get('mapping')}")
    if mapping.get("claims_equivalence") is True:
        return "deny", "crosswalk-claims-exact-equivalence", None
    if mapping.get("status") != "active":
        return "deny", "crosswalk-mapping-inactive", None
    source = terms.get(mapping.get("source_term"))
    target = terms.get(mapping.get("target_term"))
    if source is None or target is None or source.get("status") != "active" or target.get("status") != "active":
        return "deny", "crosswalk-term-not-admitted", None
    if mapping.get("reviewed") is not True:
        return "deny", "crosswalk-review-missing", None
    min_confidence = as_number(op.get("min_confidence", 0.0), "operation.min_confidence")
    confidence = as_number(mapping.get("confidence", 0.0), "crosswalk_mapping.confidence")
    if confidence < min_confidence:
        return "deny", "crosswalk-confidence-too-low", None
    if mapping.get("mapping_kind") == "exact" and mapping.get("exact_equivalence_review") is not True:
        return "deny", "crosswalk-exact-review-missing", None
    hid = mapping.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "crosswalk"):
        return "allow", "crosswalk-mapping-applied", hid
    return "deny", "crosswalk-missing-live-authority", None


def eval_validate_shape_constraint(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    shapes = index(records, "shape_constraints")
    handles = index(records, "handles")
    shape = shapes.get(op.get("shape"))
    require(shape is not None, f"unknown shape constraint {op.get('shape')}")
    if shape.get("claims_authority") is True:
        return "deny", "shape-constraint-claims-authority", None
    if shape.get("status") != "active":
        return "deny", "shape-constraint-inactive", None
    if shape.get("shape_epoch") != shape.get("current_epoch"):
        return "deny", "shape-constraint-stale", None
    if shape.get("validation_passed") is not True:
        return "deny", "shape-validation-failed", None
    target = op.get("target", shape.get("target_handle"))
    if not (isinstance(target, str) and has_live_right(handles, target, "read")):
        return "deny", "shape-target-missing-read-authority", None
    hid = shape.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "shape"):
        return "allow", "shape-constraint-validated", hid
    return "deny", "shape-constraint-missing-live-authority", None


def eval_verify_ontology_alignment(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    alignments = index(records, "ontology_alignments")
    handles = index(records, "handles")
    alignment = alignments.get(op.get("alignment"))
    require(alignment is not None, f"unknown ontology alignment {op.get('alignment')}")
    if alignment.get("claims_inferred_authority") is True:
        return "deny", "ontology-alignment-claims-authority", None
    if alignment.get("status") != "active":
        return "deny", "ontology-alignment-inactive", None
    if alignment.get("alignment_epoch") != alignment.get("current_epoch"):
        return "deny", "ontology-alignment-stale", None
    if alignment.get("relation") == "equivalent" and alignment.get("reviewed") is not True:
        return "deny", "ontology-equivalence-review-missing", None
    min_confidence = as_number(op.get("min_confidence", 0.0), "operation.min_confidence")
    confidence = as_number(alignment.get("confidence", 0.0), "ontology_alignment.confidence")
    if confidence < min_confidence:
        return "deny", "ontology-alignment-confidence-too-low", None
    hid = alignment.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "ontology"):
        return "allow", "ontology-alignment-verified", hid
    return "deny", "ontology-alignment-missing-live-authority", None


def eval_publish_catalog_entry(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    entries = index(records, "catalog_entries")
    handles = index(records, "handles")
    entry = entries.get(op.get("entry"))
    require(entry is not None, f"unknown catalog entry {op.get('entry')}")
    if entry.get("claims_disclosure_authority") is True:
        return "deny", "catalog-entry-claims-disclosure-authority", None
    if entry.get("status") != "ready":
        return "deny", "catalog-entry-not-ready", None
    if entry.get("catalog_epoch") != entry.get("current_epoch"):
        return "deny", "catalog-entry-stale-epoch", None
    if entry.get("public_release_approved") is not True:
        return "deny", "catalog-entry-release-review-missing", None
    if entry.get("redacted") is not True:
        return "deny", "catalog-entry-redaction-missing", None
    source = entry.get("source_handle")
    if not (isinstance(source, str) and has_live_right(handles, source, "disclose")):
        return "deny", "catalog-source-lacks-disclose-right", None
    hid = entry.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "catalog"):
        return "allow", "catalog-entry-published", hid
    return "deny", "catalog-entry-missing-live-authority", None


def eval_render_interop_card(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    cards = index(records, "interop_cards")
    card = cards.get(op.get("card"))
    require(card is not None, f"unknown interop card {op.get('card')}")
    if card.get("status") != "renderable":
        return "deny", "interop-card-not-renderable", None
    if card.get("claims_live_authority") is True:
        return "deny", "interop-card-claims-live-authority", None
    if card.get("overstates_equivalence") is True:
        return "deny", "interop-card-overstates-equivalence", None
    if card.get("leaks_hidden_identifier") is True:
        return "deny", "interop-card-hidden-identifier-leak", None
    return "allow", "interop-card-rendered", None


# Revision 176 host-adapter / filesystem-compatibility evaluators.
def eval_admit_adapter_mount(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    mounts = index(records, "adapter_mounts")
    handles = index(records, "handles")
    mount = mounts.get(op.get("mount"))
    require(mount is not None, f"unknown adapter mount {op.get('mount')}")
    if mount.get("claims_root_authority") is True:
        return "deny", "adapter-mount-claims-root-authority", None
    if mount.get("status") != "active":
        return "deny", "adapter-mount-inactive", None
    if mount.get("policy_epoch") != mount.get("current_epoch"):
        return "deny", "adapter-mount-stale-policy", None
    if mount.get("sandbox_ok") is not True:
        return "deny", "adapter-mount-sandbox-not-ok", None
    hid = mount.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "mount"):
        return "allow", "adapter-mount-admitted", hid
    return "deny", "adapter-mount-missing-live-authority", None


def eval_render_stat_projection(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    projections = index(records, "stat_projections")
    handles = index(records, "handles")
    projection = projections.get(op.get("projection"))
    require(projection is not None, f"unknown stat projection {op.get('projection')}")
    if projection.get("claims_read_authority") is True:
        return "deny", "stat-projection-claims-read-authority", None
    if projection.get("status") != "renderable":
        return "deny", "stat-projection-not-renderable", None
    fields = string_set(op.get("fields", projection.get("fields", [])), "stat_projection.fields")
    hidden = string_set(projection.get("hidden_fields", []), "stat_projection.hidden_fields")
    if fields & hidden:
        return "deny", "stat-projection-hidden-metadata-leak", None
    source = projection.get("source_handle")
    if not (isinstance(source, str) and has_live_right(handles, source, "read")):
        return "deny", "stat-projection-source-lacks-read", None
    hid = projection.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "stat"):
        return "allow", "stat-projection-rendered", source
    return "deny", "stat-projection-missing-live-authority", None


def eval_resolve_inode_alias(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    aliases = index(records, "inode_aliases")
    handles = index(records, "handles")
    alias = aliases.get(op.get("alias"))
    require(alias is not None, f"unknown inode alias {op.get('alias')}")
    if alias.get("claims_object_identity") is True:
        return "deny", "inode-alias-claims-object-identity", None
    if alias.get("status") != "active":
        return "deny", "inode-alias-inactive", None
    if alias.get("alias_epoch") != alias.get("current_epoch"):
        return "deny", "inode-alias-stale-epoch", None
    if alias.get("collision") is True:
        return "deny", "inode-alias-collision", None
    target = alias.get("target_handle")
    if not (isinstance(target, str) and has_any_live_right(handles, target)):
        return "deny", "inode-alias-target-not-live", None
    hid = alias.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "alias"):
        return "allow", "inode-alias-resolved", target
    return "deny", "inode-alias-missing-live-authority", None


def eval_read_xattr_parcel(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    parcels = index(records, "xattr_parcels")
    handles = index(records, "handles")
    parcel = parcels.get(op.get("parcel"))
    require(parcel is not None, f"unknown xattr parcel {op.get('parcel')}")
    if parcel.get("claims_policy_authority") is True:
        return "deny", "xattr-claims-policy-authority", None
    if parcel.get("status") != "active":
        return "deny", "xattr-parcel-inactive", None
    name = op.get("name", parcel.get("name"))
    require(isinstance(name, str), "xattr operation needs a string name")
    allowed = string_set(parcel.get("allowed_names", []), "xattr.allowed_names")
    if allowed and name not in allowed:
        return "deny", "xattr-name-not-allowed", None
    sensitive = string_set(parcel.get("sensitive_names", []), "xattr.sensitive_names")
    if name in sensitive and parcel.get("redacted") is not True:
        return "deny", "xattr-sensitive-name-unredacted", None
    source = parcel.get("source_handle")
    if not (isinstance(source, str) and has_any_live_right(handles, source)):
        return "deny", "xattr-source-not-live", None
    hid = parcel.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "xattr"):
        return "allow", "xattr-parcel-read", hid
    return "deny", "xattr-missing-live-authority", None


def eval_deliver_watcher_event(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    watchers = index(records, "watcher_subscriptions")
    handles = index(records, "handles")
    watcher = watchers.get(op.get("watcher"))
    require(watcher is not None, f"unknown watcher subscription {op.get('watcher')}")
    if watcher.get("claims_open_authority") is True:
        return "deny", "watcher-claims-open-authority", None
    if watcher.get("status") != "active":
        return "deny", "watcher-subscription-inactive", None
    if watcher.get("event_epoch") != watcher.get("current_epoch") or watcher.get("cursor_state") == "stale":
        return "deny", "watcher-subscription-stale", None
    event_type = op.get("event_type", watcher.get("event_type"))
    allowed = string_set(watcher.get("allowed_events", []), "watcher.allowed_events")
    if event_type not in allowed:
        return "deny", "watcher-event-not-allowed", None
    hid = watcher.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "watch"):
        return "allow", "watcher-event-delivered", hid
    return "deny", "watcher-missing-live-authority", None


def eval_acquire_lock_token(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    locks = index(records, "lock_tokens")
    handles = index(records, "handles")
    token = locks.get(op.get("token"))
    require(token is not None, f"unknown lock token {op.get('token')}")
    if token.get("claims_write_authority") is True:
        return "deny", "lock-token-claims-write-authority", None
    if token.get("status") != "available":
        return "deny", "lock-token-not-available", None
    if token.get("range_conflict") is True:
        return "deny", "lock-token-range-conflict", None
    target = token.get("target_handle")
    required = token.get("required_right", op.get("required_right", "write"))
    if not (isinstance(target, str) and isinstance(required, str) and has_live_right(handles, target, required)):
        return "deny", "lock-target-lacks-required-right", None
    hid = token.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "lock"):
        return "allow", "lock-token-acquired", hid
    return "deny", "lock-token-missing-live-authority", None


def eval_execute_rename_plan(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    plans = index(records, "rename_plans")
    handles = index(records, "handles")
    plan = plans.get(op.get("plan"))
    require(plan is not None, f"unknown rename plan {op.get('plan')}")
    if plan.get("claims_atomic_completion") is True:
        return "deny", "rename-plan-claims-completion", None
    if plan.get("status") != "ready":
        return "deny", "rename-plan-not-ready", None
    if plan.get("approval_cut") is not True:
        return "deny", "rename-plan-missing-approval-cut", None
    if plan.get("cross_mount") is True and plan.get("allow_cross_mount") is not True:
        return "deny", "rename-cross-mount-denied", None
    source = plan.get("source_handle")
    if not (isinstance(source, str) and has_live_right(handles, source, "write")):
        return "deny", "rename-source-lacks-write", None
    target_parent = plan.get("target_parent_handle")
    if not (isinstance(target_parent, str) and has_live_right(handles, target_parent, "write")):
        return "deny", "rename-target-parent-lacks-write", None
    hid = plan.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "rename"):
        return "allow", "rename-plan-executed", source
    return "deny", "rename-plan-missing-live-authority", None


def eval_promote_tempfile_lease(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    leases = index(records, "tempfile_leases")
    handles = index(records, "handles")
    lease = leases.get(op.get("lease"))
    require(lease is not None, f"unknown tempfile lease {op.get('lease')}")
    if lease.get("claims_committed") is True:
        return "deny", "tempfile-claims-committed", None
    if lease.get("status") != "staged":
        return "deny", "tempfile-not-staged", None
    if lease.get("flush_proof") is not True:
        return "deny", "tempfile-missing-flush-proof", None
    if lease.get("approval_cut") is not True:
        return "deny", "tempfile-missing-approval-cut", None
    target = lease.get("target_handle")
    if not (isinstance(target, str) and has_live_right(handles, target, "write")):
        return "deny", "tempfile-target-lacks-write", None
    hid = lease.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "tempfile"):
        return "allow", "tempfile-lease-promoted", target
    return "deny", "tempfile-missing-live-authority", None


def eval_hydrate_placeholder(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    tickets = index(records, "hydration_tickets")
    handles = index(records, "handles")
    ticket = tickets.get(op.get("ticket"))
    require(ticket is not None, f"unknown hydration ticket {op.get('ticket')}")
    if ticket.get("claims_read_authority") is True:
        return "deny", "hydration-ticket-claims-read-authority", None
    if ticket.get("status") != "ready":
        return "deny", "hydration-ticket-not-ready", None
    if ticket.get("placeholder_epoch") != ticket.get("current_epoch"):
        return "deny", "hydration-placeholder-stale", None
    if ticket.get("network_verified") is not True:
        return "deny", "hydration-network-unverified", None
    source = ticket.get("source_handle")
    if not (isinstance(source, str) and has_live_right(handles, source, "read")):
        return "deny", "hydration-source-lacks-read", None
    result = ticket.get("result_handle")
    if not (isinstance(result, str) and has_live_right(handles, result, "read")):
        return "deny", "hydration-result-lacks-read", None
    hid = ticket.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "hydrate"):
        return "allow", "placeholder-hydrated", result
    return "deny", "hydration-missing-live-authority", None


def eval_handoff_external_app(op: dict[str, Any], records: dict[str, list[dict[str, Any]]]) -> tuple[str, str, str | None]:
    handoffs = index(records, "external_app_handoffs")
    handles = index(records, "handles")
    handoff = handoffs.get(op.get("handoff"))
    require(handoff is not None, f"unknown external app handoff {op.get('handoff')}")
    if handoff.get("claims_persistent_grant") is True:
        return "deny", "external-handoff-claims-persistent-grant", None
    if handoff.get("status") != "ready":
        return "deny", "external-handoff-not-ready", None
    if handoff.get("portal_approved") is not True:
        return "deny", "external-handoff-missing-portal-approval", None
    if handoff.get("redacted") is not True:
        return "deny", "external-handoff-unredacted", None
    target = handoff.get("target_handle")
    if not (isinstance(target, str) and has_live_right(handles, target, "read")):
        return "deny", "external-handoff-target-lacks-read", None
    hid = handoff.get("authority")
    if isinstance(hid, str) and has_live_right(handles, hid, "handoff"):
        return "allow", "external-app-handoff-issued", target
    return "deny", "external-handoff-missing-live-authority", None


EVALUATORS = {
    "read_handle": eval_read_handle,
    "attenuate_handle": eval_attenuate_handle,
    "compat_pathwalk": eval_compat_pathwalk,
    "portal_redeem": eval_portal_redeem,
    "semantic_open": eval_semantic_open,
    "consent_export": eval_consent_export,
    "retain_source_via_index": eval_retain_source_via_index,
    "commit_mutable_session": eval_commit_mutable_session,
    "reacquire_from_restore_token": eval_reacquire_from_restore_token,
    "sweep_decision": eval_sweep_decision,
    "tool_invocation": eval_tool_invocation,
    "delegate_handle": eval_delegate_handle,
    "render_shell_card": eval_render_shell_card,
    "forget_source": eval_forget_source,
    "quarantine_open": eval_quarantine_open,
    "trust_transition_release": eval_trust_transition_release,
    "render_authority_diff": eval_render_authority_diff,
    "export_plan": eval_export_plan,
    "policy_decision": eval_policy_decision,
    "witness_bundle_verify": eval_witness_bundle_verify,
    "scenario_replay": eval_scenario_replay,
    "override_grant": eval_override_grant,
    "renew_lease": eval_renew_lease,
    "publish_offline_branch": eval_publish_offline_branch,
    "reconcile_merge": eval_reconcile_merge,
    "verify_remote_attestation": eval_verify_remote_attestation,
    "check_freshness_fence": eval_check_freshness_fence,
    "checkpoint_journal": eval_checkpoint_journal,
    "redaction_view_read": eval_redaction_view_read,
    "render_audit_projection": eval_render_audit_projection,
    "disclose_package": eval_disclose_package,
    "deliver_notification": eval_deliver_notification,
    "subject_access_export": eval_subject_access_export,
    "compose_shared_view": eval_compose_shared_view,
    "group_bound_authority": eval_group_bound_authority,
    "resolve_label_overlay": eval_resolve_label_overlay,
    "handoff_packet": eval_handoff_packet,
    "render_collaboration_card": eval_render_collaboration_card,
    "collect_gc_candidate": eval_collect_gc_candidate,
    "prune_snapshot": eval_prune_snapshot,
    "release_archive_hold": eval_release_archive_hold,
    "restore_from_backup": eval_restore_from_backup,
    "verify_deletion_claim": eval_verify_deletion_claim,
    "verify_package_install": eval_verify_package_install,
    "resolve_dependency_pin": eval_resolve_dependency_pin,
    "verify_transparency_entry": eval_verify_transparency_entry,
    "admit_verifier_root": eval_admit_verifier_root,
    "bind_extension_tool": eval_bind_extension_tool,
    "invoke_extension_tool": eval_invoke_extension_tool,
    "reserve_budget": eval_reserve_budget,
    "admit_rate_limit": eval_admit_rate_limit,
    "start_background_job": eval_start_background_job,
    "hydrate_cache_entry": eval_hydrate_cache_entry,
    "emit_capacity_signal": eval_emit_capacity_signal,
    "settle_metering_receipt": eval_settle_metering_receipt,
    "verify_identity_session": eval_verify_identity_session,
    "redeem_credential_token": eval_redeem_credential_token,
    "open_encryption_envelope": eval_open_encryption_envelope,
    "rotate_key_version": eval_rotate_key_version,
    "lease_secret": eval_lease_secret,
    "inject_secret": eval_inject_secret,
    "recover_escrow": eval_recover_escrow,
    "render_secret_card": eval_render_secret_card,
    "verify_runtime_posture": eval_verify_runtime_posture,
    "admit_network_connector": eval_admit_network_connector,
    "redeem_clipboard_parcel": eval_redeem_clipboard_parcel,
    "redeem_dragdrop_parcel": eval_redeem_dragdrop_parcel,
    "bind_peripheral_device": eval_bind_peripheral_device,
    "observe_sensor_sample": eval_observe_sensor_sample,
    "apply_transform_plan": eval_apply_transform_plan,
    "decode_codec_payload": eval_decode_codec_payload,
    "apply_schema_migration": eval_apply_schema_migration,
    "apply_patch_set": eval_apply_patch_set,
    "attach_annotation_layer": eval_attach_annotation_layer,
    "verify_lineage_link": eval_verify_lineage_link,
    "render_preview_artifact": eval_render_preview_artifact,
    "admit_canonicalization_claim": eval_admit_canonicalization_claim,
    "evaluate_classification_mark": eval_evaluate_classification_mark,
    "authorize_license_use": eval_authorize_license_use,
    "check_jurisdiction_fence": eval_check_jurisdiction_fence,
    "enforce_compliance_obligation": eval_enforce_compliance_obligation,
    "approve_public_release": eval_approve_public_release,
    "bind_purpose_use": eval_bind_purpose_use,
    "render_compliance_card": eval_render_compliance_card,
    "admit_query_scope": eval_admit_query_scope,
    "admit_planner_trace": eval_admit_planner_trace,
    "open_result_member": eval_open_result_member,
    "render_aggregation_view": eval_render_aggregation_view,
    "admit_evaluation_set": eval_admit_evaluation_set,
    "record_benchmark_run": eval_record_benchmark_run,
    "apply_scoring_rubric": eval_apply_scoring_rubric,
    "render_model_selection_card": eval_render_model_selection_card,
    "admit_alert_signal": eval_admit_alert_signal,
    "open_incident_case": eval_open_incident_case,
    "apply_triage_verdict": eval_apply_triage_verdict,
    "capture_forensic_snapshot": eval_capture_forensic_snapshot,
    "verify_evidence_chain": eval_verify_evidence_chain,
    "approve_containment_plan": eval_approve_containment_plan,
    "execute_remediation_plan": eval_execute_remediation_plan,
    "execute_recovery_rollback": eval_execute_recovery_rollback,
    "render_postmortem_record": eval_render_postmortem_record,
    "admit_event_envelope": eval_admit_event_envelope,
    "evaluate_trigger_rule": eval_evaluate_trigger_rule,
    "fire_schedule_window": eval_fire_schedule_window,
    "start_workflow_run": eval_start_workflow_run,
    "execute_workflow_step": eval_execute_workflow_step,
    "apply_idempotency_key": eval_apply_idempotency_key,
    "apply_retry_policy": eval_apply_retry_policy,
    "execute_compensation_plan": eval_execute_compensation_plan,
    "complete_human_task": eval_complete_human_task,
    "render_workflow_card": eval_render_workflow_card,
    "admit_change_proposal": eval_admit_change_proposal,
    "record_decision": eval_record_decision,
    "verify_approval_quorum": eval_verify_approval_quorum,
    "start_rollout_plan": eval_start_rollout_plan,
    "evaluate_feature_flag": eval_evaluate_feature_flag,
    "enforce_deprecation_notice": eval_enforce_deprecation_notice,
    "check_compatibility_contract": eval_check_compatibility_contract,
    "execute_migration_run": eval_execute_migration_run,
    "render_governance_card": eval_render_governance_card,
"verify_user_profile": eval_verify_user_profile,
"apply_preference_set": eval_apply_preference_set,
"admit_personalization_model": eval_admit_personalization_model,
"render_recommendation_set": eval_render_recommendation_set,
"execute_shortcut_binding": eval_execute_shortcut_binding,
"accept_autofill_proposal": eval_accept_autofill_proposal,
"apply_experiment_assignment": eval_apply_experiment_assignment,
"record_feedback_signal": eval_record_feedback_signal,
"render_personalization_card": eval_render_personalization_card,
    "bind_namespace_context": eval_bind_namespace_context,
    "resolve_external_reference": eval_resolve_external_reference,
    "admit_vocabulary_term": eval_admit_vocabulary_term,
    "apply_crosswalk_mapping": eval_apply_crosswalk_mapping,
    "validate_shape_constraint": eval_validate_shape_constraint,
    "verify_ontology_alignment": eval_verify_ontology_alignment,
    "publish_catalog_entry": eval_publish_catalog_entry,
    "render_interop_card": eval_render_interop_card,

"admit_adapter_mount": eval_admit_adapter_mount,
"render_stat_projection": eval_render_stat_projection,
"resolve_inode_alias": eval_resolve_inode_alias,
"read_xattr_parcel": eval_read_xattr_parcel,
"deliver_watcher_event": eval_deliver_watcher_event,
"acquire_lock_token": eval_acquire_lock_token,
"execute_rename_plan": eval_execute_rename_plan,
"promote_tempfile_lease": eval_promote_tempfile_lease,
"hydrate_placeholder": eval_hydrate_placeholder,
"handoff_external_app": eval_handoff_external_app,
}


def evaluate(fixture: dict[str, Any]) -> tuple[str, str, str | None]:
    records = fixture["records"]
    op = fixture["operation"]
    operation = op.get("op")
    evaluator = EVALUATORS.get(operation)
    if evaluator is None:
        raise FixtureError(f"unsupported operation {operation!r}")
    return evaluator(op, records)

def check_fixture(path: Path) -> None:
    try:
        fixture = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise FixtureError(f"invalid JSON: {exc}") from exc
    require(isinstance(fixture, dict), "fixture top level must be an object")
    unknown = set(fixture) - TOP_KEYS
    missing = TOP_KEYS - set(fixture)
    require(not unknown, f"unknown top-level keys: {sorted(unknown)}")
    require(not missing, f"missing top-level keys: {sorted(missing)}")
    require(fixture["schema"] == SCHEMA, f"schema must be {SCHEMA}")
    require(fixture["mode"] in {"positive", "negative"}, "mode must be positive or negative")
    covers = fixture["covers"]
    require(isinstance(covers, list) and covers, "covers must be a non-empty list of proof-obligation ids")
    require(all(isinstance(c, str) and c.startswith("PO-VIEWFS-") for c in covers), "covers entries must be PO-VIEWFS-* strings")
    records = fixture["records"]
    require(isinstance(records, dict), "records must be object")
    unknown_records = set(records) - RECORD_KEYS
    missing_records = RECORD_KEYS - set(records)
    require(not unknown_records, f"unknown record families: {sorted(unknown_records)}")
    require(not missing_records, f"missing record families: {sorted(missing_records)}")
    for key, value in records.items():
        require(isinstance(value, list), f"records.{key} must be a list")
    result, reason, handle = evaluate(fixture)
    expect = fixture["expect"]
    require(result == expect.get("result"), f"expected result {expect.get('result')}, got {result}:{reason}")
    require(reason == expect.get("reason"), f"expected reason {expect.get('reason')}, got {reason}")
    if "handle" in expect:
        require(handle == expect["handle"], f"expected handle {expect['handle']}, got {handle}")
    if fixture["mode"] == "positive":
        require(result == "allow", "positive fixture must allow")
    if fixture["mode"] == "negative":
        require(result == "deny", "negative fixture must deny")


def main() -> int:
    errors: list[str] = []
    paths = sorted(FIXTURE_DIR.glob("*.json"))
    if not paths:
        errors.append(f"no fixtures found in {FIXTURE_DIR.relative_to(ROOT)}")
    seen_names: set[str] = set()
    for path in paths:
        try:
            data = json.loads(path.read_text())
            name = data.get("name")
            if name in seen_names:
                raise FixtureError(f"duplicate fixture name {name}")
            seen_names.add(name)
            check_fixture(path)
        except FixtureError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
        except Exception as exc:  # noqa: BLE001 - this is a lint/check script.
            errors.append(f"{path.relative_to(ROOT)}: unexpected error: {exc}")
    if errors:
        print("viewfs-core fixture check failed:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"viewfs-core fixture check: ok ({len(paths)} fixtures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
