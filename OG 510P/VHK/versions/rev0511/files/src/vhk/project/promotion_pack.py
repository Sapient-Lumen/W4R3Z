from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vhk.project.claim_pack import build_claim_plan
from vhk.project.loader import load_project
from vhk.project.strategy import summarize_project_strategy


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 8) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out




def _promotion_gate_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str(item.get("status") or "review") for item in rows if isinstance(item, dict)]
    return {
        "gate_count": len(rows),
        "pass_count": sum(1 for status in statuses if status == "pass"),
        "review_count": sum(1 for status in statuses if status == "review"),
        "fail_count": sum(1 for status in statuses if status == "fail"),
        "failing_gate_ids": [str(item.get("gate_id") or "") for item in rows if str(item.get("status") or "") == "fail" and str(item.get("gate_id") or "")],
        "review_gate_ids": [str(item.get("gate_id") or "") for item in rows if str(item.get("status") or "") == "review" and str(item.get("gate_id") or "")],
    }


def _promotion_backlog_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    states = [str(item.get("queue_state") or "review") for item in rows if isinstance(item, dict)]
    return {
        "task_count": len(rows),
        "blocked_count": sum(1 for state in states if state == "blocked"),
        "review_count": sum(1 for state in states if state == "review"),
        "todo_count": sum(1 for state in states if state == "todo"),
        "done_count": sum(1 for state in states if state == "done"),
    }


def _promotion_evidence_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [str(item.get("evidence_status") or "partial") for item in rows if isinstance(item, dict)]
    return {
        "entry_count": len(rows),
        "complete_count": sum(1 for status in statuses if status == "complete"),
        "partial_count": sum(1 for status in statuses if status == "partial"),
        "missing_count": sum(1 for status in statuses if status == "missing"),
    }


def _promotion_input_lane_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    postures = [str(item.get("shipping_posture") or "reviewed") for item in rows if isinstance(item, dict)]
    primary_lane_counts: dict[str, int] = {}
    review_surface_ids: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        lane_id = str(item.get("primary_input_lane_id") or "").strip()
        if lane_id:
            primary_lane_counts[lane_id] = primary_lane_counts.get(lane_id, 0) + 1
        posture = str(item.get("shipping_posture") or "reviewed")
        if posture in {"reviewed", "specialist"}:
            surface_id = str(item.get("export_surface_id") or "").strip()
            if surface_id:
                review_surface_ids.append(surface_id)
    ordered_lane_ids = [
        lane_id
        for lane_id, _count in sorted(primary_lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))
    ]
    return {
        "entry_count": len(rows),
        "flagship_count": sum(1 for posture in postures if posture == "flagship"),
        "specialist_count": sum(1 for posture in postures if posture == "specialist"),
        "reviewed_count": sum(1 for posture in postures if posture == "reviewed"),
        "orthogonal_count": sum(1 for posture in postures if posture == "orthogonal"),
        "primary_lane_counts": primary_lane_counts,
        "ordered_primary_lane_ids": ordered_lane_ids,
        "review_surface_ids": _dedupe_keep_order(review_surface_ids),
    }


def _promotion_activation_route_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    postures = [str(item.get("startup_posture") or "reviewed") for item in rows if isinstance(item, dict)]
    primary_route_counts: dict[str, int] = {}
    review_surface_ids: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        route_id = str(item.get("primary_activation_route_id") or "").strip()
        if route_id:
            primary_route_counts[route_id] = primary_route_counts.get(route_id, 0) + 1
        posture = str(item.get("startup_posture") or "reviewed")
        if posture in {"reviewed", "session-bound"}:
            surface_id = str(item.get("export_surface_id") or "").strip()
            if surface_id:
                review_surface_ids.append(surface_id)
    ordered_route_ids = [
        route_id
        for route_id, _count in sorted(primary_route_counts.items(), key=lambda pair: (-pair[1], pair[0]))
    ]
    return {
        "entry_count": len(rows),
        "resident_count": sum(1 for posture in postures if posture == "resident"),
        "session_bound_count": sum(1 for posture in postures if posture == "session-bound"),
        "launcher_first_count": sum(1 for posture in postures if posture == "launcher-first"),
        "reviewed_count": sum(1 for posture in postures if posture == "reviewed"),
        "orthogonal_count": sum(1 for posture in postures if posture == "orthogonal"),
        "primary_route_counts": primary_route_counts,
        "ordered_primary_route_ids": ordered_route_ids,
        "review_surface_ids": _dedupe_keep_order(review_surface_ids),
    }


def _promotion_operator_control_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    postures = [str(item.get("control_posture") or "reviewed") for item in rows if isinstance(item, dict)]
    primary_lane_counts: dict[str, int] = {}
    review_surface_ids: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        lane_id = str(item.get("primary_control_lane_id") or "").strip()
        if lane_id:
            primary_lane_counts[lane_id] = primary_lane_counts.get(lane_id, 0) + 1
        posture = str(item.get("control_posture") or "reviewed")
        if posture in {"daemon-reviewed", "session-managed", "reviewed"}:
            surface_id = str(item.get("export_surface_id") or "").strip()
            if surface_id:
                review_surface_ids.append(surface_id)
    ordered_lane_ids = [
        lane_id
        for lane_id, _count in sorted(primary_lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))
    ]
    return {
        "entry_count": len(rows),
        "service_managed_count": sum(1 for posture in postures if posture == "service-managed"),
        "session_managed_count": sum(1 for posture in postures if posture == "session-managed"),
        "daemon_reviewed_count": sum(1 for posture in postures if posture == "daemon-reviewed"),
        "manual_entry_count": sum(1 for posture in postures if posture == "manual-entry"),
        "reviewed_count": sum(1 for posture in postures if posture == "reviewed"),
        "primary_control_lane_counts": primary_lane_counts,
        "ordered_primary_control_lane_ids": ordered_lane_ids,
        "review_surface_ids": _dedupe_keep_order(review_surface_ids),
    }


def _promotion_recovery_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    postures = [str(item.get("recovery_posture") or "review-led") for item in rows if isinstance(item, dict)]
    primary_lane_counts: dict[str, int] = {}
    review_surface_ids: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        lane_id = str(item.get("primary_recovery_lane_id") or "").strip()
        if lane_id:
            primary_lane_counts[lane_id] = primary_lane_counts.get(lane_id, 0) + 1
        posture = str(item.get("recovery_posture") or "review-led")
        if posture in {"rollback-first", "session-recreate", "daemon-reset", "review-led"}:
            surface_id = str(item.get("export_surface_id") or "").strip()
            if surface_id:
                review_surface_ids.append(surface_id)
    ordered_lane_ids = [lane_id for lane_id, _count in sorted(primary_lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))]
    return {
        "entry_count": len(rows),
        "rollback_first_count": sum(1 for posture in postures if posture == "rollback-first"),
        "session_recreate_count": sum(1 for posture in postures if posture == "session-recreate"),
        "daemon_reset_count": sum(1 for posture in postures if posture == "daemon-reset"),
        "service_restart_count": sum(1 for posture in postures if posture == "service-restart"),
        "reload_and_smoke_count": sum(1 for posture in postures if posture == "reload-and-smoke"),
        "manual_smoke_count": sum(1 for posture in postures if posture == "manual-smoke"),
        "review_led_count": sum(1 for posture in postures if posture == "review-led"),
        "primary_recovery_lane_counts": primary_lane_counts,
        "ordered_primary_recovery_lane_ids": ordered_lane_ids,
        "review_surface_ids": _dedupe_keep_order(review_surface_ids),
    }


def _promotion_verification_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    postures = [str(item.get("verification_posture") or "review-proof") for item in rows if isinstance(item, dict)]
    primary_lane_counts: dict[str, int] = {}
    review_surface_ids: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        lane_id = str(item.get("primary_verification_lane_id") or "").strip()
        if lane_id:
            primary_lane_counts[lane_id] = primary_lane_counts.get(lane_id, 0) + 1
        posture = str(item.get("verification_posture") or "review-proof")
        if posture in {"portal-proof", "daemon-proof", "review-proof"}:
            surface_id = str(item.get("export_surface_id") or "").strip()
            if surface_id:
                review_surface_ids.append(surface_id)
    ordered_lane_ids = [lane_id for lane_id, _count in sorted(primary_lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))]
    return {
        "entry_count": len(rows),
        "service_smoke_count": sum(1 for posture in postures if posture == "service-smoke"),
        "input_event_smoke_count": sum(1 for posture in postures if posture == "input-event-smoke"),
        "portal_proof_count": sum(1 for posture in postures if posture == "portal-proof"),
        "daemon_proof_count": sum(1 for posture in postures if posture == "daemon-proof"),
        "event_flow_smoke_count": sum(1 for posture in postures if posture == "event-flow-smoke"),
        "launch_smoke_count": sum(1 for posture in postures if posture == "launch-smoke"),
        "review_proof_count": sum(1 for posture in postures if posture == "review-proof"),
        "primary_verification_lane_counts": primary_lane_counts,
        "ordered_primary_verification_lane_ids": ordered_lane_ids,
        "review_surface_ids": _dedupe_keep_order(review_surface_ids),
    }


def _promotion_performance_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    postures = [str(item.get("performance_posture") or "review-measured") for item in rows if isinstance(item, dict)]
    primary_lane_counts: dict[str, int] = {}
    hotspot_counts: dict[str, int] = {}
    review_surface_ids: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        lane_id = str(item.get("primary_performance_lane_id") or "").strip()
        if lane_id:
            primary_lane_counts[lane_id] = primary_lane_counts.get(lane_id, 0) + 1
        for hotspot_id in [str(x) for x in list(item.get("performance_hotspot_ids") or []) if str(x)]:
            hotspot_counts[hotspot_id] = hotspot_counts.get(hotspot_id, 0) + 1
        posture = str(item.get("performance_posture") or "review-measured")
        if posture in {"warm-daemon", "consent-bound-async", "review-measured"}:
            surface_id = str(item.get("export_surface_id") or "").strip()
            if surface_id:
                review_surface_ids.append(surface_id)
    ordered_lane_ids = [lane_id for lane_id, _count in sorted(primary_lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))]
    ordered_hotspot_ids = [hotspot_id for hotspot_id, _count in sorted(hotspot_counts.items(), key=lambda pair: (-pair[1], pair[0]))]
    return {
        "entry_count": len(rows),
        "low_latency_edge_count": sum(1 for posture in postures if posture == "low-latency-edge"),
        "throughput_first_count": sum(1 for posture in postures if posture == "throughput-first"),
        "warm_daemon_count": sum(1 for posture in postures if posture == "warm-daemon"),
        "event_pipeline_count": sum(1 for posture in postures if posture == "event-pipeline"),
        "consent_bound_async_count": sum(1 for posture in postures if posture == "consent-bound-async"),
        "launch_to_dispatch_count": sum(1 for posture in postures if posture == "launch-to-dispatch"),
        "review_measured_count": sum(1 for posture in postures if posture == "review-measured"),
        "primary_performance_lane_counts": primary_lane_counts,
        "ordered_primary_performance_lane_ids": ordered_lane_ids,
        "ordered_hotspot_ids": ordered_hotspot_ids,
        "review_surface_ids": _dedupe_keep_order(review_surface_ids),
    }


def _promotion_dispatch_budget_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    postures = [str(item.get("dispatch_posture") or "review-budget") for item in rows if isinstance(item, dict)]
    primary_lane_counts: dict[str, int] = {}
    hotspot_counts: dict[str, int] = {}
    review_surface_ids: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        lane_id = str(item.get("primary_dispatch_lane_id") or "").strip()
        if lane_id:
            primary_lane_counts[lane_id] = primary_lane_counts.get(lane_id, 0) + 1
        for hotspot_id in [str(x) for x in list(item.get("performance_hotspot_ids") or []) if str(x)]:
            hotspot_counts[hotspot_id] = hotspot_counts.get(hotspot_id, 0) + 1
        posture = str(item.get("dispatch_posture") or "review-budget")
        if posture in {"daemon-warm", "session-resume", "review-budget"}:
            surface_id = str(item.get("export_surface_id") or "").strip()
            if surface_id:
                review_surface_ids.append(surface_id)
    ordered_lane_ids = [lane_id for lane_id, _count in sorted(primary_lane_counts.items(), key=lambda pair: (-pair[1], pair[0]))]
    ordered_hotspot_ids = [hotspot_id for hotspot_id, _count in sorted(hotspot_counts.items(), key=lambda pair: (-pair[1], pair[0]))]
    return {
        "entry_count": len(rows),
        "edge_resident_count": sum(1 for posture in postures if posture == "edge-resident"),
        "service_resident_count": sum(1 for posture in postures if posture == "service-resident"),
        "daemon_warm_count": sum(1 for posture in postures if posture == "daemon-warm"),
        "session_resume_count": sum(1 for posture in postures if posture == "session-resume"),
        "launch_cold_count": sum(1 for posture in postures if posture == "launch-cold"),
        "review_budget_count": sum(1 for posture in postures if posture == "review-budget"),
        "primary_dispatch_lane_counts": primary_lane_counts,
        "ordered_primary_dispatch_lane_ids": ordered_lane_ids,
        "ordered_hotspot_ids": ordered_hotspot_ids,
        "review_surface_ids": _dedupe_keep_order(review_surface_ids),
    }


def _promotion_claim_review_rows(claim_plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in list(claim_plan.get("recommended_claims") or []):
        if not isinstance(item, dict):
            continue
        current_host_fit = dict(item.get("current_host_fit") or {})
        if not current_host_fit:
            continue
        rows.append(
            {
                "target": str(item.get("target") or ""),
                "title": str(item.get("title") or item.get("target") or "target"),
                "recommended_level": str(item.get("recommended_level") or item.get("claim_level") or "unsupported"),
                "summary": str(item.get("summary") or ""),
                "blocking_capabilities": [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)],
                "required_artifacts": [str(x) for x in list(item.get("required_artifacts") or []) if str(x)],
                "current_host_fit": current_host_fit,
            }
        )
    return rows


def _promotion_claim_witness_contract(claim_plan: dict[str, Any]) -> dict[str, Any]:
    rows = _promotion_claim_review_rows(claim_plan)
    if not rows:
        return {}

    portal_route_contract = dict(claim_plan.get("portal_route_contract") or {})
    host_truth = dict(claim_plan.get("host_truth") or {})
    statuses = [str((item.get("current_host_fit") or {}).get("status") or "unknown") for item in rows]
    strong_rows = [item for item in rows if str(item.get("recommended_level") or "") in {"reference", "supported"}]
    strong_statuses = [str((item.get("current_host_fit") or {}).get("status") or "unknown") for item in strong_rows]

    overall = "pass"
    if any(status == "drifted" for status in strong_statuses):
        overall = "fail"
    elif any(status in {"degraded", "unknown"} for status in strong_statuses):
        overall = "review"
    elif any(status == "drifted" for status in statuses):
        overall = "review"
    elif any(status in {"degraded", "unknown"} for status in statuses):
        overall = "review"

    notes: list[str] = []
    current_desktop = str(portal_route_contract.get("xdg_current_desktop") or "").strip()
    if current_desktop:
        notes.append(f"XDG_CURRENT_DESKTOP is `{current_desktop}` on the current host.")
    portal_status = str(portal_route_contract.get("status") or "unknown")
    if portal_status and portal_status != "unknown":
        notes.append(f"Portal route contract status is `{portal_status}`.")
    strong_drifted = [item for item in strong_rows if str((item.get("current_host_fit") or {}).get("status") or "") == "drifted"]
    strong_review = [item for item in strong_rows if str((item.get("current_host_fit") or {}).get("status") or "") in {"degraded", "unknown"}]
    if strong_drifted:
        notes.append(
            "Current host should not be treated as verified proof for stronger claims: "
            + ", ".join(f"`{item.get('target') or ''}`" for item in strong_drifted[:4])
        )
    elif strong_review:
        notes.append(
            "Current host is only partial or incomplete proof for stronger claims: "
            + ", ".join(f"`{item.get('target') or ''}`" for item in strong_review[:4])
        )

    return {
        "status": overall,
        "reviewed_claim_count": len(rows),
        "strong_claim_count": len(strong_rows),
        "aligned_count": sum(1 for status in statuses if status == "aligned"),
        "degraded_count": sum(1 for status in statuses if status == "degraded"),
        "drifted_count": sum(1 for status in statuses if status == "drifted"),
        "neutral_count": sum(1 for status in statuses if status == "neutral"),
        "unknown_count": sum(1 for status in statuses if status == "unknown"),
        "strong_aligned_count": sum(1 for status in strong_statuses if status == "aligned"),
        "strong_degraded_count": sum(1 for status in strong_statuses if status == "degraded"),
        "strong_drifted_count": sum(1 for status in strong_statuses if status == "drifted"),
        "strong_unknown_count": sum(1 for status in strong_statuses if status == "unknown"),
        "current_desktop": current_desktop,
        "portal_route_status": portal_status,
        "host_truth_status": str(host_truth.get("overall_status") or host_truth.get("status") or "unknown"),
        "review_rows": rows,
        "notes": _dedupe_keep_order(notes),
    }


def _build_claim_witness_gate(contract: dict[str, Any]) -> dict[str, Any]:
    if not contract:
        return {}
    status = str(contract.get("status") or "review")
    rows = [dict(item) for item in list(contract.get("review_rows") or []) if isinstance(item, dict)]
    strong_rows = [item for item in rows if str(item.get("recommended_level") or "") in {"reference", "supported"}]
    blocking_targets = [
        str(item.get("target") or "")
        for item in strong_rows
        if str((item.get("current_host_fit") or {}).get("status") or "") == "drifted" and str(item.get("target") or "")
    ]
    review_targets = [
        str(item.get("target") or "")
        for item in strong_rows
        if str((item.get("current_host_fit") or {}).get("status") or "") in {"degraded", "unknown"} and str(item.get("target") or "")
    ]
    if status == "fail":
        summary = "The current host drifts from at least one stronger support claim and should not be treated as verified release proof."
    elif status == "review":
        summary = "Current-host proof still needs review before stronger Linux support claims are promoted from this machine."
    else:
        summary = "Current-host witness posture looks aligned enough that stronger claim work can use this machine as one credible proof source."
    commands = [
        "vhk gen-claim-pack . --force --quiet",
        "vhk audit-target-claims .",
        "vhk gen-host-contract-pack . --force --quiet",
    ]
    return {
        "gate_id": "current-host-proof-gate",
        "title": "Current-host proof gate",
        "status": status,
        "summary": summary,
        "rationale": "Linux automation proof is target-lane specific, so a session on the wrong desktop should not silently become verified support evidence for portal-first or compositor-specific claims.",
        "surface_count": 0,
        "affected_surfaces": [],
        "ready_surfaces": [],
        "review_surfaces": review_targets,
        "blocking_surfaces": blocking_targets,
        "commands": commands,
        "wave_ids": [],
        "claim_targets": [str(item.get("target") or "") for item in rows if str(item.get("target") or "")],
    }


def _build_claim_witness_backlog_item(contract: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    if not contract or not gate:
        return {}
    status = str(gate.get("status") or "review")
    if status == "pass":
        return {}
    queue_state = "blocked" if status == "fail" else "review"
    priority = "high" if status == "fail" else "medium"
    next_action = "Refresh claim docs and collect proof on the matching desktop lane before treating this host run as verified evidence."
    if status == "review":
        next_action = "Refresh claim docs and record whether this host is only partial proof or whether stronger claims need a better evidence host."
    return {
        "task_id": "gate:current-host-proof-gate",
        "title": "Resolve current-host proof posture",
        "queue_state": queue_state,
        "kind": "gate-review",
        "priority": priority,
        "wave_id": "",
        "wave_title": "",
        "export_surface_id": "",
        "gate_id": "current-host-proof-gate",
        "rationale": str(gate.get("rationale") or ""),
        "next_action": next_action,
        "blockers": [str(x) for x in list(gate.get("blocking_surfaces") or []) if str(x)],
        "review_notes": [str(x) for x in list(contract.get("notes") or []) if str(x)][:6],
        "commands": [str(x) for x in list(gate.get("commands") or []) if str(x)],
        "required_capabilities": [],
        "related_routes": [],
    }


def _build_claim_witness_evidence_entry(project_dir: Path, contract: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    if not contract or not gate:
        return {}
    required_artifacts = [
        "docs/VHK_CLAIM_GUIDE.md",
        "docs/VHK_TARGET_CLAIMS.yaml",
        "docs/VHK_HOST_REQUIREMENTS.md",
        "docs/VHK_READINESS_REPORT.md",
    ]
    present = [path for path in required_artifacts if (project_dir / path).exists()]
    missing = [path for path in required_artifacts if path not in present]
    status = "complete" if not missing else ("partial" if present else "missing")
    return {
        "evidence_id": "gate:current-host-proof-gate",
        "title": "Current-host proof gate evidence",
        "subject_kind": "gate",
        "subject_id": "current-host-proof-gate",
        "posture": str(gate.get("status") or "review"),
        "evidence_status": status,
        "required_artifacts": required_artifacts,
        "present_artifacts": present,
        "missing_artifacts": missing,
        "required_count": len(required_artifacts),
        "present_count": len(present),
        "missing_count": len(missing),
        "rationale": "Promotion review should keep wrong-host proof visible, not only claim wording, so release pressure does not outrun target-specific evidence.",
        "commands": [str(x) for x in list(gate.get("commands") or []) if str(x)],
        "blockers": [str(x) for x in list(gate.get("blocking_surfaces") or []) if str(x)],
        "review_notes": [str(x) for x in list(contract.get("notes") or []) if str(x)][:6],
    }
def build_promotion_pack_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Any]:
    project = load_project(project_dir)
    plan = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    promotion_plan = [dict(item) for item in list(plan.get("export_promotion_plan") or []) if isinstance(item, dict)]
    promotion_input_lanes = [dict(item) for item in list(plan.get("promotion_input_lane_plan") or []) if isinstance(item, dict)]
    promotion_input_lane_summary = _promotion_input_lane_summary(promotion_input_lanes)
    promotion_activation_routes = [dict(item) for item in list(plan.get("promotion_activation_route_plan") or []) if isinstance(item, dict)]
    promotion_activation_route_summary = _promotion_activation_route_summary(promotion_activation_routes)
    promotion_operator_controls = [dict(item) for item in list(plan.get("promotion_operator_control_plan") or []) if isinstance(item, dict)]
    promotion_operator_control_summary = _promotion_operator_control_summary(promotion_operator_controls)
    promotion_recovery_plan = [dict(item) for item in list(plan.get("promotion_recovery_plan") or []) if isinstance(item, dict)]
    promotion_recovery_summary = _promotion_recovery_summary(promotion_recovery_plan)
    promotion_verification_plan = [dict(item) for item in list(plan.get("promotion_verification_plan") or []) if isinstance(item, dict)]
    promotion_verification_summary = _promotion_verification_summary(promotion_verification_plan)
    promotion_performance_plan = [dict(item) for item in list(plan.get("promotion_performance_plan") or []) if isinstance(item, dict)]
    promotion_performance_summary = _promotion_performance_summary(promotion_performance_plan)
    promotion_dispatch_budget_plan = [dict(item) for item in list(plan.get("promotion_dispatch_budget_plan") or []) if isinstance(item, dict)]
    promotion_dispatch_budget_summary = _promotion_dispatch_budget_summary(promotion_dispatch_budget_plan)
    promotion_authority_envelope_plan = [dict(item) for item in list(plan.get("promotion_authority_envelope_plan") or []) if isinstance(item, dict)]
    promotion_authority_envelope_summary = dict(plan.get("promotion_authority_envelope_summary") or {})
    route_portfolio = [dict(item) for item in list(plan.get("route_portfolio") or []) if isinstance(item, dict)]
    promotion_waves = [dict(item) for item in list(plan.get("promotion_waves") or []) if isinstance(item, dict)]
    promotion_readiness = [dict(item) for item in list(plan.get("promotion_readiness") or []) if isinstance(item, dict)]
    readiness_summary = dict(plan.get("promotion_readiness_summary") or {})
    promotion_gates = [dict(item) for item in list(plan.get("promotion_gates") or []) if isinstance(item, dict)]
    gate_summary = dict(plan.get("promotion_gate_summary") or {})
    promotion_backlog = [dict(item) for item in list(plan.get("promotion_backlog") or []) if isinstance(item, dict)]
    backlog_summary = dict(plan.get("promotion_backlog_summary") or {})
    promotion_evidence = [dict(item) for item in list(plan.get("promotion_evidence") or []) if isinstance(item, dict)]
    evidence_summary = dict(plan.get("promotion_evidence_summary") or {})

    claim_plan = build_claim_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane_profile,
    )
    promotion_claim_witness = _promotion_claim_witness_contract(claim_plan)
    promotion_claim_review_rows = [dict(item) for item in list(promotion_claim_witness.get("review_rows") or []) if isinstance(item, dict)]
    host_truth = dict(claim_plan.get("host_truth") or {})
    portal_route_contract = dict(claim_plan.get("portal_route_contract") or {})

    witness_gate = _build_claim_witness_gate(promotion_claim_witness)
    if witness_gate and not any(str(item.get("gate_id") or "") == str(witness_gate.get("gate_id") or "") for item in promotion_gates):
        promotion_gates.append(witness_gate)
    witness_task = _build_claim_witness_backlog_item(promotion_claim_witness, witness_gate)
    if witness_task and not any(str(item.get("task_id") or "") == str(witness_task.get("task_id") or "") for item in promotion_backlog):
        promotion_backlog.append(witness_task)
    witness_evidence = _build_claim_witness_evidence_entry(project_dir, promotion_claim_witness, witness_gate)
    if witness_evidence and not any(str(item.get("evidence_id") or "") == str(witness_evidence.get("evidence_id") or "") for item in promotion_evidence):
        promotion_evidence.append(witness_evidence)

    gate_rank = {"fail": 0, "review": 1, "pass": 2}
    promotion_gates.sort(key=lambda item: (gate_rank.get(str(item.get("status") or "review"), 9), str(item.get("title") or "")))
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    queue_rank = {"blocked": 0, "review": 1, "todo": 2, "done": 3}
    promotion_backlog.sort(key=lambda item: (queue_rank.get(str(item.get("queue_state") or "review"), 9), priority_rank.get(str(item.get("priority") or "medium"), 9), str(item.get("title") or "")))
    evidence_rank = {"missing": 0, "partial": 1, "complete": 2}
    promotion_evidence.sort(key=lambda item: (evidence_rank.get(str(item.get("evidence_status") or "partial"), 9), str(item.get("subject_kind") or ""), str(item.get("title") or "")))
    gate_summary = _promotion_gate_summary(promotion_gates)
    backlog_summary = _promotion_backlog_summary(promotion_backlog)
    evidence_summary = _promotion_evidence_summary(promotion_evidence)

    summary = {
        "surface_count": len(promotion_plan),
        "route_count": len(route_portfolio),
        "wave_count": len(promotion_waves),
        "shipping_lane_count": len(promotion_input_lanes),
        "flagship_shipping_lane_count": int(promotion_input_lane_summary.get("flagship_count") or 0),
        "specialist_shipping_lane_count": int(promotion_input_lane_summary.get("specialist_count") or 0),
        "reviewed_shipping_lane_count": int(promotion_input_lane_summary.get("reviewed_count") or 0),
        "orthogonal_shipping_lane_count": int(promotion_input_lane_summary.get("orthogonal_count") or 0),
        "activation_route_count": len(promotion_activation_routes),
        "operator_control_count": len(promotion_operator_controls),
        "recovery_lane_count": len(promotion_recovery_plan),
        "verification_lane_count": len(promotion_verification_plan),
        "performance_lane_count": len(promotion_performance_plan),
        "dispatch_budget_count": len(promotion_dispatch_budget_plan),
        "authority_envelope_count": len(promotion_authority_envelope_plan),
        "resident_activation_route_count": int(promotion_activation_route_summary.get("resident_count") or 0),
        "session_bound_activation_route_count": int(promotion_activation_route_summary.get("session_bound_count") or 0),
        "launcher_first_activation_route_count": int(promotion_activation_route_summary.get("launcher_first_count") or 0),
        "reviewed_activation_route_count": int(promotion_activation_route_summary.get("reviewed_count") or 0),
        "service_managed_control_count": int(promotion_operator_control_summary.get("service_managed_count") or 0),
        "session_managed_control_count": int(promotion_operator_control_summary.get("session_managed_count") or 0),
        "daemon_reviewed_control_count": int(promotion_operator_control_summary.get("daemon_reviewed_count") or 0),
        "manual_entry_control_count": int(promotion_operator_control_summary.get("manual_entry_count") or 0),
        "rollback_first_recovery_count": int(promotion_recovery_summary.get("rollback_first_count") or 0),
        "session_recreate_recovery_count": int(promotion_recovery_summary.get("session_recreate_count") or 0),
        "daemon_reset_recovery_count": int(promotion_recovery_summary.get("daemon_reset_count") or 0),
        "service_restart_recovery_count": int(promotion_recovery_summary.get("service_restart_count") or 0),
        "reload_and_smoke_recovery_count": int(promotion_recovery_summary.get("reload_and_smoke_count") or 0),
        "manual_smoke_recovery_count": int(promotion_recovery_summary.get("manual_smoke_count") or 0),
        "service_smoke_verification_count": int(promotion_verification_summary.get("service_smoke_count") or 0),
        "input_event_smoke_verification_count": int(promotion_verification_summary.get("input_event_smoke_count") or 0),
        "portal_proof_verification_count": int(promotion_verification_summary.get("portal_proof_count") or 0),
        "daemon_proof_verification_count": int(promotion_verification_summary.get("daemon_proof_count") or 0),
        "event_flow_smoke_verification_count": int(promotion_verification_summary.get("event_flow_smoke_count") or 0),
        "launch_smoke_verification_count": int(promotion_verification_summary.get("launch_smoke_count") or 0),
        "low_latency_edge_performance_count": int(promotion_performance_summary.get("low_latency_edge_count") or 0),
        "throughput_first_performance_count": int(promotion_performance_summary.get("throughput_first_count") or 0),
        "warm_daemon_performance_count": int(promotion_performance_summary.get("warm_daemon_count") or 0),
        "event_pipeline_performance_count": int(promotion_performance_summary.get("event_pipeline_count") or 0),
        "consent_bound_async_performance_count": int(promotion_performance_summary.get("consent_bound_async_count") or 0),
        "launch_to_dispatch_performance_count": int(promotion_performance_summary.get("launch_to_dispatch_count") or 0),
        "edge_resident_dispatch_count": int(promotion_dispatch_budget_summary.get("edge_resident_count") or 0),
        "service_resident_dispatch_count": int(promotion_dispatch_budget_summary.get("service_resident_count") or 0),
        "daemon_warm_dispatch_count": int(promotion_dispatch_budget_summary.get("daemon_warm_count") or 0),
        "session_resume_dispatch_count": int(promotion_dispatch_budget_summary.get("session_resume_count") or 0),
        "launch_cold_dispatch_count": int(promotion_dispatch_budget_summary.get("launch_cold_count") or 0),
        "input_edge_privileged_authority_count": int(promotion_authority_envelope_summary.get("input_edge_privileged_count") or 0),
        "desktop_mediated_authority_count": int(promotion_authority_envelope_summary.get("desktop_mediated_count") or 0),
        "helper_daemon_privileged_authority_count": int(promotion_authority_envelope_summary.get("helper_daemon_privileged_count") or 0),
        "session_userland_authority_count": int(promotion_authority_envelope_summary.get("session_userland_count") or 0),
        "launch_userland_authority_count": int(promotion_authority_envelope_summary.get("launch_userland_count") or 0),
        "high_priority_surface_count": sum(1 for item in promotion_plan if str(item.get("priority") or "") == "high"),
        "conditional_surface_count": sum(1 for item in promotion_plan if str(item.get("dominant_fit") or "") in {"conditional", "weak"}),
        "helper_sensitive_surface_count": sum(1 for item in promotion_plan if str(item.get("export_surface_id") or "") == "helper-route-dossier"),
        "macro_count": sum(int(item.get("macro_count") or 0) for item in promotion_plan),
        "top_surface_ids": [str(item.get("export_surface_id") or "") for item in promotion_plan[:4] if str(item.get("export_surface_id") or "")],
        "ready_surface_count": int(readiness_summary.get("ready_count") or 0),
        "review_surface_count": int(readiness_summary.get("review_count") or 0),
        "blocked_surface_count": int(readiness_summary.get("blocked_count") or 0),
        "gate_count": len(promotion_gates),
        "failing_gate_count": int(gate_summary.get("fail_count") or 0),
        "review_gate_count": int(gate_summary.get("review_count") or 0),
        "backlog_task_count": int(backlog_summary.get("task_count") or 0),
        "blocked_backlog_count": int(backlog_summary.get("blocked_count") or 0),
        "review_backlog_count": int(backlog_summary.get("review_count") or 0),
        "evidence_entry_count": int(evidence_summary.get("entry_count") or 0),
        "complete_evidence_count": int(evidence_summary.get("complete_count") or 0),
        "partial_evidence_count": int(evidence_summary.get("partial_count") or 0),
        "missing_evidence_count": int(evidence_summary.get("missing_count") or 0),
        "current_host_proof_status": str(promotion_claim_witness.get("status") or "unknown"),
        "current_host_proof_claim_count": int(promotion_claim_witness.get("reviewed_claim_count") or 0),
        "selected_evidence_lane_id": str((claim_plan.get("selected_evidence_lane") or {}).get("profile_id") or ""),
        "selected_evidence_lane_fit_status": str((claim_plan.get("evidence_lane_fit") or {}).get("status") or "unknown"),
        "primary_shipping_lane_ids": [str(x) for x in list(promotion_input_lane_summary.get("ordered_primary_lane_ids") or []) if str(x)],
        "primary_activation_route_ids": [str(x) for x in list(promotion_activation_route_summary.get("ordered_primary_route_ids") or []) if str(x)],
        "primary_operator_control_lane_ids": [str(x) for x in list(promotion_operator_control_summary.get("ordered_primary_control_lane_ids") or []) if str(x)],
        "primary_recovery_lane_ids": [str(x) for x in list(promotion_recovery_summary.get("ordered_primary_recovery_lane_ids") or []) if str(x)],
        "primary_verification_lane_ids": [str(x) for x in list(promotion_verification_summary.get("ordered_primary_verification_lane_ids") or []) if str(x)],
        "primary_performance_lane_ids": [str(x) for x in list(promotion_performance_summary.get("ordered_primary_performance_lane_ids") or []) if str(x)],
        "primary_dispatch_budget_lane_ids": [str(x) for x in list(promotion_dispatch_budget_summary.get("ordered_primary_dispatch_lane_ids") or []) if str(x)],
        "primary_authority_lane_ids": [str(x) for x in list(promotion_authority_envelope_summary.get("ordered_primary_authority_lane_ids") or []) if str(x)],
        "top_performance_hotspot_ids": [str(x) for x in list(promotion_performance_summary.get("ordered_hotspot_ids") or []) if str(x)],
    }

    review_commands = _dedupe_keep_order(
        [
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-promotion-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-design-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-route-selection-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-setup-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-claim-pack {project_dir.as_posix()} --force --quiet",
            f"vhk audit-target-claims {project_dir.as_posix()}",
            *[
                str(cmd)
                for item in promotion_plan
                for cmd in list(item.get("commands") or [])
                if str(cmd)
            ],
            *[
                str(cmd)
                for item in promotion_input_lanes
                for cmd in list(item.get("commands") or [])
                if str(cmd)
            ],
            *[
                str(cmd)
                for item in promotion_activation_routes
                for cmd in list(item.get("commands") or [])
                if str(cmd)
            ],
            *[
                str(cmd)
                for item in promotion_operator_controls
                for cmd in list(item.get("commands") or [])
                if str(cmd)
            ],
            *[
                str(cmd)
                for item in promotion_recovery_plan
                for cmd in list(item.get("commands") or [])
                if str(cmd)
            ],
            *[
                str(cmd)
                for item in promotion_verification_plan
                for cmd in list(item.get("commands") or [])
                if str(cmd)
            ],
            *[
                str(cmd)
                for item in promotion_performance_plan
                for cmd in list(item.get("commands") or [])
                if str(cmd)
            ],
        ]
    )

    return {
        "source_contract": "promotion_pack",
        **plan,
        "promotion_summary": summary,
        "promotion_input_lane_plan": promotion_input_lanes,
        "promotion_input_lane_summary": promotion_input_lane_summary,
        "promotion_activation_route_plan": promotion_activation_routes,
        "promotion_activation_route_summary": promotion_activation_route_summary,
        "promotion_operator_control_plan": promotion_operator_controls,
        "promotion_operator_control_summary": promotion_operator_control_summary,
        "promotion_recovery_plan": promotion_recovery_plan,
        "promotion_recovery_summary": promotion_recovery_summary,
        "promotion_verification_plan": promotion_verification_plan,
        "promotion_verification_summary": promotion_verification_summary,
        "promotion_performance_plan": promotion_performance_plan,
        "promotion_performance_summary": promotion_performance_summary,
        "promotion_dispatch_budget_plan": promotion_dispatch_budget_plan,
        "promotion_dispatch_budget_summary": promotion_dispatch_budget_summary,
        "promotion_authority_envelope_plan": promotion_authority_envelope_plan,
        "promotion_authority_envelope_summary": promotion_authority_envelope_summary,
        "host_truth": host_truth,
        "portal_route_contract": portal_route_contract,
        "promotion_claim_witness": {key: value for key, value in promotion_claim_witness.items() if key != "review_rows"},
        "promotion_claim_review_rows": promotion_claim_review_rows,
        "selected_evidence_lane": dict(claim_plan.get("selected_evidence_lane") or {}),
        "evidence_lane_fit": dict(claim_plan.get("evidence_lane_fit") or {}),
        "promotion_gates": promotion_gates,
        "promotion_gate_summary": gate_summary,
        "promotion_backlog": promotion_backlog,
        "promotion_backlog_summary": backlog_summary,
        "promotion_evidence": promotion_evidence,
        "promotion_evidence_summary": evidence_summary,
        "review_commands": review_commands,
    }


def render_promotion_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("promotion_summary") or {})
    route_portfolio = _trim_items(plan.get("route_portfolio"), limit=8)
    promotion_plan = _trim_items(plan.get("export_promotion_plan"), limit=10)
    promotion_input_lanes = _trim_items(plan.get("promotion_input_lane_plan"), limit=10)
    promotion_input_lane_summary = dict(plan.get("promotion_input_lane_summary") or {})
    promotion_activation_routes = _trim_items(plan.get("promotion_activation_route_plan"), limit=10)
    promotion_activation_route_summary = dict(plan.get("promotion_activation_route_summary") or {})
    promotion_operator_controls = _trim_items(plan.get("promotion_operator_control_plan"), limit=10)
    promotion_operator_control_summary = dict(plan.get("promotion_operator_control_summary") or {})
    promotion_recovery_plan = _trim_items(plan.get("promotion_recovery_plan"), limit=10)
    promotion_recovery_summary = dict(plan.get("promotion_recovery_summary") or {})
    promotion_verification_plan = _trim_items(plan.get("promotion_verification_plan"), limit=10)
    promotion_verification_summary = dict(plan.get("promotion_verification_summary") or {})
    promotion_performance_plan = _trim_items(plan.get("promotion_performance_plan"), limit=10)
    promotion_performance_summary = dict(plan.get("promotion_performance_summary") or {})
    promotion_dispatch_budget_plan = _trim_items(plan.get("promotion_dispatch_budget_plan"), limit=10)
    promotion_dispatch_budget_summary = dict(plan.get("promotion_dispatch_budget_summary") or {})
    promotion_authority_envelope_plan = _trim_items(plan.get("promotion_authority_envelope_plan"), limit=10)
    promotion_authority_envelope_summary = dict(plan.get("promotion_authority_envelope_summary") or {})
    promotion_waves = _trim_items(plan.get("promotion_waves"), limit=6)
    promotion_readiness = _trim_items(plan.get("promotion_readiness"), limit=10)
    readiness_summary = dict(plan.get("promotion_readiness_summary") or {})
    promotion_gates = _trim_items(plan.get("promotion_gates"), limit=8)
    gate_summary = dict(plan.get("promotion_gate_summary") or {})
    promotion_backlog = _trim_items(plan.get("promotion_backlog"), limit=12)
    backlog_summary = dict(plan.get("promotion_backlog_summary") or {})
    promotion_evidence = _trim_items(plan.get("promotion_evidence"), limit=12)
    evidence_summary = dict(plan.get("promotion_evidence_summary") or {})
    host_truth = dict(plan.get("host_truth") or {})
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    promotion_claim_witness = dict(plan.get("promotion_claim_witness") or {})
    promotion_claim_review_rows = _trim_items(plan.get("promotion_claim_review_rows"), limit=8)
    selected_evidence_lane = dict(plan.get("selected_evidence_lane") or {})
    evidence_lane_fit = dict(plan.get("evidence_lane_fit") or {})

    lines: list[str] = []
    lines.append(f"# VHK promotion plan for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-promotion-pack`. This pack turns project-level route ownership into staged Linux-native shipping work instead of leaving promotions as repeated macro-by-macro advice.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Promotion surfaces: {int(summary.get('surface_count') or 0)}")
    lines.append(f"- Promotion waves: {int(summary.get('wave_count') or 0)}")
    lines.append(f"- Shipping lanes (flagship/specialist/reviewed/orthogonal): {int(promotion_input_lane_summary.get('flagship_count') or 0)}/{int(promotion_input_lane_summary.get('specialist_count') or 0)}/{int(promotion_input_lane_summary.get('reviewed_count') or 0)}/{int(promotion_input_lane_summary.get('orthogonal_count') or 0)}")
    lines.append(f"- Startup routes (resident/session-bound/launcher-first/reviewed/orthogonal): {int(promotion_activation_route_summary.get('resident_count') or 0)}/{int(promotion_activation_route_summary.get('session_bound_count') or 0)}/{int(promotion_activation_route_summary.get('launcher_first_count') or 0)}/{int(promotion_activation_route_summary.get('reviewed_count') or 0)}/{int(promotion_activation_route_summary.get('orthogonal_count') or 0)}")
    lines.append(f"- Operator controls (service-managed/session-managed/daemon-reviewed/manual-entry/reviewed): {int(promotion_operator_control_summary.get('service_managed_count') or 0)}/{int(promotion_operator_control_summary.get('session_managed_count') or 0)}/{int(promotion_operator_control_summary.get('daemon_reviewed_count') or 0)}/{int(promotion_operator_control_summary.get('manual_entry_count') or 0)}/{int(promotion_operator_control_summary.get('reviewed_count') or 0)}")
    lines.append(f"- Recovery lanes (rollback-first/session-recreate/daemon-reset/service-restart/reload-and-smoke/manual-smoke): {int(promotion_recovery_summary.get('rollback_first_count') or 0)}/{int(promotion_recovery_summary.get('session_recreate_count') or 0)}/{int(promotion_recovery_summary.get('daemon_reset_count') or 0)}/{int(promotion_recovery_summary.get('service_restart_count') or 0)}/{int(promotion_recovery_summary.get('reload_and_smoke_count') or 0)}/{int(promotion_recovery_summary.get('manual_smoke_count') or 0)}")
    lines.append(f"- Verification lanes (service/input-event/portal/daemon/event-flow/launch): {int(promotion_verification_summary.get('service_smoke_count') or 0)}/{int(promotion_verification_summary.get('input_event_smoke_count') or 0)}/{int(promotion_verification_summary.get('portal_proof_count') or 0)}/{int(promotion_verification_summary.get('daemon_proof_count') or 0)}/{int(promotion_verification_summary.get('event_flow_smoke_count') or 0)}/{int(promotion_verification_summary.get('launch_smoke_count') or 0)}")
    lines.append(f"- Performance envelopes (low-latency/throughput/warm-daemon/event-pipeline/consent-bound/launch): {int(promotion_performance_summary.get('low_latency_edge_count') or 0)}/{int(promotion_performance_summary.get('throughput_first_count') or 0)}/{int(promotion_performance_summary.get('warm_daemon_count') or 0)}/{int(promotion_performance_summary.get('event_pipeline_count') or 0)}/{int(promotion_performance_summary.get('consent_bound_async_count') or 0)}/{int(promotion_performance_summary.get('launch_to_dispatch_count') or 0)}")
    lines.append(f"- Dispatch budgets (edge/service/daemon/session/launch): {int(promotion_dispatch_budget_summary.get('edge_resident_count') or 0)}/{int(promotion_dispatch_budget_summary.get('service_resident_count') or 0)}/{int(promotion_dispatch_budget_summary.get('daemon_warm_count') or 0)}/{int(promotion_dispatch_budget_summary.get('session_resume_count') or 0)}/{int(promotion_dispatch_budget_summary.get('launch_cold_count') or 0)}")
    lines.append(f"- Authority envelopes (edge/desktop/helper/session/launch): {int(promotion_authority_envelope_summary.get('input_edge_privileged_count') or 0)}/{int(promotion_authority_envelope_summary.get('desktop_mediated_count') or 0)}/{int(promotion_authority_envelope_summary.get('helper_daemon_privileged_count') or 0)}/{int(promotion_authority_envelope_summary.get('session_userland_count') or 0)}/{int(promotion_authority_envelope_summary.get('launch_userland_count') or 0)}")
    lines.append(f"- High-priority surfaces: {int(summary.get('high_priority_surface_count') or 0)}")
    lines.append(f"- Conditional/helper-sensitive surfaces: {int(summary.get('conditional_surface_count') or 0) + int(summary.get('helper_sensitive_surface_count') or 0)}")
    lines.append(f"- Macros covered by promotion plan: {int(summary.get('macro_count') or 0)}")
    lines.append(f"- Ready/review/blocked surfaces: {int(summary.get('ready_surface_count') or 0)}/{int(summary.get('review_surface_count') or 0)}/{int(summary.get('blocked_surface_count') or 0)}")
    lines.append(f"- Promotion gates (pass/review/fail): {int(gate_summary.get('pass_count') or 0)}/{int(gate_summary.get('review_count') or 0)}/{int(gate_summary.get('fail_count') or 0)}")
    lines.append(f"- Promotion backlog (blocked/review/todo): {int(backlog_summary.get('blocked_count') or 0)}/{int(backlog_summary.get('review_count') or 0)}/{int(backlog_summary.get('todo_count') or 0)}")
    lines.append(f"- Promotion evidence (complete/partial/missing): {int(evidence_summary.get('complete_count') or 0)}/{int(evidence_summary.get('partial_count') or 0)}/{int(evidence_summary.get('missing_count') or 0)}")
    if promotion_claim_witness:
        lines.append(f"- Current-host proof gate: `{promotion_claim_witness.get('status') or 'unknown'}` across {int(promotion_claim_witness.get('reviewed_claim_count') or 0)} reviewed claim(s)")
    lines.append("")

    if promotion_claim_witness or promotion_claim_review_rows or host_truth or portal_route_contract or evidence_lane_fit:
        lines.append("## Current host claim witness")
        lines.append("")
        if host_truth or portal_route_contract:
            lines.append(f"- Host truth status: `{host_truth.get('overall_status') or host_truth.get('status') or 'unknown'}`")
            lines.append(f"- Portal route status: `{portal_route_contract.get('status') or 'unknown'}`")
            if portal_route_contract.get('xdg_current_desktop'):
                lines.append(f"- XDG_CURRENT_DESKTOP: `{portal_route_contract.get('xdg_current_desktop')}`")
        if promotion_claim_witness:
            lines.append(f"- Proof posture: `{promotion_claim_witness.get('status') or 'unknown'}`")
            lines.append(f"- Strong claims aligned/degraded/drifted/unknown: {int(promotion_claim_witness.get('strong_aligned_count') or 0)}/{int(promotion_claim_witness.get('strong_degraded_count') or 0)}/{int(promotion_claim_witness.get('strong_drifted_count') or 0)}/{int(promotion_claim_witness.get('strong_unknown_count') or 0)}")
            notes = [str(x) for x in list(promotion_claim_witness.get('notes') or []) if str(x)]
            if notes:
                lines.append(f"- Witness notes: {'; '.join(notes[:4])}")
        if selected_evidence_lane or evidence_lane_fit:
            lines.append(f"- Selected evidence lane: `{selected_evidence_lane.get('profile_id') or evidence_lane_fit.get('profile_id') or 'unknown'}` ({selected_evidence_lane.get('title') or evidence_lane_fit.get('profile_title') or 'target'})")
            lines.append(f"- Evidence lane fit: `{evidence_lane_fit.get('status') or 'unknown'}` · source `{evidence_lane_fit.get('selection_source') or 'flagship-default'}`")
            lines.append(f"- Evidence lane requirements (aligned/degraded/drifted/ahead/outside-profile/unknown): {len(evidence_lane_fit.get('aligned_requirement_ids') or [])}/{len(evidence_lane_fit.get('degraded_requirement_ids') or [])}/{len(evidence_lane_fit.get('drifted_requirement_ids') or [])}/{len(evidence_lane_fit.get('ahead_requirement_ids') or [])}/{len(evidence_lane_fit.get('outside_profile_requirement_ids') or [])}/{len(evidence_lane_fit.get('unknown_requirement_ids') or [])}")
        lines.append("")
        for item in promotion_claim_review_rows:
            current_host_fit = dict(item.get('current_host_fit') or {})
            lines.append(f"- `{item.get('target') or ''}` (`{item.get('recommended_level') or 'unsupported'}`) → host `{current_host_fit.get('status') or 'unknown'}`")
        if promotion_claim_review_rows:
            lines.append("")

    if route_portfolio:
        lines.append("## Route portfolio")
        lines.append("")
        for item in route_portfolio:
            lines.append(f"- `{item.get('route_id') or ''}` — {item.get('macro_count') or 0} macro(s), dominant fit `{item.get('dominant_fit') or 'good'}`")
        lines.append("")

    if promotion_input_lanes:
        lines.append("## Promotion shipping lanes")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_input_lane_summary.get('entry_count') or 0)}")
        primary_lane_ids = [str(x) for x in list(promotion_input_lane_summary.get('ordered_primary_lane_ids') or []) if str(x)]
        if primary_lane_ids:
            lines.append(f"- Dominant primary lanes: {', '.join(f'`{lane_id}`' for lane_id in primary_lane_ids[:5])}")
        review_surface_ids = [str(x) for x in list(promotion_input_lane_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Review-led surfaces: {', '.join(f'`{surface_id}`' for surface_id in review_surface_ids[:6])}")
        lines.append("")
        for item in promotion_input_lanes:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Shipping posture: `{item.get('shipping_posture') or 'reviewed'}`")
            if item.get('primary_input_lane_id'):
                lines.append(f"- Primary input lane: `{item.get('primary_input_lane_id')}` ({item.get('primary_input_lane_fit') or 'unknown'})")
            alternate_ids = [str(x) for x in list(item.get('alternate_input_lane_ids') or []) if str(x)]
            if alternate_ids:
                lines.append(f"- Alternate lanes: {', '.join(f'`{lane_id}`' for lane_id in alternate_ids[:4])}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: {', '.join(f'`{req}`' for req in host_requirement_ids[:5])}")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append(f"- Cautions: {'; '.join(cautions[:3])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{cmd}`' for cmd in commands[:4])}")
            lines.append("")

    if promotion_activation_routes:
        lines.append("## Promotion startup routes")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_activation_route_summary.get('entry_count') or 0)}")
        primary_route_ids = [str(x) for x in list(promotion_activation_route_summary.get('ordered_primary_route_ids') or []) if str(x)]
        if primary_route_ids:
            lines.append(f"- Dominant primary routes: {', '.join(f'`{route_id}`' for route_id in primary_route_ids[:5])}")
        review_surface_ids = [str(x) for x in list(promotion_activation_route_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Review-led/session-bound surfaces: {', '.join(f'`{surface_id}`' for surface_id in review_surface_ids[:6])}")
        lines.append("")
        for item in promotion_activation_routes:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Startup posture: `{item.get('startup_posture') or 'reviewed'}`")
            if item.get('primary_activation_route_id'):
                lines.append(f"- Primary activation route: `{item.get('primary_activation_route_id')}` (`{item.get('primary_activation_kind') or 'unknown'}` · `{item.get('primary_activation_fit') or 'unknown'}`)")
            if item.get('startup_owner'):
                lines.append(f"- Startup owner: {item.get('startup_owner')}")
            if item.get('steady_state'):
                lines.append(f"- Steady state: {item.get('steady_state')}")
            if item.get('entrypoint'):
                lines.append(f"- Entrypoint: `{item.get('entrypoint')}`")
            alternate_ids = [str(x) for x in list(item.get('alternate_activation_route_ids') or []) if str(x)]
            if alternate_ids:
                lines.append(f"- Alternate routes: {', '.join(f'`{route_id}`' for route_id in alternate_ids[:4])}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: {', '.join(f'`{req}`' for req in host_requirement_ids[:5])}")
            alt_group_ids = [str(x) for x in list(item.get('alternative_requirement_group_ids') or []) if str(x)]
            if alt_group_ids:
                lines.append(f"- Alternative requirement groups: {', '.join(f'`{group_id}`' for group_id in alt_group_ids[:4])}")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append(f"- Cautions: {'; '.join(cautions[:3])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{cmd}`' for cmd in commands[:4])}")
            lines.append("")

    if promotion_operator_controls:
        lines.append("## Promotion operator controls")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_operator_control_summary.get('entry_count') or 0)}")
        primary_control_lane_ids = [str(x) for x in list(promotion_operator_control_summary.get('ordered_primary_control_lane_ids') or []) if str(x)]
        if primary_control_lane_ids:
            lines.append(f"- Dominant control lanes: {', '.join(f'`{lane_id}`' for lane_id in primary_control_lane_ids[:5])}")
        review_surface_ids = [str(x) for x in list(promotion_operator_control_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Review-led/session-led surfaces: {', '.join(f'`{surface_id}`' for surface_id in review_surface_ids[:6])}")
        lines.append("")
        for item in promotion_operator_controls:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Control posture: `{item.get('control_posture') or 'reviewed'}`")
            if item.get('primary_control_lane_id'):
                lines.append(f"- Primary control lane: `{item.get('primary_control_lane_id')}`")
            if item.get('operator_owner'):
                lines.append(f"- Operator owner: {item.get('operator_owner')}")
            if item.get('status_surface'):
                lines.append(f"- Status surface: {item.get('status_surface')}")
            if item.get('reload_surface'):
                lines.append(f"- Reload surface: {item.get('reload_surface')}")
            if item.get('log_surface'):
                lines.append(f"- Log surface: {item.get('log_surface')}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: {', '.join(f'`{req}`' for req in host_requirement_ids[:5])}")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append(f"- Cautions: {'; '.join(cautions[:3])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{cmd}`' for cmd in commands[:4])}")
            lines.append("")

    if promotion_recovery_plan:
        lines.append("## Promotion recovery lanes")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_recovery_summary.get('entry_count') or 0)}")
        primary_recovery_lane_ids = [str(x) for x in list(promotion_recovery_summary.get('ordered_primary_recovery_lane_ids') or []) if str(x)]
        if primary_recovery_lane_ids:
            lines.append(f"- Dominant recovery lanes: {', '.join(f'`{lane_id}`' for lane_id in primary_recovery_lane_ids[:5])}")
        review_surface_ids = [str(x) for x in list(promotion_recovery_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Review-led/recovery-sensitive surfaces: {', '.join(f'`{surface_id}`' for surface_id in review_surface_ids[:6])}")
        lines.append("")
        for item in promotion_recovery_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Recovery posture: `{item.get('recovery_posture') or 'review-led'}`")
            if item.get('primary_recovery_lane_id'):
                lines.append(f"- Primary recovery lane: `{item.get('primary_recovery_lane_id')}`")
            if item.get('failure_boundary'):
                lines.append(f"- Failure boundary: {item.get('failure_boundary')}")
            if item.get('first_response'):
                lines.append(f"- First response: {item.get('first_response')}")
            if item.get('rollback_surface'):
                lines.append(f"- Rollback surface: {item.get('rollback_surface')}")
            if item.get('reentry_check'):
                lines.append(f"- Re-entry check: {item.get('reentry_check')}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: {', '.join(f'`{req}`' for req in host_requirement_ids[:5])}")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append(f"- Cautions: {'; '.join(cautions[:3])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{cmd}`' for cmd in commands[:4])}")
            lines.append("")

    if promotion_verification_plan:
        lines.append("## Promotion verification lanes")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_verification_summary.get('entry_count') or 0)}")
        primary_verification_lane_ids = [str(x) for x in list(promotion_verification_summary.get('ordered_primary_verification_lane_ids') or []) if str(x)]
        if primary_verification_lane_ids:
            lines.append(f"- Dominant verification lanes: {', '.join(f'`{lane_id}`' for lane_id in primary_verification_lane_ids[:5])}")
        review_surface_ids = [str(x) for x in list(promotion_verification_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Review-led/proof-sensitive surfaces: {', '.join(f'`{surface_id}`' for surface_id in review_surface_ids[:6])}")
        lines.append("")
        for item in promotion_verification_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Verification posture: `{item.get('verification_posture') or 'review-proof'}`")
            if item.get('primary_verification_lane_id'):
                lines.append(f"- Primary verification lane: `{item.get('primary_verification_lane_id')}`")
            gate_ids = [str(x) for x in list(item.get('verification_gate_ids') or []) if str(x)]
            if gate_ids:
                lines.append(f"- Verification gates: {', '.join(f'`{gate_id}`' for gate_id in gate_ids[:5])}")
            if item.get('smoke_loop'):
                lines.append(f"- Smoke loop: {item.get('smoke_loop')}")
            if item.get('live_probe'):
                lines.append(f"- Live probe: {item.get('live_probe')}")
            if item.get('acceptance_boundary'):
                lines.append(f"- Acceptance boundary: {item.get('acceptance_boundary')}")
            proof_surfaces = [str(x) for x in list(item.get('proof_surfaces') or []) if str(x)]
            if proof_surfaces:
                lines.append(f"- Proof surfaces: {', '.join(f'`{surface}`' for surface in proof_surfaces[:5])}")
            acceptance_checks = [str(x) for x in list(item.get('acceptance_checks') or []) if str(x)]
            if acceptance_checks:
                lines.append(f"- Acceptance checks: {'; '.join(acceptance_checks[:3])}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: {', '.join(f'`{req}`' for req in host_requirement_ids[:5])}")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append(f"- Cautions: {'; '.join(cautions[:3])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{cmd}`' for cmd in commands[:4])}")
            lines.append("")

    if promotion_performance_plan:
        lines.append("## Promotion performance envelopes")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_performance_summary.get('entry_count') or 0)}")
        primary_performance_lane_ids = [str(x) for x in list(promotion_performance_summary.get('ordered_primary_performance_lane_ids') or []) if str(x)]
        if primary_performance_lane_ids:
            lines.append(f"- Dominant performance lanes: {', '.join(f'`{lane_id}`' for lane_id in primary_performance_lane_ids[:5])}")
        hotspot_ids = [str(x) for x in list(promotion_performance_summary.get('ordered_hotspot_ids') or []) if str(x)]
        if hotspot_ids:
            lines.append(f"- Dominant planner hotspots: {', '.join(f'`{hotspot_id}`' for hotspot_id in hotspot_ids[:6])}")
        review_surface_ids = [str(x) for x in list(promotion_performance_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Performance-sensitive review surfaces: {', '.join(f'`{surface_id}`' for surface_id in review_surface_ids[:6])}")
        lines.append("")
        for item in promotion_performance_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Performance posture: `{item.get('performance_posture') or 'review-measured'}`")
            if item.get('primary_performance_lane_id'):
                lines.append(f"- Primary performance lane: `{item.get('primary_performance_lane_id')}`")
            if item.get('latency_class'):
                lines.append(f"- Latency class: {item.get('latency_class')}")
            if item.get('hot_path'):
                lines.append(f"- Hot path: {item.get('hot_path')}")
            if item.get('batching_strategy'):
                lines.append(f"- Batching strategy: {item.get('batching_strategy')}")
            if item.get('throughput_boundary'):
                lines.append(f"- Throughput boundary: {item.get('throughput_boundary')}")
            acceptance_signals = [str(x) for x in list(item.get('acceptance_signals') or []) if str(x)]
            if acceptance_signals:
                lines.append(f"- Acceptance signals: {', '.join(f'`{signal}`' for signal in acceptance_signals[:5])}")
            hotspot_ids = [str(x) for x in list(item.get('performance_hotspot_ids') or []) if str(x)]
            if hotspot_ids:
                lines.append(f"- Related hotspots: {', '.join(f'`{hotspot_id}`' for hotspot_id in hotspot_ids[:5])}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: {', '.join(f'`{req}`' for req in host_requirement_ids[:5])}")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append(f"- Cautions: {'; '.join(cautions[:3])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{cmd}`' for cmd in commands[:4])}")
            lines.append("")

    if promotion_dispatch_budget_plan:
        lines.append("## Promotion dispatch budgets")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_dispatch_budget_summary.get('entry_count') or 0)}")
        primary_dispatch_lane_ids = [str(x) for x in list(promotion_dispatch_budget_summary.get('ordered_primary_dispatch_lane_ids') or []) if str(x)]
        if primary_dispatch_lane_ids:
            lines.append(f"- Dominant dispatch lanes: {', '.join(f'`{lane_id}`' for lane_id in primary_dispatch_lane_ids[:5])}")
        hotspot_ids = [str(x) for x in list(promotion_dispatch_budget_summary.get('ordered_hotspot_ids') or []) if str(x)]
        if hotspot_ids:
            lines.append(f"- Related planner hotspots: {', '.join(f'`{hotspot_id}`' for hotspot_id in hotspot_ids[:6])}")
        review_surface_ids = [str(x) for x in list(promotion_dispatch_budget_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Dispatch-review surfaces: {', '.join(f'`{surface_id}`' for surface_id in review_surface_ids[:6])}")
        lines.append("")
        for item in promotion_dispatch_budget_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Dispatch posture: `{item.get('dispatch_posture') or 'review-budget'}`")
            if item.get('primary_dispatch_lane_id'):
                lines.append(f"- Primary dispatch lane: `{item.get('primary_dispatch_lane_id')}`")
            if item.get('cold_start_path'):
                lines.append(f"- Cold start path: {item.get('cold_start_path')}")
            if item.get('steady_state_path'):
                lines.append(f"- Steady state path: {item.get('steady_state_path')}")
            if item.get('first_use_expectation'):
                lines.append(f"- First-use expectation: {item.get('first_use_expectation')}")
            guardrails = [str(x) for x in list(item.get('dispatch_guardrails') or []) if str(x)]
            if guardrails:
                lines.append(f"- Guardrails: {'; '.join(guardrails[:3])}")
            hotspot_ids = [str(x) for x in list(item.get('performance_hotspot_ids') or []) if str(x)]
            if hotspot_ids:
                lines.append(f"- Related hotspots: {', '.join(f'`{hotspot_id}`' for hotspot_id in hotspot_ids[:5])}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: {', '.join(f'`{req}`' for req in host_requirement_ids[:5])}")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append(f"- Cautions: {'; '.join(cautions[:3])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{cmd}`' for cmd in commands[:4])}")
            lines.append("")

    if promotion_waves:
        lines.append("## Promotion waves")
        lines.append("")
        for item in promotion_waves:
            lines.append(f"### {item.get('title') or item.get('wave_id')}")
            lines.append("")
            lines.append(str(item.get("goal") or ""))
            lines.append("")
            lines.append(f"- Priority: `{item.get('priority') or 'medium'}`")
            lines.append(f"- Surfaces: {int(item.get('surface_count') or 0)}")
            lines.append(f"- Macros: {int(item.get('macro_count') or 0)}")
            route_ids = [str(x) for x in list(item.get("route_ids") or []) if str(x)]
            if route_ids:
                lines.append(f"- Supporting routes: {', '.join(f'`{route_id}`' for route_id in route_ids)}")
            commands = [str(x) for x in list(item.get("commands") or []) if str(x)]
            if commands:
                lines.append("")
                lines.append("Suggested commands:")
                for cmd in commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")


    if promotion_authority_envelope_plan:
        lines.append("## Promotion authority envelopes")
        lines.append("")
        lines.append(f"- Entries: {int(promotion_authority_envelope_summary.get('entry_count') or 0)}")
        primary_authority_lane_ids = [str(x) for x in list(promotion_authority_envelope_summary.get('ordered_primary_authority_lane_ids') or []) if str(x)]
        if primary_authority_lane_ids:
            lines.append(f"- Primary authority lanes: `{', '.join(primary_authority_lane_ids[:6])}`")
        review_surface_ids = [str(x) for x in list(promotion_authority_envelope_summary.get('review_surface_ids') or []) if str(x)]
        if review_surface_ids:
            lines.append(f"- Review surfaces: `{', '.join(review_surface_ids[:6])}`")
        lines.append("")
        for item in promotion_authority_envelope_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Authority posture: `{item.get('authority_posture') or 'mixed-review'}`")
            primary_lane = str(item.get('primary_authority_lane_id') or '').strip()
            if primary_lane:
                lines.append(f"- Primary authority lane: `{primary_lane}`")
            if item.get('authority_owner'):
                lines.append(f"- Authority owner: {item.get('authority_owner')}")
            if item.get('authority_boundary'):
                lines.append(f"- Authority boundary: {item.get('authority_boundary')}")
            if item.get('revocation_surface'):
                lines.append(f"- Revocation surface: {item.get('revocation_surface')}")
            guardrails = [str(x) for x in list(item.get('authority_guardrails') or []) if str(x)]
            if guardrails:
                lines.append("- Authority guardrails:")
                for note in guardrails[:3]:
                    lines.append(f"  - {note}")
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: `{', '.join(host_requirement_ids[:5])}`")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            cautions = [str(x) for x in list(item.get('cautions') or []) if str(x)]
            if cautions:
                lines.append("- Cautions:")
                for note in cautions[:3]:
                    lines.append(f"  - {note}")
            evidence = [str(x) for x in list(item.get('evidence') or []) if str(x)]
            if evidence:
                lines.append(f"- Evidence: `{', '.join(evidence[:6])}`")
            lines.append("")

    if promotion_readiness:
        lines.append("## Promotion readiness")
        lines.append("")
        lines.append(f"- Ready surfaces: {int(readiness_summary.get('ready_count') or 0)}")
        lines.append(f"- Review surfaces: {int(readiness_summary.get('review_count') or 0)}")
        lines.append(f"- Blocked surfaces: {int(readiness_summary.get('blocked_count') or 0)}")
        lines.append("")
        for item in promotion_readiness:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Readiness: `{item.get('readiness_status') or 'review'}`")
            lines.append(f"- Priority: `{item.get('priority') or 'medium'}`")
            lines.append(f"- Required capabilities: {', '.join(f'`{x}`' for x in list(item.get('required_capabilities') or [])[:5]) or 'none'}")
            missing = [str(x) for x in list(item.get('missing_capabilities') or []) if str(x)]
            if missing:
                lines.append(f"- Missing capabilities: {', '.join(f'`{x}`' for x in missing)}")
            blockers = [str(x) for x in list(item.get('blockers') or []) if str(x)]
            if blockers:
                lines.append(f"- Blockers: {'; '.join(blockers[:4])}")
            review_notes = [str(x) for x in list(item.get('review_notes') or []) if str(x)]
            if review_notes:
                lines.append(f"- Review notes: {'; '.join(review_notes[:4])}")
            lines.append(f"- Next action: {item.get('next_action') or ''}")
            lines.append("")

    if promotion_gates:
        lines.append("## Promotion gates")
        lines.append("")
        lines.append(f"- Passing gates: {int(gate_summary.get('pass_count') or 0)}")
        lines.append(f"- Review gates: {int(gate_summary.get('review_count') or 0)}")
        lines.append(f"- Failing gates: {int(gate_summary.get('fail_count') or 0)}")
        lines.append("")
        for item in promotion_gates:
            lines.append(f"### {item.get('title') or item.get('gate_id')}")
            lines.append("")
            lines.append(f"- Status: `{item.get('status') or 'review'}`")
            lines.append(f"- Summary: {item.get('summary') or ''}")
            blocking = [str(x) for x in list(item.get('blocking_surfaces') or []) if str(x)]
            review = [str(x) for x in list(item.get('review_surfaces') or []) if str(x)]
            if blocking:
                lines.append(f"- Blocking surfaces: {', '.join(f'`{x}`' for x in blocking[:6])}")
            if review:
                lines.append(f"- Review surfaces: {', '.join(f'`{x}`' for x in review[:6])}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append(f"- Review commands: {', '.join(f'`{x}`' for x in commands[:4])}")
            lines.append("")

    if promotion_backlog:
        lines.append("## Promotion backlog")
        lines.append("")
        lines.append(f"- Tasks: {int(backlog_summary.get('task_count') or 0)}")
        lines.append(f"- Blocked tasks: {int(backlog_summary.get('blocked_count') or 0)}")
        lines.append(f"- Review tasks: {int(backlog_summary.get('review_count') or 0)}")
        lines.append(f"- Ready-to-run tasks: {int(backlog_summary.get('todo_count') or 0)}")
        lines.append("")
        for item in promotion_backlog:
            lines.append(f"### {item.get('title') or item.get('task_id')}")
            lines.append("")
            lines.append(f"- Queue state: `{item.get('queue_state') or 'review'}`")
            lines.append(f"- Kind: `{item.get('kind') or 'review'}`")
            lines.append(f"- Priority: `{item.get('priority') or 'medium'}`")
            if item.get('wave_title') or item.get('wave_id'):
                lines.append(f"- Wave: {item.get('wave_title') or item.get('wave_id')}")
            if item.get('export_surface_id'):
                lines.append(f"- Surface: `{item.get('export_surface_id')}`")
            if item.get('gate_id'):
                lines.append(f"- Gate: `{item.get('gate_id')}`")
            rationale = str(item.get('rationale') or '').strip()
            if rationale:
                lines.append(f"- Why now: {rationale}")
            blockers = [str(x) for x in list(item.get('blockers') or []) if str(x)]
            if blockers:
                lines.append(f"- Blockers: {'; '.join(blockers[:4])}")
            review_notes = [str(x) for x in list(item.get('review_notes') or []) if str(x)]
            if review_notes:
                lines.append(f"- Review notes: {'; '.join(review_notes[:4])}")
            lines.append(f"- Next action: {item.get('next_action') or ''}")
            commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
            if commands:
                lines.append("- Commands: " + ", ".join(f'`{x}`' for x in commands[:4]))
            lines.append("")

    if promotion_plan:
        lines.append("## Surface-by-surface promotion work")
        lines.append("")
        for item in promotion_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id')}")
            lines.append("")
            lines.append(f"- Surface id: `{item.get('export_surface_id') or ''}`")
            lines.append(f"- Priority: `{item.get('priority') or 'medium'}`")
            lines.append(f"- Dominant fit: `{item.get('dominant_fit') or 'good'}`")
            lines.append(f"- Macros: {', '.join(f'`{x}`' for x in list(item.get('macros') or [])[:6]) or 'none'}")
            tools = [str(x) for x in list(item.get("tool_family") or []) if str(x)]
            if tools:
                lines.append(f"- Tool families: {', '.join(tools[:5])}")
            reasons = [str(x) for x in list(item.get("reasons") or []) if str(x)]
            if reasons:
                lines.append(f"- Why: {reasons[0]}")
            risks = [str(x) for x in list(item.get("risks") or []) if str(x)]
            if risks:
                lines.append(f"- Risks: {', '.join(risks[:4])}")
            commands = [str(x) for x in list(item.get("commands") or []) if str(x)]
            if commands:
                lines.append("")
                lines.append("Commands:")
                for cmd in commands[:4]:
                    lines.append(f"- `{cmd}`")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_promotion_fixups(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    promotion_plan = [dict(item) for item in list(plan.get("export_promotion_plan") or []) if isinstance(item, dict)]
    promotion_readiness = [dict(item) for item in list(plan.get("promotion_readiness") or []) if isinstance(item, dict)]
    promotion_gates = [dict(item) for item in list(plan.get("promotion_gates") or []) if isinstance(item, dict)]
    promotion_backlog = [dict(item) for item in list(plan.get("promotion_backlog") or []) if isinstance(item, dict)]
    promotion_claim_witness = dict(plan.get("promotion_claim_witness") or {})
    promotion_claim_review_rows = [dict(item) for item in list(plan.get("promotion_claim_review_rows") or []) if isinstance(item, dict)]

    high_priority = [item for item in promotion_plan if str(item.get("priority") or "") == "high"]
    conditional = [item for item in promotion_plan if str(item.get("dominant_fit") or "") in {"conditional", "weak"}]
    helper = [item for item in promotion_plan if str(item.get("export_surface_id") or "") == "helper-route-dossier"]
    blocked = [item for item in promotion_readiness if str(item.get("readiness_status") or "") == "blocked"]
    review = [item for item in promotion_readiness if str(item.get("readiness_status") or "") == "review"]
    blocked_tasks = [item for item in promotion_backlog if str(item.get("queue_state") or "") == "blocked"]
    review_tasks = [item for item in promotion_backlog if str(item.get("queue_state") or "") == "review"]

    lines: list[str] = []
    lines.append(f"# VHK promotion fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-promotion-pack`. Use this when the planner already knows which Linux-native surfaces the project wants, but the repo still needs explicit promotion sequencing and review commands.")
    lines.append("")

    lines.append("## High-priority promotions")
    lines.append("")
    if high_priority:
        for item in high_priority:
            lines.append(f"- `{item.get('export_surface_id') or ''}` for {', '.join(f'`{x}`' for x in list(item.get('macros') or [])[:5]) or 'no macros'}")
        lines.append("")
    else:
        lines.append("None. No surface currently stands out as an immediate high-priority export lane.")
        lines.append("")

    lines.append("## Conditional or weak-fit promotions")
    lines.append("")
    if conditional:
        for item in conditional:
            lines.append(f"- `{item.get('export_surface_id') or ''}` stays `{item.get('dominant_fit') or 'conditional'}` and should keep fallback/review notes explicit.")
        lines.append("")
    else:
        lines.append("None. The current promotion surfaces mostly look strong enough to stage directly.")
        lines.append("")

    lines.append("## Promotion readiness blockers")
    lines.append("")
    if blocked:
        for item in blocked:
            lines.append(f"- `{item.get('export_surface_id') or ''}` is blocked: {'; '.join(str(x) for x in list(item.get('blockers') or [])[:3]) or 'review capability matrix'}")
        lines.append("")
    else:
        lines.append("None. No promotion surface is currently blocked by the available fit/capability signals.")
        lines.append("")

    lines.append("## Promotion readiness reviews")
    lines.append("")
    if review:
        for item in review:
            lines.append(f"- `{item.get('export_surface_id') or ''}` needs review: {'; '.join(str(x) for x in list(item.get('review_notes') or [])[:3]) or item.get('next_action') or 'review target desktops'}")
        lines.append("")
    else:
        lines.append("None. No promotion surface currently stands out as needing extra session review.")
        lines.append("")

    lines.append("## Promotion gates needing attention")
    lines.append("")
    gate_attention = [item for item in promotion_gates if str(item.get('status') or '') in {'review', 'fail'}]
    if gate_attention:
        for item in gate_attention:
            lines.append(f"- `{item.get('gate_id') or ''}` is `{item.get('status') or 'review'}`: {item.get('summary') or ''}")
        lines.append("")
    else:
        lines.append("None. Promotion gates currently look aligned with the staged surfaces.")
        lines.append("")

    lines.append("## Backlog tasks to run now")
    lines.append("")
    active_tasks = blocked_tasks + review_tasks
    if active_tasks:
        for item in active_tasks[:8]:
            ident = str(item.get('export_surface_id') or item.get('gate_id') or item.get('task_id') or '')
            lines.append(f"- `{ident}` is `{item.get('queue_state') or 'review'}`: {item.get('next_action') or item.get('rationale') or ''}")
        lines.append("")
    else:
        lines.append("None. The current backlog is mostly ready-to-run promotion work.")
        lines.append("")

    lines.append("## Current-host proof drift")
    lines.append("")
    if promotion_claim_witness:
        attention = [item for item in promotion_claim_review_rows if str((item.get("current_host_fit") or {}).get("status") or "") in {"drifted", "degraded", "unknown"}]
        if attention:
            for item in attention[:6]:
                lines.append(f"- `{item.get('target') or ''}` is `{((item.get('current_host_fit') or {}).get('status')) or 'unknown'}` on this host while recommended at `{item.get('recommended_level') or 'unsupported'}`")
            lines.append("")
        else:
            lines.append("None. Current-host witness review does not show target drift for the currently modeled claim set.")
            lines.append("")
    else:
        lines.append("None. Promotion-pack was generated without current-host claim witness data.")
        lines.append("")

    lines.append("## Helper-boundary surfaces")
    lines.append("")
    if helper:
        for item in helper:
            lines.append(f"- `{item.get('export_surface_id') or ''}` covers {', '.join(f'`{x}`' for x in list(item.get('macros') or [])[:5]) or 'no macros'} and should keep helper/session contracts explicit.")
        lines.append("")
    else:
        lines.append("None. No helper-boundary promotion surface is currently prominent in this project.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_promotion_backlog(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    backlog = [dict(item) for item in list(plan.get("promotion_backlog") or []) if isinstance(item, dict)]
    summary = dict(plan.get("promotion_backlog_summary") or {})

    lines: list[str] = []
    lines.append(f"# VHK promotion backlog for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-promotion-pack`. Use this as the execution queue for Linux-native promotion work after the planner has already identified lanes, readiness, and gates.")
    lines.append("")
    lines.append("## Queue summary")
    lines.append("")
    lines.append(f"- Tasks: {int(summary.get('task_count') or 0)}")
    lines.append(f"- Blocked: {int(summary.get('blocked_count') or 0)}")
    lines.append(f"- Review: {int(summary.get('review_count') or 0)}")
    lines.append(f"- Todo: {int(summary.get('todo_count') or 0)}")
    lines.append("")
    if not backlog:
        lines.append("No promotion backlog tasks were generated.")
        return "\n".join(lines).rstrip() + "\n"

    lines.append("## Tasks")
    lines.append("")
    for item in backlog:
        ident = str(item.get('task_id') or '')
        lines.append(f"### {item.get('title') or ident}")
        lines.append("")
        lines.append(f"- Id: `{ident}`")
        lines.append(f"- State: `{item.get('queue_state') or 'review'}`")
        lines.append(f"- Kind: `{item.get('kind') or 'review'}`")
        lines.append(f"- Priority: `{item.get('priority') or 'medium'}`")
        if item.get('wave_title') or item.get('wave_id'):
            lines.append(f"- Wave: {item.get('wave_title') or item.get('wave_id')}")
        if item.get('export_surface_id'):
            lines.append(f"- Surface: `{item.get('export_surface_id')}`")
        if item.get('gate_id'):
            lines.append(f"- Gate: `{item.get('gate_id')}`")
        rationale = str(item.get('rationale') or '').strip()
        if rationale:
            lines.append(f"- Rationale: {rationale}")
        next_action = str(item.get('next_action') or '').strip()
        if next_action:
            lines.append(f"- Next action: {next_action}")
        blockers = [str(x) for x in list(item.get('blockers') or []) if str(x)]
        if blockers:
            lines.append(f"- Blockers: {'; '.join(blockers[:5])}")
        review_notes = [str(x) for x in list(item.get('review_notes') or []) if str(x)]
        if review_notes:
            lines.append(f"- Review notes: {'; '.join(review_notes[:5])}")
        required = [str(x) for x in list(item.get('required_capabilities') or []) if str(x)]
        if required:
            lines.append("- Required capabilities: " + ", ".join(f'`{x}`' for x in required[:5]))
        commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
        if commands:
            lines.append("")
            lines.append("Commands:")
            for cmd in commands[:4]:
                lines.append(f"- `{cmd}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_promotion_evidence(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    evidence = [dict(item) for item in list(plan.get("promotion_evidence") or []) if isinstance(item, dict)]
    summary = dict(plan.get("promotion_evidence_summary") or {})

    lines: list[str] = []
    lines.append(f"# VHK promotion evidence for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-promotion-pack`. Use this as the proof checklist for promotion surfaces and gates so release posture is backed by checked-in artifacts instead of memory.")
    lines.append("")
    lines.append("## Evidence summary")
    lines.append("")
    lines.append(f"- Entries: {int(summary.get('entry_count') or 0)}")
    lines.append(f"- Complete: {int(summary.get('complete_count') or 0)}")
    lines.append(f"- Partial: {int(summary.get('partial_count') or 0)}")
    lines.append(f"- Missing: {int(summary.get('missing_count') or 0)}")
    lines.append("")
    if not evidence:
        lines.append("No promotion evidence entries were generated.")
        return "\n".join(lines).rstrip() + "\n"

    lines.append("## Evidence entries")
    lines.append("")
    for item in evidence:
        lines.append(f"### {item.get('title') or item.get('evidence_id')}")
        lines.append("")
        lines.append(f"- Id: `{item.get('evidence_id') or ''}`")
        lines.append(f"- Status: `{item.get('evidence_status') or 'partial'}`")
        lines.append(f"- Subject: `{item.get('subject_kind') or 'surface'}` / `{item.get('subject_id') or ''}`")
        lines.append(f"- Posture: `{item.get('posture') or 'review'}`")
        lines.append(f"- Required artifacts: {', '.join(f'`{x}`' for x in list(item.get('required_artifacts') or [])[:6]) or 'none'}")
        missing = [str(x) for x in list(item.get('missing_artifacts') or []) if str(x)]
        if missing:
            lines.append(f"- Missing artifacts: {', '.join(f'`{x}`' for x in missing[:6])}")
        present = [str(x) for x in list(item.get('present_artifacts') or []) if str(x)]
        if present:
            lines.append(f"- Present artifacts: {', '.join(f'`{x}`' for x in present[:6])}")
        rationale = str(item.get('rationale') or '').strip()
        if rationale:
            lines.append(f"- Rationale: {rationale}")
        blockers = [str(x) for x in list(item.get('blockers') or []) if str(x)]
        if blockers:
            lines.append(f"- Blockers: {'; '.join(blockers[:5])}")
        review_notes = [str(x) for x in list(item.get('review_notes') or []) if str(x)]
        if review_notes:
            lines.append(f"- Review notes: {'; '.join(review_notes[:5])}")
        commands = [str(x) for x in list(item.get('commands') or []) if str(x)]
        if commands:
            lines.append("")
            lines.append("Suggested commands:")
            for cmd in commands[:4]:
                lines.append(f"- `{cmd}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_promotion_refresh_script(plan: dict[str, Any]) -> str:
    selected_evidence_lane = dict(plan.get("selected_evidence_lane") or {})
    evidence_lane_fit = dict(plan.get("evidence_lane_fit") or {})
    evidence_arg = ""
    selected_profile_id = str(selected_evidence_lane.get("profile_id") or evidence_lane_fit.get("profile_id") or "").strip()
    selection_source = str(evidence_lane_fit.get("selection_source") or selected_evidence_lane.get("selection_source") or "")
    if selection_source == "explicit" and selected_profile_id:
        evidence_arg = f" --evidence-lane {selected_profile_id}"
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST="${1:-./build/promotion-review}"')
    lines.append('mkdir -p "$DEST"')
    lines.append('echo "Collecting VHK promotion evidence into $DEST"')
    lines.append("")
    lines.append(f'printf "+ %s\\n" "vhk plan-project . --json{evidence_arg} > $DEST/plan-project.json"')
    lines.append(f'sh -lc "vhk plan-project . --json{evidence_arg} > \\\"$DEST\\\"/plan-project.json" || true')
    lines.append(f'printf "+ %s\\n" "vhk gen-promotion-pack . --force --quiet{evidence_arg}"')
    lines.append(f'sh -lc "vhk gen-promotion-pack . --force --quiet{evidence_arg}" || true')
    lines.append(f'printf "+ %s\\n" "vhk gen-claim-pack . --force --quiet{evidence_arg}"')
    lines.append(f'sh -lc "vhk gen-claim-pack . --force --quiet{evidence_arg}" || true')
    lines.append('printf "+ %s\\n" "vhk gen-design-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-design-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-route-selection-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-route-selection-pack . --force --quiet" || true')
    lines.append('echo "Promotion review refresh complete."')
    return "\n".join(lines).rstrip() + "\n"

def write_promotion_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    promotion_doc: bool = True,
    fixups_doc: bool = True,
    backlog_doc: bool = True,
    evidence_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_promotion_pack_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane_profile,
    )

    written: dict[str, Path] = {}
    if promotion_doc:
        path = out_dir / "VHK_PROMOTION_PLAN.md"
        _write_if_allowed(path, render_promotion_doc(plan), force=force)
        written["promotion_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_PROMOTION_FIXUPS.md"
        _write_if_allowed(path, render_promotion_fixups(plan), force=force)
        written["fixups_doc"] = path
    if backlog_doc:
        path = out_dir / "VHK_PROMOTION_BACKLOG.md"
        _write_if_allowed(path, render_promotion_backlog(plan), force=force)
        written["backlog_doc"] = path
    if evidence_doc:
        path = out_dir / "VHK_PROMOTION_EVIDENCE.md"
        _write_if_allowed(path, render_promotion_evidence(plan), force=force)
        written["evidence_doc"] = path
    if plan_json:
        path = out_dir / "VHK_PROMOTION_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_review_promotion_plan.sh"
        _write_if_allowed(path, render_promotion_refresh_script(plan), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["refresh_script"] = path
    return written
