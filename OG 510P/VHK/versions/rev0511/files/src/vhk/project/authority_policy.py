from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from vhk.project.loader import load_project
from vhk.project.strategy import summarize_project_strategy


_AUTHORITY_POSTURE_ORDER = {
    'input-edge-privileged': 0,
    'desktop-mediated': 1,
    'helper-daemon-privileged': 2,
    'session-userland': 3,
    'launch-userland': 4,
    'mixed-review': 5,
}

_ROUTE_AUTHORITY_META: dict[str, dict[str, Any]] = {
    'portal-shortcuts-route': {
        'authority_posture': 'desktop-mediated',
        'primary_authority_lane_id': 'portal-session-authority',
        'primary_authority_lane_title': 'Portal/session authority',
        'authority_owner': 'The desktop portal frontend/backend and its session object own trigger authority for this lane; VHK exports actions and evidence, but the desktop decides whether shortcuts are active.',
        'authority_boundary': 'Desktop/session policy, consent, backend routing, and session lifetime bound this lane more than local package presence does.',
        'revocation_surface': 'Portal backend drift, consent loss, session close, or desktop restart can revoke authority without any project change.',
        'summary': 'This lane is desktop-mediated at the trigger edge: the portal/session owns the hotkey surface and VHK should market it as a consent/session-shaped route, not as raw global hook parity.',
        'guardrails': [
            'Keep portal/session language explicit in release notes; do not market this lane as equivalent to always-on remapper ownership.',
            'Treat backend routing and session lifetime as first-class release checks, not as optional diagnostics.',
        ],
        'proof_targets': [
            'Create and bind the portal shortcut session on the target desktop.',
            'Verify the needed portal backend is both installed and routed on the current desktop.',
        ],
        'related_surface_ids': ['helper-route-dossier'],
    },
    'native-trigger-route': {
        'authority_posture': 'session-userland',
        'primary_authority_lane_id': 'session-binding-authority',
        'primary_authority_lane_title': 'Session binding authority',
        'authority_owner': 'The active compositor/window-manager binding layer inside the current user session owns trigger authority; VHK emits configs and launcher actions, but the session binding owner still decides activation.',
        'authority_boundary': 'This stays inside ordinary user-session ownership: binding reloads, compositor syntax, and launcher availability matter more than privileged device access.',
        'revocation_surface': 'A broken compositor config include, stale reload, or missing launcher hook can revoke authority at session reload time.',
        'summary': 'This lane is session-userland at the trigger edge: the compositor or desktop session owns shortcut activation, and VHK should keep that owner visible instead of treating it as an invisible runtime detail.',
        'guardrails': [
            'Keep generated binding snippets thin and reviewable so session-owned trigger authority stays easy to reload and recover.',
            'Do not let launcher fallback prose blur the difference between native bindings and plain app launch.',
        ],
        'proof_targets': [
            'Reload the compositor/window-manager bindings successfully on the target session.',
            'Verify the documented binding path still resolves to the intended launcher or command.',
        ],
        'related_surface_ids': [],
    },
    'remapper-route': {
        'authority_posture': 'input-edge-privileged',
        'primary_authority_lane_id': 'evdev-uinput-edge-authority',
        'primary_authority_lane_title': 'evdev/uinput edge authority',
        'authority_owner': 'A remapper or input-edge daemon owns trigger authority close to evdev/uinput or compositor key routing, while VHK keeps richer workflow logic outside the remapper.',
        'authority_boundary': 'This is an input-edge boundary with privileged/device policy concerns, rescue posture, and recovery choreography.',
        'revocation_surface': 'Bad remapper config, missing device access, or lost panic/recovery path can revoke authority immediately at the keyboard edge.',
        'summary': 'This lane is input-edge privileged at the trigger edge: it should ship with panic/recovery proof and with explicit device-policy language, not just with low-latency bragging rights.',
        'guardrails': [
            'Keep remapper exports thin so privileged ownership does not absorb full macro semantics or review-only logic.',
            'Carry panic, rollback, and rescue instructions in every release/install lane that depends on a remapper.',
        ],
        'proof_targets': [
            'Reload the remapper safely and verify the panic/recovery path before broad release claims.',
            'Confirm device access and reload behavior on the target host, not only in the author environment.',
        ],
        'related_surface_ids': ['remapper-export'],
    },
    'helper-input-route': {
        'authority_posture': 'helper-daemon-privileged',
        'primary_authority_lane_id': 'uinput-helper-daemon-authority',
        'primary_authority_lane_title': 'uinput helper daemon authority',
        'authority_owner': 'A helper daemon/socket plus its /dev/uinput policy own repeated injection authority; VHK stays the orchestrator and evidence layer around that daemon boundary.',
        'authority_boundary': 'This depends on warm helper state, socket reachability, and uinput permissions rather than on ordinary user-session startup alone.',
        'revocation_surface': 'Helper daemon stop, socket drift, or missing /dev/uinput access can revoke authority before the macro logic runs.',
        'summary': 'This lane is helper-daemon privileged: repeated authority depends on a warm helper contract, so release/install docs should name the daemon, socket, and uinput policy directly.',
        'guardrails': [
            'Keep helper-daemon ownership explicit in install docs; package presence alone is not proof that the lane is live.',
            'Prefer one reviewed warm helper path over mixed one-shot helper spawns when claiming repeated injection authority.',
        ],
        'proof_targets': [
            'Verify the helper daemon is active and the client can reach its socket.',
            'Confirm /dev/uinput access or equivalent helper permissions on the target host.',
        ],
        'related_surface_ids': ['helper-route-dossier'],
    },
    'launcher-entrypoint': {
        'authority_posture': 'launch-userland',
        'primary_authority_lane_id': 'desktop-entry-userland-authority',
        'primary_authority_lane_title': 'Desktop-entry userland authority',
        'authority_owner': 'The desktop shell/launcher owns discoverability and process start for this lane; authority ends there unless another owned route takes over downstream.',
        'authority_boundary': 'This is plain launch-time userland authority shaped by desktop-entry registration and shell indexing.',
        'revocation_surface': 'Missing desktop entry, broken launcher script, or shell index drift can remove authority by making the action undiscoverable.',
        'summary': 'This lane is launch-userland: it should always be documented as the fallback/discoverability owner rather than as a substitute for resident hotkey or helper ownership.',
        'guardrails': [
            'Keep launcher language discoverability-first; do not let it stand in for resident trigger ownership.',
            'Review desktop-entry indexing separately from downstream runtime truth.',
        ],
        'proof_targets': [
            'Verify the desktop entry or launcher surface is discoverable in the target shell.',
            'Confirm launch succeeds from the registered entrypoint without relying on an author shell environment.',
        ],
        'related_surface_ids': ['launcher-surface-export'],
    },
    'text-surface-route': {
        'authority_posture': 'session-userland',
        'primary_authority_lane_id': 'session-text-service-authority',
        'primary_authority_lane_title': 'Session text service authority',
        'authority_owner': 'A user-session text service plus its config/match tree own expansion authority; VHK is the authoring/orchestration layer behind that service.',
        'authority_boundary': 'Service lifecycle, config load path, and app/context filters bound this lane more than privileged input ownership does.',
        'revocation_surface': 'Service stop, wrong config root, or app-scoping drift can revoke the expected text surface without changing the project YAML.',
        'summary': 'This lane is session-userland for text: release/install docs should say which text service owns expansion authority and how its config is loaded.',
        'guardrails': [
            'Do not market text-service ownership as universal app-context authority on Wayland-class desktops.',
            'Keep generated text packages distinct from interpolation-heavy runner prompts.',
        ],
        'proof_targets': [
            'Confirm the exported text package/config is loaded by the active text service.',
            'Verify the text surface behaves in the intended app/session contexts on the target desktop.',
        ],
        'related_surface_ids': ['text-package-export'],
    },
    'watcher-service-route': {
        'authority_posture': 'session-userland',
        'primary_authority_lane_id': 'resident-user-service-authority',
        'primary_authority_lane_title': 'Resident user service authority',
        'authority_owner': 'A user-session watcher/bus service owns event intake and dispatch authority while macros remain payloads behind that service boundary.',
        'authority_boundary': 'This is ordinary user-session service authority: residency, event subscriptions, and restartability matter more than privileged input seams.',
        'revocation_surface': 'Service stop, lost event subscriptions, or login/session churn can revoke authority even though no remapper/helper permission changed.',
        'summary': 'This lane is session-userland on the event plane: it should ship with service-status and restart proof instead of being hidden inside generic startup prose.',
        'guardrails': [
            'Keep watcher/event subscriptions thin and restartable so service ownership stays observable.',
            'Do not overstate watcher authority as if it were a global input/capture permission story.',
        ],
        'proof_targets': [
            'Confirm the user service stays active and subscribed to the intended event plane.',
            'Verify restart/log inspection paths before treating the watcher lane as shippable.',
        ],
        'related_surface_ids': ['watcher-service-export'],
    },
}


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in values:
        text = str(item or '').strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _surface_ids(rows: list[dict[str, Any]], posture: str) -> list[str]:
    return [
        str(item.get('export_surface_id') or '')
        for item in rows
        if str(item.get('authority_posture') or '') == posture and str(item.get('export_surface_id') or '').strip()
    ]


def build_project_authority_policy(
    project_dir: Path,
    *,
    capability_usage: dict[str, list[dict[str, object]]] | None = None,
    capability_matrix: dict[str, object] | None = None,
    capability_issues: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    project = load_project(project_dir)
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
        capability_issues=capability_issues,
    )
    rows = [dict(item) for item in list(strategy.get('promotion_authority_envelope_plan') or []) if isinstance(item, dict)]
    summary = dict(strategy.get('promotion_authority_envelope_summary') or {})
    surface_map = {
        str(item.get('export_surface_id') or ''): {
            'export_surface_id': str(item.get('export_surface_id') or ''),
            'title': str(item.get('title') or item.get('export_surface_id') or ''),
            'authority_posture': str(item.get('authority_posture') or 'mixed-review'),
            'primary_authority_lane_id': str(item.get('primary_authority_lane_id') or ''),
            'primary_authority_lane_title': str(item.get('primary_authority_lane_title') or ''),
            'authority_owner': str(item.get('authority_owner') or ''),
            'authority_boundary': str(item.get('authority_boundary') or ''),
            'revocation_surface': str(item.get('revocation_surface') or ''),
            'summary': str(item.get('summary') or ''),
            'authority_guardrails': [str(x) for x in list(item.get('authority_guardrails') or []) if str(x)][:6],
            'commands': [str(x) for x in list(item.get('commands') or []) if str(x)][:10],
            'cautions': [str(x) for x in list(item.get('cautions') or []) if str(x)][:6],
            'host_requirement_ids': [str(x) for x in list(item.get('host_requirement_ids') or []) if str(x)][:10],
        }
        for item in rows
        if str(item.get('export_surface_id') or '').strip()
    }

    session_userland_surface_ids = _surface_ids(rows, 'session-userland')
    desktop_mediated_surface_ids = _surface_ids(rows, 'desktop-mediated')
    input_edge_surface_ids = _surface_ids(rows, 'input-edge-privileged')
    helper_daemon_surface_ids = _surface_ids(rows, 'helper-daemon-privileged')
    launch_userland_surface_ids = _surface_ids(rows, 'launch-userland')
    review_surface_ids = _surface_ids(rows, 'mixed-review')
    adjacent_privileged_surface_ids = _dedupe_keep_order(input_edge_surface_ids + helper_daemon_surface_ids)
    service_candidate_surface_ids = [
        surface_id
        for surface_id in session_userland_surface_ids
        if surface_id in {'watcher-service-export', 'text-package-export'}
    ]

    has_visible_macros = bool(getattr(project, 'macros', {}) or getattr(project, 'bindings', []) or getattr(project, 'hotstrings', []))
    has_bus_watchers = bool(getattr(project, 'bus_watchers', []) or getattr(project, 'window_watchers', []) or getattr(project, 'clipboard_watchers', []))
    if has_visible_macros and 'launcher-surface-export' not in launch_userland_surface_ids:
        launch_userland_surface_ids.append('launcher-surface-export')
    if has_bus_watchers and 'watcher-service-export' not in session_userland_surface_ids:
        session_userland_surface_ids.append('watcher-service-export')
    if has_bus_watchers and 'watcher-service-export' not in service_candidate_surface_ids:
        service_candidate_surface_ids.append('watcher-service-export')

    if adjacent_privileged_surface_ids and desktop_mediated_surface_ids:
        primary_mode = 'xdg-local-userland-plus-portal-and-adjacent-privileged-review'
    elif adjacent_privileged_surface_ids:
        primary_mode = 'xdg-local-userland-plus-adjacent-privileged-review'
    elif desktop_mediated_surface_ids:
        primary_mode = 'xdg-local-userland-plus-portal-review'
    else:
        primary_mode = 'xdg-local-userland-only'

    summary_line = 'This Linux-native project owns userland launcher/runtime/service surfaces directly while keeping portal sessions and privileged helper/remapper ownership explicit instead of pretending one packaging lane erases Linux boundary lines.'
    if primary_mode == 'xdg-local-userland-only':
        summary_line = 'This Linux-native project mostly stays in userland: launcher, text-service, and watcher ownership are the main surfaces, so review can stay focused on session deployment and startup truth.'

    guardrails = [
        'Treat launcher links, package trees, and user-service units as userland ownership only; they do not grant portal sessions or evdev/uinput control by themselves.',
        'Keep privileged remappers/helpers adjacent to the VHK-owned lane unless the operator separately reviews their system/user units and permission model.',
        'Keep desktop-mediated triggers honest: package guidance for them, but do not claim they become unconditional global hooks after install.',
    ]
    if review_surface_ids:
        guardrails.append('Surfaces still marked mixed-review should remain review-only in release/install language until a concrete Linux owner is chosen.')

    install_actions = [
        'Package launcher, docs, bundle payload, and runtime roots as one reviewable userland app story.',
        'Expose authority guidance from the shipped lane itself so operators can review Linux boundary lines without reopening planning docs.',
    ]
    if service_candidate_surface_ids:
        install_actions.append('Generate session-service handoff inputs for resident user-session surfaces rather than burying startup policy in shell history.')
    if desktop_mediated_surface_ids:
        install_actions.append('Keep desktop-mediated surfaces tied to portal/session guidance instead of rebranding them as privileged or always-on trigger lanes.')
    if adjacent_privileged_surface_ids:
        install_actions.append('Call out adjacent privileged surfaces explicitly so remapper/helper setup stays a reviewed follow-on step, not a side effect of local install.')

    return {
        'primary_mode': primary_mode,
        'summary': summary_line,
        'session_userland_surface_ids': session_userland_surface_ids,
        'service_candidate_surface_ids': service_candidate_surface_ids,
        'desktop_mediated_surface_ids': desktop_mediated_surface_ids,
        'adjacent_privileged_surface_ids': adjacent_privileged_surface_ids,
        'input_edge_surface_ids': input_edge_surface_ids,
        'helper_daemon_surface_ids': helper_daemon_surface_ids,
        'launch_userland_surface_ids': launch_userland_surface_ids,
        'review_surface_ids': review_surface_ids,
        'authority_posture_counts': {
            'input_edge_privileged_count': max(int(summary.get('input_edge_privileged_count') or 0), len(input_edge_surface_ids)),
            'desktop_mediated_count': max(int(summary.get('desktop_mediated_count') or 0), len(desktop_mediated_surface_ids)),
            'helper_daemon_privileged_count': max(int(summary.get('helper_daemon_privileged_count') or 0), len(helper_daemon_surface_ids)),
            'session_userland_count': max(int(summary.get('session_userland_count') or 0), len(session_userland_surface_ids)),
            'launch_userland_count': max(int(summary.get('launch_userland_count') or 0), len(launch_userland_surface_ids)),
            'mixed_review_count': max(int(summary.get('mixed_review_count') or 0), len(review_surface_ids)),
        },
        'authority_lane_ids': [str(x) for x in list(summary.get('ordered_primary_authority_lane_ids') or []) if str(x)],
        'guardrails': guardrails,
        'install_actions': install_actions,
        'surface_map': surface_map,
    }


def _route_meta(route_id: str) -> dict[str, Any]:
    meta = dict(_ROUTE_AUTHORITY_META.get(str(route_id or ''), {}))
    if meta:
        return meta
    return {
        'authority_posture': 'mixed-review',
        'primary_authority_lane_id': '',
        'primary_authority_lane_title': '',
        'authority_owner': 'Review which Linux layer actually owns this route before publishing it as a stable release lane.',
        'authority_boundary': 'Authority crosses multiple Linux layers until the route owner is chosen explicitly.',
        'revocation_surface': 'Treat this route as review-only until its Linux owner and recovery story are pinned down.',
        'summary': 'This route still needs an explicit Linux owner before it belongs in polished release/install prose.',
        'guardrails': ['Keep release/install language honest and review-bound until the route owner is explicit.'],
        'proof_targets': ['Identify the Linux owner for this route before treating it as a stable lane.'],
        'related_surface_ids': [],
    }


def _scope_from_postures(postures: list[str]) -> str:
    ordered = _dedupe_keep_order(postures)
    if not ordered:
        return 'mixed-review'
    return '-plus-'.join(p.replace('-', '_') for p in ordered)


def build_release_lane_authority_story(
    route_groups: list[dict[str, Any]] | list[Mapping[str, Any]],
    *,
    authority_policy: Mapping[str, Any] | None = None,
    deploy_style: str = '',
    release_level: str = '',
) -> dict[str, Any]:
    policy = dict(authority_policy or {})
    surface_map = {
        str(key): dict(value)
        for key, value in dict(policy.get('surface_map') or {}).items()
        if str(key).strip() and isinstance(value, Mapping)
    }
    route_rows: list[dict[str, Any]] = []
    combined_guardrails: list[str] = []
    combined_commands: list[str] = []
    combined_proof_targets: list[str] = []
    combined_related_surface_ids: list[str] = []

    for raw in route_groups or []:
        if not isinstance(raw, Mapping):
            continue
        group_id = str(raw.get('selection_group') or '').strip()
        route_id = str(raw.get('primary_route_id') or '').strip()
        if not group_id or not route_id:
            continue
        meta = _route_meta(route_id)
        related_surface_ids = _dedupe_keep_order([str(x) for x in list(meta.get('related_surface_ids') or []) if str(x)])
        surface_commands: list[str] = []
        surface_guardrails: list[str] = []
        surface_summaries: list[str] = []
        for surface_id in related_surface_ids:
            surface = dict(surface_map.get(surface_id) or {})
            if not surface:
                continue
            surface_commands.extend(str(x) for x in list(surface.get('commands') or []) if str(x))
            surface_guardrails.extend(str(x) for x in list(surface.get('authority_guardrails') or []) if str(x))
            if str(surface.get('summary') or '').strip():
                surface_summaries.append(str(surface.get('summary') or '').strip())
        row = {
            'selection_group': group_id,
            'group_title': str(raw.get('group_title') or group_id),
            'route_id': route_id,
            'route_title': str(raw.get('primary_route_title') or route_id),
            'route_status': str(raw.get('primary_route_status') or 'unknown'),
            'authority_posture': str(meta.get('authority_posture') or 'mixed-review'),
            'primary_authority_lane_id': str(meta.get('primary_authority_lane_id') or ''),
            'primary_authority_lane_title': str(meta.get('primary_authority_lane_title') or ''),
            'authority_owner': str(meta.get('authority_owner') or ''),
            'authority_boundary': str(meta.get('authority_boundary') or ''),
            'revocation_surface': str(meta.get('revocation_surface') or ''),
            'summary': surface_summaries[0] if surface_summaries else str(meta.get('summary') or ''),
            'guardrails': _dedupe_keep_order([str(x) for x in list(meta.get('guardrails') or []) if str(x)] + surface_guardrails)[:6],
            'proof_targets': _dedupe_keep_order([str(x) for x in list(meta.get('proof_targets') or []) if str(x)])[:6],
            'commands': _dedupe_keep_order(surface_commands)[:8],
            'related_surface_ids': related_surface_ids,
        }
        route_rows.append(row)
        combined_guardrails.extend(row['guardrails'])
        combined_commands.extend(row['commands'])
        combined_proof_targets.extend(row['proof_targets'])
        combined_related_surface_ids.extend(related_surface_ids)

    if 'launcher-surface-export' in [str(x) for x in list(policy.get('launch_userland_surface_ids') or []) if str(x)] and 'launcher-surface-export' not in combined_related_surface_ids:
        combined_related_surface_ids.append('launcher-surface-export')

    trigger_row = next((row for row in route_rows if row.get('selection_group') == 'trigger-entry'), None)
    if trigger_row:
        primary = dict(trigger_row)
    elif route_rows:
        primary = dict(sorted(route_rows, key=lambda row: _AUTHORITY_POSTURE_ORDER.get(str(row.get('authority_posture') or 'mixed-review'), 9))[0])
    else:
        primary = _route_meta('')

    posture_counts = Counter(str(row.get('authority_posture') or 'mixed-review') for row in route_rows)
    ordered_postures = [
        str(row.get('authority_posture') or 'mixed-review')
        for row in sorted(route_rows, key=lambda row: (_AUTHORITY_POSTURE_ORDER.get(str(row.get('authority_posture') or 'mixed-review'), 9), str(row.get('selection_group') or '')))
    ]
    authority_scope = _scope_from_postures(ordered_postures)
    summary = str(primary.get('summary') or 'Authority posture unavailable').strip()
    if route_rows:
        route_bits = [
            f"{row.get('selection_group') or 'route'}=`{row.get('route_id') or 'unknown'}`/{row.get('authority_posture') or 'mixed-review'}"
            for row in route_rows
        ]
        summary += ' Route ownership: ' + '; '.join(route_bits[:4]) + '.'
    if str(deploy_style).strip():
        summary += f" Deploy style stays `{deploy_style}` so release/install assets should preserve that owner boundary instead of flattening it into generic Linux prose."
    if str(release_level).strip() in {'caveated', 'experimental'}:
        summary += ' Because this lane is not yet fully proven, keep launcher/manual recovery and owner boundaries especially visible.'

    support_snippet = (
        f"Authority posture for this lane: `{authority_scope}`. "
        f"Primary owner: {primary.get('primary_authority_lane_title') or primary.get('authority_posture') or 'review-bound'}. "
        f"Keep release/install language aligned with {primary.get('authority_posture') or 'mixed-review'} ownership instead of implying one flat Linux runtime."
    )

    return {
        'authority_scope': authority_scope,
        'primary_authority_posture': str(primary.get('authority_posture') or 'mixed-review'),
        'primary_authority_lane_id': str(primary.get('primary_authority_lane_id') or ''),
        'primary_authority_lane_title': str(primary.get('primary_authority_lane_title') or ''),
        'authority_owner': str(primary.get('authority_owner') or ''),
        'authority_boundary': str(primary.get('authority_boundary') or ''),
        'revocation_surface': str(primary.get('revocation_surface') or ''),
        'summary': summary,
        'support_snippet': support_snippet,
        'guardrails': _dedupe_keep_order(combined_guardrails)[:8],
        'commands': _dedupe_keep_order(combined_commands)[:10],
        'proof_targets': _dedupe_keep_order(combined_proof_targets)[:8],
        'related_surface_ids': _dedupe_keep_order(combined_related_surface_ids),
        'route_authority_rows': route_rows,
        'posture_counts': dict(posture_counts),
    }
