#!/usr/bin/env python3
from __future__ import annotations

from collections.abc import Callable

REQUIRED_FIELDWORK_GAPS = [
    "GAP-029-affected-person-outcome-validation",
    "GAP-031-source-evidence-preservation-and-claim-capture",
    "GAP-032-license-maintainer-contribution-governance",
    "GAP-033-power-distribution-and-material-outcome-theory",
]


def require_text_contains(surface_id: str, field_name: str, text: str, tokens: list[str], fail: Callable[[str], None]) -> None:
    lower = str(text).lower()
    for token in tokens:
        if token not in lower:
            fail(f"{surface_id} {field_name} lacks required token {token!r}")


def validate_fieldwork_chain_links(
    *,
    surface_kind: str,
    surface_id: str,
    row: dict,
    known_gap_ids: set[str],
    source_claim_ids: set[str],
    authorization_gate_ids: set[str] | None,
    field_control_ids: set[str],
    sampling_gate_ids: set[str],
    plan_ids: set[str],
    authorization_gates: dict[str, dict] | None,
    field_intake_controls: dict[str, dict],
    fail: Callable[[str], None],
) -> dict[str, str]:
    """Validate the repeated fieldwork chain and return resolved IDs.

    This helper is intentionally small: it checks links common to fieldwork
    authorization and execution surfaces without hiding each surface's own
    status, privacy, or non-closing rules.
    """
    auth_id = row.get("linked_authorization_gate")
    control_id = row.get("linked_field_intake_control")
    sampling_id = row.get("linked_sampling_gate")
    plan_id = row.get("linked_outcome_tail_plan")

    if authorization_gate_ids is not None:
        if auth_id not in authorization_gate_ids:
            fail(f"{surface_kind} {surface_id} links unknown authorization gate {auth_id}")
    if control_id not in field_control_ids:
        fail(f"{surface_kind} {surface_id} links unknown field-intake control {control_id}")
    if sampling_id not in sampling_gate_ids:
        fail(f"{surface_kind} {surface_id} links unknown sampling gate {sampling_id}")
    if plan_id not in plan_ids:
        fail(f"{surface_kind} {surface_id} links unknown outcome-tail plan {plan_id}")

    linked_control = field_intake_controls.get(control_id, {})
    if linked_control.get("linked_sampling_gate") != sampling_id or linked_control.get("linked_outcome_tail_plan") != plan_id:
        fail(f"{surface_kind} {surface_id} control/gate/plan mismatch")

    if authorization_gates is not None and auth_id in authorization_gates:
        linked_auth = authorization_gates.get(auth_id, {})
        if linked_auth.get("linked_field_intake_control") != control_id or linked_auth.get("linked_sampling_gate") != sampling_id or linked_auth.get("linked_outcome_tail_plan") != plan_id:
            fail(f"{surface_kind} {surface_id} authorization/control/gate/plan mismatch")

    for required_gap in REQUIRED_FIELDWORK_GAPS:
        if required_gap not in row.get("linked_gaps", []):
            fail(f"{surface_kind} {surface_id} must block {required_gap}")
    for gap_id in row.get("linked_gaps", []):
        if gap_id not in known_gap_ids:
            fail(f"{surface_kind} {surface_id} links unknown gap {gap_id}")

    linked_receipts = set(row.get("linked_source_claim_receipts", []))
    if not linked_receipts:
        fail(f"{surface_kind} {surface_id} must link at least one source-claim receipt")
    for receipt_id in linked_receipts:
        if receipt_id not in source_claim_ids:
            fail(f"{surface_kind} {surface_id} links unknown source-claim receipt {receipt_id}")

    return {
        "authorization_gate": str(auth_id),
        "field_intake_control": str(control_id),
        "sampling_gate": str(sampling_id),
        "outcome_tail_plan": str(plan_id),
    }



def validate_fieldwork_follow_on_links(
    *,
    surface_kind: str,
    surface_id: str,
    row: dict,
    execution_control_ids: set[str],
    execution_controls: dict[str, dict],
    known_gap_ids: set[str],
    source_claim_ids: set[str],
    authorization_gate_ids: set[str],
    field_control_ids: set[str],
    sampling_gate_ids: set[str],
    plan_ids: set[str],
    authorization_gates: dict[str, dict],
    field_intake_controls: dict[str, dict],
    fail: Callable[[str], None],
) -> dict[str, str]:
    """Validate a fieldwork surface that follows execution controls.

    Release/publication-control surfaces must not invent a parallel chain. They
    must point to a known execution control, and the execution control must point
    to the same authorization, intake, sampling, and outcome-tail records.
    """
    execution_id = row.get("linked_fieldwork_execution_control")
    if execution_id not in execution_control_ids:
        fail(f"{surface_kind} {surface_id} links unknown fieldwork execution control {execution_id}")

    ids = validate_fieldwork_chain_links(
        surface_kind=surface_kind,
        surface_id=surface_id,
        row=row,
        known_gap_ids=known_gap_ids,
        source_claim_ids=source_claim_ids,
        authorization_gate_ids=authorization_gate_ids,
        field_control_ids=field_control_ids,
        sampling_gate_ids=sampling_gate_ids,
        plan_ids=plan_ids,
        authorization_gates=authorization_gates,
        field_intake_controls=field_intake_controls,
        fail=fail,
    )
    execution = execution_controls.get(str(execution_id), {})
    if execution:
        pairs = {
            "linked_authorization_gate": ids["authorization_gate"],
            "linked_field_intake_control": ids["field_intake_control"],
            "linked_sampling_gate": ids["sampling_gate"],
            "linked_outcome_tail_plan": ids["outcome_tail_plan"],
        }
        for field, expected in pairs.items():
            if execution.get(field) != expected:
                fail(f"{surface_kind} {surface_id} execution/{field} mismatch: {execution_id} -> {execution.get(field)} vs {expected}")
    ids["fieldwork_execution_control"] = str(execution_id)
    return ids



def validate_fieldwork_post_release_links(
    *,
    surface_kind: str,
    surface_id: str,
    row: dict,
    release_control_ids: set[str],
    release_controls: dict[str, dict],
    execution_control_ids: set[str],
    execution_controls: dict[str, dict],
    known_gap_ids: set[str],
    source_claim_ids: set[str],
    authorization_gate_ids: set[str],
    field_control_ids: set[str],
    sampling_gate_ids: set[str],
    plan_ids: set[str],
    authorization_gates: dict[str, dict],
    field_intake_controls: dict[str, dict],
    fail: Callable[[str], None],
) -> dict[str, str]:
    """Validate a fieldwork surface that follows public release controls.

    Correction/withdrawal-control surfaces must inherit the already-validated
    release chain. They may not invent a parallel release, execution,
    authorization, intake, sampling, or outcome-tail lineage.
    """
    release_id = row.get("linked_fieldwork_release_control")
    if release_id not in release_control_ids:
        fail(f"{surface_kind} {surface_id} links unknown fieldwork release control {release_id}")

    ids = validate_fieldwork_follow_on_links(
        surface_kind=surface_kind,
        surface_id=surface_id,
        row=row,
        execution_control_ids=execution_control_ids,
        execution_controls=execution_controls,
        known_gap_ids=known_gap_ids,
        source_claim_ids=source_claim_ids,
        authorization_gate_ids=authorization_gate_ids,
        field_control_ids=field_control_ids,
        sampling_gate_ids=sampling_gate_ids,
        plan_ids=plan_ids,
        authorization_gates=authorization_gates,
        field_intake_controls=field_intake_controls,
        fail=fail,
    )
    release = release_controls.get(str(release_id), {})
    if release:
        pairs = {
            "linked_fieldwork_execution_control": ids["fieldwork_execution_control"],
            "linked_authorization_gate": ids["authorization_gate"],
            "linked_field_intake_control": ids["field_intake_control"],
            "linked_sampling_gate": ids["sampling_gate"],
            "linked_outcome_tail_plan": ids["outcome_tail_plan"],
        }
        for field, expected in pairs.items():
            if release.get(field) != expected:
                fail(f"{surface_kind} {surface_id} release/{field} mismatch: {release_id} -> {release.get(field)} vs {expected}")
    ids["fieldwork_release_control"] = str(release_id)
    return ids


def validate_fieldwork_post_correction_links(
    *,
    surface_kind: str,
    surface_id: str,
    row: dict,
    correction_control_ids: set[str],
    correction_controls: dict[str, dict],
    release_control_ids: set[str],
    release_controls: dict[str, dict],
    execution_control_ids: set[str],
    execution_controls: dict[str, dict],
    known_gap_ids: set[str],
    source_claim_ids: set[str],
    authorization_gate_ids: set[str],
    field_control_ids: set[str],
    sampling_gate_ids: set[str],
    plan_ids: set[str],
    authorization_gates: dict[str, dict],
    field_intake_controls: dict[str, dict],
    fail: Callable[[str], None],
) -> dict[str, str]:
    """Validate a fieldwork surface that follows correction controls.

    Redress-verification surfaces must inherit the already-validated correction
    chain. They may not invent a parallel correction, release, execution,
    authorization, intake, sampling, or outcome-tail lineage.
    """
    correction_id = row.get("linked_fieldwork_correction_control")
    if correction_id not in correction_control_ids:
        fail(f"{surface_kind} {surface_id} links unknown fieldwork correction control {correction_id}")

    ids = validate_fieldwork_post_release_links(
        surface_kind=surface_kind,
        surface_id=surface_id,
        row=row,
        release_control_ids=release_control_ids,
        release_controls=release_controls,
        execution_control_ids=execution_control_ids,
        execution_controls=execution_controls,
        known_gap_ids=known_gap_ids,
        source_claim_ids=source_claim_ids,
        authorization_gate_ids=authorization_gate_ids,
        field_control_ids=field_control_ids,
        sampling_gate_ids=sampling_gate_ids,
        plan_ids=plan_ids,
        authorization_gates=authorization_gates,
        field_intake_controls=field_intake_controls,
        fail=fail,
    )
    correction = correction_controls.get(str(correction_id), {})
    if correction:
        pairs = {
            "linked_fieldwork_release_control": ids["fieldwork_release_control"],
            "linked_fieldwork_execution_control": ids["fieldwork_execution_control"],
            "linked_authorization_gate": ids["authorization_gate"],
            "linked_field_intake_control": ids["field_intake_control"],
            "linked_sampling_gate": ids["sampling_gate"],
            "linked_outcome_tail_plan": ids["outcome_tail_plan"],
        }
        for field, expected in pairs.items():
            if correction.get(field) != expected:
                fail(f"{surface_kind} {surface_id} correction/{field} mismatch: {correction_id} -> {correction.get(field)} vs {expected}")
    ids["fieldwork_correction_control"] = str(correction_id)
    return ids


def validate_fieldwork_post_redress_links(
    *,
    surface_kind: str,
    surface_id: str,
    row: dict,
    redress_control_ids: set[str],
    redress_controls: dict[str, dict],
    correction_control_ids: set[str],
    correction_controls: dict[str, dict],
    release_control_ids: set[str],
    release_controls: dict[str, dict],
    execution_control_ids: set[str],
    execution_controls: dict[str, dict],
    known_gap_ids: set[str],
    source_claim_ids: set[str],
    authorization_gate_ids: set[str],
    field_control_ids: set[str],
    sampling_gate_ids: set[str],
    plan_ids: set[str],
    authorization_gates: dict[str, dict],
    field_intake_controls: dict[str, dict],
    fail: Callable[[str], None],
) -> dict[str, str]:
    """Validate a fieldwork surface that follows redress verification controls.

    Closure-dossier surfaces must inherit the already-validated redress chain.
    They may not invent a parallel redress, correction, release, execution,
    authorization, intake, sampling, or outcome-tail lineage.
    """
    redress_id = row.get("linked_fieldwork_redress_verification_control")
    if redress_id not in redress_control_ids:
        fail(f"{surface_kind} {surface_id} links unknown fieldwork redress verification control {redress_id}")

    ids = validate_fieldwork_post_correction_links(
        surface_kind=surface_kind,
        surface_id=surface_id,
        row=row,
        correction_control_ids=correction_control_ids,
        correction_controls=correction_controls,
        release_control_ids=release_control_ids,
        release_controls=release_controls,
        execution_control_ids=execution_control_ids,
        execution_controls=execution_controls,
        known_gap_ids=known_gap_ids,
        source_claim_ids=source_claim_ids,
        authorization_gate_ids=authorization_gate_ids,
        field_control_ids=field_control_ids,
        sampling_gate_ids=sampling_gate_ids,
        plan_ids=plan_ids,
        authorization_gates=authorization_gates,
        field_intake_controls=field_intake_controls,
        fail=fail,
    )
    redress = redress_controls.get(str(redress_id), {})
    if redress:
        pairs = {
            "linked_fieldwork_correction_control": ids["fieldwork_correction_control"],
            "linked_fieldwork_release_control": ids["fieldwork_release_control"],
            "linked_fieldwork_execution_control": ids["fieldwork_execution_control"],
            "linked_authorization_gate": ids["authorization_gate"],
            "linked_field_intake_control": ids["field_intake_control"],
            "linked_sampling_gate": ids["sampling_gate"],
            "linked_outcome_tail_plan": ids["outcome_tail_plan"],
        }
        for field, expected in pairs.items():
            if redress.get(field) != expected:
                fail(f"{surface_kind} {surface_id} redress/{field} mismatch: {redress_id} -> {redress.get(field)} vs {expected}")
    ids["fieldwork_redress_verification_control"] = str(redress_id)
    return ids



def validate_fieldwork_post_closure_links(
    *,
    surface_kind: str,
    surface_id: str,
    row: dict,
    closure_dossier_ids: set[str],
    closure_dossiers: dict[str, dict],
    redress_control_ids: set[str],
    redress_controls: dict[str, dict],
    correction_control_ids: set[str],
    correction_controls: dict[str, dict],
    release_control_ids: set[str],
    release_controls: dict[str, dict],
    execution_control_ids: set[str],
    execution_controls: dict[str, dict],
    known_gap_ids: set[str],
    source_claim_ids: set[str],
    authorization_gate_ids: set[str],
    field_control_ids: set[str],
    sampling_gate_ids: set[str],
    plan_ids: set[str],
    authorization_gates: dict[str, dict],
    field_intake_controls: dict[str, dict],
    fail: Callable[[str], None],
) -> dict[str, str]:
    """Validate a fieldwork surface that follows closure dossiers.

    Post-closure monitoring surfaces must inherit the already-validated closure
    chain. They may not invent a parallel closure, redress, correction, release,
    execution, authorization, intake, sampling, or outcome-tail lineage.
    """
    closure_id = row.get("linked_fieldwork_closure_dossier")
    if closure_id not in closure_dossier_ids:
        fail(f"{surface_kind} {surface_id} links unknown fieldwork closure dossier {closure_id}")

    ids = validate_fieldwork_post_redress_links(
        surface_kind=surface_kind,
        surface_id=surface_id,
        row=row,
        redress_control_ids=redress_control_ids,
        redress_controls=redress_controls,
        correction_control_ids=correction_control_ids,
        correction_controls=correction_controls,
        release_control_ids=release_control_ids,
        release_controls=release_controls,
        execution_control_ids=execution_control_ids,
        execution_controls=execution_controls,
        known_gap_ids=known_gap_ids,
        source_claim_ids=source_claim_ids,
        authorization_gate_ids=authorization_gate_ids,
        field_control_ids=field_control_ids,
        sampling_gate_ids=sampling_gate_ids,
        plan_ids=plan_ids,
        authorization_gates=authorization_gates,
        field_intake_controls=field_intake_controls,
        fail=fail,
    )
    closure = closure_dossiers.get(str(closure_id), {})
    if closure:
        pairs = {
            "linked_fieldwork_redress_verification_control": ids["fieldwork_redress_verification_control"],
            "linked_fieldwork_correction_control": ids["fieldwork_correction_control"],
            "linked_fieldwork_release_control": ids["fieldwork_release_control"],
            "linked_fieldwork_execution_control": ids["fieldwork_execution_control"],
            "linked_authorization_gate": ids["authorization_gate"],
            "linked_field_intake_control": ids["field_intake_control"],
            "linked_sampling_gate": ids["sampling_gate"],
            "linked_outcome_tail_plan": ids["outcome_tail_plan"],
        }
        for field, expected in pairs.items():
            if closure.get(field) != expected:
                fail(f"{surface_kind} {surface_id} closure/{field} mismatch: {closure_id} -> {closure.get(field)} vs {expected}")
    ids["fieldwork_closure_dossier"] = str(closure_id)
    return ids



def validate_archive_stewardship_handoff_control(
    *,
    control_id: str,
    row: dict,
    known_gap_ids: set[str],
    source_claim_ids: set[str],
    fail: Callable[[str], None],
) -> None:
    """Validate archive-wide stewardship handoff rows.

    These rows are deliberately not part of the claimant/household fieldwork
    chain. They protect the archive itself: license, maintainer, contribution,
    security, source-refresh, route-retirement, and succession decisions.
    """
    if not control_id.startswith("ASH-"):
        fail(f"archive stewardship handoff control id should start with ASH-: {control_id}")
    status = row.get("handoff_status", "")
    if any(token in status.lower() for token in ["approved", "active", "complete", "closed", "validated"]):
        fail(f"archive stewardship handoff control {control_id} claims approval/closure-like status: {status}")
    for gap_id in row.get("linked_gaps", []):
        if gap_id not in known_gap_ids:
            fail(f"archive stewardship handoff control {control_id} links unknown gap {gap_id}")
    for receipt_id in row.get("linked_source_claim_receipts", []):
        if receipt_id not in source_claim_ids:
            fail(f"archive stewardship handoff control {control_id} links unknown source-claim receipt {receipt_id}")
    for field_name in [
        "required_owner_decisions",
        "required_public_documents",
        "role_classes_required",
        "handoff_clocks",
        "allowed_cube_artifacts",
        "prohibited_cube_artifacts",
    ]:
        values = row.get(field_name, [])
        if not isinstance(values, list) or not values:
            fail(f"archive stewardship handoff control {control_id} missing non-empty {field_name}")
    blocker = row.get("handoff_blocker", "")
    if not isinstance(blocker, str) or not blocker.strip():
        fail(f"archive stewardship handoff control {control_id} lacks handoff_blocker")
    text = " ".join(
        row.get("required_owner_decisions", [])
        + row.get("required_public_documents", [])
        + row.get("role_classes_required", [])
        + row.get("handoff_clocks", [])
        + [blocker, row.get("next_action", "")]
    ).lower()
    for token in ["license", "maintainer", "security", "succession"]:
        if token not in text:
            fail(f"archive stewardship handoff control {control_id} lacks {token} stewardship language")
    if any(token in (blocker + " " + row.get("next_action", "")).lower() for token in ["gap closed", "owner approved", "license granted", "maintainer appointed", "custody complete"]):
        fail(f"archive stewardship handoff control {control_id} uses handoff-as-proof language")
    allowed_text = " ".join(row.get("allowed_cube_artifacts", [])).lower()
    if any(token in allowed_text for token in ["private", "credential", "token", "secret", "legal advice", "vulnerability report"]):
        fail(f"archive stewardship handoff control {control_id} allowed artifacts appear to allow private stewardship material")
