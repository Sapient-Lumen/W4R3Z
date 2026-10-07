#!/usr/bin/env python3
"""Verify release evidence-pack registry and attached pack manifests."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()




HOSTILE_REVIEW_OVERLAY = "release_queue/HOSTILE_REVIEW_VECTORS.json"


def hostile_vectors_pass(hostile: dict[str, Any], *, minimum_count: int, expected_ids: set[str] | None = None) -> tuple[bool, dict[str, Any]]:
    vectors = hostile.get("vectors", []) if isinstance(hostile.get("vectors"), list) else []
    seen_ids = {str(row.get("id")) for row in vectors if isinstance(row, dict)}
    failed_rows = [row for row in vectors if isinstance(row, dict) and row.get("status") != "pass"]
    missing_ids = sorted((expected_ids or set()) - seen_ids)
    ok = (
        hostile.get("status") == "pass"
        and len(vectors) >= minimum_count
        and not failed_rows
        and not missing_ids
        and hostile.get("blocking_publication_until_external_review") is True
        and hostile.get("external_reviewer_signoff") == "missing"
    )
    return ok, {
        "hostile_status": hostile.get("status"),
        "vector_count": len(vectors),
        "seen_ids": sorted(seen_ids),
        "missing_ids": missing_ids,
        "failed_vectors": failed_rows[:5],
        "external_reviewer_signoff": hostile.get("external_reviewer_signoff"),
        "blocking_publication_until_external_review": hostile.get("blocking_publication_until_external_review"),
    }


def hostile_overlay_state(root: pathlib.Path, release: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path = root / HOSTILE_REVIEW_OVERLAY
    if not path.exists():
        return {}, [{"category": "hostile_review_overlay_missing", "path": HOSTILE_REVIEW_OVERLAY}]
    try:
        overlay = load_json(path)
    except Exception as exc:  # noqa: BLE001
        return {}, [{"category": "hostile_review_overlay_unreadable", "path": HOSTILE_REVIEW_OVERLAY, "error": str(exc)}]
    problems: list[dict[str, Any]] = []
    if overlay.get("generated_for_revision") != release.get("revision"):
        problems.append({"category": "hostile_review_overlay_revision_mismatch", "overlay": overlay.get("generated_for_revision"), "current": release.get("revision")})
    if overlay.get("checked_bundle") != release.get("bundle"):
        problems.append({"category": "hostile_review_overlay_bundle_mismatch", "overlay": overlay.get("checked_bundle"), "current": release.get("bundle")})
    if overlay.get("publication_authorized") is not False:
        problems.append({"category": "hostile_review_overlay_publication_authorized_not_false"})
    return overlay, problems


def hostile_overlay_entry(overlay: dict[str, Any], source_tex: str) -> dict[str, Any] | None:
    for row in overlay.get("entries", []):
        if isinstance(row, dict) and row.get("source_tex") == source_tex:
            return row
    return None


def rel_inside(root: pathlib.Path, rel: str) -> pathlib.Path | None:
    path = (root / rel).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path


def published_receipts_by_evidence_manifest(root: pathlib.Path) -> dict[str, dict[str, Any]]:
    receipts: dict[str, dict[str, Any]] = {}
    published_root = root / "published"
    if not published_root.exists():
        return receipts
    for receipt_path in sorted(published_root.glob("*/PUBLICATION_RECEIPT.json")):
        try:
            receipt = load_json(receipt_path)
        except Exception:
            continue
        manifest = str(receipt.get("evidence_pack_manifest", ""))
        if manifest:
            receipts[manifest] = receipt
    return receipts


def historical_decision_note_mismatch_allowed(entry: dict[str, Any], manifest: dict[str, Any], manifest_rel: str, published_receipts: dict[str, dict[str, Any]]) -> bool:
    """Permit queue-note path drift only for already-published immutable evidence.

    Publication moves a queue note from ``published_ready`` to ``published`` after
    the freeze packet has already bound the evidence-pack manifest digest.
    Rewriting that historical evidence pack would break the freeze packet.
    Therefore the checker accepts this one-field registry/manifest difference
    only when a publication receipt binds the same evidence manifest, source,
    and source hash, and the registry's current decision note is the published
    queue note.  Current unpublished lanes remain strict.
    """
    receipt = published_receipts.get(manifest_rel)
    if not isinstance(receipt, dict):
        return False
    if str(entry.get("decision_note", "")).startswith("release_queue/published/") is False:
        return False
    if not str(manifest.get("decision_note", "")).startswith("release_queue/published_ready/"):
        return False
    for key in ["source_tex", "source_sha256"]:
        if str(entry.get(key, "")) != str(manifest.get(key, "")) or str(receipt.get(key, "")) != str(entry.get(key, "")):
            return False
    return True


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    registry_path = root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json"
    failures: list[dict[str, Any]] = []
    entry_reports: list[dict[str, Any]] = []
    if not registry_path.exists():
        return {
            "status": "pass",
            "generated_for_revision": release["revision"],
            "checked_bundle": release["bundle"],
            "publication_authorized": False,
            "registry_present": False,
            "entries": [],
            "summary": {"registry_entry_count": 0, "attached_entry_count": 0, "checks_failed": 0},
            "fail_closed_rule": "No registry means no evidence pack has been attached; selected freeze targets remain gated by evidence policy.",
        }

    registry = load_json(registry_path)
    if registry.get("publication_authorized") is not False:
        failures.append({"category": "registry_publication_authorized_not_false"})
    if registry.get("generated_for_revision") != release["revision"]:
        failures.append({"category": "registry_revision_mismatch", "registry": registry.get("generated_for_revision"), "current": release["revision"]})
    if registry.get("checked_bundle") != release["bundle"]:
        failures.append({"category": "registry_bundle_mismatch", "registry": registry.get("checked_bundle"), "current": release["bundle"]})

    published_receipts = published_receipts_by_evidence_manifest(root)
    hostile_overlay, hostile_overlay_problems = hostile_overlay_state(root, release)
    registered_manifests = {str(entry.get("manifest", "")) for entry in registry.get("entries", []) if isinstance(entry, dict)}
    pack_root = root / "release_queue" / "evidence_packs"
    actual_manifests = {p.relative_to(root).as_posix() for p in pack_root.glob("*/EVIDENCE_PACK_MANIFEST.json")} if pack_root.exists() else set()
    unregistered = sorted(actual_manifests - registered_manifests)
    for rel in unregistered:
        failures.append({"category": "unregistered_evidence_pack_manifest", "path": rel})

    for entry in registry.get("entries", []):
        entry_failures: list[dict[str, Any]] = []
        manifest_rel = str(entry.get("manifest", ""))
        manifest_path = rel_inside(root, manifest_rel)
        manifest: dict[str, Any] = {}
        if manifest_path is None or not manifest_path.exists():
            entry_failures.append({"category": "manifest_missing_or_escapes_archive", "path": manifest_rel})
        else:
            manifest = load_json(manifest_path)
            if manifest.get("publication_authorized") is not False:
                entry_failures.append({"category": "manifest_publication_authorized_not_false"})
            for key in ["evidence_pack_id", "source_tex", "source_sha256", "title", "decision_note"]:
                if str(manifest.get(key, "")) != str(entry.get(key, "")):
                    if key == "decision_note" and historical_decision_note_mismatch_allowed(entry, manifest, manifest_rel, published_receipts):
                        continue
                    entry_failures.append({"category": "entry_manifest_mismatch", "key": key, "entry": entry.get(key), "manifest": manifest.get(key)})
            source_rel = str(entry.get("source_tex", ""))
            source_path = rel_inside(root, source_rel)
            if source_path is None or not source_path.exists():
                entry_failures.append({"category": "source_missing_or_escapes_archive", "source_tex": source_rel})
            else:
                actual_sha = sha256_file(source_path)
                if actual_sha != entry.get("source_sha256") or actual_sha != manifest.get("source_sha256"):
                    entry_failures.append({"category": "source_sha256_mismatch", "source_tex": source_rel, "actual": actual_sha, "entry": entry.get("source_sha256"), "manifest": manifest.get("source_sha256")})
            roles = {row.get("role") for row in manifest.get("pack_paths", []) if isinstance(row, dict)}
            required_roles = {"pack_readme", "release_preflight_static_report"}
            missing_roles = sorted(required_roles - roles)
            if missing_roles:
                entry_failures.append({"category": "missing_required_pack_roles", "roles": missing_roles})
            card_roles = {"certified_menu_card", "routing_signature_manifest_card", "congestion_eq_accountant_card", "pscq_mechanism_card", "wcongeq_replay_card", "calibration_recipe_card", "state_anonymity_accountant_card", "mucc_contact_floor_card", "source_bound_static_preflight_card"}
            if not (roles & card_roles):
                entry_failures.append({"category": "missing_required_pack_card_role", "accepted_roles": sorted(card_roles)})
            for row in manifest.get("pack_paths", []):
                if not isinstance(row, dict):
                    entry_failures.append({"category": "malformed_pack_path_row", "row": row})
                    continue
                rel = str(row.get("path", ""))
                path = rel_inside(root, rel)
                if path is None or not path.exists():
                    entry_failures.append({"category": "pack_path_missing_or_escapes_archive", "path": rel})
                    continue
                actual = sha256_file(path)
                if actual != row.get("sha256"):
                    entry_failures.append({"category": "pack_path_sha256_mismatch", "path": rel, "expected": row.get("sha256"), "actual": actual})
                if manifest.get("evidence_pack_root") and not rel.startswith(str(manifest.get("evidence_pack_root")).rstrip("/") + "/"):
                    entry_failures.append({"category": "pack_path_outside_pack_root", "path": rel, "root": manifest.get("evidence_pack_root")})

            card_rows = [row for row in manifest.get("pack_paths", []) if isinstance(row, dict) and row.get("role") in card_roles]
            if card_rows:
                card_rel = card_rows[0].get("path", "")
                card_path = rel_inside(root, str(card_rel))
                if card_path and card_path.exists():
                    card = load_json(card_path)
                    values = card.get("card_values", {}) if isinstance(card.get("card_values"), dict) else {}
                    if card.get("source_sha256") != entry.get("source_sha256"):
                        entry_failures.append({"category": "card_source_sha256_mismatch"})
                    card_type = str(card.get("card_type", ""))
                    if card_type == "minimal_public_certified_menu_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "card_source_label_not_bound"})
                        if not values.get("coordinate_alpha_matches_recomputed"):
                            entry_failures.append({"category": "card_coordinate_alpha_not_recomputed"})
                        raw_members = values.get("raw_policy_pool_members", []) if isinstance(values.get("raw_policy_pool_members"), list) else []
                        certified = values.get("certified_members", []) if isinstance(values.get("certified_members"), list) else []
                        if not certified:
                            entry_failures.append({"category": "card_missing_certified_members"})
                        if int(values.get("raw_policy_pool_count", -1)) != len(raw_members):
                            entry_failures.append({"category": "card_raw_pool_count_mismatch"})
                        if certified and not set(certified).issubset(set(raw_members)):
                            entry_failures.append({"category": "card_certified_members_not_subset_raw_pool"})
                        thresholds = values.get("sla_thresholds", {}) if isinstance(values.get("sla_thresholds"), dict) else {}
                        bound = values.get("representative_bound_row", {}) if isinstance(values.get("representative_bound_row"), dict) else {}
                        if bound and thresholds and not (float(bound.get("UCB_P", 999)) <= float(thresholds.get("privacy_tau_P", -1)) and float(bound.get("UCB_T_ms", 999999)) <= float(thresholds.get("latency_tau_T_ms", -1)) and float(bound.get("UCB_B_kb", 999)) <= float(thresholds.get("bandwidth_tau_B_kb", -1))):
                            entry_failures.append({"category": "card_representative_bounds_exceed_thresholds"})
                    elif card_type == "routing_signature_manifest_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "signature_card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "signature_card_source_label_not_bound"})
                        raw_m = int(values.get("raw_policy_pool_count", 0))
                        meff = int(values.get("effective_multiplicity", 0))
                        classes = values.get("quotient_class_labels", []) if isinstance(values.get("quotient_class_labels"), list) else []
                        representatives = values.get("representatives", []) if isinstance(values.get("representatives"), list) else []
                        if not (raw_m > meff > 0):
                            entry_failures.append({"category": "signature_card_multiplicity_not_reduced", "raw_m": raw_m, "m_eff": meff})
                        if meff != len(classes) or meff != len(representatives):
                            entry_failures.append({"category": "signature_card_meff_binding_mismatch", "m_eff": meff, "classes": classes, "representatives": representatives})
                        if values.get("exact_equivalence_card") is not True or abs(float(values.get("transfer_margin_delta", 999))) > 1e-12:
                            entry_failures.append({"category": "signature_card_transfer_margin_not_exact_zero", "transfer_margin_delta": values.get("transfer_margin_delta")})
                        if not values.get("hash_role_guard") or not values.get("certified_a_handoff_guard"):
                            entry_failures.append({"category": "signature_card_guard_text_missing"})
                    elif card_type == "congestion_eq_accountant_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "congeq_card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "congeq_card_source_label_not_bound"})
                        if abs(float(values.get("stage_epsilon_1", -1)) - 0.010) > 1e-12 or abs(float(values.get("stage_epsilon_2", -1)) - 0.008) > 1e-12:
                            entry_failures.append({"category": "congeq_stage_caps_not_expected", "eps1": values.get("stage_epsilon_1"), "eps2": values.get("stage_epsilon_2")})
                        if values.get("epoch_cap_matches_recomputed") is not True or abs(float(values.get("epoch_cap", 999)) - 0.018) > 1e-12:
                            entry_failures.append({"category": "congeq_epoch_cap_not_recomputed", "epoch_cap": values.get("epoch_cap"), "recomputed": values.get("epoch_cap_recomputed")})
                        if values.get("reset_block_cap_matches_recomputed") is not True or abs(float(values.get("reset_block_cap", 999)) - 0.090) > 1e-12:
                            entry_failures.append({"category": "congeq_reset_block_not_recomputed", "reset_block_cap": values.get("reset_block_cap"), "recomputed": values.get("reset_block_cap_recomputed")})
                        if values.get("mean_waits_match_rounded_source") is not True:
                            entry_failures.append({"category": "congeq_mean_wait_sanity_not_recomputed", "declared": values.get("declared_mean_waits"), "recomputed": values.get("mean_waits_recomputed")})
                        owners = values.get("downstream_owner_boundary", []) if isinstance(values.get("downstream_owner_boundary"), list) else []
                        if not {"PSC-Q", "W-Congestion-EQ"}.issubset(set(owners)):
                            entry_failures.append({"category": "congeq_downstream_owner_boundary_missing", "owners": owners})
                    elif card_type == "pscq_mechanism_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "pscq_card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "pscq_card_source_label_not_bound"})
                        if values.get("calendar_manifest_id") != "pscq.knobs.v0.1" or values.get("calendar_family") != "renewal_uniform":
                            entry_failures.append({"category": "pscq_calendar_identity_mismatch", "manifest_id": values.get("calendar_manifest_id"), "family": values.get("calendar_family")})
                        if abs(float(values.get("delta_ms", -1)) - 2.0) > 1e-12:
                            entry_failures.append({"category": "pscq_delta_ms_not_expected", "delta_ms": values.get("delta_ms")})
                        if abs(float(values.get("slot_rate_hz_recomputed", -1)) - 500.0) > 1e-9 or abs(float(values.get("slack_floor_hz_at_rho_max_recomputed", -1)) - 100.0) > 1e-9:
                            entry_failures.append({"category": "pscq_slot_budget_not_recomputed", "slot_rate": values.get("slot_rate_hz_recomputed"), "slack_floor": values.get("slack_floor_hz_at_rho_max_recomputed")})
                        if values.get("substitution_only_guard") is not True or values.get("observer_resolution_guard") is not True:
                            entry_failures.append({"category": "pscq_mechanism_guards_missing", "substitution": values.get("substitution_only_guard"), "observer": values.get("observer_resolution_guard")})
                        if values.get("dither_composition_guard") is not True or values.get("resource_separation_guard") is not True:
                            entry_failures.append({"category": "pscq_release_guards_missing", "dither": values.get("dither_composition_guard"), "resource": values.get("resource_separation_guard")})
                    elif card_type == "wcongeq_replay_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "wcongeq_card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "wcongeq_card_source_label_not_bound"})
                        if values.get("witness_id") != "congeq.wait.twostage.v1" or values.get("mechanism_id") != "pscq.calendar.v1":
                            entry_failures.append({"category": "wcongeq_binding_identity_mismatch", "witness": values.get("witness_id"), "mechanism": values.get("mechanism_id")})
                        if values.get("accountant_profile") != "congeq.epochsum.v1" or values.get("checker_profile") != "wcongeq-checker.v1":
                            entry_failures.append({"category": "wcongeq_profile_mismatch", "accountant": values.get("accountant_profile"), "checker": values.get("checker_profile")})
                        if values.get("epoch_cap_matches_recomputed") is not True or abs(float(values.get("epoch_cap", 999)) - 0.018) > 1e-12:
                            entry_failures.append({"category": "wcongeq_epoch_cap_not_recomputed", "epoch_cap": values.get("epoch_cap"), "recomputed": values.get("epoch_cap_recomputed")})
                        if values.get("reset_cap_matches_recomputed") is not True or abs(float(values.get("reset_cap", 999)) - 0.090) > 1e-12:
                            entry_failures.append({"category": "wcongeq_reset_cap_not_recomputed", "reset_cap": values.get("reset_cap"), "recomputed": values.get("reset_cap_recomputed")})
                        if values.get("claim_cap_matches_reset_cap") is not True or abs(float(values.get("published_claim_cap", 999)) - 0.090) > 1e-12:
                            entry_failures.append({"category": "wcongeq_claim_cap_not_bound", "claim_cap": values.get("published_claim_cap")})
                        if values.get("pscq_admissibility_required") is not True:
                            entry_failures.append({"category": "wcongeq_pscq_admissibility_guard_missing"})
                        if values.get("replay_soundness_theorem_present") is not True:
                            entry_failures.append({"category": "wcongeq_replay_soundness_theorem_missing"})
                        if values.get("deployment_truth_guard_present") is not True:
                            entry_failures.append({"category": "wcongeq_deployment_truth_guard_missing"})
                    elif card_type == "calibration_recipe_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "calibration_card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "calibration_card_source_label_not_bound"})
                        if values.get("exposure_nf_id") != "enf.committee_contact.v1" or values.get("threat_window_id") != "tw.lookup.30d.v1":
                            entry_failures.append({"category": "calibration_import_tuple_mismatch", "exposure_nf_id": values.get("exposure_nf_id"), "threat_window_id": values.get("threat_window_id")})
                        if abs(float(values.get("delta", -1)) - 0.02) > 1e-12 or abs(float(values.get("eta", -1)) - 0.05) > 1e-12:
                            entry_failures.append({"category": "calibration_gap_or_error_target_mismatch", "delta": values.get("delta"), "eta": values.get("eta")})
                        if abs(float(values.get("cadence_epochs_per_day", -1)) - 1000.0) > 1e-9:
                            entry_failures.append({"category": "calibration_cadence_mismatch", "cadence": values.get("cadence_epochs_per_day")})
                        if values.get("horizon_epochs_match_recomputed") is not True or values.get("horizon_days_match_recomputed") is not True:
                            entry_failures.append({"category": "calibration_horizon_not_recomputed", "epochs": values.get("declared_horizon_epochs"), "recomputed_epochs": values.get("horizon_epochs_recomputed"), "days": values.get("declared_horizon_days"), "recomputed_days": values.get("horizon_days_recomputed")})
                        if values.get("alert_tax_bits_match_recomputed") is not True:
                            entry_failures.append({"category": "calibration_alert_tax_not_recomputed", "declared": values.get("declared_alert_tax_bits"), "recomputed": values.get("alert_tax_bits_recomputed")})
                        if values.get("calibration_card_non_substitution_guard_present") is not True or values.get("route_materialization_boundary_present") is not True:
                            entry_failures.append({"category": "calibration_route_boundary_guards_missing", "non_substitution": values.get("calibration_card_non_substitution_guard_present"), "route_boundary": values.get("route_materialization_boundary_present")})
                        route_audit = values.get("worked_route_materialization_audit", {}) if isinstance(values.get("worked_route_materialization_audit"), dict) else {}
                        route_checks = route_audit.get("checks", {}) if isinstance(route_audit.get("checks"), dict) else {}
                        expected_route_checks = {
                            "owner_map_names_calibration_recipe_packet": True,
                            "owner_map_names_eval_calibration_recipe_plan_id": True,
                            "verifier_report_materializes_calibration_recipe_packet": False,
                            "replay_plans_materialize_eval_calibration_recipe": False,
                            "support_map_materializes_calibration_recipe_bundle": False,
                        }
                        if route_audit.get("status") != "pass":
                            entry_failures.append({"category": "calibration_worked_route_materialization_audit_not_pass", "audit": route_audit})
                        for check_key, expected_value in expected_route_checks.items():
                            if route_checks.get(check_key) is not expected_value:
                                entry_failures.append({"category": "calibration_worked_route_materialization_check_mismatch", "check": check_key, "expected": expected_value, "actual": route_checks.get(check_key)})
                    elif card_type == "state_anonymity_accountant_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "state_card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "state_card_source_label_not_bound"})
                        if values.get("exposure_nf_id") != "enf-committee-contact-bucket-v2" or values.get("threat_window_id") != "tw-24h-200-lookups" or values.get("state_decl_id") != "state-routing-scores-cache-v1":
                            entry_failures.append({"category": "state_card_identity_mismatch", "exposure_nf_id": values.get("exposure_nf_id"), "tw_id": values.get("threat_window_id"), "state_decl_id": values.get("state_decl_id")})
                        if abs(float(values.get("delta", -1)) - 0.01) > 1e-12 or abs(float(values.get("temperature_tau", -1)) - 0.20) > 1e-12:
                            entry_failures.append({"category": "state_card_delta_tau_mismatch", "delta": values.get("delta"), "tau": values.get("temperature_tau")})
                        if values.get("epsilon_nat_matches_recomputed") is not True or abs(float(values.get("epsilon_nat_declared", 999)) - 0.10) > 1e-12:
                            entry_failures.append({"category": "state_card_epsilon_nat_not_recomputed", "declared": values.get("epsilon_nat_declared"), "recomputed": values.get("epsilon_nat_recomputed")})
                        if values.get("epsilon_bits_matches_recomputed") is not True or abs(float(values.get("epsilon_bits_declared", 999)) - 0.144) > 0.001:
                            entry_failures.append({"category": "state_card_epsilon_bits_not_recomputed", "declared": values.get("epsilon_bits_declared"), "recomputed": values.get("epsilon_bits_recomputed")})
                        if int(values.get("horizon_epochs", -1)) != 16 or values.get("horizon_bits_matches_recomputed") is not True or abs(float(values.get("horizon_bits_declared", 999)) - 2.31) > 0.02:
                            entry_failures.append({"category": "state_card_horizon_not_recomputed", "epochs": values.get("horizon_epochs"), "declared": values.get("horizon_bits_declared"), "recomputed": values.get("horizon_bits_recomputed")})
                        if values.get("per_epoch_odds_matches_recomputed") is not True or abs(float(values.get("per_epoch_odds_declared", 999)) - 1.105) > 0.002:
                            entry_failures.append({"category": "state_card_odds_not_recomputed", "declared": values.get("per_epoch_odds_declared"), "recomputed": values.get("per_epoch_odds_recomputed")})
                        if values.get("unit_conversion_guard_present") is not True:
                            entry_failures.append({"category": "state_card_unit_conversion_guard_missing"})
                        hostile = values.get("hostile_review", {}) if isinstance(values.get("hostile_review"), dict) else {}
                        hostile_source = "card"
                        if not hostile:
                            overlay_row = hostile_overlay_entry(hostile_overlay, str(entry.get("source_tex", "")))
                            if isinstance(overlay_row, dict):
                                hostile = overlay_row.get("hostile_review", {}) if isinstance(overlay_row.get("hostile_review"), dict) else {}
                                hostile_source = "hostile_review_overlay"
                                if overlay_row.get("source_sha256") != entry.get("source_sha256"):
                                    entry_failures.append({"category": "state_hostile_overlay_source_hash_mismatch", "overlay": overlay_row.get("source_sha256"), "entry": entry.get("source_sha256")})
                            else:
                                entry_failures.append({"category": "state_hostile_overlay_entry_missing", "source_tex": entry.get("source_tex"), "overlay_path": HOSTILE_REVIEW_OVERLAY})
                        if hostile_source == "hostile_review_overlay" and hostile_overlay_problems:
                            entry_failures.append({"category": "state_hostile_overlay_invalid", "problems": hostile_overlay_problems})
                        ok, hostile_detail = hostile_vectors_pass(hostile, minimum_count=3)
                        if not ok:
                            entry_failures.append({"category": "state_hostile_vectors_not_pass", "source": hostile_source, **hostile_detail})
                    elif card_type == "mucc_contact_floor_card":
                        if values.get("extraction_status") != "pass" or values.get("extraction_failures"):
                            entry_failures.append({"category": "mucc_card_extraction_not_pass", "failures": values.get("extraction_failures", [])[:10]})
                        if not values.get("source_span", {}).get("label_present"):
                            entry_failures.append({"category": "mucc_card_source_label_not_bound"})
                        if values.get("exposure_nf_id") != "enf.committee_contact.v1" or values.get("threat_window_id") != "tw.lookup.30d.v1":
                            entry_failures.append({"category": "mucc_card_identity_mismatch", "exposure_nf_id": values.get("exposure_nf_id"), "tw_id": values.get("threat_window_id")})
                        if int(values.get("committee_universe_M", -1)) != 256 or int(values.get("destination_replication_d", -1)) != 8 or int(values.get("live_threshold_t", -1)) != 4:
                            entry_failures.append({"category": "mucc_card_tuple_mismatch", "M": values.get("committee_universe_M"), "d": values.get("destination_replication_d"), "t": values.get("live_threshold_t")})
                        if abs(float(values.get("alpha", -1)) - 0.8) > 1e-12 or abs(float(values.get("beta", -1)) - 0.05) > 1e-12:
                            entry_failures.append({"category": "mucc_card_alpha_beta_mismatch", "alpha": values.get("alpha"), "beta": values.get("beta")})
                        if values.get("p_floor_matches_recomputed") is not True or abs(float(values.get("p_floor_declared", 999)) - 0.59375) > 1e-12:
                            entry_failures.append({"category": "mucc_p_floor_not_recomputed", "declared": values.get("p_floor_declared"), "recomputed": values.get("p_floor_recomputed")})
                        if values.get("expected_contact_floor_matches_recomputed") is not True or abs(float(values.get("expected_contact_floor_declared", 999)) - 152.0) > 1e-12:
                            entry_failures.append({"category": "mucc_contact_floor_not_recomputed", "declared": values.get("expected_contact_floor_declared"), "recomputed": values.get("expected_contact_floor_recomputed")})
                        if values.get("underbudget_drill_present") is not True:
                            entry_failures.append({"category": "mucc_underbudget_drill_missing", "rounds": values.get("public_rounds"), "total": values.get("underbudget_total_contacts")})
                        if values.get("exact_or_upper_yield_guard_present") is not True or values.get("lower_bound_non_theorem_guard_present") is not True or values.get("live_factor_non_substitution_guard_present") is not True:
                            entry_failures.append({"category": "mucc_live_factor_guards_missing", "exact_upper": values.get("exact_or_upper_yield_guard_present"), "lower_bound": values.get("lower_bound_non_theorem_guard_present"), "live_factor": values.get("live_factor_non_substitution_guard_present")})
                        if values.get("fixed_stop_guard_present") is not True:
                            entry_failures.append({"category": "mucc_fixed_stop_guard_missing"})
                        hostile = values.get("hostile_review", {}) if isinstance(values.get("hostile_review"), dict) else {}
                        expected_ids = {
                            "beta_instead_of_one_minus_beta",
                            "drop_alpha_denominator",
                            "multiply_by_alpha_instead_of_dividing",
                            "round_down_expected_contact_floor",
                            "underbudget_three_round_schedule",
                            "universal_floor_as_success_certificate",
                            "optimistic_joint_model_as_mucc_marginal_certificate",
                            "independent_liveness_as_correlation_robust_certificate",
                            "one_sided_marginal_ceiling_as_approx_mucc",
                            "two_sided_radius_without_factor_two",
                            "lower_bound_liveness_as_theorem_evidence",
                            "upper_yield_alpha_as_sufficiency_input",
                            "live_yield_alpha_vs_lookup_concurrency_alpha",
                            "outer_d_t_as_inner_n_h_alpha_calibration",
                            "key_independence_as_mucc_label_uniformity",
                            "exact_mucc_as_joint_contact_privacy",
                        }
                        if values.get("sharp_sufficiency_ladder_present") is not True or values.get("alpha_direction_non_substitution_guard_present") is not True:
                            entry_failures.append({"category": "mucc_sufficiency_ladder_guards_missing", "sharp_ladder": values.get("sharp_sufficiency_ladder_present"), "alpha_direction": values.get("alpha_direction_non_substitution_guard_present")})
                        if values.get("nested_quorum_parameter_guard_present") is not True or values.get("key_independence_label_uniformity_guard_present") is not True or values.get("joint_contact_privacy_nonclaim_guard_present") is not True or values.get("phantom_churn_table_pointer_removed") is not True:
                            entry_failures.append({
                                "category": "mucc_nested_quorum_label_symmetry_or_joint_privacy_guard_missing",
                                "nested_quorum": values.get("nested_quorum_parameter_guard_present"),
                                "label_uniformity": values.get("key_independence_label_uniformity_guard_present"),
                                "joint_privacy_nonclaim": values.get("joint_contact_privacy_nonclaim_guard_present"),
                                "phantom_pointer_removed": values.get("phantom_churn_table_pointer_removed"),
                            })
                        try:
                            inner_tuple = (
                                int(values.get("inner_committee_members_n", -1)),
                                int(values.get("inner_quorum_h", -1)),
                                float(values.get("inner_member_reachability_q", -1.0)),
                                float(values.get("inner_common_outage_rho", -1.0)),
                            )
                            inner_alpha = float(values.get("inner_alpha_lower_recomputed", -1.0))
                            forbidden_alpha = float(values.get("forbidden_outer_as_inner_alpha", -1.0))
                            alpha_overstatement = float(values.get("nested_quorum_alpha_overstatement", -1.0))
                            alpha_ratio = float(values.get("nested_quorum_alpha_overstatement_ratio", -1.0))
                        except Exception:
                            inner_tuple = (-1, -1, -1.0, -1.0)
                            inner_alpha = forbidden_alpha = alpha_overstatement = alpha_ratio = -1.0
                        if (
                            inner_tuple != (16, 11, 0.6, 0.0)
                            or abs(inner_alpha - 0.3288404125089791) > 1e-12
                            or abs(forbidden_alpha - 0.8263296) > 1e-12
                            or abs(alpha_overstatement - (0.8263296 - 0.3288404125089791)) > 1e-12
                            or abs(alpha_ratio - (0.8263296 / 0.3288404125089791)) > 1e-12
                            or forbidden_alpha <= inner_alpha
                        ):
                            entry_failures.append({
                                "category": "mucc_nested_quorum_collision_drill_mismatch",
                                "inner_tuple": inner_tuple,
                                "inner_alpha": inner_alpha,
                                "forbidden_outer_as_inner_alpha": forbidden_alpha,
                                "overstatement": alpha_overstatement,
                                "ratio": alpha_ratio,
                            })
                        try:
                            full_leakage_values = (
                                int(values.get("perfect_leakage_fixed_contact_count", -1)),
                                float(values.get("perfect_leakage_contact_marginal", -1.0)),
                                int(values.get("perfect_leakage_support_intersection_size", -1)),
                                float(values.get("perfect_leakage_total_variation_distance", -1.0)),
                                float(values.get("perfect_leakage_bayes_recovery", -1.0)),
                                float(values.get("perfect_leakage_mutual_information_bits", -1.0)),
                                float(values.get("perfect_leakage_success_probability_D0", -1.0)),
                                float(values.get("perfect_leakage_success_probability_D1", -1.0)),
                            )
                        except Exception:
                            full_leakage_values = (-1, -1.0, -1, -1.0, -1.0, -1.0, -1.0, -1.0)
                        if (
                            full_leakage_values[0] != 250
                            or abs(full_leakage_values[1] - 250.0 / 256.0) > 1e-12
                            or full_leakage_values[2] != 0
                            or abs(full_leakage_values[3] - 1.0) > 1e-12
                            or abs(full_leakage_values[4] - 1.0) > 1e-12
                            or abs(full_leakage_values[5] - 1.0) > 1e-12
                            or abs(full_leakage_values[6] - 0.9628928) > 1e-12
                            or abs(full_leakage_values[7] - 0.9628032) > 1e-12
                        ):
                            entry_failures.append({"category": "mucc_perfect_leakage_counterexample_mismatch", "observed": full_leakage_values})
                        if int(values.get("iid_binomial_minimum_integer_contacts_for_success", -1)) != 228 or int(values.get("thinned_hypergeom_minimum_integer_contacts_for_success", -1)) != 228:
                            entry_failures.append({"category": "mucc_optimistic_sufficiency_threshold_mismatch", "iid": values.get("iid_binomial_minimum_integer_contacts_for_success"), "fixed_size": values.get("thinned_hypergeom_minimum_integer_contacts_for_success")})
                        if int(values.get("mucc_marginal_independent_minimum_integer_contacts_for_success", -1)) != 250 or int(values.get("mucc_marginal_independent_predecessor_contacts", -1)) != 249:
                            entry_failures.append({"category": "mucc_robust_sufficiency_threshold_mismatch", "minimum": values.get("mucc_marginal_independent_minimum_integer_contacts_for_success"), "predecessor": values.get("mucc_marginal_independent_predecessor_contacts")})
                        if abs(float(values.get("mean_only_liveness_success_lower_bound_at_full_contact", -1)) - 0.68) > 1e-12 or int(values.get("mean_only_liveness_required_contacts_unclipped", -1)) != 310 or values.get("mean_only_liveness_target_certifiable_within_M") is not False:
                            entry_failures.append({"category": "mucc_mean_only_noncertificate_mismatch", "full_contact_bound": values.get("mean_only_liveness_success_lower_bound_at_full_contact"), "required_contacts": values.get("mean_only_liveness_required_contacts_unclipped"), "certifiable": values.get("mean_only_liveness_target_certifiable_within_M")})
                        ok, hostile_detail = hostile_vectors_pass(hostile, minimum_count=16, expected_ids=expected_ids)
                        if not ok:
                            entry_failures.append({"category": "mucc_card_hostile_vectors_not_pass", **hostile_detail})
                    elif card_type == "source_bound_static_preflight_card":
                        if values.get("source_bound") is not True:
                            entry_failures.append({"category": "generic_card_not_source_bound"})
                        if values.get("source_sha256") != entry.get("source_sha256"):
                            entry_failures.append({"category": "generic_card_source_sha256_mismatch"})
                    else:
                        entry_failures.append({"category": "unknown_card_type", "card_type": card_type})

            preflight_rel = next((row.get("path") for row in manifest.get("pack_paths", []) if isinstance(row, dict) and row.get("role") == "release_preflight_static_report"), "")
            if preflight_rel:
                preflight_path = rel_inside(root, str(preflight_rel))
                if preflight_path and preflight_path.exists():
                    preflight = load_json(preflight_path)
                    if preflight.get("status") != "pass" or preflight.get("problems"):
                        entry_failures.append({"category": "preflight_static_not_pass", "status": preflight.get("status"), "problems": preflight.get("problems")})
                    if preflight.get("details", {}).get("source_sha256") != entry.get("source_sha256"):
                        entry_failures.append({"category": "preflight_source_sha256_mismatch"})

        entry_report = {
            "evidence_pack_id": entry.get("evidence_pack_id"),
            "source_tex": entry.get("source_tex"),
            "source_sha256": entry.get("source_sha256"),
            "manifest": manifest_rel,
            "status": "pass" if not entry_failures else "fail",
            "failure_count": len(entry_failures),
            "failures": entry_failures,
        }
        entry_reports.append(entry_report)
        failures.extend({"entry": entry.get("evidence_pack_id"), **failure} for failure in entry_failures)

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "registry_present": True,
        "registry_path": "release_queue/EVIDENCE_PACK_REGISTRY.json",
        "entries": entry_reports,
        "summary": {
            "registry_entry_count": len(registry.get("entries", [])),
            "attached_entry_count": sum(1 for row in registry.get("entries", []) if row.get("status") == "attached_non_public_freeze_evidence"),
            "unregistered_pack_dir_count": len(unregistered),
            "checks_failed": len(failures),
        },
        "failures": failures[:50],
        "fail_closed_rule": "If evidence-pack integrity fails, the evidence gate is unresolved and publication remains blocked.",
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
