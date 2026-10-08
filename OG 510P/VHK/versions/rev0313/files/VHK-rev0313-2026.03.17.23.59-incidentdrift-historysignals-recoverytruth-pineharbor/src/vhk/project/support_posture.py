from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from vhk.project.publish_pack import build_publish_plan


def load_or_build_publish_plan(
    project_dir: str | Path,
    *,
    prefer_cached: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    """Load docs/VHK_PUBLISH_PLAN.json when present, otherwise rebuild it.

    This keeps outward-facing surfaces cheap when a project has already generated
    its publish pack, but still gives bundle/export commands something useful on
    fresh projects that have not emitted docs yet.
    """

    project_path = Path(project_dir).expanduser().resolve()
    cached = project_path / "docs" / "VHK_PUBLISH_PLAN.json"
    if prefer_cached and cached.exists():
        try:
            payload = json.loads(cached.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
    return build_publish_plan(
        project_path,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )


def load_or_build_release_lane_plan(
    project_dir: str | Path,
    *,
    prefer_cached: bool = True,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any] | None:
    """Load docs/VHK_RELEASE_LANE_PLAN.json when present, otherwise rebuild it.

    Imported lazily to avoid circular imports: release-lane planning currently
    consumes support posture, while support posture also wants to enrich itself
    with release-lane summaries when available.
    """

    project_path = Path(project_dir).expanduser().resolve()
    cached = project_path / "docs" / "VHK_RELEASE_LANE_PLAN.json"
    if prefer_cached and cached.exists():
        try:
            payload = json.loads(cached.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
    try:
        from vhk.project.release_lane_pack import build_release_lane_plan

        return build_release_lane_plan(
            project_path,
            target_profiles=target_profiles,
            capability_usage=capability_usage,
        )
    except Exception:
        return None


def load_or_build_release_deploy_plan(
    project_dir: str | Path,
    *,
    prefer_cached: bool = True,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any] | None:
    """Load docs/VHK_RELEASE_DEPLOY_PLAN.json when present, otherwise rebuild it."""

    project_path = Path(project_dir).expanduser().resolve()
    cached = project_path / "docs" / "VHK_RELEASE_DEPLOY_PLAN.json"
    if prefer_cached and cached.exists():
        try:
            payload = json.loads(cached.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except Exception:
            pass
    try:
        from vhk.project.release_deploy_pack import build_release_deploy_plan

        return build_release_deploy_plan(
            project_path,
            target_profiles=target_profiles,
            capability_usage=capability_usage,
        )
    except Exception:
        return None


def _release_lane_titles(rows: list[dict[str, Any]], *, level: str) -> list[str]:
    return [
        str(item.get("title") or item.get("profile_id") or "target")
        for item in rows
        if str(item.get("release_level") or "") == level
    ]


def summarize_release_lane_posture(plan: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(plan, dict):
        return {}
    rows = [dict(item) for item in list(plan.get("release_lanes") or []) if isinstance(item, dict)]
    if not rows:
        return {}

    docs = [
        "docs/VHK_RELEASE_LANES.md",
        "docs/VHK_RELEASE_SNIPPETS.md",
        "docs/VHK_RELEASE_LANE_PLAN.json",
    ]
    summary = dict(plan.get("release_summary") or {})
    flagship = next(
        (
            dict(item)
            for item in rows
            if str(item.get("release_level") or "") in {"reference", "supported"}
        ),
        dict(rows[0]),
    )
    return {
        "flagship_lane_id": str(flagship.get("profile_id") or ""),
        "flagship_lane_title": str(flagship.get("title") or flagship.get("profile_id") or ""),
        "flagship_release_level": str(flagship.get("release_level") or "experimental"),
        "flagship_release_headline": str(flagship.get("release_headline") or ""),
        "flagship_public_snippet": str(flagship.get("public_snippet") or ""),
        "lane_count": len(rows),
        "reference_lane_ids": [str(x) for x in list(summary.get("reference_lane_ids") or []) if str(x)]
        or [str(item.get("profile_id") or "") for item in rows if str(item.get("release_level") or "") == "reference"],
        "supported_lane_ids": [str(x) for x in list(summary.get("supported_lane_ids") or []) if str(x)]
        or [str(item.get("profile_id") or "") for item in rows if str(item.get("release_level") or "") == "supported"],
        "caveated_lane_ids": [str(x) for x in list(summary.get("caveated_lane_ids") or []) if str(x)]
        or [str(item.get("profile_id") or "") for item in rows if str(item.get("release_level") or "") == "caveated"],
        "experimental_lane_ids": [str(x) for x in list(summary.get("experimental_lane_ids") or []) if str(x)]
        or [str(item.get("profile_id") or "") for item in rows if str(item.get("release_level") or "") == "experimental"],
        "reference_lane_titles": _release_lane_titles(rows, level="reference"),
        "supported_lane_titles": _release_lane_titles(rows, level="supported"),
        "caveated_lane_titles": _release_lane_titles(rows, level="caveated"),
        "experimental_lane_titles": _release_lane_titles(rows, level="experimental"),
        "docs": docs,
    }


def summarize_release_deploy_posture(plan: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(plan, dict):
        return {}
    rows = [dict(item) for item in list(plan.get("deploy_lanes") or []) if isinstance(item, dict)]
    if not rows:
        return {}

    docs = [
        "docs/VHK_RELEASE_DEPLOYMENT.md",
        "docs/VHK_RELEASE_INSTALL_SNIPPETS.md",
        "docs/VHK_RELEASE_DEPLOY_PLAN.json",
    ]
    summary = dict(plan.get("deploy_summary") or {})
    flagship = next(
        (
            dict(item)
            for item in rows
            if str(item.get("release_level") or "") in {"reference", "supported"}
        ),
        dict(rows[0]),
    )
    return {
        "flagship_lane_id": str(flagship.get("profile_id") or ""),
        "flagship_lane_title": str(flagship.get("title") or flagship.get("profile_id") or ""),
        "flagship_release_level": str(flagship.get("release_level") or "experimental"),
        "flagship_deploy_style": str(flagship.get("deploy_style") or ""),
        "flagship_delivery_headline": str(flagship.get("delivery_headline") or ""),
        "lane_count": len(rows),
        "docs": docs,
        "reference_lane_ids": [str(x) for x in list((plan.get("release_summary") or {}).get("reference_lane_ids") or []) if str(x)],
        "supported_lane_ids": [str(x) for x in list((plan.get("release_summary") or {}).get("supported_lane_ids") or []) if str(x)],
        "caveated_lane_ids": [str(x) for x in list((plan.get("release_summary") or {}).get("caveated_lane_ids") or []) if str(x)],
        "experimental_lane_ids": [str(x) for x in list((plan.get("release_summary") or {}).get("experimental_lane_ids") or []) if str(x)],
        "deploy_summary": summary,
    }


def _merge_release_deploy_posture(posture: dict[str, Any], release_deploy_plan: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(posture)
    overview = summarize_release_deploy_posture(release_deploy_plan)
    if not overview:
        merged["release_deploy_overview"] = {}
        return merged

    docs = [str(x) for x in list(merged.get("docs") or []) if str(x)]
    for path in list(overview.get("docs") or []):
        text = str(path)
        if text and text not in docs:
            docs.append(text)
    merged["docs"] = docs
    merged["release_deploy_overview"] = overview
    merged["flagship_deploy_style"] = str(overview.get("flagship_deploy_style") or "")
    merged["flagship_delivery_headline"] = str(overview.get("flagship_delivery_headline") or "")
    return merged


def _merge_release_lane_posture(posture: dict[str, Any], release_lane_plan: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(posture)
    overview = summarize_release_lane_posture(release_lane_plan)
    if not overview:
        merged["release_lane_overview"] = {}
        return merged

    docs = [str(x) for x in list(merged.get("docs") or []) if str(x)]
    for path in list(overview.get("docs") or []):
        text = str(path)
        if text and text not in docs:
            docs.append(text)
    merged["docs"] = docs
    merged["release_lane_overview"] = overview
    merged["flagship_lane_id"] = str(overview.get("flagship_lane_id") or "")
    merged["flagship_lane_title"] = str(overview.get("flagship_lane_title") or "")
    merged["flagship_release_level"] = str(overview.get("flagship_release_level") or "")
    merged["release_lane_reference_ids"] = [str(x) for x in list(overview.get("reference_lane_ids") or []) if str(x)]
    merged["release_lane_supported_ids"] = [str(x) for x in list(overview.get("supported_lane_ids") or []) if str(x)]
    merged["release_lane_caveated_ids"] = [str(x) for x in list(overview.get("caveated_lane_ids") or []) if str(x)]
    merged["release_lane_experimental_ids"] = [str(x) for x in list(overview.get("experimental_lane_ids") or []) if str(x)]
    return merged


def summarize_support_posture(
    project_dir: str | Path,
    *,
    prefer_cached: bool = True,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
    include_release_lanes: bool = True,
    include_release_deploy: bool = True,
) -> dict[str, Any]:
    plan = load_or_build_publish_plan(
        project_dir,
        prefer_cached=prefer_cached,
        capability_usage=capability_usage,
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )
    posture = summarize_support_posture_from_plan(plan)
    if include_release_lanes:
        release_lane_plan = load_or_build_release_lane_plan(
            project_dir,
            prefer_cached=prefer_cached,
            capability_usage=capability_usage,
        )
        posture = _merge_release_lane_posture(posture, release_lane_plan)
    elif include_release_deploy:
        posture = dict(posture)
        posture["release_lane_overview"] = {}
    if include_release_deploy:
        release_deploy_plan = load_or_build_release_deploy_plan(
            project_dir,
            prefer_cached=prefer_cached,
            capability_usage=capability_usage,
        )
        posture = _merge_release_deploy_posture(posture, release_deploy_plan)
    return posture


def summarize_support_posture_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    project = dict(plan.get("project") or {})
    story = dict(plan.get("bundle_release_story") or {})
    matrix = [dict(item) for item in list(plan.get("public_support_matrix") or []) if isinstance(item, dict)]
    publish_paths = dict(plan.get("publish_paths") or {})
    docs = [
        str(publish_paths.get("public_support_doc") or "docs/VHK_PUBLIC_SUPPORT.md"),
        str(publish_paths.get("install_quickstart_doc") or "docs/VHK_INSTALL_QUICKSTART.md"),
    ]
    docs = [doc for doc in docs if doc]

    def _rows(level: str) -> list[dict[str, Any]]:
        return [row for row in matrix if str(row.get("claim_level") or "unsupported") == level]

    def _titles(level: str) -> list[str]:
        rows = _rows(level)
        return [str(row.get("title") or row.get("target") or "target") for row in rows]

    summary_rows = []
    for row in matrix[:8]:
        summary_rows.append(
            {
                "target": str(row.get("target") or ""),
                "title": str(row.get("title") or row.get("target") or "target"),
                "claim_level": str(row.get("claim_level") or "unsupported"),
                "recommended_level": str(row.get("recommended_level") or row.get("claim_level") or "unsupported"),
                "audit_status": str(row.get("audit_status") or "recommended"),
                "fit": str(row.get("fit") or "unknown"),
                "present_artifacts": [str(x) for x in list(row.get("present_artifacts") or []) if str(x)],
                "missing_artifacts": [str(x) for x in list(row.get("missing_artifacts") or []) if str(x)],
            }
        )

    return {
        "project": {
            "name": str(project.get("name") or "project"),
            "root_dir": str(project.get("root_dir") or "."),
            "desktop_backend": str(project.get("desktop_backend") or "unknown"),
        },
        "claim_source": str(plan.get("claim_source") or "planner_recommendations"),
        "headline": str(plan.get("publish_headline") or story.get("headline") or "Support posture unavailable"),
        "language_guardrails": [str(x) for x in list(plan.get("language_guardrails") or []) if str(x)][:6],
        "reference_targets": _titles("reference"),
        "supported_targets": _titles("supported"),
        "caveated_targets": _titles("caveated"),
        "experimental_targets": _titles("experimental"),
        "unsupported_targets": _titles("unsupported"),
        "docs": docs,
        "matrix": summary_rows,
    }


def render_support_about_text(posture: dict[str, Any]) -> str:
    project = dict(posture.get("project") or {})
    headline = str(posture.get("headline") or "Support posture unavailable")
    docs = [str(x) for x in list(posture.get("docs") or []) if str(x)]
    lane_overview = dict(posture.get("release_lane_overview") or {})

    lines = [f"VHK support posture for {project.get('name') or 'project'}", "", headline]
    for label, key in [
        ("Reference", "reference_targets"),
        ("Supported", "supported_targets"),
        ("Caveated", "caveated_targets"),
        ("Experimental", "experimental_targets"),
    ]:
        values = [str(x) for x in list(posture.get(key) or []) if str(x)]
        if values:
            lines.append(f"{label}: " + ", ".join(values[:4]))
    flagship = str(lane_overview.get("flagship_lane_title") or lane_overview.get("flagship_lane_id") or "").strip()
    if flagship:
        lines.append("")
        lines.append(f"Flagship release lane: {flagship}")
        headline_text = str(lane_overview.get("flagship_release_headline") or "").strip()
        if headline_text:
            lines.append(headline_text)
    deploy_overview = dict(posture.get("release_deploy_overview") or {})
    deploy_style = str(deploy_overview.get("flagship_deploy_style") or posture.get("flagship_deploy_style") or "").strip()
    delivery = str(deploy_overview.get("flagship_delivery_headline") or posture.get("flagship_delivery_headline") or "").strip()
    if deploy_style or delivery:
        lines.append("")
        if deploy_style:
            lines.append(f"Flagship deploy style: {deploy_style}")
        if delivery:
            lines.append(delivery)
    guardrails = [str(x) for x in list(posture.get("language_guardrails") or []) if str(x)]
    if guardrails:
        lines.append("")
        lines.append("Guardrails:")
        for item in guardrails[:4]:
            lines.append(f"- {item}")
    if docs:
        lines.append("")
        lines.append("Docs:")
        for path in docs:
            lines.append(f"- {path}")
    return "\n".join(lines).rstrip() + "\n"
