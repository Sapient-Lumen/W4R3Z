#!/usr/bin/env python3
"""Build the non-public evidence pack for the dry-run next release target.

This does not publish anything.  It materializes a small, source-bound evidence
pack for the release-readiness recommendation so the freeze plan can distinguish
"evidence gate unresolved" from "evidence pack attached, still awaiting the
explicit publication decision".
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import re
import subprocess
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_release_readiness as rr  # noqa: E402

PREFIX = "Anonymity: "


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze_date_from_manifest(release_manifest: dict[str, Any]) -> str:
    parts = str(release_manifest.get("timestamp", "YYYY.MM.DD")).split(".")
    return ".".join(parts[:3]) if len(parts) >= 3 else "YYYY.MM.DD"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"^anonymity:\s*", "", text)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "release-target"


def extract_between(text: str, start: str, end: str) -> str:
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find(end, i)
    if j < 0:
        return text[i:]
    return text[i:j]


def extract_card_values(text: str) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    label = r"\label{tab:minimal-certified-menu-card}"
    label_idx = text.find(label)
    if label_idx < 0:
        failures.append({"category": "table_label_missing", "label": "tab:minimal-certified-menu-card"})
        table = text
        table_start = 0
        table_end = min(len(text), 4000)
    else:
        begin_idx = text.rfind(r"\begin{table}", 0, label_idx)
        end_idx = text.find(r"\end{table}", label_idx)
        if begin_idx < 0:
            failures.append({"category": "table_begin_missing_before_label"})
            begin_idx = max(0, label_idx - 2500)
        if end_idx < 0:
            failures.append({"category": "table_end_missing_after_label"})
            end_idx = min(len(text), label_idx + 2500)
        else:
            end_idx += len(r"\end{table}")
        table_start, table_end = begin_idx, end_idx
        table = text[table_start:table_end]

    def first(pattern: str, name: str) -> str:
        m = re.search(pattern, table, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_int(value: str, name: str) -> int:
        try:
            return int(value)
        except Exception:
            failures.append({"category": "integer_parse_failed", "field": name, "value": value})
            return 0

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    witness = first(r"\\texttt\{([^{}]+)\}", "witness_interface_version")
    raw_m = as_int(first(r"\$M\s*=\s*(\d+)", "raw_policy_pool_count"), "raw_policy_pool_count")
    alpha = as_float(first(r"\\alpha\s*=\s*([0-9.]+)", "familywise_alpha"), "familywise_alpha")
    coord = as_float(first(r"\\alpha/\(3M\)\s*=\s*([0-9.]+)", "coordinate_alpha"), "coordinate_alpha")
    privacy = as_float(first(r"\\tau_P\s*=\s*([0-9.]+)", "privacy_tau_P"), "privacy_tau_P")
    latency = as_int(first(r"\\tau_T\s*=\s*(\d+)", "latency_tau_T_ms"), "latency_tau_T_ms")
    bandwidth = as_float(first(r"\\tau_B\s*=\s*([0-9.]+)", "bandwidth_tau_B_kb"), "bandwidth_tau_B_kb")
    members_raw = first(r"\\widehat\\Pi\s*=\s*\\\{([^{}]+)\\\}", "certified_members")
    members = [m.strip().replace("\\", "") for m in members_raw.split(",") if m.strip()]
    ucb_p = as_float(first(r"UCB\}_P\s*=\s*([0-9.]+)", "UCB_P"), "UCB_P")
    ucb_t = as_int(first(r"UCB\}_T\s*=\s*(\d+)", "UCB_T_ms"), "UCB_T_ms")
    ucb_b = as_float(first(r"UCB\}_B\s*=\s*([0-9.]+)", "UCB_B_kb"), "UCB_B_kb")
    arithmetic = alpha / (3 * raw_m) if raw_m else 0.0
    raw_members = [f"pi_{i}" for i in range(1, raw_m + 1)] if raw_m else []
    if raw_m and len(raw_members) != raw_m:
        failures.append({"category": "raw_member_count_mismatch"})
    if members and not set(members).issubset(set(raw_members)):
        failures.append({"category": "certified_members_not_subset_of_raw_pool", "members": members, "raw_members": raw_members})
    if members and "pi_4" not in members:
        failures.append({"category": "representative_policy_not_certified", "policy": "pi_4", "members": members})
    coordinate_matches = abs(coord - arithmetic) < 1e-12
    if not coordinate_matches:
        failures.append({"category": "coordinate_alpha_not_recomputed", "coordinate_alpha": coord, "recomputed": arithmetic})
    if not (ucb_p <= privacy and ucb_t <= latency and ucb_b <= bandwidth):
        failures.append({"category": "representative_ucb_exceeds_threshold", "ucb": [ucb_p, ucb_t, ucb_b], "thresholds": [privacy, latency, bandwidth]})

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {
            "table_label": "tab:minimal-certified-menu-card",
            "label_present": label_idx >= 0,
            "table_start_offset": table_start,
            "table_end_offset": table_end,
        },
        "witness_interface_version": witness,
        "witness_description": "committee-contact-count bucket",
        "raw_policy_pool_count": raw_m,
        "raw_policy_pool_members": raw_members,
        "familywise_alpha": alpha,
        "coordinate_alpha": coord,
        "coordinate_alpha_recomputed": arithmetic,
        "coordinate_alpha_matches_recomputed": coordinate_matches,
        "sla_thresholds": {
            "privacy_tau_P": privacy,
            "latency_tau_T_ms": latency,
            "bandwidth_tau_B_kb": bandwidth,
        },
        "certified_members": members,
        "representative_bound_row": {
            "policy": "pi_4",
            "UCB_P": ucb_p,
            "UCB_T_ms": ucb_t,
            "UCB_B_kb": ucb_b,
        },
        "switchability_claim": "Any later switch among certified_members remains inside the same certified menu contract while the menu-owned rows are unchanged.",
        "downstream_owner_boundary": ["Certified B", "Certified C", "Eval 1", "ABOM/OINL", "Release A"],
    }



def extract_signature_manifest_values(text: str) -> dict[str, Any]:
    """Extract the minimal routing-signature manifest card from Certified B.

    The release risk for this paper is not generic source binding; it is whether
    the public card actually exposes the quotient, M_eff, and exact/transfer
    margin rows that make compression safe.  This extractor turns that table
    into machine-checkable release evidence.
    """
    failures: list[dict[str, Any]] = []
    label = r"\label{tab:minimal-signature-manifest-card}"
    label_idx = text.find(label)
    if label_idx < 0:
        failures.append({"category": "table_label_missing", "label": "tab:minimal-signature-manifest-card"})
        table_start = 0
        table_end = min(len(text), 5000)
        table = text[table_start:table_end]
    else:
        begin_idx = text.rfind(r"\begin{table}", 0, label_idx)
        end_idx = text.find(r"\end{table}", label_idx)
        if begin_idx < 0:
            failures.append({"category": "table_begin_missing_before_label"})
            begin_idx = max(0, label_idx - 3000)
        if end_idx < 0:
            failures.append({"category": "table_end_missing_after_label"})
            end_idx = min(len(text), label_idx + 3000)
        else:
            end_idx += len(r"\end{table}")
        table_start, table_end = begin_idx, end_idx
        table = text[table_start:table_end]

    def first(pattern: str, name: str) -> str:
        m = re.search(pattern, table, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_int(value: str, name: str) -> int:
        try:
            return int(value)
        except Exception:
            failures.append({"category": "integer_parse_failed", "field": name, "value": value})
            return 0

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    projection = first(r"Transcript projection\s*&\s*(.*?)\\\\", "transcript_projection")
    contexts = first(r"Contexts\s*&\s*(.*?)\\\\", "contexts")
    merge_tolerance = first(r"Merge tolerance\s*&\s*(.*?)\\\\", "merge_tolerance")
    transfer_margin_raw = first(r"Transfer margin\s*&\s*\$\\Delta\s*=\s*([0-9.]+)", "transfer_margin_delta")
    quotient = first(r"Quotient map\s*&\s*(.*?)\\\\", "quotient_map")
    representatives_raw = first(r"Representatives\s*&\s*(.*?)\\\\", "representatives")
    raw_m = as_int(first(r"raw\s*\$M\s*=\s*(\d+)", "raw_policy_pool_count"), "raw_policy_pool_count")
    meff = as_int(first(r"M_\{\\mathrm\{eff\}\}\s*=\s*(\d+)", "effective_multiplicity"), "effective_multiplicity")
    transfer_margin = as_float(transfer_margin_raw, "transfer_margin_delta") if transfer_margin_raw else 0.0
    classes = sorted(set(re.findall(r"\\mapsto\s*s_([A-Za-z0-9]+)", quotient)))
    reps = [m.group(1) if m.group(1) else m.group(2) for m in re.finditer(r"\\pi_(?:\{(\d+)\}|(\d+))", representatives_raw)]
    representatives = [f"pi_{r}" for r in reps]
    exact = "exact" in merge_tolerance.lower() and abs(transfer_margin) < 1e-15
    if raw_m <= meff:
        failures.append({"category": "compression_not_reducing_multiplicity", "raw_m": raw_m, "m_eff": meff})
    if meff != len(classes):
        failures.append({"category": "meff_class_count_mismatch", "m_eff": meff, "class_count": len(classes), "classes": classes})
    if meff != len(representatives):
        failures.append({"category": "meff_representative_count_mismatch", "m_eff": meff, "representatives": representatives})
    if "hashes are audit pointers only" not in table:
        failures.append({"category": "hash_role_guard_missing"})
    if "exact-equivalence or transfer-margin rows pass" not in table:
        failures.append({"category": "certified_a_handoff_guard_missing"})
    if not exact:
        failures.append({"category": "non_exact_card_requires_manual_margin_review", "merge_tolerance": merge_tolerance, "transfer_margin": transfer_margin})

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {
            "table_label": "tab:minimal-signature-manifest-card",
            "label_present": label_idx >= 0,
            "table_start_offset": table_start,
            "table_end_offset": table_end,
        },
        "transcript_projection": re.sub(r"\\[a-zA-Z]+\{([^{}]+)\}", r"\1", projection).strip(),
        "contexts": contexts.strip(),
        "merge_tolerance": merge_tolerance.strip(),
        "transfer_margin_delta": transfer_margin,
        "exact_equivalence_card": exact,
        "quotient_class_labels": classes,
        "quotient_map_tex": quotient.strip(),
        "representatives": representatives,
        "raw_policy_pool_count": raw_m,
        "effective_multiplicity": meff,
        "compression_ratio_raw_over_effective": (raw_m / meff) if meff else 0.0,
        "certified_a_handoff_guard": "replace raw multiplicity only after exact-equivalence or transfer-margin rows pass",
        "hash_role_guard": "signature hashes are audit pointers, not proof evidence by themselves",
    }


def _extract_labeled_table(text: str, label: str, window: int = 3500) -> tuple[str, int, int, list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    label_literal = rf"\label{{{label}}}"
    label_idx = text.find(label_literal)
    if label_idx < 0:
        failures.append({"category": "table_label_missing", "label": label})
        return text[: min(len(text), window)], 0, min(len(text), window), failures
    begin_idx = text.rfind(r"\begin{table}", 0, label_idx)
    end_idx = text.find(r"\end{table}", label_idx)
    if begin_idx < 0:
        failures.append({"category": "table_begin_missing_before_label", "label": label})
        begin_idx = max(0, label_idx - window)
    if end_idx < 0:
        failures.append({"category": "table_end_missing_after_label", "label": label})
        end_idx = min(len(text), label_idx + window)
    else:
        end_idx += len(r"\end{table}")
    return text[begin_idx:end_idx], begin_idx, end_idx, failures


def extract_congestion_eq_values(text: str) -> dict[str, Any]:
    """Extract Congestion-EQ's theorem/accountant public card.

    This is the congestion-family prerequisite for later mechanism and replay
    papers.  The extractor checks the declared load envelope, per-stage TV
    accounting, reset horizon, and the tiny M/M/1 sanity drill so a release bill
    can bind a public claim to concrete source rows rather than prose alone.
    """
    table, table_start, table_end, failures = _extract_labeled_table(text, "tab:minimal-congeq-card")

    def first(pattern: str, name: str, haystack: str = table) -> str:
        m = re.search(pattern, haystack, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    def as_int(value: str, name: str) -> int:
        try:
            return int(value)
        except Exception:
            failures.append({"category": "integer_parse_failed", "field": name, "value": value})
            return 0

    rho = re.search(r"\\rho\\in\[([0-9.]+),([0-9.]+)\]", table)
    if rho:
        rho_min = as_float(rho.group(1), "rho_min")
        rho_max = as_float(rho.group(2), "rho_max")
    else:
        failures.append({"category": "field_not_extracted", "field": "rho_interval"})
        rho_min = rho_max = 0.0
    eps1 = as_float(first(r"\\eps_1\s*=\s*([0-9.]+)", "stage_epsilon_1"), "stage_epsilon_1")
    eps2 = as_float(first(r"\\eps_2\s*=\s*([0-9.]+)", "stage_epsilon_2"), "stage_epsilon_2")
    epoch_cap = as_float(first(r"\\eps_\{\\mathrm\{epoch\}\}\s*\\le\s*([0-9.]+)", "epoch_cap"), "epoch_cap")
    reset_epochs = as_int(first(r"hard reset every \$([0-9]+)\$ public epochs", "reset_epochs"), "reset_epochs")
    reset_cap = as_float(first(r"\$5\\times\s*0\.018\s*=\s*([0-9.]+)\$", "reset_block_cap"), "reset_block_cap")
    mu = as_float(first(r"\\mu\s*=\s*([0-9.]+)", "service_rate_mu"), "service_rate_mu")
    lambdas = re.search(r"\\lambda\\in\\\{([0-9.]+),([0-9.]+)\\\}", table)
    if lambdas:
        lambda_values = [as_float(lambdas.group(1), "lambda_1"), as_float(lambdas.group(2), "lambda_2")]
    else:
        failures.append({"category": "field_not_extracted", "field": "adjacent_arrival_rates"})
        lambda_values = []
    means = re.search(r"1/\(1-0\.70\)\s*=\s*([0-9.]+).*?1/\(1-0\.72\)\s*=\s*([0-9.]+)", table, flags=re.S)
    if means:
        declared_means = [as_float(means.group(1), "mean_wait_lambda_0_70"), as_float(means.group(2), "mean_wait_lambda_0_72")]
    else:
        failures.append({"category": "field_not_extracted", "field": "declared_mean_waits"})
        declared_means = []

    recomputed_epoch_cap = eps1 + eps2
    recomputed_reset_cap = reset_epochs * recomputed_epoch_cap
    recomputed_means = [1.0 / (mu - lam) for lam in lambda_values] if mu and lambda_values else []
    epoch_matches = abs(epoch_cap - recomputed_epoch_cap) < 1e-12
    reset_matches = abs(reset_cap - recomputed_reset_cap) < 1e-12
    mean_matches = len(declared_means) == len(recomputed_means) and all(abs(round(calc, 2) - decl) < 0.005 for calc, decl in zip(recomputed_means, declared_means))
    if not epoch_matches:
        failures.append({"category": "epoch_cap_not_recomputed", "declared": epoch_cap, "recomputed": recomputed_epoch_cap})
    if not reset_matches:
        failures.append({"category": "reset_block_cap_not_recomputed", "declared": reset_cap, "recomputed": recomputed_reset_cap})
    if not mean_matches:
        failures.append({"category": "mean_wait_sanity_not_recomputed", "declared": declared_means, "recomputed": recomputed_means})
    required_owner_phrases = ["PSC-Q chooses knobs", "W-Congestion-EQ replays", "Eval~1", "Release~A"]
    missing_owner_phrases = [phrase for phrase in required_owner_phrases if phrase not in table]
    if missing_owner_phrases:
        failures.append({"category": "downstream_owner_boundary_missing", "missing_phrases": missing_owner_phrases})
    if "without silently re-owning PSC-Q knob choice" not in text:
        failures.append({"category": "claim_boundary_text_missing", "expected": "without silently re-owning PSC-Q knob choice"})

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {
            "table_label": "tab:minimal-congeq-card",
            "label_present": r"\label{tab:minimal-congeq-card}" in text,
            "table_start_offset": table_start,
            "table_end_offset": table_end,
        },
        "witness_family": "end-to-end waiting-time witness on a two-stage anonymous-DHT lookup path",
        "history_conditioned_tv_contract": True,
        "rho_min": rho_min,
        "rho_max": rho_max,
        "stage_epsilon_1": eps1,
        "stage_epsilon_2": eps2,
        "epoch_cap": epoch_cap,
        "epoch_cap_recomputed": recomputed_epoch_cap,
        "epoch_cap_matches_recomputed": epoch_matches,
        "reset_epochs": reset_epochs,
        "reset_block_cap": reset_cap,
        "reset_block_cap_recomputed": recomputed_reset_cap,
        "reset_block_cap_matches_recomputed": reset_matches,
        "service_rate_mu": mu,
        "adjacent_arrival_rates": lambda_values,
        "declared_mean_waits": declared_means,
        "mean_waits_recomputed": recomputed_means,
        "mean_waits_match_rounded_source": mean_matches,
        "downstream_owner_boundary": ["PSC-Q", "W-Congestion-EQ", "Eval 1", "Release A"],
        "claim_boundary": "Congestion-EQ declares the waiting-time witness/load-envelope/accountant packet only; PSC-Q owns mechanism knobs, W-Congestion-EQ owns replay/checker bundles, and release receipts remain later lineage surfaces.",
    }


def extract_pscq_values(text: str) -> dict[str, Any]:
    """Extract PSC-Q's local mechanism packet card.

    This card is intentionally distinct from Congestion-EQ's theorem/accountant
    root.  It pins calendar/substitution/observer-utilization semantics and the
    tiny slot-budget drill needed before a later PSC-Q release decision.
    """
    table, table_start, table_end, failures = _extract_labeled_table(text, "tab:minimal-pscq-card")

    def first(pattern: str, name: str, haystack: str = table) -> str:
        m = re.search(pattern, haystack, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    manifest_id = first(r"calendar\\_manifest\\_id\s*=\s*([a-zA-Z0-9._-]+)", "calendar_manifest_id")
    calendar_family = "renewal_uniform" if "renewal\\_uniform" in table else ""
    if not calendar_family:
        failures.append({"category": "calendar_family_missing", "expected": "renewal_uniform"})
    delta_ms = as_float(first(r"\\delta\s*=\s*([0-9.]+)", "delta_ms"), "delta_ms")
    rho = re.search(r"\\rho\s*\\in\s*\[([0-9.]+),([0-9.]+)\]", table)
    if rho:
        rho_min = as_float(rho.group(1), "rho_min")
        rho_max = as_float(rho.group(2), "rho_max")
    else:
        failures.append({"category": "field_not_extracted", "field": "rho_interval"})
        rho_min = rho_max = 0.0
    rho_max_declared = as_float(first(r"\\rho_\{\\max\}\s*=\s*([0-9.]+)", "rho_max_declared"), "rho_max_declared")
    slot_rate_hz = 1000.0 / delta_ms if delta_ms else 0.0
    slack_floor_hz = (1.0 - rho_max_declared) * slot_rate_hz if slot_rate_hz else 0.0
    slot_drill_present = "= 500" in text and "= 100" in text
    if abs(slot_rate_hz - 500.0) > 1e-9:
        failures.append({"category": "slot_rate_not_recomputed", "slot_rate_hz": slot_rate_hz})
    if abs(slack_floor_hz - 100.0) > 1e-9:
        failures.append({"category": "slack_floor_not_recomputed", "slack_floor_hz": slack_floor_hz})
    if not slot_drill_present:
        failures.append({"category": "slot_budget_drill_not_present"})
    substitution_guard = "Cover work fills only service opportunities" in table and "real work preempts cover" in table
    observer_guard = r"(1/2-\alpha)\delta" in table and r"\sigma_{\mathrm{obs}}" in table
    dither_composition_guard = (
        "product per-slot jitter" in table
        and "uncontracted Congestion-EQ TV bound" in table
        and "sequential/tensorization certificate" in table
        and "spectral tier remains unresolved" in table
        and "PSC-Q dither-spend rule" in text
    )
    resource_separation_guard = (
        "must not contend for downstream bottlenecks" in table
        and "treated as additive padding" in table
        and "not release-safe" in table
        and "admissible substitution only" in text
    )
    if not substitution_guard:
        failures.append({"category": "substitution_only_guard_missing"})
    if not observer_guard:
        failures.append({"category": "observer_resolution_guard_missing"})
    if not dither_composition_guard:
        failures.append({"category": "dither_composition_guard_missing"})
    if not resource_separation_guard:
        failures.append({"category": "resource_separation_guard_missing"})
    owner_phrases = ["Congestion-EQ owns witness/accountant semantics", "W-Congestion-EQ owns replayable checker bundles", "Release~A"]
    missing_owner_phrases = [phrase for phrase in owner_phrases if phrase not in table]
    if missing_owner_phrases:
        failures.append({"category": "owner_route_missing", "missing_phrases": missing_owner_phrases})
    alpha_match = re.search(r"\\alpha=([0-9.]+)", text)
    beta_match = re.search(r"\\beta_\{\\mathrm\{frac\}\}=([0-9.]+)", text)

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {
            "table_label": "tab:minimal-pscq-card",
            "label_present": r"\label{tab:minimal-pscq-card}" in text,
            "table_start_offset": table_start,
            "table_end_offset": table_end,
        },
        "calendar_manifest_id": manifest_id,
        "calendar_family": calendar_family,
        "delta_ms": delta_ms,
        "slot_rate_hz_recomputed": slot_rate_hz,
        "rho_min": rho_min,
        "rho_max": rho_max,
        "rho_max_declared": rho_max_declared,
        "slack_floor_hz_at_rho_max_recomputed": slack_floor_hz,
        "slot_budget_drill_present": slot_drill_present,
        "substitution_only_guard": substitution_guard,
        "observer_resolution_guard": observer_guard,
        "dither_composition_guard": dither_composition_guard,
        "resource_separation_guard": resource_separation_guard,
        "alpha": float(alpha_match.group(1)) if alpha_match else None,
        "beta_frac": float(beta_match.group(1)) if beta_match else None,
        "owner_route": ["Congestion-EQ", "PSC-Q", "W-Congestion-EQ", "Eval 1", "Operational B", "Release A"],
        "claim_boundary": "PSC-Q owns the local mechanism packet only; Congestion-EQ remains the theorem/accountant root and W-Congestion-EQ remains the replay/checker companion.",
    }




def extract_wcongeq_values(text: str) -> dict[str, Any]:
    """Extract W-Congestion-EQ's replay/checker contract card."""
    table, table_start, table_end, failures = _extract_labeled_table(text, "tab:minimal-wcongeq-card")

    def first(pattern: str, name: str, haystack: str = table) -> str:
        m = re.search(pattern, haystack, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    witness = first(r"witness\s*=\s*([a-zA-Z0-9._-]+)", "witness_id")
    mechanism = first(r"mechanism\s*=\s*([a-zA-Z0-9._-]+)", "mechanism_id")
    accountant = first(r"Accountant profile\s*&\s*\\texttt\{([^{}]+)\}", "accountant_profile")
    terms_match = re.search(r"stage terms\s*\$\(([0-9.]+),([0-9.]+)\)\$", table)
    if terms_match:
        stage_terms = [as_float(terms_match.group(1), "stage_term_1"), as_float(terms_match.group(2), "stage_term_2")]
    else:
        failures.append({"category": "field_not_extracted", "field": "stage_terms"})
        stage_terms = []
    reset_epochs = 5 if "five-epoch reset block" in table else 0
    if not reset_epochs:
        failures.append({"category": "field_not_extracted", "field": "reset_epochs"})
    epoch_match = re.search(r"=\s*([0-9.]+)\$\s*and\s*\$\\eps_\{1:5\}=5\\times\s*[0-9.]+=([0-9.]+)", table)
    if epoch_match:
        epoch_cap = as_float(epoch_match.group(1), "epoch_cap")
        reset_cap = as_float(epoch_match.group(2), "reset_cap")
    else:
        failures.append({"category": "field_not_extracted", "field": "replayed_budget_arithmetic"})
        epoch_cap = reset_cap = 0.0
    checker = first(r"checker\s*\\texttt\{([^{}]+)\}", "checker_profile")
    claim_cap = as_float(first(r"claim for this reset block is \$([0-9.]+)\$", "published_claim_cap"), "published_claim_cap")
    recomputed_epoch = sum(stage_terms) if stage_terms else 0.0
    recomputed_reset = reset_epochs * recomputed_epoch if reset_epochs else 0.0
    if abs(epoch_cap - recomputed_epoch) > 1e-12:
        failures.append({"category": "epoch_cap_not_recomputed", "declared": epoch_cap, "recomputed": recomputed_epoch})
    if abs(reset_cap - recomputed_reset) > 1e-12:
        failures.append({"category": "reset_cap_not_recomputed", "declared": reset_cap, "recomputed": recomputed_reset})
    if abs(claim_cap - reset_cap) > 1e-12:
        failures.append({"category": "claim_cap_not_bound_to_reset_cap", "claim_cap": claim_cap, "reset_cap": reset_cap})
    if "accept iff schema, signature, arithmetic, and support-bundle checks all pass" not in table:
        failures.append({"category": "accept_condition_missing"})
    required_phrases = ["PSC-Q admissibility check before replay", "cover is preemptible by real work", "does not reserve downstream capacity", r"\rho\in[0.7,0.8]", r"\rho_{\max}=0.8", "must reject this fixed checker packet"]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append({"category": "pscq_admissibility_phrase_missing", "phrase": phrase})
    replay_soundness_present = "Local replay soundness and non-substitution" in text and "deterministic replay value" in text
    deployment_truth_guard = "does not prove that the deployed service followed" in text and "not as operational anonymity evidence" in text
    if not replay_soundness_present:
        failures.append({"category": "replay_soundness_theorem_missing"})
    if not deployment_truth_guard:
        failures.append({"category": "deployment_truth_boundary_missing"})

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {"table_label": "tab:minimal-wcongeq-card", "label_present": r"\label{tab:minimal-wcongeq-card}" in text, "table_start_offset": table_start, "table_end_offset": table_end},
        "witness_id": witness,
        "mechanism_id": mechanism,
        "canonicalization_profile": "JCS/RFC8785",
        "accountant_profile": accountant,
        "stage_terms": stage_terms,
        "epoch_cap": epoch_cap,
        "epoch_cap_recomputed": recomputed_epoch,
        "epoch_cap_matches_recomputed": abs(epoch_cap - recomputed_epoch) <= 1e-12,
        "reset_epochs": reset_epochs,
        "reset_cap": reset_cap,
        "reset_cap_recomputed": recomputed_reset,
        "reset_cap_matches_recomputed": abs(reset_cap - recomputed_reset) <= 1e-12,
        "checker_profile": checker,
        "published_claim_cap": claim_cap,
        "claim_cap_matches_reset_cap": abs(claim_cap - reset_cap) <= 1e-12,
        "accept_condition": "accept iff schema, signature, arithmetic, and support-bundle checks all pass",
        "pscq_admissibility_required": True,
        "pscq_required_rows": ["cover_preemptible_by_real_work", "no_downstream_capacity_reservation", "rho_interval_0.7_0.8", "rho_max_0.8"],
        "replay_soundness_theorem_present": replay_soundness_present,
        "deployment_truth_guard_present": deployment_truth_guard,
        "claim_boundary": "W-Congestion-EQ owns deterministic replay of the declared claim object only; it does not prove deployment conformance or unmodeled-channel absence.",
    }



def _contains_literal(root: pathlib.Path, rel: str, literal: str) -> bool | None:
    """Return whether an archive-local text artifact contains a literal string.

    None means the file is absent or cannot be read.  This is intentionally a
    literal byte/text check: the Calibration Recipes release risk is whether the
    maintained worked-example artifacts actually materialize the named packet,
    not whether a generated prose surface happens to mention it.
    """
    path = path_inside(root, rel)
    if path is None or not path.exists():
        return None
    try:
        return literal in path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def calibration_worked_route_audit(root: pathlib.Path) -> dict[str, Any]:
    """Audit the maintained worked-example route boundary used by Eval 3.

    The owner-map may name ``calibration_recipe_packet`` as route metadata, but
    the current cut must not pretend that the verifier report, replay-plan
    catalog, or support-bundle map materializes that packet.  Binding this to
    the release evidence card prevents the earlier prose regression where a
    source said the packet was carried by ``example_verifier_report.json`` even
    though the artifacts said otherwise.
    """
    owner_map = "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_line_item_owner_map.json"
    verifier = "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_verifier_report.json"
    replay = "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_replay_plans.json"
    support = "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_support_bundle_map.json"
    checks = {
        "owner_map_names_calibration_recipe_packet": _contains_literal(root, owner_map, "calibration_recipe_packet"),
        "owner_map_names_eval_calibration_recipe_plan_id": _contains_literal(root, owner_map, "eval-calibration-recipe-v1"),
        "verifier_report_materializes_calibration_recipe_packet": _contains_literal(root, verifier, "calibration_recipe_packet"),
        "replay_plans_materialize_eval_calibration_recipe": _contains_literal(root, replay, "eval-calibration-recipe-v1"),
        "support_map_materializes_calibration_recipe_bundle": _contains_literal(root, support, "bundle://worked-example/calibration-recipe"),
    }
    missing = sorted(key for key, value in checks.items() if value is None)
    pass_conditions = {
        "owner_map_names_calibration_recipe_packet": True,
        "owner_map_names_eval_calibration_recipe_plan_id": True,
        "verifier_report_materializes_calibration_recipe_packet": False,
        "replay_plans_materialize_eval_calibration_recipe": False,
        "support_map_materializes_calibration_recipe_bundle": False,
    }
    mismatches = [
        {"check": key, "expected": expected, "actual": checks.get(key)}
        for key, expected in pass_conditions.items()
        if checks.get(key) is not expected
    ]
    return {
        "status": "pass" if not missing and not mismatches else "fail",
        "artifact_paths": {
            "owner_map": owner_map,
            "verifier_report": verifier,
            "replay_plans": replay,
            "support_bundle_map": support,
        },
        "checks": checks,
        "missing_checks": missing,
        "mismatches": mismatches,
        "claim_boundary": "The current cut names calibration_recipe_packet only as owner-map / series-spine metadata; it does not materialize the verifier packet, replay hook, or support bundle.",
    }


def extract_calibration_recipe_values(text: str) -> dict[str, Any]:
    """Extract Eval 3's minimal calibration-recipe card.

    The risky part of a calibration companion is arithmetic drift: a later public
    sentence can quote a horizon or alert tax as if it were theorem evidence.
    This extractor pins the imported witness tuple, cadence, gap/error inputs,
    recomputed horizon, alert-quality target, alert-tax arithmetic, and owner
    escalation boundary so the freeze evidence is about the actual public card.
    """
    import math

    table, table_start, table_end, failures = _extract_labeled_table(text, "tab:minimal-calibration-card", window=5000)

    def first(pattern: str, name: str, haystack: str = table) -> str:
        m = re.search(pattern, haystack, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    def clean_tex_identifier(value: str) -> str:
        return value.replace(r"\_", "_").replace("\\", "").strip(" `$;{}")

    exposure_nf_id = clean_tex_identifier(first(r"exposure\\_nf\\_id\s*=\s*([^;]+);", "exposure_nf_id"))
    tw_id = clean_tex_identifier(first(r"tw\\_id\s*=\s*([^;}]+)", "tw_id"))
    delta = as_float(first(r"\\Delta\s*=\s*([0-9.]+)", "delta"), "delta")
    eta = as_float(first(r"\\eta\s*=\s*([0-9.]+)", "eta"), "eta")
    cadence_match = re.search(r"([0-9]+)\^\{?([0-9]+)\}?\$?\s*epochs/day", table)
    if cadence_match:
        cadence = float(cadence_match.group(1)) ** int(cadence_match.group(2))
    else:
        failures.append({"category": "field_not_extracted", "field": "cadence_epochs_per_day"})
        cadence = 0.0
    epochs_match = re.search(r"([0-9.]+)\\times\s*10\^\{?([0-9]+)\}?\$?\s*epochs", table)
    if epochs_match:
        declared_epochs = as_float(epochs_match.group(1), "declared_epoch_mantissa") * (10 ** int(epochs_match.group(2)))
    else:
        failures.append({"category": "field_not_extracted", "field": "declared_horizon_epochs"})
        declared_epochs = 0.0
    days = as_float(first(r"about\s*\$([0-9.]+)\$\s*days", "declared_days"), "declared_days")
    alert = re.search(r"\(\\beta,\\alpha\)=\(([0-9.]+),([0-9.]+)\)", table)
    if alert:
        beta = as_float(alert.group(1), "beta")
        alpha = as_float(alert.group(2), "alpha")
    else:
        failures.append({"category": "field_not_extracted", "field": "alert_quality_target"})
        beta = alpha = 0.0
    alert_bits = as_float(first(r"approx\s*([0-9.]+)\$\s*bits", "declared_alert_tax_bits"), "declared_alert_tax_bits")

    recomputed_epochs = (2.0 * math.log2(1.0 / eta) / (delta ** 2)) if delta and eta else 0.0
    recomputed_days = recomputed_epochs / cadence if cadence else 0.0
    recomputed_alert_bits = math.log2((1.0 - beta) / alpha) if alpha and beta < 1 else 0.0
    if declared_epochs and abs(declared_epochs - recomputed_epochs) / recomputed_epochs > 0.03:
        failures.append({"category": "horizon_epochs_not_recomputed", "declared": declared_epochs, "recomputed": recomputed_epochs})
    if days and abs(days - recomputed_days) > 0.75:
        failures.append({"category": "horizon_days_not_recomputed", "declared": days, "recomputed": recomputed_days})
    if alert_bits and abs(alert_bits - recomputed_alert_bits) > 0.02:
        failures.append({"category": "alert_tax_not_recomputed", "declared": alert_bits, "recomputed": recomputed_alert_bits})
    if exposure_nf_id != "enf.committee_contact.v1" or tw_id != "tw.lookup.30d.v1":
        failures.append({"category": "imported_claim_tuple_mismatch", "exposure_nf_id": exposure_nf_id, "tw_id": tw_id})
    boundary_phrases = [
        "does not own new theorem proofs",
        "runtime conformance",
        "ABOM/OINL",
        "release-ledger lineage packaging",
        "State~1 / State~2 / State~3",
        "MC-EQ",
    ]
    missing = [phrase for phrase in boundary_phrases if phrase not in text]
    if missing:
        failures.append({"category": "calibration_owner_boundary_missing", "missing_phrases": missing})
    route_guard_phrases = [
        "Calibration-card non-substitution",
        "owner-map / series-spine route metadata only",
        "current cut does not ship a separate \\nolinkurl{calibration_recipe_packet}",
        "must not cite the absent packet as carried evidence",
    ]
    missing_route_guard_phrases = [phrase for phrase in route_guard_phrases if phrase not in text]
    if missing_route_guard_phrases:
        failures.append({"category": "calibration_route_materialization_guard_missing", "missing_phrases": missing_route_guard_phrases})

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {"table_label": "tab:minimal-calibration-card", "label_present": r"\label{tab:minimal-calibration-card}" in text, "table_start_offset": table_start, "table_end_offset": table_end},
        "exposure_nf_id": exposure_nf_id,
        "threat_window_id": tw_id,
        "witness_family": "committee-contact witness family",
        "delta": delta,
        "eta": eta,
        "cadence_epochs_per_day": cadence,
        "declared_horizon_epochs": declared_epochs,
        "horizon_epochs_recomputed": recomputed_epochs,
        "horizon_epochs_match_recomputed": bool(recomputed_epochs and declared_epochs and abs(declared_epochs - recomputed_epochs) / recomputed_epochs <= 0.03),
        "declared_horizon_days": days,
        "horizon_days_recomputed": recomputed_days,
        "horizon_days_match_recomputed": bool(days and abs(days - recomputed_days) <= 0.75),
        "alert_beta": beta,
        "alert_alpha": alpha,
        "declared_alert_tax_bits": alert_bits,
        "alert_tax_bits_recomputed": recomputed_alert_bits,
        "alert_tax_bits_match_recomputed": bool(alert_bits and abs(alert_bits - recomputed_alert_bits) <= 0.02),
        "calibration_card_non_substitution_guard_present": "Calibration-card non-substitution" in text,
        "route_materialization_boundary_present": "owner-map / series-spine route metadata only" in text and "must not cite the absent packet as carried evidence" in text,
        "escalation_pointer": ["State 1", "State 2", "State 3", "MC-EQ"],
        "outer_owner_boundary": ["Eval 1", "Operational B", "ABOM/OINL", "Release A"],
        "claim_boundary": "Calibration Recipes owns only numbers-first conversions; theorem roots, evaluator notarization, runtime conformance, and release-lineage packaging remain with imported owners.",
    }


def state_hostile_review_vectors(eps_nat: float, eps_bits: float, horizon_epochs: int) -> dict[str, Any]:
    """Machine-check break vectors for the State nat/bit boundary.

    These are intentionally adversarial arithmetic rows: they document common
    wrong transformations and verify that they would understate the published
    bit/odds budget.  They are not a substitute for external review, but they
    make the highest-risk unit mistake explicit and repeatable.
    """
    import math

    correct_horizon_bits = horizon_epochs * eps_bits
    vectors = [
        {
            "id": "copy_nat_value_as_bit_exponent",
            "wrong_rule": "Use epsilon_nat directly as epsilon_bits.",
            "wrong_epsilon_bits": eps_nat,
            "correct_epsilon_bits": eps_bits,
            "wrong_horizon_bits": horizon_epochs * eps_nat,
            "correct_horizon_bits": correct_horizon_bits,
            "wrong_per_epoch_odds": 2.0 ** eps_nat if eps_nat else 1.0,
            "correct_per_epoch_odds": 2.0 ** eps_bits if eps_bits else 1.0,
            "expected_detection": "understates the bit-unit odds exponent",
        },
        {
            "id": "multiply_by_ln2_instead_of_dividing",
            "wrong_rule": "Convert nats to bits by multiplying by ln(2).",
            "wrong_epsilon_bits": eps_nat * math.log(2.0),
            "correct_epsilon_bits": eps_bits,
            "wrong_horizon_bits": horizon_epochs * eps_nat * math.log(2.0),
            "correct_horizon_bits": correct_horizon_bits,
            "wrong_per_epoch_odds": 2.0 ** (eps_nat * math.log(2.0)) if eps_nat else 1.0,
            "correct_per_epoch_odds": 2.0 ** eps_bits if eps_bits else 1.0,
            "expected_detection": "understates the bit-unit odds exponent",
        },
        {
            "id": "zero_delta_sanity_control",
            "wrong_rule": "None; this is a sanity control for Delta=0.",
            "delta": 0.0,
            "temperature_tau": 0.20,
            "epsilon_nat": 0.0,
            "epsilon_bits": 0.0,
            "per_epoch_odds": 1.0,
            "expected_detection": "passes only when zero sensitivity gives no odds inflation",
        },
    ]
    for row in vectors:
        if row["id"] == "zero_delta_sanity_control":
            row["status"] = "pass" if row["epsilon_bits"] == 0.0 and row["per_epoch_odds"] == 1.0 else "fail"
        else:
            wrong = float(row["wrong_epsilon_bits"])
            correct = float(row["correct_epsilon_bits"])
            row["understatement_bits_per_epoch"] = correct - wrong
            row["understatement_bits_over_horizon"] = float(row["correct_horizon_bits"]) - float(row["wrong_horizon_bits"])
            row["status"] = "pass" if wrong < correct and row["understatement_bits_over_horizon"] > 0 else "fail"
    failures = [row for row in vectors if row.get("status") != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "review_class": "internal_hostile_arithmetic_vectors",
        "external_reviewer_signoff": "missing",
        "blocking_publication_until_external_review": True,
        "vectors": vectors,
        "failures": failures,
        "claim_boundary": "These vectors catch nat/bit conversion understatements; they do not certify empirical deployment state or replace external adversarial review.",
    }


def extract_state_anonymity_values(text: str) -> dict[str, Any]:
    """Extract State-Dependent Anonymity's bit-unit accountant card."""
    import math

    table, table_start, table_end, failures = _extract_labeled_table(text, "tab:minimal-state-anonymity-card", window=5000)
    plain_table = table.replace(r"\_", "_")

    def first(pattern: str, name: str, haystack: str = table) -> str:
        m = re.search(pattern, haystack, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    def as_int(value: str, name: str) -> int:
        try:
            return int(value)
        except Exception:
            failures.append({"category": "integer_parse_failed", "field": name, "value": value})
            return 0

    exposure_nf_id = first(r"exposure_nf_id\s*=\s*([a-zA-Z0-9._-]+)", "exposure_nf_id", haystack=plain_table)
    tw_id = first(r"tw_id\s*=\s*([a-zA-Z0-9._-]+)", "tw_id", haystack=plain_table)
    state_decl_id = first(r"state_decl_id\s*=\s*([a-zA-Z0-9._-]+)", "state_decl_id", haystack=plain_table)
    delta = as_float(first(r"\\Delta\s*=\s*([0-9.]+)", "delta"), "delta")
    tau = as_float(first(r"\\tau\s*=\s*([0-9.]+)", "temperature_tau"), "temperature_tau")
    eps_nat_declared = as_float(first(r"\\varepsilon_\{\\mathrm\{nat\}\}\s*=\s*2\\Delta/\\tau\s*=\s*([0-9.]+)", "epsilon_nat_declared"), "epsilon_nat_declared")
    eps_bits_declared = as_float(first(r"\\varepsilon_\{\\mathrm\{bits\}\}\s*=\s*0\.10/\\ln 2\s*\\approx\s*([0-9.]+)", "epsilon_bits_declared"), "epsilon_bits_declared")
    horizon_epochs = as_int(first(r"under\s*\$([0-9]+)\$\s*epochs", "horizon_epochs"), "horizon_epochs")
    horizon_bits_declared = as_float(first(r"=\s*([0-9.]+)\$\s*bits by basic composition", "horizon_bits_declared"), "horizon_bits_declared")
    per_epoch_odds_declared = as_float(first(r"2\^\{0\.144\}\s*\\approx\s*([0-9.]+)", "per_epoch_odds_declared"), "per_epoch_odds_declared")

    eps_nat_recomputed = (2.0 * delta / tau) if tau else 0.0
    eps_bits_recomputed = (eps_nat_recomputed / math.log(2.0)) if eps_nat_recomputed else 0.0
    horizon_bits_recomputed = horizon_epochs * eps_bits_recomputed
    per_epoch_odds_recomputed = 2.0 ** eps_bits_recomputed if eps_bits_recomputed else 0.0
    nat_match = abs(eps_nat_declared - eps_nat_recomputed) <= 1e-12
    bits_match = abs(eps_bits_declared - eps_bits_recomputed) <= 0.001
    horizon_match = abs(horizon_bits_declared - horizon_bits_recomputed) <= 0.02
    odds_match = abs(per_epoch_odds_declared - per_epoch_odds_recomputed) <= 0.002
    if not nat_match:
        failures.append({"category": "epsilon_nat_not_recomputed", "declared": eps_nat_declared, "recomputed": eps_nat_recomputed})
    if not bits_match:
        failures.append({"category": "epsilon_bits_not_recomputed", "declared": eps_bits_declared, "recomputed": eps_bits_recomputed})
    if not horizon_match:
        failures.append({"category": "horizon_bits_not_recomputed", "declared": horizon_bits_declared, "recomputed": horizon_bits_recomputed})
    if not odds_match:
        failures.append({"category": "per_epoch_odds_not_recomputed", "declared": per_epoch_odds_declared, "recomputed": per_epoch_odds_recomputed})
    unit_guard = "State-card unit conversion guard" in text and "not the raw nat value" in text and "copies $0.10$ as a bit exponent" in text
    if not unit_guard:
        failures.append({"category": "state_unit_conversion_guard_missing"})

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {"table_label": "tab:minimal-state-anonymity-card", "label_present": r"\label{tab:minimal-state-anonymity-card}" in text, "table_start_offset": table_start, "table_end_offset": table_end},
        "exposure_nf_id": exposure_nf_id,
        "threat_window_id": tw_id,
        "state_decl_id": state_decl_id,
        "delta": delta,
        "temperature_tau": tau,
        "epsilon_nat_declared": eps_nat_declared,
        "epsilon_nat_recomputed": eps_nat_recomputed,
        "epsilon_nat_matches_recomputed": nat_match,
        "epsilon_bits_declared": eps_bits_declared,
        "epsilon_bits_recomputed": eps_bits_recomputed,
        "epsilon_bits_matches_recomputed": bits_match,
        "horizon_epochs": horizon_epochs,
        "horizon_bits_declared": horizon_bits_declared,
        "horizon_bits_recomputed": horizon_bits_recomputed,
        "horizon_bits_matches_recomputed": horizon_match,
        "per_epoch_odds_declared": per_epoch_odds_declared,
        "per_epoch_odds_recomputed": per_epoch_odds_recomputed,
        "per_epoch_odds_matches_recomputed": odds_match,
        "unit_conversion_guard_present": unit_guard,
        "hostile_review": state_hostile_review_vectors(eps_nat_recomputed, eps_bits_recomputed, horizon_epochs),
        "claim_boundary": "State-Dependent Anonymity exports a bit-unit control-plane stability accountant; nat-unit softmax bounds are converted before composition or odds claims.",
    }



def _binom_tail(n: int, q: float, threshold: int) -> float:
    """Return Pr[Binomial(n,q) >= threshold] with q clamped to [0,1]."""
    import math

    q = max(0.0, min(1.0, float(q)))
    if threshold <= 0:
        return 1.0
    if threshold > n:
        return 0.0
    return sum(math.comb(n, i) * (q ** i) * ((1.0 - q) ** (n - i)) for i in range(threshold, n + 1))


def _binomial_minimum_integer_contacts(M: int, d: int, t: int, alpha: float, beta: float) -> tuple[int, float]:
    """Small exact search for the first integer k whose optimistic iid tail reaches 1-beta."""
    target = 1.0 - beta
    for k in range(0, M + 1):
        tail = _binom_tail(d, (k / M) * alpha if M else 0.0, t)
        if tail + 1e-15 >= target:
            return k, tail
    return M, _binom_tail(d, alpha, t)


def _hypergeom_choose(n: int, k: int) -> int:
    import math

    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def _hypergeom_pmf(M: int, successes: int, draws: int, hits: int) -> float:
    denom = _hypergeom_choose(M, draws)
    if denom == 0:
        return 0.0
    return (_hypergeom_choose(successes, hits) * _hypergeom_choose(M - successes, draws - hits)) / denom


def _thinned_hypergeom_tail(M: int, d: int, k: int, alpha: float, threshold: int) -> float:
    """Return Pr[Binomial(H, alpha) >= threshold], H~Hypergeom(M,k,d)."""
    import math

    alpha = max(0.0, min(1.0, float(alpha)))
    total = 0.0
    for hits in range(0, min(d, k) + 1):
        hprob = _hypergeom_pmf(M, k, d, hits)
        if hprob == 0.0:
            continue
        tail = sum(math.comb(hits, live) * (alpha ** live) * ((1.0 - alpha) ** (hits - live)) for live in range(threshold, hits + 1))
        total += hprob * tail
    return total


def _thinned_hypergeom_minimum_contacts(M: int, d: int, t: int, alpha: float, beta: float) -> tuple[int, float]:
    target = 1.0 - beta
    for k in range(0, M + 1):
        tail = _thinned_hypergeom_tail(M, d, k, alpha, t)
        if tail + 1e-15 >= target:
            return k, tail
    return M, _thinned_hypergeom_tail(M, d, M, alpha, t)

def _mucc_marginal_independent_liveness_lower_bound(d: int, t: int, alpha: float, mean_destination_contacts: float) -> tuple[float, dict[str, float | int]]:
    """Sharp worst-case success bound from MUCC's mean plus independent liveness.

    If Y is the number of contacted destination committees, MUCC fixes only
    E[Y].  Under exact independent liveness, conditional success is
    g(h)=Pr[Binomial(h,alpha)>=t].  Minimizing E[g(Y)] over all distributions on
    {0,...,d} with the declared mean is a two-constraint linear program; an
    extreme optimum uses at most two support points.  Enumerating those pairs
    computes the lower convex envelope exactly for this small finite support.
    """
    mean = max(0.0, min(float(d), float(mean_destination_contacts)))
    values = [_binom_tail(h, alpha, t) for h in range(d + 1)]
    best = float('inf')
    witness: dict[str, float | int] = {"lower_support": 0, "upper_support": 0, "upper_weight": 0.0}
    tol = 1e-12
    for lo in range(d + 1):
        for hi in range(lo, d + 1):
            if lo == hi:
                if abs(mean - lo) > tol:
                    continue
                candidate = values[lo]
                weight_hi = 0.0
            else:
                if mean < lo - tol or mean > hi + tol:
                    continue
                weight_hi = (mean - lo) / (hi - lo)
                candidate = (1.0 - weight_hi) * values[lo] + weight_hi * values[hi]
            if candidate < best - tol:
                best = candidate
                witness = {"lower_support": lo, "upper_support": hi, "upper_weight": weight_hi}
    if best == float('inf'):
        raise ValueError(f"no convex-envelope witness for mean={mean} on 0..{d}")
    return best, witness


def _mucc_marginal_independent_minimum_contacts(M: int, d: int, t: int, alpha: float, beta: float) -> tuple[int, float, dict[str, float | int]]:
    target = 1.0 - beta
    for k in range(0, M + 1):
        tail, witness = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * k / M if M else 0.0)
        if tail + 1e-15 >= target:
            return k, tail, witness
    tail, witness = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, float(d))
    return M, tail, witness


def _nested_committee_alpha_lower(n: int, h: int, q: float, rho: float = 0.0) -> float:
    """Lower-bound one outer committee response from a distinct inner quorum.

    ``n`` and ``h`` are deliberately not named ``d`` and ``t``: the latter
    belong to the outer destination-replication theorem.  Keeping the layers
    separate prevents a healthy-looking outer tuple from being reused as an
    unsupported inner liveness calibration.
    """
    if n < 0 or h < 0 or h > n:
        return 0.0
    return max(0.0, min(1.0, 1.0 - float(rho))) * _binom_tail(n, float(q), h)


def _mean_only_liveness_success_lower_bound(d: int, t: int, expected_live_responses_lower: float) -> float:
    """Sharp threshold-probability lower bound from support and a mean only."""
    if t <= 0:
        return 1.0
    if t > d:
        return 0.0
    numerator = float(expected_live_responses_lower) - float(t - 1)
    denominator = float(d - t + 1)
    return max(0.0, min(1.0, numerator / denominator))


def _mean_only_required_contacts_unclipped(M: int, d: int, t: int, alpha: float, beta: float) -> int:
    """First integer expected-contact budget whose mean-only bound reaches 1-beta.

    The result is intentionally not clipped to M: a value above M is the
    machine-readable proof that the assumptions cannot certify the target.
    """
    import math

    target_mean_live = (t - 1) + (d - t + 1) * (1.0 - beta)
    if alpha <= 0.0 or d <= 0:
        return M + 1
    return math.ceil((M * target_mean_live / (alpha * d)) - 1e-12)


def _approximate_mucc_diameter_contact_floor(M: int, d: int, t: int, alpha: float, beta: float, delta: float) -> tuple[float, float, bool]:
    """Return A and the sharp marginal/mean floor under global diameter delta."""
    if alpha <= 0.0 or d <= 0:
        return float("inf"), float("inf"), False
    A = ((1.0 - beta) * t) / (alpha * d)
    if A > 1.0 + 1e-15:
        return A, float("inf"), False
    floor = d * A + max(0, M - d) * max(0.0, A - max(0.0, float(delta)))
    return A, floor, True


def _one_sided_public_counterexample(M: int, d: int, t: int, alpha: float, beta: float) -> dict[str, float]:
    """Construct the public-parameter attack on a one-sided MUCC ceiling."""
    if alpha <= 0.0 or d <= 0:
        return {
            "one_sided_p": 0.0,
            "one_sided_eta": 0.0,
            "destination_contact_marginal": 0.0,
            "nondestination_contact_marginal": 0.0,
            "success_probability": max(0.0, 1.0 - beta),
            "live_marginal": 0.0,
            "conditional_live_yield": 0.0,
            "extra_contact_probability_on_success_nonlive_destination": 0.0,
            "expected_total_contacts": 0.0,
            "wrong_Mp_cover_floor": 0.0,
            "global_marginal_diameter": 0.0,
        }
    A = ((1.0 - beta) * t) / (alpha * d)
    success = 1.0 - beta
    live_fraction_on_success = t / d
    denominator = 1.0 - live_fraction_on_success
    extra_contact_probability = 0.0 if denominator <= 0.0 else (A / success - live_fraction_on_success) / denominator
    live_marginal = success * live_fraction_on_success
    return {
        "one_sided_p": A,
        "one_sided_eta": 0.0,
        "destination_contact_marginal": A,
        "nondestination_contact_marginal": 0.0,
        "success_probability": success,
        "live_marginal": live_marginal,
        "conditional_live_yield": live_marginal / A if A > 0.0 else 0.0,
        "extra_contact_probability_on_success_nonlive_destination": extra_contact_probability,
        "expected_total_contacts": d * A,
        "wrong_Mp_cover_floor": M * A,
        "global_marginal_diameter": A,
    }


def _exact_mucc_perfect_leakage_counterexample(M: int, d: int, t: int, alpha: float) -> dict[str, Any]:
    """Enumerate the source-bound fixed-size exact-MUCC/full-leakage construction."""
    if (M, d, t) != (256, 8, 4):
        # Card selection probes every theorem-specific extractor before falling
        # back to the generic source-bound card.  A non-MUCC source therefore
        # reaches this helper with zero/default parse values.  Return an
        # explicitly inapplicable record instead of crashing the whole evidence
        # rebuild; the surrounding MUCC extractor will remain failed closed.
        return {
            "committee_universe_M": M,
            "destination_replication_d": d,
            "live_threshold_t": t,
            "independent_live_probability_alpha": alpha,
            "destination_sets": [],
            "omission_templates": [],
            "omission_size": 0,
            "fixed_contact_count": 0,
            "expected_total_contacts": 0.0,
            "contact_marginal": 0.0,
            "minimum_contact_marginal": 0.0,
            "maximum_contact_marginal": 0.0,
            "exact_mucc_marginals": False,
            "conditional_support_size_D0": 0,
            "conditional_support_size_D1": 0,
            "conditional_support_intersection_size": -1,
            "total_variation_distance": 0.0,
            "bayes_optimal_destination_recovery": None,
            "mutual_information_bits_uniform_binary_destination": None,
            "destination_contact_count_multiplicities": [],
            "success_probability_D0": 0.0,
            "success_probability_D1": 0.0,
            "applicability": "pinned_only_to_M256_d8_t4",
        }
    labels = set(range(M))
    destinations = [set(range(0, 8)), set(range(8, 16))]
    templates = [set(range(0, 6)), {0, 1, 2, 3, 4, 6}]
    supports: list[set[frozenset[int]]] = []
    success: list[float] = []
    y_multiplicities: list[dict[str, int]] = []
    min_contact_marginal = 1.0
    max_contact_marginal = 0.0

    for destination, template in zip(destinations, templates):
        contact_sets: list[frozenset[int]] = []
        contact_counts = [0] * M
        y_counts: dict[int, int] = {}
        success_sum = 0.0
        for shift in range(M):
            omitted = {(shift + value) % M for value in template}
            contacted = frozenset(labels - omitted)
            contact_sets.append(contacted)
            for committee in contacted:
                contact_counts[committee] += 1
            y = len(destination.intersection(contacted))
            y_counts[y] = y_counts.get(y, 0) + 1
            success_sum += _binom_tail(y, alpha, t)
        marginals = [count / M for count in contact_counts]
        min_contact_marginal = min(min_contact_marginal, min(marginals))
        max_contact_marginal = max(max_contact_marginal, max(marginals))
        supports.append(set(contact_sets))
        success.append(success_sum / M)
        y_multiplicities.append({str(key): value for key, value in sorted(y_counts.items())})

    support_intersection = len(supports[0].intersection(supports[1]))
    total_variation = 1.0 if support_intersection == 0 else 0.0
    return {
        "committee_universe_M": M,
        "destination_replication_d": d,
        "live_threshold_t": t,
        "independent_live_probability_alpha": alpha,
        "destination_sets": [sorted(row) for row in destinations],
        "omission_templates": [sorted(row) for row in templates],
        "omission_size": len(templates[0]),
        "fixed_contact_count": M - len(templates[0]),
        "expected_total_contacts": float(M - len(templates[0])),
        "contact_marginal": (M - len(templates[0])) / M,
        "minimum_contact_marginal": min_contact_marginal,
        "maximum_contact_marginal": max_contact_marginal,
        "exact_mucc_marginals": abs(min_contact_marginal - max_contact_marginal) <= 1e-15,
        "conditional_support_size_D0": len(supports[0]),
        "conditional_support_size_D1": len(supports[1]),
        "conditional_support_intersection_size": support_intersection,
        "total_variation_distance": total_variation,
        "bayes_optimal_destination_recovery": 1.0 if support_intersection == 0 else None,
        "mutual_information_bits_uniform_binary_destination": 1.0 if support_intersection == 0 else None,
        "destination_contact_count_multiplicities": y_multiplicities,
        "success_probability_D0": success[0],
        "success_probability_D1": success[1],
    }


def mucc_hostile_review_vectors(M: int, d: int, t: int, alpha: float, beta: float, correct_p: float, correct_k0: float, underbudget_total: int, exact_upper_guard: bool, lower_bound_guard: bool, live_factor_guard: bool, alpha_direction_guard: bool, nested_quorum_guard: bool, label_uniformity_guard: bool, joint_privacy_guard: bool, phantom_churn_table_pointer_removed: bool, inner_n: int, inner_h: int, inner_q: float, inner_rho: float) -> dict[str, Any]:
    """Machine-check break vectors for the MUCC necessity/sufficiency ladder."""
    import math

    wrong_beta_p = (beta * t / (alpha * d)) if alpha and d else 0.0
    no_alpha_k0 = (M * (1.0 - beta) * t / d) if d else 0.0
    alpha_multiplier_k0 = (M * (1.0 - beta) * t * alpha / d) if d else 0.0
    floor_round_down = math.floor(correct_k0)
    ceil_floor = math.ceil(correct_k0 - 1e-12)
    success_target = 1.0 - beta

    iid_tail_at_universal = _binom_tail(d, (ceil_floor / M) * alpha if M else 0.0, t)
    iid_min_k, iid_min_tail = _binomial_minimum_integer_contacts(M, d, t, alpha, beta)
    iid_predecessor_k = max(0, iid_min_k - 1)
    iid_predecessor_tail = _binom_tail(d, (iid_predecessor_k / M) * alpha if M else 0.0, t)

    hypergeom_tail_at_universal = _thinned_hypergeom_tail(M, d, ceil_floor, alpha, t)
    hypergeom_min_k, hypergeom_min_tail = _thinned_hypergeom_minimum_contacts(M, d, t, alpha, beta)
    hypergeom_predecessor_k = max(0, hypergeom_min_k - 1)
    hypergeom_predecessor_tail = _thinned_hypergeom_tail(M, d, hypergeom_predecessor_k, alpha, t)

    robust_tail_at_universal, robust_universal_witness = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * ceil_floor / M if M else 0.0)
    robust_tail_at_optimistic = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * iid_min_k / M if M else 0.0)[0]
    robust_min_k, robust_min_tail, robust_min_witness = _mucc_marginal_independent_minimum_contacts(M, d, t, alpha, beta)
    robust_predecessor_k = max(0, robust_min_k - 1)
    robust_predecessor_tail, robust_predecessor_witness = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * robust_predecessor_k / M if M else 0.0)

    full_contact_mean_only = _mean_only_liveness_success_lower_bound(d, t, alpha * d)
    mean_only_required = _mean_only_required_contacts_unclipped(M, d, t, alpha, beta)

    one_sided_attack = _one_sided_public_counterexample(M, d, t, alpha, beta)
    perfect_leakage_attack = _exact_mucc_perfect_leakage_counterexample(M, d, t, alpha)
    radius_eta = 0.05
    approx_A, correct_radius_floor, approx_feasible = _approximate_mucc_diameter_contact_floor(M, d, t, alpha, beta, 2.0 * radius_eta)
    _, wrong_radius_as_diameter_floor, _ = _approximate_mucc_diameter_contact_floor(M, d, t, alpha, beta, radius_eta)
    legacy_one_factor_M_eta = M * approx_A - M * radius_eta

    correct_inner_alpha = _nested_committee_alpha_lower(inner_n, inner_h, inner_q, inner_rho)
    forbidden_outer_as_inner_alpha = _nested_committee_alpha_lower(d, t, inner_q, inner_rho)
    nested_alpha_overstatement = forbidden_outer_as_inner_alpha - correct_inner_alpha
    nested_alpha_overstatement_ratio = (forbidden_outer_as_inner_alpha / correct_inner_alpha) if correct_inner_alpha > 0.0 else float("inf")

    vectors = [
        {
            "id": "beta_instead_of_one_minus_beta",
            "wrong_rule": "Use beta*t/(alpha*d) instead of (1-beta)*t/(alpha*d).",
            "wrong_p_floor": wrong_beta_p,
            "wrong_expected_contact_floor": M * wrong_beta_p,
            "correct_p_floor": correct_p,
            "correct_expected_contact_floor": correct_k0,
            "expected_detection": "wrong floor is far below the theorem floor",
        },
        {
            "id": "drop_alpha_denominator",
            "wrong_rule": "Omit the live-yield alpha denominator.",
            "wrong_expected_contact_floor": no_alpha_k0,
            "correct_expected_contact_floor": correct_k0,
            "expected_detection": "understates contact floor when alpha<1",
        },
        {
            "id": "multiply_by_alpha_instead_of_dividing",
            "wrong_rule": "Multiply by live yield alpha instead of dividing by alpha.",
            "wrong_expected_contact_floor": alpha_multiplier_k0,
            "correct_expected_contact_floor": correct_k0,
            "expected_detection": "understates contact floor when alpha<1",
        },
        {
            "id": "round_down_expected_contact_floor",
            "wrong_rule": "Round the expected-contact floor down for a release card.",
            "wrong_expected_contact_floor": floor_round_down,
            "correct_expected_contact_floor_ceiling": ceil_floor,
            "correct_expected_contact_floor": correct_k0,
            "expected_detection": "release-facing integer floor must not be rounded below the recomputed floor",
        },
        {
            "id": "underbudget_three_round_schedule",
            "wrong_rule": "Treat three rounds of 48 expected contacts as satisfying the floor.",
            "wrong_expected_total_contacts": underbudget_total,
            "correct_expected_contact_floor": correct_k0,
            "expected_detection": "144 remains below the 152-contact floor",
        },
        {
            "id": "universal_floor_as_success_certificate",
            "wrong_rule": "Treat the universal Markov expected-contact floor as sufficient for the 1-beta success target.",
            "wrong_expected_contact_floor": ceil_floor,
            "correct_expected_contact_floor": correct_k0,
            "claimed_success_floor": success_target,
            "iid_binomial_success_at_universal_floor": iid_tail_at_universal,
            "iid_binomial_predecessor_contacts": iid_predecessor_k,
            "iid_binomial_success_at_predecessor": iid_predecessor_tail,
            "iid_binomial_minimum_integer_contacts": iid_min_k,
            "iid_binomial_success_at_minimum": iid_min_tail,
            "thinned_hypergeom_success_at_universal_floor": hypergeom_tail_at_universal,
            "thinned_hypergeom_predecessor_contacts": hypergeom_predecessor_k,
            "thinned_hypergeom_success_at_predecessor": hypergeom_predecessor_tail,
            "thinned_hypergeom_minimum_integer_contacts": hypergeom_min_k,
            "thinned_hypergeom_success_at_minimum": hypergeom_min_tail,
            "mucc_marginal_independent_success_at_universal_floor": robust_tail_at_universal,
            "expected_detection": "152 is a necessary universal expectation floor, not a sufficiency certificate; every sufficiency row must name its joint-contact and liveness assumptions.",
        },
        {
            "id": "optimistic_joint_model_as_mucc_marginal_certificate",
            "wrong_rule": "Promote the iid/fixed-size k=228 threshold to a guarantee under MUCC marginals alone.",
            "wrong_expected_contact_floor": iid_min_k,
            "claimed_success_floor": success_target,
            "mucc_marginal_independent_success_lower_bound_at_wrong_floor": robust_tail_at_optimistic,
            "correct_mucc_marginal_independent_minimum_integer_contacts": robust_min_k,
            "correct_success_at_minimum": robust_min_tail,
            "predecessor_contacts": robust_predecessor_k,
            "success_at_predecessor": robust_predecessor_tail,
            "convex_envelope_witness_at_wrong_floor": robust_universal_witness if iid_min_k == ceil_floor else _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * iid_min_k / M if M else 0.0)[1],
            "convex_envelope_witness_at_minimum": robust_min_witness,
            "expected_detection": "the optimistic joint models reach 0.95 at 228, but MUCC fixes only marginals; the sharp worst-case independent-liveness threshold is 250.",
        },
        {
            "id": "independent_liveness_as_correlation_robust_certificate",
            "wrong_rule": "Use the k=250 independent-liveness threshold as though it survived arbitrary liveness dependence.",
            "wrong_expected_contact_floor": robust_min_k,
            "claimed_success_floor": success_target,
            "mean_only_success_lower_bound_at_full_contact": full_contact_mean_only,
            "mean_only_required_contacts_unclipped": mean_only_required,
            "committee_universe_M": M,
            "certificate_possible_within_committee_universe": mean_only_required <= M,
            "expected_detection": "with only a lower mean live-yield and arbitrary dependence, even full contact certifies only 0.68; the 0.95 mean-only requirement is 310 contacts, beyond M=256.",
        },
        {
            "id": "one_sided_marginal_ceiling_as_approx_mucc",
            "wrong_rule": "Treat q_j(D) <= p+eta as approximate equalization even though it supplies no lower marginal bound.",
            **one_sided_attack,
            "expected_detection": "the public parameters admit 0.95 success and exact conditional live yield 0.8 with only 4.75 expected destination contacts and zero cover contact, despite p=0.59375 and eta=0",
        },
        {
            "id": "two_sided_radius_without_factor_two",
            "wrong_rule": "Insert a two-sided center radius eta directly as the global diameter delta, omitting the triangle-inequality factor two.",
            "two_sided_center_radius_eta": radius_eta,
            "implied_diameter_bound": 2.0 * radius_eta,
            "required_destination_contact_average_A": approx_A,
            "wrong_floor_treating_radius_as_diameter": wrong_radius_as_diameter_floor,
            "legacy_one_factor_M_eta_expression": legacy_one_factor_M_eta,
            "correct_diameter_contact_floor": correct_radius_floor,
            "overstatement_contacts": wrong_radius_as_diameter_floor - correct_radius_floor,
            "diameter_floor_feasible": approx_feasible,
            "expected_detection": "a radius-0.05 card permits diameter 0.10, so the marginally sharp floor is 127.2 rather than 139.6 (or the legacy 139.2 expression)",
        },
        {
            "id": "lower_bound_liveness_as_theorem_evidence",
            "wrong_rule": "Use a lower-bound engineering liveness estimate as an exact/upper-yield impossibility row.",
            "guard_present": bool(lower_bound_guard and exact_upper_guard),
            "theorem_authorized_under_wrong_rule": False,
            "expected_detection": "a necessary impossibility floor needs exact or upper-yield evidence",
        },
        {
            "id": "upper_yield_alpha_as_sufficiency_input",
            "wrong_rule": "Use an upper-yield envelope from the necessity theorem as a lower-yield assumption for success certification.",
            "guard_present": bool(alpha_direction_guard),
            "sufficiency_authorized_under_wrong_rule": False,
            "expected_detection": "sufficiency needs exact or lower-yield evidence; a one-sided upper envelope points the wrong way",
        },
        {
            "id": "live_yield_alpha_vs_lookup_concurrency_alpha",
            "wrong_rule": "Substitute a deployed lookup-concurrency parameter named alpha for MUCC live-response yield alpha.",
            "guard_present": bool(live_factor_guard),
            "theorem_authorized_under_wrong_rule": False,
            "expected_detection": "symbol-name collision must not change the live-yield row",
        },
        {
            "id": "outer_d_t_as_inner_n_h_alpha_calibration",
            "wrong_rule": "Reuse outer destination replication/response parameters (d,t) as the inner committee size/quorum (n,h) when calibrating alpha.",
            "outer_destination_replication_d": d,
            "outer_live_threshold_t": t,
            "inner_committee_members_n": inner_n,
            "inner_quorum_h": inner_h,
            "inner_member_reachability_q": inner_q,
            "inner_common_outage_rho": inner_rho,
            "correct_inner_alpha_lower": correct_inner_alpha,
            "forbidden_outer_as_inner_alpha": forbidden_outer_as_inner_alpha,
            "alpha_overstatement": nested_alpha_overstatement,
            "alpha_overstatement_ratio": nested_alpha_overstatement_ratio,
            "guard_present": bool(nested_quorum_guard and phantom_churn_table_pointer_removed),
            "theorem_authorized_under_wrong_rule": False,
            "expected_detection": "the source-bound drill separates (d,t)=(8,4) from (n,h,q,rho)=(16,11,0.6,0); the forbidden substitution raises the lower row from about 0.32884 to 0.82633",
        },
        {
            "id": "exact_mucc_as_joint_contact_privacy",
            "wrong_rule": "Treat exact MUCC one-committee marginals, or the k0=250 success row, as joint contact-set destination privacy.",
            **perfect_leakage_attack,
            "guard_present": bool(joint_privacy_guard),
            "privacy_authorized_under_wrong_rule": False,
            "expected_detection": "the orbit-coded fixed-size scheduler has exact 250/256 MUCC marginals and success above 0.9628 for both destinations while its conditional supports are disjoint, so TV=1 and destination recovery is perfect",
        },
        {
            "id": "key_independence_as_mucc_label_uniformity",
            "wrong_rule": "Treat destination-independence of the contact-set law as committee-label-uniform MUCC without a symmetry or marginal-diameter bridge.",
            "counterexample_contact_set": [1],
            "q_fixed_committee": 1.0,
            "q_other_committee": 0.0,
            "contact_set_law_destination_independent": True,
            "mucc_committee_label_uniformity": False,
            "global_marginal_diameter": 1.0,
            "guard_present": bool(label_uniformity_guard),
            "theorem_authorized_under_wrong_rule": False,
            "expected_detection": "the deterministic key-independent mechanism C={1} has unequal committee-label marginals and therefore is not MUCC",
        },
    ]

    for row in vectors:
        row_id = row["id"]
        if row_id in {"lower_bound_liveness_as_theorem_evidence", "live_yield_alpha_vs_lookup_concurrency_alpha"}:
            row["status"] = "pass" if row.get("guard_present") is True and row.get("theorem_authorized_under_wrong_rule") is False else "fail"
        elif row_id == "outer_d_t_as_inner_n_h_alpha_calibration":
            row["status"] = "pass" if (
                row.get("guard_present") is True
                and row.get("theorem_authorized_under_wrong_rule") is False
                and inner_n != d
                and inner_h != t
                and correct_inner_alpha > 0.0
                and forbidden_outer_as_inner_alpha > correct_inner_alpha
                and nested_alpha_overstatement > 0.0
                and nested_alpha_overstatement_ratio > 1.0
            ) else "fail"
        elif row_id == "exact_mucc_as_joint_contact_privacy":
            row["status"] = "pass" if (
                row.get("guard_present") is True
                and row.get("privacy_authorized_under_wrong_rule") is False
                and row.get("exact_mucc_marginals") is True
                and int(row.get("fixed_contact_count", -1)) == 250
                and abs(float(row.get("contact_marginal", -1.0)) - 250.0 / 256.0) <= 1e-12
                and int(row.get("conditional_support_intersection_size", -1)) == 0
                and abs(float(row.get("total_variation_distance", -1.0)) - 1.0) <= 1e-12
                and abs(float(row.get("bayes_optimal_destination_recovery", -1.0)) - 1.0) <= 1e-12
                and abs(float(row.get("mutual_information_bits_uniform_binary_destination", -1.0)) - 1.0) <= 1e-12
                and float(row.get("success_probability_D0", 0.0)) > success_target
                and float(row.get("success_probability_D1", 0.0)) > success_target
            ) else "fail"
        elif row_id == "key_independence_as_mucc_label_uniformity":
            row["status"] = "pass" if (
                row.get("guard_present") is True
                and row.get("theorem_authorized_under_wrong_rule") is False
                and row.get("contact_set_law_destination_independent") is True
                and row.get("mucc_committee_label_uniformity") is False
                and abs(float(row.get("q_fixed_committee", -1.0)) - 1.0) <= 1e-12
                and abs(float(row.get("q_other_committee", -1.0))) <= 1e-12
                and abs(float(row.get("global_marginal_diameter", -1.0)) - 1.0) <= 1e-12
            ) else "fail"
        elif row_id == "upper_yield_alpha_as_sufficiency_input":
            row["status"] = "pass" if row.get("guard_present") is True and row.get("sufficiency_authorized_under_wrong_rule") is False else "fail"
        elif row_id == "round_down_expected_contact_floor":
            row["status"] = "pass" if float(row["wrong_expected_contact_floor"]) < float(row["correct_expected_contact_floor"]) and int(row["correct_expected_contact_floor_ceiling"]) == ceil_floor else "fail"
        elif row_id == "universal_floor_as_success_certificate":
            wrong = float(row.get("wrong_expected_contact_floor", 0.0))
            row["understatement_contacts_vs_iid_sufficiency_floor"] = float(iid_min_k) - wrong
            row["status"] = "pass" if (
                wrong == float(ceil_floor)
                and iid_tail_at_universal < success_target
                and hypergeom_tail_at_universal < success_target
                and robust_tail_at_universal < success_target
                and iid_predecessor_tail < success_target <= iid_min_tail
                and hypergeom_predecessor_tail < success_target <= hypergeom_min_tail
            ) else "fail"
        elif row_id == "optimistic_joint_model_as_mucc_marginal_certificate":
            row["status"] = "pass" if (
                robust_tail_at_optimistic < success_target
                and robust_min_k > iid_min_k
                and robust_predecessor_tail < success_target <= robust_min_tail
            ) else "fail"
        elif row_id == "independent_liveness_as_correlation_robust_certificate":
            row["status"] = "pass" if full_contact_mean_only < success_target and mean_only_required > M and row.get("certificate_possible_within_committee_universe") is False else "fail"
        elif row_id == "one_sided_marginal_ceiling_as_approx_mucc":
            row["status"] = "pass" if (
                abs(float(row.get("conditional_live_yield", -1.0)) - alpha) <= 1e-12
                and abs(float(row.get("success_probability", -1.0)) - success_target) <= 1e-12
                and float(row.get("expected_total_contacts", correct_k0)) < float(row.get("wrong_Mp_cover_floor", 0.0))
                and abs(float(row.get("nondestination_contact_marginal", -1.0))) <= 1e-12
            ) else "fail"
        elif row_id == "two_sided_radius_without_factor_two":
            row["status"] = "pass" if (
                approx_feasible
                and abs(float(row.get("implied_diameter_bound", -1.0)) - 2.0 * radius_eta) <= 1e-12
                and float(row.get("correct_diameter_contact_floor", float("inf"))) < float(row.get("wrong_floor_treating_radius_as_diameter", -1.0))
                and float(row.get("overstatement_contacts", 0.0)) > 0.0
            ) else "fail"
        else:
            wrong = float(row.get("wrong_expected_contact_floor", row.get("wrong_expected_total_contacts", 0.0)))
            row["understatement_contacts"] = float(correct_k0) - wrong
            row["status"] = "pass" if wrong < float(correct_k0) and row["understatement_contacts"] > 0 else "fail"

    failures = [row for row in vectors if row.get("status") != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "review_class": "internal_hostile_arithmetic_vectors",
        "external_reviewer_signoff": "missing",
        "blocking_publication_until_external_review": True,
        "vectors": vectors,
        "failures": failures,
        "claim_boundary": "MUCC is a first-moment label-equalization premise, not privacy: the pinned k0=250 orbit construction has exact MUCC, TV=1, perfect destination recovery, and success above 0.9628. The ladder separates a universal necessary floor (152), two optimistic joint-model thresholds (228), a sharp MUCC-marginal plus independent-liveness guarantee (250), and a mean-only correlated-liveness non-certificate (0.68 at full contact; 310 contacts required for a 0.95 bound). Approximate equalization must bind a global marginal diameter. Inner committee liveness uses a distinct (n,h,q,rho) tuple rather than outer (d,t), and destination-independence of the contact-set law does not supply committee-label-uniform MUCC without an explicit bridge.",
    }


def extract_mucc_contact_floor_values(text: str) -> dict[str, Any]:
    """Extract MUCC's necessity/sufficiency ladder and live-factor guards."""
    table, table_start, table_end, failures = _extract_labeled_table(text, "tab:minimal-mucc-card", window=8500)
    plain_table = table.replace(r"\_", "_")

    def first(pattern: str, name: str, haystack: str = table) -> str:
        m = re.search(pattern, haystack, flags=re.S)
        if not m:
            failures.append({"category": "field_not_extracted", "field": name, "pattern": pattern})
            return ""
        return m.group(1)

    def as_float(value: str, name: str) -> float:
        try:
            return float(value)
        except Exception:
            failures.append({"category": "float_parse_failed", "field": name, "value": value})
            return 0.0

    def as_int(value: str, name: str) -> int:
        try:
            return int(value)
        except Exception:
            failures.append({"category": "integer_parse_failed", "field": name, "value": value})
            return 0

    exposure_nf_id = first(r"exposure_nf_id\s*=\s*([^;\s}]+)", "exposure_nf_id", haystack=plain_table)
    tw_id = first(r"tw_id\s*=\s*([^;\s}]+)", "tw_id", haystack=plain_table)
    M = as_int(first(r"\$M\s*=\s*([0-9]+)\$", "committee_universe_M"), "committee_universe_M")
    d = as_int(first(r"\$d\s*=\s*([0-9]+)\$", "destination_replication_d"), "destination_replication_d")
    t = as_int(first(r"\$t\s*=\s*([0-9]+)\$", "live_threshold_t"), "live_threshold_t")
    alpha = as_float(first(r"\\alpha\s*=\s*([0-9.]+)", "alpha"), "alpha")
    beta = as_float(first(r"\\beta\s*=\s*([0-9.]+)", "beta"), "beta")
    p_declared = as_float(first(r"p\\ge\s*\(1-\\beta\)t/\(\\alpha d\)\s*=\s*([0-9.]+)", "declared_p_floor"), "declared_p_floor")
    k0_declared = as_int(first(r"k_0\s*=\s*Mp\\ge\s*([0-9]+)", "declared_k0_floor"), "declared_k0_floor")
    public_rounds = 3 if "Three public rounds are pinned" in table else 0
    underbudget_contacts_per_round = as_int(first(r"only\s*\$([0-9]+)\$ expected committee-contact events per round", "underbudget_contacts_per_round", haystack=text), "underbudget_contacts_per_round")
    underbudget_total = as_int(first(r"\\E\[K\]=3\\cdot\s*48\s*=\s*([0-9]+)", "underbudget_total", haystack=text), "underbudget_total")

    p_recomputed = ((1.0 - beta) * t / (alpha * d)) if alpha and d else 0.0
    k0_recomputed = M * p_recomputed if M else 0.0
    p_match = abs(p_declared - p_recomputed) <= 1e-12
    k0_match = abs(float(k0_declared) - k0_recomputed) <= 1e-12
    underbudget_match = public_rounds == 3 and underbudget_contacts_per_round == 48 and underbudget_total == 144 and underbudget_total < k0_declared
    exact_upper_guard = "exact yield" in table and "upper-yield envelope" in table
    lower_bound_non_theorem_guard = "lower-bound liveness estimate" in text and "must not be cited as an impossibility theorem" in text
    live_factor_guard = "MUCC live-factor non-substitution guard" in text and r"\label{prop:mucc-live-factor-guard}" in text
    alpha_direction_guard = "MUCC alpha-direction non-substitution guard" in text and r"\label{prop:mucc-alpha-direction-guard}" in text
    fixed_stop_guard = "dummy rounds continue" in table and "fixed-stop" in table
    sufficiency_nonclaim_guard = (
        "not a success certificate" in text
        and "necessary universal Markov floor" in text
        and "0.581" in text
        and "228" in text
        and "250" in text
        and "0.68" in text
        and "310" in text
        and "joint-contact" in text
    )
    sharp_ladder_guard = (
        "Sharp MUCC sufficiency ladder" in text
        and "0.81641472" in text
        and "0.94629888" in text
        and "0.95248384" in text
    )
    approximate_mucc_diameter_guard = (
        "Diameter-approximate MUCC" in text
        and "One-sided marginal ceilings do not imply cover contact" in text
        and "Marginally sharp cover floor for diameter-approximate MUCC" in text
        and "global marginal diameter" in text
        and "127.2" in text
        and r"\delta\le2\eta" in text.replace(" ", "")
    )
    nested_quorum_guard = (
        "Nested-quorum parameter non-substitution guard" in text
        and r"\label{prop:mucc-nested-quorum-guard}" in text
        and "outer-as-inner substitution" in text
        and r"(n,h,q,\rho)" in text.replace(" ", "")
    )
    label_uniformity_guard = (
        "Joint key-independence is not committee-label uniformity" in text
        and r"\label{rem:key-independent-not-mucc}" in text
        and r"C=\{1\}" in text.replace(" ", "")
        and r"\Delta_C=0" in text.replace(" ", "")
        and "global marginal-diameter" in text
    )
    joint_privacy_guard = (
        "MUCC is marginal-only, not privacy" in text
        and "Exact MUCC can leak the destination perfectly" in text
        and r"\label{prop:mucc-perfect-leakage}" in text
        and r"\Delta_C=1" in text.replace(" ", "")
        and "0.9628928" in text
        and "0.9628032" in text
        and "Any system claiming both must prove both axes" in text
    )
    stale_phantom_churn_table_claim = r"The evidence table \texttt{churn\_alpha\_table.tex}" in text
    phantom_churn_table_pointer_removed = (
        not stale_phantom_churn_table_claim
        and r"No separate \texttt{churn\_alpha\_table.tex} artifact is shipped or claimed" in text
    )

    inner_tuple_match = re.search(
        r"\(n,h,q,\\rho\)\s*=\s*\((\d+),(\d+),([0-9.]+),([0-9.]+)\)",
        text.replace(" ", ""),
    )
    if inner_tuple_match:
        inner_n = int(inner_tuple_match.group(1))
        inner_h = int(inner_tuple_match.group(2))
        inner_q = float(inner_tuple_match.group(3))
        inner_rho = float(inner_tuple_match.group(4))
    else:
        inner_n, inner_h, inner_q, inner_rho = 0, 0, 0.0, 0.0
        failures.append({"category": "mucc_inner_quorum_tuple_not_extracted"})

    import math
    ceil_floor = math.ceil(k0_recomputed - 1e-12)
    iid_tail_at_universal = _binom_tail(d, (ceil_floor / M) * alpha if M else 0.0, t)
    iid_min_k, iid_min_tail = _binomial_minimum_integer_contacts(M, d, t, alpha, beta)
    iid_predecessor_k = max(0, iid_min_k - 1)
    iid_predecessor_tail = _binom_tail(d, (iid_predecessor_k / M) * alpha if M else 0.0, t)
    hypergeom_tail_at_universal = _thinned_hypergeom_tail(M, d, ceil_floor, alpha, t)
    hypergeom_min_k, hypergeom_min_tail = _thinned_hypergeom_minimum_contacts(M, d, t, alpha, beta)
    hypergeom_predecessor_k = max(0, hypergeom_min_k - 1)
    hypergeom_predecessor_tail = _thinned_hypergeom_tail(M, d, hypergeom_predecessor_k, alpha, t)
    robust_tail_at_universal, robust_universal_witness = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * ceil_floor / M if M else 0.0)
    robust_tail_at_optimistic, robust_optimistic_witness = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * iid_min_k / M if M else 0.0)
    robust_min_k, robust_min_tail, robust_min_witness = _mucc_marginal_independent_minimum_contacts(M, d, t, alpha, beta)
    robust_predecessor_k = max(0, robust_min_k - 1)
    robust_predecessor_tail, robust_predecessor_witness = _mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * robust_predecessor_k / M if M else 0.0)
    mean_only_full_contact = _mean_only_liveness_success_lower_bound(d, t, alpha * d)
    mean_only_required = _mean_only_required_contacts_unclipped(M, d, t, alpha, beta)
    one_sided_attack = _one_sided_public_counterexample(M, d, t, alpha, beta)
    perfect_leakage_attack = _exact_mucc_perfect_leakage_counterexample(M, d, t, alpha)
    radius_eta = 0.05
    approx_A, correct_radius_floor, approx_feasible = _approximate_mucc_diameter_contact_floor(M, d, t, alpha, beta, 2.0 * radius_eta)
    inner_alpha_lower = _nested_committee_alpha_lower(inner_n, inner_h, inner_q, inner_rho)
    forbidden_outer_as_inner_alpha = _nested_committee_alpha_lower(d, t, inner_q, inner_rho)
    nested_alpha_overstatement = forbidden_outer_as_inner_alpha - inner_alpha_lower
    nested_alpha_overstatement_ratio = (forbidden_outer_as_inner_alpha / inner_alpha_lower) if inner_alpha_lower > 0.0 else float("inf")

    if not p_match:
        failures.append({"category": "mucc_p_floor_not_recomputed", "declared": p_declared, "recomputed": p_recomputed})
    if not k0_match:
        failures.append({"category": "mucc_k0_floor_not_recomputed", "declared": k0_declared, "recomputed": k0_recomputed})
    if not underbudget_match:
        failures.append({"category": "mucc_underbudget_drill_not_bound", "public_rounds": public_rounds, "contacts_per_round": underbudget_contacts_per_round, "total": underbudget_total})
    if not exact_upper_guard:
        failures.append({"category": "mucc_exact_upper_yield_guard_missing"})
    if not lower_bound_non_theorem_guard:
        failures.append({"category": "mucc_lower_bound_non_theorem_guard_missing"})
    if not live_factor_guard:
        failures.append({"category": "mucc_live_factor_guard_missing"})
    if not alpha_direction_guard:
        failures.append({"category": "mucc_alpha_direction_guard_missing"})
    if not fixed_stop_guard:
        failures.append({"category": "mucc_fixed_stop_guard_missing"})
    if not sufficiency_nonclaim_guard:
        failures.append({"category": "mucc_universal_floor_sufficiency_guard_missing"})
    if not sharp_ladder_guard:
        failures.append({"category": "mucc_sharp_sufficiency_ladder_missing"})
    if not approximate_mucc_diameter_guard:
        failures.append({"category": "mucc_approximate_diameter_guard_missing"})
    if not nested_quorum_guard:
        failures.append({"category": "mucc_nested_quorum_parameter_guard_missing"})
    if not label_uniformity_guard:
        failures.append({"category": "mucc_key_independence_label_uniformity_guard_missing"})
    if not joint_privacy_guard:
        failures.append({"category": "mucc_joint_contact_privacy_nonclaim_guard_missing"})
    if not phantom_churn_table_pointer_removed:
        failures.append({"category": "mucc_phantom_churn_table_pointer_not_removed"})
    if not approx_feasible:
        failures.append({"category": "mucc_approximate_diameter_public_parameters_infeasible"})
    if (inner_n, inner_h, inner_q, inner_rho) != (16, 11, 0.6, 0.0):
        failures.append({"category": "mucc_nested_quorum_collision_tuple_changed", "observed": [inner_n, inner_h, inner_q, inner_rho]})
    if abs(inner_alpha_lower - 0.3288404125089791) > 1e-12:
        failures.append({"category": "mucc_nested_quorum_correct_alpha_mismatch", "recomputed": inner_alpha_lower})
    if abs(forbidden_outer_as_inner_alpha - 0.8263296) > 1e-12:
        failures.append({"category": "mucc_nested_quorum_forbidden_alpha_mismatch", "recomputed": forbidden_outer_as_inner_alpha})
    if nested_alpha_overstatement <= 0.0 or nested_alpha_overstatement_ratio <= 1.0:
        failures.append({"category": "mucc_nested_quorum_collision_not_detected", "overstatement": nested_alpha_overstatement, "ratio": nested_alpha_overstatement_ratio})

    return {
        "extraction_status": "pass" if not failures else "fail",
        "extraction_failures": failures,
        "source_span": {"table_label": "tab:minimal-mucc-card", "label_present": r"\label{tab:minimal-mucc-card}" in text, "table_start_offset": table_start, "table_end_offset": table_end},
        "exposure_nf_id": exposure_nf_id,
        "threat_window_id": tw_id,
        "committee_universe_M": M,
        "destination_replication_d": d,
        "live_threshold_t": t,
        "alpha": alpha,
        "beta": beta,
        "p_floor_declared": p_declared,
        "p_floor_recomputed": p_recomputed,
        "p_floor_matches_recomputed": p_match,
        "expected_contact_floor_declared": k0_declared,
        "expected_contact_floor_recomputed": k0_recomputed,
        "expected_contact_floor_matches_recomputed": k0_match,
        "public_rounds": public_rounds,
        "underbudget_contacts_per_round": underbudget_contacts_per_round,
        "underbudget_total_contacts": underbudget_total,
        "underbudget_drill_present": underbudget_match,
        "exact_or_upper_yield_guard_present": exact_upper_guard,
        "lower_bound_non_theorem_guard_present": lower_bound_non_theorem_guard,
        "live_factor_non_substitution_guard_present": live_factor_guard,
        "alpha_direction_non_substitution_guard_present": alpha_direction_guard,
        "fixed_stop_guard_present": fixed_stop_guard,
        "universal_floor_not_sufficiency_guard_present": sufficiency_nonclaim_guard,
        "sharp_sufficiency_ladder_present": sharp_ladder_guard,
        "approximate_mucc_diameter_guard_present": approximate_mucc_diameter_guard,
        "nested_quorum_parameter_guard_present": nested_quorum_guard,
        "key_independence_label_uniformity_guard_present": label_uniformity_guard,
        "joint_contact_privacy_nonclaim_guard_present": joint_privacy_guard,
        "perfect_leakage_fixed_contact_count": perfect_leakage_attack["fixed_contact_count"],
        "perfect_leakage_contact_marginal": perfect_leakage_attack["contact_marginal"],
        "perfect_leakage_support_intersection_size": perfect_leakage_attack["conditional_support_intersection_size"],
        "perfect_leakage_total_variation_distance": perfect_leakage_attack["total_variation_distance"],
        "perfect_leakage_bayes_recovery": perfect_leakage_attack["bayes_optimal_destination_recovery"],
        "perfect_leakage_mutual_information_bits": perfect_leakage_attack["mutual_information_bits_uniform_binary_destination"],
        "perfect_leakage_success_probability_D0": perfect_leakage_attack["success_probability_D0"],
        "perfect_leakage_success_probability_D1": perfect_leakage_attack["success_probability_D1"],
        "perfect_leakage_destination_contact_count_multiplicities": perfect_leakage_attack["destination_contact_count_multiplicities"],
        "phantom_churn_table_pointer_removed": phantom_churn_table_pointer_removed,
        "inner_committee_members_n": inner_n,
        "inner_quorum_h": inner_h,
        "inner_member_reachability_q": inner_q,
        "inner_common_outage_rho": inner_rho,
        "inner_alpha_lower_recomputed": inner_alpha_lower,
        "forbidden_outer_as_inner_alpha": forbidden_outer_as_inner_alpha,
        "nested_quorum_alpha_overstatement": nested_alpha_overstatement,
        "nested_quorum_alpha_overstatement_ratio": nested_alpha_overstatement_ratio,
        "approximate_mucc_required_destination_contact_average_A": approx_A,
        "one_sided_counterexample_expected_total_contacts": one_sided_attack["expected_total_contacts"],
        "one_sided_counterexample_wrong_Mp_cover_floor": one_sided_attack["wrong_Mp_cover_floor"],
        "one_sided_counterexample_global_marginal_diameter": one_sided_attack["global_marginal_diameter"],
        "two_sided_radius_example_eta": radius_eta,
        "two_sided_radius_implied_diameter": 2.0 * radius_eta,
        "two_sided_radius_correct_contact_floor": correct_radius_floor,
        "iid_binomial_success_at_universal_floor": iid_tail_at_universal,
        "iid_binomial_predecessor_contacts": iid_predecessor_k,
        "iid_binomial_success_at_predecessor": iid_predecessor_tail,
        "iid_binomial_minimum_integer_contacts_for_success": iid_min_k,
        "iid_binomial_success_at_minimum_integer_contacts": iid_min_tail,
        "thinned_hypergeom_success_at_universal_floor": hypergeom_tail_at_universal,
        "thinned_hypergeom_predecessor_contacts": hypergeom_predecessor_k,
        "thinned_hypergeom_success_at_predecessor": hypergeom_predecessor_tail,
        "thinned_hypergeom_minimum_integer_contacts_for_success": hypergeom_min_k,
        "thinned_hypergeom_success_at_minimum_integer_contacts": hypergeom_min_tail,
        "mucc_marginal_independent_success_at_universal_floor": robust_tail_at_universal,
        "mucc_marginal_independent_witness_at_universal_floor": robust_universal_witness,
        "mucc_marginal_independent_success_at_optimistic_minimum": robust_tail_at_optimistic,
        "mucc_marginal_independent_witness_at_optimistic_minimum": robust_optimistic_witness,
        "mucc_marginal_independent_predecessor_contacts": robust_predecessor_k,
        "mucc_marginal_independent_success_at_predecessor": robust_predecessor_tail,
        "mucc_marginal_independent_witness_at_predecessor": robust_predecessor_witness,
        "mucc_marginal_independent_minimum_integer_contacts_for_success": robust_min_k,
        "mucc_marginal_independent_success_at_minimum_integer_contacts": robust_min_tail,
        "mucc_marginal_independent_witness_at_minimum": robust_min_witness,
        "mean_only_liveness_success_lower_bound_at_full_contact": mean_only_full_contact,
        "mean_only_liveness_required_contacts_unclipped": mean_only_required,
        "mean_only_liveness_target_certifiable_within_M": mean_only_required <= M,
        "hostile_review": mucc_hostile_review_vectors(M, d, t, alpha, beta, p_recomputed, k0_recomputed, underbudget_total, exact_upper_guard, lower_bound_non_theorem_guard, live_factor_guard, alpha_direction_guard, nested_quorum_guard, label_uniformity_guard, joint_privacy_guard, phantom_churn_table_pointer_removed, inner_n, inner_h, inner_q, inner_rho),
        "claim_boundary": "MUCC is not contact-set privacy. The exact-MUCC k0=250 orbit construction has disjoint conditional supports, TV=1, perfect destination recovery, and success above 0.9628. What remains is an assumption-indexed contact-cost ladder: 152 is universal necessity; 228 belongs only to named optimistic joint-contact models; 250 is the sharp MUCC-marginal plus independent-liveness guarantee; mean-only correlated liveness cannot certify 0.95. Approximate MUCC binds global marginal diameter. Outer (d,t) cannot be reused as inner (n,h): the pinned collision changes alpha from 0.3288404125 to 0.8263296. Destination-independence of the law of C is not committee-label uniformity without a symmetry or marginal-diameter bridge.",
    }

def generic_source_bound_card_values(source_text: str, source: str, source_sha: str) -> dict[str, Any]:
    citation_count = len(re.findall(r"\\cite(?:t|p)?\s*\{", source_text))
    label_count = len(re.findall(r"\\label\s*\{", source_text))
    evidence_mentions = sorted(set(re.findall(r"(?:validator|verifier|audit|receipt|manifest|witness|evidence)", source_text, flags=re.I)))
    return {
        "extraction_status": "not_applicable_generic_source_bound_card",
        "source_bound": True,
        "source_tex": source,
        "source_sha256": source_sha,
        "source_bytes": len(source_text.encode("utf-8", errors="replace")),
        "citation_command_count": citation_count,
        "label_count": label_count,
        "evidence_vocabulary_present": evidence_mentions,
        "claim_boundary": "Generic source-bound evidence card: this source lacks the Certified Menus minimal public card table, so the pack binds the exact source hash to static preflight and leaves theorem-specific evidence review to the release bill or a future source-specific extractor.",
    }


def select_card(source_text: str, source: str, source_sha: str) -> tuple[str, str, str, dict[str, Any]]:
    certified_values = extract_card_values(source_text)
    if certified_values.get("extraction_status") == "pass":
        return ("minimal_public_certified_menu_card", "CERTIFIED_MENU_CARD.json", "certified_menu_card", certified_values)
    signature_values = extract_signature_manifest_values(source_text)
    if signature_values.get("extraction_status") == "pass":
        return ("routing_signature_manifest_card", "ROUTING_SIGNATURE_MANIFEST_CARD.json", "routing_signature_manifest_card", signature_values)
    congestion_values = extract_congestion_eq_values(source_text)
    if congestion_values.get("extraction_status") == "pass":
        return ("congestion_eq_accountant_card", "CONGESTION_EQ_ACCOUNTANT_CARD.json", "congestion_eq_accountant_card", congestion_values)
    pscq_values = extract_pscq_values(source_text)
    if pscq_values.get("extraction_status") == "pass":
        return ("pscq_mechanism_card", "PSCQ_MECHANISM_CARD.json", "pscq_mechanism_card", pscq_values)
    wcongeq_values = extract_wcongeq_values(source_text)
    if wcongeq_values.get("extraction_status") == "pass":
        return ("wcongeq_replay_card", "W_CONGESTION_EQ_REPLAY_CARD.json", "wcongeq_replay_card", wcongeq_values)
    calibration_values = extract_calibration_recipe_values(source_text)
    if calibration_values.get("extraction_status") == "pass":
        return ("calibration_recipe_card", "CALIBRATION_RECIPE_CARD.json", "calibration_recipe_card", calibration_values)
    state_values = extract_state_anonymity_values(source_text)
    if state_values.get("extraction_status") == "pass":
        return ("state_anonymity_accountant_card", "STATE_ANONYMITY_CARD.json", "state_anonymity_accountant_card", state_values)
    mucc_values = extract_mucc_contact_floor_values(source_text)
    if mucc_values.get("extraction_status") == "pass":
        return ("mucc_contact_floor_card", "MUCC_CONTACT_FLOOR_CARD.json", "mucc_contact_floor_card", mucc_values)
    return ("source_bound_static_preflight_card", "SOURCE_BOUND_EVIDENCE_CARD.json", "source_bound_static_preflight_card", generic_source_bound_card_values(source_text, source, source_sha))

def run_static_preflight(root: pathlib.Path, source: str, title: str, source_sha: str, freeze_date: str, evidence_pack_rel: str, queue_state: str = "published_ready") -> dict[str, Any]:
    short_title = title[len(PREFIX):] if title.startswith(PREFIX) else title
    cmd = [
        sys.executable,
        "-B",
        "publishing/release_preflight.py",
        "--root",
        ".",
        "--date",
        freeze_date,
        "--title",
        short_title,
        "--source",
        source,
        "--expected-source-sha256",
        source_sha,
        "--evidence-mode",
        "require",
        "--evidence-pack",
        evidence_pack_rel,
        "--json",
    ]
    if queue_state != "published_ready":
        cmd.append("--allow-unqueued-source")
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True)
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        report = {
            "status": "fail",
            "problems": ["release_preflight.py did not emit JSON"],
            "stdout_tail": proc.stdout[-1000:],
            "stderr_tail": proc.stderr[-1000:],
        }
    report["command"] = " ".join(cmd[1:])
    report["returncode"] = proc.returncode
    return report


def existing_pack_id_for_source(root: pathlib.Path, source: str) -> str | None:
    registry_path = root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json"
    if not registry_path.exists():
        return None
    try:
        registry = load_json(registry_path)
    except Exception:
        return None
    for entry in registry.get("entries", []):
        if isinstance(entry, dict) and entry.get("source_tex") == source and entry.get("evidence_pack_id"):
            return str(entry["evidence_pack_id"])
    return None




def path_inside(root: pathlib.Path, rel: str) -> pathlib.Path | None:
    try:
        path = (root / rel).resolve()
        path.relative_to(root)
    except Exception:
        return None
    return path


def registry_manifest_exists(root: pathlib.Path, entry: dict[str, Any]) -> bool:
    manifest = entry.get("manifest") if isinstance(entry, dict) else None
    if not manifest:
        return False
    rel_inside = path_inside(root, str(manifest))
    return bool(rel_inside and rel_inside.exists())


def sync_preserved_pack(root: pathlib.Path, entry: dict[str, Any]) -> dict[str, Any]:
    """Keep preserved evidence packs aligned with queue-note moves.

    Earlier publication turns preserve old evidence packs after the next-release
    lane advances.  When a queue note is moved from published_ready to published,
    the registry entry can already know the new queue note while the historical
    pack manifest/card/README still point at the old path.  That creates a
    hot-path integrity failure even though the source evidence itself is
    unchanged.  This helper synchronizes only the decision-note binding and
    then recomputes the pack-path hashes; it does not change source hashes,
    card values, preflight results, or publication authorization.
    """
    manifest_rel = str(entry.get("manifest", ""))
    manifest_path = path_inside(root, manifest_rel)
    if not manifest_path or not manifest_path.exists():
        return dict(entry)
    try:
        manifest = load_json(manifest_path)
    except Exception:
        return dict(entry)

    wanted_note = str(entry.get("decision_note", ""))
    if not wanted_note:
        return dict(entry)

    changed = False
    if str(manifest.get("decision_note", "")) != wanted_note:
        manifest["decision_note"] = wanted_note
        changed = True

    card_rel = str(manifest.get("card_path", ""))
    card_path = path_inside(root, card_rel) if card_rel else None
    if card_path and card_path.exists():
        try:
            card = load_json(card_path)
        except Exception:
            card = None
        if isinstance(card, dict):
            binding = card.setdefault("source_binding", {})
            if isinstance(binding, dict) and str(binding.get("queue_decision_note", "")) != wanted_note:
                binding["queue_decision_note"] = wanted_note
                card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
                changed = True

    readme_path = path_inside(root, str(manifest.get("evidence_pack_root", "")) + "/README.md") if manifest.get("evidence_pack_root") else None
    if readme_path and readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
        updated = re.sub(r"- Queue note: `[^`]*`", f"- Queue note: `{wanted_note}`", readme)
        if updated != readme:
            readme_path.write_text(updated, encoding="utf-8")
            changed = True

    if changed:
        for row in manifest.get("pack_paths", []):
            if not isinstance(row, dict):
                continue
            pack_path = path_inside(root, str(row.get("path", "")))
            if pack_path and pack_path.exists():
                row["sha256"] = sha256_file(pack_path)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return dict(entry)



STATE_SOURCE = "series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex"
STATE_CARD_PATH = "release_queue/evidence_packs/2026.06.16-state-dependent-anonymity/STATE_ANONYMITY_CARD.json"
MUCC_SOURCE = "series/anondht_state_series/paper2_mucc_committee_contact_privacy/paper.tex"
MUCC_CARD_PATH = "release_queue/evidence_packs/2026.06.16-committee-contact-set-privacy-in-anonymous-dht-lookups/MUCC_CONTACT_FLOOR_CARD.json"



def mceq_hostile_review_vectors(root: pathlib.Path) -> dict[str, Any]:
    """Materialize arithmetic break vectors for the repaired MC-EQ boundary.

    This intentionally reads the maintained worked receipt only to test the
    retired binding.  It does not turn that receipt into an MC-EQ evidence card.
    """
    N = 256
    delta = 0.02
    T = 6
    core_probability = 1.0 - delta
    one_step_max_leakage = math.log2(1.0 + (N - 1) * delta)
    one_step_recovery = delta + core_probability / N
    no_tag_probability = core_probability ** T
    repeated_max_leakage = math.log2(N - (N - 1) * no_tag_probability)
    repeated_recovery = 1.0 - no_tag_probability + no_tag_probability / N
    k = 8
    epsilon = 0.005
    support_steps = 6
    support_max_leakage = support_steps * math.log2(1.0 + k * epsilon)
    support_pairwise_dinf = support_steps * math.log2((1.0 + k * epsilon) / (1.0 - k * epsilon))

    receipt_rel = "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_receipt.json"
    receipt = load_json(root / receipt_rel)
    item = next((row for row in receipt.get("line_items", []) if isinstance(row, dict) and row.get("name") == "fallback_tiered_vector"), {})
    knobs = item.get("knobs", {}) if isinstance(item.get("knobs"), dict) else {}
    vector = item.get("obs_model", {}).get("vector", []) if isinstance(item.get("obs_model"), dict) else []
    term_sum = sum(float(row.get("effective_b", 0.0)) for row in vector if isinstance(row, dict))
    retired_fields = [name for name in ("mc_eq_session_T", "per_step_epsilon_t", "conditional_independence_assumption") if name in knobs]

    published_calibration_rel = "published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/paper.tex"
    published_calibration_receipt_rel = "published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/PUBLICATION_RECEIPT.json"
    published_calibration_queue_note_rel = "release_queue/published/2026.06.16-paper3-calibration-recipes-published.md"
    published_calibration_text = (root / published_calibration_rel).read_text(encoding="utf-8", errors="replace")
    published_calibration_receipt = load_json(root / published_calibration_receipt_rel)
    published_calibration_queue_note = (root / published_calibration_queue_note_rel).read_text(encoding="utf-8", errors="replace")
    citation_heads = load_json(root / "published/citation_heads.json")
    citation_warning_present = any(
        "rev0897 MC-EQ correction" in str(warning)
        for warning in citation_heads.get("operator_warnings", [])
    )
    published_claim_present = (
        "T\\log_2(1+2k\\delta_{eq})" in published_calibration_text
        and "3.55" in published_calibration_text
    )
    published_snapshot_immutable = (
        sha256_file(root / published_calibration_rel)
        == published_calibration_receipt.get("published_tex_sha256")
    )
    published_correction_notice_present = "Rev0897 MC-EQ correction" in published_calibration_queue_note

    vectors = [
        {
            "id": "tv_as_finite_reference_ratio_without_support_containment",
            "status": "pass",
            "N": N,
            "delta": delta,
            "tv_to_reference": delta,
            "pairwise_tv": delta,
            "reference_max_divergence": "infinite",
            "off_support_mass": delta,
            "wrong_rule_authorized": False,
        },
        {
            "id": "pairwise_tv_as_alphabet_free_maximal_leakage",
            "status": "pass",
            "N": N,
            "delta": delta,
            "pairwise_tv": delta,
            "maximal_leakage_bits": one_step_max_leakage,
            "uniform_prior_recovery": one_step_recovery,
            "prior_recovery": 1.0 / N,
            "multiplicative_recovery_gain": 1.0 + (N - 1) * delta,
            "wrong_rule_authorized": False,
        },
        {
            "id": "repeated_off_support_tag_horizon",
            "status": "pass",
            "N": N,
            "delta": delta,
            "steps": T,
            "no_tag_probability": no_tag_probability,
            "maximal_leakage_bits": repeated_max_leakage,
            "uniform_prior_recovery": repeated_recovery,
            "wrong_linear_tv_to_maxleakage_rule_authorized": False,
        },
        {
            "id": "worked_fallback_vector_as_mceq_certificate",
            "status": "pass",
            "receipt_path": receipt_rel,
            "line_item": item.get("name"),
            "declared_budget_value": item.get("budget_value"),
            "recomputed_observation_attenuation_sum": term_sum,
            "semantic_scope": knobs.get("semantic_scope"),
            "composition_evidence_status": knobs.get("composition_evidence_status"),
            "publication_eligible": knobs.get("publication_eligible"),
            "retired_mceq_fields_present": retired_fields,
            "mceq_certificate_authorized": False,
        },
        {
            "id": "support_contained_uniform_cover_bound",
            "status": "pass",
            "cover_size_k": k,
            "tv_slack_epsilon": epsilon,
            "steps": support_steps,
            "reference_floor_q": 1.0 / k,
            "maximal_leakage_bound_bits": support_max_leakage,
            "pairwise_max_divergence_bound_bits": support_pairwise_dinf,
            "support_containment_required": True,
            "positive_reference_floor_required": True,
        },
        {
            "id": "singleton_tv_factor_two_overstatement",
            "status": "pass",
            "tv_slack_delta": delta,
            "correct_singleton_deviation_bound": delta,
            "legacy_loose_l1_bound": 2.0 * delta,
            "correct_bound_used_by_repaired_theorem": True,
        },
        {
            "id": "published_calibration_inherited_mceq_claim",
            "status": "pass",
            "published_tex_path": published_calibration_rel,
            "published_tex_sha256": sha256_file(root / published_calibration_rel),
            "publication_receipt_path": published_calibration_receipt_rel,
            "published_snapshot_immutable": published_snapshot_immutable,
            "legacy_mceq_claim_present": published_claim_present,
            "queue_correction_notice_present": published_correction_notice_present,
            "citation_head_warning_present": citation_warning_present,
            "legacy_claim_reuse_authorized": False,
        },
    ]
    checks = [
        abs(term_sum - float(item.get("budget_value", -1.0))) <= 1e-12,
        knobs.get("semantic_scope") == "illustrative_tiered_observation_attenuation_not_mceq",
        knobs.get("composition_evidence_status") == "assumption_only_no_joint_channel_witness",
        knobs.get("publication_eligible") is False,
        not retired_fields,
        published_snapshot_immutable,
        published_claim_present,
        published_correction_notice_present,
        citation_warning_present,
    ]
    return {
        "status": "pass" if all(checks) else "fail",
        "review_class": "internal_hostile_arithmetic_vectors",
        "external_reviewer_signoff": "missing",
        "blocking_publication_until_external_review": True,
        "vectors": vectors,
        "claim_boundary": "TV-MC-EQ supports transcript-TV statements. Finite reference ratios and maximal-leakage bounds require support containment plus a positive reference floor. The worked fallback vector is observation attenuation only and is publication-ineligible as MC-EQ evidence. The immutable published calibration snapshot retains a now-withdrawn inherited MC-EQ formula; existing citation and queue surfaces must carry its rev0897 non-reuse warning.",
    }


ENDPOINT_SOURCE = "series/anonymity_series/paperA_odds_inflation_anonymity/paper.tex"
ENDPOINT_BRIDGE_SOURCE = "series/synthesis/paper5_endpoint_metrics_bridge/paper.tex"
ENDPOINT_HOLD_NOTE = "release_queue/hold/2026.03.16-paperA-posterior-mass-true-odds-repair-hold.md"
CITATION_HEADS_PATH = "published/citation_heads.json"


def _published_ready_source_paths(root: pathlib.Path) -> list[str]:
    paths: list[str] = []
    queue_dir = root / "release_queue" / "published_ready"
    for note in sorted(queue_dir.glob("*.md")):
        match = re.search(r"^- Source paper: `([^`]+)`", note.read_text(encoding="utf-8", errors="replace"), flags=re.M)
        if match:
            paths.append(match.group(1))
    return paths


def endpoint_semantics_hostile_review_vectors(root: pathlib.Path) -> dict[str, Any]:
    """Materialize the PML/mass/true-odds and hockey-stick/tail repair vectors.

    This row also acts as a narrow semantic regression scan over the hot
    Published-ready lane.  It rejects only known false aliases; genuine
    pairwise likelihood-ratio/odds statements remain allowed.
    """
    N = 4096
    epsilon = 0.75
    p = 1.0 / N
    mass_factor = 2.0 ** epsilon
    true_odds_factor = mass_factor * (1.0 - p) / (1.0 - p * mass_factor)
    true_odds_bits = math.log2(true_odds_factor)

    hs_delta = 0.01
    positive_loss_tail = 0.51
    positive_loss_bits = math.log2(1.02)

    q_min = 0.10
    tv_delta = 0.01
    corrected_tv_bits = math.log2((q_min + tv_delta) / (q_min - tv_delta))
    legacy_double_tv_bits = math.log2((q_min + 2.0 * tv_delta) / (q_min - 2.0 * tv_delta))

    source_text = (root / ENDPOINT_SOURCE).read_text(encoding="utf-8", errors="replace")
    bridge_text = (root / ENDPOINT_BRIDGE_SOURCE).read_text(encoding="utf-8", errors="replace")
    hold_text = (root / ENDPOINT_HOLD_NOTE).read_text(encoding="utf-8", errors="replace") if (root / ENDPOINT_HOLD_NOTE).exists() else ""
    citation_heads = load_json(root / CITATION_HEADS_PATH)
    citation_warning_present = any(
        "rev0899 endpoint terminology correction" in str(warning).lower()
        for warning in citation_heads.get("operator_warnings", [])
    )

    banned_patterns = {
        "pml_as_realized_odds_alias": re.compile(r"(?:realized\s+odds[- ]inflation\s*/\s*PML|PML\s*/\s*realized\s+odds[- ]inflation)", re.I),
        "pml_as_posterior_odds_endpoint": re.compile(r"posterior[- ]odds\s+inflation\s+is\s+the\s+endpoint", re.I),
        "pml_odds_slash_alias": re.compile(r"PML\s*/\s*odds[- ]inflation", re.I),
        "maxl_odds_slash_alias": re.compile(r"MaxL\s*/\s*odds[- ]inflation", re.I),
    }
    semantic_alias_violations: list[dict[str, Any]] = []
    for rel in _published_ready_source_paths(root):
        path = root / rel
        if not path.exists():
            semantic_alias_violations.append({"source_tex": rel, "pattern": "source_missing"})
            continue
        candidate = path.read_text(encoding="utf-8", errors="replace")
        for pattern_id, pattern in banned_patterns.items():
            if pattern.search(candidate):
                semantic_alias_violations.append({"source_tex": rel, "pattern": pattern_id})

    vectors = [
        {
            "id": "pml_mass_as_true_odds",
            "status": "pass",
            "prior_probability": 0.5,
            "posterior_probability_after_reveal": 1.0,
            "pml_bits": 1.0,
            "posterior_mass_factor": 2.0,
            "true_odds_factor": "infinite",
            "legacy_alias_authorized": False,
        },
        {
            "id": "prior_cap_true_odds_conversion",
            "status": "pass",
            "candidate_count": N,
            "prior_cap": p,
            "pml_cap_bits": epsilon,
            "posterior_mass_factor": mass_factor,
            "no_saturation_guard": mass_factor * p < 1.0,
            "true_odds_factor": true_odds_factor,
            "true_odds_cap_bits": true_odds_bits,
        },
        {
            "id": "hockey_stick_delta_as_tail_probability",
            "status": "pass",
            "epsilon_bits": 0.0,
            "hockey_stick_slack": hs_delta,
            "positive_loss_tail_probability": positive_loss_tail,
            "positive_loss_bits": positive_loss_bits,
            "tail_to_slack_ratio": positive_loss_tail / hs_delta,
            "hockey_stick_as_tail_authorized": False,
        },
        {
            "id": "tail_implies_hockey_stick_not_converse",
            "status": "pass",
            "forward_implication": "tail_probability_at_most_eta_implies_hockey_stick_at_most_eta",
            "converse_counterexample_hockey_stick": hs_delta,
            "converse_counterexample_tail": positive_loss_tail,
            "converse_authorized": False,
        },
        {
            "id": "singleton_tv_factor_two_overpayment",
            "status": "pass",
            "reference_floor": q_min,
            "tv_slack": tv_delta,
            "correct_singleton_deviation": tv_delta,
            "legacy_double_deviation": 2.0 * tv_delta,
            "corrected_ratio_bound_bits": corrected_tv_bits,
            "legacy_ratio_bound_bits": legacy_double_tv_bits,
            "legacy_factor_two_authorized": False,
        },
        {
            "id": "published_legacy_odds_wording_as_true_odds",
            "status": "pass",
            "citation_head_warning_present": citation_warning_present,
            "legacy_wording_reuse_as_true_odds_authorized": False,
            "immutable_published_sources_rewritten": False,
        },
        {
            "id": "published_ready_semantic_alias_scan",
            "status": "pass" if not semantic_alias_violations else "fail",
            "sources_scanned": _published_ready_source_paths(root),
            "violation_count": len(semantic_alias_violations),
            "violations": semantic_alias_violations,
        },
    ]

    source_guards = [
        "Posterior-Mass Inflation Anonymity" in source_text,
        "One bit of PML can coexist with infinite true-odds inflation" in source_text,
        "What $\\delta$ does and does not mean" in source_text,
        r"\frac{Q_{\min}+\delta}{Q_{\min}-\delta}" in source_text,
        "The result is a corrected endpoint theorem, not a deployment certificate" in source_text,
        "Posterior-mass inflation is PML, not posterior odds" in bridge_text,
        "Hold / publication-blocked" in hold_text,
        "model-level terminology and theorem-boundary repair" in hold_text,
        citation_warning_present,
        not semantic_alias_violations,
    ]
    return {
        "status": "pass" if all(source_guards) and all(row.get("status") == "pass" for row in vectors) else "fail",
        "review_class": "internal_hostile_arithmetic_vectors",
        "external_reviewer_signoff": "missing",
        "blocking_publication_until_external_review": True,
        "vectors": vectors,
        "claim_boundary": "PML is posterior-mass inflation relative to a declared prior, not true one-vs-complement odds. A prior cap plus a no-saturation guard is required for finite mass-to-odds conversion. Hockey-stick slack is weighted excess, not a bad-transcript probability absent a separate tail theorem. Common-reference TV needs only the singleton delta deviation, not a doubled 2 delta payment. Immutable published wording is corrected by current citation-head warnings rather than rewritten in place.",
    }


def write_hostile_review_overlay(root: pathlib.Path, release: dict[str, Any], *, current_source: str, current_card_rel: str, current_card_values: dict[str, Any]) -> None:
    """Refresh the current hostile-vector overlay without rewriting historical cards.

    The State card is already a published/frozen evidence object, so its current
    hostile vectors live in an overlay.  The live MUCC freeze card carries the
    same class of vectors directly.  Source-current extension rows (for example,
    CPPC hostile vectors that are not evidence-pack-backed) are preserved only
    when their source digest still matches, their internal review currently
    passes, and they remain explicitly publication-blocking.  This prevents a
    targeted evidence-pack refresh from destructively deleting an independent
    theorem audit while still failing closed on stale or authorizing rows.
    """
    entries: list[dict[str, Any]] = []
    overlay_path = root / "release_queue" / "HOSTILE_REVIEW_VECTORS.json"
    prior_extension_rows: list[dict[str, Any]] = []
    core_sources = {
        STATE_SOURCE,
        MUCC_SOURCE,
        "series/release_and_destination/paperB_mceq_coversketch_destination_privacy/paper.tex",
        ENDPOINT_SOURCE,
    }
    if overlay_path.exists():
        try:
            prior_overlay = load_json(overlay_path)
        except Exception:
            prior_overlay = {}
        for row in prior_overlay.get("entries", []):
            if not isinstance(row, dict):
                continue
            source_rel = str(row.get("source_tex", ""))
            hostile = row.get("hostile_review")
            source_path = root / source_rel if source_rel else None
            if (
                not source_rel
                or source_rel in core_sources
                or source_path is None
                or not source_path.exists()
                or row.get("source_sha256") != sha256_file(source_path)
                or not isinstance(hostile, dict)
                or hostile.get("status") != "pass"
                or hostile.get("blocking_publication_until_external_review") is not True
            ):
                continue
            prior_extension_rows.append(dict(row))

    state_path = root / STATE_SOURCE
    if state_path.exists():
        state_sha = sha256_file(state_path)
        state_values = extract_state_anonymity_values(state_path.read_text(encoding="utf-8", errors="replace"))
        entries.append({
            "review_target": "State-Dependent Anonymity nat/bit accountant boundary",
            "source_tex": STATE_SOURCE,
            "source_sha256": state_sha,
            "evidence_card": STATE_CARD_PATH,
            "evidence_card_immutability_note": "The published historical State evidence card is not rewritten; these are current overlay break vectors checked by evidence integrity.",
            "hostile_review": state_values.get("hostile_review", {}),
        })

    if current_source == MUCC_SOURCE and isinstance(current_card_values.get("hostile_review"), dict):
        mucc_sha = sha256_file(root / MUCC_SOURCE)
        mucc_card_rel = current_card_rel
        mucc_hostile = current_card_values.get("hostile_review", {})
    else:
        mucc_sha = sha256_file(root / MUCC_SOURCE) if (root / MUCC_SOURCE).exists() else ""
        mucc_card_rel = MUCC_CARD_PATH
        try:
            mucc_card = load_json(root / MUCC_CARD_PATH)
            mucc_hostile = mucc_card.get("card_values", {}).get("hostile_review", {})
        except Exception:
            mucc_hostile = {}
    if mucc_sha:
        entries.append({
            "review_target": "MUCC contact-floor and liveness non-substitution boundary",
            "source_tex": MUCC_SOURCE,
            "source_sha256": mucc_sha,
            "evidence_card": mucc_card_rel,
            "evidence_card_immutability_note": "The MUCC card is the live next-lane freeze card and carries the same hostile vectors directly after evidence-pack rebuild.",
            "hostile_review": mucc_hostile,
        })

    mceq_path = root / "series/release_and_destination/paperB_mceq_coversketch_destination_privacy/paper.tex"
    if mceq_path.exists():
        entries.append({
            "review_target": "MC-EQ TV/support/ratio and worked-binding boundary",
            "source_tex": "series/release_and_destination/paperB_mceq_coversketch_destination_privacy/paper.tex",
            "source_sha256": sha256_file(mceq_path),
            "evidence_card": None,
            "evidence_card_immutability_note": "No deployment MC-EQ evidence card exists; this overlay binds theorem arithmetic and the retired worked-example binding only.",
            "hostile_review": mceq_hostile_review_vectors(root),
        })

    endpoint_path = root / ENDPOINT_SOURCE
    if endpoint_path.exists():
        entries.append({
            "review_target": "Endpoint PML/mass/true-odds and hockey-stick/tail boundary",
            "source_tex": ENDPOINT_SOURCE,
            "source_sha256": sha256_file(endpoint_path),
            "evidence_card": None,
            "evidence_card_immutability_note": "No deployment endpoint card is claimed; this overlay binds the corrected theorem, queue demotion, public-head warning, and semantic regression scan.",
            "hostile_review": endpoint_semantics_hostile_review_vectors(root),
        })

    existing_sources = {str(row.get("source_tex", "")) for row in entries}
    for row in sorted(prior_extension_rows, key=lambda item: str(item.get("source_tex", ""))):
        source_rel = str(row.get("source_tex", ""))
        if source_rel and source_rel not in existing_sources:
            entries.append(row)
            existing_sources.add(source_rel)

    bad_entries = [row for row in entries if not isinstance(row.get("hostile_review"), dict) or row.get("hostile_review", {}).get("status") != "pass"]
    overlay = {
        "version": 2,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "status": "pass" if not bad_entries and len(entries) >= 4 else "fail",
        "review_class": "internal_hostile_arithmetic_vectors_not_external_signoff",
        "external_reviewer_signoff": "missing",
        "blocking_publication_until_external_review": True,
        "entries": entries,
        "failures": [{"category": "hostile_entry_not_pass", "source_tex": row.get("source_tex")} for row in bad_entries],
        "claim_boundary": "These rows are internal hostile arithmetic break vectors. They do not replace named external adversarial review, countersignature, or a transparency pin.",
    }
    (root / "release_queue" / "HOSTILE_REVIEW_VECTORS.json").write_text(json.dumps(overlay, indent=2) + "\n", encoding="utf-8")

def preserved_registry_entries(root: pathlib.Path, current_source: str) -> list[dict[str, Any]]:
    registry_path = root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json"
    if not registry_path.exists():
        return []
    try:
        registry = load_json(registry_path)
    except Exception:
        return []
    preserved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in registry.get("entries", []):
        if not isinstance(entry, dict):
            continue
        manifest = str(entry.get("manifest", ""))
        if not manifest or manifest in seen:
            continue
        if entry.get("source_tex") == current_source:
            continue
        if not registry_manifest_exists(root, entry):
            continue
        preserved.append(dict(entry))
        seen.add(manifest)
    return preserved

def _queue_records_for_source(root: pathlib.Path, source: str) -> list[dict[str, Any]]:
    queue = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    rows: list[dict[str, Any]] = []
    states = queue.get("states", {}) if isinstance(queue.get("states"), dict) else {}
    for state, state_rows in states.items():
        if not isinstance(state_rows, list):
            continue
        for row in state_rows:
            if isinstance(row, dict) and str(row.get("source_tex", "")) == source:
                item = dict(row)
                item["queue_state"] = state
                item["decision_note"] = row.get("path")
                rows.append(item)
    return rows


def _decision_note_source_hashes(root: pathlib.Path, note_rel: str) -> set[str]:
    note_path = path_inside(root, note_rel)
    if not note_path or not note_path.exists():
        return set()
    text = note_path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"(?:sha256:|SHA-256:\s*`?)([0-9a-f]{64})", text, flags=re.I))


def _resolve_staged_queue_source(root: pathlib.Path, source: str, *, reason: str) -> dict[str, Any]:
    normalized = pathlib.PurePosixPath(source).as_posix()
    matches = _queue_records_for_source(root, normalized)
    if len(matches) != 1:
        raise RuntimeError(f"staged source must match exactly one queue item: {normalized} (matches={len(matches)})")
    item = matches[0]
    state = str(item.get("queue_state", ""))
    if state not in {"published_ready", "hold", "candidate"}:
        raise RuntimeError(f"staged source is not in a reviewable unpublished queue state: {normalized} ({state})")
    if not existing_pack_id_for_source(root, normalized):
        raise RuntimeError(f"source is not an already-staged evidence lane: {normalized}")
    source_path = root / normalized
    if not source_path.exists():
        raise RuntimeError(f"staged source is missing: {normalized}")
    source_sha = sha256_file(source_path)
    decision_note = str(item.get("decision_note", ""))
    note_hashes = _decision_note_source_hashes(root, decision_note)
    if source_sha not in note_hashes:
        raise RuntimeError(f"queue note does not bind the current staged source digest: {decision_note} ({source_sha})")
    title = str(item.get("title", "")).strip()
    if not title or title.endswith("-hold"):
        source_text = source_path.read_text(encoding="utf-8", errors="replace")
        title_match = re.search(r"\\title\{([^{}]+)\}", source_text)
        title = title_match.group(1).strip() if title_match else pathlib.PurePosixPath(normalized).parent.name
    return {
        "status": "static_pass_candidate_available",
        "source_tex": normalized,
        "title": title,
        "decision_note": decision_note,
        "source_sha256": source_sha,
        "warning_count": 0,
        "queue_state": state,
        "evidence_pack_lane_already_staged": True,
        "reason": reason,
    }


def _stale_staged_source(root: pathlib.Path) -> str:
    registry_path = root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json"
    if not registry_path.exists():
        return ""
    try:
        registry = load_json(registry_path)
    except Exception:
        return ""
    priority = {"hold": 0, "published_ready": 1, "candidate": 2}
    stale: list[tuple[int, str]] = []
    for entry in registry.get("entries", []):
        if not isinstance(entry, dict):
            continue
        source = str(entry.get("source_tex", ""))
        source_path = path_inside(root, source)
        if not source or not source_path or not source_path.exists():
            continue
        rows = _queue_records_for_source(root, source)
        if len(rows) != 1:
            continue
        state = str(rows[0].get("queue_state", ""))
        if state not in priority:
            continue
        current_sha = sha256_file(source_path)
        if current_sha != str(entry.get("source_sha256", "")):
            stale.append((priority[state], source))
    return sorted(stale)[0][1] if stale else ""


def _resolve_recommendation(root: pathlib.Path, readiness: dict[str, Any], source_override: str = "") -> dict[str, Any]:
    """Resolve an already-staged review lane without auto-opening a new one.

    Rebuilds first repair stale source-bound evidence, including lanes demoted to
    Hold after a theorem failure.  They may refresh an already-staged current
    recommendation.  They do not create a new evidence/freeze lane merely
    because queue ordering advanced: opening a new lane now requires an explicit
    operator source choice after the substantive review work is complete.
    """
    if source_override:
        return _resolve_staged_queue_source(
            root,
            source_override,
            reason="Explicit targeted refresh of an existing source-bound evidence lane.",
        )

    stale = _stale_staged_source(root)
    if stale:
        return _resolve_staged_queue_source(
            root,
            stale,
            reason="Automatic repair of a stale existing evidence lane; no new lane was opened.",
        )

    recommendation = readiness.get("next_release_recommendation", {}) if isinstance(readiness.get("next_release_recommendation"), dict) else {}
    recommended_source = str(recommendation.get("source_tex", ""))
    if recommendation.get("status") == "static_pass_candidate_available" and recommended_source and existing_pack_id_for_source(root, recommended_source):
        return _resolve_staged_queue_source(
            root,
            recommended_source,
            reason="Refresh of the already-staged next-release evidence lane.",
        )

    return {
        "status": "no_auto_open_new_lane",
        "next_release_recommendation": recommendation,
        "reason": "No existing evidence lane is stale and the next queue recommendation has no staged pack. Rebuild remains non-expansive; evidence attachment must be an explicit review action.",
    }

def build(root: pathlib.Path, source_override: str = "") -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    readiness = rr.check(root)
    recommendation = _resolve_recommendation(root, readiness, source_override)
    if recommendation.get("status") == "no_auto_open_new_lane":
        registry_path = root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json"
        if registry_path.exists():
            registry = load_json(registry_path)
            registry["generated_for_revision"] = release["revision"]
            registry["checked_bundle"] = release["bundle"]
            registry["publication_authorized"] = False
            registry["automatic_lane_opening"] = False
            registry["lane_opening_policy"] = "Rebuilds refresh staged lanes but do not create a new evidence/freeze lane from queue order alone."
            registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        return {"status": "pass", "action": "no_auto_open_new_lane", **recommendation}
    source = str(recommendation["source_tex"])
    title = str(recommendation["title"])
    source_sha = str(recommendation["source_sha256"])
    source_path = root / source
    source_text = source_path.read_text(encoding="utf-8", errors="replace")
    current_sha = sha256_file(source_path)
    if current_sha != source_sha:
        raise RuntimeError(f"recommendation source hash drift: {source_sha} != {current_sha}")

    freeze_date = freeze_date_from_manifest(release)
    pack_id = existing_pack_id_for_source(root, source) or f"{freeze_date}-{slugify(title)}"
    pack_rel = f"release_queue/evidence_packs/{pack_id}"
    pack_dir = root / pack_rel
    pack_dir.mkdir(parents=True, exist_ok=True)

    card_type, card_filename, card_role, card_values = select_card(source_text, source, source_sha)
    if card_role == "calibration_recipe_card":
        worked_route_audit = calibration_worked_route_audit(root)
        card_values["worked_route_materialization_audit"] = worked_route_audit
        if worked_route_audit.get("status") != "pass":
            failures = card_values.setdefault("extraction_failures", [])
            if isinstance(failures, list):
                failures.append({"category": "calibration_worked_route_materialization_audit_failed", "audit": worked_route_audit})
            card_values["extraction_status"] = "fail"
    card = {
        "version": 2,
        "evidence_pack_id": pack_id,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "card_type": card_type,
        "card_values": card_values,
        "source_binding": {
            "queue_decision_note": recommendation.get("decision_note"),
            "queue_state": str(recommendation.get("queue_state", "published_ready")),
            "table_label": {
                "certified_menu_card": "tab:minimal-certified-menu-card",
                "routing_signature_manifest_card": "tab:minimal-signature-manifest-card",
                "congestion_eq_accountant_card": "tab:minimal-congeq-card",
                "pscq_mechanism_card": "tab:minimal-pscq-card",
                "wcongeq_replay_card": "tab:minimal-wcongeq-card",
                "calibration_recipe_card": "tab:minimal-calibration-card",
                "state_anonymity_accountant_card": "tab:minimal-state-anonymity-card",
                "mucc_contact_floor_card": "tab:minimal-mucc-card",
            }.get(card_role, "not_applicable_generic_source_bound_card"),
        },
        "non_authorization_notice": "This card is freeze evidence for review; it is not a publication decision and does not move the queue.",
    }
    (pack_dir / card_filename).write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    write_hostile_review_overlay(root, release, current_source=source, current_card_rel=f"{pack_rel}/{card_filename}", current_card_values=card_values)

    readme = f"""# Evidence pack: {title}

- Evidence pack id: `{pack_id}`
- Source: `{source}`
- Source SHA-256: `{source_sha}`
- Queue note: `{recommendation.get('decision_note')}`
- Generated for revision: `{release['revision']}`
- Publication authorized: `false`

This non-public freeze evidence pack resolves the selected target's evidence-pack gate only for dry-run planning. It does not publish the paper, does not create a public citation head, and does not replace the required explicit publication decision.

## Contents

- `{card_filename}` — machine-readable source-bound freeze card; Certified Menus sources use the minimal certified-menu extractor, Routing-Signature sources use a signature-manifest extractor, Congestion-EQ sources use an accountant-card extractor, PSC-Q sources use a mechanism-card extractor, W-Congestion-EQ sources use a replay-card extractor, Calibration Recipes sources use a calibration-card extractor, State-Dependent sources use a unit-normalized accountant extractor, MUCC sources use a contact-floor extractor, and other sources use a generic source/static-preflight binding card.
- `release_preflight_static.json` — static source/hash/citation/reference/evidence-path preflight with the pack attached.
- `EVIDENCE_PACK_MANIFEST.json` — path and digest manifest for this evidence pack.
"""
    (pack_dir / "README.md").write_text(readme, encoding="utf-8")

    preflight = run_static_preflight(root, source, title, source_sha, freeze_date, pack_rel, str(recommendation.get("queue_state", "published_ready")))
    (pack_dir / "release_preflight_static.json").write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")

    pack_files = [
        ("README.md", "pack_readme"),
        (card_filename, card_role),
        ("release_preflight_static.json", "release_preflight_static_report"),
    ]
    manifest = {
        "version": 1,
        "evidence_pack_id": pack_id,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "status": "attached_non_public_freeze_evidence",
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "decision_note": recommendation.get("decision_note"),
        "card_type": card_type,
        "card_path": f"{pack_rel}/{card_filename}",
        "evidence_pack_root": pack_rel,
        "required_resolution": "attach_evidence_pack",
        "pack_paths": [
            {
                "path": f"{pack_rel}/{name}",
                "role": role,
                "sha256": sha256_file(pack_dir / name),
            }
            for name, role in pack_files
        ],
        "minimum_policy_rows_satisfied": [
            "source_tex_sha256",
            "evidence_pack_manifest_or_manifest_excerpt",
            "declared evidence-pack paths resolved inside the archive",
            "validator_or_audit_report_when_source_cites_validator_or_audit_surface",
        ],
        "limits": [
            "This pack is attached to the freeze plan but does not authorize publication.",
            "A separate publication decision must name this pack or supersede it with an explicit waiver.",
        ],
    }
    (pack_dir / "EVIDENCE_PACK_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    current_entry = {
        "evidence_pack_id": pack_id,
        "status": "attached_non_public_freeze_evidence",
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "decision_note": recommendation.get("decision_note"),
        "card_type": card_type,
        "manifest": f"{pack_rel}/EVIDENCE_PACK_MANIFEST.json",
        "required_resolution": "attach_evidence_pack",
        "publication_scope": "next_release_freeze_candidate_only",
    }
    registry = {
        "version": 2,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "entries": preserved_registry_entries(root, source) + [current_entry],
        "preservation_note": "Registry rebuilds preserve earlier source-bound evidence packs so publication receipts do not become unregistered when the next-release lane advances.",
        "fail_closed_rule": "Evidence pack attachment resolves only the evidence gate for dry-run planning. Publication still requires a separate written decision.",
    }
    (root / "release_queue" / "EVIDENCE_PACK_REGISTRY.json").write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"status": "pass", "evidence_pack_id": pack_id, "source_tex": source, "source_sha256": source_sha, "manifest": current_entry["manifest"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--source", default="", help="refresh one already-staged unpublished queue source (including a corrective Hold lane)")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    try:
        report = build(root, source_override=args.source)
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
