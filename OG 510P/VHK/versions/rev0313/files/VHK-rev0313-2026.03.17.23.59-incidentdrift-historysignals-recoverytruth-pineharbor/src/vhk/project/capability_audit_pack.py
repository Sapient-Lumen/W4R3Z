from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from vhk.project.activation_pack import build_activation_pack_plan
from vhk.project.claim_pack import audit_target_claims
from vhk.project.host_contract_pack import build_host_contract_plan
from vhk.project.loader import load_project
from vhk.project.readiness_pack import build_readiness_plan
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


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return slug or "project"


def _first_text(item: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _track_status(value: str | None) -> str:
    lowered = str(value or "unknown").strip().lower()
    if lowered in {"ready", "ok", "pass"}:
        return "ready"
    if lowered in {"limited", "warning", "degraded"}:
        return "degraded"
    if lowered in {"missing", "blocked", "fail", "permission_denied", "service_missing", "interface_missing", "backend_missing"}:
        return "blocked"
    return "unknown"


def _status_rank(value: str) -> int:
    return {"blocked": 0, "degraded": 1, "unknown": 2, "ready": 3}.get(str(value or "unknown"), 2)


def _lane_status(*values: str) -> str:
    statuses = [str(v or "unknown") for v in values if str(v or "").strip()]
    if not statuses:
        return "unknown"
    if "blocked" in statuses:
        return "blocked"
    if "degraded" in statuses:
        return "degraded"
    if "unknown" in statuses:
        return "unknown"
    return "ready"


def _build_paths(project_name: str, build_root: Path | None) -> dict[str, str]:
    slug = _slugify(project_name)
    root = (build_root or Path("build") / "capability-audit" / slug).as_posix()
    return {
        "root": root,
        "manifest": f"{root}/vhk_capability_audit_handoff.json",
        "readme": f"{root}/README.md",
        "collect_script": f"{root}/collect_capability_audit.sh",
        "reports_root": f"{root}/reports/latest",
        "reports_dir": f"{root}/reports/latest/reports",
        "docs_dir": f"{root}/reports/latest/docs",
        "scripts_dir": f"{root}/reports/latest/scripts",
        "doctor_json": f"{root}/reports/latest/reports/doctor.json",
        "validate_json": f"{root}/reports/latest/reports/validate.json",
        "plan_json": f"{root}/reports/latest/reports/plan-project.json",
        "audit_plan_json": f"{root}/reports/latest/docs/VHK_CAPABILITY_AUDIT_PLAN.json",
    }


def build_capability_audit_plan(
    project_dir: Path,
    *,
    build_root: Path | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        evidence_lane_profile=evidence_lane_profile,
    )
    host_plan = build_host_contract_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )
    readiness_plan = build_readiness_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )
    activation_plan = build_activation_pack_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
    )
    paths = _build_paths(str(project.name or "project"), build_root)
    input_lane_dossier = dict(strategy.get("input_lane_dossier") or {})
    promotion_input_lane_plan = [dict(item) for item in list(strategy.get("promotion_input_lane_plan") or []) if isinstance(item, dict)]
    promotion_activation_route_plan = [dict(item) for item in list(strategy.get("promotion_activation_route_plan") or []) if isinstance(item, dict)]
    promotion_operator_control_plan = [dict(item) for item in list(strategy.get("promotion_operator_control_plan") or []) if isinstance(item, dict)]
    promotion_recovery_plan = [dict(item) for item in list(strategy.get("promotion_recovery_plan") or []) if isinstance(item, dict)]
    promotion_verification_plan = [dict(item) for item in list(strategy.get("promotion_verification_plan") or []) if isinstance(item, dict)]
    promotion_performance_plan = [dict(item) for item in list(strategy.get("promotion_performance_plan") or []) if isinstance(item, dict)]
    promotion_dispatch_budget_plan = [dict(item) for item in list(strategy.get("promotion_dispatch_budget_plan") or []) if isinstance(item, dict)]
    promotion_authority_envelope_plan = [dict(item) for item in list(strategy.get("promotion_authority_envelope_plan") or []) if isinstance(item, dict)]

    usage_map = {
        str(key): [dict(item) for item in list(value or []) if isinstance(item, dict)]
        for key, value in dict(capability_usage or {}).items()
        if str(key)
    }
    host_requirements = [dict(item) for item in list(host_plan.get("host_requirements") or []) if isinstance(item, dict)]
    readiness_requirements = [dict(item) for item in list(readiness_plan.get("readiness_requirements") or []) if isinstance(item, dict)]
    session_capabilities = {str(k): dict(v) for k, v in dict(capability_matrix or {}).items() if isinstance(v, Mapping)}

    relevant_capabilities: list[str] = []
    for capability in list(usage_map.keys()) + [str(item.get("capability") or "") for item in host_requirements]:
        cap = str(capability or "").strip()
        if cap and cap not in relevant_capabilities:
            relevant_capabilities.append(cap)

    capability_lanes: list[dict[str, Any]] = []
    for capability in relevant_capabilities:
        refs = [dict(item) for item in usage_map.get(capability, [])]
        session_item = dict(session_capabilities.get(capability) or {})
        session_status = _track_status(str(session_item.get("status") or "unknown")) if session_item else "unknown"
        reqs = [dict(item) for item in host_requirements if str(item.get("capability") or "") == capability]
        readiness = [dict(item) for item in readiness_requirements if str(item.get("capability") or "") == capability]
        req_statuses = [str(item.get("observed_status") or "unknown") for item in reqs]
        readiness_statuses = [str(item.get("readiness_status") or "unknown") for item in readiness]
        lane_status = _lane_status(session_status, *req_statuses, *readiness_statuses)
        notes: list[str] = []
        recommended = str(session_item.get("recommended") or "").strip()
        if recommended:
            notes.append(f"Current session recommendation: `{recommended}`")
        mechanisms = [str(x) for x in list(session_item.get("mechanisms") or []) if str(x)]
        if mechanisms:
            notes.append("Mechanisms: " + ", ".join(mechanisms[:4]))
        if reqs:
            notes.append(f"Host requirements touching this capability: {len(reqs)}")
        if readiness:
            notes.append(f"Readiness requirements touching this capability: {len(readiness)}")
        capability_lanes.append(
            {
                "capability": capability,
                "status": lane_status,
                "session_status": session_status,
                "usage_refs": refs,
                "session_item": session_item,
                "host_requirements": reqs,
                "readiness_requirements": readiness,
                "notes": notes,
            }
        )

    capability_lanes.sort(key=lambda item: (_status_rank(str(item.get("status") or "unknown")), str(item.get("capability") or "")))

    fallback_routes: list[dict[str, Any]] = []
    for route in list(activation_plan.get("activation_routes") or []):
        if not isinstance(route, Mapping):
            continue
        row = dict(route)
        fallback_ids = [str(x) for x in list(row.get("fallback_routes") or []) if str(x)]
        if fallback_ids or str(row.get("activation_kind") or "") == "launcher":
            fallback_routes.append(row)
    fallback_routes.sort(key=lambda item: (_status_rank(str(item.get("route_status") or "unknown")), str(item.get("activation_kind") or ""), str(item.get("title") or "")))

    helper_boundaries = [
        dict(item)
        for item in host_requirements
        if str(item.get("requirement_type") or "") in {"service", "permission"}
    ]
    helper_boundaries.sort(key=lambda item: (_status_rank(str(item.get("observed_status") or "unknown")), str(item.get("priority") or ""), str(item.get("title") or "")))

    portal_audit: list[dict[str, Any]] = []
    for item in host_requirements:
        row = dict(item)
        portals = [str(x) for x in list(row.get("portal_interfaces") or []) if str(x)]
        backend_hints = [str(x) for x in list(row.get("portal_backend_hints") or []) if str(x)]
        if portals or backend_hints or str(row.get("requirement_type") or "") == "portal":
            portal_audit.append(row)
    for capability, item in session_capabilities.items():
        portal_backends = [str(x) for x in list(item.get("portal_backends") or []) if str(x)]
        mechanisms = [str(x) for x in list(item.get("mechanisms") or []) if str(x).startswith("portal:")]
        if not portal_backends and not mechanisms:
            continue
        portal_audit.append(
            {
                "id": f"session-{capability}",
                "title": f"Session portal lane for {capability}",
                "requirement_type": "portal",
                "capability": capability,
                "observed_status": _track_status(str(item.get("status") or "unknown")),
                "portal_interfaces": mechanisms,
                "portal_backend_hints": portal_backends,
                "recommended": item.get("recommended"),
                "notes": list(item.get("notes") or []),
            }
        )
    portal_audit.sort(key=lambda item: (_status_rank(str(item.get("observed_status") or "unknown")), str(item.get("title") or "")))

    audit_surface = next(
        (
            dict(item)
            for item in list(strategy.get("deployable_surfaces") or [])
            if isinstance(item, Mapping) and str(item.get("id") or "") == "capability-audit-pack"
        ),
        {},
    )
    audit_recipe = next(
        (
            dict(item)
            for item in list(strategy.get("setup_recipes") or [])
            if isinstance(item, Mapping) and str(item.get("id") or "") == "capability-audit-review"
        ),
        {},
    )

    claim_audit: dict[str, Any] | None = None
    claims_file = project_dir / "docs" / "VHK_TARGET_CLAIMS.yaml"
    if claims_file.exists():
        try:
            claim_audit = audit_target_claims(
                project_dir,
                claims_file=claims_file,
                capability_usage=capability_usage,
                capability_matrix=capability_matrix,
                capability_issues=capability_issues,
                host_snapshot=host_snapshot,
                evidence_lane_profile=evidence_lane_profile,
            )
        except Exception as exc:
            claim_audit = {
                "claims_file": str(claims_file),
                "summary": {"claims": 0, "pass": 0, "warning": 0, "fail": 1},
                "results": [],
                "error": str(exc),
            }

    blocked_lanes = [str(item.get("capability") or "") for item in capability_lanes if str(item.get("status") or "") == "blocked"]
    degraded_lanes = [str(item.get("capability") or "") for item in capability_lanes if str(item.get("status") or "") == "degraded"]
    unknown_lanes = [str(item.get("capability") or "") for item in capability_lanes if str(item.get("status") or "") == "unknown"]
    if blocked_lanes:
        overall = "blocked"
    elif degraded_lanes:
        overall = "degraded"
    elif unknown_lanes:
        overall = "unknown"
    else:
        overall = "ready"

    review_commands = [
        "vhk doctor --json",
        f"vhk validate {project_dir.as_posix()} --json",
        f"vhk plan-project {project_dir.as_posix()} --json",
        f"vhk gen-host-contract-pack {project_dir.as_posix()} --force --quiet",
        f"vhk gen-readiness-pack {project_dir.as_posix()} --force --quiet",
        f"vhk gen-activation-pack {project_dir.as_posix()} --force --quiet",
        f"vhk gen-capability-audit-pack {project_dir.as_posix()} --force --quiet",
    ]
    if claim_audit is not None:
        review_commands.append(f"vhk audit-target-claims {project_dir.as_posix()}")

    return {
        "source_contract": "capability_audit_pack",
        "project": dict(strategy.get("project") or {}),
        "overview": dict(strategy.get("overview") or {}),
        "capability_audit_summary": {
            "overall_status": overall,
            "lane_count": len(capability_lanes),
            "blocked_lanes": blocked_lanes,
            "degraded_lanes": degraded_lanes,
            "unknown_lanes": unknown_lanes,
            "ready_lanes": [str(item.get("capability") or "") for item in capability_lanes if str(item.get("status") or "") == "ready"],
        },
        "capability_lanes": capability_lanes,
        "input_lane_dossier": input_lane_dossier,
        "promotion_input_lane_plan": promotion_input_lane_plan,
        "promotion_activation_route_plan": promotion_activation_route_plan,
        "promotion_operator_control_plan": promotion_operator_control_plan,
        "promotion_recovery_plan": promotion_recovery_plan,
        "promotion_verification_plan": promotion_verification_plan,
        "promotion_performance_plan": promotion_performance_plan,
        "promotion_dispatch_budget_plan": promotion_dispatch_budget_plan,
        "promotion_authority_envelope_plan": promotion_authority_envelope_plan,
        "fallback_routes": fallback_routes,
        "helper_boundaries": helper_boundaries,
        "portal_audit": portal_audit,
        "audit_surface": audit_surface,
        "audit_recipe": audit_recipe,
        "host_contract_summary": dict(host_plan.get("host_summary") or {}),
        "readiness_summary": dict(readiness_plan.get("readiness_summary") or {}),
        "activation_summary": dict(activation_plan.get("activation_summary") or {}),
        "session_capabilities": dict(capability_matrix or {}),
        "session_issues": [dict(item) for item in list(capability_issues or []) if isinstance(item, dict)],
        "host_snapshot": dict(host_snapshot or {}),
        "review_commands": review_commands,
        "claims_file": str(claims_file) if claims_file.exists() else None,
        "claim_audit": claim_audit,
        "audit_paths": paths,
    }


def render_capability_audit_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("capability_audit_summary") or {})
    lanes = _trim_items(plan.get("capability_lanes"), limit=10)
    input_lane_dossier = dict(plan.get("input_lane_dossier") or {})
    input_lanes = _trim_items(input_lane_dossier.get("lanes"), limit=8)
    promotion_input_lanes = _trim_items(plan.get("promotion_input_lane_plan"), limit=8)
    promotion_activation_routes = _trim_items(plan.get("promotion_activation_route_plan"), limit=8)
    promotion_operator_controls = _trim_items(plan.get("promotion_operator_control_plan"), limit=8)
    promotion_recovery_plan = _trim_items(plan.get("promotion_recovery_plan"), limit=8)
    promotion_verification_plan = _trim_items(plan.get("promotion_verification_plan"), limit=8)
    promotion_performance_plan = _trim_items(plan.get("promotion_performance_plan"), limit=8)
    promotion_dispatch_budget_plan = _trim_items(plan.get("promotion_dispatch_budget_plan"), limit=8)
    promotion_authority_envelope_plan = _trim_items(plan.get("promotion_authority_envelope_plan"), limit=8)
    helpers = _trim_items(plan.get("helper_boundaries"), limit=8)
    portals = _trim_items(plan.get("portal_audit"), limit=8)
    routes = _trim_items(plan.get("fallback_routes"), limit=8)
    review_commands = [str(x) for x in list(plan.get("review_commands") or []) if str(x)]
    claim_audit = dict(plan.get("claim_audit") or {})

    lines: list[str] = []
    lines.append(f"# VHK capability audit for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-capability-audit-pack`. Use it to turn Linux desktop limits into a reviewable shipping surface: session capability facts, helper boundaries, portal routing hints, and explicit fallback routes instead of vague compatibility slogans.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall audit status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Capability lanes: {summary.get('lane_count') or 0}")
    lines.append(f"- Blocked lanes: {len(summary.get('blocked_lanes') or [])}")
    lines.append(f"- Degraded lanes: {len(summary.get('degraded_lanes') or [])}")
    lines.append(f"- Unknown lanes: {len(summary.get('unknown_lanes') or [])}")
    lines.append("")

    if input_lanes:
        lines.append("## Input lane dossier")
        lines.append("")
        summary_text = str(input_lane_dossier.get("summary") or "").strip()
        if summary_text:
            lines.append(f"- Summary: {summary_text}")
        recommended_lane_ids = [str(x) for x in list(input_lane_dossier.get("recommended_lane_ids") or []) if str(x)]
        if recommended_lane_ids:
            lines.append(f"- Recommended lanes: `{', '.join(recommended_lane_ids[:4])}`")
        lines.append("")
        for item in input_lanes:
            lines.append(f"### {item.get('title') or item.get('id') or 'lane'}")
            lines.append(f"- Fit: `{item.get('fit') or 'unknown'}`")
            lines.append(f"- Kind: `{item.get('kind') or 'unknown'}`")
            recommended_for = [str(x) for x in list(item.get("recommended_for") or []) if str(x)]
            if recommended_for:
                lines.append(f"- Best for: {', '.join(recommended_for[:4])}")
            session_caps = [str(x) for x in list(item.get("session_capabilities") or []) if str(x)]
            if session_caps:
                lines.append(f"- Session posture: `{', '.join(session_caps[:4])}`")
            host_requirement_ids = [str(x) for x in list(item.get("host_requirement_ids") or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: `{', '.join(host_requirement_ids[:5])}`")
            why = str(item.get("why") or "").strip()
            if why:
                lines.append(f"- Why: {why}")
            cautions = [str(x) for x in list(item.get("cautions") or []) if str(x)]
            if cautions:
                lines.append("- Cautions:")
                for note in cautions[:3]:
                    lines.append(f"  - {note}")
            evidence = [str(x) for x in list(item.get("evidence") or []) if str(x)]
            if evidence:
                lines.append(f"- Evidence: `{', '.join(evidence[:6])}`")
            lines.append("")

    if promotion_input_lanes:
        lines.append("## Promotion lane plan")
        lines.append("")
        for item in promotion_input_lanes:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Shipping posture: `{item.get('shipping_posture') or 'reviewed'}`")
            primary_lane = str(item.get('primary_input_lane_id') or '').strip()
            if primary_lane:
                lines.append(f"- Primary lane: `{primary_lane}` (`{item.get('primary_input_lane_fit') or 'unknown'}`)")
            alternate_lane_ids = [str(x) for x in list(item.get('alternate_input_lane_ids') or []) if str(x)]
            if alternate_lane_ids:
                lines.append(f"- Alternate lanes: `{', '.join(alternate_lane_ids[:4])}`")
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

    if promotion_activation_routes:
        lines.append("## Promotion startup routes")
        lines.append("")
        for item in promotion_activation_routes:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Startup posture: `{item.get('startup_posture') or 'reviewed'}`")
            primary_route = str(item.get('primary_activation_route_id') or '').strip()
            if primary_route:
                lines.append(f"- Primary activation route: `{primary_route}` (`{item.get('primary_activation_kind') or 'unknown'}` · `{item.get('primary_activation_fit') or 'unknown'}`)")
            if item.get('startup_owner'):
                lines.append(f"- Startup owner: {item.get('startup_owner')}")
            if item.get('steady_state'):
                lines.append(f"- Steady state: {item.get('steady_state')}")
            alternate_route_ids = [str(x) for x in list(item.get('alternate_activation_route_ids') or []) if str(x)]
            if alternate_route_ids:
                lines.append(f"- Alternate routes: `{', '.join(alternate_route_ids[:4])}`")
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

    if promotion_operator_controls:
        lines.append("## Promotion operator controls")
        lines.append("")
        for item in promotion_operator_controls:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Control posture: `{item.get('control_posture') or 'reviewed'}`")
            primary_lane = str(item.get('primary_control_lane_id') or '').strip()
            if primary_lane:
                lines.append(f"- Primary control lane: `{primary_lane}`")
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

    if promotion_recovery_plan:
        lines.append("## Promotion recovery lanes")
        lines.append("")
        for item in promotion_recovery_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Recovery posture: `{item.get('recovery_posture') or 'review-led'}`")
            primary_lane = str(item.get('primary_recovery_lane_id') or '').strip()
            if primary_lane:
                lines.append(f"- Primary recovery lane: `{primary_lane}`")
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

    if promotion_verification_plan:
        lines.append("## Promotion verification lanes")
        lines.append("")
        for item in promotion_verification_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Verification posture: `{item.get('verification_posture') or 'review-proof'}`")
            primary_lane = str(item.get('primary_verification_lane_id') or '').strip()
            if primary_lane:
                lines.append(f"- Primary verification lane: `{primary_lane}`")
            gate_ids = [str(x) for x in list(item.get('verification_gate_ids') or []) if str(x)]
            if gate_ids:
                lines.append(f"- Verification gates: `{', '.join(gate_ids[:5])}`")
            if item.get('smoke_loop'):
                lines.append(f"- Smoke loop: {item.get('smoke_loop')}")
            if item.get('live_probe'):
                lines.append(f"- Live probe: {item.get('live_probe')}")
            if item.get('acceptance_boundary'):
                lines.append(f"- Acceptance boundary: {item.get('acceptance_boundary')}")
            proof_surfaces = [str(x) for x in list(item.get('proof_surfaces') or []) if str(x)]
            if proof_surfaces:
                lines.append(f"- Proof surfaces: `{', '.join(proof_surfaces[:5])}`")
            acceptance_checks = [str(x) for x in list(item.get('acceptance_checks') or []) if str(x)]
            if acceptance_checks:
                lines.append("- Acceptance checks:")
                for note in acceptance_checks[:3]:
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

    if promotion_performance_plan:
        lines.append("## Promotion performance envelopes")
        lines.append("")
        for item in promotion_performance_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Performance posture: `{item.get('performance_posture') or 'review-measured'}`")
            primary_lane = str(item.get('primary_performance_lane_id') or '').strip()
            if primary_lane:
                lines.append(f"- Primary performance lane: `{primary_lane}`")
            if item.get('latency_class'):
                lines.append(f"- Latency class: {item.get('latency_class')}")
            if item.get('hot_path'):
                lines.append(f"- Hot path: {item.get('hot_path')}")
            if item.get('batching_strategy'):
                lines.append(f"- Batching strategy: {item.get('batching_strategy')}")
            if item.get('throughput_boundary'):
                lines.append(f"- Throughput boundary: {item.get('throughput_boundary')}")
            hotspot_ids = [str(x) for x in list(item.get('performance_hotspot_ids') or []) if str(x)]
            if hotspot_ids:
                lines.append(f"- Related hotspots: `{', '.join(hotspot_ids[:5])}`")
            acceptance_signals = [str(x) for x in list(item.get('acceptance_signals') or []) if str(x)]
            if acceptance_signals:
                lines.append("- Acceptance signals:")
                for note in acceptance_signals[:3]:
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

    if promotion_dispatch_budget_plan:
        lines.append("## Promotion dispatch budgets")
        lines.append("")
        for item in promotion_dispatch_budget_plan:
            lines.append(f"### {item.get('title') or item.get('export_surface_id') or 'surface'}")
            lines.append(f"- Dispatch posture: `{item.get('dispatch_posture') or 'review-budget'}`")
            primary_lane = str(item.get('primary_dispatch_lane_id') or '').strip()
            if primary_lane:
                lines.append(f"- Primary dispatch lane: `{primary_lane}`")
            if item.get('cold_start_path'):
                lines.append(f"- Cold start path: {item.get('cold_start_path')}")
            if item.get('steady_state_path'):
                lines.append(f"- Steady state path: {item.get('steady_state_path')}")
            if item.get('first_use_expectation'):
                lines.append(f"- First-use expectation: {item.get('first_use_expectation')}")
            guardrails = [str(x) for x in list(item.get('dispatch_guardrails') or []) if str(x)]
            if guardrails:
                lines.append("- Dispatch guardrails:")
                for note in guardrails[:3]:
                    lines.append(f"  - {note}")
            hotspot_ids = [str(x) for x in list(item.get('performance_hotspot_ids') or []) if str(x)]
            if hotspot_ids:
                lines.append(f"- Related hotspots: `{', '.join(hotspot_ids[:5])}`")
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

    if promotion_authority_envelope_plan:
        lines.append("## Promotion authority envelopes")
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
            host_requirement_ids = [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)]
            if host_requirement_ids:
                lines.append(f"- Related host requirements: `{', '.join(host_requirement_ids[:5])}`")
            summary_text = str(item.get('summary') or '').strip()
            if summary_text:
                lines.append(f"- Summary: {summary_text}")
            lines.append("")

    if lanes:
        lines.append("## Capability lanes")
        lines.append("")
        for item in lanes:
            capability = item.get("capability") or "capability"
            lines.append(f"### {capability}")
            lines.append(f"- Audit status: `{item.get('status') or 'unknown'}`")
            lines.append(f"- Session fit: `{item.get('session_status') or 'unknown'}`")
            session_item = dict(item.get("session_item") or {})
            recommended = str(session_item.get("recommended") or "").strip()
            if recommended:
                lines.append(f"- Session recommendation: `{recommended}`")
            mechanisms = [str(x) for x in list(session_item.get("mechanisms") or []) if str(x)]
            if mechanisms:
                lines.append(f"- Mechanisms: `{', '.join(mechanisms[:5])}`")
            refs = [dict(x) for x in list(item.get("usage_refs") or []) if isinstance(x, dict)]
            if refs:
                examples: list[str] = []
                for ref in refs[:4]:
                    source = str(ref.get("source") or "usage")
                    macro = str(ref.get("macro") or ref.get("watcher") or "").strip()
                    step = str(ref.get("step_type") or ref.get("keys") or "").strip()
                    text = ":".join(part for part in [source, macro, step] if part)
                    examples.append(text or source)
                if examples:
                    lines.append(f"- Used by: {', '.join(examples)}")
            reqs = [dict(x) for x in list(item.get("host_requirements") or []) if isinstance(x, dict)]
            if reqs:
                lines.append("- Host requirements:")
                for req in reqs[:4]:
                    lines.append(f"  - `{req.get('id')}` — `{req.get('observed_status') or 'unknown'}` — {_first_text(req, 'observed_note', 'why', 'title')}")
            ready = [dict(x) for x in list(item.get("readiness_requirements") or []) if isinstance(x, dict)]
            if ready:
                lines.append("- Readiness checks:")
                for req in ready[:4]:
                    lines.append(f"  - `{req.get('id')}` — `{req.get('readiness_status') or 'unknown'}` — {_first_text(req, 'readiness_note', 'observed_note', 'title')}")
            notes = [str(x) for x in list(item.get("notes") or []) if str(x)]
            if notes:
                lines.append("- Notes:")
                for note in notes[:4]:
                    lines.append(f"  - {note}")
            lines.append("")

    if helpers:
        lines.append("## Helper and permission boundaries")
        lines.append("")
        for item in helpers:
            title = item.get("title") or item.get("id") or "boundary"
            lines.append(f"### {title}")
            lines.append(f"- Observed status: `{item.get('observed_status') or 'unknown'}`")
            groups = [str(x) for x in list(item.get("groups") or []) if str(x)]
            paths = [str(x) for x in list(item.get("paths") or []) if str(x)]
            services = [str(x) for x in list(item.get("services") or []) if str(x)]
            if groups:
                lines.append(f"- Groups: `{', '.join(groups)}`")
            if paths:
                lines.append(f"- Paths: `{', '.join(paths[:4])}`")
            if services:
                lines.append(f"- Helper services/binaries: `{', '.join(services[:4])}`")
            why = _first_text(item, "observed_note", "why")
            if why:
                lines.append(f"- Why it matters: {why}")
            lines.append("")

    if portals:
        lines.append("## Portal and session routing audit")
        lines.append("")
        for item in portals:
            title = item.get("title") or item.get("id") or "portal"
            lines.append(f"### {title}")
            lines.append(f"- Observed status: `{item.get('observed_status') or 'unknown'}`")
            interfaces = [str(x) for x in list(item.get("portal_interfaces") or []) if str(x)]
            if interfaces:
                lines.append(f"- Interfaces: `{', '.join(interfaces[:5])}`")
            hints = [str(x) for x in list(item.get("portal_backend_hints") or []) if str(x)]
            if hints:
                lines.append(f"- Backend hints: `{', '.join(hints[:5])}`")
            recommended = str(item.get("recommended") or "").strip()
            if recommended:
                lines.append(f"- Recommended path: `{recommended}`")
            notes = [str(x) for x in list(item.get("notes") or []) if str(x)]
            if notes:
                lines.append("- Notes:")
                for note in notes[:3]:
                    lines.append(f"  - {note}")
            lines.append("")

    if routes:
        lines.append("## Fallback routes")
        lines.append("")
        for item in routes:
            title = item.get("title") or item.get("id") or "route"
            lines.append(f"### {title}")
            lines.append(f"- Route status: `{item.get('route_status') or 'unknown'}`")
            lines.append(f"- Kind: `{item.get('activation_kind') or 'unknown'}`")
            entrypoint = str(item.get("entrypoint") or "").strip()
            if entrypoint:
                lines.append(f"- Entrypoint: `{entrypoint}`")
            fallbacks = [str(x) for x in list(item.get("fallback_routes") or []) if str(x)]
            if fallbacks:
                lines.append(f"- Fallback ids: `{', '.join(fallbacks)}`")
            note = _first_text(item, "route_note", "why")
            if note:
                lines.append(f"- Note: {note}")
            lines.append("")

    if claim_audit:
        claim_summary = dict(claim_audit.get("summary") or {})
        lines.append("## Claim posture")
        lines.append("")
        lines.append(f"- Claims reviewed: {claim_summary.get('claims') or 0}")
        lines.append(f"- Pass: {claim_summary.get('pass') or 0}")
        lines.append(f"- Warning: {claim_summary.get('warning') or 0}")
        lines.append(f"- Fail: {claim_summary.get('fail') or 0}")
        lines.append(f"- Current-host fit (aligned/degraded/drifted/neutral/unknown): {claim_summary.get('fit_aligned') or 0}/{claim_summary.get('fit_degraded') or 0}/{claim_summary.get('fit_drifted') or 0}/{claim_summary.get('fit_neutral') or 0}/{claim_summary.get('fit_unknown') or 0}")
        error = str(claim_audit.get("error") or "").strip()
        if error:
            lines.append(f"- Claim audit error: {error}")
        lines.append("")
        for item in _trim_items(claim_audit.get("results"), limit=6):
            current_host_fit = dict(item.get("current_host_fit") or {})
            line = f"- **{item.get('title') or item.get('target') or 'claim'}** — `{item.get('status') or 'unknown'}` · claim `{item.get('claim_level') or 'unsupported'}` vs recommended `{item.get('recommended_level') or 'unsupported'}`"
            if current_host_fit:
                line += f" · host witness `{current_host_fit.get('status') or 'unknown'}`"
            lines.append(line)
        lines.append("")

    lines.append("## Refresh commands")
    lines.append("")
    for cmd in review_commands[:10]:
        lines.append(f"- `{cmd}`")
    lines.append("")
    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"


def render_capability_fixups_doc(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("capability_audit_summary") or {})
    lanes = [dict(item) for item in list(plan.get("capability_lanes") or []) if isinstance(item, dict)]
    routes = [dict(item) for item in list(plan.get("fallback_routes") or []) if isinstance(item, dict)]
    helpers = [dict(item) for item in list(plan.get("helper_boundaries") or []) if isinstance(item, dict)]

    blocked = [item for item in lanes if str(item.get("status") or "") == "blocked"]
    degraded = [item for item in lanes if str(item.get("status") or "") == "degraded"]

    lines: list[str] = []
    lines.append(f"# VHK capability fixups for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-capability-audit-pack`. Use this as the follow-up queue for blocked/degraded Linux capability lanes and the fallback surfaces that should stay visible in docs or release notes.")
    lines.append("")
    lines.append("## Current posture")
    lines.append("")
    lines.append(f"- Overall audit status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Blocked lanes: {', '.join(summary.get('blocked_lanes') or []) or '(none)' }")
    lines.append(f"- Degraded lanes: {', '.join(summary.get('degraded_lanes') or []) or '(none)' }")
    lines.append("")

    lines.append("## Blocked queue")
    lines.append("")
    if not blocked:
        lines.append("- No blocked capability lanes in the current audit snapshot.")
    else:
        for item in blocked:
            lines.append(f"- **{item.get('capability') or 'capability'}** — session `{item.get('session_status') or 'unknown'}`")
            for req in list(item.get("host_requirements") or [])[:4]:
                hint = _first_text(req, "observed_note", "why")
                lines.append(f"  - Host requirement `{req.get('id')}` → `{req.get('observed_status') or 'unknown'}`{f' — {hint}' if hint else ''}")
            for req in list(item.get("readiness_requirements") or [])[:4]:
                hint = _first_text(req, "readiness_note", "observed_note")
                lines.append(f"  - Readiness `{req.get('id')}` → `{req.get('readiness_status') or 'unknown'}`{f' — {hint}' if hint else ''}")
    lines.append("")

    lines.append("## Degraded queue")
    lines.append("")
    if not degraded:
        lines.append("- No degraded capability lanes in the current audit snapshot.")
    else:
        for item in degraded:
            lines.append(f"- **{item.get('capability') or 'capability'}** — session `{item.get('session_status') or 'unknown'}`")
            notes = [str(x) for x in list(item.get("notes") or []) if str(x)]
            for note in notes[:3]:
                lines.append(f"  - {note}")
    lines.append("")

    lines.append("## Fallback route reminders")
    lines.append("")
    if not routes:
        lines.append("- No explicit fallback routes were modeled.")
    else:
        for item in routes[:6]:
            lines.append(f"- **{item.get('title') or item.get('id') or 'route'}** — `{item.get('route_status') or 'unknown'}` via `{item.get('activation_kind') or 'unknown'}`")
    lines.append("")

    lines.append("## Helper boundary reminders")
    lines.append("")
    if not helpers:
        lines.append("- No helper/permission boundary items were modeled.")
    else:
        for item in helpers[:6]:
            title = item.get("title") or item.get("id") or "boundary"
            hint = _first_text(item, "observed_note", "why")
            lines.append(f"- **{title}** — `{item.get('observed_status') or 'unknown'}`{f' — {hint}' if hint else ''}")
    lines.append("")
    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"


def render_refresh_script(project_dir: Path, *, build_root: Path | None) -> str:
    project = project_dir.as_posix()
    parts = [
        "#!/usr/bin/env sh",
        "set -eu",
        "",
        'echo "Refreshing VHK capability audit pack..."',
    ]
    cmd = [f'vhk gen-capability-audit-pack {project} --force --quiet']
    if build_root is not None:
        cmd[0] += f" --build-root {build_root.as_posix()}"
    parts.append(cmd[0])
    parts.append('echo "Capability-audit refresh complete."')
    parts.append("")
    return "\n".join(parts)


def render_handoff_readme(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("capability_audit_summary") or {})
    paths = dict(plan.get("audit_paths") or {})
    lines: list[str] = []
    lines.append(f"# Capability audit handoff for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-capability-audit-pack`. This handoff turns session capability facts, helper boundaries, and fallback routes into a reviewable audit bundle instead of leaving them scattered across planner output.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Overall audit status: `{summary.get('overall_status') or 'unknown'}`")
    lines.append(f"- Audit doc: `docs/VHK_CAPABILITY_AUDIT.md`")
    lines.append(f"- Audit fixups: `docs/VHK_CAPABILITY_FIXUPS.md`")
    lines.append(f"- Manifest: `{Path(str(paths.get('manifest') or 'vhk_capability_audit_handoff.json')).name}`")
    lines.append("")
    lines.append("## Capture flow")
    lines.append("")
    lines.append("1. Run `./collect_capability_audit.sh` to capture a fresh doctor/validate/plan snapshot plus regenerated audit docs under `reports/latest/`.")
    lines.append("2. Review `reports/latest/docs/VHK_CAPABILITY_AUDIT.md` and `reports/latest/docs/VHK_CAPABILITY_FIXUPS.md`.")
    lines.append("3. Keep at least one fallback route visible in public docs when the audit is degraded or blocked.")
    lines.append("")
    return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"


def render_collect_script(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    paths = dict(plan.get("audit_paths") or {})
    project_root = str(project.get("root_dir") or ".")
    root = str(paths.get("root") or "build/capability-audit/project")
    docs_dir = str(paths.get("docs_dir") or f"{root}/reports/latest/docs")
    scripts_dir = str(paths.get("scripts_dir") or f"{root}/reports/latest/scripts")
    reports_dir = str(paths.get("reports_dir") or f"{root}/reports/latest/reports")
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append(f'PROJECT_DIR="{project_root}"')
    lines.append('SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"')
    lines.append('REPORT_ROOT="${1:-$SCRIPT_DIR/reports/latest}"')
    lines.append('DOCS_DIR="$REPORT_ROOT/docs"')
    lines.append('SCRIPTS_DIR="$REPORT_ROOT/scripts"')
    lines.append('REPORTS_DIR="$REPORT_ROOT/reports"')
    lines.append('mkdir -p "$DOCS_DIR" "$SCRIPTS_DIR" "$REPORTS_DIR"')
    lines.append('echo "Collecting VHK capability-audit evidence..."')
    lines.append('vhk doctor --json > "$REPORTS_DIR/doctor.json" || true')
    lines.append('vhk validate "$PROJECT_DIR" --json > "$REPORTS_DIR/validate.json" || true')
    lines.append('vhk plan-project "$PROJECT_DIR" --json > "$REPORTS_DIR/plan-project.json" || true')
    lines.append('vhk gen-host-contract-pack "$PROJECT_DIR" --out-dir "$DOCS_DIR" --script-dir "$SCRIPTS_DIR" --force --quiet || true')
    lines.append('vhk gen-readiness-pack "$PROJECT_DIR" --out-dir "$DOCS_DIR" --script-dir "$SCRIPTS_DIR" --force --quiet || true')
    lines.append('vhk gen-activation-pack "$PROJECT_DIR" --out-dir "$DOCS_DIR" --script-dir "$SCRIPTS_DIR" --force --quiet || true')
    lines.append(f'vhk gen-capability-audit-pack "$PROJECT_DIR" --out-dir "$DOCS_DIR" --script-dir "$SCRIPTS_DIR" --build-root "$REPORT_ROOT/build" --force --quiet || true')
    lines.append('echo "Capability-audit capture complete: $REPORT_ROOT"')
    lines.append("")
    return "\n".join(lines)


def write_capability_audit_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    build_root: Path | None = None,
    force: bool = False,
    audit_doc: bool = True,
    fixups_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    handoff: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or project_dir / "docs").expanduser().resolve()
    script_dir = (script_dir or project_dir / "scripts").expanduser().resolve()
    build_root = (build_root.expanduser().resolve() if build_root is not None else None)

    plan = build_capability_audit_plan(
        project_dir,
        build_root=build_root,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane_profile,
    )

    written: dict[str, Path] = {}
    if audit_doc:
        path = out_dir / "VHK_CAPABILITY_AUDIT.md"
        _write_if_allowed(path, render_capability_audit_doc(plan), force=force)
        written["audit_doc"] = path
    if fixups_doc:
        path = out_dir / "VHK_CAPABILITY_FIXUPS.md"
        _write_if_allowed(path, render_capability_fixups_doc(plan), force=force)
        written["fixups_doc"] = path
    if plan_json:
        path = out_dir / "VHK_CAPABILITY_AUDIT_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, ensure_ascii=False, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_refresh_capability_audit_pack.sh"
        _write_if_allowed(path, render_refresh_script(project_dir, build_root=build_root), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path
    if handoff:
        paths = dict(plan.get("audit_paths") or {})
        root = project_dir / str(paths.get("root") or "build/capability-audit/project")
        readme_path = project_dir / str(paths.get("readme") or root / "README.md")
        manifest_path = project_dir / str(paths.get("manifest") or root / "vhk_capability_audit_handoff.json")
        collect_path = project_dir / str(paths.get("collect_script") or root / "collect_capability_audit.sh")
        _write_if_allowed(readme_path, render_handoff_readme(plan), force=force)
        _write_if_allowed(manifest_path, json.dumps({
            "project": dict(plan.get("project") or {}),
            "summary": dict(plan.get("capability_audit_summary") or {}),
            "paths": paths,
            "claim_summary": dict((plan.get("claim_audit") or {}).get("summary") or {}),
        }, ensure_ascii=False, indent=2) + "\n", force=force)
        _write_if_allowed(collect_path, render_collect_script(plan), force=force)
        collect_path.chmod(0o755)
        written["handoff_readme"] = readme_path
        written["handoff_manifest"] = manifest_path
        written["handoff_script"] = collect_path
    return written
