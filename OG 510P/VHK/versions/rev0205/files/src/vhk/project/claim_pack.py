from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from vhk.project.loader import load_project
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


def _recommended_claim_level(item: dict[str, Any]) -> str:
    score = int(item.get("score") or 0)
    blocker_count = len([str(x) for x in list(item.get("blocking_capabilities") or []) if str(x)])
    fit = str(item.get("fit") or "unknown").strip().lower()

    if fit in {"poor", "missing"} or score < 68:
        return "unsupported"
    if score >= 84 and blocker_count == 0:
        return "reference"
    if score >= 80 and blocker_count <= 1:
        return "supported"
    if score >= 74 and blocker_count <= 2:
        return "caveated"
    return "experimental"


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


def build_claim_plan(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
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
        level = _recommended_claim_level(item)
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
    plan["claim_commands"] = audit_commands
    plan["claim_summary"] = {
        "claim_count": len(recommended_claims),
        "reference_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "reference"),
        "supported_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "supported"),
        "caveated_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "caveated"),
        "experimental_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "experimental"),
        "unsupported_count": sum(1 for item in recommended_claims if item.get("recommended_level") == "unsupported"),
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
        "target_claims": [dict(item) for item in list(plan.get("recommended_claims") or []) if isinstance(item, dict)],
    }
    return yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)


def render_claim_audit_script(plan: dict[str, Any], *, out_dir: Path, script_dir: Path) -> str:
    docs_rel = out_dir.name if out_dir.name else "docs"
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
    lines.append(f"vhk gen-claim-pack . --out-dir ./{docs_rel} --script-dir ./{script_dir.name} --force >/dev/null")
    lines.append("")
    lines.append('echo "[3/4] Auditing target claims"')
    lines.append("vhk audit-target-claims .")
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

        maintainer_notes = str(row.get("maintainer_notes") or "").strip()
        evidence_status = str(row.get("evidence_status") or "").strip().lower()
        if claim_level in {"reference", "supported", "caveated"} and not maintainer_notes:
            warnings.append("Add maintainer_notes describing why this claim is believable for your project")
        if claim_level in {"reference", "supported"} and evidence_status not in {"verified", "planned"}:
            warnings.append("Use evidence_status=verified or planned for stronger claims")

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
            }
        )

    return {
        "project": dict(plan.get("project") or {}),
        "claims_file": str(claims_file),
        "summary": {
            "claims": len(results),
            "pass": pass_count,
            "warning": warning_count,
            "fail": fail_count,
        },
        "results": results,
    }
