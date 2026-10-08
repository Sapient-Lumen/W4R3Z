from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from vhk.project.loader import load_project
from vhk.project.claim_witness import claim_host_fit_for_target, claim_host_review_summary, recommended_claim_level
from vhk.project.strategy import summarize_project_strategy


_CLAIM_LEVELS = ["unsupported", "experimental", "caveated", "supported", "reference"]
_CLAIM_STRENGTH = {name: idx for idx, name in enumerate(_CLAIM_LEVELS)}

def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 5) -> list[dict[str, Any]]:
    return [dict(item) for item in list(items or [])[:limit] if isinstance(item, dict)]


def _first_text(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _required_artifacts(level: str) -> list[str]:
    base = [
        "docs/VHK_PORTABILITY_GUIDE.md",
        "docs/VHK_TARGET_ROLLOUT.md",
        "docs/VHK_PORTABILITY_PLAN.json",
    ]
    if level in {"reference", "supported", "caveated"}:
        base.extend(
            [
                "docs/VHK_OPERATOR_GUIDE.md",
                "docs/VHK_VERIFICATION_GUIDE.md",
            ]
        )
    if level in {"reference", "supported"}:
        base.append("scripts/vhk_verify_release.sh")
    return base


def _claim_caveats(item: dict[str, Any], *, level: str) -> list[str]:
    caveats: list[str] = []
    blockers = [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)]
    if blockers:
        caveats.append(
            "Blocking capabilities for this lane still include: " + ", ".join(f"`{name}`" for name in blockers[:4])
        )
    highlights = [str(x) for x in list(item.get("diff_highlights") or []) if str(x)]
    for text in highlights[:3]:
        caveats.append(text)
    if level in {"experimental", "unsupported"}:
        caveats.append("Keep marketing/release notes explicit: do not collapse this lane into a blanket \"Linux support\" claim.")
    elif level == "caveated":
        caveats.append("Ship this lane with caveats, setup notes, and rollback paths visible to operators and support.")
    elif level == "supported":
        caveats.append("Keep at least one alternate trigger/deployment surface documented in case compositor or portal behavior shifts.")
    return caveats


def _claim_summary(item: dict[str, Any], *, level: str) -> str:
    summary = _first_text(item, "summary", "why", "description", "notes")
    if not summary:
        summary = "Review this desktop lane before promising support."
    if level == "reference":
        return summary + " This is the best candidate for a reference support lane."
    if level == "supported":
        return summary + " This looks supportable if its current blockers stay documented and verified."
    if level == "caveated":
        return summary + " This should ship only with explicit caveats and target-specific setup notes."
    if level == "experimental":
        return summary + " Treat this as experimental until the project proves the missing or degraded pieces on a real session."
    return summary + " Keep this outside the supported matrix for now."

def _claim_yaml_row(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "target": str(item.get("target") or ""),
        "title": str(item.get("title") or item.get("target") or "target"),
        "score": int(item.get("score") or 0),
        "fit": str(item.get("fit") or "unknown"),
        "recommended_level": str(item.get("recommended_level") or "unsupported"),
        "claim_level": str(item.get("claim_level") or item.get("recommended_level") or "unsupported"),
        "summary": str(item.get("summary") or ""),
        "blocking_capabilities": [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)],
        "preferred_surfaces": [dict(x) for x in list(item.get("preferred_surfaces") or []) if isinstance(x, Mapping)],
        "required_artifacts": [str(x) for x in list(item.get("required_artifacts") or []) if str(x)],
        "required_commands": [str(x) for x in list(item.get("required_commands") or []) if str(x)],
        "caveats": [str(x) for x in list(item.get("caveats") or []) if str(x)],
        "evidence_status": str(item.get("evidence_status") or "planned"),
        "maintainer_notes": str(item.get("maintainer_notes") or ""),
    }


def build_claim_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Any]:
    """Load a VHK project and emit a planner-backed support-claim payload."""

    project = load_project(project_dir)
    plan = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )

    environment_diffs = [dict(item) for item in list(plan.get("environment_diffs") or []) if isinstance(item, dict)]

    recommended_claims: list[dict[str, Any]] = []
    for item in sorted(environment_diffs, key=lambda row: (-int(row.get("score") or 0), str(row.get("title") or ""))):
        level = recommended_claim_level(item)
        preferred_surfaces = [
            {
                "id": str(surface.get("id") or ""),
                "title": str(surface.get("title") or surface.get("id") or "surface"),
                "category": str(surface.get("category") or ""),
                "fit": str(surface.get("fit") or ""),
            }
            for surface in list(item.get("preferred_surfaces") or [])[:4]
            if isinstance(surface, dict)
        ]
        recommended_claims.append(
            {
                "target": str(item.get("id") or ""),
                "title": str(item.get("title") or item.get("id") or "environment"),
                "score": int(item.get("score") or 0),
                "fit": str(item.get("fit") or "unknown"),
                "recommended_level": level,
                "claim_level": level,
                "summary": _claim_summary(item, level=level),
                "blocking_capabilities": [str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)],
                "preferred_surfaces": preferred_surfaces,
                "required_artifacts": _required_artifacts(level),
                "required_commands": [str(x) for x in list(item.get("commands") or []) if str(x)][:6],
                "caveats": _claim_caveats(item, level=level),
                "evidence_status": "planned",
                "maintainer_notes": "",
            }
        )

    host_plan: dict[str, Any] = {}
    host_summary: dict[str, Any] = {}
    portal_route_contract: dict[str, Any] = {}
    selected_evidence_lane: dict[str, Any] = {}
    evidence_lane_fit: dict[str, Any] = {}
    host_requirements: list[dict[str, Any]] = []
    if host_snapshot is not None or capability_matrix or capability_issues:
        try:
            from vhk.project.host_contract_pack import build_host_contract_plan

            host_plan = build_host_contract_plan(
                project_dir,
                capability_usage=capability_usage,
                capability_matrix=capability_matrix,
                capability_issues=capability_issues,
                host_snapshot=host_snapshot,
            )
        except Exception:
            host_plan = {}
        host_summary = dict(host_plan.get("host_summary") or {})
        portal_route_contract = dict(host_plan.get("portal_route_contract") or {})
        host_requirements = [dict(item) for item in list(host_plan.get("host_requirements") or []) if isinstance(item, Mapping)]
        if host_summary or portal_route_contract:
            from vhk.project.target_fit_contract import build_target_fit_contract_from_lane, select_target_lane

            for row in recommended_claims:
                row["current_host_fit"] = claim_host_fit_for_target(
                    str(row.get("target") or ""),
                    title=str(row.get("title") or row.get("target") or "target"),
                    host_summary=host_summary,
                    portal_route_contract=portal_route_contract,
                )
            selected_evidence_lane = select_target_lane(
                project_dir,
                bundle_target_profile=evidence_lane_profile,
                capability_usage=capability_usage,
            )
            if selected_evidence_lane:
                evidence_lane_fit = build_target_fit_contract_from_lane(
                    selected_evidence_lane,
                    host_truth=host_summary,
                    host_requirements=host_requirements,
                    portal_route_contract=portal_route_contract,
                )
                if evidence_lane_fit:
                    evidence_lane_fit["selection_source"] = "explicit" if evidence_lane_profile else "flagship-default"
                    evidence_lane_fit["requested_profile_id"] = str(evidence_lane_profile or "").strip() or None

    audit_commands = [
        "vhk doctor --json",
        "vhk validate . --json",
        "vhk plan-project . --json",
        "vhk gen-operator-pack . --force",
        "vhk gen-verification-pack . --force",
        "vhk gen-portability-pack . --force",
        "vhk gen-claim-pack . --force",
        "vhk audit-target-claims .",
    ]

    plan["claim_paths"] = {
        "project_root": str(Path(project.root_dir)),
        "docs_dir": "docs",
        "scripts_dir": "scripts",
        "claims_file": "docs/VHK_TARGET_CLAIMS.yaml",
    }
    plan["claim_levels"] = {
        "reference": "Strongest lane; suitable as a reference environment in release notes and docs.",
        "supported": "Shippable lane with verified docs/artifacts, but not necessarily the flagship environment.",
        "caveated": "Supported only with explicit setup notes, helper boundaries, or desktop-specific caveats.",
        "experimental": "Available for testing, but not yet something the project should promise broadly.",
        "unsupported": "Outside the supported matrix for now.",
    }
    plan["recommended_claims"] = recommended_claims
    plan["host_truth"] = host_summary
    plan["portal_route_contract"] = portal_route_contract
    if selected_evidence_lane:
        plan["selected_evidence_lane"] = {
            "profile_id": str(selected_evidence_lane.get("profile_id") or ""),
            "title": str(selected_evidence_lane.get("title") or selected_evidence_lane.get("profile_id") or "target"),
            "release_level": str(selected_evidence_lane.get("release_level") or ""),
            "backend": str(selected_evidence_lane.get("backend") or ""),
            "desktop_family": str(selected_evidence_lane.get("desktop_family") or ""),
            "trigger_route_id": str(selected_evidence_lane.get("trigger_route_id") or ""),
            "overall_status": str(selected_evidence_lane.get("overall_status") or ""),
            "selection_source": "explicit" if evidence_lane_profile else "flagship-default",
            "requested_profile_id": str(evidence_lane_profile or "").strip() or None,
        }
    if evidence_lane_fit:
        plan["evidence_lane_fit"] = evidence_lane_fit
    claim_host_review = claim_host_review_summary(recommended_claims)
    plan["claim_host_review"] = claim_host_review if int(claim_host_review.get("claims_with_current_host_review") or 0) > 0 else {}
    plan["claim_commands"] = audit_commands
    plan["claim_summary"] = {
        "claim_count": len(recommended_claims),
        "reference_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "reference"),
        "supported_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "supported"),
        "caveated_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "caveated"),
        "experimental_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "experimental"),
        "unsupported_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "unsupported"),
        "selected_evidence_lane_id": str((plan.get("selected_evidence_lane") or {}).get("profile_id") or ""),
        "selected_evidence_lane_fit_status": str((plan.get("evidence_lane_fit") or {}).get("status") or "unknown"),
    }
    return plan


def render_claim_guide(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    overview = dict(plan.get("overview") or {})
    claim_paths = dict(plan.get("claim_paths") or {})
    claim_levels = dict(plan.get("claim_levels") or {})
    recommended_claims = _trim_items(plan.get("recommended_claims"), limit=8)
    session_capabilities = dict(plan.get("session_capabilities") or {})
    session_issues = list(plan.get("session_issues") or [])
    host_truth = dict(plan.get("host_truth") or {})
    portal_route_contract = dict(plan.get("portal_route_contract") or {})
    claim_host_review = dict(plan.get("claim_host_review") or {})
    claim_commands = [str(item).strip() for item in list(plan.get("claim_commands") or []) if str(item).strip()]

    lines: list[str] = []
    lines.append(f"# VHK claim guide for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-claim-pack`. Use it to turn Linux support claims into something reviewable and auditable instead of a vague compatibility slogan.")
    if session_capabilities:
        lines.append("This guide is session-aware: rerun it on a real desktop when you want the current machine to influence the claim audit.")
    else:
        lines.append("This guide is capability-agnostic: rerun it with session checks on the desktop you want to ship before locking down support claims.")
    lines.append("")

    lines.append("## Project snapshot")
    lines.append("")
    lines.append(f"- Root: `{project.get('root_dir') or '.'}`")
    lines.append(f"- Desktop backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Macros: {overview.get('macros', 0)}")
    lines.append(f"- Bindings: {overview.get('bindings', 0)}")
    lines.append(f"- Hotstrings: {overview.get('hotstrings', 0)}")
    lines.append(f"- Clipboard watchers: {overview.get('clipboard_watchers', 0)}")
    lines.append(f"- Bus watchers: {overview.get('bus_watchers', 0)}")
    lines.append(f"- Window watchers: {overview.get('window_watchers', 0)}")
    if claim_paths:
        lines.append(f"- Claim file: `{claim_paths.get('claims_file') or 'docs/VHK_TARGET_CLAIMS.yaml'}`")
    lines.append("")

    if claim_levels:
        lines.append("## Claim level glossary")
        lines.append("")
        for level in ["reference", "supported", "caveated", "experimental", "unsupported"]:
            desc = str(claim_levels.get(level) or "").strip()
            if desc:
                lines.append(f"- **{level}** — {desc}")
        lines.append("")

    selected_evidence_lane = dict(plan.get("selected_evidence_lane") or {})
    evidence_lane_fit = dict(plan.get("evidence_lane_fit") or {})

    if host_truth or portal_route_contract or claim_host_review or evidence_lane_fit:
        lines.append("## Current host review")
        lines.append("")
        lines.append(f"- Host truth status: `{host_truth.get('overall_status') or host_truth.get('status') or 'unknown'}`")
        lines.append(f"- Portal route status: `{portal_route_contract.get('status') or 'unknown'}`")
        lines.append(f"- XDG_CURRENT_DESKTOP: `{portal_route_contract.get('xdg_current_desktop') or 'unknown'}`")
        if claim_host_review:
            lines.append(f"- Claim evidence alignment (aligned/degraded/drifted/neutral/unknown): {claim_host_review.get('aligned_count') or 0}/{claim_host_review.get('degraded_count') or 0}/{claim_host_review.get('drifted_count') or 0}/{claim_host_review.get('neutral_count') or 0}/{claim_host_review.get('unknown_count') or 0}")
        if evidence_lane_fit:
            lines.append(f"- Selected evidence lane: `{selected_evidence_lane.get('profile_id') or evidence_lane_fit.get('profile_id') or 'unknown'}` ({selected_evidence_lane.get('title') or evidence_lane_fit.get('profile_title') or 'target'})")
            lines.append(f"- Evidence lane fit: `{evidence_lane_fit.get('status') or 'unknown'}` · source `{evidence_lane_fit.get('selection_source') or 'flagship-default'}`")
            lines.append(f"- Evidence lane requirements (aligned/degraded/drifted/ahead/outside-profile/unknown): {len(evidence_lane_fit.get('aligned_requirement_ids') or [])}/{len(evidence_lane_fit.get('degraded_requirement_ids') or [])}/{len(evidence_lane_fit.get('drifted_requirement_ids') or [])}/{len(evidence_lane_fit.get('ahead_requirement_ids') or [])}/{len(evidence_lane_fit.get('outside_profile_requirement_ids') or [])}/{len(evidence_lane_fit.get('unknown_requirement_ids') or [])}")
        lines.append("")

    if recommended_claims:
        lines.append("## Recommended target claims")
        lines.append("")
        lines.append("Start from these recommendations, then edit `docs/VHK_TARGET_CLAIMS.yaml` only when you have stronger evidence than the planner currently sees.")
        lines.append("")
        for item in recommended_claims:
            title = item.get("title") or item.get("target") or "target"
            lines.append(f"### {title}")
            lines.append(f"Recommended level: `{item.get('recommended_level') or 'unsupported'}` · Fit: `{item.get('fit') or 'unknown'}` · Score: {item.get('score') or 0}")
            summary = _first_text(item, "summary", "why", "description", "notes")
            if summary:
                lines.append("")
                lines.append(summary)
            preferred_surfaces = [dict(x) for x in list(item.get("preferred_surfaces") or []) if isinstance(x, dict)]
            if preferred_surfaces:
                lines.append("")
                lines.append("Preferred surfaces:")
                for surface in preferred_surfaces[:4]:
                    lines.append(f"- {surface.get('title') or surface.get('id') or 'surface'}")
            current_host_fit = dict(item.get("current_host_fit") or {})
            if current_host_fit:
                lines.append("")
                lines.append(f"Current host review: `{current_host_fit.get('status') or 'unknown'}` · desktop `{current_host_fit.get('desktop_match_status') or 'unknown'}` · portal `{current_host_fit.get('portal_route_status') or 'unknown'}`")
                notes = [str(x) for x in list(current_host_fit.get("notes") or []) if str(x)]
                for text in notes[:3]:
                    lines.append(f"- {text}")
            caveats = [str(x) for x in list(item.get("caveats") or []) if str(x)]
            if caveats:
                lines.append("")
                lines.append("Claim caveats:")
                for text in caveats[:4]:
                    lines.append(f"- {text}")
            artifacts = [str(x) for x in list(item.get("required_artifacts") or []) if str(x)]
            if artifacts:
                lines.append("")
                lines.append("Expected proof artifacts:")
                for path in artifacts[:5]:
                    lines.append(f"- `{path}`")
            lines.append("")

    if session_issues:
        lines.append("## Current session issues")
        lines.append("")
        for issue in session_issues[:8]:
            msg = str(issue.get("message") or "session issue")
            sev = str(issue.get("severity") or "warning")
            suggestion = str(issue.get("suggestion") or "")
            if suggestion:
                lines.append(f"- **{sev}** — {msg} ({suggestion})")
            else:
                lines.append(f"- **{sev}** — {msg}")
        lines.append("")

    if claim_commands:
        lines.append("## Claim audit commands")
        lines.append("")
        for cmd in claim_commands:
            lines.append(f"- `{cmd}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_target_claims_yaml(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    payload = {
        "schema": "vhk.target_claims.v1",
        "project": {
            "name": str(project.get("name") or "project"),
            "root_dir": str(project.get("root_dir") or "."),
            "desktop_backend": str(project.get("desktop_backend") or "unknown"),
        },
        "claim_levels": dict(plan.get("claim_levels") or {}),
        "target_claims": [_claim_yaml_row(item) for item in list(plan.get("recommended_claims") or []) if isinstance(item, Mapping)],
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def render_claim_audit_script(plan: dict[str, Any], *, out_dir: Path, script_dir: Path) -> str:
    docs_rel = out_dir.name if out_dir.name else "docs"
    selected_evidence_lane = dict(plan.get("selected_evidence_lane") or {})
    evidence_arg = ""
    if str(selected_evidence_lane.get("selection_source") or "") == "explicit" and str(selected_evidence_lane.get("profile_id") or ""):
        evidence_arg = f" --evidence-lane {selected_evidence_lane.get('profile_id')}"
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('echo "[1/4] Refreshing capability facts"')
    lines.append("vhk doctor --json > ./claim_audit.doctor.json")
    lines.append("vhk validate . --json > ./claim_audit.validate.json")
    lines.append("")
    lines.append('echo "[2/4] Refreshing planner-backed packs"')
    lines.append("vhk gen-operator-pack . --force >/dev/null")
    lines.append("vhk gen-verification-pack . --force >/dev/null")
    lines.append("vhk gen-portability-pack . --force >/dev/null")
    lines.append(f"vhk gen-claim-pack . --out-dir ./{docs_rel} --script-dir ./{script_dir.name} --force{evidence_arg} >/dev/null")
    lines.append("")
    lines.append('echo "[3/4] Auditing target claims"')
    lines.append(f"vhk audit-target-claims .{evidence_arg}")
    lines.append("")
    lines.append('echo "[4/4] Review complete"')
    lines.append('echo "Check docs/VHK_TARGET_CLAIMS.yaml before changing release notes or claiming broader Linux support."')
    lines.append("")
    return "\n".join(lines)


def write_claim_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    guide: bool = True,
    claims: bool = True,
    plan_json: bool = True,
    script: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Path]:
    """Write planner-backed claim artifacts for an existing project."""

    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_claim_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane_profile,
    )

    written: dict[str, Path] = {}
    if guide:
        path = out_dir / "VHK_CLAIM_GUIDE.md"
        _write_if_allowed(path, render_claim_guide(plan), force=force)
        written["guide"] = path
    if claims:
        path = out_dir / "VHK_TARGET_CLAIMS.yaml"
        _write_if_allowed(path, render_target_claims_yaml(plan), force=force)
        written["claims"] = path
    if plan_json:
        path = out_dir / "VHK_CLAIM_AUDIT_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2) + "\n", force=force)
        written["plan_json"] = path
    if script:
        path = script_dir / "vhk_audit_claims.sh"
        _write_if_allowed(path, render_claim_audit_script(plan, out_dir=out_dir, script_dir=script_dir), force=force)
        path.chmod(path.stat().st_mode | 0o111)
        written["script"] = path
    return written


def _load_claims_file(claims_file: Path) -> dict[str, Any]:
    payload = yaml.safe_load(claims_file.read_text()) or {}
    if not isinstance(payload, dict):
        raise ValueError("Target claims file must be a mapping")
    claims = payload.get("target_claims")
    if claims is None:
        payload["target_claims"] = []
    elif not isinstance(claims, list):
        raise ValueError("Target claims file 'target_claims' must be a list")
    return payload


def audit_target_claims(
    project_dir: Path,
    *,
    claims_file: Path | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    host_snapshot: dict[str, object] | None = None,
    evidence_lane_profile: str | None = None,
) -> dict[str, Any]:
    """Audit a project's target support claims against the current planner output."""

    project_dir = project_dir.expanduser().resolve()
    claims_file = (claims_file or (project_dir / "docs" / "VHK_TARGET_CLAIMS.yaml")).expanduser().resolve()
    if not claims_file.exists():
        raise FileNotFoundError(f"Missing target claims file: {claims_file}")

    plan = build_claim_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane_profile,
    )
    recommended = {str(item.get("target") or ""): dict(item) for item in list(plan.get("recommended_claims") or []) if isinstance(item, dict)}
    claim_doc = _load_claims_file(claims_file)
    claim_rows = [dict(item) for item in list(claim_doc.get("target_claims") or []) if isinstance(item, dict)]

    results: list[dict[str, Any]] = []
    pass_count = 0
    warning_count = 0
    fail_count = 0

    for row in claim_rows:
        target = str(row.get("target") or "").strip()
        title = str(row.get("title") or target or "target")
        claim_level = str(row.get("claim_level") or "unsupported").strip().lower()
        recommendation = recommended.get(target)
        issues: list[str] = []
        warnings: list[str] = []

        if claim_level not in _CLAIM_STRENGTH:
            issues.append(f"Unknown claim_level `{claim_level}`")
            recommended_level = "unsupported"
            expected_title = title
            required_artifacts: list[str] = []
        elif recommendation is None:
            issues.append("Target is not present in the current planner output")
            recommended_level = "unsupported"
            expected_title = title
            required_artifacts = []
        else:
            recommended_level = str(recommendation.get("recommended_level") or "unsupported")
            expected_title = str(recommendation.get("title") or title or target)
            required_artifacts = [str(x) for x in list(row.get("required_artifacts") or recommendation.get("required_artifacts") or []) if str(x)]
            if _CLAIM_STRENGTH[claim_level] > _CLAIM_STRENGTH.get(recommended_level, 0):
                issues.append(f"Claim `{claim_level}` is stronger than the current recommendation `{recommended_level}`")

        current_host_fit = dict((recommendation or {}).get("current_host_fit") or {})
        current_host_fit_status = str(current_host_fit.get("status") or "")
        maintainer_notes = str(row.get("maintainer_notes") or "").strip()
        evidence_status = str(row.get("evidence_status") or "").strip().lower()
        if claim_level in {"reference", "supported", "caveated"} and not maintainer_notes:
            warnings.append("Add maintainer_notes describing why this claim is believable for your project")
        if claim_level in {"reference", "supported"} and evidence_status not in {"verified", "planned"}:
            warnings.append("Use evidence_status=verified or planned for stronger claims")
        if current_host_fit_status == "drifted":
            text = "Current host drifts from this target claim: " + "; ".join([str(x) for x in list(current_host_fit.get("notes") or [])[:2]])
            if claim_level in {"reference", "supported"} and evidence_status == "verified":
                issues.append(text)
            else:
                warnings.append(text)
        elif current_host_fit_status == "degraded":
            text = "Current host is only partial proof for this target claim: " + "; ".join([str(x) for x in list(current_host_fit.get("notes") or [])[:2]])
            if claim_level == "reference" and evidence_status == "verified":
                issues.append(text)
            elif claim_level in {"reference", "supported"}:
                warnings.append(text)
        elif current_host_fit_status == "unknown" and claim_level in {"reference", "supported"} and evidence_status == "verified":
            warnings.append("Current host review is still unknown, so this machine should not be treated as sole verified proof for a strong claim")

        missing_artifacts = [path for path in required_artifacts if not (project_dir / path).exists()]
        if missing_artifacts:
            text = "Missing required artifacts: " + ", ".join(f"`{path}`" for path in missing_artifacts[:5])
            if claim_level in {"reference", "supported"}:
                issues.append(text)
            else:
                warnings.append(text)

        if issues:
            status = "fail"
            fail_count += 1
        elif warnings:
            status = "warning"
            warning_count += 1
        else:
            status = "pass"
            pass_count += 1

        results.append(
            {
                "target": target,
                "title": expected_title,
                "claim_level": claim_level,
                "recommended_level": recommended_level,
                "status": status,
                "issues": issues,
                "warnings": warnings,
                "current_host_fit": current_host_fit,
            }
        )

    evidence_lane = dict(plan.get("selected_evidence_lane") or {})
    evidence_lane_fit = dict(plan.get("evidence_lane_fit") or {})

    fit_counts = {
        "aligned": sum(1 for item in results if str((item.get("current_host_fit") or {}).get("status") or "") == "aligned"),
        "degraded": sum(1 for item in results if str((item.get("current_host_fit") or {}).get("status") or "") == "degraded"),
        "drifted": sum(1 for item in results if str((item.get("current_host_fit") or {}).get("status") or "") == "drifted"),
        "neutral": sum(1 for item in results if str((item.get("current_host_fit") or {}).get("status") or "") == "neutral"),
        "unknown": sum(1 for item in results if str((item.get("current_host_fit") or {}).get("status") or "") == "unknown"),
    }

    return {
        "project": dict(plan.get("project") or {}),
        "claims_file": str(claims_file),
        "summary": {
            "claims": len(results),
            "pass": pass_count,
            "warning": warning_count,
            "fail": fail_count,
            "fit_aligned": fit_counts["aligned"],
            "fit_degraded": fit_counts["degraded"],
            "fit_drifted": fit_counts["drifted"],
            "fit_neutral": fit_counts["neutral"],
            "fit_unknown": fit_counts["unknown"],
        },
        "results": results,
        "selected_evidence_lane": evidence_lane,
        "evidence_lane_fit": evidence_lane_fit,
    }
