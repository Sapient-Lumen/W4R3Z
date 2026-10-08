from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from vhk.project.authority_policy import build_project_authority_policy, build_release_lane_authority_story
from vhk.project.support_posture import summarize_support_posture
from vhk.project.target_route_pack import build_target_route_plan


def _write_if_allowed(path: Path, content: bytes | str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def _trim_items(items: list[dict[str, Any]] | None, limit: int = 10) -> list[dict[str, Any]]:
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


def _first_text(item: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _lane_primary_group(plan: Mapping[str, Any], group_id: str) -> dict[str, Any]:
    for item in list(plan.get("selected_groups") or []):
        if isinstance(item, Mapping) and str(item.get("selection_group") or "") == group_id:
            return dict(item)
    return {}


def _lane_primary_route(plan: Mapping[str, Any], group_id: str) -> dict[str, Any]:
    primary = _lane_primary_group(plan, group_id)
    route_id = str(primary.get("primary_route_id") or "")
    if not route_id:
        return {}
    for item in list(plan.get("activation_routes") or []):
        if isinstance(item, Mapping) and str(item.get("id") or "") == route_id:
            return dict(item)
    return {
        "id": route_id,
        "title": str(primary.get("primary_route_title") or route_id),
        "route_status": str(primary.get("primary_route_status") or "unknown"),
    }


def _release_level_rank(level: str) -> int:
    return {"experimental": 0, "caveated": 1, "supported": 2, "reference": 3}.get(str(level or "experimental"), 0)


def _status_rank(status: str) -> int:
    return {"blocked": 0, "unknown": 1, "planned": 2, "ready": 3}.get(str(status or "unknown"), 1)


def _lane_quality_score(plan: Mapping[str, Any], *, project_backend: str) -> int:
    profile = dict(plan.get("profile") or {})
    summary = dict(plan.get("selection_summary") or {})
    total = max(int(summary.get("selection_group_count") or 0), 1)
    ready = len(list(summary.get("ready_primary_groups") or []))
    planned = len(list(summary.get("planned_primary_groups") or []))
    blocked = len(list(summary.get("blocked_primary_groups") or []))
    backend = str(profile.get("backend") or "")
    score = ready * 40 - planned * 8 - blocked * 45
    if backend and backend == project_backend:
        score += 12
    trigger = _lane_primary_group(plan, "trigger-entry")
    trigger_status = str(trigger.get("primary_route_status") or "unknown")
    score += {"ready": 12, "planned": 4, "unknown": 0, "blocked": -12}.get(trigger_status, 0)
    portalish = str(trigger.get("primary_route_id") or "") == "portal-shortcuts-route"
    if portalish and backend == "wayland":
        score += 4
    return score


def _base_release_level(plan: Mapping[str, Any]) -> str:
    summary = dict(plan.get("selection_summary") or {})
    total = max(int(summary.get("selection_group_count") or 0), 1)
    ready = len(list(summary.get("ready_primary_groups") or []))
    planned = len(list(summary.get("planned_primary_groups") or []))
    blocked = len(list(summary.get("blocked_primary_groups") or []))
    overall = str(summary.get("overall_status") or "unknown")

    if blocked > 0 or overall == "unknown":
        return "experimental"
    if ready >= total - 1 and planned <= 1:
        return "supported"
    if ready >= max(1, total // 2):
        return "supported"
    if ready >= 1:
        return "caveated"
    return "experimental"


def _route_family(route_id: str) -> str:
    mapping = {
        "portal-shortcuts-route": "portal-session",
        "native-trigger-route": "native-bindings",
        "remapper-route": "remapper",
        "helper-input-route": "helper-daemon",
        "launcher-entrypoint": "launcher",
        "text-surface-route": "text-service",
        "watcher-service-route": "watcher-service",
    }
    return mapping.get(route_id, route_id or "route")


def _required_artifacts_for_lane(plan: Mapping[str, Any]) -> list[str]:
    trigger = _lane_primary_group(plan, "trigger-entry")
    trigger_id = str(trigger.get("primary_route_id") or "")
    items = [
        "docs/VHK_TARGET_ROUTE_MATRIX.md",
        "docs/VHK_ROUTE_SELECTION.md",
        "docs/VHK_ACTIVATION_ROUTES.md",
        "docs/VHK_PUBLIC_SUPPORT.md",
        "docs/VHK_INSTALL_QUICKSTART.md",
    ]
    if trigger_id in {"portal-shortcuts-route", "remapper-route", "helper-input-route"}:
        items.extend([
            "docs/VHK_HOST_REQUIREMENTS.md",
            "docs/VHK_READINESS_REPORT.md",
            "docs/VHK_OPERATOR_GUIDE.md",
            "docs/VHK_VERIFICATION_GUIDE.md",
        ])
    if trigger_id == "portal-shortcuts-route":
        items.append("docs/VHK_HOST_FIXUPS.md")
    return _dedupe_keep_order(items)


def _release_headline(profile: Mapping[str, Any], level: str, trigger_route_id: str) -> str:
    title = str(profile.get("title") or profile.get("id") or "target")
    trigger_family = _route_family(trigger_route_id)
    if level == "reference":
        return f"Reference release lane: {title} ({trigger_family} trigger edge)."
    if level == "supported":
        return f"Supported release lane: {title} ({trigger_family} trigger edge)."
    if level == "caveated":
        return f"Caveated release lane: {title} ({trigger_family} trigger edge with extra setup/review work)."
    return f"Experimental release lane: {title} ({trigger_family} trigger edge still needs stronger proof)."


def _release_summary_text(plan: Mapping[str, Any], *, level: str) -> str:
    profile = dict(plan.get("profile") or {})
    summary = dict(plan.get("selection_summary") or {})
    ready = len(list(summary.get("ready_primary_groups") or []))
    planned = len(list(summary.get("planned_primary_groups") or []))
    blocked = len(list(summary.get("blocked_primary_groups") or []))
    trigger = _lane_primary_group(plan, "trigger-entry")
    trigger_id = str(trigger.get("primary_route_id") or "")
    trigger_status = str(trigger.get("primary_route_status") or "unknown")
    base = str(profile.get("summary") or "Review the selected routes carefully before publishing this lane.")
    tail = f" The modeled trigger edge is `{trigger_id or 'unknown'}` (`{trigger_status}`)."
    if level == "reference":
        tail += f" This profile currently has {ready} ready primary groups and is the best candidate for the flagship Linux release story."
    elif level == "supported":
        tail += f" This profile currently has {ready} ready primary groups and {planned} planned group(s), so it looks shippable with explicit install/ops guidance."
    elif level == "caveated":
        tail += f" This profile still leans on {planned} planned group(s) and should ship only with visible caveats and operator guidance."
    else:
        tail += f" This profile still has {blocked} blocked and {planned} planned group(s), so it belongs in preview/testing language only."
    return base + tail


def _public_snippet(plan: Mapping[str, Any], *, level: str) -> str:
    profile = dict(plan.get("profile") or {})
    trigger = _lane_primary_group(plan, "trigger-entry")
    text_entry = _lane_primary_group(plan, "text-entry")
    trigger_family = _route_family(str(trigger.get("primary_route_id") or ""))
    text_status = str(text_entry.get("primary_route_status") or "unknown")
    prefix = {
        "reference": "Reference Linux lane:",
        "supported": "Supported Linux lane:",
        "caveated": "Caveated Linux lane:",
        "experimental": "Experimental Linux lane:",
    }.get(level, "Linux lane:")
    snippet = f"{prefix} {profile.get('title') or profile.get('id') or 'target'} uses a {trigger_family} trigger route as its documented entry path."
    if text_status == "ready":
        snippet += " Text-entry helpers are modeled as ready in this lane."
    elif text_status == "planned":
        snippet += " Text-entry helpers still need install/service follow-through, so keep setup steps visible in release notes."
    else:
        snippet += " Text-entry behavior still needs stronger proof before it should be marketed broadly."
    return snippet


def _support_snippet(plan: Mapping[str, Any], *, level: str) -> str:
    profile = dict(plan.get("profile") or {})
    trigger = _lane_primary_group(plan, "trigger-entry")
    trigger_id = str(trigger.get("primary_route_id") or "")
    trigger_status = str(trigger.get("primary_route_status") or "unknown")
    text_entry = _lane_primary_group(plan, "text-entry")
    watcher = _lane_primary_group(plan, "event-plane")
    lines = [
        f"Support posture for {profile.get('title') or profile.get('id') or 'target'}:",
        f"- Release level: `{level}`",
        f"- Primary trigger route: `{trigger_id or 'unknown'}` (`{trigger_status}`)",
        f"- Text lane: `{text_entry.get('primary_route_id') or 'unknown'}` (`{text_entry.get('primary_route_status') or 'unknown'}`)",
        f"- Event/watcher lane: `{watcher.get('primary_route_id') or 'unknown'}` (`{watcher.get('primary_route_status') or 'unknown'}`)",
    ]
    if level in {"caveated", "experimental"}:
        lines.append("- Keep fallback/manual launcher routes visible in support docs and rollback guidance.")
    else:
        lines.append("- Treat launcher entrypoints as the universal fallback when desktop-native/session routes drift.")
    return "\n".join(lines)


def _authority_public_snippet(title: str, story: Mapping[str, Any]) -> str:
    primary = str(story.get("primary_authority_lane_title") or story.get("primary_authority_posture") or "review-bound")
    scope = str(story.get("authority_scope") or "mixed-review")
    summary = str(story.get("summary") or "Authority posture unavailable").strip()
    return f"Authority lane for {title}: `{scope}` with primary owner `{primary}`. {summary}"


def build_release_lane_plan(
    project_dir: Path,
    *,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Any]:
    project_dir = project_dir.expanduser().resolve()
    target_plan = build_target_route_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )
    support_posture = summarize_support_posture(
        project_dir,
        prefer_cached=False,
        capability_usage=capability_usage,
        include_release_lanes=False,
        include_release_deploy=False,
    )
    project_authority_policy = build_project_authority_policy(
        project_dir,
        capability_usage=capability_usage,
    )

    project = dict(target_plan.get("project") or {})
    project_backend = str(project.get("desktop_backend") or "unknown")
    group_matrix = [dict(item) for item in list(target_plan.get("group_matrix") or []) if isinstance(item, dict)]
    divergent_group_ids = {
        str(item.get("selection_group") or "")
        for item in group_matrix
        if bool(item.get("divergent")) and str(item.get("selection_group") or "")
    }

    lanes: list[dict[str, Any]] = []
    for raw in list(target_plan.get("target_profiles") or []):
        if not isinstance(raw, Mapping):
            continue
        profile = dict(raw.get("profile") or {})
        summary = dict(raw.get("selection_summary") or {})
        score = _lane_quality_score(raw, project_backend=project_backend)
        base_level = _base_release_level(raw)
        trigger = _lane_primary_group(raw, "trigger-entry")
        artifacts = _required_artifacts_for_lane(raw)
        present = [path for path in artifacts if (project_dir / path).exists()]
        missing = [path for path in artifacts if not (project_dir / path).exists()]
        route_groups = [
            {
                "selection_group": str(item.get("selection_group") or ""),
                "group_title": str(item.get("group_title") or item.get("selection_group") or "group"),
                "primary_route_id": str(item.get("primary_route_id") or ""),
                "primary_route_title": str(item.get("primary_route_title") or item.get("primary_route_id") or "route"),
                "primary_route_status": str(item.get("primary_route_status") or "unknown"),
                "selection_note": str(item.get("selection_note") or ""),
                "divergent_across_targets": str(item.get("selection_group") or "") in divergent_group_ids,
            }
            for item in list(raw.get("selected_groups") or [])
            if isinstance(item, Mapping)
        ]
        lane_authority_story = build_release_lane_authority_story(
            route_groups,
            authority_policy=project_authority_policy,
            release_level=base_level,
        )
        lane = {
            "profile_id": str(profile.get("id") or ""),
            "title": str(profile.get("title") or profile.get("id") or "target"),
            "backend": str(profile.get("backend") or ""),
            "desktop_family": str(profile.get("desktop_family") or ""),
            "summary": _release_summary_text(raw, level=base_level),
            "overall_status": str(summary.get("overall_status") or "unknown"),
            "release_level": base_level,
            "release_score": score,
            "release_headline": _release_headline(profile, base_level, str(trigger.get("primary_route_id") or "")),
            "assumptions": [str(x) for x in list(profile.get("assumptions") or []) if str(x)],
            "route_groups": route_groups,
            "requirement_expectations": [
                {
                    "id": str(item.get("id") or ""),
                    "title": str(item.get("title") or item.get("id") or "requirement"),
                    "priority": str(item.get("priority") or "conditional"),
                    "requirement_type": str(item.get("requirement_type") or ""),
                    "expected_status": str(item.get("expected_status") or item.get("status") or "unknown"),
                    "alternative_group": item.get("alternative_group"),
                }
                for item in list(raw.get("requirement_expectations") or [])
                if isinstance(item, Mapping) and str(item.get("id") or "")
            ],
            "ready_primary_groups": [str(x) for x in list(summary.get("ready_primary_groups") or []) if str(x)],
            "planned_primary_groups": [str(x) for x in list(summary.get("planned_primary_groups") or []) if str(x)],
            "blocked_primary_groups": [str(x) for x in list(summary.get("blocked_primary_groups") or []) if str(x)],
            "required_artifacts": artifacts,
            "present_artifacts": present,
            "missing_artifacts": missing,
            "public_snippet": _public_snippet(raw, level=base_level),
            "support_snippet": _support_snippet(raw, level=base_level),
            "authority_story": lane_authority_story,
            "authority_snippet": _authority_public_snippet(str(profile.get("title") or profile.get("id") or "target"), lane_authority_story),
            "operator_commands": _dedupe_keep_order(
                [
                    "vhk gen-activation-pack . --force --quiet --no-activation-check",
                    "vhk gen-route-selection-pack . --force --quiet --no-selection-check",
                    "vhk gen-target-route-pack . --force --quiet",
                    "vhk gen-publish-pack . --force --quiet --no-session-check",
                    "vhk gen-release-lane-pack . --force --quiet",
                ]
            ),
        }
        lanes.append(lane)

    lanes.sort(
        key=lambda item: (
            -_release_level_rank(str(item.get("release_level") or "experimental")),
            -int(item.get("release_score") or 0),
            str(item.get("title") or ""),
        )
    )

    promoted_reference = False
    for lane in lanes:
        if lane.get("release_level") in {"supported", "caveated"} and not promoted_reference:
            lane["release_level"] = "reference"
            trigger_route_id = next(
                (
                    str(item.get("primary_route_id") or "")
                    for item in list(lane.get("route_groups") or [])
                    if str(item.get("selection_group") or "") == "trigger-entry"
                ),
                "",
            )
            lane["release_headline"] = _release_headline({"title": lane.get("title")}, "reference", trigger_route_id)
            lane["public_snippet"] = str(lane.get("public_snippet") or "").replace("Supported Linux lane:", "Reference Linux lane:").replace("Caveated Linux lane:", "Reference Linux lane:")
            lane["support_snippet"] = str(lane.get("support_snippet") or "").replace("Release level: `supported`", "Release level: `reference`").replace("Release level: `caveated`", "Release level: `reference`")
            lane["authority_story"] = build_release_lane_authority_story(
                [dict(item) for item in list(lane.get("route_groups") or []) if isinstance(item, Mapping)],
                authority_policy=project_authority_policy,
                release_level="reference",
            )
            lane["authority_snippet"] = _authority_public_snippet(str(lane.get("title") or lane.get("profile_id") or "target"), dict(lane.get("authority_story") or {}))
            promoted_reference = True
            break

    # Re-sort after promoting the flagship lane.
    lanes.sort(
        key=lambda item: (
            -_release_level_rank(str(item.get("release_level") or "experimental")),
            -int(item.get("release_score") or 0),
            str(item.get("title") or ""),
        )
    )

    level_buckets = {
        level: [str(item.get("profile_id") or "") for item in lanes if str(item.get("release_level") or "") == level]
        for level in ["reference", "supported", "caveated", "experimental"]
    }

    authority_primary_postures = Counter(str((item.get("authority_story") or {}).get("primary_authority_posture") or "mixed-review") for item in lanes)
    authority_scopes = Counter(str((item.get("authority_story") or {}).get("authority_scope") or "mixed-review") for item in lanes)

    review_commands = _dedupe_keep_order(
        [
            f"vhk plan-project {project_dir.as_posix()} --json",
            f"vhk gen-target-route-pack {project_dir.as_posix()} --force --quiet",
            f"vhk gen-publish-pack {project_dir.as_posix()} --force --quiet --no-session-check",
            f"vhk gen-release-lane-pack {project_dir.as_posix()} --force --quiet",
        ]
    )

    return {
        "source_contract": "release_lane_pack",
        "project": project,
        "target_summary": dict(target_plan.get("target_summary") or {}),
        "support_posture": {
            "headline": str(support_posture.get("headline") or "Support posture unavailable"),
            "language_guardrails": [str(x) for x in list(support_posture.get("language_guardrails") or []) if str(x)][:6],
            "docs": [str(x) for x in list(support_posture.get("docs") or []) if str(x)],
        },
        "authority_policy": project_authority_policy,
        "authority_summary": {
            "primary_posture_counts": dict(authority_primary_postures),
            "authority_scope_counts": dict(authority_scopes),
            "ordered_primary_postures": [posture for posture, _count in sorted(authority_primary_postures.items(), key=lambda pair: (-pair[1], pair[0]))],
            "ordered_authority_scopes": [scope for scope, _count in sorted(authority_scopes.items(), key=lambda pair: (-pair[1], pair[0]))],
        },
        "release_summary": {
            "lane_count": len(lanes),
            "reference_lane_ids": level_buckets["reference"],
            "supported_lane_ids": level_buckets["supported"],
            "caveated_lane_ids": level_buckets["caveated"],
            "experimental_lane_ids": level_buckets["experimental"],
        },
        "release_lanes": lanes,
        "group_matrix": group_matrix,
        "review_commands": review_commands,
    }


def render_release_lanes(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    summary = dict(plan.get("release_summary") or {})
    support_posture = dict(plan.get("support_posture") or {})
    authority_summary = dict(plan.get("authority_summary") or {})
    lanes = _trim_items(plan.get("release_lanes"), limit=8)

    lines: list[str] = []
    lines.append(f"# VHK release lanes for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-release-lane-pack`. This pack turns cross-desktop route comparisons into ship-facing Linux release lanes so maintainers can publish per-desktop guidance without hand-maintaining every sentence.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Declared project backend: `{project.get('desktop_backend') or 'unknown'}`")
    lines.append(f"- Release lanes modeled: {int(summary.get('lane_count') or 0)}")
    lines.append(f"- Reference lanes: {', '.join(f'`{x}`' for x in list(summary.get('reference_lane_ids') or [])) or 'none'}")
    lines.append(f"- Supported lanes: {', '.join(f'`{x}`' for x in list(summary.get('supported_lane_ids') or [])) or 'none'}")
    lines.append(f"- Caveated lanes: {', '.join(f'`{x}`' for x in list(summary.get('caveated_lane_ids') or [])) or 'none'}")
    lines.append(f"- Experimental lanes: {', '.join(f'`{x}`' for x in list(summary.get('experimental_lane_ids') or [])) or 'none'}")
    lines.append("")

    headline = str(support_posture.get("headline") or "").strip()
    if headline:
        lines.append("## Current public-support posture")
        lines.append("")
        lines.append(headline)
        lines.append("")

    if authority_summary:
        lines.append("## Release authority overview")
        lines.append("")
        primary_postures = [str(x) for x in list(authority_summary.get("ordered_primary_postures") or []) if str(x)]
        scopes = [str(x) for x in list(authority_summary.get("ordered_authority_scopes") or []) if str(x)]
        if primary_postures:
            lines.append("- Primary authority postures: " + ", ".join(f"`{item}`" for item in primary_postures))
        if scopes:
            lines.append("- Authority scopes: " + ", ".join(f"`{item}`" for item in scopes))
        lines.append("")

    if lanes:
        lines.append("## Recommended release lanes")
        lines.append("")
        for lane in lanes:
            lines.append(f"### {lane.get('title') or lane.get('profile_id')}")
            lines.append("")
            lines.append(f"- Profile id: `{lane.get('profile_id') or ''}`")
            lines.append(f"- Release level: `{lane.get('release_level') or 'experimental'}`")
            lines.append(f"- Overall route status: `{lane.get('overall_status') or 'unknown'}`")
            lines.append(f"- Score: {lane.get('release_score') or 0}")
            lines.append(f"- Headline: {lane.get('release_headline') or ''}")
            lines.append(f"- Summary: {lane.get('summary') or ''}")
            authority_story = dict(lane.get("authority_story") or {})
            if authority_story:
                lines.append(f"- Authority scope: `{authority_story.get('authority_scope') or 'mixed-review'}`")
                lines.append(f"- Primary authority: `{authority_story.get('primary_authority_lane_title') or authority_story.get('primary_authority_posture') or 'review-bound'}`")
                lines.append(f"- Authority summary: {authority_story.get('summary') or ''}")
            lines.append("- Primary routes:")
            for group in list(lane.get("route_groups") or []):
                marker = " divergent" if group.get("divergent_across_targets") else ""
                lines.append(
                    f"  - `{group.get('selection_group') or ''}` → `{group.get('primary_route_id') or ''}` (`{group.get('primary_route_status') or 'unknown'}`){marker}"
                )
            missing = [str(x) for x in list(lane.get("missing_artifacts") or []) if str(x)]
            if missing:
                lines.append("- Missing release artifacts:")
                for item in missing[:6]:
                    lines.append(f"  - `{item}`")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_release_snippets(plan: dict[str, Any]) -> str:
    project = dict(plan.get("project") or {})
    support_posture = dict(plan.get("support_posture") or {})
    authority_summary = dict(plan.get("authority_summary") or {})
    lanes = _trim_items(plan.get("release_lanes"), limit=8)

    lines: list[str] = []
    lines.append(f"# VHK release snippets for {project.get('name') or 'project'}")
    lines.append("")
    lines.append("Generated by `vhk gen-release-lane-pack`. Copy from here into README/release notes/support guides instead of improvising Linux support language for each desktop family.")
    lines.append("")

    guardrails = [str(x) for x in list(support_posture.get("language_guardrails") or []) if str(x)]
    lines.append("## Language guardrails")
    lines.append("")
    if guardrails:
        for item in guardrails:
            lines.append(f"- {item}")
    else:
        lines.append("- Keep desktop/session claims explicit instead of promising generic Linux parity.")
    lines.append("")

    lines.append("## Copy-ready public support snippets")
    lines.append("")
    for lane in lanes:
        lines.append(f"### {lane.get('title') or lane.get('profile_id')}")
        lines.append("")
        lines.append(lane.get("public_snippet") or "")
        lines.append("")
        lines.append("```text")
        lines.append(str(lane.get("public_snippet") or ""))
        lines.append("```")
        lines.append("")

    lines.append("## Copy-ready support handoff snippets")
    lines.append("")
    for lane in lanes:
        lines.append(f"### {lane.get('title') or lane.get('profile_id')}")
        lines.append("")
        lines.append("```text")
        lines.append(str(lane.get("support_snippet") or ""))
        lines.append("```")
        lines.append("")

    lines.append("## Copy-ready authority handoff snippets")
    lines.append("")
    for lane in lanes:
        lines.append(f"### {lane.get('title') or lane.get('profile_id')}")
        lines.append("")
        lines.append("```text")
        lines.append(str(lane.get("authority_snippet") or ""))
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_release_refresh_script(plan: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("#!/usr/bin/env sh")
    lines.append("set -eu")
    lines.append("")
    lines.append('DEST="${1:-./build/release-lane-review}"')
    lines.append('mkdir -p "$DEST"')
    lines.append('echo "Collecting VHK release-lane evidence into $DEST"')
    lines.append("")
    lines.append('printf "+ %s\\n" "vhk plan-project . --json > $DEST/plan-project.json"')
    lines.append('sh -lc "vhk plan-project . --json > \"$DEST\"/plan-project.json" || true')
    lines.append('printf "+ %s\\n" "vhk gen-target-route-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-target-route-pack . --force --quiet" || true')
    lines.append('printf "+ %s\\n" "vhk gen-publish-pack . --force --quiet --no-session-check"')
    lines.append('sh -lc "vhk gen-publish-pack . --force --quiet --no-session-check" || true')
    lines.append('printf "+ %s\\n" "vhk gen-release-lane-pack . --force --quiet"')
    lines.append('sh -lc "vhk gen-release-lane-pack . --force --quiet" || true')
    lines.append('echo "Release-lane refresh complete."')
    return "\n".join(lines).rstrip() + "\n"


def write_release_lane_pack(
    project_dir: Path,
    *,
    out_dir: Path | None = None,
    script_dir: Path | None = None,
    force: bool = False,
    lanes_doc: bool = True,
    snippets_doc: bool = True,
    plan_json: bool = True,
    refresh_script: bool = True,
    target_profiles: list[str] | None = None,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
) -> dict[str, Path]:
    project_dir = project_dir.expanduser().resolve()
    out_dir = (out_dir or (project_dir / "docs")).expanduser().resolve()
    script_dir = (script_dir or (project_dir / "scripts")).expanduser().resolve()

    plan = build_release_lane_plan(
        project_dir,
        target_profiles=target_profiles,
        capability_usage=capability_usage,
    )

    written: dict[str, Path] = {}
    if lanes_doc:
        path = out_dir / "VHK_RELEASE_LANES.md"
        _write_if_allowed(path, render_release_lanes(plan), force=force)
        written["lanes_doc"] = path
    if snippets_doc:
        path = out_dir / "VHK_RELEASE_SNIPPETS.md"
        _write_if_allowed(path, render_release_snippets(plan), force=force)
        written["snippets_doc"] = path
    if plan_json:
        path = out_dir / "VHK_RELEASE_LANE_PLAN.json"
        _write_if_allowed(path, json.dumps(plan, indent=2, sort_keys=True) + "\n", force=force)
        written["plan_json"] = path
    if refresh_script:
        path = script_dir / "vhk_refresh_release_lanes.sh"
        _write_if_allowed(path, render_release_refresh_script(plan), force=force)
        path.chmod(0o755)
        written["refresh_script"] = path
    return written
