#!/usr/bin/env python3
"""Small offline checks for volatile frontier-source freshness assertions.

The assertion file is intentionally narrow: it covers only current public source
rows that carry empirical-pressure or custody language. It is not a bibliography
registry and it performs no network access.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from source_role_event_utils import (
    CREDIT_CAP_VALUES,
    SOURCE_REF_DISPOSITIONS,
    SOURCE_ROLE_VALUES,
    covered_source_role_event_refs,
    is_metadata_wrapper_row_id,
)

sys.dont_write_bytecode = True

ASSERTION_FILE = "FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json"
GENERATED_AUDIT = "docs/30-program/frontier-source-freshness-audit.generated.md"

RECEIPT_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def bibliography_ref_ids(root: Path) -> set[str]:
    text = (root / "docs/00-meta/bibliography.md").read_text()
    return set(re.findall(r"^`?(REF-\d{4})`?", text)) | set(re.findall(r"`(REF-\d{4})`", text))


def _coerce_role_values(data: dict[str, Any], failures: list[str]) -> set[str]:
    declared = data.get("source_role_values", [])
    if not isinstance(declared, list):
        failures.append(f"{ASSERTION_FILE}: top-level source_role_values must be a list")
        return SOURCE_ROLE_VALUES
    declared_set = {str(item) for item in declared}
    missing = sorted(SOURCE_ROLE_VALUES - declared_set)
    extra = sorted(declared_set - SOURCE_ROLE_VALUES)
    if missing:
        failures.append(f"{ASSERTION_FILE}: source_role_values missing required roles {missing}")
    if extra:
        failures.append(f"{ASSERTION_FILE}: source_role_values contains unknown roles {extra}")
    return declared_set or SOURCE_ROLE_VALUES


def _validate_role_list(label: str, value: Any, allowed_roles: set[str], failures: list[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        failures.append(f"{label}: secondary_source_roles must be a list when present")
        return []
    roles = [str(item) for item in value]
    for role in roles:
        if role not in allowed_roles:
            failures.append(f"{label}: unknown secondary source role `{role}`")
    return roles


def _validate_receipts(
    assertion: dict[str, Any],
    allowed_roles: set[str],
    known_refs: set[str],
    failures: list[str],
) -> int:
    aid = assertion.get("assertion_id", "<missing-assertion-id>")
    receipts = assertion.get("source_snapshot_receipts", [])
    if receipts in (None, []):
        return 0
    if not isinstance(receipts, list):
        failures.append(f"{aid}: source_snapshot_receipts must be a list")
        return 0
    seen_receipts: set[str] = set()
    source_refs = set(assertion.get("source_refs_must_exist", []))
    for receipt in receipts:
        if not isinstance(receipt, dict):
            failures.append(f"{aid}: source_snapshot_receipts entries must be objects")
            continue
        rid = str(receipt.get("receipt_id", "<missing-receipt-id>"))
        if rid in seen_receipts:
            failures.append(f"{aid}: duplicate source_snapshot_receipt `{rid}`")
        seen_receipts.add(rid)
        for required_key in ["receipt_id", "source_ref", "checked_at", "public_status", "source_role", "no_promotion_disposition"]:
            if required_key not in receipt:
                failures.append(f"{aid}/{rid}: missing receipt field `{required_key}`")
        source_ref = str(receipt.get("source_ref", ""))
        if source_ref and source_ref not in known_refs:
            failures.append(f"{aid}/{rid}: receipt source ref `{source_ref}` is not present in bibliography")
        if source_ref and source_ref not in source_refs:
            failures.append(f"{aid}/{rid}: receipt source ref `{source_ref}` is not included in source_refs_must_exist")
        role = str(receipt.get("source_role", ""))
        if role and role not in allowed_roles:
            failures.append(f"{aid}/{rid}: unknown receipt source role `{role}`")
        checked_at = str(receipt.get("checked_at", ""))
        if checked_at and not RECEIPT_DATE_RE.match(checked_at):
            failures.append(f"{aid}/{rid}: checked_at must be YYYY-MM-DD")
        for text_key in ["public_status", "no_promotion_disposition"]:
            if text_key in receipt and not str(receipt.get(text_key, "")).strip():
                failures.append(f"{aid}/{rid}: `{text_key}` must not be empty")
    return len(receipts)


def _validate_string_list(label: str, value: Any, allowed: set[str], failures: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        failures.append(f"{label}: must be a non-empty list")
        return []
    out = [str(item) for item in value]
    bad = sorted(set(out) - allowed)
    if bad:
        failures.append(f"{label}: contains unknown values {bad}")
    return out


def _normalize_typed_event_replay_policy(
    aid: str,
    policy: Any,
    allowed_roles: set[str],
    failures: list[str],
    *,
    label: str,
    default_source_role: str = "",
) -> dict[str, Any] | None:
    """Normalize one event-replay policy object.

    rev0354 adds row-scoped mixed-role policies for assertions whose refs cannot
    honestly be replayed under a single source role.  The low-level vocabulary is
    still identical to the older one-policy assertion form.
    """
    if not isinstance(policy, dict):
        failures.append(f"{aid}: {label} must be an object when present")
        return None
    if policy.get("enabled") is not True:
        failures.append(f"{aid}: {label}.enabled must be true when policy is present")
    role = str(policy.get("source_role") or default_source_role or "")
    if role not in allowed_roles:
        failures.append(f"{aid}: {label} source_role is unknown: `{role}`")
    include_dispositions = _validate_string_list(
        f"{aid}: {label}.include_dispositions",
        policy.get("include_dispositions", []),
        SOURCE_REF_DISPOSITIONS,
        failures,
    )
    forbidden_dispositions = _validate_string_list(
        f"{aid}: {label}.forbidden_dispositions",
        policy.get("forbidden_dispositions", []),
        SOURCE_REF_DISPOSITIONS,
        failures,
    )
    excluded_dispositions = policy.get("excluded_dispositions", ["excluded_from_acquired_source_refs"])
    excluded_dispositions = _validate_string_list(
        f"{aid}: {label}.excluded_dispositions",
        excluded_dispositions,
        SOURCE_REF_DISPOSITIONS,
        failures,
    )
    forbidden_role = str(policy.get("forbidden_role", "metadata_wrapper"))
    if forbidden_role not in allowed_roles:
        failures.append(f"{aid}: {label} forbidden_role is unknown: `{forbidden_role}`")
    credit_cap = str(policy.get("credit_cap", ""))
    if credit_cap and credit_cap not in CREDIT_CAP_VALUES:
        failures.append(f"{aid}: {label} has unknown credit_cap `{credit_cap}`")
    return {
        "policy_id": str(policy.get("policy_id", label)),
        "source_role": role,
        "include_dispositions": set(include_dispositions),
        "forbidden_dispositions": set(forbidden_dispositions),
        "excluded_dispositions": set(excluded_dispositions),
        "forbidden_role": forbidden_role,
        "credit_cap": credit_cap,
    }


def _validate_typed_event_replay_policy(
    assertion: dict[str, Any],
    allowed_roles: set[str],
    failures: list[str],
) -> dict[str, Any] | None:
    """Return a normalized one-role event-replay policy for older assertions.

    The policy deliberately lives on the freshness assertion rather than in a new
    registry. It says: when a freshness assertion points at a row that carries
    `source_role_events`, the freshness check must verify the event disposition
    that makes the row safe to read.
    """
    aid = str(assertion.get("assertion_id", "<missing-assertion-id>"))
    policy = assertion.get("typed_event_replay_policy")
    if policy in (None, {}):
        return None
    return _normalize_typed_event_replay_policy(
        aid,
        policy,
        allowed_roles,
        failures,
        label="typed_event_replay_policy",
        default_source_role=str(assertion.get("source_role", "")),
    )


def _validate_row_scoped_typed_event_replay_policies(
    assertion: dict[str, Any],
    allowed_roles: set[str],
    failures: list[str],
) -> list[dict[str, Any]]:
    """Return normalized row-scoped replay policies for mixed-role assertions.

    A single frontier-source assertion sometimes mixes acquired public custody,
    interpretation/denominator pressure, and future runway timing.  rev0354 keeps
    those rows in one freshness assertion but requires the event replay to name
    the source role expected for each row/ref subset.
    """
    aid = str(assertion.get("assertion_id", "<missing-assertion-id>"))
    raw_policies = assertion.get("typed_event_replay_policies")
    if raw_policies in (None, []):
        return []
    if assertion.get("typed_event_replay_policy") not in (None, {}):
        failures.append(f"{aid}: use either typed_event_replay_policy or typed_event_replay_policies, not both")
    if not isinstance(raw_policies, list):
        failures.append(f"{aid}: typed_event_replay_policies must be a list when present")
        return []
    assertion_target_refs = set(assertion.get("source_refs_must_exist", []) or [])
    required_rows = assertion.get("required_row_refs", []) or []
    required_row_refs_by_key: dict[tuple[str, str], set[str]] = {}
    for spec in required_rows:
        if not isinstance(spec, dict):
            continue
        key = (str(spec.get("ledger_file", "")), str(spec.get("row_id", "")))
        required_row_refs_by_key.setdefault(key, set()).update(spec.get("source_refs_must_include", []) or [])
        required_row_refs_by_key[key].update(spec.get("source_refs_must_not_include", []) or [])
    normalized: list[dict[str, Any]] = []
    seen_policy_ids: set[str] = set()
    for idx, policy in enumerate(raw_policies):
        label = f"typed_event_replay_policies[{idx}]"
        item = _normalize_typed_event_replay_policy(
            aid,
            policy,
            allowed_roles,
            failures,
            label=label,
            default_source_role=str(assertion.get("source_role", "")),
        )
        if item is None:
            continue
        policy_id = str(item.get("policy_id") or f"{aid}-POLICY-{idx}")
        if policy_id in seen_policy_ids:
            failures.append(f"{aid}: duplicate typed_event_replay_policies policy_id `{policy_id}`")
        seen_policy_ids.add(policy_id)
        applies = policy.get("applies_to_rows", []) if isinstance(policy, dict) else []
        if not isinstance(applies, list) or not applies:
            failures.append(f"{aid}/{policy_id}: applies_to_rows must be a non-empty list")
            item["applies_to_rows"] = []
            normalized.append(item)
            continue
        normalized_applies: list[dict[str, Any]] = []
        for apply_idx, row_spec in enumerate(applies):
            if not isinstance(row_spec, dict):
                failures.append(f"{aid}/{policy_id}: applies_to_rows[{apply_idx}] must be an object")
                continue
            ledger_file = str(row_spec.get("ledger_file", ""))
            row_id = str(row_spec.get("row_id", ""))
            refs = row_spec.get("source_refs", [])
            refs = _validate_string_list(
                f"{aid}/{policy_id}: applies_to_rows[{apply_idx}].source_refs",
                refs,
                assertion_target_refs,
                failures,
            )
            key = (ledger_file, row_id)
            if key not in required_row_refs_by_key:
                failures.append(f"{aid}/{policy_id}: applies_to_rows[{apply_idx}] does not match a required_row_refs ledger_file/row_id pair: {key}")
            missing_from_required_row = sorted(set(refs) - required_row_refs_by_key.get(key, set()))
            if missing_from_required_row:
                failures.append(f"{aid}/{policy_id}: applies_to_rows[{apply_idx}] refs not present in that required_row_refs spec: {missing_from_required_row}")
            normalized_applies.append({"ledger_file": ledger_file, "row_id": row_id, "source_refs": set(refs)})
        item["applies_to_rows"] = normalized_applies
        normalized.append(item)
    return normalized


def _validate_watchlist_zero_route_placement_policy(
    assertion: dict[str, Any],
    failures: list[str],
) -> dict[str, Any] | None:
    """Validate a watchlist policy that requires zero route-bearing placements."""
    aid = str(assertion.get("assertion_id", "<missing-assertion-id>"))
    policy = assertion.get("watchlist_zero_route_placement_policy")
    if policy in (None, {}):
        return None
    if not isinstance(policy, dict):
        failures.append(f"{aid}: watchlist_zero_route_placement_policy must be an object when present")
        return None
    if policy.get("enabled") is not True:
        failures.append(f"{aid}: watchlist_zero_route_placement_policy.enabled must be true when policy is present")
    assertion_refs = set(assertion.get("source_refs_must_exist", []) or [])
    refs = policy.get("source_refs", [])
    refs = _validate_string_list(f"{aid}: watchlist_zero_route_placement_policy.source_refs", refs, assertion_refs, failures)
    allowed_count = policy.get("allowed_route_placements", 0)
    if allowed_count != 0:
        failures.append(f"{aid}: watchlist_zero_route_placement_policy.allowed_route_placements must be 0")
    rationale = str(policy.get("rationale", "")).strip()
    if not rationale:
        failures.append(f"{aid}: watchlist_zero_route_placement_policy.rationale must not be empty")
    return {"source_refs": set(refs), "allowed_route_placements": 0, "rationale": rationale}


def _evaluate_watchlist_zero_route_placement_policy(
    root: Path,
    assertion_id: str,
    policy: dict[str, Any],
    failures: list[str],
) -> dict[str, Any]:
    """Replay watchlist-zero placement against the executable isolation audit."""
    from frontier_source_policy import evaluate_frontier_source_isolation

    isolation = evaluate_frontier_source_isolation(root)
    source_refs = set(policy.get("source_refs", set()))
    placements = [item for item in isolation.get("placements", []) if item.get("ref") in source_refs]
    if placements:
        failures.append(
            f"{assertion_id}: watchlist refs have route-bearing placements despite zero-placement policy: "
            + "; ".join(f"{item.get('ref')} in {item.get('file')}:{item.get('row_id')}" for item in placements)
        )
    return {"source_refs": sorted(source_refs), "route_placements": len(placements), "failures": len(placements)}



def evaluate_frontier_source_freshness(root: Path) -> dict[str, Any]:
    path = root / ASSERTION_FILE
    if not path.exists():
        return {
            "assertion_file": ASSERTION_FILE,
            "assertions": [],
            "row_checks": [],
            "failures": [f"missing frontier-source assertion file: {ASSERTION_FILE}"],
            "total_required_rows": 0,
        }
    data = load_json(root, ASSERTION_FILE)
    known_refs = bibliography_ref_ids(root)
    failures: list[str] = []
    allowed_roles = _coerce_role_values(data, failures)
    row_checks: list[dict[str, Any]] = []
    assertion_summaries: list[dict[str, Any]] = []
    assertion_rows = data.get("assertion_rows", [])
    assertion_ids = [row.get("assertion_id", "<missing-assertion-id>") for row in assertion_rows]
    seen_assertion_ids: set[str] = set()
    duplicate_assertion_ids: set[str] = set()
    for aid in assertion_ids:
        if aid in seen_assertion_ids:
            duplicate_assertion_ids.add(aid)
        seen_assertion_ids.add(aid)
    for aid in sorted(duplicate_assertion_ids):
        failures.append(f"duplicate assertion_id `{aid}` in {ASSERTION_FILE}")
    numeric_stems: list[str] = []
    for aid in assertion_ids:
        m = re.match(r"^(FSF-\d{4})", str(aid))
        if m:
            numeric_stems.append(m.group(1))
    duplicate_numeric_stems = sorted({stem for stem in numeric_stems if numeric_stems.count(stem) > 1})
    for stem in duplicate_numeric_stems:
        failures.append(f"duplicate frontier-source assertion numeric stem `{stem}` in {ASSERTION_FILE}")
    replay_mode_counts = {
        "one_role_typed_replay": 0,
        "row_scoped_mixed_role_replay": 0,
        "zero_placement_watchlist": 0,
        "row_refs_only": 0,
    }
    for assertion in assertion_rows:
        aid = assertion.get("assertion_id", "<missing-assertion-id>")
        for required_key in [
            "assertion_id",
            "frontier_source",
            "freshness_state",
            "source_refs_must_exist",
            "required_row_refs",
            "source_role",
            "checked_at",
            "public_status",
            "no_promotion_disposition",
        ]:
            if required_key not in assertion:
                failures.append(f"{aid}: missing canonical assertion field `{required_key}`")
        if "required_row_source_refs" in assertion:
            failures.append(f"{aid}: deprecated field `required_row_source_refs` is ignored by older freshness checks; use canonical `required_row_refs`")
        source_role = str(assertion.get("source_role", ""))
        if source_role and source_role not in allowed_roles:
            failures.append(f"{aid}: unknown source role `{source_role}`")
        secondary_roles = _validate_role_list(str(aid), assertion.get("secondary_source_roles", []), allowed_roles, failures)
        checked_at = str(assertion.get("checked_at", ""))
        if checked_at and not RECEIPT_DATE_RE.match(checked_at):
            failures.append(f"{aid}: checked_at must be YYYY-MM-DD")
        for text_key in ["public_status", "no_promotion_disposition"]:
            if text_key in assertion and not str(assertion.get(text_key, "")).strip():
                failures.append(f"{aid}: `{text_key}` must not be empty")
        missing_assertion_refs = [ref for ref in assertion.get("source_refs_must_exist", []) if ref not in known_refs]
        for ref in missing_assertion_refs:
            failures.append(f"{aid}: source ref `{ref}` is not present in bibliography")
        receipt_count = _validate_receipts(assertion, allowed_roles, known_refs, failures)
        typed_event_policy = _validate_typed_event_replay_policy(assertion, allowed_roles, failures)
        row_scoped_event_policies = _validate_row_scoped_typed_event_replay_policies(assertion, allowed_roles, failures)
        watchlist_zero_policy = _validate_watchlist_zero_route_placement_policy(assertion, failures)
        if typed_event_policy:
            replay_mode_counts["one_role_typed_replay"] += 1
        if row_scoped_event_policies:
            replay_mode_counts["row_scoped_mixed_role_replay"] += 1
        if watchlist_zero_policy:
            replay_mode_counts["zero_placement_watchlist"] += 1
        if not typed_event_policy and not row_scoped_event_policies and not watchlist_zero_policy:
            replay_mode_counts["row_refs_only"] += 1
        assertion_failures_before = len(failures)
        required_rows = assertion.get("required_row_refs", [])
        assertion_target_refs = set(assertion.get("source_refs_must_exist", []) or [])
        row_scoped_policy_map: dict[tuple[str, str], list[tuple[dict[str, Any], set[str]]]] = {}
        for policy in row_scoped_event_policies:
            for row_spec in policy.get("applies_to_rows", []) or []:
                key = (str(row_spec.get("ledger_file", "")), str(row_spec.get("row_id", "")))
                row_scoped_policy_map.setdefault(key, []).append((policy, set(row_spec.get("source_refs", set()))))
        event_replay_rows = 0
        event_replay_failed_rows = 0
        for spec in required_rows:
            ledger_file = spec.get("ledger_file", "<missing-ledger>")
            row_collection = spec.get("row_collection", "<missing-row-collection>")
            id_field = spec.get("id_field", "<missing-id-field>")
            row_id = spec.get("row_id", "<missing-row-id>")
            must_include = spec.get("source_refs_must_include", [])
            must_not_include = spec.get("source_refs_must_not_include", [])
            check = {
                "assertion_id": aid,
                "ledger_file": ledger_file,
                "row_collection": row_collection,
                "row_id": row_id,
                "required_refs": must_include,
                "forbidden_refs": must_not_include,
                "present_refs": [],
                "missing_refs": [],
                "forbidden_present_refs": [],
                "event_required_refs": [],
                "event_forbidden_refs": [],
                "event_covered_refs": [],
                "event_forbidden_covered_refs": [],
                "event_missing_refs": [],
                "event_forbidden_missing_refs": [],
                "event_credit_cap_failures": [],
                "event_policy_checks": [],
                "event_policy_failures": [],
                "status": "pass",
            }
            ledger_path = root / ledger_file
            if not ledger_path.exists():
                check["status"] = "fail"
                check["missing_refs"] = list(must_include)
                failures.append(f"{aid}: missing ledger file `{ledger_file}` for row `{row_id}`")
                row_checks.append(check)
                continue
            ledger = load_json(root, ledger_file)
            rows = ledger.get(row_collection)
            if not isinstance(rows, list):
                check["status"] = "fail"
                check["missing_refs"] = list(must_include)
                failures.append(f"{aid}: `{ledger_file}` lacks list `{row_collection}` for row `{row_id}`")
                row_checks.append(check)
                continue
            row = next((item for item in rows if isinstance(item, dict) and item.get(id_field) == row_id), None)
            if row is None:
                check["status"] = "fail"
                check["missing_refs"] = list(must_include)
                failures.append(f"{aid}: `{ledger_file}` lacks `{id_field}` row `{row_id}`")
                row_checks.append(check)
                continue
            refs = row.get("source_refs", [])
            check["present_refs"] = [ref for ref in must_include if ref in refs]
            missing = [ref for ref in must_include if ref not in refs]
            forbidden_present = [ref for ref in must_not_include if ref in refs]
            check["missing_refs"] = missing
            check["forbidden_present_refs"] = forbidden_present
            if missing or forbidden_present:
                check["status"] = "fail"
            if missing:
                failures.append(f"{aid}: `{ledger_file}` row `{row_id}` missing source refs {missing}")
            if forbidden_present:
                failures.append(f"{aid}: `{ledger_file}` row `{row_id}` contains forbidden source refs {forbidden_present}")

            if typed_event_policy:
                include_event_refs = set(must_include) & assertion_target_refs
                forbidden_event_refs = set(must_not_include) & assertion_target_refs
                if include_event_refs:
                    event_replay_rows += 1
                    check["event_required_refs"] = sorted(include_event_refs)
                    covered, cap_failures, matched_event = covered_source_role_event_refs(
                        row,
                        include_event_refs,
                        source_role=str(typed_event_policy["source_role"]),
                        dispositions=set(typed_event_policy["include_dispositions"]),
                        credit_cap=str(typed_event_policy.get("credit_cap", "")),
                    )
                    missing_event_refs = sorted(include_event_refs - covered)
                    check["event_covered_refs"] = sorted(covered)
                    check["event_missing_refs"] = missing_event_refs
                    check["event_credit_cap_failures"].extend(cap_failures)
                    if missing_event_refs or cap_failures or not matched_event:
                        check["status"] = "fail"
                        event_replay_failed_rows += 1
                    if missing_event_refs:
                        failures.append(
                            f"{aid}: `{ledger_file}` row `{row_id}` lacks typed source_role_event coverage for refs {missing_event_refs}"
                        )
                    if cap_failures:
                        failures.append(
                            f"{aid}: `{ledger_file}` row `{row_id}` has typed source_role_event credit-cap failures {cap_failures}"
                        )
                if forbidden_event_refs:
                    event_replay_rows += 1
                    check["event_forbidden_refs"] = sorted(forbidden_event_refs)
                    if is_metadata_wrapper_row_id(row_id):
                        forbidden_role = str(typed_event_policy["forbidden_role"])
                        forbidden_dispositions = set(typed_event_policy["forbidden_dispositions"])
                    else:
                        forbidden_role = str(typed_event_policy["source_role"])
                        forbidden_dispositions = set(typed_event_policy["excluded_dispositions"])
                    covered, cap_failures, matched_event = covered_source_role_event_refs(
                        row,
                        forbidden_event_refs,
                        source_role=forbidden_role,
                        dispositions=forbidden_dispositions,
                        credit_cap=str(typed_event_policy.get("credit_cap", "")),
                    )
                    missing_event_refs = sorted(forbidden_event_refs - covered)
                    check["event_forbidden_covered_refs"] = sorted(covered)
                    check["event_forbidden_missing_refs"] = missing_event_refs
                    check["event_credit_cap_failures"].extend(cap_failures)
                    if missing_event_refs or cap_failures or not matched_event:
                        check["status"] = "fail"
                        event_replay_failed_rows += 1
                    if missing_event_refs:
                        failures.append(
                            f"{aid}: `{ledger_file}` row `{row_id}` lacks typed exclusion/forbidden source_role_event coverage for refs {missing_event_refs}"
                        )
                    if cap_failures:
                        failures.append(
                            f"{aid}: `{ledger_file}` row `{row_id}` has typed exclusion/forbidden credit-cap failures {cap_failures}"
                        )
            for policy, policy_refs in row_scoped_policy_map.get((str(ledger_file), str(row_id)), []):
                if not policy_refs:
                    continue
                event_replay_rows += 1
                policy_id = str(policy.get("policy_id", "<policy>"))
                covered, cap_failures, matched_event = covered_source_role_event_refs(
                    row,
                    set(policy_refs),
                    source_role=str(policy["source_role"]),
                    dispositions=set(policy["include_dispositions"]),
                    credit_cap=str(policy.get("credit_cap", "")),
                )
                missing_event_refs = sorted(set(policy_refs) - covered)
                policy_check = {
                    "policy_id": policy_id,
                    "source_role": policy.get("source_role"),
                    "source_ref_disposition_any_of": sorted(policy.get("include_dispositions", [])),
                    "credit_cap": policy.get("credit_cap", ""),
                    "required_refs": sorted(policy_refs),
                    "covered_refs": sorted(covered),
                    "missing_refs": missing_event_refs,
                    "credit_cap_failures": cap_failures,
                    "matched_event": matched_event,
                }
                check["event_policy_checks"].append(policy_check)
                if missing_event_refs or cap_failures or not matched_event:
                    check["status"] = "fail"
                    event_replay_failed_rows += 1
                    failure_text = (
                        f"policy `{policy_id}` role `{policy.get('source_role')}` lacks coverage for refs {missing_event_refs}"
                        if missing_event_refs
                        else f"policy `{policy_id}` role `{policy.get('source_role')}` did not match an event"
                    )
                    if cap_failures:
                        failure_text += f"; credit-cap failures {cap_failures}"
                    check["event_policy_failures"].append(failure_text)
                    failures.append(f"{aid}: `{ledger_file}` row `{row_id}` {failure_text}")
            row_checks.append(check)
        watchlist_zero_check = None
        if watchlist_zero_policy:
            watchlist_zero_check = _evaluate_watchlist_zero_route_placement_policy(root, str(aid), watchlist_zero_policy, failures)
        assertion_summaries.append({
            "assertion_id": aid,
            "frontier_source": assertion.get("frontier_source", ""),
            "freshness_state": assertion.get("freshness_state", ""),
            "source_role": source_role,
            "secondary_source_roles": secondary_roles,
            "checked_at": checked_at,
            "public_status": assertion.get("public_status", ""),
            "required_rows": len(required_rows),
            "typed_event_replay_rows": event_replay_rows,
            "typed_event_replay_failed_rows": event_replay_failed_rows,
            "watchlist_zero_placement_refs": len(watchlist_zero_check.get("source_refs", [])) if watchlist_zero_check else 0,
            "watchlist_zero_route_placements": watchlist_zero_check.get("route_placements", 0) if watchlist_zero_check else 0,
            "replay_mode": "row-scoped-mixed-role" if row_scoped_event_policies else ("one-role-typed" if typed_event_policy else ("zero-placement-watchlist" if watchlist_zero_policy else "row-refs-only")),
            "receipt_count": receipt_count,
            "failures": len(failures) - assertion_failures_before,
            "no_overclaim": assertion.get("no_overclaim", ""),
            "no_promotion_disposition": assertion.get("no_promotion_disposition", ""),
        })
    role_counts: dict[str, int] = {}
    for item in assertion_summaries:
        role = str(item.get("source_role") or "<missing>")
        role_counts[role] = role_counts.get(role, 0) + 1
    return {
        "assertion_file": ASSERTION_FILE,
        "revision": data.get("revision", "<missing>"),
        "schema_version": data.get("schema_version", "<missing>"),
        "purpose": data.get("purpose", ""),
        "non_promotion_rule": data.get("non_promotion_rule", ""),
        "source_role_values": sorted(allowed_roles),
        "role_counts": role_counts,
        "replay_mode_counts": replay_mode_counts,
        "assertions": assertion_summaries,
        "row_checks": row_checks,
        "failures": failures,
        "total_required_rows": len(row_checks),
        "total_typed_event_replay_rows": sum(1 for check in row_checks if check.get("event_required_refs") or check.get("event_forbidden_refs") or check.get("event_policy_checks")),
        "total_typed_event_replay_failed_rows": sum(1 for check in row_checks if check.get("event_missing_refs") or check.get("event_forbidden_missing_refs") or check.get("event_credit_cap_failures") or check.get("event_policy_failures")),
        "total_watchlist_zero_placement_refs": sum(item.get("watchlist_zero_placement_refs", 0) for item in assertion_summaries),
        "total_watchlist_zero_route_placements": sum(item.get("watchlist_zero_route_placements", 0) for item in assertion_summaries),
    }


def write_frontier_source_freshness_audit(root: Path) -> None:
    result = evaluate_frontier_source_freshness(root)
    checks_by_assertion: dict[str, list[dict[str, Any]]] = {}
    for check in result.get("row_checks", []):
        checks_by_assertion.setdefault(str(check.get("assertion_id")), []).append(check)

    lines = [
        "# Frontier-source freshness audit (generated)",
        "",
        f"Generated from `{ASSERTION_FILE}` and the named executable ledgers. Do not edit directly; run `make index` after changing frontier source assertions or source-carrying rows.",
        "",
        f"- Assertion revision: `{result.get('revision', '<missing>')}`",
        f"- Assertion schema version: `{result.get('schema_version', '<missing>')}`",
        f"- Freshness assertions: `{len(result.get('assertions', []))}`",
        f"- Required source-carrying rows checked: `{result.get('total_required_rows', 0)}`",
        f"- Typed source-role event rows replayed: `{result.get('total_typed_event_replay_rows', 0)}`",
        f"- Typed source-role event replay failures: `{result.get('total_typed_event_replay_failed_rows', 0)}`",
        f"- Watchlist zero-placement refs checked: `{result.get('total_watchlist_zero_placement_refs', 0)}`",
        f"- Watchlist route-bearing placements: `{result.get('total_watchlist_zero_route_placements', 0)}`",
        f"- Freshness failures: `{len(result.get('failures', []))}`",
        "",
        "## Source-role counts",
        "",
    ]
    for role, count in sorted(result.get("role_counts", {}).items()):
        lines.append(f"- `{role}`: `{count}`")
    lines += [
        "",
        "## Replay modes",
        "",
        "| Mode | Assertions |",
        "|---|---:|",
    ]
    for mode, count in sorted(result.get("replay_mode_counts", {}).items()):
        lines.append(f"| `{mode}` | `{count}` |")
    lines += [
        "",
        "## Assertion summary",
        "",
        "| Assertion | Replay mode | Source role | Checked at | Public status | Frontier source | Freshness state | Receipts | Required rows | Event rows | Watchlist refs | Watchlist placements | Failed rows |",
        "|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in result.get("assertions", []):
        aid = str(item.get("assertion_id"))
        row_checks = checks_by_assertion.get(aid, [])
        failed_rows = sum(1 for check in row_checks if check.get("status") != "pass")
        public_status = str(item.get("public_status", "")).replace("|", "/")
        lines.append(
            f"| `{aid}` | `{item.get('replay_mode', '')}` | `{item.get('source_role', '')}` | `{item.get('checked_at', '')}` | {public_status} | {item.get('frontier_source', '')} | `{item.get('freshness_state', '')}` | `{item.get('receipt_count', 0)}` | `{item.get('required_rows', 0)}` | `{item.get('typed_event_replay_rows', 0)}` | `{item.get('watchlist_zero_placement_refs', 0)}` | `{item.get('watchlist_zero_route_placements', 0)}` | `{failed_rows}` |"
        )

    lines += [
        "",
        "## Failure details",
        "",
    ]
    failed_checks = [check for check in result.get("row_checks", []) if check.get("status") != "pass"]
    if not result.get("failures") and not failed_checks:
        lines.append("None.")
    else:
        for item in result.get("failures", []):
            lines.append(f"- {item}")
        for check in failed_checks:
            required = ", ".join(f"`{ref}`" for ref in check.get("required_refs", [])) or "—"
            missing = ", ".join(f"`{ref}`" for ref in check.get("missing_refs", [])) or "—"
            forbidden_present = ", ".join(f"`{ref}`" for ref in check.get("forbidden_present_refs", [])) or "—"
            event_missing = ", ".join(f"`{ref}`" for ref in check.get("event_missing_refs", [])) or "—"
            event_forbidden_missing = ", ".join(f"`{ref}`" for ref in check.get("event_forbidden_missing_refs", [])) or "—"
            event_cap_failures = "; ".join(check.get("event_credit_cap_failures", [])) or "—"
            event_policy_failures = "; ".join(check.get("event_policy_failures", [])) or "—"
            row_label = f"`{check.get('ledger_file')}` / `{check.get('row_id')}`"
            lines.append(f"- `{check.get('assertion_id')}` {row_label}: required {required}; missing {missing}; forbidden present {forbidden_present}; event missing {event_missing}; event forbidden missing {event_forbidden_missing}; event cap failures {event_cap_failures}; row-scoped policy failures {event_policy_failures}")

    lines += [
        "",
        "## Typed event replay rule",
        "",
        "For assertions that declare `typed_event_replay_policy` or row-scoped `typed_event_replay_policies`, the evaluator now checks not only row-level `source_refs`, but also the covering `source_role_events` disposition and credit cap. Row-scoped policies are used when one freshness assertion mixes acquired support custody, denominator pressure, and future runway timing. This prevents a fresh public source from surviving as a bare row ref after its custody, denominator, handoff, exclusion, runway, or metadata-wrapper boundary event is removed.",
        "",
        "## Source-role receipt rule",
        "",
        "Every frontier-source assertion now carries `source_role`, `checked_at`, `public_status`, and `no_promotion_disposition`. Optional per-source snapshot receipts are validated when present. The allowed roles are `acquired_support`, `denominator_pressure`, `forecast_runway`, `operational_status`, and `metadata_wrapper`.",
        "Assertions that declare `watchlist_zero_route_placement_policy` also replay against the source-custody isolation evaluator and must have zero route-bearing placements for the named watchlist refs.",
        "",
        "## Compression note",
        "",
        "The evaluator still checks every required source-carrying row. The generated artifact intentionally retains assertion summaries and failure details rather than a row-by-row PASS table, keeping the control plane smaller while preserving failure visibility.",
        "",
        "## Non-promotion rule",
        "",
        result.get("non_promotion_rule") or "Freshness assertions repair custody and replay pressure only; they do not promote a route.",
        "",
        "## Why this exists",
        "",
        "Volatile public sources are high-value and high-risk: a current catalog, likelihood chain, or schedule can silently supersede the object named in an older row. This audit is intentionally narrow: it checks only the rows that currently spend public frontier-source language, and it treats watchlist-only sources as custody/timing pressure rather than evidence.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines))


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_frontier_source_freshness_audit(root)
    outcome = evaluate_frontier_source_freshness(root)
    if outcome["failures"]:
        print("FRONTIER SOURCE FRESHNESS FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("FRONTIER SOURCE FRESHNESS OK")
