from __future__ import annotations

import json
import html
import yaml
import os
import platform
import re
import difflib
import hashlib
import shlex
import shutil
import subprocess
import time
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from vhk.core.clipboard_watchers import run_clipboard_watcher
from vhk.core.file_watchers import run_file_watcher
from vhk.core.bus_watchers import run_bus_watcher, run_bus_daemon
from vhk.core.window_watchers import run_window_watcher
from vhk.system.wm_events import iter_wm_events, window_info_from_event
from vhk.system.event_bus import emit_bus_event, get_bus_socket_path
from vhk.system.httpd import HttpdConfig, make_http_server
from vhk.system.osc import OscdConfig, make_oscd_server
from vhk.system.hypr_socket2 import bridge_hypr_custom_to_bus, get_hypr_socket2_path
from vhk.system.dbus_bridge import iter_dbus_signals
from vhk.system.global_shortcuts_portal import (
    BoundShortcut,
    ShortcutSpec,
    bind_shortcuts as portal_bind_shortcuts,
    create_session as portal_create_session,
    iter_shortcut_signals as iter_portal_shortcut_signals,
    list_shortcuts as portal_list_shortcuts,
    vhk_hotkey_to_shortcuts_spec,
)
from vhk.core.models import I3WindowSelector
from vhk.core.panic import PanicConfig, clear_panic, set_panic
from vhk.core.runner import Runner
from vhk.core.eventlog_report import find_latest_event_log, read_event_log, summarize_event_log
from vhk.core.eventlog_trace import eventlog_to_chrome_trace
from vhk.core.eventlog_history import collect_history
from vhk.i3.ipc import I3Connection, discover_socket_path
from vhk.i3.tree import find_all
from vhk.project.bundle import bundle_project, bundle_release_stage, verify_bundle, inspect_bundle
from vhk.project.bundle_materialize import materialize_bundle, BundleMaterializeError
from vhk.project.loader import load_project
from vhk.project.palette import build_palette_entries, find_palette_entry
from vhk.project.desktop_entry import render_desktop_entry, default_desktop_install_path
from vhk.project.launcher_script import render_launcher_script, default_launcher_install_path
from vhk.project.dragonfly_pack import (
    default_dragonfly_dir,
    find_voice_phrase_collisions,
    write_dragonfly_pack,
    _normalize_spoken_form,
    _translate_voice_context,
)
from vhk.project.talon_pack import write_talon_pack, default_talon_dir
from vhk.project.playerctl_pack import write_playerctl_pack, default_playerctl_dir
from vhk.project.kitty_pack import write_kitty_pack, default_kitty_dir
from vhk.project.wezterm_pack import write_wezterm_pack, default_wezterm_dir
from vhk.project.mpv_pack import write_mpv_pack, default_mpv_dir
from vhk.project.qutebrowser_pack import write_qutebrowser_pack, default_qutebrowser_dir
from vhk.project.autokey_pack import (
    write_autokey_pack,
    default_autokey_dir,
    _translate_window_filter,
    _AUTOKEY_WINDOW_FILTER_APPROXIMATION_REASON,
)
from vhk.project.rofi_mode import build_rofi_mode_manifest
from vhk.project.wm_bindings import build_wm_binding_manifest
from vhk.project.wm_launcher_modes import build_wm_launcher_mode_manifest
from vhk.project.wm_includes import build_wm_include_manifest, default_wm_include_install_path
from vhk.project.wm_bundle import build_wm_bundle_manifest, write_wm_bundle
from vhk.project.preset_prompts import prompt_preset_overlay
from vhk.project.prompt_profiles import make_prompt_profile_store, sanitize_prompt_answers, apply_saved_answers
from vhk.project.preset_prompts import resolve_preset_profile_key
from vhk.project.presets import resolve_macro_preset
from vhk.project.prompt_profile_defs import build_prompt_profile_definitions, find_prompt_profile_definition
from vhk.project.lint import lint_steps
from vhk.project.strategy import summarize_project_strategy
from vhk.project.window_contracts import summarize_project_window_contract
from vhk.project.optimizer import optimize_steps
from vhk.project.retime import retime_steps
from vhk.project.scaffold import scaffold_steps
from vhk.project.init_project import init_project as init_project_fs, add_macro as add_macro_fs
from vhk.project.operator_pack import write_operator_pack
from vhk.project.design_pack import write_design_pack
from vhk.project.promotion_pack import write_promotion_pack
from vhk.project.session_fit_pack import write_session_fit_pack
from vhk.project.host_contract_pack import write_host_contract_pack
from vhk.project.readiness_pack import write_readiness_pack, collect_live_readiness_snapshot
from vhk.project.activation_pack import write_activation_pack
from vhk.project.route_selection_pack import write_route_selection_pack
from vhk.project.target_route_pack import write_target_route_pack
from vhk.project.release_lane_pack import write_release_lane_pack
from vhk.project.release_deploy_pack import write_release_deploy_pack
from vhk.project.release_stage_pack import write_release_stage_pack
from vhk.project.verification_pack import write_verification_pack
from vhk.project.support_pack import write_support_pack
from vhk.project.portability_pack import write_portability_pack
from vhk.project.claim_pack import build_claim_plan, write_claim_pack, audit_target_claims as audit_target_claims_fs
from vhk.project.publish_pack import write_publish_pack
from vhk.project.distribution_pack import write_distribution_pack
from vhk.project.runtime_pack import write_runtime_pack
from vhk.project.runtime_embed_pack import write_runtime_embed_pack
from vhk.project.native_install_pack import write_native_install_pack
from vhk.project.service_compose_pack import write_service_compose_pack
from vhk.project.host_rehearsal_pack import write_host_rehearsal_pack
from vhk.project.host_dossier_pack import write_host_dossier_pack
from vhk.project.capability_audit_pack import write_capability_audit_pack
from vhk.project.trigger_pack import (
    build_trigger_pack_plan,
    annotate_trigger_surfaces,
    build_trigger_pack_manifest,
    write_trigger_pack_artifacts,
)
from vhk.project.setup_pack import write_setup_pack
from vhk.project.schema import generate_schema, write_default_schemas
from vhk.system.clipboard import choose_backend as clipboard_backend
from vhk.system.dialogs import choose_dialog_backend, choose_choice_backend, choose_from_list, ask_yes_no, input_text, prompt_form
from vhk.system.doctor import (
    build_clear_stuck_keys_hint,
    build_doctor_advice,
    build_doctor_capability_matrix,
    probe_accessibility_bus,
    probe_display_geometry,
    probe_i3_ipc,
    probe_screenshot_capture,
    probe_tesseract_languages,
    probe_uinput,
    probe_wayland_protocols,
    probe_wayland_virtual_screen,
    probe_ydotool_socket,
    probe_dotoold,
    probe_kdotool,
    probe_current_user_groups,
    probe_input_event_access,
    probe_xdg_portal_screenshot,
    probe_xdg_portal_screencast,
    probe_xdg_portal_input_capture,
    probe_xdg_portal_backend_config,
    probe_xdg_portal_backend_manifests,
    probe_xdg_portal_global_shortcuts,
    probe_xdg_portal_remote_desktop,
    probe_x11_extensions,
    probe_xkb_layout,
)
from vhk.system.input import choose_keyboard_backend, choose_pointer_backend
from vhk.system.cursor import choose_backend as cursor_backend
from vhk.system.notify import choose_backend as notify_backend
from vhk.system.region_select import select_region, parse_geometry
from vhk.system.screenshot import choose_backend as screenshot_backend
from vhk.system.session import detect_backend
from vhk.vision.assets import Needle, compute_click_offset, load_needle, scale_needle, try_load_needle
from vhk.vision.annotate import annotate_match
from vhk.vision.match import preview_image_search_file
from vhk.vision.ocr import tesseract_available

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()
console_err = Console(stderr=True)


_SEV_ORDER = {"info": 1, "warning": 2, "error": 3}


def _iter_voice_export_collisions(project) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    for backend in ("dragonfly", "talon"):
        for collision in find_voice_phrase_collisions(project, backend=backend):
            context_label = collision.context_label or "global"
            issues.append(
                {
                    "severity": "warning",
                    "code": "VOICE_PHRASE_COLLISION",
                    "path": f"voice:{backend}:{context_label}",
                    "message": (
                        f"Spoken phrase `{collision.phrase}` is assigned to multiple {backend.title()} voice commands "
                        f"in the same effective scope ({context_label})."
                    ),
                    "suggestion": (
                        "Give the commands distinct `voice_phrases` or add/exportable `voice_when` context so the "
                        "spoken phrase is unique within each backend scope."
                    ),
                    "category": "voice_export",
                    "backend": backend,
                    "phrase": collision.phrase,
                    "context_label": collision.context_label,
                    "targets": list(collision.targets),
                }
            )
    return issues


def _effective_explicit_voice_phrases(macro: object, *, preset: object | None = None) -> list[str]:
    explicit: list[str] = []
    if preset is not None:
        explicit.extend(str(item) for item in getattr(preset, "voice_phrases", []) or [])
    if not explicit:
        explicit.extend(str(item) for item in getattr(macro, "voice_phrases", []) or [])
    return explicit



def _iter_voice_phrase_quality_issues(project) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []

    def add(
        *,
        severity: str,
        code: str,
        path: str,
        message: str,
        suggestion: str | None = None,
        **extra: object,
    ) -> None:
        issues.append(
            {
                "severity": severity,
                "code": code,
                "path": path,
                "message": message,
                "suggestion": suggestion,
                "category": "voice_phrase_quality",
                **extra,
            }
        )

    def target_label(macro_name: str, preset_name: str | None = None) -> str:
        return f"{macro_name}[{preset_name}]" if preset_name else macro_name

    for macro in project.macros.values():
        if getattr(macro, "hidden", False):
            continue
        voice_targets = [(macro, None)]
        for preset in getattr(macro, "presets", []) or []:
            if getattr(preset, "hidden", False):
                continue
            voice_targets.append((macro, preset))

        for macro_obj, preset in voice_targets:
            label = target_label(macro_obj.name, preset.name if preset is not None else None)
            explicit = _effective_explicit_voice_phrases(macro_obj, preset=preset)
            normalized_to_raw: dict[str, list[str]] = {}
            for raw_phrase in explicit:
                normalized = _normalize_spoken_form(raw_phrase)
                if not normalized:
                    add(
                        severity="warning",
                        code="VOICE_PHRASE_EMPTY_AFTER_NORMALIZATION",
                        path=f"voice:quality:{label}",
                        message=(
                            f"Voice phrase `{raw_phrase}` for `{label}` normalizes to an empty spoken form and will be ignored during voice export."
                        ),
                        suggestion=(
                            "Use letters/numbers/spaces that already resemble the literal phrase you intend to say."
                        ),
                        target=label,
                        raw_phrase=raw_phrase,
                    )
                    continue
                normalized_to_raw.setdefault(normalized, []).append(raw_phrase)
                if normalized != str(raw_phrase).strip().lower():
                    add(
                        severity="info",
                        code="VOICE_PHRASE_NORMALIZED",
                        path=f"voice:quality:{label}",
                        message=(
                            f"Voice phrase `{raw_phrase}` for `{label}` exports as literal `{normalized}` after normalization."
                        ),
                        suggestion=(
                            "Prefer lowercase space-separated `voice_phrases` so the written YAML already matches the generated Talon/Dragonfly command phrase."
                        ),
                        target=label,
                        raw_phrase=raw_phrase,
                        normalized_phrase=normalized,
                    )

            for normalized, raw_variants in sorted(normalized_to_raw.items()):
                unique_raw = list(dict.fromkeys(str(item) for item in raw_variants))
                if len(unique_raw) < 2:
                    continue
                add(
                    severity="info",
                    code="VOICE_PHRASE_REDUNDANT_VARIANT",
                    path=f"voice:quality:{label}",
                    message=(
                        f"Multiple `voice_phrases` for `{label}` collapse to the same exported spoken form `{normalized}`."
                    ),
                    suggestion=(
                        "Keep one canonical literal phrase per target unless you intentionally want multiple distinct spoken forms."
                    ),
                    target=label,
                    normalized_phrase=normalized,
                    raw_phrases=unique_raw,
                )

            selector = getattr(preset, "voice_when", None) if preset is not None and getattr(preset, "voice_when", None) is not None else getattr(macro_obj, "voice_when", None)
            dragonfly_payload, _dragonfly_label, dragonfly_unsupported = _translate_voice_context(selector, backend="dragonfly")
            talon_payload, _talon_label, talon_unsupported = _translate_voice_context(selector, backend="talon")
            exports_globally = (
                selector is None
                or (
                    not dragonfly_unsupported
                    and not talon_unsupported
                    and not dragonfly_payload
                    and not talon_payload
                )
            )
            if not exports_globally:
                continue

            short_phrases: list[str] = []
            short_phrase_candidates = [
                _normalize_spoken_form(item)
                for item in explicit
            ] if explicit else []
            for phrase in short_phrase_candidates:
                word_count = len([part for part in phrase.split() if part])
                if phrase and word_count <= 1:
                    short_phrases.append(phrase)
            short_phrases = list(dict.fromkeys(short_phrases))
            if short_phrases:
                add(
                    severity="info",
                    code="VOICE_PHRASE_SHORT_GLOBAL",
                    path=f"voice:quality:{label}",
                    message=(
                        f"`{label}` exports short global spoken phrase(s): " + ", ".join(f"`{item}`" for item in short_phrases) + "."
                    ),
                    suggestion=(
                        "Prefer 2+ word spoken forms or add exportable `voice_when` context if you want to keep the command short."
                    ),
                    target=label,
                    phrases=short_phrases,
                )

    return issues


def _selector_field_names(selector: I3WindowSelector | None) -> list[str]:
    if selector is None:
        return []
    try:
        data = selector.model_dump(by_alias=True, exclude_none=True)
    except Exception:
        return []
    out: list[str] = []
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, bool) and value is False:
            continue
        out.append(str(key))
    return sorted(out)


def _kmonad_collision_keys(bindings: list[object]) -> dict[str, list[str]]:
    collisions: dict[str, list[str]] = {}
    by_key: dict[str, list[str]] = {}
    for binding in bindings:
        keys = str(getattr(binding, "keys", "") or "")
        parsed = _parse_i3_hotkey_to_kmonad_key(keys)
        if not parsed:
            continue
        by_key.setdefault(parsed, []).append(keys)
    for parsed, raw in by_key.items():
        if len(raw) > 1:
            collisions[parsed] = sorted(raw)
    return collisions


def _iter_export_honesty_issues(project) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    backend = str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "").strip().lower()

    def add(
        *,
        severity: str,
        code: str,
        path: str,
        message: str,
        suggestion: str | None = None,
        **extra: object,
    ) -> None:
        issues.append(
            {
                "severity": severity,
                "code": code,
                "path": path,
                "message": message,
                "suggestion": suggestion,
                "category": "export_honesty",
                **extra,
            }
        )

    def target_label(macro_name: str, preset_name: str | None = None) -> str:
        return f"{macro_name}[{preset_name}]" if preset_name else macro_name

    # Voice export honesty: surface unsupported `voice_when` fields before pack generation.
    for macro in project.macros.values():
        if getattr(macro, "hidden", False):
            continue
        voice_targets = [(macro, None)]
        for preset in getattr(macro, "presets", []) or []:
            if getattr(preset, "hidden", False):
                continue
            voice_targets.append((macro, preset))
        for macro_obj, preset in voice_targets:
            selector = getattr(preset, "voice_when", None) if preset is not None and getattr(preset, "voice_when", None) is not None else getattr(macro_obj, "voice_when", None)
            if selector is None:
                continue
            label = target_label(macro_obj.name, preset.name if preset is not None else None)
            for voice_backend in ("dragonfly", "talon"):
                _payload, _context_label, unsupported = _translate_voice_context(selector, backend=voice_backend)
                if unsupported:
                    add(
                        severity="warning",
                        code="VOICE_CONTEXT_EXPORT_GAP",
                        path=f"voice:{voice_backend}:{label}",
                        message=(
                            f"`voice_when` for `{label}` uses selector fields that {voice_backend.title()} cannot export honestly: "
                            + ", ".join(unsupported)
                        ),
                        suggestion=(
                            "Prefer class/title scoping for Talon and Dragonfly, and reserve instance/window_role for Dragonfly-only contexts."
                        ),
                        backend=voice_backend,
                        target=label,
                        unsupported_fields=list(unsupported),
                    )

            if preset is not None and bool(getattr(preset, "prompt_form", None)):
                add(
                    severity="info",
                    code="VOICE_PROMPT_EXPORT_OPT_IN",
                    path=f"voice:prompt:{label}",
                    message=(
                        f"Voice exports skip preset `{label}` by default because it requires an interactive prompt overlay."
                    ),
                    suggestion=(
                        "Regenerate the Talon/Dragonfly pack with `--include-prompt-entries` only when a spoken command opening a prompt is acceptable."
                    ),
                    target=label,
                )

    # AutoKey export honesty: selectors can widen to title-or-class matching.
    for binding in getattr(project, "bindings", []) or []:
        selector = getattr(binding, "when", None)
        if selector is None:
            continue
        regex, label, unsupported, approximate = _translate_window_filter(selector, allow_approximation=False)
        if unsupported:
            if all(str(item).startswith(_AUTOKEY_WINDOW_FILTER_APPROXIMATION_REASON) for item in unsupported):
                code = "AUTOKEY_SCOPE_APPROXIMATION_REQUIRED"
                suggestion = (
                    "Keep the scope in VHK/WM binds, or regenerate `vhk gen-autokey-pack` with `--allow-window-filter-approximation` only if title-or-class widening is acceptable."
                )
            else:
                code = "AUTOKEY_SCOPE_EXPORT_GAP"
                suggestion = (
                    "Simplify the selector to one approximated title or class filter, or keep this trigger outside the AutoKey adapter lane."
                )
            add(
                severity="warning",
                code=code,
                path=f"autokey:binding:{binding.keys}",
                message=(
                    f"AutoKey export cannot preserve the binding scope for `{binding.keys}` without changing meaning: "
                    + "; ".join(str(item) for item in unsupported)
                ),
                suggestion=suggestion,
                trigger_kind="binding",
                trigger=binding.keys,
                unsupported_fields=[str(item) for item in unsupported],
            )

    for hotstring in getattr(project, "hotstrings", []) or []:
        if not getattr(hotstring, "enabled", True):
            continue
        selector = getattr(hotstring, "when", None)
        if selector is None:
            continue
        regex, label, unsupported, approximate = _translate_window_filter(selector, allow_approximation=False)
        if unsupported:
            if all(str(item).startswith(_AUTOKEY_WINDOW_FILTER_APPROXIMATION_REASON) for item in unsupported):
                code = "AUTOKEY_SCOPE_APPROXIMATION_REQUIRED"
                suggestion = (
                    "Keep this hotstring global, prefer Espanso for scoped text expansion, or regenerate `vhk gen-autokey-pack` with `--allow-window-filter-approximation` only if title-or-class widening is acceptable."
                )
            else:
                code = "AUTOKEY_SCOPE_EXPORT_GAP"
                suggestion = (
                    "Simplify the selector to one approximated title or class filter, or keep this hotstring out of the AutoKey adapter lane."
                )
            add(
                severity="warning",
                code=code,
                path=f"autokey:hotstring:{hotstring.trigger}",
                message=(
                    f"AutoKey export cannot preserve the hotstring scope for `{hotstring.trigger}` without changing meaning: "
                    + "; ".join(str(item) for item in unsupported)
                ),
                suggestion=suggestion,
                trigger_kind="hotstring",
                trigger=hotstring.trigger,
                unsupported_fields=[str(item) for item in unsupported],
            )

    # GlobalShortcuts portal export honesty: the portal owns global activation, while
    # scoped selectors still remain runtime-only in VHK after dispatch.
    bindings = list(getattr(project, "bindings", []) or [])
    for binding in bindings:
        trigger = str(getattr(binding, "keys", "") or "")
        preferred_trigger = vhk_hotkey_to_shortcuts_spec(trigger)
        if not preferred_trigger:
            add(
                severity="warning",
                code="PORTAL_TRIGGER_EXPORT_GAP",
                path=f"portal:binding:{trigger}",
                message=(
                    f"GlobalShortcuts export cannot express `{trigger}` as a freedesktop shortcuts-spec preferred trigger, so this binding would be skipped from the portal catalog."
                ),
                suggestion=(
                    "Prefer simple base-layer keyboard chords for the portal lane, or keep this trigger on a WM/remapper surface instead of `vhk gen-portal-shortcuts-spec`."
                ),
                trigger_kind="binding",
                trigger=trigger,
            )
        selector = getattr(binding, "when", None)
        if selector is None:
            continue
        fields = _selector_field_names(selector)
        if not fields:
            continue
        add(
            severity="info",
            code="PORTAL_SCOPE_RUNTIME_ONLY",
            path=f"portal:binding:{trigger}",
            message=(
                f"GlobalShortcuts export registers `{trigger}` globally at the portal layer; these selector fields remain runtime-only in VHK after activation: "
                + ", ".join(fields)
            ),
            suggestion=(
                "Use the portal lane when a permissioned global shortcut is acceptable, or prefer compositor binds/xremap when you want more app-aware gating before the macro starts."
            ),
            trigger_kind="binding",
            trigger=trigger,
            runtime_only_fields=list(fields),
        )

    # keyd / Kanata / sxhkd export honesty: binding selectors remain runtime-only in VHK.
    for binding in bindings:
        selector = getattr(binding, "when", None)
        if selector is None:
            continue
        fields = _selector_field_names(selector)
        if not fields:
            continue
        for surface, code, title, suggestion in (
            (
                "keyd",
                "KEYD_SCOPE_RUNTIME_ONLY",
                "keyd",
                "Treat keyd as the global capture layer and keep per-window gating in VHK, or explore keyd's separate application-mapper lane when you need the remapper itself to own more app-aware scope.",
            ),
            (
                "kanata",
                "KANATA_SCOPE_RUNTIME_ONLY",
                "Kanata",
                "Use Kanata for low-level capture and let VHK keep window-aware ownership, or move the trigger to a WM/xremap surface when you want more native app scoping.",
            ),
            (
                "sxhkd",
                "SXHKD_SCOPE_RUNTIME_ONLY",
                "sxhkd",
                "Keep per-window gating in VHK/WM rules, or prefer xremap/compositor binds when you want more app-aware ownership before the macro starts.",
            ),
        ):
            add(
                severity="info",
                code=code,
                path=f"{surface}:binding:{binding.keys}",
                message=(
                    f"{title} export keeps `{binding.keys}` global at the daemon level; these selector fields remain runtime-only in VHK: "
                    + ", ".join(fields)
                ),
                suggestion=suggestion,
                trigger_kind="binding",
                trigger=binding.keys,
                runtime_only_fields=list(fields),
            )

    # KMonad export honesty: leader/layer flow changes trigger shape, and selectors stay runtime-only.
    if bindings:
        add(
            severity="info",
            code="KMONAD_TRIGGER_SHAPE_CHANGE",
            path="kmonad:bindings",
            message=(
                "KMonad export rewrites project bindings into a leader/layer flow instead of preserving direct WM-style modifier chords."
            ),
            suggestion=(
                "Use KMonad when a leader-driven macro layer is acceptable; prefer keyd, Kanata, xremap, or compositor binds when you want direct hotkeys to stay visible at the trigger layer."
            ),
            binding_count=len(bindings),
        )

    for binding in bindings:
        selector = getattr(binding, "when", None)
        if selector is None:
            continue
        fields = _selector_field_names(selector)
        if not fields:
            continue
        add(
            severity="info",
            code="KMONAD_SCOPE_RUNTIME_ONLY",
            path=f"kmonad:binding:{binding.keys}",
            message=(
                f"KMonad export keeps `{binding.keys}` global at the interception layer; these selector fields remain runtime-only in VHK: "
                + ", ".join(fields)
            ),
            suggestion=(
                "Let KMonad own the leader/layer capture and keep window-aware checks in VHK, or move the trigger to a WM/xremap surface when app scoping should happen earlier."
            ),
            trigger_kind="binding",
            trigger=binding.keys,
            runtime_only_fields=list(fields),
        )

    collisions = _kmonad_collision_keys(bindings)
    for parsed_key, raw_keys in sorted(collisions.items()):
        add(
            severity="info",
            code="KMONAD_COLLISION_SELECTOR_LAYER",
            path=f"kmonad:collision:{parsed_key}",
            message=(
                f"KMonad export will place {len(raw_keys)} bindings sharing final key `{parsed_key}` behind selector sublayers instead of one flat hotkey map."
            ),
            suggestion=(
                "Review the generated selector keys in `vhk gen-kmonad-config`, or reduce collisions on the final trigger key when you want a simpler leader layer."
            ),
            parsed_key=parsed_key,
            triggers=list(raw_keys),
        )

    if backend == "wayland" and bindings:
        add(
            severity="warning",
            code="SXHKD_X11_ONLY",
            path="sxhkd:backend:wayland",
            message=(
                "sxhkd is an X11-only hotkey daemon, but this project is marked for a Wayland desktop backend."
            ),
            suggestion=(
                "Prefer compositor binds, xremap, keyd, Kanata, KMonad, or the GlobalShortcuts portal on Wayland; keep `vhk gen-sxhkd-config` for X11 hosts."
            ),
            backend=backend,
            binding_count=len(bindings),
        )

    # xremap export honesty: only app/window scoping survives into the remapper.
    for binding in getattr(project, "bindings", []) or []:
        selector = getattr(binding, "when", None)
        if selector is None:
            continue
        unsupported = _xremap_selector_export_gaps(selector)
        if unsupported:
            add(
                severity="info",
                code="XREMAP_SCOPE_EXPORT_GAP",
                path=f"xremap:binding:{binding.keys}",
                message=(
                    f"xremap export can only pre-scope `{binding.keys}` by application/window title; these selector fields stay runtime-only in VHK: "
                    + ", ".join(str(item) for item in unsupported)
                ),
                suggestion=(
                    "Keep the richer selector in VHK, or reduce the binding scope to class/app_id/title fields when you want xremap itself to own more of the app-aware gating."
                ),
                trigger_kind="binding",
                trigger=binding.keys,
                unsupported_fields=[str(item) for item in unsupported],
            )

    # Espanso export honesty: app-scoped configs are X11-only, and overlapping scopes need composites.
    scoped_hotstrings = [hs for hs in getattr(project, "hotstrings", []) or [] if getattr(hs, "enabled", True) and getattr(hs, "when", None) is not None]
    if backend == "wayland" and scoped_hotstrings:
        add(
            severity="warning",
            code="ESPANSO_APP_SCOPE_WAYLAND",
            path="espanso:package-dir:wayland",
            message=(
                "This project uses scoped hotstrings, but Espanso's app-specific configurations are not supported on Wayland."
            ),
            suggestion=(
                "Treat `vhk gen-espanso --package-dir` as an X11-oriented adapter lane for scoped snippets, or keep scoped text automation inside VHK/palette flows on Wayland."
            ),
            backend=backend,
            scoped_hotstring_count=len(scoped_hotstrings),
        )

    actual_groups: dict[tuple[tuple[str, str], ...], dict[str, object]] = {}
    for hotstring in scoped_hotstrings:
        selector = hotstring.when
        fields = selector.model_dump(by_alias=True, exclude_none=True) if selector is not None else {}
        unsupported = sorted(
            str(key)
            for key in fields
            if key not in {"class", "title", "title_regex", "app_id", "app_id_regex"}
        )
        if unsupported:
            add(
                severity="warning",
                code="ESPANSO_SCOPE_EXPORT_GAP",
                path=f"espanso:hotstring:{hotstring.trigger}",
                message=(
                    f"Espanso export only understands class/title app filters, so `{hotstring.trigger}` would lose selector fields: "
                    + ", ".join(unsupported)
                ),
                suggestion=(
                    "Keep the richer selector in VHK, or reduce the hotstring scope to class/title/app_id fields before exporting to Espanso."
                ),
                trigger=hotstring.trigger,
                unsupported_fields=list(unsupported),
            )
            continue
        filters = _espanso_filters_from_selector(selector)
        key = _espanso_filter_key(filters)
        if key not in actual_groups:
            actual_groups[key] = {"filters": filters, "hotstrings": []}
        actual_groups[key]["hotstrings"].append(hotstring)

    if actual_groups:
        configs = _plan_espanso_scoped_configs(actual_groups)
        synthetic_count = sum(1 for item in configs if bool(item.get("synthetic")))
        if synthetic_count:
            add(
                severity="info",
                code="ESPANSO_SCOPE_COMPOSITE_CONFIG",
                path="espanso:package-dir:scopes",
                message=(
                    f"Espanso package-dir export would generate {synthetic_count} synthetic composite config(s) so overlapping scoped hotstrings stay active despite Espanso's one-active-config rule."
                ),
                suggestion=(
                    "Review the generated `config/` ordering and synthetic composites after running `vhk gen-espanso --package-dir`."
                ),
                synthetic_config_count=synthetic_count,
                scoped_filter_count=len(actual_groups),
            )

    return issues


def _unified_diff(
    before_text: str,
    after_text: str,
    *,
    fromfile: str,
    tofile: str,
    context: int = 3,
) -> str:
    """Return a unified diff as plain text."""

    before_lines = before_text.splitlines(keepends=True)
    after_lines = after_text.splitlines(keepends=True)
    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=fromfile,
        tofile=tofile,
        n=int(context),
        lineterm="",
    )
    out = "\n".join(diff)
    if out and not out.endswith("\n"):
        out += "\n"
    return out


def _escape_i3_str(s: str) -> str:
    # i3 criteria strings are quoted; escape backslash + double quotes.
    return s.replace("\\", "\\\\").replace('"', '\\"')


_I3_REGEX_META_RE = re.compile(r"([.^$*+?{}\[\]\\|()])")


def _escape_i3_regex_literal(s: str) -> str:
    return _I3_REGEX_META_RE.sub(r"\\\1", s)


def _exact_i3_pattern(value: str) -> str:
    return f"^{_escape_i3_regex_literal(value)}$"


def _selector_to_i3_criteria(sel: I3WindowSelector, *, include_pid: bool = False) -> str:
    """Convert a selector to i3's criteria syntax.

    Notes
    -----
    i3 criteria such as class/instance/title are regular expressions (PCRE).
    We keep this conservative: only fields that cleanly map to criteria are
    emitted.
    """

    parts: list[str] = []
    if sel.wm_class:
        parts.append(f'class="{_escape_i3_str(sel.wm_class)}"')
    if sel.instance:
        parts.append(f'instance="{_escape_i3_str(sel.instance)}"')
    if getattr(sel, "window_role", None):
        parts.append(f'window_role="{_escape_i3_str(getattr(sel, "window_role"))}"')
    if sel.title:
        parts.append(f'title="{_escape_i3_str(sel.title)}"')
    # sway native windows use app_id.
    if getattr(sel, "app_id", None):
        parts.append(f'app_id="{_escape_i3_str(getattr(sel, "app_id"))}"')
    if include_pid and getattr(sel, "pid", None) is not None:
        parts.append(f'pid="{int(getattr(sel, "pid"))}"')
    if not parts:
        return ""
    return "[" + " ".join(parts) + "]"


def _selector_to_i3_exact_criteria(sel: I3WindowSelector, *, include_title: bool = True, include_pid: bool = False) -> str:
    parts: list[str] = []
    if sel.wm_class:
        parts.append(f'class="{_escape_i3_str(_exact_i3_pattern(sel.wm_class))}"')
    if sel.instance:
        parts.append(f'instance="{_escape_i3_str(_exact_i3_pattern(sel.instance))}"')
    if getattr(sel, "window_role", None):
        parts.append(f'window_role="{_escape_i3_str(_exact_i3_pattern(getattr(sel, "window_role")))}"')
    if include_title and sel.title:
        parts.append(f'title="{_escape_i3_str(_exact_i3_pattern(sel.title))}"')
    if getattr(sel, "app_id", None):
        parts.append(f'app_id="{_escape_i3_str(_exact_i3_pattern(getattr(sel, "app_id")))}"')
    if include_pid and getattr(sel, "pid", None) is not None:
        parts.append(f'pid="{int(getattr(sel, "pid"))}"')
    if not parts:
        return ""
    return "[" + " ".join(parts) + "]"


def _selector_without_title(sel: I3WindowSelector) -> I3WindowSelector:
    sel2 = sel.model_copy(deep=True)
    sel2.title = None
    sel2.title_regex = False
    return sel2


def _selector_match_summary(match) -> dict[str, object]:
    wp = match.node.get("window_properties") or {}
    return {
        "id": match.node.get("id") or match.node.get("window"),
        "workspace": match.workspace,
        "class": wp.get("class"),
        "instance": wp.get("instance"),
        "window_role": wp.get("window_role") or wp.get("role"),
        "title": wp.get("title") or match.node.get("name"),
        "focused": bool(match.node.get("focused")),
    }


def _preview_selector_against_i3(stable: I3WindowSelector, exact: I3WindowSelector) -> dict[str, object]:
    try:
        socket_path = discover_socket_path()
        tree = I3Connection(socket_path=socket_path).get_tree()
    except Exception as exc:
        return {
            "status": "unavailable",
            "error": str(exc),
        }

    stable_matches = find_all(tree, stable)
    exact_matches = find_all(tree, exact)
    warnings: list[str] = []
    if len(stable_matches) > 1:
        warnings.append("Stable selector matches multiple current windows; add title only if you truly need a single instance.")
    if len(exact_matches) == 0:
        warnings.append("Exact selector does not match a current i3 window; this can happen if the title changed or the window is unmanaged.")
    if len(exact_matches) > 1:
        warnings.append("Exact selector still matches multiple current windows; prefer adding workspace context or a more specific role/title.")

    return {
        "status": "ok",
        "socket_path": socket_path,
        "stable": {
            "match_count": len(stable_matches),
            "matches": [_selector_match_summary(m) for m in stable_matches[:5]],
            "truncated": len(stable_matches) > 5,
        },
        "exact": {
            "match_count": len(exact_matches),
            "matches": [_selector_match_summary(m) for m in exact_matches[:5]],
            "truncated": len(exact_matches) > 5,
        },
        "warnings": warnings,
        "session_capabilities": session_capabilities,
    }


def _selector_to_criteria(sel: I3WindowSelector, *, wm: str) -> str:
    # i3 doesn't understand sway's app_id/pid criteria; keep those for sway.
    if wm == "i3":
        sel2 = sel.model_copy()
        sel2.app_id = None  # type: ignore[attr-defined]
        return _selector_to_i3_criteria(sel2, include_pid=False)
    return _selector_to_i3_criteria(sel, include_pid=True)


def _default_wm() -> str:
    # If we're on a Wayland session, users are probably on a Wayland compositor.
    # Hyprland sets HYPRLAND_INSTANCE_SIGNATURE.
    if os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"):
        return "hyprland"
    # sway exports SWAYSOCK.
    if os.environ.get("SWAYSOCK"):
        return "sway"
    # Fallback: i3 on X11, sway on Wayland.
    return "sway" if detect_backend() == "wayland" else "i3"

def _apply_preset_prompt_overlay(
    project,
    resolved,
    *,
    initial_vars: dict[str, object],
    dry_run: bool = False,
    quiet: bool = False,
    prompt_profile: str | None = None,
    save_prompt_profile: str | None = None,
) -> dict[str, object] | None:
    """Apply an optional preset prompt overlay to initial vars.

    Preset vars are merged first, then CLI-provided vars, then prompt answers so
    the prompt can see CLI defaults while still letting the user confirm or
    override prompted fields interactively.
    """

    if getattr(resolved, "prompt_form", None) is None:
        return initial_vars
    profile_key = resolve_preset_profile_key(
        resolved.prompt_form,
        {"macro": {"name": resolved.macro_name}, "preset": {"name": resolved.preset_name or "default"}, **dict(initial_vars)},
        macro_name=resolved.macro_name,
        preset_name=resolved.preset_name,
    )
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    try:
        prompt_values = prompt_preset_overlay(
            resolved.prompt_form,
            dict(initial_vars),
            dry_run=dry_run,
            profile_store=store,
            profile_key=profile_key,
            prompt_profile=prompt_profile,
            save_prompt_profile=save_prompt_profile,
        )
    except TypeError:
        prompt_values = prompt_preset_overlay(resolved.prompt_form, dict(initial_vars), dry_run=dry_run)
    if prompt_values is not None and profile_key:
        from vhk.project.prompt_profiles import sanitize_prompt_answers
        saved = sanitize_prompt_answers(getattr(resolved.prompt_form, "fields", []), prompt_values)
        if saved:
            store.save_last(profile_key, saved)
            if save_prompt_profile:
                store.save_profile(profile_key, save_prompt_profile, saved)
    if prompt_values is None:
        if not quiet:
            console.print("[yellow]Cancelled preset prompt.[/yellow]")
        return None
    merged = dict(initial_vars)
    merged.update(prompt_values)
    return merged



@app.command()
def run(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    macro: str = typer.Argument(..., help="Macro name to run"),
    preset: str | None = typer.Option(None, "--preset", help="Saved parameter preset defined on the macro"),
    vars_json: str | None = typer.Option(None, "--vars", help="Initial vars as JSON"),
    preset_prompts: bool = typer.Option(True, "--preset-prompts/--no-preset-prompts", help="Allow preset-attached prompt forms to collect additional values before running"),
    prompt_profile: str | None = typer.Option(None, "--prompt-profile", help="Named prompt profile to preload for PromptForm steps and preset overlays"),
    save_prompt_profile: str | None = typer.Option(None, "--save-prompt-profile", help="Save submitted prompt answers under this named profile"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress human-friendly output (keep stdout clean for integrations)"),
    print_return: bool = typer.Option(
        False, "--print-return", help="Print the macro's return value (default return_value) to stdout on success"
    ),
    return_var: str = typer.Option("return_value", "--return-var", help="Variable name to print with --print-return"),
    step: bool = typer.Option(False, "--step", help="Interactive step-through (press Enter per step)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Override project settings: do not execute side effects"),
    require_window: str | None = typer.Option(
        None,
        "--require-window",
        help="Run only if the currently active window matches this JSON selector (useful for WMs without native criteria-scoped keybinds)",
    ),
):
    """Run a macro from a project folder."""

    project = load_project(project_dir)

    # Optional active-window gating.
    if require_window:
        try:
            selector = I3WindowSelector.model_validate_json(require_window)
        except Exception as exc:
            raise typer.BadParameter(f"require-window must be valid JSON for I3WindowSelector: {exc}")

        try:
            from vhk.system.active_window import ActiveWindowProbeError, active_window_matches

            ok, wm = active_window_matches(selector)
        except ActiveWindowProbeError as exc:
            if not quiet:
                console.print(f"[red]Active window probe failed:[/red] {exc}")
            raise typer.Exit(code=2)
        except Exception as exc:
            if not quiet:
                console.print(f"[red]Active window probe crashed:[/red] {exc}")
            raise typer.Exit(code=2)

        if not ok:
            if not quiet:
                console.print(f"[yellow]Skipped:[/yellow] active window does not match selector (wm={wm}).")
            raise typer.Exit(code=0)
    if dry_run:
        project.settings.dry_run = True
    if macro not in project.macros:
        raise typer.BadParameter(f"Unknown macro '{macro}'. Available: {', '.join(project.macros.keys())}")

    try:
        resolved = resolve_macro_preset(project, macro, preset_name=preset)
    except KeyError:
        available = ", ".join(p.name for p in project.macros[macro].presets) or "(none)"
        raise typer.BadParameter(f"Unknown preset '{preset}' for macro '{macro}'. Available: {available}")

    initial_vars = dict(resolved.vars)
    if vars_json:
        initial_vars.update(json.loads(vars_json))
    if preset_prompts:
        maybe_vars = _apply_preset_prompt_overlay(project, resolved, initial_vars=initial_vars, dry_run=project.settings.dry_run, quiet=quiet, prompt_profile=prompt_profile, save_prompt_profile=save_prompt_profile)
        if maybe_vars is None:
            raise typer.Exit(code=0)
        initial_vars = maybe_vars

    run_console = Console(file=sys.stderr, force_terminal=False) if (quiet or print_return) else console

    runner = Runner(project=project, console=run_console, step_mode=step, prompt_profile=prompt_profile, save_prompt_profile=save_prompt_profile)
    result = runner.run(macro_name=macro, initial_vars=initial_vars)

    if not result.ok:
        run_console.print(f"[red]Macro failed:[/red] {result.error}")
        raise typer.Exit(code=1)

    if print_return:
        value = None
        if result.vars:
            value = result.vars.get(return_var)
        if value is None:
            return
        if isinstance(value, (dict, list)):
            out = json.dumps(value, ensure_ascii=False)
        else:
            out = str(value)
        sys.stdout.write(out)
        return

    if (not quiet) and result.event_log:
        console.print(f"[dim]Event log:[/dim] {result.event_log}")


@app.command()
def list_macros(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
):
    """List macros in a project."""

    project = load_project(project_dir)
    for name in sorted(project.macros.keys()):
        console.print(name)


def _profile_payload(project, store, *, include_values: bool = False) -> dict[str, Any]:
    profiles = store.list_all_profiles()
    payload: dict[str, Any] = {
        "project": project.name,
        "count": sum(len(v) for v in profiles.values()),
        "keys": profiles,
    }
    if include_values:
        payload["profiles"] = store.export_profiles()
        definitions = build_prompt_profile_definitions(project)
        payload["definitions"] = {k: v.to_dict() for k, v in definitions.items()}
    return payload


def _materialize_profile_fields(project, profile_key: str, profile_name: str):
    definition = find_prompt_profile_definition(project, profile_key)
    if definition is None:
        return None, None
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    saved = store.load_profile(profile_key, profile_name)
    fields = apply_saved_answers(list(definition.fields), saved)
    return definition, fields


def _edit_prompt_profile(project, store, profile_key: str, name: str, *, values_json: str | None = None, quiet: bool = False) -> bool:
    definition = find_prompt_profile_definition(project, profile_key)
    if definition is None:
        if not quiet:
            console.print(f"[red]No prompt definition found for profile key:[/red] {profile_key}")
        return False
    saved = store.load_profile(profile_key, name)
    fields = apply_saved_answers(list(definition.fields), saved)
    values = json.loads(values_json) if values_json else prompt_form(fields, title=definition.title or f"Edit profile {name}", text=definition.text or f"Update saved values for {profile_key}")
    if values is None:
        return False
    clean = sanitize_prompt_answers(fields, values)
    store.save_profile(profile_key, name, clean)
    if not quiet:
        console.print(f"[green]Updated prompt profile:[/green] {profile_key} #{name}")
    return True


def _copy_prompt_profile(project, store, profile_key: str, source_name: str, target_name: str | None, *, overwrite: bool = False, quiet: bool = False) -> bool:
    target = str(target_name or "").strip()
    if not target:
        target = str(input_text(f"Copy profile '{source_name}' to", title="Copy prompt profile", default=f"{source_name}-copy") or "").strip()
    if not target:
        return False
    try:
        ok = store.copy_profile(profile_key, source_name, target, overwrite=overwrite)
    except FileExistsError:
        if not ask_yes_no(f"Overwrite existing profile '{target}'?", title="Copy prompt profile", default_yes=False):
            return False
        ok = store.copy_profile(profile_key, source_name, target, overwrite=True)
    if not ok:
        if not quiet:
            console.print(f"[red]Prompt profile not found:[/red] {profile_key} #{source_name}")
        return False
    if not quiet:
        console.print(f"[green]Copied prompt profile:[/green] {profile_key} #{source_name} → #{target}")
    return True


def _rename_prompt_profile(project, store, profile_key: str, old_name: str, new_name: str | None, *, overwrite: bool = False, quiet: bool = False) -> bool:
    target = str(new_name or "").strip()
    if not target:
        target = str(input_text(f"Rename profile '{old_name}' to", title="Rename prompt profile", default=old_name) or "").strip()
    if not target:
        return False
    try:
        ok = store.rename_profile(profile_key, old_name, target, overwrite=overwrite)
    except FileExistsError:
        if not ask_yes_no(f"Overwrite existing profile '{target}'?", title="Rename prompt profile", default_yes=False):
            return False
        ok = store.rename_profile(profile_key, old_name, target, overwrite=True)
    if not ok:
        if not quiet:
            console.print(f"[red]Prompt profile not found:[/red] {profile_key} #{old_name}")
        return False
    if not quiet:
        console.print(f"[green]Renamed prompt profile:[/green] {profile_key} #{old_name} → #{target}")
    return True


def _delete_prompt_profile(project, store, profile_key: str, name: str, *, confirm: bool = True, quiet: bool = False) -> bool:
    if confirm and not ask_yes_no(f"Delete prompt profile '{name}' for {profile_key}?", title="Delete prompt profile", default_yes=False):
        return False
    if not store.delete_profile(profile_key, name):
        if not quiet:
            console.print(f"[red]Prompt profile not found:[/red] {profile_key} #{name}")
        return False
    if not quiet:
        console.print(f"[green]Deleted prompt profile:[/green] {profile_key} #{name}")
    return True


def _handle_palette_profile_action(project, store, selected) -> bool:
    profile_key = selected.prompt_profile_key
    profile_name = selected.prompt_profile
    if not profile_key or not profile_name:
        console.print(f"[red]Palette entry is missing prompt profile metadata:[/red] {selected.entry_id}")
        return False
    if selected.action == "edit_profile":
        return _edit_prompt_profile(project, store, profile_key, profile_name)
    if selected.action == "copy_profile":
        return _copy_prompt_profile(project, store, profile_key, profile_name, None)
    if selected.action == "rename_profile":
        return _rename_prompt_profile(project, store, profile_key, profile_name, None)
    if selected.action == "delete_profile":
        return _delete_prompt_profile(project, store, profile_key, profile_name, confirm=True)
    console.print(f"[red]Unknown palette profile action:[/red] {selected.action}")
    return False


@app.command()
def palette(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    as_json: bool = typer.Option(False, "--json", help="Print palette entries as JSON instead of opening a chooser"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include macros marked hidden in palette output"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include saved parameter presets as separate palette entries"),
    recent_first: bool = typer.Option(True, "--recent-first/--alpha", help="Sort by recent runs first (default) or alphabetically"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Override project settings: do not execute side effects"),
    vars_json: str | None = typer.Option(None, "--vars", help="Initial vars as JSON when running the selected macro"),
    preset_prompts: bool = typer.Option(True, "--preset-prompts/--no-preset-prompts", help="Allow preset-attached prompt forms to collect additional values before running"),
    prompt_profile: str | None = typer.Option(None, "--prompt-profile", help="Named prompt profile to preload for PromptForm steps and preset overlays"),
    save_prompt_profile: str | None = typer.Option(None, "--save-prompt-profile", help="Save submitted prompt answers under this named profile"),
    profile_actions: bool = typer.Option(True, "--profile-actions/--no-profile-actions", help="Expand saved prompt profiles as separate palette entries for prompted presets"),
    profile_management_actions: bool = typer.Option(False, "--profile-management-actions/--no-profile-management-actions", help="Expand saved profiles into explicit edit/copy/rename/delete palette actions"),
    entry_id: str | None = typer.Option(None, "--entry-id", help="Resolve and optionally run one palette entry directly by stable id"),
    no_run: bool = typer.Option(False, "--no-run", help="Choose a macro, preset, or saved-profile action but do not run it"),
    history_limit: int = typer.Option(50, "--history-limit", min=1, help="How many recent runs to scan when ranking palette entries"),
):
    """Open a launcher-friendly macro palette for a project."""

    project = load_project(project_dir)
    if dry_run:
        project.settings.dry_run = True

    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    entries = build_palette_entries(
        project,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=profile_actions,
        include_profile_management_actions=profile_management_actions,
        profile_store=store,
        recent_first=recent_first,
        history_limit=history_limit,
    )
    payload = {
        "project": project.name,
        "count": len(entries),
        "entries": [e.to_dict() for e in entries],
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return

    if not entries:
        console.print("[yellow]No palette-visible macros found.[/yellow]")
        raise typer.Exit(code=0)

    selected = None
    if entry_id is not None:
        selected = find_palette_entry(entries, entry_id=entry_id)
        if selected is None:
            console.print(f"[red]Unknown palette entry id:[/red] {entry_id}")
            raise typer.Exit(code=2)
    else:
        labels = [e.label for e in entries]
        chosen = choose_from_list(labels, title=project.name, text="Run macro")
        if not chosen:
            raise typer.Exit(code=0)
        selected = find_palette_entry(entries, label=chosen)
        if selected is None:
            console.print(f"[red]Unknown palette selection:[/red] {chosen}")
            raise typer.Exit(code=2)

    if no_run:
        sys.stdout.write(selected.entry_id + "\n")
        return

    if selected.action != "run":
        ok = _handle_palette_profile_action(project, store, selected)
        raise typer.Exit(code=0 if ok else 1)

    try:
        resolved = resolve_macro_preset(project, selected.macro, preset_name=selected.preset)
    except KeyError:
        console.print(f"[red]Unknown palette selection preset:[/red] {selected.entry_id}")
        raise typer.Exit(code=2)

    initial_vars = dict(resolved.vars)
    if vars_json:
        initial_vars.update(json.loads(vars_json))
    if preset_prompts:
        selected_prompt_profile = selected.prompt_profile or prompt_profile
        maybe_vars = _apply_preset_prompt_overlay(project, resolved, initial_vars=initial_vars, dry_run=project.settings.dry_run, prompt_profile=selected_prompt_profile, save_prompt_profile=save_prompt_profile)
        if maybe_vars is None:
            raise typer.Exit(code=0)
        initial_vars = maybe_vars
    selected_prompt_profile = selected.prompt_profile or prompt_profile
    runner = Runner(project=project, console=console, prompt_profile=selected_prompt_profile, save_prompt_profile=save_prompt_profile)
    result = runner.run(macro_name=selected.macro, initial_vars=initial_vars)

    if not result.ok:
        console.print(f"[red]Macro failed:[/red] {result.error}")
        raise typer.Exit(code=1)

    if result.event_log:
        console.print(f"[dim]Event log:[/dim] {result.event_log}")


@app.command()
def export_launcher_script(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Argument(None, help="Output script path; omit to print to stdout"),
    install: bool = typer.Option(False, "--install", help="Write the launcher script to ~/.local/bin or XDG_BIN_HOME"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file"),
    launcher_id: str | None = typer.Option(None, "--launcher-id", help="Override the launcher script basename"),
    title: str | None = typer.Option(None, "--title", help="Launcher prompt title"),
    command: str = typer.Option("vhk", "--command", help="Executable to invoke for vhk commands inside the script"),
    launcher_backend: str = typer.Option("auto", "--launcher-backend", help="Preferred launcher backend: auto|rofi|dmenu|wofi|fuzzel|tofi|console"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in exported palette rows"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include presets as separate launcher rows"),
    profile_actions: bool = typer.Option(True, "--profile-actions/--no-profile-actions", help="Include saved prompt profiles as separate launcher rows"),
    profile_management_actions: bool = typer.Option(False, "--profile-management-actions/--no-profile-management-actions", help="Include edit/copy/rename/delete prompt-profile rows"),
    alpha: bool = typer.Option(False, "--alpha", help="Sort exported rows alphabetically instead of using recent-first ordering"),
    history_limit: int = typer.Option(50, "--history-limit", min=1, help="How many recent runs to scan when ranking exported rows"),
):
    """Export a launcher-script wrapper for this VHK project palette."""

    project = load_project(project_dir)
    text = render_launcher_script(
        project,
        command=command,
        title=title,
        launcher_backend=launcher_backend,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=profile_actions,
        include_profile_management_actions=profile_management_actions,
        alpha=alpha,
        history_limit=history_limit,
    )

    target = default_launcher_install_path(project, launcher_id=launcher_id) if install else output
    if target is None:
        sys.stdout.write(text)
        return

    if target.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {target}")
        console.print("Use [bold]--force[/bold] to replace it.")
        raise typer.Exit(code=1)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    target.chmod(target.stat().st_mode | 0o111)
    console.print(f"[green]Wrote launcher script:[/green] {target}")


@app.command()
def export_rofi_mode(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Argument(None, help="Output script path; required unless --install is used"),
    install: bool = typer.Option(False, "--install", help="Write the launcher script to ~/.local/bin or XDG_BIN_HOME"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file"),
    launcher_id: str | None = typer.Option(None, "--launcher-id", help="Override the launcher script basename"),
    mode_name: str | None = typer.Option(None, "--mode-name", help="Rofi mode name to expose"),
    command: str = typer.Option("vhk", "--command", help="Executable to invoke for vhk commands inside the script"),
    title: str | None = typer.Option(None, "--title", help="Prompt title inside the exported launcher script"),
    show_icons: bool = typer.Option(True, "--show-icons/--no-show-icons", help="Include -show-icons in the suggested rofi command"),
    extra_mode: list[str] = typer.Option([], "--extra-mode", help="Additional rofi modes to include before the VHK mode; may be repeated"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in exported palette rows"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include presets as separate launcher rows"),
    profile_actions: bool = typer.Option(True, "--profile-actions/--no-profile-actions", help="Include saved prompt profiles as separate launcher rows"),
    profile_management_actions: bool = typer.Option(False, "--profile-management-actions/--no-profile-management-actions", help="Include edit/copy/rename/delete prompt-profile rows"),
    alpha: bool = typer.Option(False, "--alpha", help="Sort exported rows alphabetically instead of using recent-first ordering"),
    history_limit: int = typer.Option(50, "--history-limit", min=1, help="How many recent runs to scan when ranking exported rows"),
    as_json: bool = typer.Option(False, "--json", help="Print a JSON manifest instead of human-readable instructions"),
):
    """Export a rofi script-mode launcher for this VHK project palette."""

    project = load_project(project_dir)
    target = default_launcher_install_path(project, launcher_id=launcher_id) if install else output
    if target is None:
        console.print("[red]Need an output path or --install for export-rofi-mode.[/red]")
        raise typer.Exit(code=1)

    text = render_launcher_script(
        project,
        command=command,
        title=title,
        launcher_backend="rofi",
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=profile_actions,
        include_profile_management_actions=profile_management_actions,
        alpha=alpha,
        history_limit=history_limit,
    )

    if target.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {target}")
        console.print("Use [bold]--force[/bold] to replace it.")
        raise typer.Exit(code=1)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    target.chmod(target.stat().st_mode | 0o111)

    manifest = build_rofi_mode_manifest(
        project,
        script_path=target,
        mode_name=mode_name,
        show_icons=show_icons,
        extra_modes=extra_mode,
    )

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return

    console.print(f"[green]Wrote rofi mode launcher:[/green] {target}")
    console.print(f"[dim]Mode:[/dim] {manifest.mode_name}")
    console.print("[dim]Run with:[/dim]")
    console.print(manifest.command)


@app.command(name="gen-dragonfly-pack")
def gen_dragonfly_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/dragonfly)"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to invoke for VHK runs inside the generated grammar module"),
    grammar_name: str | None = typer.Option(None, "--grammar-name", help="Override the Dragonfly grammar name"),
    module_name: str | None = typer.Option(None, "--module-name", help="Override the generated Python module filename"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in the generated command module"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include macro presets as separate spoken commands"),
    include_prompt_entries: bool = typer.Option(False, "--include-prompt-entries", help="Include preset entries that still open an interactive prompt overlay"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable Dragonfly voice-command pack for this project.

    This keeps voice triggering as an adapter layer. The generated Dragonfly
    module does not re-implement any VHK automation logic; it simply maps spoken
    phrases to `vhk run ...` subprocess calls.
    """

    project = load_project(project_dir)
    target_dir = out_dir or default_dragonfly_dir(project)
    manifest = write_dragonfly_pack(
        project,
        out_dir=target_dir,
        command=command,
        grammar_name=grammar_name,
        module_name=module_name,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_prompt_entries=include_prompt_entries,
    )

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote Dragonfly pack:[/green] {target_dir}")
    console.print(f"[dim]Module:[/dim] {manifest.module_path}")
    console.print(f"[dim]Commands:[/dim] {len(manifest.commands)} included, {len(manifest.skipped)} skipped")
    console.print(f"[dim]Manifest:[/dim] {manifest.commands_path}")


@app.command(name="gen-talon-pack")
def gen_talon_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/talon)"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to invoke for VHK runs inside the generated Talon action module"),
    base_name: str | None = typer.Option(None, "--base-name", help="Override the generated Talon file basename (without extension)"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in the generated Talon pack"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include macro presets as separate spoken commands"),
    include_prompt_entries: bool = typer.Option(False, "--include-prompt-entries", help="Include preset entries that still open an interactive prompt overlay"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable Talon voice-command pack for this project.

    This keeps voice triggering as an adapter layer. The generated Talon files
    do not re-implement any VHK automation logic; they simply map spoken
    phrases to `vhk run ...` subprocess calls.
    """

    project = load_project(project_dir)
    target_dir = out_dir or default_talon_dir(project)
    manifest = write_talon_pack(
        project,
        out_dir=target_dir,
        command=command,
        base_name=base_name,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_prompt_entries=include_prompt_entries,
    )

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote Talon pack:[/green] {target_dir}")
    console.print(f"[dim]Command file:[/dim] {manifest.talon_path}")
    console.print(f"[dim]Python module:[/dim] {manifest.python_path}")
    console.print(f"[dim]Commands:[/dim] {len(manifest.commands)} included, {len(manifest.skipped)} skipped")
    console.print(f"[dim]Manifest:[/dim] {manifest.commands_path}")


@app.command(name="gen-playerctl-pack")
def gen_playerctl_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/playerctl)"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to invoke for VHK runs inside generated helper scripts"),
    base_name: str | None = typer.Option(None, "--base-name", help="Override the generated pack basename used in metadata"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable playerctl/MPRIS adapter pack for this project.

    The generated artifacts keep playerctl as the thin media-control and follow
    surface. VHK still owns macro semantics and route review.
    """

    project = load_project(project_dir)
    target_dir = out_dir or default_playerctl_dir(project)
    manifest = write_playerctl_pack(
        project,
        out_dir=target_dir,
        command=command,
        base_name=base_name,
    )

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote playerctl pack:[/green] {target_dir}")
    console.print(f"[dim]Routes:[/dim] {len(manifest.routes)}")
    console.print(f"[dim]Route catalog:[/dim] {manifest.routes_path}")
    console.print(f"[dim]Manifest:[/dim] {manifest.commands_path}")


@app.command(name="gen-wezterm-pack")
def gen_wezterm_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/wezterm)"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable WezTerm CLI adapter pack for this project."""

    project = load_project(project_dir)
    target_dir = out_dir or default_wezterm_dir(project)
    manifest = write_wezterm_pack(project, out_dir=target_dir)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote WezTerm pack:[/green] {target_dir}")
    console.print(f"[dim]Routes:[/dim] {len(manifest.routes)}")
    console.print(f"[dim]Skipped:[/dim] {len(manifest.skipped)}")
    console.print(f"[dim]Route catalog:[/dim] {manifest.routes_path}")
    console.print(f"[dim]Manifest:[/dim] {manifest.commands_path}")


@app.command(name="gen-mpv-pack")
def gen_mpv_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/mpv)"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable mpv JSON IPC adapter pack for this project."""

    project = load_project(project_dir)
    target_dir = out_dir or default_mpv_dir(project)
    manifest = write_mpv_pack(project, out_dir=target_dir)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote mpv pack:[/green] {target_dir}")
    console.print(f"[dim]Routes:[/dim] {len(manifest.routes)}")
    console.print(f"[dim]Skipped:[/dim] {len(manifest.skipped)}")
    console.print(f"[dim]Route catalog:[/dim] {manifest.routes_path}")
    console.print(f"[dim]Manifest:[/dim] {manifest.commands_path}")


@app.command(name="gen-qutebrowser-pack")
def gen_qutebrowser_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/qutebrowser)"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to invoke for VHK runs inside generated qutebrowser userscripts"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable qutebrowser userscript adapter pack for this project."""

    project = load_project(project_dir)
    target_dir = out_dir or default_qutebrowser_dir(project)
    manifest = write_qutebrowser_pack(project, out_dir=target_dir, command=command)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote qutebrowser pack:[/green] {target_dir}")
    console.print(f"[dim]Routes:[/dim] {len(manifest.routes)}")
    console.print(f"[dim]Userscripts:[/dim] {len(manifest.userscript_paths)}")
    console.print(f"[dim]Route catalog:[/dim] {manifest.routes_path}")
    console.print(f"[dim]Manifest:[/dim] {manifest.commands_path}")


@app.command(name="gen-kitty-pack")
def gen_kitty_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/kitty)"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable kitty remote-control adapter pack for this project."""

    project = load_project(project_dir)
    target_dir = out_dir or default_kitty_dir(project)
    manifest = write_kitty_pack(project, out_dir=target_dir)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote kitty pack:[/green] {target_dir}")
    console.print(f"[dim]Routes:[/dim] {len(manifest.routes)}")
    console.print(f"[dim]Skipped:[/dim] {len(manifest.skipped)}")
    console.print(f"[dim]Route catalog:[/dim] {manifest.routes_path}")
    console.print(f"[dim]Manifest:[/dim] {manifest.commands_path}")


@app.command(name="gen-autokey-pack")
def gen_autokey_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Argument(None, help="Output directory (default: <project>/integrations/autokey)"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to invoke for VHK runs inside generated AutoKey scripts"),
    include_disabled: bool = typer.Option(False, "--include-disabled", help="Include disabled VHK hotstrings in the generated pack"),
    return_send_mode: str = typer.Option("keyboard", "--return-send-mode", help="AutoKey insertion mode for return-value hotstrings: keyboard|ctrl-v|ctrl-shift-v|shift-insert|selection"),
    allow_window_filter_approximation: bool = typer.Option(False, "--allow-window-filter-approximation", help="Allow scoped AutoKey exports that approximate VHK selectors with AutoKey's coarse title-or-class window regex"),
    as_json: bool = typer.Option(False, "--json", help="Print the generated manifest as JSON"),
):
    """Generate a reviewable AutoKey/X11 adapter pack for this project.

    The generated files keep VHK as the automation runner. AutoKey only owns
    the X11-facing hotstring/hotkey trigger layer.
    """

    project = load_project(project_dir)
    target_dir = out_dir or default_autokey_dir(project)
    manifest = write_autokey_pack(
        project,
        out_dir=target_dir,
        command=command,
        include_disabled=include_disabled,
        return_send_mode=return_send_mode,
        allow_window_filter_approximation=allow_window_filter_approximation,
    )

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return
    console.print(f"[green]Wrote AutoKey pack:[/green] {target_dir}")
    console.print(f"[dim]Data:[/dim] {manifest.data_dir}")
    console.print(f"[dim]Entries:[/dim] {len(manifest.entries)} included, {len(manifest.skipped)} skipped")
    console.print(f"[dim]Manifest:[/dim] {manifest.manifest_path}")


@app.command()
def export_wm_bindings(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Argument(None, help="Output config snippet path; omit to print to stdout"),
    wm: str = typer.Option(..., "--wm", help="Target WM / compositor: i3|sway|hyprland"),
    launcher: str = typer.Option("rofi-mode", "--launcher", help="Launcher surface: rofi-mode|launcher-script|palette-command"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file"),
    key: str | None = typer.Option(None, "--key", help="Override the binding key string; default depends on the target WM"),
    launcher_path: Path | None = typer.Option(None, "--launcher-path", help="Path to the exported launcher helper; defaults to the normal install path"),
    launcher_id: str | None = typer.Option(None, "--launcher-id", help="Launcher helper basename when a default helper path is implied"),
    mode_name: str | None = typer.Option(None, "--mode-name", help="Rofi mode name to reference when --launcher=rofi-mode"),
    show_icons: bool = typer.Option(True, "--show-icons/--no-show-icons", help="Include -show-icons in suggested rofi-mode commands"),
    extra_mode: list[str] = typer.Option([], "--extra-mode", help="Additional rofi modes to include before the VHK mode; may be repeated"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to use when --launcher=palette-command"),
    uwsm_app: bool = typer.Option(False, "--uwsm-app", help="For Hyprland, wrap the launcher with 'uwsm app --'"),
    as_json: bool = typer.Option(False, "--json", help="Print a JSON manifest instead of the config snippet"),
):
    """Export a ready-to-paste i3/sway/Hyprland binding snippet for a VHK launcher surface."""

    project = load_project(project_dir)
    try:
        manifest = build_wm_binding_manifest(
            project,
            wm=wm,
            launcher=launcher,
            key=key,
            launcher_path=launcher_path,
            launcher_id=launcher_id,
            mode_name=mode_name,
            show_icons=show_icons,
            extra_modes=extra_mode,
            command=command,
            uwsm_app=uwsm_app,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return

    if output is None:
        sys.stdout.write(manifest.snippet)
        return

    if output.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {output}")
        console.print("Use [bold]--force[/bold] to replace it.")
        raise typer.Exit(code=1)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(manifest.snippet, encoding="utf-8")
    console.print(f"[green]Wrote WM binding snippet:[/green] {output}")


@app.command()
def export_wm_launcher_mode(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Argument(None, help="Output WM mode/submap snippet path; omit to print to stdout"),
    wm: str = typer.Option(..., "--wm", help="Target WM / compositor: i3|sway|hyprland"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file"),
    mode_enter: str = typer.Option(..., "--mode-enter", help="Key chord that enters the WM launcher mode / submap"),
    mode_name: str = typer.Option("vhk-launch", "--mode-name", help="WM mode/submap name"),
    mode_one_shot: bool = typer.Option(True, "--mode-one-shot/--mode-sticky", help="Auto-exit the mode/submap after running one action"),
    mode_exit_keys: str = typer.Option("Escape,Return", "--mode-exit-keys", help="Comma-separated keys that leave the mode/submap"),
    launcher: str = typer.Option("palette-command", "--launcher", help="Launcher action for the dedicated launcher key: palette-command|rofi-mode|launcher-script"),
    launcher_key: str | None = typer.Option("p", "--launcher-key", help="Key inside the mode/submap that opens the selected launcher surface"),
    launcher_action: bool = typer.Option(True, "--launcher-action/--no-launcher-action", help="Include a dedicated launcher action inside the mode/submap"),
    launcher_path: Path | None = typer.Option(None, "--launcher-path", help="Path to the exported launcher helper; defaults to the normal install path"),
    launcher_id: str | None = typer.Option(None, "--launcher-id", help="Launcher helper basename when a default helper path is implied"),
    rofi_mode_name: str | None = typer.Option(None, "--rofi-mode-name", help="Rofi custom mode name when --launcher=rofi-mode"),
    show_icons: bool = typer.Option(True, "--show-icons/--no-show-icons", help="Include -show-icons in rofi launcher actions"),
    extra_mode: list[str] = typer.Option([], "--extra-mode", help="Additional rofi modes to include before the VHK mode; may be repeated"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to use for palette-entry actions and --launcher=palette-command"),
    uwsm_app: bool = typer.Option(False, "--uwsm-app", help="For Hyprland, wrap launcher commands with 'uwsm app --'"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in direct launcher-mode entries"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include presets as separate direct launcher-mode entries"),
    profile_actions: bool = typer.Option(True, "--profile-actions/--no-profile-actions", help="Include saved prompt profiles as separate direct launcher-mode entries"),
    profile_management_actions: bool = typer.Option(False, "--profile-management-actions/--no-profile-management-actions", help="Include edit/copy/rename/delete prompt-profile entries"),
    alpha: bool = typer.Option(False, "--alpha", help="Sort launcher-mode entries alphabetically instead of using recent-first ordering"),
    history_limit: int = typer.Option(50, "--history-limit", min=1, help="How many recent runs to scan when ranking launcher-mode entries"),
    entry_keys: str = typer.Option("1,2,3,4,5,6,7,8,9,0", "--entry-keys", help="Comma-separated keys assigned to direct palette entries inside the mode/submap"),
    max_entries: int | None = typer.Option(None, "--max-entries", min=0, help="Maximum number of direct palette entries to include (defaults to the number of entry keys)"),
    as_json: bool = typer.Option(False, "--json", help="Print a JSON manifest instead of the config snippet"),
):
    """Export an i3/sway mode or Hyprland submap for launcher and palette-entry actions."""

    project = load_project(project_dir)
    target = output
    if target is None and not as_json:
        target = None

    try:
        manifest = build_wm_launcher_mode_manifest(
            project,
            wm=wm,
            mode_enter=mode_enter,
            mode_name=mode_name,
            launcher=launcher,
            launcher_key=launcher_key,
            launcher_path=launcher_path,
            launcher_id=launcher_id,
            rofi_mode_name=rofi_mode_name,
            show_icons=show_icons,
            extra_modes=extra_mode,
            command=command,
            include_launcher_action=launcher_action,
            include_hidden=include_hidden,
            include_presets=include_presets,
            include_profile_actions=profile_actions,
            include_profile_management_actions=profile_management_actions,
            alpha=alpha,
            history_limit=history_limit,
            entry_keys=[part.strip() for part in entry_keys.split(",") if part.strip()],
            max_entries=max_entries,
            one_shot=mode_one_shot,
            exit_keys=[part.strip() for part in mode_exit_keys.split(",") if part.strip()],
            uwsm_app=uwsm_app,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return

    if output is None:
        sys.stdout.write(manifest.snippet)
        return

    if output.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {output}")
        console.print("Use [bold]--force[/bold] to replace it.")
        raise typer.Exit(code=1)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(manifest.snippet, encoding="utf-8")
    console.print(f"[green]Wrote WM launcher mode snippet:[/green] {output}")


@app.command()
def export_wm_include(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Argument(None, help="Output include snippet path; omit to print to stdout"),
    wm: str = typer.Option(..., "--wm", help="Target WM / compositor: i3|sway|hyprland"),
    kind: str = typer.Option("binding", "--kind", help="Snippet kind: binding|launcher-mode"),
    install: bool = typer.Option(False, "--install", help="Write the snippet into a conventional XDG config include directory"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file"),
    launcher: str = typer.Option("rofi-mode", "--launcher", help="Launcher surface: rofi-mode|launcher-script|palette-command"),
    key: str | None = typer.Option(None, "--key", help="Top-level keybind when --kind=binding"),
    launcher_path: Path | None = typer.Option(None, "--launcher-path", help="Path to the exported launcher helper, when relevant"),
    launcher_id: str | None = typer.Option(None, "--launcher-id", help="Launcher helper basename when a default helper path is implied"),
    mode_name: str | None = typer.Option(None, "--mode-name", help="Rofi mode name for binding snippets or WM mode/submap name for launcher-mode snippets"),
    rofi_mode_name: str | None = typer.Option(None, "--rofi-mode-name", help="Rofi mode name used inside launcher-mode snippets when --launcher=rofi-mode"),
    show_icons: bool = typer.Option(True, "--show-icons/--no-show-icons", help="Include icons in rofi launcher commands where applicable"),
    extra_mode: list[str] = typer.Option([], "--extra-mode", help="Additional rofi modes to include before the VHK mode; may be repeated"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to use when --launcher=palette-command or when dispatching palette entry ids"),
    uwsm_app: bool = typer.Option(False, "--uwsm-app", help="For Hyprland, wrap launcher commands with 'uwsm app --'"),
    mode_enter: str | None = typer.Option(None, "--mode-enter", help="Key chord that enters the WM launcher mode / submap when --kind=launcher-mode"),
    mode_one_shot: bool = typer.Option(True, "--mode-one-shot/--mode-sticky", help="Auto-exit the mode/submap after running one action"),
    mode_exit_keys: str = typer.Option("Escape,Return", "--mode-exit-keys", help="Comma-separated keys that leave the mode/submap"),
    launcher_key: str | None = typer.Option("p", "--launcher-key", help="Key inside the mode/submap that opens the selected launcher surface"),
    launcher_action: bool = typer.Option(True, "--launcher-action/--no-launcher-action", help="Include a dedicated launcher action inside the mode/submap"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in exported launcher-mode entries"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include presets as separate exported launcher-mode entries"),
    profile_actions: bool = typer.Option(True, "--profile-actions/--no-profile-actions", help="Include saved prompt profiles as separate exported launcher-mode entries"),
    profile_management_actions: bool = typer.Option(False, "--profile-management-actions/--no-profile-management-actions", help="Include edit/copy/rename/delete prompt-profile entries in launcher-mode snippets"),
    alpha: bool = typer.Option(False, "--alpha", help="Sort launcher-mode entries alphabetically instead of using recent-first ordering"),
    history_limit: int = typer.Option(50, "--history-limit", min=1, help="How many recent runs to scan when ranking launcher-mode entries"),
    entry_keys: str = typer.Option("1,2,3,4,5,6,7,8,9,0", "--entry-keys", help="Comma-separated keys assigned to direct palette entries inside launcher-mode snippets"),
    max_entries: int | None = typer.Option(None, "--max-entries", min=0, help="Maximum number of direct palette entries to include (defaults to the number of entry keys)"),
    as_json: bool = typer.Option(False, "--json", help="Print a JSON manifest instead of the config snippet"),
):
    """Export a WM include-ready snippet plus the include/source line to add once to the main config."""

    project = load_project(project_dir)
    target = None
    if install:
        target = default_wm_include_install_path(project, wm=wm, kind=kind)
    elif output is not None:
        target = output

    kwargs: dict[str, Any]
    if str(kind).strip().lower() == "launcher-mode":
        if not str(mode_enter or "").strip():
            console.print("[red]--mode-enter is required when --kind=launcher-mode[/red]")
            raise typer.Exit(code=1)
        kwargs = {
            "mode_enter": str(mode_enter),
            "mode_name": mode_name or "vhk-launch",
            "launcher": launcher,
            "launcher_key": launcher_key,
            "launcher_path": launcher_path,
            "launcher_id": launcher_id,
            "rofi_mode_name": rofi_mode_name,
            "show_icons": show_icons,
            "extra_modes": extra_mode,
            "command": command,
            "include_launcher_action": launcher_action,
            "include_hidden": include_hidden,
            "include_presets": include_presets,
            "include_profile_actions": profile_actions,
            "include_profile_management_actions": profile_management_actions,
            "alpha": alpha,
            "history_limit": history_limit,
            "entry_keys": [part.strip() for part in entry_keys.split(",") if part.strip()],
            "max_entries": max_entries,
            "one_shot": mode_one_shot,
            "exit_keys": [part.strip() for part in mode_exit_keys.split(",") if part.strip()],
            "uwsm_app": uwsm_app,
        }
    else:
        kwargs = {
            "launcher": launcher,
            "key": key,
            "launcher_path": launcher_path,
            "launcher_id": launcher_id,
            "mode_name": mode_name,
            "show_icons": show_icons,
            "extra_modes": extra_mode,
            "command": command,
            "uwsm_app": uwsm_app,
        }

    try:
        manifest = build_wm_include_manifest(
            project,
            wm=wm,
            kind=kind,
            install_path=target,
            **kwargs,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return

    if target is None:
        sys.stdout.write(manifest.snippet)
        sys.stdout.write("\n")
        sys.stdout.write(f"# Add this once to {manifest.parent_config_path}:\n")
        sys.stdout.write(manifest.bootstrap_line + "\n")
        return

    if target.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {target}")
        console.print("Use [bold]--force[/bold] to replace it.")
        raise typer.Exit(code=1)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(manifest.snippet, encoding="utf-8")
    console.print(f"[green]Wrote WM include snippet:[/green] {target}")
    console.print(f"Add this once to [bold]{manifest.parent_config_path}[/bold]:")
    console.print(manifest.bootstrap_line)


@app.command()
def export_wm_bundle(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output_dir: Path | None = typer.Argument(None, help="Bundle directory; required unless --install is used"),
    wm: str = typer.Option(..., "--wm", help="Target WM / compositor: i3|sway|hyprland"),
    kind: str = typer.Option("binding", "--kind", help="Snippet kind: binding|launcher-mode"),
    launcher: str = typer.Option("rofi-mode", "--launcher", help="Launcher surface: rofi-mode|launcher-script|palette-command"),
    install: bool = typer.Option(False, "--install", help="Write helper/script and snippet into conventional XDG locations instead of a self-contained bundle dir"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing bundle files"),
    key: str | None = typer.Option(None, "--key", help="Top-level keybind when --kind=binding"),
    launcher_path: Path | None = typer.Option(None, "--launcher-path", help="Override the helper/script path when using rofi-mode or launcher-script"),
    launcher_id: str | None = typer.Option(None, "--launcher-id", help="Launcher helper basename when a default helper path is implied"),
    mode_name: str | None = typer.Option(None, "--mode-name", help="Rofi mode name for binding bundles or WM mode/submap name for launcher-mode bundles"),
    rofi_mode_name: str | None = typer.Option(None, "--rofi-mode-name", help="Rofi mode name used inside launcher-mode bundles when --launcher=rofi-mode"),
    title: str | None = typer.Option(None, "--title", help="Prompt title inside generated launcher helpers"),
    show_icons: bool = typer.Option(True, "--show-icons/--no-show-icons", help="Include icons in rofi commands where applicable"),
    extra_mode: list[str] = typer.Option([], "--extra-mode", help="Additional rofi modes to include before the VHK mode; may be repeated"),
    command: str = typer.Option("vhk", "--command", help="Executable prefix to use when --launcher=palette-command or inside generated helpers"),
    launcher_backend: str = typer.Option("auto", "--launcher-backend", help="Default backend inside exported generic launcher scripts: auto|rofi|dmenu|wofi|fuzzel|tofi|console"),
    uwsm_app: bool = typer.Option(False, "--uwsm-app", help="For Hyprland, wrap launcher commands with 'uwsm app --'"),
    mode_enter: str | None = typer.Option(None, "--mode-enter", help="Key chord that enters the WM launcher mode / submap when --kind=launcher-mode"),
    mode_one_shot: bool = typer.Option(True, "--mode-one-shot/--mode-sticky", help="Auto-exit the mode/submap after running one action"),
    mode_exit_keys: str = typer.Option("Escape,Return", "--mode-exit-keys", help="Comma-separated keys that leave the mode/submap"),
    launcher_key: str | None = typer.Option("p", "--launcher-key", help="Key inside the mode/submap that opens the selected launcher surface"),
    launcher_action: bool = typer.Option(True, "--launcher-action/--no-launcher-action", help="Include a dedicated launcher action inside the mode/submap"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in exported bundle rows"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include presets as separate exported bundle rows"),
    profile_actions: bool = typer.Option(True, "--profile-actions/--no-profile-actions", help="Include saved prompt profiles as separate exported bundle rows"),
    profile_management_actions: bool = typer.Option(False, "--profile-management-actions/--no-profile-management-actions", help="Include edit/copy/rename/delete prompt-profile rows in exported bundle rows"),
    alpha: bool = typer.Option(False, "--alpha", help="Sort exported launcher rows alphabetically instead of using recent-first ordering"),
    history_limit: int = typer.Option(50, "--history-limit", min=1, help="How many recent runs to scan when ranking exported launcher rows"),
    entry_keys: str = typer.Option("1,2,3,4,5,6,7,8,9,0", "--entry-keys", help="Comma-separated keys assigned to direct palette entries inside launcher-mode bundles"),
    max_entries: int | None = typer.Option(None, "--max-entries", min=0, help="Maximum number of direct palette entries to include (defaults to the number of entry keys)"),
    as_json: bool = typer.Option(False, "--json", help="Print a JSON manifest instead of human-readable output"),
):
    """Export a complete WM integration bundle: launcher helper (if needed) + include/source snippet + bootstrap hint."""

    project = load_project(project_dir)
    if not install and output_dir is None:
        console.print("[red]Need an output directory or --install for export-wm-bundle.[/red]")
        raise typer.Exit(code=1)

    kwargs: dict[str, Any]
    if str(kind).strip().lower() == "launcher-mode":
        if not str(mode_enter or "").strip():
            console.print("[red]--mode-enter is required when --kind=launcher-mode[/red]")
            raise typer.Exit(code=1)
        kwargs = {
            "mode_enter": str(mode_enter),
            "mode_name": mode_name or "vhk-launch",
            "launcher_key": launcher_key,
            "rofi_mode_name": rofi_mode_name,
            "show_icons": show_icons,
            "extra_modes": extra_mode,
            "include_launcher_action": launcher_action,
            "entry_keys": [part.strip() for part in entry_keys.split(",") if part.strip()],
            "max_entries": max_entries,
            "one_shot": mode_one_shot,
            "exit_keys": [part.strip() for part in mode_exit_keys.split(",") if part.strip()],
            "uwsm_app": uwsm_app,
        }
    else:
        kwargs = {
            "key": key,
            "mode_name": mode_name,
            "show_icons": show_icons,
            "extra_modes": extra_mode,
            "uwsm_app": uwsm_app,
        }

    try:
        if as_json and not install:
            manifest = build_wm_bundle_manifest(
                project,
                wm=wm,
                kind=kind,
                launcher=launcher,
                output_dir=output_dir,
                install=install,
                launcher_path=launcher_path,
                launcher_id=launcher_id,
                title=title,
                command=command,
                launcher_backend=launcher_backend,
                include_hidden=include_hidden,
                include_presets=include_presets,
                include_profile_actions=profile_actions,
                include_profile_management_actions=profile_management_actions,
                alpha=alpha,
                history_limit=history_limit,
                **kwargs,
            )
            sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
            return

        manifest = write_wm_bundle(
            project,
            wm=wm,
            kind=kind,
            launcher=launcher,
            output_dir=output_dir,
            install=install,
            force=force,
            launcher_path=launcher_path,
            launcher_id=launcher_id,
            title=title,
            command=command,
            launcher_backend=launcher_backend,
            include_hidden=include_hidden,
            include_presets=include_presets,
            include_profile_actions=profile_actions,
            include_profile_management_actions=profile_management_actions,
            alpha=alpha,
            history_limit=history_limit,
            **kwargs,
        )
    except FileExistsError as exc:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {exc}")
        console.print("Use [bold]--force[/bold] to replace it.")
        raise typer.Exit(code=1)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1)

    if as_json:
        sys.stdout.write(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n")
        return

    if install:
        console.print(f"[green]Installed WM bundle files for {project.name}.[/green]")
    else:
        console.print(f"[green]Wrote WM bundle:[/green] {manifest.root_dir}")
        if manifest.manifest_path:
            console.print(f"[dim]Manifest:[/dim] {manifest.manifest_path}")
        if manifest.bootstrap_path:
            console.print(f"[dim]Bootstrap note:[/dim] {manifest.bootstrap_path}")
    if manifest.helper_path:
        console.print(f"[dim]Launcher helper:[/dim] {manifest.helper_path}")
    console.print(f"[dim]Config snippet:[/dim] {manifest.include_path}")
    console.print(f"[dim]Add this once to {manifest.parent_config_path}:[/dim]")
    console.print(manifest.bootstrap_line)
    console.print(f"[dim]Reload with:[/dim] {manifest.reload_command}")



@app.command()
def export_desktop_entry(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    output: Path | None = typer.Argument(None, help="Output .desktop file path; omit to print to stdout"),
    install: bool = typer.Option(False, "--install", help="Write the desktop entry to XDG_DATA_HOME/applications"),
    force: bool = typer.Option(False, "--force", help="Overwrite an existing output file"),
    desktop_id: str | None = typer.Option(None, "--desktop-id", help="Desktop file id / basename (without .desktop is okay)"),
    name: str | None = typer.Option(None, "--name", help="Display name for the launcher entry"),
    comment: str | None = typer.Option(None, "--comment", help="Comment/tooltip for the launcher entry"),
    icon: str | None = typer.Option("applications-utilities", "--icon", help="Icon name or absolute icon path"),
    command: str = typer.Option("vhk", "--command", help="Executable to place in Exec= lines"),
    include_actions: bool = typer.Option(True, "--actions/--no-actions", help="Include desktop quick actions for macros/presets/profiles"),
    include_hidden: bool = typer.Option(False, "--include-hidden", help="Include hidden macros/presets in exported actions"),
    include_presets: bool = typer.Option(True, "--presets/--no-presets", help="Include presets as separate launcher actions"),
    profile_actions: bool = typer.Option(True, "--profile-actions/--no-profile-actions", help="Include saved prompt profiles as separate launcher actions"),
    alpha: bool = typer.Option(False, "--alpha", help="Sort exported actions alphabetically instead of using recent-first ordering"),
    history_limit: int = typer.Option(50, "--history-limit", min=1, help="How many recent runs to scan when ranking exported actions"),
    max_actions: int = typer.Option(8, "--max-actions", min=0, max=64, help="Maximum number of desktop actions to include"),
):
    """Export a .desktop launcher for this VHK project."""

    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    text = render_desktop_entry(
        project,
        command=command,
        desktop_id=desktop_id,
        entry_name=name,
        comment=comment,
        icon=icon,
        include_actions=include_actions,
        profile_store=store,
        include_hidden=include_hidden,
        include_presets=include_presets,
        include_profile_actions=profile_actions,
        alpha=alpha,
        history_limit=history_limit,
        max_actions=max_actions,
    )

    if install:
        target = default_desktop_install_path(project, desktop_id=desktop_id)
    else:
        target = output

    if target is None:
        sys.stdout.write(text)
        return

    if target.exists() and not force:
        console.print(f"[red]Refusing to overwrite existing file:[/red] {target}")
        console.print("Use [bold]--force[/bold] to replace it.")
        raise typer.Exit(code=1)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    console.print(f"[green]Wrote desktop entry:[/green] {target}")



@app.command()
def list_prompt_profiles(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    as_json: bool = typer.Option(False, "--json", help="Print prompt profile data as JSON"),
    include_values: bool = typer.Option(False, "--values", help="Include saved prompt-profile values and known field definitions"),
):
    """List saved prompt profiles for this project."""

    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    payload = _profile_payload(project, store, include_values=include_values)
    profiles = payload["keys"]
    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return
    if not profiles:
        console.print("(no prompt profiles)")
        raise typer.Exit(code=0)
    table = Table(title="VHK prompt profiles")
    table.add_column("Profile key")
    table.add_column("Names")
    if include_values:
        table.add_column("Saved values")
        exported = payload.get("profiles", {})
        for key, names in profiles.items():
            value_bits = []
            rows = exported.get(key, {}) if isinstance(exported, dict) else {}
            for name in names:
                values = rows.get(name, {}) if isinstance(rows, dict) else {}
                value_bits.append(f"{name}={json.dumps(values, ensure_ascii=False, sort_keys=True)}")
            table.add_row(key, ", ".join(names), "\n".join(value_bits))
    else:
        for key, names in profiles.items():
            table.add_row(key, ", ".join(names))
    console.print(table)


@app.command()
def edit_prompt_profile(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    profile_key: str = typer.Argument(..., help="Prompt profile key"),
    name: str = typer.Argument(..., help="Named profile to edit"),
    values_json: str | None = typer.Option(None, "--values-json", help="Updated values as JSON instead of opening a prompt"),
):
    """Edit one saved named prompt profile."""

    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    if not store.has_profile(profile_key, name):
        console.print(f"[red]Prompt profile not found:[/red] {profile_key} #{name}")
        raise typer.Exit(code=1)
    if not _edit_prompt_profile(project, store, profile_key, name, values_json=values_json):
        raise typer.Exit(code=1)


@app.command()
def copy_prompt_profile(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    profile_key: str = typer.Argument(..., help="Prompt profile key"),
    source_name: str = typer.Argument(..., help="Existing named profile to copy"),
    target_name: str = typer.Argument(..., help="New profile name"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace the destination profile if it exists"),
):
    """Copy one saved named prompt profile."""

    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    try:
        ok = _copy_prompt_profile(project, store, profile_key, source_name, target_name, overwrite=overwrite)
    except Exception as exc:
        console.print(f"[red]Copy failed:[/red] {exc}")
        raise typer.Exit(code=1)
    if not ok:
        raise typer.Exit(code=1)


@app.command()
def rename_prompt_profile(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    profile_key: str = typer.Argument(..., help="Prompt profile key"),
    old_name: str = typer.Argument(..., help="Existing named profile to rename"),
    new_name: str = typer.Argument(..., help="New profile name"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Replace the destination profile if it exists"),
):
    """Rename one saved named prompt profile."""

    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    try:
        ok = _rename_prompt_profile(project, store, profile_key, old_name, new_name, overwrite=overwrite)
    except Exception as exc:
        console.print(f"[red]Rename failed:[/red] {exc}")
        raise typer.Exit(code=1)
    if not ok:
        raise typer.Exit(code=1)


@app.command()
def delete_prompt_profile(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    profile_key: str = typer.Argument(..., help="Prompt profile key"),
    name: str = typer.Argument(..., help="Named profile to delete"),
    yes: bool = typer.Option(False, "--yes", help="Delete without confirmation"),
):
    """Delete one saved named prompt profile."""

    project = load_project(project_dir)
    store = make_prompt_profile_store(project.root_dir, project.settings.prompt_profile_store)
    if not _delete_prompt_profile(project, store, profile_key, name, confirm=not yes):
        raise typer.Exit(code=1)


@app.command()
def list_watchers(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
):
    """List watchers defined in project.yaml."""

    project = load_project(project_dir)

    if not project.clipboard_watchers and not getattr(project, "file_watchers", []) and not project.window_watchers and not getattr(project, "bus_watchers", []):
        console.print("(no watchers)")
        raise typer.Exit(code=0)

    if project.clipboard_watchers:
        table = Table(title="VHK clipboard watchers")
        table.add_column("Name")
        table.add_column("Selection")
        table.add_column("Pattern")
        table.add_column("Macro")
        table.add_column("Enabled")

        for watcher in project.clipboard_watchers:
            table.add_row(
                watcher.name,
                watcher.selection,
                watcher.pattern or "(any)",
                watcher.macro,
                "yes" if watcher.enabled else "no",
            )
        console.print(table)

    if getattr(project, "file_watchers", []):
        table_file = Table(title="VHK file watchers")
        table_file.add_column("Name")
        table_file.add_column("Event")
        table_file.add_column("Directory")
        table_file.add_column("Pattern")
        table_file.add_column("Macro")
        table_file.add_column("Quiet")
        table_file.add_column("Enabled")

        for watcher in project.file_watchers:
            table_file.add_row(
                watcher.name,
                watcher.event,
                watcher.directory,
                watcher.pattern,
                watcher.macro,
                (f"{int(getattr(watcher, 'quiet_ms', 0) or 0)}ms" if int(getattr(watcher, 'quiet_ms', 0) or 0) > 0 else "—"),
                "yes" if watcher.enabled else "no",
            )
        console.print(table_file)

    if getattr(project, "bus_watchers", []):
        table_bus = Table(title="VHK bus watchers")
        table_bus.add_column("Name")
        table_bus.add_column("Event")
        table_bus.add_column("Macro")
        table_bus.add_column("Dispatch")
        table_bus.add_column("Enabled")

        for watcher in project.bus_watchers:
            table_bus.add_row(
                watcher.name,
                watcher.event,
                watcher.macro or "(dispatch)",
                "yes" if watcher.dispatch else "no",
                "yes" if watcher.enabled else "no",
            )
        console.print(table_bus)

    if project.window_watchers:
        table2 = Table(title="VHK window watchers")
        table2.add_column("Name")
        table2.add_column("Event")
        table2.add_column("When")
        table2.add_column("Macro")
        table2.add_column("Enabled")

        for watcher in project.window_watchers:
            when = "(any)"
            if watcher.when is not None:
                when = json.dumps(watcher.when.model_dump(by_alias=True), ensure_ascii=False)
            table2.add_row(
                watcher.name,
                watcher.event,
                when,
                watcher.macro,
                "yes" if watcher.enabled else "no",
            )
        console.print(table2)


def _project_capability_usage(project) -> dict[str, list[dict[str, object]]]:
    usage: dict[str, list[dict[str, object]]] = {
        "screen_capture": [],
        "text_injection": [],
        "pointer_injection": [],
        "global_hotkeys": [],
        "window_introspection": [],
    }

    def record(capability: str, **meta: object) -> None:
        usage.setdefault(capability, []).append(meta)

    if project.bindings:
        record("global_hotkeys", source="bindings", count=len(project.bindings))
        for binding in project.bindings:
            if getattr(binding, "when", None) is not None:
                record("window_introspection", source="binding_when", keys=getattr(binding, "keys", None))

    for hotstring in project.hotstrings:
        if getattr(hotstring, "when", None) is not None:
            record("window_introspection", source="hotstring_when", trigger=getattr(hotstring, "trigger", None))

    for watcher in getattr(project, "bus_watchers", []) or []:
        if getattr(watcher, "when", None) is not None:
            record("window_introspection", source="bus_watcher_when", watcher=getattr(watcher, "name", None))

    for watcher in project.window_watchers:
        record("window_introspection", source="window_watcher", watcher=getattr(watcher, "name", None), event=getattr(watcher, "event", None))

    screen_types = {
        "CaptureScreenshot",
        "ImageSearchFile",
        "ImageSearchAllFile",
        "WaitForImageFile",
        "PixelSearchFile",
        "PixelSearchAllFile",
        "WaitForPixelFile",
        "PixelGetColorFile",
        "OcrReadTextFile",
        "ImageSearch",
        "ImageSearchAll",
        "WaitForImage",
        "WaitForImageAll",
        "WaitForImageVanish",
        "ClickImageAll",
        "PixelSearch",
        "PixelSearchAll",
        "WaitForPixel",
        "WaitForPixelAll",
        "WaitForPixelVanish",
        "ClickPixelAll",
        "PixelGetColor",
        "OcrReadText",
        "OcrNeedleText",
        "WaitForNeedleText",
        "WaitForText",
        "WaitForTextVanish",
        "AssertText",
        "OcrFindTextFile",
        "OcrFindText",
        "OcrFindTextAllFile",
        "OcrFindTextAll",
        "WaitForTextBox",
        "ClickText",
        "ClickTextAll",
        "VisualAssert",
        "VisualVerify",
        "WaitForRegionChange",
        "WaitForRegionStable",
        "ClickNeedle",
    }
    text_types = {"TypeText", "PasteClipboard", "Key", "KeyDown", "KeyUp", "ResetModifiers"}
    pointer_types = {"MouseMove", "MouseClick", "MouseClickAt", "MouseDrag", "MouseWheel", "ClickNeedle", "ClickImageAll", "ClickPixelAll", "ClickText", "ClickTextAll"}
    window_types = {"CoordMode", "WaitForWindowEvent", "WaitForWindow", "WaitForWindowVanish", "FocusWindow", "GetCursorPos", "GetActiveWindow", "GetWindowAtCursor", "GetWindowList"}

    def walk_steps(steps, *, macro_name: str, path_prefix: list[int]) -> None:
        for i, step in enumerate(steps or []):
            step_type = getattr(step, "type", None)
            step_id = ".".join(map(str, path_prefix + [i]))
            if step_type in screen_types:
                record("screen_capture", source="step", macro=macro_name, step_id=step_id, step_type=step_type)
            if step_type in text_types:
                record("text_injection", source="step", macro=macro_name, step_id=step_id, step_type=step_type)
            if step_type in pointer_types or (isinstance(step_type, str) and step_type.startswith("Mouse")):
                record("pointer_injection", source="step", macro=macro_name, step_id=step_id, step_type=step_type)
            if step_type in window_types:
                record("window_introspection", source="step", macro=macro_name, step_id=step_id, step_type=step_type)

            if step_type == "If":
                walk_steps(getattr(step, "then_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])
                walk_steps(getattr(step, "else_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 1])
            elif step_type == "While":
                walk_steps(getattr(step, "steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])
            elif step_type == "Try":
                walk_steps(getattr(step, "steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])
                walk_steps(getattr(step, "catch_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 1])
                walk_steps(getattr(step, "finally_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 2])
            elif step_type == "ForEach":
                walk_steps(getattr(step, "steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])

    for macro_name, macro in project.macros.items():
        walk_steps(macro.steps, macro_name=macro_name, path_prefix=[])

    return usage


def _validation_helper_inventory() -> dict[str, str | None]:
    return {
        "xdotool": shutil.which("xdotool"),
        "xvkbd": shutil.which("xvkbd"),
        "wtype": shutil.which("wtype"),
        "ydotool": shutil.which("ydotool"),
        "dotool": shutil.which("dotool"),
        "dotoolc": shutil.which("dotoolc"),
        "wmctrl": shutil.which("wmctrl"),
        "keyd": shutil.which("keyd"),
        "kanata": shutil.which("kanata"),
        "kmonad": shutil.which("kmonad"),
        "sxhkd": shutil.which("sxhkd"),
        "hyprctl": shutil.which("hyprctl"),
        "espanso": shutil.which("espanso"),
        "xremap": shutil.which("xremap"),
        "busctl": shutil.which("busctl"),
    }


def _validation_session_capability_matrix() -> dict[str, object]:
    helpers = _validation_helper_inventory()
    ss = screenshot_backend()
    screenshot_probe = {
        "backend": ss.name if ss else None,
        "status": "ok" if ss else "backend_missing",
    }
    x11 = probe_x11_extensions()
    i3 = probe_i3_ipc()
    kdotool = probe_kdotool()
    wayland_protocols = probe_wayland_protocols()
    uinput = probe_uinput()
    ydotool_socket = probe_ydotool_socket()
    dotoold = probe_dotoold()
    xdg_portal = probe_xdg_portal_screenshot()
    xdg_portal_screencast = probe_xdg_portal_screencast()
    xdg_portal_global_shortcuts = probe_xdg_portal_global_shortcuts()
    xdg_portal_remote_desktop = probe_xdg_portal_remote_desktop()
    xdg_portal_input_capture = probe_xdg_portal_input_capture()
    xdg_portal_backend_config = probe_xdg_portal_backend_config()
    xdg_portal_backend_manifests = probe_xdg_portal_backend_manifests()
    return build_doctor_capability_matrix(
        desktop_backend=detect_backend(),
        helpers=helpers,
        screenshot=screenshot_probe,
        x11=x11,
        i3=i3,
        kdotool=kdotool,
        wayland_protocols=wayland_protocols,
        uinput=uinput,
        ydotool_socket=ydotool_socket,
        dotoold=dotoold,
        xdg_portal_screenshot=xdg_portal,
        xdg_portal_screencast=xdg_portal_screencast,
        xdg_portal_global_shortcuts=xdg_portal_global_shortcuts,
        xdg_portal_remote_desktop=xdg_portal_remote_desktop,
        xdg_portal_input_capture=xdg_portal_input_capture,
        xdg_portal_backend_config=xdg_portal_backend_config,
        xdg_portal_backend_manifests=xdg_portal_backend_manifests,
    )


def _validation_host_contract_snapshot() -> dict[str, object]:
    return {
        "desktop_backend": detect_backend(),
        "helpers": _validation_helper_inventory(),
        "uinput": probe_uinput(),
        "ydotool_socket": probe_ydotool_socket(),
        "dotoold": probe_dotoold(),
        "wayland_protocols": probe_wayland_protocols(),
        "x11": probe_x11_extensions(),
        "xdg_portal_screenshot": probe_xdg_portal_screenshot(),
        "xdg_portal_screencast": probe_xdg_portal_screencast(),
        "xdg_portal_global_shortcuts": probe_xdg_portal_global_shortcuts(),
        "xdg_portal_remote_desktop": probe_xdg_portal_remote_desktop(),
        "xdg_portal_input_capture": probe_xdg_portal_input_capture(),
        "xdg_portal_backend_config": probe_xdg_portal_backend_config(),
        "xdg_portal_backend_manifests": probe_xdg_portal_backend_manifests(),
    }


def _validation_live_readiness_snapshot(requirements: list[dict[str, object]] | None = None) -> dict[str, object]:
    base_snapshot = _validation_host_contract_snapshot()
    base_snapshot["user_groups"] = probe_current_user_groups()
    base_snapshot["input_event_access"] = probe_input_event_access()
    return collect_live_readiness_snapshot(list(requirements or []), base_snapshot=base_snapshot)


def _iter_session_capability_mismatches(project, capability_matrix: dict[str, object]) -> list[dict[str, object]]:
    usage = _project_capability_usage(project)
    window_contract = summarize_project_window_contract(project)
    issues: list[dict[str, object]] = []
    for capability, refs in usage.items():
        if not refs:
            continue
        item = capability_matrix.get(capability) if isinstance(capability_matrix, dict) else None
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "unknown")
        if status in {"missing", "limited"}:
            examples = []
            for ref in refs[:3]:
                if ref.get("source") == "step":
                    examples.append(f"{ref.get('macro')}:{ref.get('step_id')}:{ref.get('step_type')}")
                elif ref.get("source") == "bindings":
                    examples.append(f"{ref.get('count')} binding(s)")
                elif ref.get("source") == "window_watcher":
                    examples.append(f"window-watcher:{ref.get('watcher')}")
                else:
                    examples.append(str(ref.get("source")))
            summary = (
                f"project relies on session capability '{capability}', but current session reports it as {status}"
                if status == "limited"
                else f"project relies on session capability '{capability}', but current session appears to be missing it"
            )
            recommended = item.get("recommended")
            mechanisms = item.get("mechanisms") or []
            notes = item.get("notes") or []
            suggestion_parts: list[str] = []
            if recommended:
                suggestion_parts.append(f"Prefer {recommended} when authoring/testing this project.")
            elif mechanisms:
                suggestion_parts.append("Available mechanisms: " + ", ".join(str(x) for x in mechanisms[:3]) + ".")
            if notes:
                suggestion_parts.append("Notes: " + "; ".join(str(x) for x in notes[:2]) + ".")
            issues.append(
                {
                    "message": summary,
                    "category": "session_capability",
                    "capability": capability,
                    "session_status": status,
                    "recommended": recommended,
                    "mechanisms": mechanisms,
                    "portal_backends": item.get("portal_backends") or [],
                    "used_by": examples,
                    "notes": notes,
                    "severity": "warning",
                    "code": f"SESSION_CAPABILITY_{status.upper()}",
                    "path": capability,
                    "suggestion": " ".join(suggestion_parts).strip() or None,
                }
            )

    window_item = capability_matrix.get("window_introspection") if isinstance(capability_matrix, dict) else None
    if isinstance(window_item, dict) and window_contract.get("used"):
        support = window_item.get("window_contract_support") if isinstance(window_item.get("window_contract_support"), dict) else {}
        supported_states = set(str(x) for x in (support.get("state_fields") or []) if str(x))
        used_states = set(str(x) for x in (window_contract.get("state_fields_used") or []) if str(x))
        unsupported_states = sorted(used_states - supported_states)
        if unsupported_states:
            pointer = window_contract.get("selector_examples") or []
            issues.append(
                {
                    "message": "project uses window-state selectors that the current session cannot honestly guarantee",
                    "category": "session_window_contract",
                    "capability": "window_introspection",
                    "session_status": str(window_item.get("status") or "unknown"),
                    "severity": "warning",
                    "code": "SESSION_WINDOW_CONTRACT_STATE_FIELDS",
                    "path": "window_introspection.window_contract_support.state_fields",
                    "unsupported_state_fields": unsupported_states,
                    "used_by": [
                        f"{item.get('macro')}:{item.get('path')}"
                        for item in pointer
                        if isinstance(item, dict) and item.get("macro") and item.get("path") and set(item.get("state_fields") or []).intersection(unsupported_states)
                    ][:6],
                    "suggestion": "Limit selectors to fields the backend exposes, or move state-sensitive flows behind compositor-specific helpers/watchers.",
                    "notes": list(support.get("notes") or []),
                }
            )
        if int(window_contract.get("geometry_required_count") or 0) > 0 and not bool(support.get("geometry")):
            issues.append(
                {
                    "message": "project requires window geometry, but the current session does not advertise a reliable geometry path",
                    "category": "session_window_contract",
                    "capability": "window_introspection",
                    "session_status": str(window_item.get("status") or "unknown"),
                    "severity": "warning",
                    "code": "SESSION_WINDOW_CONTRACT_GEOMETRY",
                    "path": "window_introspection.window_contract_support.geometry",
                    "used_by": [f"geometry-required:{int(window_contract.get('geometry_required_count') or 0)}"],
                    "suggestion": "Keep geometry-sensitive logic behind supported WM/compositor helpers or add a fallback path that does not depend on absolute window rectangles.",
                    "notes": list(support.get("notes") or []),
                }
            )
        supported_event_kinds = set(str(x) for x in (support.get("event_kinds") or []) if str(x))
        used_event_kinds = set(str(x) for x in (window_contract.get("event_kinds_used") or []) if str(x))
        unsupported_event_kinds = sorted(used_event_kinds - supported_event_kinds)
        if unsupported_event_kinds:
            issues.append(
                {
                    "message": "project uses WM event waits/hooks that the current session does not advertise",
                    "category": "session_window_contract",
                    "capability": "window_introspection",
                    "session_status": str(window_item.get("status") or "unknown"),
                    "severity": "warning",
                    "code": "SESSION_WINDOW_CONTRACT_EVENT_KINDS",
                    "path": "window_introspection.window_contract_support.event_kinds",
                    "unsupported_event_kinds": unsupported_event_kinds,
                    "used_by": [f"window-events:{kind}" for kind in unsupported_event_kinds],
                    "suggestion": "Keep event-driven waits/watchers to WM event kinds the current backend exposes, or move richer hooks behind compositor-specific helpers/services.",
                    "notes": list(support.get("notes") or []),
                }
            )
        pointer_mode = str(support.get("pointer_window") or "missing")
        if int(window_contract.get("pointer_window_count") or 0) > 0:
            if pointer_mode == "missing":
                issues.append(
                    {
                        "message": "project uses window-under-pointer introspection, but the current session does not advertise that contract",
                        "category": "session_window_contract",
                        "capability": "window_introspection",
                        "session_status": str(window_item.get("status") or "unknown"),
                        "severity": "warning",
                        "code": "SESSION_WINDOW_CONTRACT_POINTER_WINDOW_MISSING",
                        "path": "window_introspection.window_contract_support.pointer_window",
                        "used_by": [f"pointer-window:{int(window_contract.get('pointer_window_count') or 0)}"],
                        "suggestion": "Use focused-window flows or compositor-specific pointer-window helpers instead of assuming a generic under-cursor API.",
                        "notes": list(support.get("notes") or []),
                    }
                )
            elif pointer_mode == "best_effort":
                issues.append(
                    {
                        "message": "project uses window-under-pointer introspection, but the current session only appears to offer best-effort pointer-window matching",
                        "category": "session_window_contract",
                        "capability": "window_introspection",
                        "session_status": str(window_item.get("status") or "unknown"),
                        "severity": "warning",
                        "code": "SESSION_WINDOW_CONTRACT_POINTER_WINDOW_BEST_EFFORT",
                        "path": "window_introspection.window_contract_support.pointer_window",
                        "used_by": [f"pointer-window:{int(window_contract.get('pointer_window_count') or 0)}"],
                        "suggestion": "Treat pointer-window flows as approximate on this backend, or route them through a compositor-specific tool with a direct pointer-window query.",
                        "notes": list(support.get("notes") or []),
                    }
                )
    return issues


def _apply_session_capability_warnings(project, capability_matrix: dict[str, object], add_warning) -> None:
    for issue in _iter_session_capability_mismatches(project, capability_matrix):
        meta = dict(issue)
        message = str(meta.pop("message"))
        add_warning(message, **meta)


@app.command()
def validate(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON report"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Compare project needs against the current session capability matrix"),
):
    """Validate a project folder (macros, references, and expressions).

    This is intentionally a *static* checker: it does not execute side effects.
    """

    from vhk.core.expr import validate_expr

    project = load_project(project_dir)

    errors: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    def add_error(message: str, **meta: object) -> None:
        errors.append({"message": message, **meta})

    def add_warning(message: str, **meta: object) -> None:
        warnings.append({"message": message, **meta})

    # --- cross-object references ----------------------------------------

    for b in project.bindings:
        if b.macro not in project.macros:
            add_error("binding references unknown macro", binding_keys=b.keys, macro=b.macro)

    for hs in project.hotstrings:
        if hs.macro not in project.macros:
            add_error("hotstring references unknown macro", trigger=hs.trigger, macro=hs.macro)

    for w in project.clipboard_watchers:
        if w.macro not in project.macros:
            add_error("clipboard watcher references unknown macro", watcher=w.name, macro=w.macro)

    for w in getattr(project, "file_watchers", []) or []:
        if w.macro not in project.macros:
            add_error("file watcher references unknown macro", watcher=w.name, macro=w.macro)

    for w in project.window_watchers:
        if w.macro not in project.macros:
            add_error("window watcher references unknown macro", watcher=w.name, macro=w.macro)

    # --- macro validation ----------------------------------------------

    def walk_steps(steps, *, macro_name: str, path_prefix: list[int]) -> None:
        for i, step in enumerate(steps or []):
            step_id = ".".join(map(str, path_prefix + [i]))

            # Validate CallMacro targets.
            if getattr(step, "type", None) == "CallMacro":
                target = getattr(step, "macro", None)
                if isinstance(target, str) and target not in project.macros:
                    add_error("CallMacro references unknown macro", macro=macro_name, step_id=step_id, target=target)

            # Validate expression fields.
            for fname in getattr(type(step), "model_fields", {}).keys():
                if fname == "condition" or fname.endswith("_expr") or fname == "value_expr":
                    val = getattr(step, fname, None)
                    if isinstance(val, str) and val.strip():
                        try:
                            validate_expr(val)
                        except Exception as exc:
                            add_error(
                                "invalid expression",
                                macro=macro_name,
                                step_id=step_id,
                                field=fname,
                                expr=val,
                                error=str(exc),
                            )

            # Disabled steps are commonly used as authoring scaffolds/TODOs.
            # We keep validation conservative by skipping *static* asset existence
            # checks for disabled steps so placeholder needles/baselines don't
            # block project validation.
            is_enabled = bool(getattr(step, "enabled", True))

            # Validate required asset paths (static).
            # We intentionally keep this conservative: only *visual assets* that
            # are expected to exist at authoring time (needles/baselines).
            # Dynamic paths using interpolation cannot be validated statically.
            asset_fields = ("needle_path", "baseline_path") if is_enabled else tuple()
            for af in asset_fields:
                if not hasattr(step, af):
                    continue
                val = getattr(step, af, None)
                if val is None:
                    continue
                if not isinstance(val, str):
                    continue
                if not val.strip():
                    continue
                if "${" in val:
                    add_warning(
                        "asset path is dynamic; cannot validate existence statically",
                        macro=macro_name,
                        step_id=step_id,
                        field=af,
                        path=val,
                    )
                    continue

                p = Path(val).expanduser()
                if not p.is_absolute():
                    p = Path(project.root_dir) / p
                if not p.exists():
                    add_error(
                        "missing required asset file",
                        macro=macro_name,
                        step_id=step_id,
                        field=af,
                        path=val,
                        resolved=str(p),
                    )
                    continue

                # If a sidecar metadata JSON exists, warn when invalid.
                meta = p.with_suffix('.json')
                if meta.exists():
                    try:
                        json.loads(meta.read_text())
                    except Exception as exc:
                        add_warning(
                            "invalid asset metadata json",
                            macro=macro_name,
                            step_id=step_id,
                            field=f"{af}.meta",
                            path=str(meta),
                            error=str(exc),
                        )

            # Recurse into common control-flow containers.
            if getattr(step, "type", None) == "If":
                walk_steps(getattr(step, "then_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])
                walk_steps(getattr(step, "else_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 1])
            elif getattr(step, "type", None) == "While":
                walk_steps(getattr(step, "steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])
            elif getattr(step, "type", None) == "Try":
                walk_steps(getattr(step, "steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])
                walk_steps(getattr(step, "catch_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 1])
                walk_steps(getattr(step, "finally_steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 2])
            elif getattr(step, "type", None) == "ForEach":
                walk_steps(getattr(step, "steps", []), macro_name=macro_name, path_prefix=path_prefix + [i, 0])

    for macro_name, macro in project.macros.items():
        walk_steps(macro.steps, macro_name=macro_name, path_prefix=[])

    session_capabilities: dict[str, object] | None = None
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            _apply_session_capability_warnings(project, session_capabilities, add_warning)
        except Exception as exc:
            add_warning("session capability check failed", category="session_capability", error=str(exc))

    ok = len(errors) == 0
    payload = {
        "ok": ok,
        "project": project.name,
        "macro_count": len(project.macros),
        "errors": errors,
        "warnings": warnings,
        "session_capabilities": session_capabilities,
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        if ok:
            if warnings:
                console.print(f"[yellow]OK[/yellow] project validated with {len(warnings)} warning(s)")
                for w in warnings[:20]:
                    console.print(f"- {w.get('message')} ({w})")
                if len(warnings) > 20:
                    console.print(f"... ({len(warnings) - 20} more warning(s))")
            else:
                console.print("[green]OK[/green] project validated")
        else:
            console.print(f"[red]FAILED[/red] {len(errors)} error(s) found")
            for e in errors[:20]:
                console.print(f"- {e.get('message')} ({e})")
            if len(errors) > 20:
                console.print(f"... ({len(errors) - 20} more)")
            if warnings:
                console.print(f"[yellow]Warnings[/yellow] {len(warnings)}")
                for w in warnings[:20]:
                    console.print(f"- {w.get('message')} ({w})")

    raise typer.Exit(code=0 if ok else 1)


@app.command(name="init")
def init_project_cmd(
    project_dir: Path = typer.Argument(..., help="Project directory to create (will be created if missing)"),
    name: str | None = typer.Option(None, "--name", help="Project name (defaults to folder name)"),
    template: str = typer.Option("minimal", "--template", help="minimal|demo|vision"),
    schemas: bool = typer.Option(True, "--schemas/--no-schemas", help="Write JSON schemas + editor hints"),
    vscode: bool = typer.Option(True, "--vscode/--no-vscode", help="Write .vscode/settings.json yaml.schemas mappings"),
    starter_guide: bool = typer.Option(True, "--starter-guide/--no-starter-guide", help="Write docs/VHK_STARTER_GUIDE.md from planner heuristics"),
    starter_plan_json: bool = typer.Option(True, "--starter-plan-json/--no-starter-plan-json", help="Write docs/VHK_STARTER_PLAN.json from planner heuristics"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing files inside the folder"),
):
    """Initialize a new VHK project folder.

    Creates:
    - project.yaml
    - macros/main.yaml
    - assets/ (with a tiny assets/TODO.png placeholder)
    """

    template_norm = template.strip().lower()
    if template_norm not in {"minimal", "demo", "vision"}:
        raise typer.BadParameter("--template must be one of: minimal, demo, vision")

    try:
        res = init_project_fs(
            project_dir,
            name=name,
            template=template_norm,  # type: ignore[arg-type]
            with_schemas=schemas,
            with_vscode_settings=vscode,
            with_starter_guide=starter_guide,
            with_starter_plan_json=starter_plan_json,
            force=force,
        )
    except Exception as exc:
        raise typer.BadParameter(str(exc))

    console.print(f"Initialized project: [bold]{res.project_dir}[/bold]")
    if res.created_dirs:
        console.print(f"Created dirs: {len(res.created_dirs)}")
    console.print(f"Created files: {len(res.created_files)}")
    if res.starter_guide_path:
        console.print(f"Starter guide: [bold]{res.starter_guide_path}[/bold]")
    if res.starter_plan_path:
        console.print(f"Starter plan: [bold]{res.starter_plan_path}[/bold]")


@app.command(name="new-macro")
def new_macro_cmd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    macro_name: str = typer.Argument(..., help="Macro name (and filename stem under macros/)"),
    template: str = typer.Option("minimal", "--template", help="minimal|demo|vision"),
    register: bool = typer.Option(True, "--register/--no-register", help="Add entry to project.yaml macros mapping"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing macro file"),
):
    """Create a new macro YAML file inside a project."""

    template_norm = template.strip().lower()
    if template_norm not in {"minimal", "demo", "vision"}:
        raise typer.BadParameter("--template must be one of: minimal, demo, vision")

    try:
        p = add_macro_fs(project_dir, macro_name=macro_name, template=template_norm, register=register, force=force)  # type: ignore[arg-type]
    except Exception as exc:
        raise typer.BadParameter(str(exc))

    console.print(f"Wrote macro: [bold]{p}[/bold]")
    if register:
        console.print("Updated project.yaml macros mapping")


@app.command()
def schema(
    kind: str = typer.Option("macro", "--kind", help="project|macro|step|selector|region"),
    draft: str = typer.Option("7", "--draft", help="7|pydantic"),
    fmt: str = typer.Option("json", "--format", help="json|yaml"),
    out: Path | None = typer.Option(None, "--out", help="Write schema to this file (otherwise stdout)"),
):
    """Print a JSON schema for VHK YAML files.

    This is mainly used for editor autocompletion/validation (VS Code YAML,
    yaml-language-server).
    """

    kind_norm = kind.strip().lower()
    if kind_norm not in {"project", "macro", "step", "selector", "region"}:
        raise typer.BadParameter("--kind must be one of: project, macro, step, selector, region")

    draft_norm = draft.strip().lower()
    if draft_norm not in {"7", "pydantic"}:
        raise typer.BadParameter("--draft must be one of: 7, pydantic")

    fmt_norm = fmt.strip().lower()
    if fmt_norm not in {"json", "yaml"}:
        raise typer.BadParameter("--format must be one of: json, yaml")

    payload = generate_schema(kind_norm, draft=draft_norm)  # type: ignore[arg-type]
    if fmt_norm == "yaml":
        text = yaml.safe_dump(payload, sort_keys=False)
    else:
        text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    if out is not None:
        out = out.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    else:
        sys.stdout.write(text)


def _ensure_modeline(path: Path, modeline: str) -> bool:
    """Ensure the first line of the YAML file contains the schema modeline."""

    desired = f"# yaml-language-server: $schema={modeline}\n"
    raw = path.read_text() if path.exists() else ""
    lines = raw.splitlines(keepends=True)
    if lines and lines[0].startswith("# yaml-language-server: $schema="):
        if lines[0] == desired:
            return False
        lines[0] = desired
    else:
        lines.insert(0, desired)
    path.write_text("".join(lines))
    return True


@app.command(name="schemas")
def schemas_cmd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing schema/settings files"),
    vscode: bool = typer.Option(True, "--vscode/--no-vscode", help="Write .vscode/settings.json yaml.schemas mappings"),
    patch_modelines: bool = typer.Option(False, "--patch-modelines", help="Insert/replace $schema modelines in project.yaml and macros"),
):
    """Write JSON schema files into `<project>/schemas/`.

    Useful for editor autocompletion/validation in YAML files.
    """

    created = write_default_schemas(project_dir, force=force, with_vscode_settings=vscode)
    console.print(f"Wrote schemas/settings: {len(created)} file(s)")

    if patch_modelines:
        changed = 0
        proj_yaml = project_dir / "project.yaml"
        if proj_yaml.exists():
            if _ensure_modeline(proj_yaml, "schemas/vhk_project.schema.json"):
                changed += 1
        macros_dir = project_dir / "macros"
        if macros_dir.exists():
            schema_path = project_dir / "schemas" / "vhk_macro.schema.json"
            for p in sorted(macros_dir.glob("*.yaml")):
                rel = os.path.relpath(schema_path, start=p.parent)
                rel = rel.replace(os.sep, "/")
                if _ensure_modeline(p, rel):
                    changed += 1
        console.print(f"Patched modelines: {changed} file(s)")


def _iter_macro_route_issues(
    project,
    *,
    capability_usage: dict[str, object] | None = None,
    capability_matrix: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
    )

    def add(
        *,
        severity: str,
        code: str,
        path: str,
        message: str,
        suggestion: str | None = None,
        **extra: object,
    ) -> None:
        issues.append(
            {
                'severity': severity,
                'code': code,
                'path': path,
                'message': message,
                'suggestion': suggestion,
                'category': 'macro_route',
                **extra,
            }
        )

    for item in strategy.get('macro_export_candidates') or []:
        if not isinstance(item, dict):
            continue
        macro = str(item.get('macro') or '').strip()
        route_id = str(item.get('route_id') or '').strip()
        export_surface_id = str(item.get('export_surface_id') or '').strip()
        fit = str(item.get('fit') or 'good').strip() or 'good'
        tools = [str(x) for x in (item.get('tool_family') or []) if str(x)]
        commands = [str(x) for x in (item.get('commands') or []) if str(x)]
        risks = [str(x) for x in (item.get('risks') or []) if str(x)]
        evidence = [str(x) for x in (item.get('evidence') or []) if str(x)]
        activation_route_id = str(item.get('primary_activation_route_id') or '').strip() or None
        suggestion = '; '.join(commands[:2]) if commands else None

        if export_surface_id == 'remapper-export':
            add(
                severity='info',
                code='ROUTE_DRIFT_REMAPPER_TIER',
                path=f'route:{macro}',
                message=(
                    f'`{macro}` looks more like a remapper-tier macro than a full runner-owned workflow.'
                ),
                suggestion=(
                    suggestion
                    or 'Generate keyd/xremap exports and keep the VHK runner for richer fallback behavior.'
                ),
                macro_name=macro,
                route_id=route_id,
                export_surface_id=export_surface_id,
                fit=fit,
                activation_route_id=activation_route_id,
                tools=tools,
                evidence=evidence,
                risks=risks,
            )
        elif export_surface_id == 'text-package-export':
            add(
                severity='info',
                code='ROUTE_DRIFT_TEXT_TIER',
                path=f'route:{macro}',
                message=(
                    f'`{macro}` looks like a text-tier snippet that should probably ship through a phrase/package lane before falling back to the full runner.'
                ),
                suggestion=(
                    suggestion
                    or 'Generate an Espanso-style package and optimize long text toward clipboard or hybrid text lanes.'
                ),
                macro_name=macro,
                route_id=route_id,
                export_surface_id=export_surface_id,
                fit=fit,
                activation_route_id=activation_route_id,
                tools=tools,
                evidence=evidence,
                risks=risks,
            )
        elif export_surface_id == 'watcher-service-export':
            add(
                severity='info',
                code='ROUTE_DRIFT_WATCHER_SERVICE',
                path=f'route:{macro}',
                message=(
                    f'`{macro}` is event-driven enough that it fits a watcher/service lane better than a direct trigger-owned macro.'
                ),
                suggestion=(
                    suggestion
                    or 'Generate watcher/systemd artifacts so the service boundary is explicit and the runner only handles the macro body.'
                ),
                macro_name=macro,
                route_id=route_id,
                export_surface_id=export_surface_id,
                fit=fit,
                activation_route_id=activation_route_id,
                tools=tools,
                evidence=evidence,
                risks=risks,
            )
        elif export_surface_id == 'helper-route-dossier':
            add(
                severity='warning' if fit in {'conditional', 'weak'} else 'info',
                code='ROUTE_DRIFT_HELPER_BOUNDARY',
                path=f'route:{macro}',
                message=(
                    f'`{macro}` crosses helper-sensitive capture/input boundaries and should keep those seams explicit instead of pretending they are generic Linux guarantees.'
                ),
                suggestion=(
                    suggestion
                    or 'Run capability/target-route packs and keep pointer/capture helpers as named host contracts.'
                ),
                macro_name=macro,
                route_id=route_id,
                export_surface_id=export_surface_id,
                fit=fit,
                activation_route_id=activation_route_id,
                tools=tools,
                evidence=evidence,
                risks=risks,
            )

    return issues


def _iter_promotion_gate_issues(
    project,
    *,
    capability_usage: dict[str, object] | None = None,
    capability_matrix: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
    )

    for item in strategy.get('promotion_gates') or []:
        if not isinstance(item, dict):
            continue
        status = str(item.get('status') or 'review').strip().lower() or 'review'
        gate_id = str(item.get('gate_id') or '').strip()
        if not gate_id or status == 'pass':
            continue
        issues.append(
            {
                'severity': 'warning' if status == 'fail' else 'info',
                'code': 'PROMOTION_GATE_FAIL' if status == 'fail' else 'PROMOTION_GATE_REVIEW',
                'path': f'promotion-gate:{gate_id}',
                'message': str(item.get('summary') or f'Promotion gate {gate_id} needs attention.'),
                'suggestion': '; '.join(str(x) for x in list(item.get('commands') or [])[:2]) or 'Run vhk plan-project and review promotion surfaces.',
                'category': 'promotion_gate',
                'gate_id': gate_id,
                'title': str(item.get('title') or gate_id),
                'status': status,
                'affected_surfaces': [str(x) for x in list(item.get('affected_surfaces') or []) if str(x)],
                'blocking_surfaces': [str(x) for x in list(item.get('blocking_surfaces') or []) if str(x)],
                'review_surfaces': [str(x) for x in list(item.get('review_surfaces') or []) if str(x)],
                'wave_ids': [str(x) for x in list(item.get('wave_ids') or []) if str(x)],
            }
        )

    return issues


def _iter_promotion_evidence_issues(
    project,
    *,
    capability_usage: dict[str, object] | None = None,
    capability_matrix: dict[str, object] | None = None,
) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    strategy = summarize_project_strategy(
        project,
        capability_usage=capability_usage or {},
        capability_matrix=capability_matrix,
    )

    for item in strategy.get('promotion_evidence') or []:
        if not isinstance(item, dict):
            continue
        status = str(item.get('evidence_status') or 'partial').strip().lower() or 'partial'
        if status == 'complete':
            continue
        evidence_id = str(item.get('evidence_id') or '').strip()
        if not evidence_id:
            continue
        missing_artifacts = [str(x) for x in list(item.get('missing_artifacts') or []) if str(x)]
        code = 'PROMOTION_EVIDENCE_MISSING' if status == 'missing' else 'PROMOTION_EVIDENCE_PARTIAL'
        message = (
            f"Promotion evidence for `{evidence_id}` is still missing supporting artifacts."
            if status == 'missing'
            else f"Promotion evidence for `{evidence_id}` is only partially present; keep the Linux-native posture reviewable."
        )
        issues.append(
            {
                'severity': 'warning' if status == 'missing' else 'info',
                'code': code,
                'path': f'promotion-evidence:{evidence_id}',
                'message': message,
                'suggestion': '; '.join(str(x) for x in list(item.get('commands') or [])[:2]) or 'Generate the missing proof artifacts before treating this surface/gate as release-proof.',
                'category': 'promotion_evidence',
                'evidence_id': evidence_id,
                'subject_kind': str(item.get('subject_kind') or 'surface'),
                'subject_id': str(item.get('subject_id') or ''),
                'evidence_status': status,
                'posture': str(item.get('posture') or 'review'),
                'required_artifacts': [str(x) for x in list(item.get('required_artifacts') or []) if str(x)],
                'present_artifacts': [str(x) for x in list(item.get('present_artifacts') or []) if str(x)],
                'missing_artifacts': missing_artifacts,
            }
        )

    return issues


@app.command()
def lint(
    macro_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Macro YAML file to lint"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable JSON"),
    check: bool = typer.Option(False, "--check", help="Exit non-zero if issues at/above --fail-on are found"),
    fail_on: str = typer.Option("warning", "--fail-on", help="info|warning|error"),
    warn_long_delay_ms: int = typer.Option(1500, "--warn-long-delay-ms", min=0, help="Warn when Delay >= this"),
    warn_delay_before_action_ms: int = typer.Option(600, "--warn-delay-before-action-ms", min=0, help="Info when Delay before action >= this"),
    warn_low_poll_ms: int = typer.Option(75, "--warn-low-poll-ms", min=1, help="Info when poll_ms < this"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress summary output"),
):
    """Lint a macro YAML file and suggest more robust patterns.

    Philosophy: help authors move from raw recordings (fixed sleeps + absolute
    coordinates) toward condition-based waits and stable selectors.
    """

    raw = macro_path.read_text()
    payload = yaml.safe_load(raw)
    if not isinstance(payload, dict) or "steps" not in payload:
        raise typer.BadParameter("Macro YAML must be a mapping containing a 'steps:' list.")
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise typer.BadParameter("'steps' must be a list.")

    issues = lint_steps(
        steps,
        warn_long_delay_ms=warn_long_delay_ms,
        warn_delay_before_action_ms=warn_delay_before_action_ms,
        warn_low_poll_ms=warn_low_poll_ms,
    )

    if as_json:
        sys.stdout.write(
            json.dumps(
                {
                    "macro": str(macro_path),
                    "issue_count": len(issues),
                    "issues": [i.__dict__ for i in issues],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
    else:
        table = Table(title=f"Lint: {macro_path.name}")
        table.add_column("severity", style="bold")
        table.add_column("code")
        table.add_column("path")
        table.add_column("message")
        table.add_column("suggestion")

        for i in sorted(issues, key=lambda x: (_SEV_ORDER.get(x.severity, 99), x.code, x.path)):
            table.add_row(i.severity, i.code, i.path, i.message, i.suggestion or "")
        console.print(table)
        if not quiet:
            console_err.print(f"[dim]# issues: {len(issues)}[/dim]")

    if check:
        threshold = _SEV_ORDER.get(fail_on.strip().lower(), 2)
        worst = max((_SEV_ORDER.get(i.severity, 0) for i in issues), default=0)
        raise typer.Exit(code=1 if worst >= threshold else 0)


@app.command(name="lint-project")
def lint_project(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project folder containing macros/"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable JSON"),
    check: bool = typer.Option(False, "--check", help="Exit non-zero if issues at/above --fail-on are found"),
    fail_on: str = typer.Option("warning", "--fail-on", help="info|warning|error"),
    warn_long_delay_ms: int = typer.Option(1500, "--warn-long-delay-ms", min=0, help="Warn when Delay >= this"),
    warn_delay_before_action_ms: int = typer.Option(600, "--warn-delay-before-action-ms", min=0, help="Info when Delay before action >= this"),
    warn_low_poll_ms: int = typer.Option(75, "--warn-low-poll-ms", min=1, help="Info when poll_ms < this"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Compare project needs against the current session capability matrix"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress per-file output"),
):
    """Lint every macro in a project (bulk advisor)."""

    project_dir = project_dir.resolve()
    # Best-effort project validation (ensures macros parse and paths exist).
    try:
        project = load_project(project_dir)
    except Exception as exc:
        raise typer.BadParameter(f"Invalid project: {exc}")

    macros_dir = project_dir / "macros"
    if not macros_dir.exists():
        raise typer.BadParameter("Project has no macros/ directory.")

    macro_files = sorted(list(macros_dir.glob("*.yaml")) + list(macros_dir.glob("*.yml")))
    if not macro_files:
        raise typer.BadParameter("No macro YAML files found under macros/.")

    all_issues: list[dict[str, object]] = []
    worst = 0
    session_capabilities: dict[str, object] | None = None
    capability_usage = _project_capability_usage(project)

    for mp in macro_files:
        raw = mp.read_text()
        payload = yaml.safe_load(raw)
        if not isinstance(payload, dict) or "steps" not in payload or not isinstance(payload.get("steps"), list):
            if not quiet and (not as_json):
                console_err.print(f"[yellow]Skipping[/yellow] {mp}: not a macro mapping with 'steps:' list")
            continue
        issues = lint_steps(
            payload.get("steps") or [],
            warn_long_delay_ms=warn_long_delay_ms,
            warn_delay_before_action_ms=warn_delay_before_action_ms,
            warn_low_poll_ms=warn_low_poll_ms,
        )
        for i in issues:
            worst = max(worst, _SEV_ORDER.get(i.severity, 0))
            all_issues.append({"macro": str(mp.relative_to(project_dir)), **i.__dict__})

        if not quiet and (not as_json) and issues:
            console_err.print(f"[dim]{mp.relative_to(project_dir)}[/dim] — {len(issues)} issues")

    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            for issue in _iter_session_capability_mismatches(project, session_capabilities):
                worst = max(worst, _SEV_ORDER.get(str(issue.get("severity")), 0))
                all_issues.append({"macro": "<project>", **issue})
        except Exception as exc:
            all_issues.append(
                {
                    "macro": "<project>",
                    "severity": "info",
                    "code": "SESSION_CAPABILITY_CHECK_FAILED",
                    "path": "session",
                    "message": "session capability check failed",
                    "suggestion": None,
                    "category": "session_capability",
                    "error": str(exc),
                }
            )
            worst = max(worst, _SEV_ORDER.get("info", 0))

    for issue in _iter_voice_export_collisions(project):
        worst = max(worst, _SEV_ORDER.get(str(issue.get("severity")), 0))
        all_issues.append({"macro": "<project>", **issue})

    for issue in _iter_voice_phrase_quality_issues(project):
        worst = max(worst, _SEV_ORDER.get(str(issue.get("severity")), 0))
        all_issues.append({"macro": "<project>", **issue})

    for issue in _iter_export_honesty_issues(project):
        worst = max(worst, _SEV_ORDER.get(str(issue.get("severity")), 0))
        all_issues.append({"macro": "<project>", **issue})

    for issue in _iter_macro_route_issues(
        project,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
    ):
        worst = max(worst, _SEV_ORDER.get(str(issue.get("severity")), 0))
        all_issues.append({"macro": "<project>", **issue})

    for issue in _iter_promotion_gate_issues(
        project,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
    ):
        worst = max(worst, _SEV_ORDER.get(str(issue.get("severity")), 0))
        all_issues.append({"macro": "<project>", **issue})

    for issue in _iter_promotion_evidence_issues(
        project,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
    ):
        worst = max(worst, _SEV_ORDER.get(str(issue.get("severity")), 0))
        all_issues.append({"macro": "<project>", **issue})

    if as_json:
        sys.stdout.write(
            json.dumps(
                {
                    "project": str(project_dir),
                    "macro_count": len(macro_files),
                    "issue_count": len(all_issues),
                    "issues": all_issues,
                    "session_capabilities": session_capabilities,
                    "capability_usage": capability_usage,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
    else:
        table = Table(title=f"Lint project: {project_dir.name}")
        table.add_column("macro")
        table.add_column("severity", style="bold")
        table.add_column("code")
        table.add_column("path")
        table.add_column("message")
        table.add_column("suggestion")
        for i in sorted(
            all_issues,
            key=lambda x: (
                _SEV_ORDER.get(str(x.get("severity")), 99),
                str(x.get("code")),
                str(x.get("macro")),
                str(x.get("path")),
            ),
        ):
            table.add_row(
                str(i.get("macro")),
                str(i.get("severity")),
                str(i.get("code")),
                str(i.get("path")),
                str(i.get("message")),
                str(i.get("suggestion") or ""),
            )
        console.print(table)
        if not quiet:
            console_err.print(f"[dim]# issues: {len(all_issues)}[/dim]")

    if check:
        threshold = _SEV_ORDER.get(fail_on.strip().lower(), 2)
        raise typer.Exit(code=1 if worst >= threshold else 0)


@app.command(name="plan-project")
def plan_project(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable analysis"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    macro_limit: int = typer.Option(20, "--macro-limit", min=1, help="How many macro profiles to print in the table view"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
):
    """Analyze a VHK project and recommend a Linux-native integration strategy."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    payload = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        evidence_lane_profile=evidence_lane,
    )

    host_snapshot = None
    if session_check:
        requirements = [dict(item) for item in list(payload.get("host_requirements") or []) if isinstance(item, dict)]
        try:
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception:
            host_snapshot = None

    claim_plan = build_claim_plan(
        project_dir.resolve(),
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane,
    )
    host_truth = dict(claim_plan.get("host_truth") or {})
    portal_route_contract = dict(claim_plan.get("portal_route_contract") or {})

    payload = summarize_project_strategy(
        project,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_truth=host_truth,
        portal_route_contract=portal_route_contract,
        evidence_lane_profile=evidence_lane,
    )

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return

    overview = payload.get("overview") or {}
    project_meta = payload.get("project") or {}
    project_tags = list(payload.get("project_tags") or [])

    tbl = Table(title="VHK plan-project")
    tbl.add_column("Field", no_wrap=True)
    tbl.add_column("Value", overflow="fold")
    tbl.add_row("Project", str(project_meta.get("name") or "(unknown)"))
    tbl.add_row("Path", str(project_meta.get("root_dir") or project_dir))
    tbl.add_row("Desktop backend", str(project_meta.get("desktop_backend") or "(unknown)"))
    tbl.add_row("Macros", str(overview.get("macros") or 0))
    tbl.add_row("Bindings", str(overview.get("bindings") or 0))
    tbl.add_row("Hotstrings", str(overview.get("hotstrings") or 0))
    tbl.add_row("Clipboard watchers", str(overview.get("clipboard_watchers") or 0))
    tbl.add_row("File watchers", str(overview.get("file_watchers") or 0))
    tbl.add_row("Bus watchers", str(overview.get("bus_watchers") or 0))
    tbl.add_row("Window watchers", str(overview.get("window_watchers") or 0))
    tbl.add_row("Presets", str(overview.get("presets") or 0))
    tbl.add_row("Project tags", ", ".join(project_tags) if project_tags else "(none)")
    console.print(tbl)

    macros = list(payload.get("macro_profiles") or [])[: int(macro_limit)]
    if macros:
        mt = Table(title=f"Macro profiles (top {len(macros)})")
        mt.add_column("Macro", no_wrap=True)
        mt.add_column("Triggers", overflow="fold")
        mt.add_column("Tags", overflow="fold")
        mt.add_column("Steps", justify="right")
        mt.add_column("Notes", overflow="fold")
        for item in macros:
            smells = item.get("smells") or {}
            notes: list[str] = []
            if smells.get("long_delay"):
                notes.append(f"{smells.get('long_delay')} long delay")
            if smells.get("coord_click"):
                notes.append(f"{smells.get('coord_click')} coord click")
            if smells.get("raw_key_events"):
                notes.append(f"{smells.get('raw_key_events')} raw key")
            mt.add_row(
                str(item.get("macro")),
                ", ".join(item.get("triggers") or []) or "(none)",
                ", ".join(item.get("tags") or []) or "(none)",
                str(item.get("step_count") or 0),
                "; ".join(notes) if notes else "",
            )
        console.print("\n")
        console.print(mt)

    macro_routes = list(payload.get("macro_route_profiles") or [])[: int(macro_limit)]
    if macro_routes:
        mrt = Table(title=f"Macro route ownership (top {len(macro_routes)})")
        mrt.add_column("Macro", no_wrap=True)
        mrt.add_column("Route", overflow="fold", min_width=18)
        mrt.add_column("Fit", no_wrap=True)
        mrt.add_column("Activation", no_wrap=True)
        mrt.add_column("Surface", overflow="fold")
        for item in macro_routes:
            mrt.add_row(
                str(item.get("macro") or ""),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                str(item.get("primary_activation_route_id") or ""),
                str(item.get("execution_surface") or ""),
            )
        console.print("\n")
        console.print(mrt)

    export_candidates = list(payload.get("macro_export_candidates") or [])[: int(macro_limit)]
    if export_candidates:
        met = Table(title=f"Macro export candidates (top {len(export_candidates)})")
        met.add_column("Macro", no_wrap=True)
        met.add_column("Candidate", overflow="fold", min_width=18)
        met.add_column("Fit", no_wrap=True)
        met.add_column("Tools", overflow="fold")
        met.add_column("Activation", no_wrap=True)
        for item in export_candidates:
            met.add_row(
                str(item.get("macro") or ""),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                ", ".join(str(x) for x in (item.get("tool_family") or [])[:3]) or "(none)",
                str(item.get("primary_activation_route_id") or ""),
            )
        console.print("\n")
        console.print(met)

    route_portfolio = list(payload.get("route_portfolio") or [])
    if route_portfolio:
        rpt = Table(title="Route portfolio")
        rpt.add_column("Route", overflow="fold", min_width=18)
        rpt.add_column("Macros", justify="right", no_wrap=True)
        rpt.add_column("Fit", no_wrap=True)
        rpt.add_column("Activation", overflow="fold")
        rpt.add_column("Examples", overflow="fold")
        for item in route_portfolio[:8]:
            rpt.add_row(
                str(item.get("title") or ""),
                str(item.get("macro_count") or 0),
                str(item.get("dominant_fit") or "").upper(),
                ", ".join(str(x) for x in (item.get("top_activation_routes") or [])[:3]) or "(none)",
                ", ".join(str(x) for x in (item.get("example_macros") or [])[:4]) or "(none)",
            )
        console.print("\n")
        console.print(rpt)

    promotion_plan = list(payload.get("export_promotion_plan") or [])
    if promotion_plan:
        ppt = Table(title="Export promotion plan")
        ppt.add_column("Priority", no_wrap=True)
        ppt.add_column("Surface", overflow="fold", min_width=18)
        ppt.add_column("Macros", justify="right", no_wrap=True)
        ppt.add_column("Tools", overflow="fold")
        ppt.add_column("Commands", overflow="fold")
        for item in promotion_plan[:8]:
            ppt.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("macro_count") or 0),
                ", ".join(str(x) for x in (item.get("tool_family") or [])[:4]) or "(none)",
                "; ".join(str(x) for x in (item.get("commands") or [])[:2]) or "(none)",
            )
        console.print("\n")
        console.print(ppt)

    promotion_waves = list(payload.get("promotion_waves") or [])
    if promotion_waves:
        pwt = Table(title="Promotion waves")
        pwt.add_column("Wave", overflow="fold", min_width=18)
        pwt.add_column("Priority", no_wrap=True)
        pwt.add_column("Surfaces", justify="right", no_wrap=True)
        pwt.add_column("Macros", justify="right", no_wrap=True)
        pwt.add_column("Routes", overflow="fold")
        for item in promotion_waves[:6]:
            pwt.add_row(
                str(item.get("title") or item.get("wave_id") or ""),
                str(item.get("priority") or "medium").upper(),
                str(item.get("surface_count") or 0),
                str(item.get("macro_count") or 0),
                ", ".join(str(x) for x in (item.get("route_ids") or [])[:4]) or "(none)",
            )
        console.print("\n")
        console.print(pwt)

    promotion_readiness = list(payload.get("promotion_readiness") or [])
    if promotion_readiness:
        prt = Table(title="Promotion readiness")
        prt.add_column("Status", no_wrap=True)
        prt.add_column("Surface", overflow="fold", min_width=18)
        prt.add_column("Priority", no_wrap=True)
        prt.add_column("Blockers", justify="right", no_wrap=True)
        prt.add_column("Required caps", overflow="fold")
        prt.add_column("Next action", overflow="fold")
        for item in promotion_readiness[:8]:
            prt.add_row(
                str(item.get("readiness_status") or "review").upper(),
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("priority") or "medium").upper(),
                str(item.get("blocker_count") or 0),
                ", ".join(str(x) for x in (item.get("required_capabilities") or [])[:4]) or "(none)",
                str(item.get("next_action") or ""),
            )
        console.print("\n")
        console.print(prt)
        readiness_summary = payload.get("promotion_readiness_summary") or {}
        if isinstance(readiness_summary, dict) and readiness_summary:
            console.print(
                f"[dim]Promotion readiness summary:[/dim] ready={int(readiness_summary.get('ready_count') or 0)}, review={int(readiness_summary.get('review_count') or 0)}, blocked={int(readiness_summary.get('blocked_count') or 0)}"
            )

    promotion_gates = list(payload.get("promotion_gates") or [])
    if promotion_gates:
        pgt = Table(title="Promotion gates")
        pgt.add_column("Status", no_wrap=True)
        pgt.add_column("Gate", overflow="fold", min_width=18)
        pgt.add_column("Surfaces", justify="right", no_wrap=True)
        pgt.add_column("Blocking", overflow="fold")
        pgt.add_column("Summary", overflow="fold")
        for item in promotion_gates[:6]:
            pgt.add_row(
                str(item.get("status") or "review").upper(),
                str(item.get("title") or item.get("gate_id") or ""),
                str(item.get("surface_count") or 0),
                ", ".join(str(x) for x in (item.get("blocking_surfaces") or [])[:4]) or "(none)",
                str(item.get("summary") or ""),
            )
        console.print("\n")
        console.print(pgt)
        gate_summary = payload.get("promotion_gate_summary") or {}
        if isinstance(gate_summary, dict) and gate_summary:
            console.print(
                f"[dim]Promotion gate summary:[/dim] pass={int(gate_summary.get('pass_count') or 0)}, review={int(gate_summary.get('review_count') or 0)}, fail={int(gate_summary.get('fail_count') or 0)}"
            )

    promotion_backlog = list(payload.get("promotion_backlog") or [])
    if promotion_backlog:
        pbt = Table(title="Promotion backlog")
        pbt.add_column("State", no_wrap=True)
        pbt.add_column("Task", overflow="fold", min_width=18)
        pbt.add_column("Priority", no_wrap=True)
        pbt.add_column("Wave", overflow="fold")
        pbt.add_column("Surface / gate", overflow="fold")
        pbt.add_column("Next action", overflow="fold")
        for item in promotion_backlog[:8]:
            pbt.add_row(
                str(item.get("queue_state") or "review").upper(),
                str(item.get("title") or item.get("task_id") or ""),
                str(item.get("priority") or "medium").upper(),
                str(item.get("wave_title") or item.get("wave_id") or ""),
                str(item.get("export_surface_id") or item.get("gate_id") or ""),
                str(item.get("next_action") or ""),
            )
        console.print("\n")
        console.print(pbt)
        backlog_summary = payload.get("promotion_backlog_summary") or {}
        if isinstance(backlog_summary, dict) and backlog_summary:
            console.print(
                f"[dim]Promotion backlog summary:[/dim] blocked={int(backlog_summary.get('blocked_count') or 0)}, review={int(backlog_summary.get('review_count') or 0)}, todo={int(backlog_summary.get('todo_count') or 0)}"
            )

    promotion_evidence = list(payload.get("promotion_evidence") or [])
    if promotion_evidence:
        pet = Table(title="Promotion evidence")
        pet.add_column("Status", no_wrap=True)
        pet.add_column("Subject", overflow="fold", min_width=18)
        pet.add_column("Kind", no_wrap=True)
        pet.add_column("Posture", no_wrap=True)
        pet.add_column("Missing", justify="right", no_wrap=True)
        pet.add_column("Required artifacts", overflow="fold")
        for item in promotion_evidence[:8]:
            pet.add_row(
                str(item.get("evidence_status") or "partial").upper(),
                str(item.get("title") or item.get("evidence_id") or ""),
                str(item.get("subject_kind") or "surface").upper(),
                str(item.get("posture") or "review").upper(),
                str(item.get("missing_count") or 0),
                ", ".join(str(x) for x in (item.get("required_artifacts") or [])[:4]) or "(none)",
            )
        console.print("\n")
        console.print(pet)
        evidence_summary = payload.get("promotion_evidence_summary") or {}
        if isinstance(evidence_summary, dict) and evidence_summary:
            console.print(
                f"[dim]Promotion evidence summary:[/dim] complete={int(evidence_summary.get('complete_count') or 0)}, partial={int(evidence_summary.get('partial_count') or 0)}, missing={int(evidence_summary.get('missing_count') or 0)}"
            )

    performance = payload.get("performance_profile") or {}
    hotspots = list(performance.get("hotspots") or [])
    if hotspots:
        pt = Table(title="Performance hotspots")
        pt.add_column("Severity", no_wrap=True)
        pt.add_column("Hotspot", overflow="fold", min_width=20)
        pt.add_column("Count", justify="right", no_wrap=True)
        pt.add_column("Macros", overflow="fold")
        pt.add_column("Actions", overflow="fold")
        for item in hotspots[:6]:
            pt.add_row(
                str(item.get("severity") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("count") or 0),
                ", ".join(str(x) for x in (item.get("macros") or [])[:4]) or "(none)",
                "; ".join(str(x) for x in (item.get("actions") or [])[:2]),
            )
        console.print("\n")
        console.print(pt)
        if performance.get("summary"):
            console.print(f"[dim]Performance summary:[/dim] {performance.get('summary')}")

    runtime_profiles = list(performance.get("macro_runtime_profiles") or [])[: int(macro_limit)]
    if runtime_profiles:
        rt = Table(title=f"Macro runtime profile (top {len(runtime_profiles)})")
        rt.add_column("Macro", no_wrap=True)
        rt.add_column("Risk", no_wrap=True)
        rt.add_column("Capture/OCR", no_wrap=True)
        rt.add_column("Poll/Event", no_wrap=True)
        rt.add_column("Delay", no_wrap=True)
        rt.add_column("Tags", overflow="fold")
        for item in runtime_profiles:
            rt.add_row(
                str(item.get("macro") or ""),
                f"{str(item.get('risk_level') or 'low').upper()} ({int(item.get('risk_score') or 0)})",
                f"{int(item.get('live_capture_steps') or 0)}/{int(item.get('ocr_steps') or 0)}",
                f"{int(item.get('polling_wait_steps') or 0)}/{int(item.get('event_wait_steps') or 0)}",
                str(int(item.get("declared_delay_ms") or 0)),
                ", ".join(str(x) for x in (item.get("tags") or [])) or "(none)",
            )
        console.print("\n")
        console.print(rt)

    input_lane_dossier = dict(payload.get("input_lane_dossier") or {})
    input_lanes = list(input_lane_dossier.get("lanes") or [])
    if input_lanes:
        ilt = Table(title="Input lane dossier")
        ilt.add_column("Lane", overflow="fold", min_width=20)
        ilt.add_column("Fit", no_wrap=True)
        ilt.add_column("Kind", no_wrap=True)
        ilt.add_column("Session", overflow="fold")
        ilt.add_column("Best for", overflow="fold")
        ilt.add_column("Boundaries", overflow="fold")
        for item in input_lanes[:6]:
            ilt.add_row(
                str(item.get("title") or item.get("id") or ""),
                str(item.get("fit") or "").upper(),
                str(item.get("kind") or ""),
                ", ".join(str(x) for x in (item.get("session_capabilities") or [])[:3]) or "(none)",
                ", ".join(str(x) for x in (item.get("recommended_for") or [])[:3]) or "(none)",
                ", ".join(str(x) for x in (item.get("host_requirement_ids") or [])[:3]) or "(none)",
            )
        console.print("\n")
        console.print(ilt)
        summary = str(input_lane_dossier.get("summary") or "").strip()
        if summary:
            console.print(f"[dim]Input lane summary:[/dim] {summary}")

    promotion_input_lane_plan = list(payload.get("promotion_input_lane_plan") or [])
    if promotion_input_lane_plan:
        pit = Table(title="Promotion lane plan")
        pit.add_column("Surface", overflow="fold", min_width=20)
        pit.add_column("Posture", no_wrap=True)
        pit.add_column("Primary lane", overflow="fold")
        pit.add_column("Alternates", overflow="fold")
        pit.add_column("Host review", overflow="fold")
        for item in promotion_input_lane_plan[:6]:
            pit.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("shipping_posture") or "").upper(),
                str(item.get("primary_input_lane_id") or "(orthogonal)"),
                ", ".join(str(x) for x in (item.get("alternate_input_lane_ids") or [])[:3]) or "(none)",
                ", ".join(str(x) for x in (item.get("host_requirement_ids") or [])[:3]) or "(none)",
            )
        console.print("\n")
        console.print(pit)

    promotion_activation_route_plan = list(payload.get("promotion_activation_route_plan") or [])
    if promotion_activation_route_plan:
        pat = Table(title="Promotion startup routes")
        pat.add_column("Surface", overflow="fold", min_width=20)
        pat.add_column("Posture", no_wrap=True)
        pat.add_column("Primary route", overflow="fold")
        pat.add_column("Kind", no_wrap=True)
        pat.add_column("Steady state", overflow="fold")
        for item in promotion_activation_route_plan[:6]:
            pat.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("startup_posture") or "").upper(),
                str(item.get("primary_activation_route_id") or "(orthogonal)"),
                str(item.get("primary_activation_kind") or ""),
                str(item.get("steady_state") or "(n/a)"),
            )
        console.print("\n")
        console.print(pat)

    promotion_operator_control_plan = list(payload.get("promotion_operator_control_plan") or [])
    promotion_recovery_plan = list(payload.get("promotion_recovery_plan") or [])
    promotion_verification_plan = list(payload.get("promotion_verification_plan") or [])
    promotion_performance_plan = list(payload.get("promotion_performance_plan") or [])
    promotion_dispatch_budget_plan = list(payload.get("promotion_dispatch_budget_plan") or [])
    promotion_authority_envelope_plan = list(payload.get("promotion_authority_envelope_plan") or [])
    if promotion_recovery_plan:
        prc = Table(title="Promotion recovery lanes")
        prc.add_column("Surface", overflow="fold", min_width=20)
        prc.add_column("Posture", no_wrap=True)
        prc.add_column("First response", overflow="fold")
        prc.add_column("Rollback / re-entry", overflow="fold")
        for item in promotion_recovery_plan[:6]:
            prc.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("recovery_posture") or "").upper(),
                str(item.get("first_response") or "(n/a)"),
                " / ".join(part for part in [str(item.get("rollback_surface") or "").strip(), str(item.get("reentry_check") or "").strip()] if part) or "(n/a)",
            )
        console.print("\n")
        console.print(prc)

    if promotion_operator_control_plan:
        pct = Table(title="Promotion operator controls")
        pct.add_column("Surface", overflow="fold", min_width=20)
        pct.add_column("Posture", no_wrap=True)
        pct.add_column("Control lane", overflow="fold")
        pct.add_column("Status / reload", overflow="fold")
        pct.add_column("Owner", overflow="fold")
        for item in promotion_operator_control_plan[:6]:
            pct.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("control_posture") or "").upper(),
                str(item.get("primary_control_lane_id") or "(review)"),
                " / ".join(
                    part
                    for part in [str(item.get("status_surface") or "").strip(), str(item.get("reload_surface") or "").strip()]
                    if part
                )
                or "(n/a)",
                str(item.get("operator_owner") or "(n/a)"),
            )
        console.print("\n")
        console.print(pct)

    if promotion_verification_plan:
        pvt = Table(title="Promotion verification lanes")
        pvt.add_column("Surface", overflow="fold", min_width=20)
        pvt.add_column("Posture", no_wrap=True)
        pvt.add_column("Verification lane", overflow="fold")
        pvt.add_column("Smoke / probe", overflow="fold")
        pvt.add_column("Gates", overflow="fold")
        for item in promotion_verification_plan[:6]:
            pvt.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("verification_posture") or "").upper(),
                str(item.get("primary_verification_lane_id") or "(review)"),
                " / ".join(
                    part
                    for part in [str(item.get("smoke_loop") or "").strip(), str(item.get("live_probe") or "").strip()]
                    if part
                )
                or "(n/a)",
                ", ".join(str(x) for x in (item.get("verification_gate_ids") or [])[:3]) or "(none)",
            )
        console.print("\n")
        console.print(pvt)

    if promotion_performance_plan:
        ppt = Table(title="Promotion performance envelopes")
        ppt.add_column("Surface", overflow="fold", min_width=20)
        ppt.add_column("Posture", no_wrap=True)
        ppt.add_column("Perf lane", overflow="fold")
        ppt.add_column("Latency", overflow="fold")
        ppt.add_column("Hotspots", overflow="fold")
        for item in promotion_performance_plan[:6]:
            ppt.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("performance_posture") or "").upper(),
                str(item.get("primary_performance_lane_id") or "(review)"),
                str(item.get("latency_class") or "(n/a)"),
                ", ".join(str(x) for x in (item.get("performance_hotspot_ids") or [])[:3]) or "(none)",
            )
        console.print("\n")
        console.print(ppt)

    if promotion_dispatch_budget_plan:
        pdt = Table(title="Promotion dispatch budgets")
        pdt.add_column("Surface", overflow="fold", min_width=20)
        pdt.add_column("Posture", no_wrap=True)
        pdt.add_column("Dispatch lane", overflow="fold")
        pdt.add_column("Cold start", overflow="fold")
        pdt.add_column("Steady state", overflow="fold")
        for item in promotion_dispatch_budget_plan[:6]:
            pdt.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("dispatch_posture") or "").upper(),
                str(item.get("primary_dispatch_lane_id") or "(review)"),
                str(item.get("cold_start_path") or "(n/a)"),
                str(item.get("steady_state_path") or "(n/a)"),
            )
        console.print("\n")
        console.print(pdt)

    if promotion_authority_envelope_plan:
        pat = Table(title="Promotion authority envelopes")
        pat.add_column("Surface", overflow="fold", min_width=20)
        pat.add_column("Posture", no_wrap=True)
        pat.add_column("Authority lane", overflow="fold")
        pat.add_column("Boundary", overflow="fold")
        pat.add_column("Revocation", overflow="fold")
        for item in promotion_authority_envelope_plan[:6]:
            pat.add_row(
                str(item.get("title") or item.get("export_surface_id") or ""),
                str(item.get("authority_posture") or "").upper(),
                str(item.get("primary_authority_lane_id") or "(review)"),
                str(item.get("authority_boundary") or "(n/a)"),
                str(item.get("revocation_surface") or "(n/a)"),
            )
        console.print("\n")
        console.print(pat)

    caps = payload.get("session_capabilities") or {}
    if isinstance(caps, dict) and caps:
        ct = Table(title="Session capability fit")
        ct.add_column("Capability", no_wrap=True)
        ct.add_column("Status", no_wrap=True)
        ct.add_column("Recommended", overflow="fold")
        ct.add_column("Mechanisms", overflow="fold")
        for name in ["screen_capture", "text_injection", "pointer_injection", "global_hotkeys", "window_introspection", "input_capture"]:
            item = caps.get(name)
            if not isinstance(item, dict):
                continue
            ct.add_row(
                name,
                str(item.get("status") or "unknown"),
                str(item.get("recommended") or ""),
                ", ".join(str(x) for x in (item.get("mechanisms") or [])[:4]),
            )
        console.print("\n")
        console.print(ct)

    planner_claim_witness = dict(payload.get("planner_claim_witness") or {})
    planner_target_claims = list(payload.get("planner_target_claims") or [])
    host_truth = dict(payload.get("host_truth") or {})
    portal_route_contract = dict(payload.get("portal_route_contract") or {})
    planner_evidence_lane = dict(payload.get("planner_evidence_lane") or {})
    planner_evidence_lane_fit = dict(payload.get("planner_evidence_lane_fit") or {})

    if planner_claim_witness or host_truth or portal_route_contract or planner_evidence_lane_fit:
        ht = Table(title="Current host proof posture")
        ht.add_column("Field", no_wrap=True)
        ht.add_column("Value", overflow="fold")
        ht.add_row("Host truth", str(host_truth.get("overall_status") or host_truth.get("status") or "unknown"))
        ht.add_row("Portal route", str(portal_route_contract.get("status") or "unknown"))
        ht.add_row("Current desktop", str(portal_route_contract.get("xdg_current_desktop") or "unknown"))
        if planner_claim_witness:
            ht.add_row("Claim witness", str(planner_claim_witness.get("status") or "unknown"))
            ht.add_row(
                "Reviewed claims",
                f"{int(planner_claim_witness.get('reviewed_claim_count') or 0)} (aligned/degraded/drifted/neutral/unknown: {int(planner_claim_witness.get('aligned_count') or 0)}/{int(planner_claim_witness.get('degraded_count') or 0)}/{int(planner_claim_witness.get('drifted_count') or 0)}/{int(planner_claim_witness.get('neutral_count') or 0)}/{int(planner_claim_witness.get('unknown_count') or 0)})",
            )
        if planner_evidence_lane_fit:
            ht.add_row("Evidence lane", str(planner_evidence_lane.get("profile_id") or planner_evidence_lane_fit.get("profile_id") or "unknown"))
            ht.add_row("Evidence fit", f"{planner_evidence_lane_fit.get('status') or 'unknown'} via {planner_evidence_lane_fit.get('selection_source') or 'flagship-default'}")
        console.print("\n")
        console.print(ht)

    if planner_target_claims:
        pct = Table(title="Planner target claims")
        pct.add_column("Level", no_wrap=True)
        pct.add_column("Target", overflow="fold", min_width=18)
        pct.add_column("Fit", no_wrap=True)
        pct.add_column("Witness", no_wrap=True)
        pct.add_column("Blockers", overflow="fold")
        for item in planner_target_claims[:8]:
            current_host_fit = dict(item.get("current_host_fit") or {})
            pct.add_row(
                str(item.get("recommended_level") or "unsupported").upper(),
                str(item.get("title") or item.get("target") or ""),
                str(item.get("fit") or "unknown").upper(),
                str(current_host_fit.get("status") or "n/a").upper(),
                ", ".join(str(x) for x in (item.get("blocking_capabilities") or [])[:4]) or "(none)",
            )
        console.print("\n")
        console.print(pct)

    window_contract = payload.get("window_contract") or {}
    if isinstance(window_contract, dict) and window_contract.get("used"):
        wt = Table(title="Window contract")
        wt.add_column("Field", no_wrap=True)
        wt.add_column("Value", overflow="fold")
        wt.add_row("Summary", str(window_contract.get("summary") or ""))
        wt.add_row("Dependency tags", ", ".join(str(x) for x in (window_contract.get("dependency_tags") or [])) or "(none)")
        wt.add_row("State fields", ", ".join(str(x) for x in (window_contract.get("state_fields_used") or [])) or "(none)")
        wt.add_row("Identity fields", ", ".join(str(x) for x in (window_contract.get("identity_fields_used") or [])) or "(none)")
        wt.add_row("Geometry", f"requested={int(window_contract.get('geometry_requested_count') or 0)}, required={int(window_contract.get('geometry_required_count') or 0)}")
        wt.add_row("Pointer-window", f"steps={int(window_contract.get('pointer_window_count') or 0)}, strict={int(window_contract.get('pointer_window_required_count') or 0)}")
        console.print("\n")
        console.print(wt)

    lanes = list(payload.get("product_lanes") or [])
    if lanes:
        lt = Table(title="Product lanes")
        lt.add_column("Score", no_wrap=True, justify="right")
        lt.add_column("Lane", overflow="fold", min_width=18)
        lt.add_column("Focus", overflow="fold")
        lt.add_column("Evidence", overflow="fold")
        for item in lanes[:8]:
            lt.add_row(
                str(item.get("score") or 0),
                str(item.get("title") or ""),
                str(item.get("focus") or ""),
                ", ".join(str(x) for x in (item.get("evidence") or [])[:4]),
            )
        console.print("\n")
        console.print(lt)

    architecture = payload.get("architecture_map") or {}
    if isinstance(architecture, dict) and (architecture.get("components") or architecture.get("risks")):
        at = Table(title="Architecture map")
        at.add_column("Priority", no_wrap=True)
        at.add_column("Component", overflow="fold", min_width=18)
        at.add_column("Owner", overflow="fold")
        at.add_column("Tooling", overflow="fold")
        for item in list(architecture.get("components") or [])[:8]:
            at.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("owner") or ""),
                str(item.get("tooling") or ""),
            )
        console.print("\n")
        console.print(at)
        if architecture.get("stance"):
            console.print(f"[dim]Architecture stance:[/dim] {architecture.get('stance')}")

    targets = list(payload.get("integration_targets") or [])
    if targets:
        tt = Table(title="Recommended integration targets")
        tt.add_column("Priority", no_wrap=True)
        tt.add_column("Target", overflow="fold", min_width=18)
        tt.add_column("Tooling", overflow="fold")
        tt.add_column("Why", overflow="fold")
        for item in targets[:8]:
            tt.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("tool") or ""),
                ", ".join(str(x) for x in (item.get("evidence") or [])[:4]),
            )
        console.print("\n")
        console.print(tt)

    playbooks = list(payload.get("playbooks") or [])
    if playbooks:
        pt = Table(title="Implementation playbooks")
        pt.add_column("Priority", no_wrap=True)
        pt.add_column("Playbook", overflow="fold", min_width=18)
        pt.add_column("Goal", overflow="fold")
        pt.add_column("Commands", overflow="fold")
        for item in playbooks[:8]:
            cmds = "\n".join(str(x) for x in (item.get("commands") or [])[:3])
            pt.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("goal") or ""),
                cmds,
            )
        console.print("\n")
        console.print(pt)

    profiles = list(payload.get("stack_profiles") or payload.get("deployment_profiles") or [])
    if profiles:
        dt = Table(title="Suggested stack profiles")
        dt.add_column("Score", no_wrap=True, justify="right")
        dt.add_column("Profile", overflow="fold", min_width=18)
        dt.add_column("Fit", no_wrap=True)
        dt.add_column("Shape", no_wrap=True)
        dt.add_column("Execution surface", overflow="fold")
        for item in profiles[:8]:
            dt.add_row(
                str(item.get("score") or 0),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                str(item.get("product_shape") or ""),
                str(item.get("execution_surface") or ""),
            )
        console.print("\n")
        console.print(dt)

    runtime_seams = list(payload.get("runtime_seams") or [])
    if runtime_seams:
        rs = Table(title="Runtime seams")
        rs.add_column("Kind", no_wrap=True)
        rs.add_column("Seam", overflow="fold", min_width=20)
        rs.add_column("Fit", no_wrap=True)
        rs.add_column("Owner", overflow="fold")
        rs.add_column("Why split", overflow="fold")
        for item in runtime_seams[:8]:
            rs.add_row(
                str(item.get("layer_kind") or ""),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                str(item.get("owner") or ""),
                str(item.get("why_split") or ""),
            )
        console.print("\n")
        console.print(rs)

    ecosystem_lessons = list(payload.get("ecosystem_lessons") or [])
    if ecosystem_lessons:
        el = Table(title="Ecosystem lessons")
        el.add_column("Category", no_wrap=True)
        el.add_column("Lesson", overflow="fold", min_width=20)
        el.add_column("From", overflow="fold")
        el.add_column("What VHK should do", overflow="fold")
        for item in ecosystem_lessons[:8]:
            el.add_row(
                str(item.get("category") or ""),
                str(item.get("title") or ""),
                ", ".join(str(x) for x in (item.get("source_tools") or [])[:3]),
                str(item.get("product_implication") or ""),
            )
        console.print("\n")
        console.print(el)

    desktop_targets = list(payload.get("desktop_targets") or [])
    if desktop_targets:
        xt = Table(title="Desktop target matrix")
        xt.add_column("Score", no_wrap=True, justify="right")
        xt.add_column("Target", overflow="fold", min_width=20)
        xt.add_column("Fit", no_wrap=True)
        xt.add_column("Trigger surface", overflow="fold")
        xt.add_column("Packaging", overflow="fold")
        for item in desktop_targets[:8]:
            xt.add_row(
                str(item.get("score") or 0),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                str(item.get("trigger_surface") or ""),
                str(item.get("packaging") or ""),
            )
        console.print("\n")
        console.print(xt)

    surface_choices = list(payload.get("surface_choices") or [])
    if surface_choices:
        st = Table(title="Candidate integration surfaces")
        st.add_column("Score", no_wrap=True, justify="right")
        st.add_column("Category", no_wrap=True)
        st.add_column("Surface", overflow="fold", min_width=20)
        st.add_column("Fit", no_wrap=True)
        st.add_column("Strengths", overflow="fold")
        st.add_column("Commands", overflow="fold")
        for item in surface_choices[:10]:
            cmds = "\n".join(str(x) for x in (item.get("commands") or [])[:2])
            st.add_row(
                str(item.get("score") or 0),
                str(item.get("category") or ""),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                str(item.get("strengths") or ""),
                cmds,
            )
        console.print("\n")
        console.print(st)

    environment_diffs = list(payload.get("environment_diffs") or [])
    if environment_diffs:
        et = Table(title="Environment comparison")
        et.add_column("Score", no_wrap=True, justify="right")
        et.add_column("Environment", overflow="fold", min_width=20)
        et.add_column("Fit", no_wrap=True)
        et.add_column("Top target", overflow="fold")
        et.add_column("Top profile", overflow="fold")
        et.add_column("Blockers", overflow="fold")
        for item in environment_diffs[:8]:
            top_target = item.get("top_target") or {}
            top_profile = item.get("top_profile") or {}
            et.add_row(
                str(item.get("score") or 0),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                str(top_target.get("title") or ""),
                str(top_profile.get("title") or ""),
                ", ".join(str(x) for x in (item.get("blocking_capabilities") or [])[:4]) or "",
            )
        console.print("\n")
        console.print(et)

    portability_gaps = list(payload.get("portability_gaps") or [])
    if portability_gaps:
        pg = Table(title="Portability gaps")
        pg.add_column("Δ", no_wrap=True, justify="right")
        pg.add_column("Environment", overflow="fold", min_width=20)
        pg.add_column("New blockers", overflow="fold")
        pg.add_column("Replace surfaces", overflow="fold")
        pg.add_column("Migration response", overflow="fold")
        for item in portability_gaps[:8]:
            replace_bits = []
            for change in (item.get("replace_surfaces") or [])[:3]:
                frm = (change.get("from") or {}).get("title") if isinstance(change, dict) else ""
                to = (change.get("to") or {}).get("title") if isinstance(change, dict) and isinstance(change.get("to"), dict) else ""
                if frm and to:
                    replace_bits.append(f"{frm} → {to}")
                elif frm:
                    replace_bits.append(str(frm))
            pg.add_row(
                str(item.get("score_delta") or 0),
                str(item.get("title") or ""),
                ", ".join(str(x) for x in (item.get("newly_blocked_capabilities") or [])[:4]) or "",
                "; ".join(replace_bits),
                str(item.get("migration_response") or ""),
            )
        console.print("\n")
        console.print(pg)

    portability_playbooks = list(payload.get("portability_playbooks") or [])
    if portability_playbooks:
        pp = Table(title="Portability playbooks")
        pp.add_column("Priority", no_wrap=True)
        pp.add_column("Environment", overflow="fold", min_width=20)
        pp.add_column("Goal", overflow="fold")
        pp.add_column("Artifacts", overflow="fold")
        pp.add_column("Commands", overflow="fold")
        for item in portability_playbooks[:8]:
            artifact_bits = []
            for artifact in (item.get("artifacts") or [])[:3]:
                if isinstance(artifact, dict):
                    title = str(artifact.get("title") or "")
                    path_hint = str(artifact.get("path_hint") or "")
                    artifact_bits.append(f"{title} ({path_hint})" if path_hint else title)
            cmds = "\n".join(str(x) for x in (item.get("commands") or [])[:2])
            pp.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("goal") or ""),
                "; ".join(artifact_bits),
                cmds,
            )
        console.print("\n")
        console.print(pp)

    toolchain_choices = list(payload.get("toolchain_choices") or [])
    if toolchain_choices:
        tc = Table(title="Concrete toolchain choices")
        tc.add_column("Score", no_wrap=True, justify="right")
        tc.add_column("Category", no_wrap=True)
        tc.add_column("Capability", overflow="fold", min_width=22)
        tc.add_column("Recommended", overflow="fold")
        tc.add_column("Fallbacks", overflow="fold")
        for item in toolchain_choices[:8]:
            tc.add_row(
                str(item.get("score") or 0),
                str(item.get("category") or ""),
                str(item.get("title") or ""),
                str(item.get("recommended_toolchain") or ""),
                ", ".join(str(x) for x in (item.get("fallback_toolchains") or [])[:4]),
            )
        console.print("\n")
        console.print(tc)

    capability_coverage = list(payload.get("capability_coverage") or [])
    if capability_coverage:
        cc = Table(title="Capability coverage matrix")
        cc.add_column("Capability", overflow="fold", min_width=22)
        cc.add_column("Use", no_wrap=True, justify="right")
        cc.add_column("Class", no_wrap=True)
        cc.add_column("Current", no_wrap=True)
        cc.add_column("Best environments", overflow="fold")
        cc.add_column("Blockers", overflow="fold")
        for item in capability_coverage[:8]:
            cc.add_row(
                str(item.get("title") or ""),
                str(item.get("usage_count") or 0),
                str(item.get("coverage_class") or ""),
                str(item.get("current_status") or "unknown"),
                ", ".join(str(x) for x in (item.get("best_environments") or [])[:3]),
                ", ".join(str(x) for x in (item.get("blocking_environments") or [])[:3]),
            )
        console.print("\n")
        console.print(cc)

    verification_gates = list(payload.get("verification_gates") or [])
    if verification_gates:
        vg = Table(title="Verification gates")
        vg.add_column("Priority", no_wrap=True)
        vg.add_column("Gate", no_wrap=True)
        vg.add_column("Capability", overflow="fold", min_width=22)
        vg.add_column("Acceptance", overflow="fold")
        vg.add_column("Commands", overflow="fold")
        for item in verification_gates[:8]:
            acceptance = "\n".join(str(x) for x in (item.get("acceptance_checks") or [])[:2])
            cmds = "\n".join(str(x) for x in (item.get("commands") or [])[:2])
            vg.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("gate_type") or "capability"),
                str(item.get("title") or ""),
                acceptance,
                cmds,
            )
        console.print("\n")
        console.print(vg)

    implementation_waves = list(payload.get("implementation_waves") or [])
    if implementation_waves:
        iw = Table(title="Implementation waves")
        iw.add_column("#", no_wrap=True, justify="right")
        iw.add_column("Priority", no_wrap=True)
        iw.add_column("Wave", overflow="fold", min_width=24)
        iw.add_column("Objective", overflow="fold")
        iw.add_column("Commands", overflow="fold")
        for item in implementation_waves[:8]:
            cmds = "\n".join(str(x) for x in (item.get("commands") or [])[:2])
            iw.add_row(
                str(item.get("order") or ""),
                str(item.get("priority") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("objective") or ""),
                cmds,
            )
        console.print("\n")
        console.print(iw)

    artifact_blueprint = list(payload.get("artifact_blueprint") or [])
    if artifact_blueprint:
        ab = Table(title="Artifact blueprint")
        ab.add_column("Priority", no_wrap=True)
        ab.add_column("Category", no_wrap=True)
        ab.add_column("Artifact", overflow="fold", min_width=24)
        ab.add_column("Surface", overflow="fold")
        ab.add_column("First wave", overflow="fold")
        ab.add_column("Generate", overflow="fold")
        for item in artifact_blueprint[:8]:
            first_wave = item.get("first_wave") or {}
            cmds = "\n".join(str(x) for x in (item.get("generator_commands") or [])[:2])
            ab.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("category") or "support"),
                str(item.get("title") or ""),
                str(item.get("deployment_surface") or ""),
                str(first_wave.get("title") or ""),
                cmds,
            )
        console.print("\n")
        console.print(ab)

    deployable_surfaces = list(payload.get("deployable_surfaces") or [])
    if deployable_surfaces:
        ds = Table(title="Deployable surfaces")
        ds.add_column("Priority", no_wrap=True)
        ds.add_column("Category", no_wrap=True)
        ds.add_column("Surface", overflow="fold", min_width=24)
        ds.add_column("Fit", no_wrap=True)
        ds.add_column("Entrypoint", overflow="fold")
        ds.add_column("Generate", overflow="fold")
        for item in deployable_surfaces[:8]:
            cmds = "\n".join(str(x) for x in (item.get("generator_commands") or [])[:2])
            ds.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("category") or "support"),
                str(item.get("title") or ""),
                str(item.get("fit") or "").upper(),
                str(item.get("entrypoint") or ""),
                cmds,
            )
        console.print("\n")
        console.print(ds)

    setup_recipes = list(payload.get("setup_recipes") or [])
    if setup_recipes:
        sr = Table(title="Setup recipes")
        sr.add_column("Priority", no_wrap=True)
        sr.add_column("Audience", no_wrap=True)
        sr.add_column("Recipe", overflow="fold", min_width=24)
        sr.add_column("Use when", overflow="fold")
        sr.add_column("Install", overflow="fold")
        sr.add_column("Verify", overflow="fold")
        for item in setup_recipes[:8]:
            install_steps = "\n".join(str(x) for x in (item.get("install_steps") or [])[:2])
            verify_steps = "\n".join(str(x) for x in (item.get("verify_steps") or [])[:2])
            sr.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("audience") or "author/operator"),
                str(item.get("title") or ""),
                str(item.get("when_to_use") or ""),
                install_steps,
                verify_steps,
            )
        console.print("\n")
        console.print(sr)

    host_requirements = list(payload.get("host_requirements") or [])
    if host_requirements:
        hr = Table(title="Host-side requirements")
        hr.add_column("Priority", no_wrap=True)
        hr.add_column("Type", no_wrap=True)
        hr.add_column("Requirement", overflow="fold", min_width=24)
        hr.add_column("Capability", overflow="fold")
        hr.add_column("Why", overflow="fold")
        hr.add_column("Verify", overflow="fold")
        for item in host_requirements[:8]:
            cmds = "\n".join(str(x) for x in (item.get("verify_commands") or [])[:2])
            hr.add_row(
                str(item.get("priority") or "conditional").upper(),
                str(item.get("requirement_type") or ""),
                str(item.get("title") or ""),
                str(item.get("capability") or ""),
                str(item.get("why") or ""),
                cmds,
            )
        console.print("\n")
        console.print(hr)

    reference_patterns = list(payload.get("reference_patterns") or [])
    if reference_patterns:
        rp = Table(title="Reference patterns")
        rp.add_column("Score", no_wrap=True, justify="right")
        rp.add_column("Type", no_wrap=True)
        rp.add_column("Pattern", overflow="fold", min_width=22)
        rp.add_column("Borrow", overflow="fold")
        rp.add_column("Commands", overflow="fold")
        for item in reference_patterns[:8]:
            cmds = "\n".join(str(x) for x in (item.get("commands") or [])[:2])
            rp.add_row(
                str(item.get("score") or 0),
                str(item.get("pattern_type") or ""),
                str(item.get("title") or ""),
                "; ".join(str(x) for x in (item.get("borrow") or [])[:2]),
                cmds,
            )
        console.print("\n")
        console.print(rp)

    roadmap = list(payload.get("next_steps") or [])
    if roadmap:
        nt = Table(title="Suggested next steps")
        nt.add_column("Priority", no_wrap=True)
        nt.add_column("Step", overflow="fold", min_width=18)
        nt.add_column("Details", overflow="fold")
        nt.add_column("Links", overflow="fold")
        for item in roadmap[:8]:
            nt.add_row(
                str(item.get("priority") or "medium").upper(),
                str(item.get("title") or ""),
                str(item.get("details") or ""),
                ", ".join(str(x) for x in (item.get("related_targets") or [])[:4]),
            )
        console.print("\n")
        console.print(nt)

    recs = list(payload.get("recommendations") or [])
    if recs:
        rt = Table(title="Strategy recommendations")
        rt.add_column("Severity", no_wrap=True)
        rt.add_column("Finding", overflow="fold", min_width=16)
        rt.add_column("Recommendation", overflow="fold")
        rt.add_column("Evidence", overflow="fold")
        for item in recs[:12]:
            rt.add_row(
                str(item.get("severity") or "info").upper(),
                str(item.get("summary") or ""),
                str(item.get("details") or ""),
                ", ".join(str(x) for x in (item.get("evidence") or [])[:4]),
            )
        console.print("\n")
        console.print(rt)


@app.command(name="gen-session-fit-pack")
def gen_session_fit_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    fit_doc: bool = typer.Option(True, "--fit-doc/--no-fit-doc", help="Write docs/VHK_SESSION_FIT.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_SESSION_FIXUPS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_SESSION_PLAN.json"),
    review_script: bool = typer.Option(True, "--review-script/--no-review-script", help="Write scripts/vhk_review_session_fit.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a host/session-fit handoff by comparing project needs with the current desktop."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_session_fit_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        fit_doc=fit_doc,
        fixups_doc=fixups_doc,
        plan_json=plan_json,
        review_script=review_script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        evidence_lane_profile=evidence_lane,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK session-fit pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["fit_doc", "fixups_doc", "plan_json", "review_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-host-contract-pack")
def gen_host_contract_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    requirements_doc: bool = typer.Option(True, "--requirements-doc/--no-requirements-doc", help="Write docs/VHK_HOST_REQUIREMENTS.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_HOST_FIXUPS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_HOST_PLAN.json"),
    review_script: bool = typer.Option(True, "--review-script/--no-review-script", help="Write scripts/vhk_review_host_contract.sh"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host probes (helpers/uinput/portal routing)"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a host-side deployment contract for packages, services, permissions, and portal routing."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if host_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            host_snapshot = _validation_host_contract_snapshot()
        except Exception as exc:
            session_issues = [
                {
                    "message": "host contract check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_host_contract_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        requirements_doc=requirements_doc,
        fixups_doc=fixups_doc,
        plan_json=plan_json,
        review_script=review_script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK host-contract pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["requirements_doc", "fixups_doc", "plan_json", "review_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if host_check:
        console.print(f"[dim]Host/session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-readiness-pack")
def gen_readiness_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    report_doc: bool = typer.Option(True, "--report-doc/--no-report-doc", help="Write docs/VHK_READINESS_REPORT.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_READINESS_FIXUPS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_READINESS_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_refresh_readiness_report.sh"),
    readiness_check: bool = typer.Option(True, "--readiness-check/--no-readiness-check", help="Include current host service/group/device probes"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a live readiness pack for service state, groups, and raw-input/portal deployment seams."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if readiness_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            strategy = summarize_project_strategy(
                project,
                capability_usage=capability_usage,
                capability_matrix=session_capabilities,
                capability_issues=session_issues,
                evidence_lane_profile=evidence_lane,
            )
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            session_issues = [
                {
                    "message": "readiness check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_readiness_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        report_doc=report_doc,
        fixups_doc=fixups_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK readiness pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["report_doc", "fixups_doc", "plan_json", "refresh_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if readiness_check:
        console.print(f"[dim]Readiness/session issues captured:[/dim] {len(session_issues)}")



@app.command(name="gen-activation-pack")
def gen_activation_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    routes_doc: bool = typer.Option(True, "--routes-doc/--no-routes-doc", help="Write docs/VHK_ACTIVATION_ROUTES.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_ACTIVATION_FIXUPS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_ACTIVATION_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_review_activation_routes.sh"),
    activation_check: bool = typer.Option(True, "--activation-check/--no-activation-check", help="Include current host/readiness probes"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a reviewable Linux activation-route pack for the project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if activation_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            strategy = summarize_project_strategy(
                project,
                capability_usage=capability_usage,
                capability_matrix=session_capabilities,
                capability_issues=session_issues,
            )
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            session_issues = [
                {
                    "message": "activation check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_activation_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        routes_doc=routes_doc,
        fixups_doc=fixups_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK activation pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["routes_doc", "fixups_doc", "plan_json", "refresh_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if activation_check:
        console.print(f"[dim]Activation issues captured:[/dim] {len(session_issues)}")




@app.command(name="gen-capability-audit-pack")
def gen_capability_audit_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    build_root: Path | None = typer.Option(None, "--build-root", help="Where to write the capability-audit handoff tree (default: <project>/build/capability-audit/<name>)"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    audit_doc: bool = typer.Option(True, "--audit-doc/--no-audit-doc", help="Write docs/VHK_CAPABILITY_AUDIT.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_CAPABILITY_FIXUPS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_CAPABILITY_AUDIT_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_refresh_capability_audit_pack.sh"),
    handoff: bool = typer.Option(True, "--handoff/--no-handoff", help="Write build/capability-audit/... handoff tree"),
    audit_check: bool = typer.Option(True, "--audit-check/--no-audit-check", help="Include current host/session probes"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a capability audit and fallback pack for Linux session/helper boundaries."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if audit_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            strategy = summarize_project_strategy(
                project,
                capability_usage=capability_usage,
                capability_matrix=session_capabilities,
                capability_issues=session_issues,
            )
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            session_issues = [
                {
                    "message": "capability audit check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_capability_audit_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        build_root=build_root,
        force=force,
        audit_doc=audit_doc,
        fixups_doc=fixups_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        handoff=handoff,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK capability-audit pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["audit_doc", "fixups_doc", "plan_json", "refresh_script", "handoff_readme", "handoff_manifest", "handoff_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if audit_check:
        console.print(f"[dim]Audit/session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-promotion-pack")
def gen_promotion_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    promotion_doc: bool = typer.Option(True, "--promotion-doc/--no-promotion-doc", help="Write docs/VHK_PROMOTION_PLAN.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_PROMOTION_FIXUPS.md"),
    backlog_doc: bool = typer.Option(True, "--backlog-doc/--no-backlog-doc", help="Write docs/VHK_PROMOTION_BACKLOG.md"),
    evidence_doc: bool = typer.Option(True, "--evidence-doc/--no-evidence-doc", help="Write docs/VHK_PROMOTION_EVIDENCE.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_PROMOTION_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_review_promotion_plan.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a staged export-promotion review pack for the project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            strategy = summarize_project_strategy(
                project,
                capability_usage=capability_usage,
                capability_matrix=session_capabilities,
                capability_issues=session_issues,
            )
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            session_issues = [
                {
                    "message": "promotion session check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_promotion_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        promotion_doc=promotion_doc,
        fixups_doc=fixups_doc,
        backlog_doc=backlog_doc,
        evidence_doc=evidence_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK promotion pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["promotion_doc", "fixups_doc", "backlog_doc", "evidence_doc", "plan_json", "refresh_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-route-selection-pack")
def gen_route_selection_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    selection_doc: bool = typer.Option(True, "--selection-doc/--no-selection-doc", help="Write docs/VHK_ROUTE_SELECTION.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_ROUTE_FIXUPS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_ROUTE_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_review_route_selection.sh"),
    selection_check: bool = typer.Option(True, "--selection-check/--no-selection-check", help="Include current host/readiness probes"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a reviewable reference-route selection pack for the project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if selection_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            strategy = summarize_project_strategy(
                project,
                capability_usage=capability_usage,
                capability_matrix=session_capabilities,
                capability_issues=session_issues,
            )
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            session_issues = [
                {
                    "message": "route selection check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_route_selection_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        selection_doc=selection_doc,
        fixups_doc=fixups_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK route-selection pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["selection_doc", "fixups_doc", "plan_json", "refresh_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if selection_check:
        console.print(f"[dim]Route-selection issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-target-route-pack")
def gen_target_route_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    matrix_doc: bool = typer.Option(True, "--matrix-doc/--no-matrix-doc", help="Write docs/VHK_TARGET_ROUTE_MATRIX.md"),
    fixups_doc: bool = typer.Option(True, "--fixups-doc/--no-fixups-doc", help="Write docs/VHK_TARGET_ROUTE_FIXUPS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_TARGET_ROUTE_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_compare_target_routes.sh"),
    target_profile: list[str] = typer.Option([], "--target-profile", help="Limit comparison to specific target profile ids (repeatable)"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a hypothetical target-desktop route-comparison pack for the project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)

    written = write_target_route_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        matrix_doc=matrix_doc,
        fixups_doc=fixups_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        target_profiles=list(target_profile or []),
        capability_usage=capability_usage,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK target-route pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["matrix_doc", "fixups_doc", "plan_json", "refresh_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-release-lane-pack")
def gen_release_lane_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    lanes_doc: bool = typer.Option(True, "--lanes-doc/--no-lanes-doc", help="Write docs/VHK_RELEASE_LANES.md"),
    snippets_doc: bool = typer.Option(True, "--snippets-doc/--no-snippets-doc", help="Write docs/VHK_RELEASE_SNIPPETS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_RELEASE_LANE_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_refresh_release_lanes.sh"),
    target_profile: list[str] = typer.Option([], "--target-profile", help="Limit the release pack to specific target profile ids (repeatable)"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed per-desktop release-lane docs for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)

    written = write_release_lane_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        lanes_doc=lanes_doc,
        snippets_doc=snippets_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        target_profiles=list(target_profile or []),
        capability_usage=capability_usage,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK release-lane pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["lanes_doc", "snippets_doc", "plan_json", "refresh_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-release-deploy-pack")
def gen_release_deploy_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    deploy_doc: bool = typer.Option(True, "--deploy-doc/--no-deploy-doc", help="Write docs/VHK_RELEASE_DEPLOYMENT.md"),
    snippets_doc: bool = typer.Option(True, "--snippets-doc/--no-snippets-doc", help="Write docs/VHK_RELEASE_INSTALL_SNIPPETS.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_RELEASE_DEPLOY_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_refresh_release_deploy.sh"),
    target_profile: list[str] = typer.Option([], "--target-profile", help="Limit the deploy pack to specific target profile ids (repeatable)"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host probes for deployment truth / portal routing"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate lane-native Linux install/autostart artifacts for VHK release lanes."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [{"message": "session capability check failed", "severity": "warning", "suggestion": str(exc), "used_by": []}]
    host_snapshot = None
    if host_check:
        try:
            strategy = summarize_project_strategy(project, capability_usage=capability_usage, capability_matrix=session_capabilities, capability_issues=session_issues, evidence_lane_profile=evidence_lane)
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception:
            host_snapshot = None

    written = write_release_deploy_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        deploy_doc=deploy_doc,
        snippets_doc=snippets_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        target_profiles=list(target_profile or []),
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK release-deploy pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["deploy_doc", "snippets_doc", "plan_json", "refresh_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-release-stage-pack")
def gen_release_stage_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write helper scripts (default: <project>/scripts)"),
    build_dir: Path | None = typer.Option(None, "--build-dir", help="Where to materialize stage trees (default: <project>/build/release-stage)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide_doc: bool = typer.Option(True, "--guide-doc/--no-guide-doc", help="Write docs/VHK_RELEASE_STAGE.md"),
    matrix_doc: bool = typer.Option(True, "--matrix-doc/--no-matrix-doc", help="Write docs/VHK_RELEASE_STAGE_MATRIX.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_RELEASE_STAGE_PLAN.json"),
    refresh_script: bool = typer.Option(True, "--refresh-script/--no-refresh-script", help="Write scripts/vhk_refresh_release_stage.sh"),
    materialize_stage_trees: bool = typer.Option(True, "--materialize-stage-trees/--no-materialize-stage-trees", help="Write per-lane stage trees under build/release-stage"),
    target_profile: list[str] = typer.Option([], "--target-profile", help="Limit the stage pack to specific target profile ids (repeatable)"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host readiness snapshot"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate per-lane staged payload trees for VHK release lanes."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]
    host_snapshot = None
    if host_check:
        try:
            strategy = summarize_project_strategy(project)
            requirements = [
                dict(item)
                for item in list((strategy.get("host_requirements") or []))
                if isinstance(item, dict)
            ]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            host_snapshot = {"status": "probe_failed", "error": str(exc)}

    written = write_release_stage_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        build_dir=build_dir,
        force=force,
        guide_doc=guide_doc,
        matrix_doc=matrix_doc,
        plan_json=plan_json,
        refresh_script=refresh_script,
        materialize_stage_trees=materialize_stage_trees,
        target_profiles=list(target_profile or []),
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK release-stage pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["guide_doc", "matrix_doc", "plan_json", "refresh_script", "build_dir"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-design-pack")
def gen_design_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    brief: bool = typer.Option(True, "--brief/--no-brief", help="Write docs/VHK_DESIGN_BRIEF.md"),
    contract: bool = typer.Option(True, "--contract/--no-contract", help="Write docs/VHK_RUNTIME_CONTRACT.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_DESIGN_PLAN.json"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed design/runtime architecture docs for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_design_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        force=force,
        brief=brief,
        contract=contract,
        plan_json=plan_json,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK design pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["brief", "contract", "plan_json"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-operator-pack")
def gen_operator_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide: bool = typer.Option(True, "--guide/--no-guide", help="Write docs/VHK_OPERATOR_GUIDE.md"),
    checklist: bool = typer.Option(True, "--checklist/--no-checklist", help="Write docs/VHK_DEPLOYMENT_CHECKLIST.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_OPERATOR_PLAN.json"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed operator/deployment docs for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_operator_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        force=force,
        guide=guide,
        checklist=checklist,
        plan_json=plan_json,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK operator pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["guide", "checklist", "plan_json"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-verification-pack")
def gen_verification_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the verification script (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide: bool = typer.Option(True, "--guide/--no-guide", help="Write docs/VHK_VERIFICATION_GUIDE.md"),
    checklist: bool = typer.Option(True, "--checklist/--no-checklist", help="Write docs/VHK_RELEASE_CHECKLIST.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_VERIFICATION_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_verify_release.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed release verification docs/checklists/scripts for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_verification_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        guide=guide,
        checklist=checklist,
        plan_json=plan_json,
        script=script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK verification pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["guide", "checklist", "plan_json", "script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-support-pack")
def gen_support_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the support capture script (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide: bool = typer.Option(True, "--guide/--no-guide", help="Write docs/VHK_SUPPORT_GUIDE.md"),
    checklist: bool = typer.Option(True, "--checklist/--no-checklist", help="Write docs/VHK_SUPPORT_CHECKLIST.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_SUPPORT_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_capture_support.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed support/triage docs/checklists/scripts for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_support_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        guide=guide,
        checklist=checklist,
        plan_json=plan_json,
        script=script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK support pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["guide", "checklist", "plan_json", "script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")




@app.command(name="gen-portability-pack")
def gen_portability_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the portability review script (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide: bool = typer.Option(True, "--guide/--no-guide", help="Write docs/VHK_PORTABILITY_GUIDE.md"),
    rollout: bool = typer.Option(True, "--rollout/--no-rollout", help="Write docs/VHK_TARGET_ROLLOUT.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_PORTABILITY_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_review_portability.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed portability docs/checklists/scripts for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_portability_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        guide=guide,
        rollout=rollout,
        plan_json=plan_json,
        script=script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK portability pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["guide", "rollout", "plan_json", "script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-claim-pack")
def gen_claim_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the claim audit script (default: <project>/scripts)"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide: bool = typer.Option(True, "--guide/--no-guide", help="Write docs/VHK_CLAIM_GUIDE.md"),
    claims: bool = typer.Option(True, "--claims/--no-claims", help="Write docs/VHK_TARGET_CLAIMS.yaml"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_CLAIM_AUDIT_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_audit_claims.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed target-claim docs/manifests/scripts for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            strategy = summarize_project_strategy(project, capability_usage=capability_usage, capability_matrix=session_capabilities, capability_issues=session_issues)
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]
            host_snapshot = None

    written = write_claim_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        guide=guide,
        claims=claims,
        plan_json=plan_json,
        script=script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK claim pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["guide", "claims", "plan_json", "script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


@app.command(name="gen-publish-pack")
def gen_publish_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the publish refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Bundle one reviewed release-stage profile instead of the whole project when generating publish commands/scripts"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    support_doc: bool = typer.Option(True, "--support-doc/--no-support-doc", help="Write docs/VHK_PUBLIC_SUPPORT.md"),
    quickstart: bool = typer.Option(True, "--quickstart/--no-quickstart", help="Write docs/VHK_INSTALL_QUICKSTART.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_PUBLISH_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_publish_pack.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed publish/distribution docs/metadata for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    written = write_publish_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        force=force,
        support_doc=support_doc,
        quickstart=quickstart,
        plan_json=plan_json,
        script=script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK publish pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["support_doc", "quickstart", "plan_json", "script", "handoff_root", "handoff_manifest", "handoff_bundle_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")


def _trigger_pack_comment_prefix(kind: str) -> str:
    return ";;" if kind == "double-semicolon" else "#"


def _trigger_pack_render_header(*, posture: dict[str, Any], surface_title: str, surface_id: str, generator_command: str, comment_style: str) -> str:
    prefix = _trigger_pack_comment_prefix(comment_style)
    lines = [
        f"{prefix} VHK trigger-pack surface: {surface_title}",
        f"{prefix} Surface id: {surface_id}",
        f"{prefix} Support headline: {posture.get('headline') or 'Support posture unavailable'}",
        f"{prefix} Generated by: vhk gen-trigger-pack",
        f"{prefix} Refresh command: {generator_command}",
    ]

    for label, key in [
        ("Reference", "reference_targets"),
        ("Supported", "supported_targets"),
        ("Caveated", "caveated_targets"),
        ("Experimental", "experimental_targets"),
    ]:
        values = [str(x) for x in list(posture.get(key) or []) if str(x)]
        if values:
            lines.append(f"{prefix} {label} lanes: {', '.join(values[:4])}")
    lines.append("")
    return "\n".join(lines)


def _trigger_pack_write(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"Refusing to overwrite existing file: {path}. Use --force.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _trigger_pack_path_for_display(path: Path, project_dir: Path) -> str:
    try:
        rel = path.resolve().relative_to(project_dir.resolve())
        return "./" + rel.as_posix()
    except Exception:
        return str(path)


def _write_trigger_surface(
    *,
    path: Path,
    content: str,
    posture: dict[str, Any],
    surface_title: str,
    surface_id: str,
    generator_command: str,
    comment_style: str,
    force: bool,
) -> None:
    header = _trigger_pack_render_header(
        posture=posture,
        surface_title=surface_title,
        surface_id=surface_id,
        generator_command=generator_command,
        comment_style=comment_style,
    )
    _trigger_pack_write(path, header + content, force=force)


@app.command(name="gen-distribution-pack")
def gen_distribution_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the distribution refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Target one reviewed release-stage profile instead of the whole project bundle"),
    app_id: str | None = typer.Option(None, "--app-id", help="Reverse-DNS application id for generated AppImage/Flatpak metadata"),
    runtime: str = typer.Option("org.freedesktop.Platform", "--runtime", help="Flatpak runtime id"),
    runtime_version: str = typer.Option("24.08", "--runtime-version", help="Flatpak runtime branch/version"),
    sdk: str = typer.Option("org.freedesktop.Sdk", "--sdk", help="Flatpak SDK id"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    distribution_doc: bool = typer.Option(True, "--distribution-doc/--no-distribution-doc", help="Write docs/VHK_DISTRIBUTION.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_DISTRIBUTION_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_distribution_pack.sh"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate package/distribution skeletons from the publish handoff."""

    written = write_distribution_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        force=force,
        distribution_doc=distribution_doc,
        plan_json=plan_json,
        script=script,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK distribution pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["distribution_doc", "plan_json", "script", "distribution_root", "distribution_appimage_script", "distribution_flatpak_manifest", "distribution_flatpak_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-runtime-pack")
def gen_runtime_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the runtime refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Target one reviewed release-stage profile instead of the whole project bundle"),
    app_id: str | None = typer.Option(None, "--app-id", help="Reverse-DNS application id to keep runtime/distribution handoffs aligned"),
    runtime: str = typer.Option("org.freedesktop.Platform", "--runtime", help="Flatpak runtime id used by the distribution handoff this runtime pack extends"),
    runtime_version: str = typer.Option("24.08", "--runtime-version", help="Flatpak runtime branch/version used by the distribution handoff"),
    sdk: str = typer.Option("org.freedesktop.Sdk", "--sdk", help="Flatpak SDK id used by the distribution handoff"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    runtime_doc: bool = typer.Option(True, "--runtime-doc/--no-runtime-doc", help="Write docs/VHK_RUNTIME.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_RUNTIME_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_runtime_pack.sh"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a reviewable Python runtime handoff on top of the distribution pack."""

    written = write_runtime_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        force=force,
        runtime_doc=runtime_doc,
        plan_json=plan_json,
        script=script,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK runtime pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["runtime_doc", "plan_json", "script", "runtime_root", "runtime_requirements", "runtime_build_wheelhouse_script", "runtime_smoke_install_script", "runtime_flatpak_generator_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-runtime-embed-pack")
def gen_runtime_embed_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the runtime-embed refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Target one reviewed release-stage profile instead of the whole project bundle"),
    app_id: str | None = typer.Option(None, "--app-id", help="Reverse-DNS application id to keep runtime/distribution/embed handoffs aligned"),
    runtime: str = typer.Option("org.freedesktop.Platform", "--runtime", help="Flatpak runtime id used by the lower-level distribution handoff"),
    runtime_version: str = typer.Option("24.08", "--runtime-version", help="Flatpak runtime branch/version used by the lower-level distribution handoff"),
    sdk: str = typer.Option("org.freedesktop.Sdk", "--sdk", help="Flatpak SDK id used by the lower-level distribution handoff"),
    python_cmd: str = typer.Option("python", "--python-cmd", help="Python executable to encode into bootstrap helpers"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    embed_doc: bool = typer.Option(True, "--embed-doc/--no-embed-doc", help="Write docs/VHK_RUNTIME_EMBED.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_RUNTIME_EMBED_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_runtime_embed_pack.sh"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate exact-target runtime embedding helpers on top of the runtime pack."""

    written = write_runtime_embed_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        force=force,
        embed_doc=embed_doc,
        plan_json=plan_json,
        script=script,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK runtime embed pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["embed_doc", "plan_json", "script", "embed_root", "embed_bootstrap_script", "embed_native_script", "embed_appimage_script", "embed_flatpak_script", "embed_smoke_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-native-install-pack")
def gen_native_install_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the native-install refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Target one reviewed release-stage profile instead of the whole project bundle"),
    app_id: str | None = typer.Option(None, "--app-id", help="Reverse-DNS application id to keep native/runtime/distribution handoffs aligned"),
    runtime: str = typer.Option("org.freedesktop.Platform", "--runtime", help="Flatpak runtime id used by the lower-level distribution handoff"),
    runtime_version: str = typer.Option("24.08", "--runtime-version", help="Flatpak runtime branch/version used by the lower-level distribution handoff"),
    sdk: str = typer.Option("org.freedesktop.Sdk", "--sdk", help="Flatpak SDK id used by the lower-level distribution handoff"),
    python_cmd: str = typer.Option("python", "--python-cmd", help="Python executable to encode into native install helpers"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host probes for deployment truth / portal routing"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    native_doc: bool = typer.Option(True, "--native-doc/--no-native-doc", help="Write docs/VHK_NATIVE_INSTALL.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_NATIVE_INSTALL_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_native_install_pack.sh"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a conservative XDG-local native install handoff on top of the runtime-embed pack."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [{"message": "session capability check failed", "severity": "warning", "suggestion": str(exc), "used_by": []}]
    host_snapshot = None
    if host_check:
        try:
            strategy = summarize_project_strategy(project, capability_usage=capability_usage, capability_matrix=session_capabilities, capability_issues=session_issues)
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception:
            host_snapshot = None

    written = write_native_install_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        force=force,
        native_doc=native_doc,
        plan_json=plan_json,
        script=script,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK native install pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["native_doc", "plan_json", "script", "native_root", "native_assemble_script", "native_install_script", "native_uninstall_script", "native_smoke_script", "native_launcher"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-service-compose-pack")
def gen_service_compose_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the service-compose refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Target one reviewed release-stage profile instead of the whole project bundle"),
    app_id: str | None = typer.Option(None, "--app-id", help="Reverse-DNS application id to keep service/native/runtime/distribution handoffs aligned"),
    runtime: str = typer.Option("org.freedesktop.Platform", "--runtime", help="Flatpak runtime id used by the lower-level distribution handoff"),
    runtime_version: str = typer.Option("24.08", "--runtime-version", help="Flatpak runtime branch/version used by the lower-level distribution handoff"),
    sdk: str = typer.Option("org.freedesktop.Sdk", "--sdk", help="Flatpak SDK id used by the lower-level distribution handoff"),
    python_cmd: str = typer.Option("python", "--python-cmd", help="Python executable to encode into lower-level runtime/native helpers"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host probes for deployment truth / portal routing"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    service_doc: bool = typer.Option(True, "--service-doc/--no-service-doc", help="Write docs/VHK_SERVICE_COMPOSE.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_SERVICE_COMPOSE_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_service_compose_pack.sh"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a Linux-native session-service composition handoff on top of the native install pack."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [{"message": "session capability check failed", "severity": "warning", "suggestion": str(exc), "used_by": []}]
    host_snapshot = None
    if host_check:
        try:
            strategy = summarize_project_strategy(project, capability_usage=capability_usage, capability_matrix=session_capabilities, capability_issues=session_issues)
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception:
            host_snapshot = None

    written = write_service_compose_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        force=force,
        service_doc=service_doc,
        plan_json=plan_json,
        script=script,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK service composition pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["service_doc", "plan_json", "script", "service_root", "service_install_script", "service_uninstall_script", "service_smoke_script", "service_busd_service", "service_busd_socket", "service_autostart"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-host-rehearsal-pack")
def gen_host_rehearsal_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the host-rehearsal refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Target one reviewed release-stage profile instead of the whole project bundle"),
    app_id: str | None = typer.Option(None, "--app-id", help="Reverse-DNS application id to keep rehearsal/native/service/runtime handoffs aligned"),
    runtime: str = typer.Option("org.freedesktop.Platform", "--runtime", help="Flatpak runtime id used by the lower-level distribution handoff"),
    runtime_version: str = typer.Option("24.08", "--runtime-version", help="Flatpak runtime branch/version used by the lower-level distribution handoff"),
    sdk: str = typer.Option("org.freedesktop.Sdk", "--sdk", help="Flatpak SDK id used by the lower-level distribution handoff"),
    python_cmd: str = typer.Option("python", "--python-cmd", help="Python executable to encode into lower-level runtime/native helpers"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    rehearsal_doc: bool = typer.Option(True, "--rehearsal-doc/--no-rehearsal-doc", help="Write docs/VHK_HOST_REHEARSAL.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_HOST_REHEARSAL_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_host_rehearsal_pack.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host readiness snapshot"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate an end-to-end reviewed-lane rehearsal handoff on top of the service-compose pack."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]
    host_snapshot = None
    if host_check:
        try:
            strategy = summarize_project_strategy(project)
            requirements = [
                dict(item)
                for item in list((strategy.get("host_requirements") or []))
                if isinstance(item, dict)
            ]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            host_snapshot = {"status": "probe_failed", "error": str(exc)}

    written = write_host_rehearsal_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        force=force,
        rehearsal_doc=rehearsal_doc,
        plan_json=plan_json,
        script=script,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK host rehearsal pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["rehearsal_doc", "plan_json", "script", "rehearsal_root", "rehearsal_install_script", "rehearsal_status_script", "rehearsal_logs_script", "rehearsal_uninstall_script", "rehearsal_smoke_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-host-dossier-pack")
def gen_host_dossier_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write the host-dossier refresh script (default: <project>/scripts)"),
    bundle_target_profile: str | None = typer.Option(None, "--bundle-target-profile", help="Target one reviewed release-stage profile instead of the whole project bundle"),
    app_id: str | None = typer.Option(None, "--app-id", help="Reverse-DNS application id to keep dossier/native/rehearsal handoffs aligned"),
    runtime: str = typer.Option("org.freedesktop.Platform", "--runtime", help="Flatpak runtime id used by lower-level distribution handoffs"),
    runtime_version: str = typer.Option("24.08", "--runtime-version", help="Flatpak runtime branch/version used by lower-level distribution handoffs"),
    sdk: str = typer.Option("org.freedesktop.Sdk", "--sdk", help="Flatpak SDK id used by lower-level distribution handoffs"),
    python_cmd: str = typer.Option("python", "--python-cmd", help="Python executable to encode into lower-level runtime/native helpers"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    dossier_doc: bool = typer.Option(True, "--dossier-doc/--no-dossier-doc", help="Write docs/VHK_HOST_DOSSIER.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_HOST_DOSSIER_PLAN.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_host_dossier_pack.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host readiness snapshot"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a shareable installed-host dossier handoff on top of the host-rehearsal pack."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]
    host_snapshot = None
    if host_check:
        try:
            strategy = summarize_project_strategy(project)
            requirements = [
                dict(item)
                for item in list((strategy.get("host_requirements") or []))
                if isinstance(item, dict)
            ]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            host_snapshot = {"status": "probe_failed", "error": str(exc)}

    written = write_host_dossier_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        bundle_target_profile=bundle_target_profile,
        app_id=app_id,
        runtime=runtime,
        runtime_version=runtime_version,
        sdk=sdk,
        python_cmd=python_cmd,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        force=force,
        dossier_doc=dossier_doc,
        plan_json=plan_json,
        script=script,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK host dossier pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["dossier_doc", "plan_json", "script", "dossier_root", "dossier_collect_script", "dossier_archive_script", "dossier_smoke_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)


@app.command(name="gen-trigger-pack")
def gen_trigger_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write the trigger pack root (default: <project>/build/trigger_pack)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide: bool = typer.Option(True, "--guide/--no-guide", help="Write docs/VHK_TRIGGER_SURFACES.md"),
    matrix: bool = typer.Option(True, "--matrix/--no-matrix", help="Write docs/VHK_TRIGGER_MATRIX.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_TRIGGER_PACK.json"),
    script: bool = typer.Option(True, "--script/--no-script", help="Write scripts/vhk_refresh_trigger_pack.sh"),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to embed inside exported configs (default: vhk)"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate a self-contained trigger/remapper export pack for a VHK project."""

    project_dir = project_dir.resolve()
    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]

    plan = build_trigger_pack_plan(
        project_dir,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
    )
    posture = dict(plan.get("support_posture") or {})

    export_root = (out_dir or (project_dir / "build" / "trigger_pack")).expanduser().resolve()
    configs_root = export_root / "configs"
    docs_dir = export_root / "docs"
    script_dir = export_root / "scripts"

    generated_surfaces: list[dict[str, Any]] = []

    def add_surface(*, surface_id: str, surface_title: str, category: str, relative_path: str, comment_style: str, text: str, generator_command: str) -> None:
        target_path = export_root / relative_path
        _write_trigger_surface(
            path=target_path,
            content=text,
            posture=posture,
            surface_title=surface_title,
            surface_id=surface_id,
            generator_command=generator_command,
            comment_style=comment_style,
            force=force,
        )
        generated_surfaces.append({
            "id": surface_id,
            "title": surface_title,
            "category": category,
            "relative_path": relative_path,
            "comment_style": comment_style,
            "generator_command": generator_command,
        })

    if list(getattr(project, "bindings", []) or []):
        add_surface(
            surface_id="wm-native-dispatch",
            surface_title="i3 WM dispatch",
            category="wm",
            relative_path="configs/wm/vhk.i3.conf",
            comment_style="hash",
            text=_generate_wm_bindings(project_dir, project, wm="i3"),
            generator_command=f"vhk gen-wm-config . --wm i3 --out {_trigger_pack_path_for_display(export_root / 'configs' / 'wm' / 'vhk.i3.conf', project_dir)}",
        )
        add_surface(
            surface_id="wm-native-dispatch",
            surface_title="sway WM dispatch",
            category="wm",
            relative_path="configs/wm/vhk.sway.conf",
            comment_style="hash",
            text=_generate_wm_bindings(project_dir, project, wm="sway"),
            generator_command=f"vhk gen-wm-config . --wm sway --out {_trigger_pack_path_for_display(export_root / 'configs' / 'wm' / 'vhk.sway.conf', project_dir)}",
        )
        add_surface(
            surface_id="wm-native-dispatch",
            surface_title="Hyprland WM dispatch",
            category="wm",
            relative_path="configs/wm/vhk.hyprland.conf",
            comment_style="hash",
            text=_generate_wm_bindings(project_dir, project, wm="hyprland"),
            generator_command=f"vhk gen-wm-config . --wm hyprland --out {_trigger_pack_path_for_display(export_root / 'configs' / 'wm' / 'vhk.hyprland.conf', project_dir)}",
        )
        add_surface(
            surface_id="sxhkd-dispatch",
            surface_title="sxhkd hotkey daemon",
            category="x11",
            relative_path="configs/x11/vhk.sxhkdrc",
            comment_style="hash",
            text=_generate_sxhkd_config(project_dir, project, vhk_cmd=vhk_cmd),
            generator_command=f"vhk gen-sxhkd-config . --vhk-cmd {shlex.quote(vhk_cmd)} --out {_trigger_pack_path_for_display(export_root / 'configs' / 'x11' / 'vhk.sxhkdrc', project_dir)}",
        )
        add_surface(
            surface_id="keyd-remap",
            surface_title="keyd remap layer",
            category="remap",
            relative_path="configs/remappers/vhk.keyd.conf",
            comment_style="hash",
            text=_generate_keyd_config(project_dir, project, vhk_cmd=vhk_cmd),
            generator_command=f"vhk gen-keyd-config . --vhk-cmd {shlex.quote(vhk_cmd)} --out {_trigger_pack_path_for_display(export_root / 'configs' / 'remappers' / 'vhk.keyd.conf', project_dir)}",
        )
        add_surface(
            surface_id="kanata-remap",
            surface_title="Kanata remap layer",
            category="remap",
            relative_path="configs/remappers/vhk.kanata.kbd",
            comment_style="hash",
            text=_generate_kanata_config(project_dir, project, vhk_cmd=vhk_cmd),
            generator_command=f"vhk gen-kanata-config . --vhk-cmd {shlex.quote(vhk_cmd)} --out {_trigger_pack_path_for_display(export_root / 'configs' / 'remappers' / 'vhk.kanata.kbd', project_dir)}",
        )
        add_surface(
            surface_id="kmonad-remap",
            surface_title="KMonad remap layer",
            category="remap",
            relative_path="configs/remappers/vhk.kmonad.kbd",
            comment_style="double-semicolon",
            text=_generate_kmonad_config(project_dir, project, vhk_cmd=vhk_cmd),
            generator_command=f"vhk gen-kmonad-config . --vhk-cmd {shlex.quote(vhk_cmd)} --out {_trigger_pack_path_for_display(export_root / 'configs' / 'remappers' / 'vhk.kmonad.kbd', project_dir)}",
        )
        add_surface(
            surface_id="xremap-remap",
            surface_title="xremap app-aware remap layer",
            category="remap",
            relative_path="configs/remappers/vhk.xremap.yml",
            comment_style="hash",
            text=_generate_xremap_config(project_dir, project, vhk_cmd=vhk_cmd),
            generator_command=f"vhk gen-xremap-config . --vhk-cmd {shlex.quote(vhk_cmd)} --out {_trigger_pack_path_for_display(export_root / 'configs' / 'remappers' / 'vhk.xremap.yml', project_dir)}",
        )
        add_surface(
            surface_id="portal-global-shortcuts",
            surface_title="GlobalShortcuts portal catalog",
            category="portal",
            relative_path="configs/portal/vhk.portal-shortcuts.yml",
            comment_style="hash",
            text=_generate_portal_shortcuts_spec(
                project_dir,
                project,
                vhk_cmd=vhk_cmd,
                catalog_path_hint=_trigger_pack_path_for_display(export_root / 'configs' / 'portal' / 'vhk.portal-shortcuts.yml', project_dir),
            ),
            generator_command=f"vhk gen-portal-shortcuts-spec . --vhk-cmd {shlex.quote(vhk_cmd)} --out {_trigger_pack_path_for_display(export_root / 'configs' / 'portal' / 'vhk.portal-shortcuts.yml', project_dir)}",
        )

    annotated, non_file = annotate_trigger_surfaces(plan, generated_surfaces)
    manifest = build_trigger_pack_manifest(
        plan,
        export_root=export_root,
        generated_surfaces=annotated,
        non_file_surfaces=non_file,
        docs_dir=docs_dir,
        script_dir=script_dir,
    )
    written = write_trigger_pack_artifacts(
        export_root=export_root,
        plan=plan,
        manifest=manifest,
        force=force,
        guide=guide,
        matrix=matrix,
        plan_json=plan_json,
        script=script,
        out_dir_display=_trigger_pack_path_for_display(export_root, project_dir),
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK trigger pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    tbl.add_row("root", str(export_root))
    tbl.add_row("configs", str(len(annotated)))
    for key in ["guide", "matrix", "plan_json", "script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")




@app.command(name="gen-setup-pack")
def gen_setup_pack(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write generated docs (default: <project>/docs)"),
    script_dir: Path | None = typer.Option(None, "--script-dir", help="Where to write generated setup scripts (default: <project>/scripts)"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing generated files"),
    guide: bool = typer.Option(True, "--guide/--no-guide", help="Write docs/VHK_SETUP_GUIDE.md"),
    matrix: bool = typer.Option(True, "--matrix/--no-matrix", help="Write docs/VHK_SETUP_MATRIX.md"),
    plan_json: bool = typer.Option(True, "--plan-json/--no-plan-json", help="Write docs/VHK_SETUP_PLAN.json"),
    apply_script: bool = typer.Option(True, "--apply-script/--no-apply-script", help="Write scripts/vhk_apply_setup_recipes.sh"),
    verify_script: bool = typer.Option(True, "--verify-script/--no-verify-script", help="Write scripts/vhk_verify_setup_recipes.sh"),
    package_script: bool = typer.Option(True, "--package-script/--no-package-script", help="Write scripts/vhk_install_toolchain_packages.sh"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    host_check: bool = typer.Option(True, "--host-check/--no-host-check", help="Include current host probes for deployment truth / portal routing"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress success summary"),
):
    """Generate planner-backed setup/install docs and runnable recipe scripts for a VHK project."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]
    host_snapshot = None
    if host_check:
        try:
            strategy = summarize_project_strategy(project, capability_usage=capability_usage, capability_matrix=session_capabilities, capability_issues=session_issues)
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception:
            host_snapshot = None

    written = write_setup_pack(
        project_dir.resolve(),
        out_dir=out_dir,
        script_dir=script_dir,
        force=force,
        guide=guide,
        matrix=matrix,
        plan_json=plan_json,
        apply_script=apply_script,
        verify_script=verify_script,
        package_script=package_script,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
    )

    if quiet:
        return

    tbl = Table(title="Generated VHK setup pack")
    tbl.add_column("Artifact", no_wrap=True)
    tbl.add_column("Path", overflow="fold")
    for key in ["guide", "matrix", "plan_json", "apply_script", "verify_script", "package_script"]:
        path = written.get(key)
        if path:
            tbl.add_row(key, str(path))
    console.print(tbl)
    if session_check:
        console.print(f"[dim]Session issues captured:[/dim] {len(session_issues)}")




@app.command(name="audit-target-claims")
def audit_target_claims(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project directory"),
    claims_file: Path | None = typer.Option(None, "--claims-file", help="Target claims YAML file (default: <project>/docs/VHK_TARGET_CLAIMS.yaml)"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable audit results"),
    fail_on: str = typer.Option("error", "--fail-on", help="Exit non-zero on error or warning"),
    session_check: bool = typer.Option(True, "--session-check/--no-session-check", help="Include current session capability matrix + mismatches"),
    evidence_lane: str | None = typer.Option(None, "--evidence-lane", help="Compare the current host against one explicit release-lane profile id"),
):
    """Audit a project's declared target claims against the current planner output."""

    project = load_project(project_dir)
    capability_usage = _project_capability_usage(project)
    session_capabilities = None
    session_issues: list[dict[str, object]] = []
    host_snapshot = None
    if session_check:
        try:
            session_capabilities = _validation_session_capability_matrix()
            session_issues = _iter_session_capability_mismatches(project, session_capabilities)
            strategy = summarize_project_strategy(project, capability_usage=capability_usage, capability_matrix=session_capabilities, capability_issues=session_issues)
            requirements = [dict(item) for item in list(strategy.get("host_requirements") or []) if isinstance(item, dict)]
            host_snapshot = _validation_live_readiness_snapshot(requirements)
        except Exception as exc:
            session_issues = [
                {
                    "message": "session capability check failed",
                    "severity": "warning",
                    "suggestion": str(exc),
                    "used_by": [],
                }
            ]
            host_snapshot = None

    payload = audit_target_claims_fs(
        project_dir.resolve(),
        claims_file=claims_file,
        capability_usage=capability_usage,
        capability_matrix=session_capabilities,
        capability_issues=session_issues,
        host_snapshot=host_snapshot,
        evidence_lane_profile=evidence_lane,
    )

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        summary = dict(payload.get("summary") or {})
        tbl = Table(title="VHK target claim audit")
        tbl.add_column("Target", no_wrap=True)
        tbl.add_column("Claim", no_wrap=True)
        tbl.add_column("Recommended", no_wrap=True)
        tbl.add_column("Status", no_wrap=True)
        tbl.add_column("Notes", overflow="fold")
        for item in list(payload.get("results") or []):
            notes = [str(x) for x in list(item.get("issues") or []) if str(x)]
            notes.extend(str(x) for x in list(item.get("warnings") or []) if str(x))
            tbl.add_row(
                str(item.get("title") or item.get("target") or "target"),
                str(item.get("claim_level") or "unsupported"),
                str(item.get("recommended_level") or "unsupported"),
                str(item.get("status") or "unknown"),
                " ; ".join(notes) if notes else "",
            )
        console.print(tbl)
        console.print(
            f"[dim]Claims:[/dim] {summary.get('claims', 0)}  "
            f"[dim]Pass:[/dim] {summary.get('pass', 0)}  "
            f"[dim]Warnings:[/dim] {summary.get('warning', 0)}  "
            f"[dim]Failures:[/dim] {summary.get('fail', 0)}"
        )

    fail_on = (fail_on or "error").strip().lower()
    summary = dict(payload.get("summary") or {})
    fail_count = int(summary.get("fail") or 0)
    warning_count = int(summary.get("warning") or 0)
    if fail_count > 0:
        raise typer.Exit(code=1)
    if fail_on == "warning" and warning_count > 0:
        raise typer.Exit(code=1)


@app.command()
def scaffold(

    macro_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Macro YAML file to scaffold"),
    out: Path | None = typer.Option(None, "--out", help="Write scaffolded YAML to this path (default: stdout)"),
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite the input file"),
    check: bool = typer.Option(False, "--check", help="Do not write output; exit non-zero if scaffolding would change the macro"),
    diff: bool = typer.Option(False, "--diff", help="Print a unified diff of the scaffold changes"),
    diff_context: int = typer.Option(3, "--diff-context", min=0, help="Number of context lines to show in unified diffs"),
    insert_stubs: bool = typer.Option(True, "--insert-stubs/--no-insert-stubs", help="Insert disabled TODO steps (non-breaking)"),
    placeholder_needle_path: str = typer.Option("assets/TODO.png", "--placeholder-needle", help="Placeholder needle path for disabled ClickNeedle/WaitForImage stubs"),
    todo_prefix: str = typer.Option("TODO:", "--todo-prefix", help="Prefix used in inserted comments"),
    warn_long_delay_ms: int = typer.Option(1500, "--warn-long-delay-ms", min=0, help="Annotate Delay >= this"),
    warn_delay_before_action_ms: int = typer.Option(600, "--warn-delay-before-action-ms", min=0, help="Annotate Delay before action >= this"),
    warn_low_poll_ms: int = typer.Option(75, "--warn-low-poll-ms", min=1, help="Annotate poll_ms < this"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress summaries"),
):
    """Insert non-breaking TODO scaffolds to upgrade a macro toward robust patterns.

    This command is intentionally conservative: it only adds comments and/or
    inserts disabled steps that authors can enable after filling in details.
    """

    if in_place and out is not None:
        raise typer.BadParameter("Use either --in-place or --out, not both.")
    if check and (in_place or out is not None):
        raise typer.BadParameter("--check cannot be combined with --in-place or --out.")

    raw = macro_path.read_text()
    payload = yaml.safe_load(raw)
    if not isinstance(payload, dict) or "steps" not in payload:
        raise typer.BadParameter("Macro YAML must be a mapping containing a 'steps:' list.")
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise typer.BadParameter("'steps' must be a list.")

    scaffolded, stats = scaffold_steps(
        steps,
        warn_long_delay_ms=warn_long_delay_ms,
        warn_delay_before_action_ms=warn_delay_before_action_ms,
        warn_low_poll_ms=warn_low_poll_ms,
        insert_stubs=insert_stubs,
        placeholder_needle_path=placeholder_needle_path,
        todo_prefix=todo_prefix,
    )

    payload2 = dict(payload)
    payload2["steps"] = scaffolded
    text = yaml.safe_dump(payload2, sort_keys=False)

    changed = (raw != text)

    writing_mode = bool(in_place or (out is not None))
    diff_only_mode = bool(diff and not writing_mode)

    if diff:
        d = _unified_diff(raw, text, fromfile=str(macro_path), tofile=f"{macro_path} (scaffolded)", context=diff_context)
        if d:
            (sys.stdout if diff_only_mode else sys.stderr).write(d)

    if check:
        if not quiet:
            console_err.print(
                f"[dim]# check: {'would change' if changed else 'no changes'} "
                f"(comments_added={stats.comments_added}, stubs_inserted={stats.stubs_inserted})[/dim]"
            )
        raise typer.Exit(code=1 if changed else 0)

    if diff_only_mode:
        if not quiet:
            console_err.print(
                f"[dim]# diff: comments_added={stats.comments_added}, stubs_inserted={stats.stubs_inserted}[/dim]"
            )
        return

    if in_place:
        macro_path.write_text(text)
        if not quiet:
            console.print(
                f"Scaffolded [bold]{macro_path}[/bold] "
                f"(comments_added={stats.comments_added}, stubs_inserted={stats.stubs_inserted})"
            )
        return

    if out is not None:
        out = out.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        if not quiet:
            console.print(
                f"Wrote scaffolded macro: [bold]{out}[/bold] "
                f"(comments_added={stats.comments_added}, stubs_inserted={stats.stubs_inserted})"
            )
        return

    # stdout default
    sys.stdout.write(text)


@app.command(name="scaffold-project")
def scaffold_project(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project folder containing macros/"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Write scaffolded macros into this folder (preserves filenames)"),
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite macro YAML files in-place"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write files; only report what would change"),
    check: bool = typer.Option(False, "--check", help="Do not write output; exit non-zero if any macro would change"),
    diff: bool = typer.Option(False, "--diff", help="Print unified diffs for macros that would change"),
    diff_context: int = typer.Option(3, "--diff-context", min=0, help="Number of context lines to show in unified diffs"),
    insert_stubs: bool = typer.Option(True, "--insert-stubs/--no-insert-stubs", help="Insert disabled TODO steps (non-breaking)"),
    placeholder_needle_path: str = typer.Option("assets/TODO.png", "--placeholder-needle", help="Placeholder needle path for disabled stubs"),
    todo_prefix: str = typer.Option("TODO:", "--todo-prefix", help="Prefix used in inserted comments"),
    warn_long_delay_ms: int = typer.Option(1500, "--warn-long-delay-ms", min=0, help="Annotate Delay >= this"),
    warn_delay_before_action_ms: int = typer.Option(600, "--warn-delay-before-action-ms", min=0, help="Annotate Delay before action >= this"),
    warn_low_poll_ms: int = typer.Option(75, "--warn-low-poll-ms", min=1, help="Annotate poll_ms < this"),
    quiet: bool = typer.Option(False, "--quiet", help="Suppress per-file output"),
):
    """Scaffold every macro in a project (bulk authoring helper)."""

    if in_place and out_dir is not None:
        raise typer.BadParameter("Use either --in-place or --out-dir, not both.")
    if check and (in_place or out_dir is not None or dry_run):
        raise typer.BadParameter("--check cannot be combined with --in-place, --out-dir, or --dry-run.")

    writing_mode = bool(in_place or (out_dir is not None) or dry_run)
    if not writing_mode and not (check or diff):
        raise typer.BadParameter("Choose either --out-dir/--in-place/--dry-run, or use --check/--diff for review.")

    project_dir = project_dir.resolve()
    try:
        _ = load_project(project_dir)
    except Exception as exc:
        raise typer.BadParameter(f"Invalid project: {exc}")

    macros_dir = project_dir / "macros"
    if not macros_dir.exists():
        raise typer.BadParameter("Project has no macros/ directory.")

    macro_files = sorted(list(macros_dir.glob("*.yaml")) + list(macros_dir.glob("*.yml")))
    if not macro_files:
        raise typer.BadParameter("No macro YAML files found under macros/.")

    if out_dir is not None:
        out_dir = out_dir.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

    changed = 0
    skipped = 0
    total_comments = 0
    total_stubs = 0

    for mp in macro_files:
        raw = mp.read_text()
        payload = yaml.safe_load(raw)
        if not isinstance(payload, dict) or "steps" not in payload or not isinstance(payload.get("steps"), list):
            skipped += 1
            if not quiet:
                console_err.print(f"[yellow]Skipping[/yellow] {mp}: not a macro mapping with 'steps:' list")
            continue

        steps = payload.get("steps") or []
        scaffolded, stats = scaffold_steps(
            steps,
            warn_long_delay_ms=warn_long_delay_ms,
            warn_delay_before_action_ms=warn_delay_before_action_ms,
            warn_low_poll_ms=warn_low_poll_ms,
            insert_stubs=insert_stubs,
            placeholder_needle_path=placeholder_needle_path,
            todo_prefix=todo_prefix,
        )
        total_comments += stats.comments_added
        total_stubs += stats.stubs_inserted

        payload2 = dict(payload)
        payload2["steps"] = scaffolded
        text = yaml.safe_dump(payload2, sort_keys=False)

        did_change = (raw != text)
        if did_change:
            changed += 1

        if not writing_mode:
            if diff and did_change:
                d = _unified_diff(raw, text, fromfile=str(mp), tofile=f"{mp} (scaffolded)", context=diff_context)
                if d:
                    sys.stdout.write(d)
            if not quiet:
                console_err.print(f"[dim]{mp.name}: {'would change' if did_change else 'no changes'}[/dim]")
            continue

        if dry_run:
            if not quiet:
                console_err.print(
                    f"[dim]{mp.name}: comments_added={stats.comments_added}, stubs_inserted={stats.stubs_inserted}[/dim]"
                )
            continue

        if in_place:
            mp.write_text(text)
            if not quiet:
                console_err.print(f"Scaffolded {mp} (comments_added={stats.comments_added}, stubs_inserted={stats.stubs_inserted})")
            continue

        assert out_dir is not None
        dst = out_dir / mp.name
        dst.write_text(text)
        if not quiet:
            console_err.print(f"Wrote {dst} (comments_added={stats.comments_added}, stubs_inserted={stats.stubs_inserted})")

    summary = (
        f"Scaffolded {len(macro_files) - skipped} macros"
        + (" (dry-run)" if dry_run else "")
        + f": files_changed={changed}, skipped={skipped}, comments_added={total_comments}, stubs_inserted={total_stubs}"
    )

    if check:
        console_err.print(summary)
        raise typer.Exit(code=1 if changed else 0)

    if not quiet:
        (console_err if not writing_mode else console).print(summary)


@app.command()
def watch_clipboard(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    watcher: str = typer.Argument(..., help="Clipboard watcher name from project.yaml"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many clipboard-change events (useful for testing)"),
):
    """Run a project-defined clipboard watcher loop."""

    project = load_project(project_dir)
    try:
        stats = run_clipboard_watcher(project, watcher, console=console, max_events=max_events)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped clipboard watcher.[/yellow]")
        raise typer.Exit(code=130)

    console.print(
        f"watcher={stats.watcher} events={stats.events_seen} runs={stats.macro_runs} "
        f"skipped_duplicates={stats.skipped_duplicates} skipped_nonmatching={stats.skipped_nonmatching} failures={stats.macro_failures}"
    )




@app.command()
def watch_file(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    watcher: str = typer.Argument(..., help="File watcher name from project.yaml"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many file events (useful for testing)"),
):
    """Run a project-defined file watcher loop."""

    project = load_project(project_dir)
    try:
        stats = run_file_watcher(project, watcher, console=console, max_events=max_events)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped file watcher.[/yellow]")
        raise typer.Exit(code=130)

    console.print(
        f"watcher={stats.watcher} events={stats.events_seen} runs={stats.macro_runs} "
        f"skipped_duplicates={stats.skipped_duplicates} failures={stats.macro_failures}"
    )




@app.command()
def bus_path(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
):
    """Print the resolved IPC event bus socket path for a project."""

    project = load_project(project_dir)
    sock = get_bus_socket_path(project_dir, configured=project.settings.bus_socket)
    console.print(str(sock))


@app.command()
def emit_bus(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    event: str = typer.Argument(..., help="Event name (string)"),
    data_json: str | None = typer.Option(None, "--data", help="Optional JSON payload for the event"),
):
    """Emit an IPC bus event for this project.

    This is the portable "escape hatch": external tools can trigger VHK
    automation by emitting a small local event, rather than spawning VHK
    with complex arguments.
    """

    project = load_project(project_dir)
    sock = get_bus_socket_path(project_dir, configured=project.settings.bus_socket)
    data = None
    if data_json:
        try:
            data = json.loads(data_json)
        except Exception as exc:
            raise typer.BadParameter(f"--data must be valid JSON: {exc}")

    emit_bus_event(sock, event, data)
    console.print(f"Emitted {event} -> {sock}")


@app.command()
def watch_bus(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    watcher: str = typer.Argument(..., help="Bus watcher name from project.yaml"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many bus events (useful for testing)"),
    force: bool = typer.Option(False, "--force", help="Unlink and re-bind the bus socket path (use only if stale)"),
):
    """Run a project-defined IPC bus watcher loop."""

    project = load_project(project_dir)
    try:
        stats = run_bus_watcher(project, watcher, console=console, max_events=max_events, force_unlink=force)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped bus watcher.[/yellow]")
        raise typer.Exit(code=130)

    console.print(
        f"watcher={stats.watcher} events={stats.events_seen} runs={stats.macro_runs} "
        f"skipped_wrong_event={stats.skipped_wrong_event} skipped_nonmatching={stats.skipped_nonmatching} "
        f"skipped_duplicates={stats.skipped_duplicates} failures={stats.macro_failures}"
    )






@app.command()
def busd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    watchers: list[str] = typer.Option([], "--watcher", help="Bus watcher name(s) from project.yaml; default runs all enabled"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many bus events (useful for testing)"),
    force: bool = typer.Option(False, "--force", help="Unlink and re-bind the bus socket path (use only if stale)"),
    reload_event: str | None = typer.Option(None, "--reload-event", help="Bus event name that triggers live reload (default uses settings.bus_reload_event). Set to empty to disable."),
    reload_signals: bool = typer.Option(False, "--reload-signals", help="Enable SIGUSR1/SIGHUP reload (only works in main thread)"),
):
    """Run multiple bus watchers in a single daemon loop.

    A UNIX datagram socket path is single-consumer; this command is the safe
    way to run more than one bus watcher for a project.

    Tip: for hotkey exports, prefer a single watcher with dispatch=true.
    """

    project = load_project(project_dir)
    try:
        stats = run_bus_daemon(
            project,
            watcher_names=(watchers or None),
            console=console,
            max_events=max_events,
            force_unlink=force,
            reload_event=reload_event,
            reload_on_signals=reload_signals,
        )
    except KeyboardInterrupt:
        console.print("[yellow]Stopped bus daemon.[/yellow]")
        raise typer.Exit(code=130)

    console.print(
        f"watchers={len(stats.watchers)} events={stats.events_seen} runs={stats.macro_runs} failures={stats.macro_failures}"
    )


@app.command(name="bus-reload")
def bus_reload_cmd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    event: str | None = typer.Option(None, "--event", help="Reload event name (default uses settings.bus_reload_event)"),
):
    """Emit a reload event on the project bus (for busd live reload).

    This is the bus-based equivalent of sxhkd's SIGUSR1 reload pattern, but works
    even when you don't have (or want) a PID file.
    """

    project = load_project(project_dir)
    ev = event if event is not None else project.settings.bus_reload_event
    ev = (ev or "").strip()
    if not ev:
        console.print("[red]Reload event is disabled (settings.bus_reload_event is empty).[/red]")
        raise typer.Exit(code=2)

    sock_path = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)
    emit_bus_event(sock_path, ev, {"ts": time.time(), "source": "vhk bus-reload"})
    console.print(f"Emitted reload event: {ev} -> {sock_path}")


    

@app.command(name="bus-stop")
def bus_stop_cmd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    event: str | None = typer.Option(None, "--event", help="Stop event name (default uses settings.bus_stop_event)"),
):
    """Emit a stop event on the project bus (for busd shutdown).

    This is useful for scripts/systemd units that want a clean, portable way to
    ask a running `vhk busd` daemon to exit.
    """

    project = load_project(project_dir)
    ev = event if event is not None else project.settings.bus_stop_event
    ev = (ev or "").strip()
    if not ev:
        console.print("[red]Stop event is disabled (settings.bus_stop_event is empty).[/red]")
        raise typer.Exit(code=2)

    sock_path = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)
    emit_bus_event(sock_path, ev, {"ts": time.time(), "source": "vhk bus-stop"})
    console.print(f"Emitted stop event: {ev} -> {sock_path}")


@app.command()
def httpd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host (default localhost only)"),
    port: int = typer.Option(39999, "--port", min=1, max=65535, help="Bind port"),
    token: str | None = typer.Option(None, "--token", help="Optional auth token (also supports env VHK_HTTP_TOKEN)"),
    dispatch_event: str = typer.Option("hotkey", "--dispatch-event", help="Bus event name for /dispatch/<macro>"),
):
    """Run a tiny local HTTP server that emits bus events.

    This is a practical integration point for tools like Node-RED, Stream Deck
    controllers, and "curl from a script" workflows.

    Endpoints
    ---------
    - GET /health
    - POST /emit            JSON: {"event": "name", "data": ...}
    - POST /bus/<event>     Body: JSON or plain text
    - POST /dispatch/<macro> Body: JSON (vars/binding/keys/require_window)

    Security
    --------
    By default the server binds to 127.0.0.1 only. If you bind to 0.0.0.0,
    set --token to prevent untrusted LAN access.
    """

    project = load_project(project_dir)
    sock = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)
    tok = token if token is not None else os.environ.get("VHK_HTTP_TOKEN")

    cfg = HttpdConfig(host=host, port=int(port), token=tok, bus_socket=str(sock), dispatch_event=dispatch_event)
    srv = make_http_server(cfg)

    actual_host, actual_port = srv.server_address[0], srv.server_address[1]
    console.print(f"[dim]HTTPD:[/dim] http://{actual_host}:{actual_port} -> bus {sock}")
    if tok:
        console.print("[dim]Auth:[/dim] token required (Authorization: Bearer <token> or X-VHK-Token)")

    try:
        srv.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped httpd.[/yellow]")
        raise typer.Exit(code=130)
    finally:
        try:
            srv.shutdown()
        except Exception:
            pass
        try:
            srv.server_close()
        except Exception:
            pass


@app.command()
def oscd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host (default localhost only)"),
    port: int = typer.Option(40001, "--port", min=1, max=65535, help="Bind UDP port"),
    token: str | None = typer.Option(None, "--token", help="Optional shared secret (also supports env VHK_OSC_TOKEN)"),
    default_event: str = typer.Option("osc", "--default-event", help="Bus event name for non-/vhk/* messages"),
    dispatch_event: str = typer.Option("hotkey", "--dispatch-event", help="Bus event name for /vhk/dispatch* messages"),
):
    """Run a small OSC (Open Sound Control) UDP server that emits VHK bus events.

    Why
    ---
    OSC is a simple UDP-based control protocol used by many controller tools
    (e.g. Bitfocus Companion / Stream Deck ecosystems, Node-RED OSC nodes,
    TouchOSC). It is a nice fit for "press a button → send a message" workflows.

    Address mapping
    ---------------
    - /vhk/emit <event> <json?>
    - /vhk/emit/<event_path> [<json?>]
    - /vhk/bus/<event_path>  [<json?>]
    - /vhk/dispatch <macro> <vars_json?>
    - /vhk/dispatch/<macro>  [<vars_json?>]

    All other OSC messages emit `--default-event` with payload:
      {"address": "/foo", "args": [...]}

    Token gating
    ------------
    If --token (or env VHK_OSC_TOKEN) is set, the first OSC argument must match
    the token or the message is ignored.
    """

    project = load_project(project_dir)
    sock = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)
    tok = token if token is not None else os.environ.get("VHK_OSC_TOKEN")

    cfg = OscdConfig(
        host=host,
        port=int(port),
        bus_socket=str(sock),
        default_event=default_event,
        dispatch_event=dispatch_event,
        token=tok,
    )
    srv = make_oscd_server(cfg)
    actual_host, actual_port = srv.address
    console.print(f"[dim]OSCD:[/dim] udp://{actual_host}:{actual_port} -> bus {sock}")
    if tok:
        console.print("[dim]Auth:[/dim] token required as first OSC arg")

    try:
        srv.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped oscd.[/yellow]")
        raise typer.Exit(code=130)
    finally:
        try:
            srv.shutdown()
        except Exception:
            pass
        try:
            srv.server_close()
        except Exception:
            pass


@app.command(name="bridge-hypr-custom")
def bridge_hypr_custom(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    hypr_socket2: Path | None = typer.Option(None, "--hypr-socket2", help="Path to Hyprland .socket2.sock (default uses env vars)"),
    bus_event: str = typer.Option("hypr.custom", "--bus-event", help="Bus event name to emit for each Hyprland custom event"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after forwarding this many custom events"),
):
    """Bridge Hyprland socket2 `custom>>...` events into the VHK bus.

    This enables a glue-free workflow where Hyprland config can emit custom
    events (via the `event` dispatcher) and VHK can react using bus_watchers.

    Tip: if the custom payload is JSON (e.g. {"macro":"foo"}), VHK will emit it
    as a dict so dispatch=true bus watchers can use it directly.
    """

    project = load_project(project_dir)
    sock = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)

    hypr = hypr_socket2
    if hypr is None:
        hypr = get_hypr_socket2_path()

    n = bridge_hypr_custom_to_bus(hypr_socket2=hypr, bus_socket=sock, bus_event=bus_event, max_events=max_events)
    console.print(f"Forwarded {n} custom event(s) -> bus '{bus_event}' ({sock})")




@app.command(name="bridge-dbus-signal")
def bridge_dbus_signal(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    match: str = typer.Option(
        ..., "--match", help="dbus-monitor match rule, e.g. interface='org.vhk.Trigger',member='Fire'"
    ),
    bus_event: str = typer.Option("dbus.signal", "--bus-event", help="Bus event name to emit for each matching DBus signal"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after forwarding this many signals"),
):
    """Bridge session-bus DBus signals into the VHK bus.

    This is useful on KDE/KWin where scripts commonly integrate with external
    automation by emitting a DBus signal and letting a helper react.

    Tip: if the first signal argument is a JSON string, VHK will decode it into
    an object automatically and place it in args[0].
    """

    project = load_project(project_dir)
    sock = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)

    n = 0
    try:
        for sig in iter_dbus_signals(match_rule=match):
            payload = {
                "sender": sig.sender,
                "path": sig.path,
                "interface": sig.interface,
                "member": sig.member,
                "args": sig.args,
            }
            emit_bus_event(sock, bus_event, payload)
            n += 1
            if max_events is not None and n >= max_events:
                break
    except KeyboardInterrupt:
        console.print("[yellow]Stopped DBus bridge.[/yellow]")
        raise typer.Exit(code=130)

    console.print(f"Forwarded {n} DBus signal(s) -> bus '{bus_event}' ({sock})")




def _build_portal_shortcut_catalog(project, *, bus_event: str = "hotkey") -> dict[str, Any]:
    """Build a reviewable GlobalShortcuts action catalog from project bindings.

    This keeps the session-bound portal lane explicit: operators can inspect the
    stable shortcut ids, preferred trigger strings, and forwarded bus payload
    before opening the interactive bind UI.
    """

    used: set[str] = set()
    by_id: dict[str, Any] = {}
    specs: list[ShortcutSpec] = []
    shortcuts: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for i, b in enumerate(list(getattr(project, "bindings", []) or [])):
        sid = (getattr(b, "name", None) or f"b{i}_{getattr(b, 'macro', None) or 'macro'}").strip().replace(" ", "_")
        sid = re.sub(r"[^A-Za-z0-9_\-\.]", "_", sid)
        if not sid:
            sid = f"b{i}"
        base = sid
        j = 2
        while sid in used:
            sid = f"{base}_{j}"
            j += 1
        used.add(sid)
        by_id[sid] = b

        desc = getattr(b, "description", None) or getattr(b, "name", None) or getattr(b, "macro", None) or sid
        trig = vhk_hotkey_to_shortcuts_spec(getattr(b, "keys", ""))
        binding_name = getattr(b, "name", None) or getattr(b, "description", None) or getattr(b, "macro", None) or sid
        payload: dict[str, Any] = {
            "macro": getattr(b, "macro", ""),
            "vars": dict(getattr(b, "vars", {}) or {}),
            "binding": binding_name,
            "keys": getattr(b, "keys", ""),
        }
        if getattr(b, "when", None) is not None:
            payload["require_window"] = b.when.model_dump(by_alias=True)

        if not trig:
            skipped.append({
                "shortcut_id": sid,
                "keys": getattr(b, "keys", ""),
                "macro": getattr(b, "macro", ""),
                "description": desc,
                "reason": "could not convert hotkey into a freedesktop shortcuts-spec trigger",
                "dispatch_payload": payload,
            })
            continue

        specs.append(ShortcutSpec(shortcut_id=sid, description=str(desc), preferred_trigger=trig))
        shortcuts.append({
            "shortcut_id": sid,
            "description": str(desc),
            "preferred_trigger": trig,
            "keys": getattr(b, "keys", ""),
            "macro": getattr(b, "macro", ""),
            "binding": binding_name,
            "vars": dict(getattr(b, "vars", {}) or {}),
            "dispatch_payload": payload,
        })
        if getattr(b, "when", None) is not None:
            shortcuts[-1]["require_window"] = b.when.model_dump(by_alias=True)

    return {
        "bus_event": str(bus_event or "hotkey"),
        "specs": specs,
        "bindings_by_id": by_id,
        "shortcuts": shortcuts,
        "skipped_bindings": skipped,
    }


def _generate_portal_shortcuts_spec(
    project_dir: Path,
    project,
    *,
    bus_event: str = "hotkey",
    vhk_cmd: str = "vhk",
    catalog_path_hint: str | None = None,
) -> str:
    """Generate a reviewable GlobalShortcuts session catalog.

    The portal route is session-managed and interactive, but a project can still
    ship a stable action catalog for review, diffing, and install docs.
    """

    lines: list[str] = []
    lines.append(f"# VHK portal shortcut catalog for project: {project.name}")
    lines.append("# Generated by: vhk gen-portal-shortcuts-spec")
    lines.append("#")
    lines.append("# Notes:")
    lines.append("# - GlobalShortcuts uses a session object plus an interactive bind step; this file is a review artifact, not a permanent backend config.")
    lines.append("# - Preferred triggers use the freedesktop shortcuts spec that portal backends expect.")
    lines.append("# - VHK still forwards a normal bus payload per activation, including require_window for scoped bindings.")
    lines.append("")

    catalog = _build_portal_shortcut_catalog(project, bus_event=bus_event)
    bind_cmd = f"{vhk_cmd} portal-hotkeys {shlex.quote(str(project_dir))} --bind --listen --bus-event {shlex.quote(str(bus_event))}"
    bindless_cmd = f"{vhk_cmd} portal-hotkeys {shlex.quote(str(project_dir))} --no-bind --listen --bus-event {shlex.quote(str(bus_event))}"
    payload: dict[str, Any] = {
        "project": {
            "name": str(getattr(project, "name", None) or project_dir.name),
            "root_dir": str(project_dir),
            "desktop_backend": str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "unknown"),
        },
        "portal_interface": "org.freedesktop.portal.GlobalShortcuts",
        "bus_event": str(catalog.get("bus_event") or "hotkey"),
        "bind_command": bind_cmd,
        "bindless_listen_command": bindless_cmd,
        "shortcuts": [dict(item) for item in list(catalog.get("shortcuts") or []) if isinstance(item, dict)],
        "skipped_bindings": [dict(item) for item in list(catalog.get("skipped_bindings") or []) if isinstance(item, dict)],
    }
    if catalog_path_hint:
        catalog_q = shlex.quote(str(catalog_path_hint))
        report_hint = str(Path(str(catalog_path_hint)).with_suffix('.assigned.yml'))
        report_q = shlex.quote(report_hint)
        diff_hint = str(Path(str(report_hint)).with_suffix('.diff.yml'))
        diff_q = shlex.quote(diff_hint)
        state_root_hint = _portal_assignment_state_root_hint(project, project_dir)
        latest_report_hint = f"{state_root_hint}/latest/vhk.portal-shortcuts.assigned.yml"
        latest_diff_hint = f"{state_root_hint}/latest/vhk.portal-shortcuts.assigned.diff.yml"
        payload["catalog_path_hint"] = str(catalog_path_hint)
        payload["assignment_report_path_hint"] = report_hint
        payload["assignment_diff_path_hint"] = diff_hint
        payload["assignment_state_root_hint"] = state_root_hint
        payload["latest_assignment_report_path_hint"] = latest_report_hint
        payload["latest_assignment_diff_path_hint"] = latest_diff_hint
        payload["bind_from_catalog_command"] = f"{vhk_cmd} portal-hotkeys {shlex.quote(str(project_dir))} --catalog {catalog_q} --bind --listen"
        payload["bindless_listen_from_catalog_command"] = f"{vhk_cmd} portal-hotkeys {shlex.quote(str(project_dir))} --catalog {catalog_q} --no-bind --listen"
        payload["bind_and_capture_assignment_command"] = f"{vhk_cmd} portal-hotkeys {shlex.quote(str(project_dir))} --catalog {catalog_q} --bind --assignment-report {report_q} --max-events 1"
        payload["bind_and_capture_assignment_history_command"] = f"{vhk_cmd} portal-hotkeys {shlex.quote(str(project_dir))} --catalog {catalog_q} --bind --assignment-history --max-events 1"
        payload["compare_assignment_report_command_template"] = f"{vhk_cmd} diff-portal-assignment-report <previous-report> {report_q} --out {diff_q} --check"
        history_md_hint = str(Path(str(catalog_path_hint)).with_suffix('.history.md'))
        payload["list_assignment_history_command"] = f"{vhk_cmd} portal-assignment-history {shlex.quote(str(project_dir))} --json"
        payload["list_assignment_history_drift_command"] = f"{vhk_cmd} portal-assignment-history {shlex.quote(str(project_dir))} --json --drift-only"
        payload["list_assignment_history_since_command_template"] = f"{vhk_cmd} portal-assignment-history {shlex.quote(str(project_dir))} --json --since <YYYYMMDDTHHMMSSZ>"
        payload["export_assignment_history_markdown_path_hint"] = history_md_hint
        payload["export_assignment_history_markdown_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --out {shlex.quote(history_md_hint)}"
        payload["export_assignment_history_drift_markdown_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --drift-only --out {shlex.quote(history_md_hint)}"
        payload["export_assignment_history_since_command_template"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --since <YYYYMMDDTHHMMSSZ> --out {shlex.quote(history_md_hint)}"
        history_html_hint = str(Path(str(catalog_path_hint)).with_suffix('.history.html'))
        payload["export_assignment_history_html_path_hint"] = history_html_hint
        payload["export_assignment_history_html_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --format html --out {shlex.quote(history_html_hint)}"
        payload["export_assignment_history_drift_html_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --format html --drift-only --out {shlex.quote(history_html_hint)}"
        payload["export_assignment_history_since_html_command_template"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --format html --since <YYYYMMDDTHHMMSSZ> --out {shlex.quote(history_html_hint)}"
        payload["prune_assignment_history_command_template"] = f"{vhk_cmd} prune-portal-assignment-history {shlex.quote(str(project_dir))} --keep <count> --dry-run"
        payload["prune_assignment_history_older_than_command_template"] = f"{vhk_cmd} prune-portal-assignment-history {shlex.quote(str(project_dir))} --keep <count> --older-than-days <days> --dry-run"
        presets_hint = str(Path(str(catalog_path_hint)).with_suffix('.history-presets.yml'))
        presets_q = shlex.quote(presets_hint)
        local_presets_hint = _portal_assignment_local_presets_path_hint(project, project_dir)
        local_presets_q = shlex.quote(local_presets_hint)
        payload["assignment_presets_path_hint"] = presets_hint
        payload["assignment_local_presets_path_hint"] = local_presets_hint
        payload["generate_assignment_presets_command"] = f"{vhk_cmd} gen-portal-assignment-presets {shlex.quote(str(project_dir))} --out {presets_q}"
        payload["generate_assignment_presets_with_local_template_command"] = f"{vhk_cmd} gen-portal-assignment-presets {shlex.quote(str(project_dir))} --out {presets_q} --local-out {local_presets_q}"
        payload["inspect_assignment_history_recent_drift_preset_command"] = f"{vhk_cmd} inspect-portal-assignment-preset {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset recent-drift --section history --json"
        payload["list_assignment_history_recent_drift_preset_command"] = f"{vhk_cmd} portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset recent-drift --json"
        payload["export_assignment_history_latest_handoff_preset_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset latest-handoff --out {shlex.quote(history_html_hint)}"
        payload["prune_assignment_history_retention_preset_command"] = f"{vhk_cmd} prune-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset retention-30d --dry-run"
        payload["list_assignment_history_recent_drift_layered_preset_command"] = f"{vhk_cmd} portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset-file {local_presets_q} --preset recent-drift --json"
        payload["export_assignment_history_latest_handoff_layered_preset_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset-file {local_presets_q} --preset latest-handoff --out {shlex.quote(history_html_hint)}"
        payload["inspect_assignment_history_recent_drift_layered_preset_command"] = f"{vhk_cmd} inspect-portal-assignment-preset {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset-file {local_presets_q} --preset recent-drift --section history --json"
        payload["prune_assignment_history_retention_layered_preset_command"] = f"{vhk_cmd} prune-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset-file {local_presets_q} --preset retention-30d --dry-run"
    lines.append(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).rstrip())
    return "\n".join(lines) + "\n"


def _slugify_portal_state_component(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(text or "").strip().lower()).strip("-")
    return slug or "project"


def _portal_assignment_history_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_portal_assignment_timestamp(value: datetime) -> str:
    normalized = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return normalized.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _parse_portal_assignment_timestamp(raw: str) -> datetime:
    value = str(raw or "").strip()
    if not value:
        raise ValueError("portal timestamp cannot be empty")
    try:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        pass

    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("portal timestamp must be YYYYMMDDTHHMMSSZ or ISO-8601") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _portal_assignment_history_timestamp() -> str:
    return _format_portal_assignment_timestamp(_portal_assignment_history_now())


def _xdg_state_home_path() -> Path:
    raw = str(os.environ.get("XDG_STATE_HOME") or "").strip()
    if raw:
        candidate = Path(raw).expanduser()
        if candidate.is_absolute():
            return candidate
    return Path.home() / ".local" / "state"


def _xdg_config_home_path() -> Path:
    raw = str(os.environ.get("XDG_CONFIG_HOME") or "").strip()
    if raw:
        candidate = Path(raw).expanduser()
        if candidate.is_absolute():
            return candidate
    return Path.home() / ".config"


def _portal_assignment_state_slug(project: Any, project_dir: Path) -> str:
    return _slugify_portal_state_component(str(getattr(project, "name", None) or project_dir.name or "project"))


def _portal_assignment_state_root(project: Any, project_dir: Path, *, state_root: Path | None = None) -> Path:
    if state_root is not None:
        return state_root.expanduser().resolve()
    return (_xdg_state_home_path() / "vhk" / "portal-shortcuts" / _portal_assignment_state_slug(project, project_dir)).resolve()


def _portal_assignment_state_root_hint(project: Any, project_dir: Path) -> str:
    return f"${{XDG_STATE_HOME:-$HOME/.local/state}}/vhk/portal-shortcuts/{_portal_assignment_state_slug(project, project_dir)}"


def _portal_assignment_local_presets_path(project: Any, project_dir: Path) -> Path:
    return (_xdg_config_home_path() / 'vhk' / 'portal-shortcuts' / _portal_assignment_state_slug(project, project_dir) / 'history-presets.local.yml').resolve()


def _portal_assignment_local_presets_path_hint(project: Any, project_dir: Path) -> str:
    return f"${{XDG_CONFIG_HOME:-$HOME/.config}}/vhk/portal-shortcuts/{_portal_assignment_state_slug(project, project_dir)}/history-presets.local.yml"


def _generate_portal_assignment_presets(
    project_dir: Path,
    project: Any,
    *,
    vhk_cmd: str = "vhk",
    presets_path_hint: str | None = None,
    local_presets_path_hint: str | None = None,
) -> str:
    lines: list[str] = []
    lines.append(f"# VHK portal assignment review presets for project: {project.name}")
    lines.append("# Generated by: vhk gen-portal-assignment-presets")
    lines.append("#")
    lines.append("# Notes:")
    lines.append("# - These saved filter bundles keep portal audit reviews repeatable across history/export/prune commands.")
    lines.append("# - Keep this file project-shared when possible; use a later --preset-file for operator-local overrides.")
    lines.append("# - When multiple --preset-file values are supplied, later files override preset names from earlier files.")
    lines.append("")

    payload: dict[str, Any] = {
        "project": {
            "name": str(getattr(project, "name", None) or project_dir.name),
            "root_dir": str(project_dir),
            "desktop_backend": str(getattr(getattr(project, "settings", None), "desktop_backend", None) or "unknown"),
        },
        "portal_interface": "org.freedesktop.portal.GlobalShortcuts",
        "state_root_hint": _portal_assignment_state_root_hint(project, project_dir),
        "layering": {
            "shared_preset_role": "Project-curated defaults meant for version control and team review.",
            "local_override_role": "Operator-local overrides meant for XDG config paths and per-host review preferences.",
            "merge_rule": "Later --preset-file entries override preset names from earlier files within the same preset section.",
        },
        "history_presets": {
            "latest-review": {
                "description": "Show the newest portal assignment snapshot with its latest drift status.",
                "filters": {
                    "limit": 1,
                    "drift_only": False,
                },
            },
            "recent-drift": {
                "description": "Review only drift-bearing history snapshots from the recent portal audit lane.",
                "filters": {
                    "limit": 20,
                    "drift_only": True,
                },
            },
            "shortcut-drift-template": {
                "description": "Template preset for one shortcut's drift. Replace <shortcut-id> with a real portal shortcut id.",
                "filters": {
                    "limit": 20,
                    "drift_only": True,
                    "changed_shortcuts": ["<shortcut-id>"],
                },
            },
        },
        "export_presets": {
            "latest-handoff": {
                "description": "Render the newest snapshot as a terse HTML handoff without raw state paths.",
                "filters": {
                    "limit": 1,
                    "format": "html",
                    "include_paths": False,
                },
            },
            "recent-drift-markdown": {
                "description": "Export recent drift-bearing snapshots as Markdown with state-file paths for operators.",
                "filters": {
                    "limit": 20,
                    "drift_only": True,
                    "format": "markdown",
                    "include_paths": True,
                },
            },
            "recent-drift-html": {
                "description": "Export recent drift-bearing snapshots as HTML without leaking raw local paths.",
                "filters": {
                    "limit": 20,
                    "drift_only": True,
                    "format": "html",
                    "include_paths": False,
                },
            },
        },
        "prune_presets": {
            "retention-30d": {
                "description": "Protect the newest 10 snapshots, then prune anything older than 30 UTC days.",
                "filters": {
                    "keep": 10,
                    "older_than_days": 30,
                },
            },
            "keep-latest-only": {
                "description": "Retain only the newest snapshot pair for minimal local history.",
                "filters": {
                    "keep": 1,
                },
            },
        },
    }
    if presets_path_hint:
        presets_q = shlex.quote(str(presets_path_hint))
        payload["presets_path_hint"] = str(presets_path_hint)
        payload["inspect_recent_drift_command"] = f"{vhk_cmd} inspect-portal-assignment-preset {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset recent-drift --section history --json"
        payload["list_recent_drift_command"] = f"{vhk_cmd} portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset recent-drift --json"
        payload["export_latest_handoff_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset latest-handoff --out ./build/vhk.portal-shortcuts.history.html"
        payload["prune_retention_command"] = f"{vhk_cmd} prune-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {presets_q} --preset retention-30d --dry-run"
    if local_presets_path_hint:
        local_q = shlex.quote(str(local_presets_path_hint))
        payload["local_presets_path_hint"] = str(local_presets_path_hint)
        if presets_path_hint:
            shared_q = shlex.quote(str(presets_path_hint))
            payload["inspect_recent_drift_layered_command"] = f"{vhk_cmd} inspect-portal-assignment-preset {shlex.quote(str(project_dir))} --preset-file {shared_q} --preset-file {local_q} --preset recent-drift --section history --json"
            payload["list_recent_drift_layered_command"] = f"{vhk_cmd} portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {shared_q} --preset-file {local_q} --preset recent-drift --json"
            payload["export_latest_handoff_layered_command"] = f"{vhk_cmd} export-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {shared_q} --preset-file {local_q} --preset latest-handoff --out ./build/vhk.portal-shortcuts.history.html"
            payload["prune_retention_layered_command"] = f"{vhk_cmd} prune-portal-assignment-history {shlex.quote(str(project_dir))} --preset-file {shared_q} --preset-file {local_q} --preset retention-30d --dry-run"
    lines.append(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).rstrip())
    return "\n".join(lines) + "\n"



def _generate_portal_assignment_local_presets(
    project_dir: Path,
    project: Any,
    *,
    shared_presets_path_hint: str | None = None,
    local_presets_path_hint: str | None = None,
) -> str:
    lines: list[str] = []
    lines.append(f"# VHK local portal assignment preset overrides for project: {project.name}")
    lines.append("# Generated by: vhk gen-portal-assignment-presets --local-out ...")
    lines.append("#")
    lines.append("# Notes:")
    lines.append("# - Keep this file operator-local; it is meant for XDG config paths rather than project checkout roots.")
    lines.append("# - Load it after the shared preset file so matching preset names override shared defaults.")
    lines.append("")
    payload: dict[str, Any] = {
        "project": {
            "name": str(getattr(project, "name", None) or project_dir.name),
            "root_dir": str(project_dir),
        },
        "portal_interface": "org.freedesktop.portal.GlobalShortcuts",
        "layering": {
            "role": "operator-local-overrides",
            "merge_rule": "Later --preset-file entries override earlier presets with the same name.",
            "shared_presets_path_hint": str(shared_presets_path_hint) if shared_presets_path_hint else None,
            "local_presets_path_hint": str(local_presets_path_hint) if local_presets_path_hint else None,
        },
        "history_presets": {
            "recent-drift": {
                "description": "Example local override: shorten the recent drift review to the newest 8 snapshots.",
                "filters": {
                    "limit": 8,
                    "drift_only": True,
                },
            },
        },
        "export_presets": {
            "latest-handoff": {
                "description": "Example local override: keep paths visible in exported handoff HTML on this host.",
                "filters": {
                    "limit": 1,
                    "format": "html",
                    "include_paths": True,
                },
            },
        },
        "prune_presets": {
            "retention-30d": {
                "description": "Example local override: keep more snapshots on this operator host before aging out old history.",
                "filters": {
                    "keep": 20,
                    "older_than_days": 30,
                },
            },
        },
    }
    lines.append(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True).rstrip())
    return "\n".join(lines) + "\n"



def _load_portal_assignment_presets_file(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("portal assignment presets must decode to a mapping")
    normalized: dict[str, Any] = {"path": str(path)}
    for key in ("history_presets", "export_presets", "prune_presets"):
        section = payload.get(key) or {}
        if not isinstance(section, dict):
            raise ValueError(f"portal assignment presets '{key}' must be a mapping")
        normalized_section: dict[str, dict[str, Any]] = {}
        for preset_name, entry in section.items():
            if not isinstance(entry, dict):
                raise ValueError(f"portal assignment preset '{preset_name}' in '{key}' must be a mapping")
            filters = entry.get("filters") or {}
            if not isinstance(filters, dict):
                raise ValueError(f"portal assignment preset '{preset_name}' filters in '{key}' must be a mapping")
            normalized_section[str(preset_name)] = {
                "description": str(entry.get("description") or ""),
                "filters": dict(filters),
                "source_path": str(path),
            }
        normalized[key] = normalized_section
    return normalized



def _load_portal_assignment_presets_files(paths: list[Path]) -> dict[str, Any]:
    if not paths:
        raise ValueError("at least one portal assignment preset file is required")
    normalized: dict[str, Any] = {
        "paths": [str(path) for path in paths],
        "history_presets": {},
        "export_presets": {},
        "prune_presets": {},
    }
    for path in paths:
        loaded = _load_portal_assignment_presets_file(path)
        for key in ("history_presets", "export_presets", "prune_presets"):
            section = dict(loaded.get(key) or {})
            merged_section = dict(normalized.get(key) or {})
            merged_section.update(section)
            normalized[key] = merged_section
    return normalized



def _resolve_portal_assignment_preset(paths: list[Path], *, preset: str, section: str) -> dict[str, Any]:
    loaded = _load_portal_assignment_presets_files(paths)
    section_key = f"{section}_presets"
    section_payload = dict(loaded.get(section_key) or {})
    entry = section_payload.get(str(preset))
    if not isinstance(entry, dict):
        available = ", ".join(sorted(section_payload)) or "<none>"
        raise ValueError(f"portal assignment preset '{preset}' not found in {section_key}; available presets: {available}")

    winner_index: int | None = None
    winner_path: str = str(entry.get("source_path") or "")
    for idx, path in enumerate(paths):
        loaded_path = _load_portal_assignment_presets_file(path)
        section_map = dict(loaded_path.get(section_key) or {})
        if isinstance(section_map.get(str(preset)), dict):
            winner_index = idx
            winner_path = str(path)

    return {
        "paths": [str(path) for path in paths],
        "name": str(preset),
        "section": str(section),
        "section_key": section_key,
        "description": str(entry.get("description") or ""),
        "filters": dict(entry.get("filters") or {}),
        "source_path": winner_path,
        "source_index": winner_index,
        "source_rank": None if winner_index is None else winner_index + 1,
        "merge_rule": "Later --preset-file entries override preset names from earlier files within the same preset section.",
    }



def _require_portal_assignment_preset_pair(preset_files: list[Path] | None, preset: str | None) -> None:
    has_files = bool(list(preset_files or []))
    if has_files != (preset is not None):
        raise typer.BadParameter("--preset-file and --preset must be used together", param_hint="--preset")



def _portal_assignment_history_filters_from_preset(filters: dict[str, Any]) -> dict[str, Any]:
    limit = filters.get("limit", 20)
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("portal history preset 'limit' must be an integer >= 1")
    drift_only = filters.get("drift_only", False)
    if not isinstance(drift_only, bool):
        raise ValueError("portal history preset 'drift_only' must be true or false")
    since_value = filters.get("since")
    until_value = filters.get("until")
    since_dt = _parse_portal_assignment_timestamp(str(since_value)) if since_value else None
    until_dt = _parse_portal_assignment_timestamp(str(until_value)) if until_value else None
    if since_dt is not None and until_dt is not None and since_dt > until_dt:
        raise ValueError("portal history preset requires since <= until")
    changed_shortcuts = filters.get("changed_shortcuts") or []
    if not isinstance(changed_shortcuts, list):
        raise ValueError("portal history preset 'changed_shortcuts' must be a list")
    normalized_changed = [str(item).strip() for item in changed_shortcuts if str(item).strip()]
    return {
        "limit": limit,
        "drift_only": drift_only,
        "since": _format_portal_assignment_timestamp(since_dt) if since_dt is not None else None,
        "until": _format_portal_assignment_timestamp(until_dt) if until_dt is not None else None,
        "changed_shortcuts": normalized_changed,
    }


def _portal_assignment_export_filters_from_preset(filters: dict[str, Any]) -> dict[str, Any]:
    base = _portal_assignment_history_filters_from_preset(filters)
    format_name = str(filters.get("format") or "markdown").strip().lower()
    if format_name not in {"markdown", "html", "auto"}:
        raise ValueError("portal export preset 'format' must be one of: auto, markdown, html")
    include_paths = filters.get("include_paths", True)
    if not isinstance(include_paths, bool):
        raise ValueError("portal export preset 'include_paths' must be true or false")
    base.update({
        "format": format_name,
        "include_paths": include_paths,
    })
    return base


def _portal_assignment_prune_filters_from_preset(filters: dict[str, Any]) -> dict[str, Any]:
    keep = filters.get("keep", 10)
    if not isinstance(keep, int) or keep < 0:
        raise ValueError("portal prune preset 'keep' must be an integer >= 0")
    older_than_days = filters.get("older_than_days")
    if older_than_days is not None and (not isinstance(older_than_days, int) or older_than_days < 0):
        raise ValueError("portal prune preset 'older_than_days' must be an integer >= 0")
    return {
        "keep": keep,
        "older_than_days": older_than_days,
    }


def _portal_assignment_history_paths(
    project: Any,
    project_dir: Path,
    *,
    state_root: Path | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    root = _portal_assignment_state_root(project, project_dir, state_root=state_root)
    stamp = str(timestamp or _portal_assignment_history_timestamp())
    latest_dir = root / "latest"
    history_dir = root / "history"
    return {
        "state_root": root,
        "latest_dir": latest_dir,
        "history_dir": history_dir,
        "latest_report": latest_dir / "vhk.portal-shortcuts.assigned.yml",
        "latest_diff": latest_dir / "vhk.portal-shortcuts.assigned.diff.yml",
        "history_report": history_dir / f"{stamp}.assigned.yml",
        "history_diff": history_dir / f"{stamp}.assigned.diff.yml",
        "timestamp": stamp,
    }


def _persist_portal_assignment_history(
    *,
    project: Any,
    project_dir: Path,
    report_payload: dict[str, Any],
    state_root: Path | None = None,
) -> dict[str, Any]:
    paths = _portal_assignment_history_paths(project, project_dir, state_root=state_root)
    latest_report = Path(paths["latest_report"])
    latest_diff = Path(paths["latest_diff"])
    history_report = Path(paths["history_report"])
    history_diff = Path(paths["history_diff"])

    previous_loaded: dict[str, Any] | None = None
    if latest_report.exists():
        try:
            previous_loaded = _load_portal_assignment_report_file(latest_report)
        except ValueError:
            previous_loaded = None

    history_report.parent.mkdir(parents=True, exist_ok=True)
    latest_report.parent.mkdir(parents=True, exist_ok=True)
    text_payload = yaml.safe_dump(report_payload, sort_keys=False, allow_unicode=True)
    history_report.write_text(text_payload)
    latest_report.write_text(text_payload)

    current_loaded = _load_portal_assignment_report_file(history_report)
    diff_payload: dict[str, Any] | None = None
    if previous_loaded is not None:
        diff_payload = _build_portal_assignment_diff(
            baseline_report=previous_loaded,
            current_report=current_loaded,
        )
        diff_text = yaml.safe_dump(diff_payload, sort_keys=False, allow_unicode=True)
        history_diff.write_text(diff_text)
        latest_diff.write_text(diff_text)

    return {
        "state_root": str(paths["state_root"]),
        "latest_report": str(latest_report),
        "latest_diff": str(latest_diff),
        "history_report": str(history_report),
        "history_diff": str(history_diff),
        "timestamp": str(paths["timestamp"]),
        "diff_payload": diff_payload,
    }


def _load_portal_assignment_diff_file(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("portal assignment diff must decode to a mapping")
    summary = payload.get("summary") or {}
    if not isinstance(summary, dict):
        raise ValueError("portal assignment diff 'summary' must be a mapping")
    return {
        "path": str(path),
        "summary": dict(summary),
        "raw": payload,
    }


def _portal_assignment_snapshot_timestamp(path: Path) -> str:
    name = path.name
    if name.endswith('.assigned.diff.yml'):
        return name[:-len('.assigned.diff.yml')]
    if name.endswith('.assigned.yml'):
        return name[:-len('.assigned.yml')]
    return path.stem


def _portal_assignment_history_report_paths(
    project: Any,
    project_dir: Path,
    *,
    state_root: Path | None = None,
) -> dict[str, Path]:
    paths = _portal_assignment_history_paths(project, project_dir, state_root=state_root)
    return {
        "state_root": Path(paths["state_root"]),
        "latest_report": Path(paths["latest_report"]),
        "latest_diff": Path(paths["latest_diff"]),
        "history_dir": Path(paths["history_dir"]),
    }



def _list_portal_assignment_history(
    *,
    project: Any,
    project_dir: Path,
    state_root: Path | None = None,
    limit: int | None = None,
    drift_only: bool = False,
    since: str | None = None,
    until: str | None = None,
    changed_shortcuts: list[str] | None = None,
    preset_name: str | None = None,
    preset_files: list[Path] | None = None,
    preset_source_path: Path | None = None,
    preset_resolution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved = _portal_assignment_history_report_paths(project, project_dir, state_root=state_root)
    history_dir = resolved["history_dir"]
    latest_report = resolved["latest_report"]
    latest_diff = resolved["latest_diff"]

    since_dt = _parse_portal_assignment_timestamp(since) if since else None
    until_dt = _parse_portal_assignment_timestamp(until) if until else None
    if since_dt is not None and until_dt is not None and since_dt > until_dt:
        raise ValueError("since must be <= until")
    changed_shortcut_filter = sorted({str(item).strip() for item in list(changed_shortcuts or []) if str(item).strip()})

    latest_entry: dict[str, Any] | None = None
    if latest_report.exists():
        loaded = _load_portal_assignment_report_file(latest_report)
        latest_entry = {
            "report_path": str(latest_report),
            "diff_path": str(latest_diff),
            "timestamp": None,
            "summary": dict((loaded.get("raw") or {}).get("summary") or {}),
            "session_handle": str(loaded.get("session_handle") or ""),
            "catalog_source": str((loaded.get("raw") or {}).get("catalog_source") or ""),
            "drift_present": None,
            "changed_shortcuts": [],
        }
        if latest_diff.exists():
            diff_loaded = _load_portal_assignment_diff_file(latest_diff)
            diff_summary = dict(diff_loaded.get("summary") or {})
            latest_entry["drift_present"] = bool(diff_summary.get("drift_present"))
            latest_entry["changed_shortcuts"] = [str(item) for item in list(diff_summary.get("changed_shortcuts") or [])]

    entries: list[dict[str, Any]] = []
    available_history_count = 0
    if history_dir.exists():
        report_paths = sorted(history_dir.glob('*.assigned.yml'), key=lambda item: item.name, reverse=True)
        available_history_count = len(report_paths)
        for report_path in report_paths:
            loaded = _load_portal_assignment_report_file(report_path)
            timestamp = _portal_assignment_snapshot_timestamp(report_path)
            timestamp_dt = _parse_portal_assignment_timestamp(timestamp)
            diff_path = report_path.with_name(f"{timestamp}.assigned.diff.yml")
            drift_present = None
            changed_shortcuts_local: list[str] = []
            if diff_path.exists():
                diff_loaded = _load_portal_assignment_diff_file(diff_path)
                diff_summary = dict(diff_loaded.get("summary") or {})
                drift_present = bool(diff_summary.get("drift_present"))
                changed_shortcuts_local = [str(item) for item in list(diff_summary.get("changed_shortcuts") or [])]
            if since_dt is not None and timestamp_dt < since_dt:
                continue
            if until_dt is not None and timestamp_dt > until_dt:
                continue
            if drift_only and not drift_present:
                continue
            if changed_shortcut_filter and not set(changed_shortcut_filter).intersection(changed_shortcuts_local):
                continue
            entries.append(
                {
                    "timestamp": timestamp,
                    "report_path": str(report_path),
                    "diff_path": str(diff_path),
                    "summary": dict((loaded.get("raw") or {}).get("summary") or {}),
                    "session_handle": str(loaded.get("session_handle") or ""),
                    "catalog_source": str((loaded.get("raw") or {}).get("catalog_source") or ""),
                    "drift_present": drift_present,
                    "changed_shortcuts": changed_shortcuts_local,
                }
            )
            if limit is not None and len(entries) >= limit:
                break

    drift_entries = [str(item.get("timestamp") or "") for item in entries if item.get("drift_present")]
    preset_resolution_payload = dict(preset_resolution or {}) if isinstance(preset_resolution, dict) else None
    if preset_resolution_payload:
        preset_resolution_payload["paths"] = [str(path) for path in list(preset_files or [])] or preset_resolution_payload.get("paths")
        if preset_source_path is not None:
            preset_resolution_payload["source_path"] = str(preset_source_path)
        if preset_name:
            preset_resolution_payload["name"] = str(preset_name)
    return {
        "project": {
            "name": str(getattr(project, "name", None) or project_dir.name),
            "root_dir": str(project_dir),
        },
        "state_root": str(resolved["state_root"]),
        "latest": latest_entry,
        "history": entries,
        "summary": {
            "available_history_count": available_history_count,
            "history_count": len(entries),
            "drift_history_count": len(drift_entries),
            "drift_history_timestamps": drift_entries,
            "latest_report_present": latest_report.exists(),
            "latest_diff_present": latest_diff.exists(),
            "filters": {
                "limit": limit,
                "drift_only": bool(drift_only),
                "since": _format_portal_assignment_timestamp(since_dt) if since_dt is not None else None,
                "until": _format_portal_assignment_timestamp(until_dt) if until_dt is not None else None,
                "changed_shortcuts": changed_shortcut_filter,
                "preset": str(preset_name or "") or None,
                "preset_file": str(list(preset_files or [])[0]) if len(list(preset_files or [])) == 1 else None,
                "preset_files": [str(path) for path in list(preset_files or [])] or None,
                "preset_source_path": str(preset_source_path) if preset_source_path is not None else None,
                "preset_resolution": preset_resolution_payload,
            },
        },
    }


def _portal_assignment_history_markdown(payload: dict[str, Any], *, generated_at: datetime | None = None, include_paths: bool = True) -> str:
    generated_dt = generated_at or _portal_assignment_history_now()
    generated_str = _format_portal_assignment_timestamp(generated_dt)

    project = dict(payload.get("project") or {})
    summary = dict(payload.get("summary") or {})
    filters = dict(summary.get("filters") or {})
    latest = dict(payload.get("latest") or {})
    latest_summary = dict(latest.get("summary") or {})
    history_entries = [dict(item) for item in list(payload.get("history") or []) if isinstance(item, dict)]

    def _md_code(value: Any) -> str:
        text_value = str(value or "")
        return f"`{text_value}`" if text_value else "—"

    def _yes_no_unknown(value: Any) -> str:
        if value is True:
            return "yes"
        if value is False:
            return "no"
        return "unknown"

    lines: list[str] = []
    lines.append(f"# VHK portal assignment history for {project.get('name') or 'project'}")
    lines.append("")
    lines.append(f"- Generated: `{generated_str}`")
    lines.append(f"- Project root: {_md_code(project.get('root_dir'))}")
    lines.append(f"- State root: {_md_code(payload.get('state_root'))}")
    lines.append("")

    lines.append("## Applied filters")
    lines.append("")
    lines.append(f"- Limit: `{filters.get('limit')}`")
    lines.append(f"- Drift only: `{bool(filters.get('drift_only'))}`")
    lines.append(f"- Since: {_md_code(filters.get('since'))}")
    lines.append(f"- Until: {_md_code(filters.get('until'))}")
    changed_filters = [str(item) for item in list(filters.get('changed_shortcuts') or []) if str(item)]
    lines.append(f"- Changed shortcuts filter: {_md_code(', '.join(changed_filters)) if changed_filters else '—'}")
    lines.append("")

    preset_resolution = dict(filters.get('preset_resolution') or {})
    if preset_resolution:
        lines.append("## Preset resolution")
        lines.append("")
        lines.append(f"- Preset: {_md_code(preset_resolution.get('name'))}")
        lines.append(f"- Section: {_md_code(preset_resolution.get('section_key') or preset_resolution.get('section'))}")
        lines.append(f"- Winning preset file: {_md_code(preset_resolution.get('source_path'))}")
        lines.append(f"- Winning layer index: {_md_code(preset_resolution.get('source_rank'))}")
        preset_paths = [str(item) for item in list(preset_resolution.get('paths') or []) if str(item)]
        lines.append(f"- Layered preset files: {_md_code(', '.join(preset_paths)) if preset_paths else '—'}")
        lines.append(f"- Merge rule: {preset_resolution.get('merge_rule') or '—'}")
        lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Matching history snapshots: `{summary.get('history_count', 0)}` of `{summary.get('available_history_count', 0)}` available")
    lines.append(f"- Drift snapshots in selection: `{summary.get('drift_history_count', 0)}`")
    lines.append(f"- Latest report present: `{bool(summary.get('latest_report_present'))}`")
    lines.append(f"- Latest diff present: `{bool(summary.get('latest_diff_present'))}`")
    lines.append("")

    if latest:
        lines.append("## Latest assignment")
        lines.append("")
        lines.append(f"- Requested shortcuts: `{latest_summary.get('requested_count', 0)}`")
        lines.append(f"- Assigned shortcuts: `{latest_summary.get('assigned_count', 0)}`")
        lines.append(f"- Matched assigned shortcuts: `{latest_summary.get('matched_assigned_count', 0)}`")
        lines.append(f"- Drift present: `{_yes_no_unknown(latest.get('drift_present'))}`")
        latest_changed = [str(item) for item in list(latest.get('changed_shortcuts') or []) if str(item)]
        lines.append(f"- Changed shortcuts: {_md_code(', '.join(latest_changed)) if latest_changed else '—'}")
        lines.append(f"- Catalog source: {_md_code(latest.get('catalog_source'))}")
        lines.append(f"- Session handle: {_md_code(latest.get('session_handle'))}")
        if include_paths:
            lines.append(f"- Latest report path: {_md_code(latest.get('report_path'))}")
            lines.append(f"- Latest diff path: {_md_code(latest.get('diff_path'))}")
        lines.append("")

    lines.append("## History snapshots")
    lines.append("")
    if history_entries:
        lines.append("| Timestamp | Matched | Requested | Assigned | Drift | Changed shortcuts |")
        lines.append("| --- | ---: | ---: | ---: | --- | --- |")
        for item in history_entries:
            item_summary = dict(item.get('summary') or {})
            changed = [str(ch) for ch in list(item.get('changed_shortcuts') or []) if str(ch)]
            changed_text = ", ".join(changed) if changed else "—"
            lines.append(
                f"| `{item.get('timestamp') or ''}` | {item_summary.get('matched_assigned_count', 0)} | {item_summary.get('requested_count', 0)} | {item_summary.get('assigned_count', 0)} | {_yes_no_unknown(item.get('drift_present'))} | {changed_text} |"
            )
    else:
        lines.append("No history snapshots matched the current filters.")
    lines.append("")

    drift_entries = [item for item in history_entries if item.get('drift_present')]
    if drift_entries:
        lines.append("## Drift details")
        lines.append("")
        for item in drift_entries:
            changed = [str(ch) for ch in list(item.get('changed_shortcuts') or []) if str(ch)]
            lines.append(f"### `{item.get('timestamp') or ''}`")
            lines.append("")
            lines.append(f"- Changed shortcuts: {_md_code(', '.join(changed)) if changed else '—'}")
            lines.append(f"- Catalog source: {_md_code(item.get('catalog_source'))}")
            lines.append(f"- Session handle: {_md_code(item.get('session_handle'))}")
            if include_paths:
                lines.append(f"- Report path: {_md_code(item.get('report_path'))}")
                lines.append(f"- Diff path: {_md_code(item.get('diff_path'))}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _portal_assignment_history_export_format(out_path: Path | None, format_name: str) -> str:
    value = str(format_name or 'auto').strip().lower()
    if value not in {'auto', 'markdown', 'html'}:
        raise ValueError('format must be one of: auto, markdown, html')
    if value == 'auto':
        suffix = str(getattr(out_path, 'suffix', '') or '').lower()
        if suffix in {'.html', '.htm'}:
            return 'html'
        return 'markdown'
    return value


def _portal_assignment_history_html(payload: dict[str, Any], *, generated_at: datetime | None = None, include_paths: bool = True) -> str:
    generated_dt = generated_at or _portal_assignment_history_now()
    generated_str = _format_portal_assignment_timestamp(generated_dt)

    project = dict(payload.get('project') or {})
    summary = dict(payload.get('summary') or {})
    filters = dict(summary.get('filters') or {})
    latest = dict(payload.get('latest') or {})
    latest_summary = dict(latest.get('summary') or {})
    history_entries = [dict(item) for item in list(payload.get('history') or []) if isinstance(item, dict)]

    def esc(value: Any) -> str:
        return html.escape(str(value or ''))

    def yes_no_unknown(value: Any) -> str:
        if value is True:
            return 'yes'
        if value is False:
            return 'no'
        return 'unknown'

    def code_or_dash(value: Any) -> str:
        text_value = str(value or '').strip()
        return f'<code>{esc(text_value)}</code>' if text_value else '<span class="muted">—</span>'

    def list_or_dash(values: list[str]) -> str:
        clean = [str(item) for item in values if str(item)]
        if not clean:
            return '<span class="muted">—</span>'
        return ', '.join(f'<code>{esc(item)}</code>' for item in clean)

    project_name = str(project.get('name') or 'project')
    changed_filters = [str(item) for item in list(filters.get('changed_shortcuts') or []) if str(item)]
    drift_entries = [item for item in history_entries if item.get('drift_present')]

    parts: list[str] = []
    parts.append('<!DOCTYPE html>')
    parts.append('<html lang="en">')
    parts.append('<head>')
    parts.append('  <meta charset="utf-8">')
    parts.append(f'  <title>{esc(project_name)} portal assignment history</title>')
    parts.append('  <meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append('  <style>')
    parts.append('    :root { color-scheme: light dark; }')
    parts.append('    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 2rem; line-height: 1.45; }')
    parts.append('    h1, h2, h3 { line-height: 1.2; }')
    parts.append('    code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 0.95em; }')
    parts.append('    .muted { opacity: 0.72; }')
    parts.append('    .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: 0.85rem; margin: 1rem 0 1.5rem; }')
    parts.append('    .card { border: 1px solid rgba(127, 127, 127, 0.35); border-radius: 0.8rem; padding: 0.9rem 1rem; }')
    parts.append('    .label { font-size: 0.82rem; opacity: 0.75; text-transform: uppercase; letter-spacing: 0.04em; }')
    parts.append('    .value { font-size: 1.3rem; font-weight: 650; margin-top: 0.2rem; }')
    parts.append('    table { width: 100%; border-collapse: collapse; margin: 1rem 0 1.5rem; }')
    parts.append('    th, td { border: 1px solid rgba(127, 127, 127, 0.25); padding: 0.55rem 0.65rem; text-align: left; vertical-align: top; }')
    parts.append('    th { background: rgba(127, 127, 127, 0.12); }')
    parts.append('    .pill { display: inline-block; border-radius: 999px; padding: 0.1rem 0.55rem; border: 1px solid rgba(127, 127, 127, 0.35); }')
    parts.append('    .pill-yes { background: rgba(220, 38, 38, 0.14); }')
    parts.append('    .pill-no { background: rgba(22, 163, 74, 0.14); }')
    parts.append('    .pill-unknown { background: rgba(127, 127, 127, 0.12); }')
    parts.append('    dl.meta { display: grid; grid-template-columns: max-content 1fr; gap: 0.45rem 0.8rem; }')
    parts.append('    dl.meta dt { font-weight: 650; }')
    parts.append('    ul.clean { padding-left: 1.2rem; }')
    parts.append('  </style>')
    parts.append('</head>')
    parts.append('<body>')
    parts.append(f'  <h1>VHK portal assignment history for {esc(project_name)}</h1>')
    parts.append('  <dl class="meta">')
    parts.append(f'    <dt>Generated</dt><dd><code>{esc(generated_str)}</code></dd>')
    parts.append(f'    <dt>Project root</dt><dd>{code_or_dash(project.get("root_dir"))}</dd>')
    parts.append(f'    <dt>State root</dt><dd>{code_or_dash(payload.get("state_root"))}</dd>')
    parts.append('  </dl>')
    parts.append('  <h2>Applied filters</h2>')
    parts.append('  <ul class="clean">')
    parts.append(f'    <li>Limit: <code>{esc(filters.get("limit"))}</code></li>')
    parts.append(f'    <li>Drift only: <code>{esc(bool(filters.get("drift_only")))}</code></li>')
    parts.append(f'    <li>Since: {code_or_dash(filters.get("since"))}</li>')
    parts.append(f'    <li>Until: {code_or_dash(filters.get("until"))}</li>')
    parts.append(f'    <li>Changed shortcuts filter: {list_or_dash(changed_filters)}</li>')
    parts.append('  </ul>')
    preset_resolution = dict(filters.get('preset_resolution') or {})
    if preset_resolution:
        preset_paths = [str(item) for item in list(preset_resolution.get('paths') or []) if str(item)]
        parts.append('  <h2>Preset resolution</h2>')
        parts.append('  <ul class="clean">')
        parts.append(f'    <li>Preset: {code_or_dash(preset_resolution.get("name"))}</li>')
        parts.append(f'    <li>Section: {code_or_dash(preset_resolution.get("section_key") or preset_resolution.get("section"))}</li>')
        parts.append(f'    <li>Winning preset file: {code_or_dash(preset_resolution.get("source_path"))}</li>')
        parts.append(f'    <li>Winning layer index: {code_or_dash(preset_resolution.get("source_rank"))}</li>')
        parts.append(f'    <li>Layered preset files: {list_or_dash(preset_paths)}</li>')
        parts.append(f'    <li>Merge rule: {esc(preset_resolution.get("merge_rule") or "—")}</li>')
        parts.append('  </ul>')
    parts.append('  <h2>Summary</h2>')
    parts.append('  <div class="summary-grid">')
    summary_cards = [
        ('Matching snapshots', f"{summary.get('history_count', 0)} / {summary.get('available_history_count', 0)}"),
        ('Drift snapshots', summary.get('drift_history_count', 0)),
        ('Latest report present', bool(summary.get('latest_report_present'))),
        ('Latest diff present', bool(summary.get('latest_diff_present'))),
    ]
    for label, value in summary_cards:
        parts.append('    <section class="card">')
        parts.append(f'      <div class="label">{esc(label)}</div>')
        parts.append(f'      <div class="value">{esc(value)}</div>')
        parts.append('    </section>')
    parts.append('  </div>')

    if latest:
        latest_changed = [str(item) for item in list(latest.get('changed_shortcuts') or []) if str(item)]
        parts.append('  <h2>Latest assignment</h2>')
        parts.append('  <ul class="clean">')
        parts.append(f'    <li>Requested shortcuts: <code>{esc(latest_summary.get("requested_count", 0))}</code></li>')
        parts.append(f'    <li>Assigned shortcuts: <code>{esc(latest_summary.get("assigned_count", 0))}</code></li>')
        parts.append(f'    <li>Matched assigned shortcuts: <code>{esc(latest_summary.get("matched_assigned_count", 0))}</code></li>')
        parts.append(f'    <li>Drift present: <span class="pill pill-{esc(yes_no_unknown(latest.get("drift_present")))}">{esc(yes_no_unknown(latest.get("drift_present")))}</span></li>')
        parts.append(f'    <li>Changed shortcuts: {list_or_dash(latest_changed)}</li>')
        parts.append(f'    <li>Catalog source: {code_or_dash(latest.get("catalog_source"))}</li>')
        parts.append(f'    <li>Session handle: {code_or_dash(latest.get("session_handle"))}</li>')
        if include_paths:
            parts.append(f'    <li>Latest report path: {code_or_dash(latest.get("report_path"))}</li>')
            parts.append(f'    <li>Latest diff path: {code_or_dash(latest.get("diff_path"))}</li>')
        parts.append('  </ul>')

    parts.append('  <h2>History snapshots</h2>')
    if history_entries:
        parts.append('  <table>')
        parts.append('    <thead><tr><th>Timestamp</th><th>Matched</th><th>Requested</th><th>Assigned</th><th>Drift</th><th>Changed shortcuts</th></tr></thead>')
        parts.append('    <tbody>')
        for item in history_entries:
            item_summary = dict(item.get('summary') or {})
            changed = [str(ch) for ch in list(item.get('changed_shortcuts') or []) if str(ch)]
            drift_text = yes_no_unknown(item.get('drift_present'))
            parts.append('      <tr>')
            parts.append(f'        <td><code>{esc(item.get("timestamp") or "")}</code></td>')
            parts.append(f'        <td>{esc(item_summary.get("matched_assigned_count", 0))}</td>')
            parts.append(f'        <td>{esc(item_summary.get("requested_count", 0))}</td>')
            parts.append(f'        <td>{esc(item_summary.get("assigned_count", 0))}</td>')
            parts.append(f'        <td><span class="pill pill-{esc(drift_text)}">{esc(drift_text)}</span></td>')
            parts.append(f'        <td>{list_or_dash(changed)}</td>')
            parts.append('      </tr>')
        parts.append('    </tbody>')
        parts.append('  </table>')
    else:
        parts.append('  <p class="muted">No history snapshots matched the current filters.</p>')

    if drift_entries:
        parts.append('  <h2>Drift details</h2>')
        for item in drift_entries:
            changed = [str(ch) for ch in list(item.get('changed_shortcuts') or []) if str(ch)]
            parts.append('  <section class="card">')
            parts.append(f'    <h3><code>{esc(item.get("timestamp") or "")}</code></h3>')
            parts.append('    <ul class="clean">')
            parts.append(f'      <li>Changed shortcuts: {list_or_dash(changed)}</li>')
            parts.append(f'      <li>Catalog source: {code_or_dash(item.get("catalog_source"))}</li>')
            parts.append(f'      <li>Session handle: {code_or_dash(item.get("session_handle"))}</li>')
            if include_paths:
                parts.append(f'      <li>Report path: {code_or_dash(item.get("report_path"))}</li>')
                parts.append(f'      <li>Diff path: {code_or_dash(item.get("diff_path"))}</li>')
            parts.append('    </ul>')
            parts.append('  </section>')

    parts.append('</body>')
    parts.append('</html>')
    return "\n".join(parts) + "\n"


def _prune_portal_assignment_history(
    *,
    project: Any,
    project_dir: Path,
    keep: int,
    state_root: Path | None = None,
    dry_run: bool = False,
    older_than_days: int | None = None,
) -> dict[str, Any]:
    if keep < 0:
        raise ValueError("keep must be >= 0")
    if older_than_days is not None and older_than_days < 0:
        raise ValueError("older_than_days must be >= 0")

    resolved = _portal_assignment_history_report_paths(project, project_dir, state_root=state_root)
    history_dir = resolved["history_dir"]
    report_paths = sorted(history_dir.glob('*.assigned.yml'), key=lambda item: item.name, reverse=True) if history_dir.exists() else []
    protected = report_paths[:keep]
    cutoff_dt = _portal_assignment_history_now() - timedelta(days=older_than_days) if older_than_days is not None else None
    removed: list[Path] = []
    kept: list[Path] = list(protected)
    for report_path in report_paths[keep:]:
        timestamp = _portal_assignment_snapshot_timestamp(report_path)
        timestamp_dt = _parse_portal_assignment_timestamp(timestamp)
        if cutoff_dt is not None and timestamp_dt >= cutoff_dt:
            kept.append(report_path)
            continue
        removed.append(report_path)

    removed_items: list[dict[str, Any]] = []
    for report_path in removed:
        timestamp = _portal_assignment_snapshot_timestamp(report_path)
        diff_path = report_path.with_name(f"{timestamp}.assigned.diff.yml")
        diff_existed = diff_path.exists()
        if not dry_run:
            try:
                report_path.unlink(missing_ok=True)
            except TypeError:
                if report_path.exists():
                    report_path.unlink()
            try:
                diff_path.unlink(missing_ok=True)
            except TypeError:
                if diff_path.exists():
                    diff_path.unlink()
        removed_items.append(
            {
                "timestamp": timestamp,
                "report_path": str(report_path),
                "diff_path": str(diff_path),
                "diff_existed": diff_existed,
            }
        )

    return {
        "project": {
            "name": str(getattr(project, "name", None) or project_dir.name),
            "root_dir": str(project_dir),
        },
        "state_root": str(resolved["state_root"]),
        "dry_run": bool(dry_run),
        "summary": {
            "keep": keep,
            "older_than_days": older_than_days,
            "cutoff_timestamp": _format_portal_assignment_timestamp(cutoff_dt) if cutoff_dt is not None else None,
            "history_count_before": len(report_paths),
            "history_count_after": len(kept) if not dry_run else len(report_paths) - len(removed),
            "protected_count": len(protected),
            "removed_count": len(removed_items),
        },
        "kept_timestamps": [_portal_assignment_snapshot_timestamp(path) for path in kept],
        "removed": removed_items,
    }



def _portal_dispatch_payload_from_binding(binding: Any, *, shortcut_id: str) -> dict[str, Any]:
    binding_name = getattr(binding, "name", None) or getattr(binding, "description", None) or getattr(binding, "macro", None) or shortcut_id
    payload: dict[str, Any] = {
        "macro": getattr(binding, "macro", ""),
        "vars": dict(getattr(binding, "vars", {}) or {}),
        "binding": binding_name,
        "keys": getattr(binding, "keys", ""),
    }
    if getattr(binding, "when", None) is not None:
        payload["require_window"] = binding.when.model_dump(by_alias=True)
    return payload



def _load_portal_shortcut_catalog_file(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("portal catalog must decode to a mapping")

    bus_event = str(payload.get("bus_event") or "hotkey")
    shortcuts = payload.get("shortcuts") or []
    if not isinstance(shortcuts, list):
        raise ValueError("portal catalog 'shortcuts' must be a list")

    specs: list[ShortcutSpec] = []
    dispatch_payloads_by_id: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()

    for index, item in enumerate(shortcuts):
        if not isinstance(item, dict):
            raise ValueError(f"portal catalog shortcut #{index + 1} must be a mapping")
        shortcut_id = str(item.get("shortcut_id") or "").strip()
        if not shortcut_id:
            raise ValueError(f"portal catalog shortcut #{index + 1} is missing shortcut_id")
        if shortcut_id in seen:
            raise ValueError(f"portal catalog contains duplicate shortcut_id: {shortcut_id}")
        seen.add(shortcut_id)

        description = str(item.get("description") or shortcut_id).strip() or shortcut_id
        preferred_trigger_raw = item.get("preferred_trigger")
        preferred_trigger = str(preferred_trigger_raw).strip() if isinstance(preferred_trigger_raw, str) else None
        specs.append(ShortcutSpec(shortcut_id=shortcut_id, description=description, preferred_trigger=preferred_trigger or None))

        dispatch_payload = item.get("dispatch_payload")
        if dispatch_payload is None:
            dispatch_payload = {
                "macro": item.get("macro", ""),
                "vars": dict(item.get("vars") or {}),
                "binding": item.get("binding") or description,
                "keys": item.get("keys") or "",
            }
            if isinstance(item.get("require_window"), dict):
                dispatch_payload["require_window"] = dict(item.get("require_window") or {})
        if not isinstance(dispatch_payload, dict):
            raise ValueError(f"portal catalog shortcut '{shortcut_id}' has a non-mapping dispatch_payload")
        dispatch_payloads_by_id[shortcut_id] = dict(dispatch_payload)

    skipped_bindings = [dict(item) for item in list(payload.get("skipped_bindings") or []) if isinstance(item, dict)]
    return {
        "bus_event": bus_event,
        "specs": specs,
        "dispatch_payloads_by_id": dispatch_payloads_by_id,
        "skipped_bindings": skipped_bindings,
        "catalog_path": str(path),
    }


def _build_portal_assignment_report(
    *,
    project_dir: Path,
    catalog_source: str,
    session_handle: str,
    specs: list[ShortcutSpec],
    assigned_shortcuts: list[BoundShortcut],
    bus_event: str,
) -> dict[str, Any]:
    requested_by_id = {str(spec.shortcut_id): spec for spec in specs if str(spec.shortcut_id)}
    assigned_by_id = {str(item.shortcut_id): item for item in assigned_shortcuts if str(item.shortcut_id)}

    comparison: list[dict[str, Any]] = []
    for shortcut_id, spec in requested_by_id.items():
        assigned = assigned_by_id.get(shortcut_id)
        comparison.append(
            {
                "shortcut_id": shortcut_id,
                "description": spec.description,
                "requested_preferred_trigger": spec.preferred_trigger,
                "assigned_trigger_description": getattr(assigned, "trigger_description", None),
                "status": "assigned" if assigned is not None else "missing-assignment",
            }
        )
    for shortcut_id, assigned in assigned_by_id.items():
        if shortcut_id in requested_by_id:
            continue
        comparison.append(
            {
                "shortcut_id": shortcut_id,
                "description": assigned.description,
                "requested_preferred_trigger": None,
                "assigned_trigger_description": assigned.trigger_description,
                "status": "extra-assigned",
            }
        )

    missing_requested = [item["shortcut_id"] for item in comparison if item["status"] == "missing-assignment"]
    extra_assigned = [item["shortcut_id"] for item in comparison if item["status"] == "extra-assigned"]
    assigned_matches = [item["shortcut_id"] for item in comparison if item["status"] == "assigned"]

    return {
        "project": {"root_dir": str(project_dir)},
        "portal_interface": "org.freedesktop.portal.GlobalShortcuts",
        "catalog_source": str(catalog_source),
        "session_handle": str(session_handle),
        "bus_event": str(bus_event),
        "requested_shortcuts": [
            {
                "shortcut_id": spec.shortcut_id,
                "description": spec.description,
                "preferred_trigger": spec.preferred_trigger,
            }
            for spec in specs
        ],
        "assigned_shortcuts": [
            {
                "shortcut_id": item.shortcut_id,
                "description": item.description,
                "trigger_description": item.trigger_description,
            }
            for item in assigned_shortcuts
        ],
        "comparison": comparison,
        "summary": {
            "requested_count": len(specs),
            "assigned_count": len(assigned_shortcuts),
            "matched_assigned_count": len(assigned_matches),
            "missing_requested": missing_requested,
            "extra_assigned": extra_assigned,
        },
    }





def _load_portal_assignment_report_file(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text())
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("portal assignment report must decode to a mapping")

    requested_shortcuts = payload.get("requested_shortcuts") or []
    assigned_shortcuts = payload.get("assigned_shortcuts") or []
    comparison = payload.get("comparison") or []
    if not isinstance(requested_shortcuts, list):
        raise ValueError("portal assignment report 'requested_shortcuts' must be a list")
    if not isinstance(assigned_shortcuts, list):
        raise ValueError("portal assignment report 'assigned_shortcuts' must be a list")
    if not isinstance(comparison, list):
        raise ValueError("portal assignment report 'comparison' must be a list")

    order: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}

    def ensure(shortcut_id: str) -> dict[str, Any]:
        entry = by_id.get(shortcut_id)
        if entry is None:
            entry = {
                "shortcut_id": shortcut_id,
                "description": None,
                "requested_preferred_trigger": None,
                "assigned_trigger_description": None,
                "status": None,
            }
            by_id[shortcut_id] = entry
            order.append(shortcut_id)
        return entry

    for index, item in enumerate(requested_shortcuts):
        if not isinstance(item, dict):
            raise ValueError(f"portal assignment report requested_shortcuts #{index + 1} must be a mapping")
        shortcut_id = str(item.get("shortcut_id") or "").strip()
        if not shortcut_id:
            raise ValueError(f"portal assignment report requested_shortcuts #{index + 1} is missing shortcut_id")
        entry = ensure(shortcut_id)
        entry["description"] = item.get("description") or entry.get("description")
        entry["requested_preferred_trigger"] = item.get("preferred_trigger")

    for index, item in enumerate(assigned_shortcuts):
        if not isinstance(item, dict):
            raise ValueError(f"portal assignment report assigned_shortcuts #{index + 1} must be a mapping")
        shortcut_id = str(item.get("shortcut_id") or "").strip()
        if not shortcut_id:
            raise ValueError(f"portal assignment report assigned_shortcuts #{index + 1} is missing shortcut_id")
        entry = ensure(shortcut_id)
        entry["description"] = item.get("description") or entry.get("description")
        entry["assigned_trigger_description"] = item.get("trigger_description")
        if entry.get("status") is None:
            entry["status"] = "extra-assigned" if entry.get("requested_preferred_trigger") is None else "assigned"

    for index, item in enumerate(comparison):
        if not isinstance(item, dict):
            raise ValueError(f"portal assignment report comparison #{index + 1} must be a mapping")
        shortcut_id = str(item.get("shortcut_id") or "").strip()
        if not shortcut_id:
            raise ValueError(f"portal assignment report comparison #{index + 1} is missing shortcut_id")
        entry = ensure(shortcut_id)
        entry["description"] = item.get("description") or entry.get("description")
        entry["requested_preferred_trigger"] = item.get("requested_preferred_trigger", entry.get("requested_preferred_trigger"))
        entry["assigned_trigger_description"] = item.get("assigned_trigger_description", entry.get("assigned_trigger_description"))
        entry["status"] = item.get("status") or entry.get("status")

    for shortcut_id, entry in by_id.items():
        if entry.get("status"):
            continue
        if entry.get("assigned_trigger_description"):
            entry["status"] = "extra-assigned" if entry.get("requested_preferred_trigger") is None else "assigned"
        else:
            entry["status"] = "missing-assignment"

    return {
        "path": str(path),
        "project": dict(payload.get("project") or {}) if isinstance(payload.get("project"), dict) else {},
        "session_handle": str(payload.get("session_handle") or ""),
        "bus_event": str(payload.get("bus_event") or "hotkey"),
        "by_id": by_id,
        "order": order,
        "raw": payload,
    }



def _build_portal_assignment_diff(*, baseline_report: dict[str, Any], current_report: dict[str, Any]) -> dict[str, Any]:
    baseline_by_id = dict(baseline_report.get("by_id") or {})
    current_by_id = dict(current_report.get("by_id") or {})

    ordered_ids: list[str] = []
    seen: set[str] = set()
    for shortcut_id in list(baseline_report.get("order") or []) + list(current_report.get("order") or []) + sorted(set(baseline_by_id) | set(current_by_id)):
        sid = str(shortcut_id or "").strip()
        if not sid or sid in seen:
            continue
        seen.add(sid)
        ordered_ids.append(sid)

    comparison: list[dict[str, Any]] = []
    added_shortcuts: list[str] = []
    removed_shortcuts: list[str] = []
    assigned_trigger_changed: list[str] = []
    requested_trigger_changed: list[str] = []
    status_changed: list[str] = []
    description_changed: list[str] = []
    unchanged_shortcuts: list[str] = []

    for shortcut_id in ordered_ids:
        baseline = baseline_by_id.get(shortcut_id)
        current = current_by_id.get(shortcut_id)
        change_kinds: list[str] = []

        if baseline is None:
            change_kinds.append("added-shortcut")
            added_shortcuts.append(shortcut_id)
        elif current is None:
            change_kinds.append("removed-shortcut")
            removed_shortcuts.append(shortcut_id)
        else:
            if (baseline.get("description") or None) != (current.get("description") or None):
                change_kinds.append("description-changed")
                description_changed.append(shortcut_id)
            if (baseline.get("requested_preferred_trigger") or None) != (current.get("requested_preferred_trigger") or None):
                change_kinds.append("requested-trigger-changed")
                requested_trigger_changed.append(shortcut_id)
            if (baseline.get("assigned_trigger_description") or None) != (current.get("assigned_trigger_description") or None):
                change_kinds.append("assigned-trigger-changed")
                assigned_trigger_changed.append(shortcut_id)
            if (baseline.get("status") or None) != (current.get("status") or None):
                change_kinds.append("status-changed")
                status_changed.append(shortcut_id)

        if not change_kinds:
            unchanged_shortcuts.append(shortcut_id)

        comparison.append(
            {
                "shortcut_id": shortcut_id,
                "description": (current or baseline or {}).get("description"),
                "baseline_status": (baseline or {}).get("status"),
                "current_status": (current or {}).get("status"),
                "baseline_requested_preferred_trigger": (baseline or {}).get("requested_preferred_trigger"),
                "current_requested_preferred_trigger": (current or {}).get("requested_preferred_trigger"),
                "baseline_assigned_trigger_description": (baseline or {}).get("assigned_trigger_description"),
                "current_assigned_trigger_description": (current or {}).get("assigned_trigger_description"),
                "change_kinds": change_kinds,
                "drift": bool(change_kinds),
            }
        )

    changed_shortcuts = [item["shortcut_id"] for item in comparison if item["drift"]]

    return {
        "portal_interface": "org.freedesktop.portal.GlobalShortcuts",
        "baseline": {
            "path": str(baseline_report.get("path") or ""),
            "project_root": str(dict(baseline_report.get("project") or {}).get("root_dir") or ""),
            "session_handle": str(baseline_report.get("session_handle") or ""),
            "bus_event": str(baseline_report.get("bus_event") or "hotkey"),
        },
        "current": {
            "path": str(current_report.get("path") or ""),
            "project_root": str(dict(current_report.get("project") or {}).get("root_dir") or ""),
            "session_handle": str(current_report.get("session_handle") or ""),
            "bus_event": str(current_report.get("bus_event") or "hotkey"),
        },
        "comparison": comparison,
        "summary": {
            "shortcut_count": len(comparison),
            "drift_present": bool(changed_shortcuts),
            "changed_shortcuts": changed_shortcuts,
            "unchanged_shortcuts": unchanged_shortcuts,
            "added_shortcuts": added_shortcuts,
            "removed_shortcuts": removed_shortcuts,
            "assigned_trigger_changed": assigned_trigger_changed,
            "requested_trigger_changed": requested_trigger_changed,
            "status_changed": status_changed,
            "description_changed": description_changed,
        },
    }


@app.command(name="portal-hotkeys")
def portal_hotkeys(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    parent_window: str = typer.Option("", "--parent-window", help="Portal parent window identifier (may be required by your DE)"),
    bus_event: str | None = typer.Option(None, "--bus-event", help="Bus event name to emit for each activated shortcut (defaults to the catalog event when --catalog is used)"),
    bind: bool = typer.Option(True, "--bind/--no-bind", help="Bind shortcuts from project bindings (interactive portal UI)"),
    catalog_path: Path | None = typer.Option(None, "--catalog", exists=True, file_okay=True, dir_okay=False, readable=True, help="Load shortcut ids, preferred triggers, and dispatch payloads from a generated portal catalog"),
    assignment_report: Path | None = typer.Option(None, "--assignment-report", help="Write requested-vs-assigned portal shortcut data after bind/list"),
    assignment_history: bool = typer.Option(False, "--assignment-history", help="Persist assignment reports under XDG state (latest + timestamped history)"),
    assignment_state_root: Path | None = typer.Option(None, "--assignment-state-root", help="Override the portal assignment history root (implies --assignment-history)"),
    session_handle: str | None = typer.Option(None, "--session-handle", help="Use an existing portal session handle (skip CreateSession)"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after forwarding this many activations"),
):
    """Use the XDG GlobalShortcuts portal as a Wayland-friendly hotkey source.

    This command creates a GlobalShortcuts session, optionally binds your
    project bindings (interactive), then forwards Activated/Deactivated signals
    into the VHK bus as dispatch-friendly payloads.

    Payload keys match bus dispatch defaults: {macro, vars, binding, keys, require_window}.
    """

    project = load_project(project_dir)
    sock = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)

    sess = session_handle or portal_create_session()
    console.print(f"[dim]GlobalShortcuts session:[/dim] {sess}")

    shortcut_dispatch_by_id: dict[str, dict[str, Any]] = {}
    catalog_source = "project bindings"
    resolved_bus_event = str(bus_event or "hotkey")

    if catalog_path is not None:
        try:
            loaded_catalog = _load_portal_shortcut_catalog_file(catalog_path.expanduser().resolve())
        except ValueError as exc:
            raise typer.BadParameter(str(exc), param_hint="--catalog") from exc
        resolved_bus_event = str(bus_event or loaded_catalog.get("bus_event") or "hotkey")
        specs = list(loaded_catalog.get("specs") or [])
        skipped_bindings = [dict(item) for item in list(loaded_catalog.get("skipped_bindings") or []) if isinstance(item, dict)]
        shortcut_dispatch_by_id = {
            str(shortcut_id): dict(payload)
            for shortcut_id, payload in dict(loaded_catalog.get("dispatch_payloads_by_id") or {}).items()
            if str(shortcut_id) and isinstance(payload, dict)
        }
        catalog_source = f"catalog {catalog_path.expanduser().resolve()}"
    else:
        catalog = _build_portal_shortcut_catalog(project, bus_event=resolved_bus_event)
        specs = list(catalog.get("specs") or [])
        skipped_bindings = [dict(item) for item in list(catalog.get("skipped_bindings") or []) if isinstance(item, dict)]
        shortcut_dispatch_by_id = {
            str(shortcut_id): _portal_dispatch_payload_from_binding(binding, shortcut_id=str(shortcut_id))
            for shortcut_id, binding in dict(catalog.get("bindings_by_id") or {}).items()
            if str(shortcut_id)
        }

    console.print(f"[dim]Shortcut source:[/dim] {catalog_source}")

    assigned_shortcuts: list[BoundShortcut] = []
    if bind:
        if not specs:
            console.print("[yellow]No portal-compatible shortcut specs found; nothing to bind.[/yellow]")
        else:
            assigned_shortcuts = list(portal_bind_shortcuts(sess, specs, parent_window=parent_window) or [])
            console.print(f"[green]Bound {len(specs)} shortcut(s).[/green]")
    if skipped_bindings:
        console.print(f"[yellow]Skipped {len(skipped_bindings)} binding(s) that are unavailable in the active portal shortcut source.[/yellow]")

    history_requested = bool(assignment_history or assignment_state_root is not None)
    if assignment_report is not None or history_requested:
        if assignment_report is not None:
            assignment_report = assignment_report.expanduser().resolve()
        if not assigned_shortcuts:
            assigned_shortcuts = list(portal_list_shortcuts(sess) or [])
        report_payload = _build_portal_assignment_report(
            project_dir=project_dir.resolve(),
            catalog_source=catalog_source,
            session_handle=sess,
            specs=list(specs),
            assigned_shortcuts=assigned_shortcuts,
            bus_event=resolved_bus_event,
        )
        if assignment_report is not None:
            assignment_report.parent.mkdir(parents=True, exist_ok=True)
            assignment_report.write_text(yaml.safe_dump(report_payload, sort_keys=False, allow_unicode=True))
            console.print(f"Wrote portal assignment report: [bold]{assignment_report}[/bold]")
        if history_requested:
            history_info = _persist_portal_assignment_history(
                project=project,
                project_dir=project_dir.resolve(),
                report_payload=report_payload,
                state_root=assignment_state_root,
            )
            console.print(f"Persisted portal assignment history: [bold]{history_info['history_report']}[/bold]")
            console.print(f"Updated latest portal assignment report: [bold]{history_info['latest_report']}[/bold]")
            if history_info.get('diff_payload') is not None:
                console.print(f"Updated latest portal assignment diff: [bold]{history_info['latest_diff']}[/bold]")

    n = 0
    try:
        for sig in iter_portal_shortcut_signals(session_handle=sess):
            dispatch_payload = shortcut_dispatch_by_id.get(sig.shortcut_id)

            payload: dict[str, Any] = {
                "portal_kind": sig.kind,
                "portal_session": sig.session_handle,
                "portal_timestamp": sig.timestamp,
                "shortcut_id": sig.shortcut_id,
            }

            if dispatch_payload is not None:
                payload.update(dict(dispatch_payload))

            emit_bus_event(sock, resolved_bus_event, payload)
            n += 1
            if max_events is not None and n >= max_events:
                break
    except KeyboardInterrupt:
        console.print("[yellow]Stopped portal-hotkeys.[/yellow]")
        raise typer.Exit(code=130)

    console.print(f"Forwarded {n} portal shortcut signal(s) -> bus '{resolved_bus_event}' ({sock})")


@app.command(name="gen-portal-shortcuts-spec")
def gen_portal_shortcuts_spec(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, '--out', help='Write to a file instead of stdout'),
    bus_event: str = typer.Option('hotkey', '--bus-event', help='Bus event name the portal listener will emit for each shortcut activation'),
    vhk_cmd: str = typer.Option('vhk', '--vhk-cmd', help='Command to invoke VHK (default: vhk)'),
):
    """Generate a reviewable GlobalShortcuts portal catalog for project bindings.

    This emits stable shortcut ids, preferred freedesktop trigger strings, and
    the forwarded bus payloads that `vhk portal-hotkeys` will use after the
    desktop portal bind flow is confirmed.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)
    text = _generate_portal_shortcuts_spec(
        project_dir,
        project,
        bus_event=bus_event,
        vhk_cmd=vhk_cmd,
        catalog_path_hint=str(out_path) if out_path else None,
    )
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote portal shortcut catalog: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)



@app.command(name="diff-portal-assignment-report")
def diff_portal_assignment_report(
    baseline_report: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True),
    current_report: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, readable=True),
    out_path: Path | None = typer.Option(None, '--out', help='Write the diff report to a file instead of stdout'),
    check: bool = typer.Option(False, '--check', help='Exit non-zero when any assignment drift is detected'),
):
    """Compare two portal assignment reports and summarize shortcut drift."""

    try:
        baseline_payload = _load_portal_assignment_report_file(baseline_report.expanduser().resolve())
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint='baseline_report') from exc
    try:
        current_payload = _load_portal_assignment_report_file(current_report.expanduser().resolve())
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint='current_report') from exc

    diff_payload = _build_portal_assignment_diff(
        baseline_report=baseline_payload,
        current_report=current_payload,
    )
    text = yaml.safe_dump(diff_payload, sort_keys=False, allow_unicode=True)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote portal assignment diff: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)

    if check and bool(dict(diff_payload.get('summary') or {}).get('drift_present')):
        raise typer.Exit(code=1)


@app.command(name="gen-portal-assignment-presets")
def gen_portal_assignment_presets(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, '--out', help='Write the generated shared preset file to a chosen path'),
    local_out: Path | None = typer.Option(None, '--local-out', help='Optionally write an operator-local override template to a chosen path'),
):
    """Generate reusable portal history/export/prune review presets."""

    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    if out_path is None:
        out_path = project_dir / 'build' / 'vhk.portal-shortcuts.history-presets.yml'
    out_path = out_path.expanduser().resolve()
    local_out_resolved = local_out.expanduser().resolve() if local_out is not None else None
    text = _generate_portal_assignment_presets(
        project_dir,
        project,
        presets_path_hint=str(out_path),
        local_presets_path_hint=str(local_out_resolved or _portal_assignment_local_presets_path(project, project_dir)),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text)
    console.print(f"Wrote portal assignment presets: [bold]{out_path}[/bold]")
    if local_out_resolved is not None:
        local_text = _generate_portal_assignment_local_presets(
            project_dir,
            project,
            shared_presets_path_hint=str(out_path),
            local_presets_path_hint=str(local_out_resolved),
        )
        local_out_resolved.parent.mkdir(parents=True, exist_ok=True)
        local_out_resolved.write_text(local_text)
        console.print(f"Wrote local portal preset overrides: [bold]{local_out_resolved}[/bold]")


@app.command(name="inspect-portal-assignment-preset")
def inspect_portal_assignment_preset(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    preset_file: list[Path] = typer.Option(..., "--preset-file", exists=True, file_okay=True, dir_okay=False, readable=True, help="Load one or more portal preset files; later files override earlier ones"),
    preset: str = typer.Option(..., "--preset", help="Preset name to inspect"),
    section: str = typer.Option("history", "--section", help="Preset section: history, export, or prune"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON instead of YAML"),
):
    """Resolve a portal review preset and show its merged filters plus provenance."""

    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    section_value = str(section or "history").strip().lower()
    if section_value not in {"history", "export", "prune"}:
        raise typer.BadParameter("section must be one of: history, export, prune", param_hint="--section")
    preset_paths_resolved = [item.expanduser().resolve() for item in list(preset_file)]
    try:
        payload = _resolve_portal_assignment_preset(preset_paths_resolved, preset=str(preset), section=section_value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--preset") from exc
    response = {
        "project": {
            "name": str(getattr(project, "name", None) or project_dir.name),
            "root_dir": str(project_dir),
        },
        "preset_resolution": payload,
    }
    if as_json:
        console.print_json(json.dumps(response))
        return
    sys.stdout.write(yaml.safe_dump(response, sort_keys=False, allow_unicode=True))


@app.command(name="portal-assignment-history")
def portal_assignment_history(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    state_root: Path | None = typer.Option(None, "--state-root", help="Override the portal assignment history root"),
    limit: int = typer.Option(20, "--limit", min=1, help="Maximum number of history snapshots to show"),
    drift_only: bool = typer.Option(False, "--drift-only", help="Only include history snapshots whose diff reports drift"),
    since: str | None = typer.Option(None, "--since", help="Only include snapshots at/after this timestamp (YYYYMMDDTHHMMSSZ or ISO-8601)"),
    until: str | None = typer.Option(None, "--until", help="Only include snapshots at/before this timestamp (YYYYMMDDTHHMMSSZ or ISO-8601)"),
    changed_shortcut: list[str] = typer.Option(None, "--changed-shortcut", help="Only include snapshots whose diff mentions this shortcut id; may be repeated"),
    preset_file: list[Path] = typer.Option(None, "--preset-file", exists=True, file_okay=True, dir_okay=False, readable=True, help="Load saved portal history filters from one or more preset files; later files override earlier ones"),
    preset: str | None = typer.Option(None, "--preset", help="History preset name from --preset-file"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON instead of a table"),
):
    """List persisted GlobalShortcuts assignment history under XDG state."""

    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    _require_portal_assignment_preset_pair(preset_file, preset)
    preset_name: str | None = None
    preset_paths_resolved: list[Path] = []
    preset_source_path: Path | None = None
    preset_resolution: dict[str, Any] | None = None
    if preset_file:
        if limit != 20 or drift_only or since is not None or until is not None or list(changed_shortcut or []):
            raise typer.BadParameter("cannot combine --preset with --limit/--drift-only/--since/--until/--changed-shortcut", param_hint="--preset")
        preset_paths_resolved = [item.expanduser().resolve() for item in list(preset_file)]
        try:
            preset_payload = _resolve_portal_assignment_preset(preset_paths_resolved, preset=str(preset), section="history")
            preset_filters = _portal_assignment_history_filters_from_preset(dict(preset_payload.get("filters") or {}))
        except ValueError as exc:
            raise typer.BadParameter(str(exc), param_hint="--preset") from exc
        preset_resolution = dict(preset_payload)
        preset_name = str(preset_payload.get("name") or preset)
        preset_source_raw = str(preset_payload.get("source_path") or "")
        preset_source_path = Path(preset_source_raw) if preset_source_raw else None
        limit = int(preset_filters["limit"])
        drift_only = bool(preset_filters["drift_only"])
        since = str(preset_filters["since"]) if preset_filters.get("since") else None
        until = str(preset_filters["until"]) if preset_filters.get("until") else None
        changed_shortcut = list(preset_filters.get("changed_shortcuts") or [])
    try:
        payload = _list_portal_assignment_history(
            project=project,
            project_dir=project_dir,
            state_root=state_root,
            limit=limit,
            drift_only=drift_only,
            since=since,
            until=until,
            changed_shortcuts=list(changed_shortcut or []),
            preset_name=preset_name,
            preset_files=preset_paths_resolved,
            preset_source_path=preset_source_path,
            preset_resolution=preset_resolution,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint='since/until') from exc

    if as_json:
        console.print_json(json.dumps(payload))
        return

    latest = payload.get("latest") or {}
    summary = payload.get("summary") or {}
    console.print(f"Portal assignment state root: [bold]{payload['state_root']}[/bold]")
    filters = dict(summary.get("filters") or {})
    preset_resolution_payload = dict(filters.get("preset_resolution") or {})
    if preset_resolution_payload:
        console.print(
            "Preset resolution: "
            f"{preset_resolution_payload.get('name')} from {preset_resolution_payload.get('source_path') or '<unknown>'} "
            f"(section={preset_resolution_payload.get('section_key') or preset_resolution_payload.get('section')})"
        )
    if latest:
        latest_summary = dict(latest.get("summary") or {})
        latest_requested = latest_summary.get("requested_count")
        latest_matched = latest_summary.get("matched_assigned_count")
        latest_drift = latest.get("drift_present")
        console.print(
            "Latest report: "
            f"requested={latest_requested} matched={latest_matched} drift={latest_drift if latest_drift is not None else 'unknown'}"
        )

    entries = list(payload.get("history") or [])
    if not entries:
        console.print("[yellow]No portal assignment history snapshots found.[/yellow]")
        return

    table = Table(title=f"Portal assignment history ({len(entries)})")
    table.add_column("Timestamp")
    table.add_column("Matched")
    table.add_column("Requested")
    table.add_column("Assigned")
    table.add_column("Drift")
    table.add_column("Changed")
    for item in entries:
        snapshot_summary = dict(item.get("summary") or {})
        table.add_row(
            str(item.get("timestamp") or ""),
            str(snapshot_summary.get("matched_assigned_count") or 0),
            str(snapshot_summary.get("requested_count") or 0),
            str(snapshot_summary.get("assigned_count") or 0),
            "yes" if item.get("drift_present") else ("no" if item.get("drift_present") is False else "unknown"),
            str(len(list(item.get("changed_shortcuts") or []))),
        )
    console.print(table)


@app.command(name="export-portal-assignment-history")
def export_portal_assignment_history(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, '--out', help='Write the exported report to a file instead of stdout'),
    format_name: str = typer.Option('auto', '--format', help='Export format: auto, markdown, or html'),
    state_root: Path | None = typer.Option(None, '--state-root', help='Override the portal assignment history root'),
    limit: int = typer.Option(20, '--limit', min=1, help='Maximum number of history snapshots to include'),
    drift_only: bool = typer.Option(False, '--drift-only', help='Only include history snapshots whose diff reports drift'),
    since: str | None = typer.Option(None, '--since', help='Only include snapshots at/after this timestamp (YYYYMMDDTHHMMSSZ or ISO-8601)'),
    until: str | None = typer.Option(None, '--until', help='Only include snapshots at/before this timestamp (YYYYMMDDTHHMMSSZ or ISO-8601)'),
    changed_shortcut: list[str] = typer.Option(None, '--changed-shortcut', help='Only include snapshots whose diff mentions this shortcut id; may be repeated'),
    preset_file: list[Path] = typer.Option(None, '--preset-file', exists=True, file_okay=True, dir_okay=False, readable=True, help='Load saved portal export filters from one or more preset files; later files override earlier ones'),
    preset: str | None = typer.Option(None, '--preset', help='Export preset name from --preset-file'),
    include_paths: bool = typer.Option(True, '--include-paths/--no-include-paths', help='Include report/diff paths in the exported output'),
):
    """Render portal assignment history as a shareable Markdown or HTML summary."""

    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    _require_portal_assignment_preset_pair(preset_file, preset)
    preset_name: str | None = None
    preset_paths_resolved: list[Path] = []
    preset_source_path: Path | None = None
    preset_resolution: dict[str, Any] | None = None
    if preset_file:
        if format_name != 'auto' or limit != 20 or drift_only or since is not None or until is not None or list(changed_shortcut or []) or include_paths is not True:
            raise typer.BadParameter("cannot combine --preset with --format/--limit/--drift-only/--since/--until/--changed-shortcut/--include-paths", param_hint="--preset")
        preset_paths_resolved = [item.expanduser().resolve() for item in list(preset_file)]
        try:
            preset_payload = _resolve_portal_assignment_preset(preset_paths_resolved, preset=str(preset), section="export")
            preset_filters = _portal_assignment_export_filters_from_preset(dict(preset_payload.get("filters") or {}))
        except ValueError as exc:
            raise typer.BadParameter(str(exc), param_hint="--preset") from exc
        preset_resolution = dict(preset_payload)
        preset_name = str(preset_payload.get("name") or preset)
        preset_source_raw = str(preset_payload.get("source_path") or "")
        preset_source_path = Path(preset_source_raw) if preset_source_raw else None
        format_name = str(preset_filters["format"])
        include_paths = bool(preset_filters["include_paths"])
        limit = int(preset_filters["limit"])
        drift_only = bool(preset_filters["drift_only"])
        since = str(preset_filters["since"]) if preset_filters.get("since") else None
        until = str(preset_filters["until"]) if preset_filters.get("until") else None
        changed_shortcut = list(preset_filters.get("changed_shortcuts") or [])
    try:
        payload = _list_portal_assignment_history(
            project=project,
            project_dir=project_dir,
            state_root=state_root,
            limit=limit,
            drift_only=drift_only,
            since=since,
            until=until,
            changed_shortcuts=list(changed_shortcut or []),
            preset_name=preset_name,
            preset_files=preset_paths_resolved,
            preset_source_path=preset_source_path,
            preset_resolution=preset_resolution,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint='since/until') from exc

    try:
        resolved_format = _portal_assignment_history_export_format(out_path, format_name)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint='format') from exc

    if resolved_format == 'html':
        text = _portal_assignment_history_html(payload, include_paths=include_paths)
    else:
        text = _portal_assignment_history_markdown(payload, include_paths=include_paths)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote portal assignment history {resolved_format.upper()}: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


@app.command(name="prune-portal-assignment-history")
def prune_portal_assignment_history(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    keep: int = typer.Option(10, "--keep", min=0, help="How many newest history snapshots to protect from pruning"),
    older_than_days: int | None = typer.Option(None, "--older-than-days", min=0, help="Only prune snapshots older than this many UTC days, after protecting newest --keep"),
    state_root: Path | None = typer.Option(None, "--state-root", help="Override the portal assignment history root"),
    preset_file: list[Path] = typer.Option(None, "--preset-file", exists=True, file_okay=True, dir_okay=False, readable=True, help="Load saved portal prune filters from one or more preset files; later files override earlier ones"),
    preset: str | None = typer.Option(None, "--preset", help="Prune preset name from --preset-file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be pruned without deleting files"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON instead of human-readable output"),
):
    """Prune older portal assignment history snapshots under XDG state."""

    project_dir = project_dir.expanduser().resolve()
    project = load_project(project_dir)
    _require_portal_assignment_preset_pair(preset_file, preset)
    preset_paths_resolved: list[Path] = []
    preset_resolution: dict[str, Any] | None = None
    if preset_file:
        if keep != 10 or older_than_days is not None:
            raise typer.BadParameter("cannot combine --preset with --keep/--older-than-days", param_hint="--preset")
        preset_paths_resolved = [item.expanduser().resolve() for item in list(preset_file)]
        try:
            preset_payload = _resolve_portal_assignment_preset(preset_paths_resolved, preset=str(preset), section="prune")
            preset_filters = _portal_assignment_prune_filters_from_preset(dict(preset_payload.get("filters") or {}))
        except ValueError as exc:
            raise typer.BadParameter(str(exc), param_hint="--preset") from exc
        preset_resolution = dict(preset_payload)
        keep = int(preset_filters["keep"])
        older_than_days = preset_filters.get("older_than_days")
    try:
        payload = _prune_portal_assignment_history(
            project=project,
            project_dir=project_dir,
            keep=keep,
            state_root=state_root,
            dry_run=dry_run,
            older_than_days=older_than_days,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint='keep') from exc

    if preset_resolution:
        summary_filters = {
            "preset": str(preset_resolution.get("name") or preset),
            "preset_files": [str(path) for path in preset_paths_resolved] or None,
            "preset_source_path": str(preset_resolution.get("source_path") or "") or None,
            "preset_resolution": preset_resolution,
        }
        payload.setdefault("summary", {})["filters"] = summary_filters
    if as_json:
        console.print_json(json.dumps(payload))
        return

    action = "Would prune" if dry_run else "Pruned"
    console.print(f"Portal assignment state root: [bold]{payload['state_root']}[/bold]")
    if preset_resolution:
        console.print(
            "Preset resolution: "
            f"{preset_resolution.get('name')} from {preset_resolution.get('source_path') or '<unknown>'} "
            f"(section={preset_resolution.get('section_key') or preset_resolution.get('section')})"
        )
    console.print(f"{action} {payload['summary']['removed_count']} history snapshot(s); keeping newest {payload['summary']['keep']}.")
    for item in list(payload.get("removed") or []):
        console.print(f"- {item['timestamp']}: {item['report_path']}")


@app.command()
def watch_window(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    watcher: str = typer.Argument(..., help="Window watcher name from project.yaml"),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many WM events (useful for testing)"),
    poll_ms: int = typer.Option(200, "--poll-ms", min=50, help="Polling interval for unknown compositors"),
):
    """Run a project-defined window watcher loop."""

    project = load_project(project_dir)
    try:
        stats = run_window_watcher(project, watcher, console=console, max_events=max_events, poll_ms=poll_ms)
    except KeyboardInterrupt:
        console.print("[yellow]Stopped window watcher.[/yellow]")
        raise typer.Exit(code=130)

    console.print(
        f"watcher={stats.watcher} events={stats.events_seen} runs={stats.macro_runs} "
        f"skipped_duplicates={stats.skipped_duplicates} skipped_nonmatching={stats.skipped_nonmatching} failures={stats.macro_failures}"
    )


@app.command()
def wm_events(
    kind: list[str] = typer.Option(["focus"], "--kind", "-k", help="Event kind(s) to stream (focus/workspace/title/urgent/new/close/custom). May be repeated."),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many events (useful for debugging)"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON lines (one per event)"),
    with_window: bool = typer.Option(False, "--with-window", help="Attach best-effort window info (may probe compositor)"),
    poll_ms: int = typer.Option(200, "--poll-ms", min=50, help="Polling interval for unknown compositors"),
):
    """Stream raw WM events (debugging helper).

    Similar to `swaymsg -t subscribe` / i3 IPC tools, but unified across
    i3/sway/Hyprland.
    """

    kinds = {k.strip() for k in kind if k and k.strip()} or {"focus"}

    n = 0
    for ev in iter_wm_events(kinds=kinds, poll_ms=poll_ms):
        payload: dict[str, object] = {
            "wm": ev.wm,
            "kind": ev.kind,
            "name": ev.name,
            "data": ev.data,
        }

        if with_window:
            info = None
            try:
                info = window_info_from_event(ev)
            except Exception:
                info = None

            if info is None and ev.kind in {"focus", "workspace"}:
                try:
                    from vhk.system.active_window import get_active_window_info

                    info, _ = get_active_window_info()
                except Exception:
                    info = None

            if info is not None:
                payload["window"] = info

        if as_json:
            sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        else:
            preview = ""
            if isinstance(payload.get("window"), dict):
                w = payload["window"]  # type: ignore[assignment]
                cls = (w.get("class") or w.get("app_id") or "") if isinstance(w, dict) else ""
                title = w.get("title") if isinstance(w, dict) else ""
                preview = f" — {cls} | {title}".rstrip()
            console.print(f"[dim]{payload['wm']}[/dim] {payload['kind']} {payload['name']}{preview}")

        n += 1
        if max_events is not None and n >= max_events:
            break


@app.command()
def record_selectors(
    duration_ms: int = typer.Option(3_000, "--duration-ms", min=100, help="How long to record WM focus/title events"),
    kind: list[str] = typer.Option(
        ["focus"],
        "--kind",
        "-k",
        help="Event kind(s) to observe (focus/workspace/title/urgent). May be repeated.",
    ),
    max_events: int | None = typer.Option(None, "--max-events", min=1, help="Stop after this many captured window samples"),
    include_workspace: bool = typer.Option(False, "--include-workspace", help="Include workspace in the suggested selector when stable"),
    include_title_in_stable: bool = typer.Option(False, "--include-title-in-stable", help="Include title (or title regex) in the stable suggestion (fragile)"),
    include_title_in_exact: bool = typer.Option(True, "--include-title-in-exact/--no-title-in-exact", help="Include title (or title regex) in the exact suggestion"),
    poll_ms: int = typer.Option(200, "--poll-ms", min=50, help="Polling interval for unknown compositors"),
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON payload or print YAML selector snippet"),
):
    """Record active-window observations and suggest a `when:` selector.

    This is a "macro authoring" helper inspired by the classic AutoHotkey
    Window Spy workflow: watch what properties are stable, then bind against
    those rather than guessing.

    Typical usage:

    - Focus the target app/window
    - Run: `vhk record-selectors --duration-ms 3000`
    - Copy the suggested `stable` selector into a `when:` block
    """

    import time

    from vhk.core.selector_suggest import suggest_selectors

    kinds = {k.strip() for k in kind if k and k.strip()} or {"focus"}

    samples: list[dict[str, object]] = []
    seen_sig: set[object] = set()

    start = time.time()
    for ev in iter_wm_events(kinds=kinds, poll_ms=poll_ms):
        info = None
        try:
            info = window_info_from_event(ev)
        except Exception:
            info = None

        if info is None:
            try:
                from vhk.system.active_window import get_active_window_info

                info, _ = get_active_window_info()
            except Exception:
                info = None

        if isinstance(info, dict) and info:
            sig = info.get("id") or info.get("address") or (info.get("class"), info.get("title"))
            if sig not in seen_sig:
                seen_sig.add(sig)
                samples.append(info)

        if max_events is not None and len(samples) >= max_events:
            break
        if (time.time() - start) * 1000.0 >= float(duration_ms):
            break

    # If nothing came through (e.g. no WM), fall back to one active-window sample.
    if not samples:
        try:
            from vhk.system.active_window import get_active_window_info

            info, _ = get_active_window_info()
            if isinstance(info, dict) and info:
                samples = [info]
        except Exception:
            samples = []

    suggestion = suggest_selectors(
        samples,
        include_workspace=include_workspace,
        include_title_in_stable=include_title_in_stable,
        include_title_in_exact=include_title_in_exact,
    )

    stable = suggestion.stable.model_dump(by_alias=True, exclude_none=True)
    exact = suggestion.exact.model_dump(by_alias=True, exclude_none=True)

    payload: dict[str, object] = {
        "kinds": sorted(kinds),
        "duration_ms": duration_ms,
        "samples": samples,
        "suggested": {
            "stable": stable,
            "exact": exact,
            "title_strategy": suggestion.title_strategy,
            "stats": suggestion.stats,
            "notes": [
                "Titles often change; prefer stable unless you truly need a title matcher.",
                "If title_strategy is alternation/prefix, title_regex will be true.",
            ],
        },
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        # Print a minimal YAML snippet ready to paste under a `when:` block.
        sys.stdout.write(yaml.safe_dump(stable, sort_keys=False))


@app.command()
def record_x11(
    duration_ms: int = typer.Option(3_000, "--duration-ms", min=100, help="How long to record global X11 input"),
    out: Path | None = typer.Option(None, "--out", help="Write YAML macro snippet to this file (default: stdout)"),
    min_delay_ms: int = typer.Option(40, "--min-delay-ms", min=0, help="Only emit Delay steps for gaps >= this"),
    smoothing: str = typer.Option("normal", "--smoothing", help="Recorder motion-thinning preset: precise|normal|compact"),
    mouse_sample_ms: int | None = typer.Option(None, "--mouse-sample-ms", min=1, help="Sample mouse motion events to avoid floods (defaults from --smoothing)"),
    mouse_min_delta: int | None = typer.Option(None, "--mouse-min-delta", min=0, help="Record motion immediately when the pointer moves by at least this many pixels (defaults from --smoothing)"),
    drag_min_dist: int = typer.Option(3, "--drag-min-dist", min=0, help="Minimum movement distance to treat press+release as a drag"),
    optimize: bool = typer.Option(False, "--optimize", help="Post-process the recording (merge delays, squash moves, compress chords)"),
    optimize_profile: str = typer.Option("balanced", "--optimize-profile", help="Optimization profile: safe|balanced|aggressive"),
    optimize_cap_delay_ms: int | None = typer.Option(None, "--optimize-cap-delay-ms", min=1, help="Cap Delay steps to this many ms (aggressive defaults to 250ms)"),
    optimize_max_click_hold_ms: int = typer.Option(250, "--optimize-max-click-hold-ms", min=0, help="Only collapse clicks when down->up hold is <= this"),
    optimize_max_keypress_gap_ms: int = typer.Option(250, "--optimize-max-keypress-gap-ms", min=0, help="Only collapse KeyDown/KeyUp when gap is <= this"),
    optimize_max_chord_gap_ms: int = typer.Option(250, "--optimize-max-chord-gap-ms", min=0, help="Only collapse modifier chords when gaps are <= this"),
    optimize_compress_text: bool | None = typer.Option(
        None,
        "--optimize-compress-text/--no-optimize-compress-text",
        help="Collapse plain character Key streams into a TypeText step (auto: on for aggressive)\n",
    ),
    optimize_max_text_gap_ms: int = typer.Option(250, "--optimize-max-text-gap-ms", min=0, help="Only combine text keys when gaps are <= this"),
    optimize_min_text_run: int = typer.Option(3, "--optimize-min-text-run", min=2, help="Minimum number of characters before collapsing into TypeText"),
    optimize_promote_paste_text: bool = typer.Option(False, "--optimize-promote-paste-text/--no-optimize-promote-paste-text", help="Rewrite long literal TypeText runs to backend=clipboard when safe"),
    optimize_paste_text_min_chars: int = typer.Option(80, "--optimize-paste-text-min-chars", min=1, help="Minimum literal text length before promoting to clipboard paste"),
    optimize_segment_paste_text: bool = typer.Option(False, "--optimize-segment-paste-text/--no-optimize-segment-paste-text", help="Split multiline/tab-rich literal TypeText into clipboard chunks plus explicit Tab/Enter keys when safe"),
    optimize_segment_paste_min_chars: int = typer.Option(24, "--optimize-segment-paste-min-chars", min=1, help="Minimum literal chunk length before a structured text segment is promoted to clipboard paste"),
    project_dir: Path | None = typer.Option(
        None,
        "--project",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Write recording into this project (macro YAML under macros/)",
    ),
    macro: str = typer.Option("recording", "--macro", help="Macro name when using --project"),
    register: bool = typer.Option(True, "--register/--no-register", help="Register macro in project.yaml when using --project"),
    append: bool = typer.Option(False, "--append", help="Append steps to an existing macro when using --project"),
    scaffold: bool = typer.Option(False, "--scaffold", help="Insert disabled TODO stubs/comments after recording (best with --project)"),
    quiet: bool = typer.Option(False, "--quiet", help="Do not print an optimization summary to stderr"),
):
    """Record a "lexical" macro on X11 using `xinput test-xi2 --root`.

    This is intentionally a baseline recorder (think: xmacrorec-class). It is
    meant to bootstrap macro authoring; later tooling can convert raw steps into
    robust, wait-driven, selector-aware workflows.

    Notes
    -----
    - Requires an X11 session.
    - In Wayland sessions, xinput typically only sees Xwayland input devices.
    """

    import shutil

    from vhk.system.session import detect_backend

    if detect_backend() != "x11":
        raise typer.BadParameter("record-x11 requires an X11 session (DISPLAY set).")
    if not shutil.which("xinput"):
        raise typer.BadParameter("Missing 'xinput'. Install xinput (X.Org tools) to use record-x11.")
    if not shutil.which("xmodmap"):
        raise typer.BadParameter("Missing 'xmodmap'. Install xmodmap to map keycodes to keysyms.")

    from vhk.system.record_x11 import dump_steps_yaml, record_x11_steps, resolve_recording_smoothing

    try:
        mouse_sample_ms_eff, mouse_min_delta_eff = resolve_recording_smoothing(
            smoothing,
            mouse_sample_ms=mouse_sample_ms,
            mouse_min_delta=mouse_min_delta,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    steps = record_x11_steps(
        duration_ms=duration_ms,
        min_delay_ms=min_delay_ms,
        mouse_sample_ms=mouse_sample_ms_eff,
        mouse_min_delta=mouse_min_delta_eff,
        drag_min_dist=drag_min_dist,
    )

    if optimize:
        optimized, stats = optimize_steps(
            steps,
            profile=optimize_profile,
            cap_delay_ms=optimize_cap_delay_ms,
            max_click_hold_ms=optimize_max_click_hold_ms,
            max_keypress_gap_ms=optimize_max_keypress_gap_ms,
            max_chord_gap_ms=optimize_max_chord_gap_ms,
            compress_text=optimize_compress_text,
            max_text_gap_ms=optimize_max_text_gap_ms,
            min_text_run=optimize_min_text_run,
            promote_paste_text=optimize_promote_paste_text,
            paste_text_min_chars=optimize_paste_text_min_chars,
            segment_paste_text=optimize_segment_paste_text,
            segment_paste_min_chars=optimize_segment_paste_min_chars,
        )
        steps = optimized
        if not quiet:
            console_err.print(
                f"[dim]# optimized recording: {stats.in_steps} -> {stats.out_steps} steps "
                f"(merged_delays={stats.merged_delays}, removed_mouse_moves={stats.removed_mouse_moves}, "
                f"compressed_clicks={stats.compressed_clicks}, compressed_keys={stats.compressed_key_presses}, "
                f"compressed_chords={stats.compressed_chords}, compressed_text_runs={stats.compressed_text_runs}, promoted_paste_texts={stats.promoted_paste_texts}, segmented_paste_texts={stats.segmented_paste_texts})[/dim]"
            )

    if scaffold:
        steps, sc_stats = scaffold_steps(steps, insert_stubs=True)
        if not quiet:
            console_err.print(
                f"[dim]# scaffolded recording: {sc_stats.in_steps} -> {sc_stats.out_steps} steps "
                f"(comments_added={sc_stats.comments_added}, stubs_inserted={sc_stats.stubs_inserted})[/dim]"
            )

    if project_dir is not None:
        if out is not None:
            raise typer.BadParameter("--out cannot be combined with --project (project recording writes into the project).")
        from vhk.project.macro_files import write_macro_steps

        res = write_macro_steps(
            project_dir,
            macro_name=macro,
            steps=steps,
            register=register,
            append=append,
        )
        if not quiet:
            try:
                rel = res.macro_path.relative_to(project_dir.resolve())
            except Exception:
                rel = res.macro_path
            msg = f"Wrote macro: [bold]{rel}[/bold]"
            if res.appended:
                msg += " (appended)"
            console.print(msg)
        return

    text = dump_steps_yaml(steps, out_path=out)
    if out is None:
        sys.stdout.write(text)



@app.command()
def optimize(
    macro_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Macro YAML file to optimize"),
    out: Path | None = typer.Option(None, "--out", help="Write optimized YAML to this path (default: stdout)") ,
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite the input file"),
    check: bool = typer.Option(False, "--check", help="Do not write output; exit non-zero if the macro would change"),
    diff: bool = typer.Option(False, "--diff", help="Print a unified diff of the changes (like code formatters)"),
    diff_context: int = typer.Option(3, "--diff-context", min=0, help="Number of context lines to show in unified diffs"),
    profile: str = typer.Option("balanced", "--profile", help="safe|balanced|aggressive"),
    cap_delay_ms: int | None = typer.Option(None, "--cap-delay-ms", min=1, help="Cap individual Delay steps to this many ms"),
    max_click_hold_ms: int = typer.Option(250, "--max-click-hold-ms", min=0, help="Only collapse clicks when down->up hold is <= this"),
    max_keypress_gap_ms: int = typer.Option(250, "--max-keypress-gap-ms", min=0, help="Only collapse KeyDown/KeyUp when gap is <= this"),
    max_chord_gap_ms: int = typer.Option(250, "--max-chord-gap-ms", min=0, help="Only collapse modifier chords when gaps are <= this"),
    compress_text: bool | None = typer.Option(
        None,
        "--compress-text/--no-compress-text",
        help="Collapse plain character Key streams into a TypeText step (auto: on for aggressive)",
    ),
    max_text_gap_ms: int = typer.Option(250, "--max-text-gap-ms", min=0, help="Only combine text keys when gaps are <= this"),
    min_text_run: int = typer.Option(3, "--min-text-run", min=2, help="Minimum number of characters before collapsing into TypeText"),
    promote_paste_text: bool = typer.Option(False, "--promote-paste-text/--no-promote-paste-text", help="Rewrite long literal TypeText steps to backend=clipboard when safe"),
    paste_text_min_chars: int = typer.Option(80, "--paste-text-min-chars", min=1, help="Minimum literal text length before promoting to clipboard paste"),
    segment_paste_text: bool = typer.Option(False, "--segment-paste-text/--no-segment-paste-text", help="Split multiline/tab-rich literal TypeText into clipboard chunks plus explicit Tab/Enter keys when safe"),
    segment_paste_min_chars: int = typer.Option(24, "--segment-paste-min-chars", min=1, help="Minimum literal chunk length before a structured text segment is promoted to clipboard paste"),
    quiet: bool = typer.Option(False, "--quiet", help="Do not print a summary to stderr"),
):
    """Optimize a macro YAML file (post-process recordings).

    See `docs/OPTIMIZE_MACROS.md` for details and examples.
    """

    if in_place and out is not None:
        raise typer.BadParameter("Use either --in-place or --out, not both.")
    if check and (in_place or out is not None):
        raise typer.BadParameter("--check cannot be combined with --in-place or --out.")

    raw = macro_path.read_text()
    payload = yaml.safe_load(raw)
    if not isinstance(payload, dict) or "steps" not in payload:
        raise typer.BadParameter("Macro YAML must be a mapping containing a 'steps:' list.")
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise typer.BadParameter("'steps' must be a list.")

    optimized, stats = optimize_steps(
        steps,
        profile=profile,
        cap_delay_ms=cap_delay_ms,
        max_click_hold_ms=max_click_hold_ms,
        max_keypress_gap_ms=max_keypress_gap_ms,
        max_chord_gap_ms=max_chord_gap_ms,
        compress_text=compress_text,
        max_text_gap_ms=max_text_gap_ms,
        min_text_run=min_text_run,
        promote_paste_text=promote_paste_text,
        paste_text_min_chars=paste_text_min_chars,
        segment_paste_text=segment_paste_text,
        segment_paste_min_chars=segment_paste_min_chars,
    )

    payload2 = dict(payload)
    payload2["steps"] = optimized
    text = yaml.safe_dump(payload2, sort_keys=False)

    changed = (raw != text)

    writing_mode = bool(in_place or (out is not None))
    diff_only_mode = bool(diff and not writing_mode)

    if diff:
        d = _unified_diff(raw, text, fromfile=str(macro_path), tofile=f"{macro_path} (optimized)", context=diff_context)
        if d:
            # Match common formatter behavior: diffs go to stdout in diff-only mode.
            (sys.stdout if diff_only_mode else sys.stderr).write(d)

    if check:
        if not quiet:
            console_err.print(
                f"[dim]# check: {'would change' if changed else 'no changes'} ({stats.in_steps} -> {stats.out_steps} steps)[/dim]"
            )
        raise typer.Exit(code=1 if changed else 0)

    if diff_only_mode:
        # `--diff` is a review mode: do not emit YAML.
        if not quiet:
            console_err.print(
                f"[dim]# diff: {stats.in_steps} -> {stats.out_steps} steps "
                f"(merged_delays={stats.merged_delays}, removed_mouse_moves={stats.removed_mouse_moves}, "
                f"compressed_clicks={stats.compressed_clicks}, compressed_key_presses={stats.compressed_key_presses}, "
                f"compressed_chords={stats.compressed_chords}, compressed_text_runs={stats.compressed_text_runs}, promoted_paste_texts={stats.promoted_paste_texts}, segmented_paste_texts={stats.segmented_paste_texts})[/dim]"
            )
        return

    if in_place:
        macro_path.write_text(text)
        if not quiet:
            console.print(
                f"Optimized [bold]{macro_path}[/bold]: {stats.in_steps} -> {stats.out_steps} steps "
                f"(delays merged: {stats.merged_delays}, mouse moves removed: {stats.removed_mouse_moves}, "
                f"clicks: {stats.compressed_clicks}, keys: {stats.compressed_key_presses}, chords: {stats.compressed_chords}, "
                f"text runs: {stats.compressed_text_runs}, paste-promoted: {stats.promoted_paste_texts}, paste-segmented: {stats.segmented_paste_texts})"
            )
        return

    if out is not None:
        out = out.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        if not quiet:
            console.print(
                f"Wrote optimized macro: [bold]{out}[/bold] ({stats.in_steps} -> {stats.out_steps} steps)"
            )
        return

    # Default output mode: YAML to stdout, summary to stderr.
    if not quiet:
        console_err.print(
            f"[dim]# optimized: {stats.in_steps} -> {stats.out_steps} steps "
            f"(merged_delays={stats.merged_delays}, removed_mouse_moves={stats.removed_mouse_moves}, "
            f"compressed_clicks={stats.compressed_clicks}, compressed_key_presses={stats.compressed_key_presses}, "
            f"compressed_chords={stats.compressed_chords}, compressed_text_runs={stats.compressed_text_runs}, promoted_paste_texts={stats.promoted_paste_texts}, segmented_paste_texts={stats.segmented_paste_texts})[/dim]",
        )
    sys.stdout.write(text)




@app.command()
def optimize_project(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project folder containing macros/"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Write optimized macros into this folder (preserves filenames)"),
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite macro YAML files in-place"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write files; only report what would change"),
    check: bool = typer.Option(False, "--check", help="Do not write output; exit non-zero if any macro would change"),
    diff: bool = typer.Option(False, "--diff", help="Print unified diffs for macros that would change"),
    diff_context: int = typer.Option(3, "--diff-context", min=0, help="Number of context lines to show in unified diffs"),
    profile: str = typer.Option("balanced", "--profile", help="safe|balanced|aggressive"),
    cap_delay_ms: int | None = typer.Option(None, "--cap-delay-ms", min=1, help="Cap individual Delay steps to this many ms"),
    max_click_hold_ms: int = typer.Option(250, "--max-click-hold-ms", min=0, help="Only collapse clicks when down->up hold is <= this"),
    max_keypress_gap_ms: int = typer.Option(250, "--max-keypress-gap-ms", min=0, help="Only collapse KeyDown/KeyUp when gap is <= this"),
    max_chord_gap_ms: int = typer.Option(250, "--max-chord-gap-ms", min=0, help="Only collapse modifier chords when gaps are <= this"),
    compress_text: bool | None = typer.Option(
        None,
        "--compress-text/--no-compress-text",
        help="Collapse plain character Key streams into a TypeText step (auto: on for aggressive)",
    ),
    max_text_gap_ms: int = typer.Option(250, "--max-text-gap-ms", min=0, help="Only combine text keys when gaps are <= this"),
    min_text_run: int = typer.Option(3, "--min-text-run", min=2, help="Minimum number of characters before collapsing into TypeText"),
    promote_paste_text: bool = typer.Option(False, "--promote-paste-text/--no-promote-paste-text", help="Rewrite long literal TypeText steps to backend=clipboard when safe"),
    paste_text_min_chars: int = typer.Option(80, "--paste-text-min-chars", min=1, help="Minimum literal text length before promoting to clipboard paste"),
    segment_paste_text: bool = typer.Option(False, "--segment-paste-text/--no-segment-paste-text", help="Split multiline/tab-rich literal TypeText into clipboard chunks plus explicit Tab/Enter keys when safe"),
    segment_paste_min_chars: int = typer.Option(24, "--segment-paste-min-chars", min=1, help="Minimum literal chunk length before a structured text segment is promoted to clipboard paste"),
    quiet: bool = typer.Option(False, "--quiet", help="Do not print per-file summaries"),
):
    """Optimize every macro in a project.

    This is a convenience wrapper around `vhk optimize` for bulk cleanup after
    recording multiple macros.

    By default this command writes into a separate output folder. Use
    `--in-place` to overwrite macro files.
    """

    if in_place and out_dir is not None:
        raise typer.BadParameter("Use either --in-place or --out-dir, not both.")
    if check and (in_place or out_dir is not None or dry_run):
        raise typer.BadParameter("--check cannot be combined with --in-place, --out-dir, or --dry-run.")

    writing_mode = bool(in_place or (out_dir is not None) or dry_run)
    # If we're not writing, we must be in a review mode.
    if not writing_mode and not (check or diff):
        raise typer.BadParameter("Choose either --out-dir/--in-place/--dry-run, or use --check/--diff for review.")

    project_dir = project_dir.resolve()
    # Load/validate the project structure (best-effort); this also ensures the
    # macro YAML parses as a Macro model.
    try:
        _ = load_project(project_dir)
    except Exception as exc:
        raise typer.BadParameter(f"Invalid project: {exc}")

    macros_dir = project_dir / "macros"
    if not macros_dir.exists():
        raise typer.BadParameter("Project has no macros/ directory.")

    macro_files = sorted(list(macros_dir.glob("*.yaml")) + list(macros_dir.glob("*.yml")))
    if not macro_files:
        raise typer.BadParameter("No macro YAML files found under macros/.")

    if out_dir is not None:
        out_dir = out_dir.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

    total_in = total_out = 0
    changed = 0
    skipped = 0

    for mp in macro_files:
        raw = mp.read_text()
        payload = yaml.safe_load(raw)
        if not isinstance(payload, dict) or "steps" not in payload or not isinstance(payload.get("steps"), list):
            skipped += 1
            if not quiet:
                console_err.print(f"[yellow]Skipping[/yellow] {mp}: not a macro mapping with 'steps:' list")
            continue

        steps = payload.get("steps") or []
        optimized, stats = optimize_steps(
            steps,
            profile=profile,
            cap_delay_ms=cap_delay_ms,
            max_click_hold_ms=max_click_hold_ms,
            max_keypress_gap_ms=max_keypress_gap_ms,
            max_chord_gap_ms=max_chord_gap_ms,
            compress_text=compress_text,
            max_text_gap_ms=max_text_gap_ms,
            min_text_run=min_text_run,
            promote_paste_text=promote_paste_text,
            paste_text_min_chars=paste_text_min_chars,
            segment_paste_text=segment_paste_text,
            segment_paste_min_chars=segment_paste_min_chars,
        )

        total_in += stats.in_steps
        total_out += stats.out_steps

        payload2 = dict(payload)
        payload2["steps"] = optimized
        text = yaml.safe_dump(payload2, sort_keys=False)

        did_change = (raw != text)
        if did_change:
            changed += 1

        if not writing_mode:
            # Review mode: no writes.
            if diff and did_change:
                d = _unified_diff(raw, text, fromfile=str(mp), tofile=f"{mp} (optimized)", context=diff_context)
                if d:
                    sys.stdout.write(d)
            if not quiet:
                console_err.print(
                    f"[dim]{mp.name}: {'would change' if did_change else 'no changes'} "
                    f"({stats.in_steps} -> {stats.out_steps})[/dim]"
                )
            continue

        if dry_run:
            if not quiet:
                console_err.print(
                    f"[dim]{mp.name}: {stats.in_steps} -> {stats.out_steps} "
                    f"(merged_delays={stats.merged_delays}, removed_mouse_moves={stats.removed_mouse_moves}, "
                    f"compressed_clicks={stats.compressed_clicks}, compressed_keys={stats.compressed_key_presses}, "
                    f"compressed_chords={stats.compressed_chords}, compressed_text_runs={stats.compressed_text_runs}, promoted_paste_texts={stats.promoted_paste_texts}, segmented_paste_texts={stats.segmented_paste_texts})[/dim]"
                )
            continue

        if in_place:
            mp.write_text(text)
            if not quiet:
                console_err.print(f"Optimized {mp} ({stats.in_steps} -> {stats.out_steps})")
            continue

        assert out_dir is not None
        dst = out_dir / mp.name
        dst.write_text(text)
        if not quiet:
            console_err.print(f"Wrote {dst} ({stats.in_steps} -> {stats.out_steps})")

    summary = (
        f"Optimized {len(macro_files) - skipped} macros"
        + (" (dry-run)" if dry_run else "")
        + f": files_changed={changed}, skipped={skipped}, steps={total_in}->{total_out}"
    )

    if check:
        # This branch should be unreachable because --check implies !writing_mode,
        # but keep it explicit.
        console_err.print(summary)
        raise typer.Exit(code=1 if changed else 0)

    if not quiet:
        # Avoid mixing the summary with unified diffs on stdout.
        (console_err if not writing_mode else console).print(summary)


@app.command()
def retime(
    macro_path: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="Macro YAML file to retime"),
    out: Path | None = typer.Option(None, "--out", help="Write retimed YAML to this path (default: stdout)"),
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite the input file"),
    speed: float | None = typer.Option(
        None,
        "--speed",
        min=0.0001,
        help="Playback speed multiplier (2.0 = twice as fast; delays are divided by this value)",
    ),
    factor: float = typer.Option(
        1.0,
        "--factor",
        min=0.0,
        help="Multiply delays by this factor (0.5 = halve delays, 2.0 = double). Ignored if --speed is provided.",
    ),
    min_ms: int | None = typer.Option(None, "--min-ms", min=0, help="Clamp retimed values to at least this many ms"),
    max_ms: int | None = typer.Option(None, "--max-ms", min=0, help="Clamp retimed values to at most this many ms"),
    include_step_delay: bool = typer.Option(True, "--include-step-delay/--no-include-step-delay", help="Scale per-step delay_ms fields"),
    include_retry_delay: bool = typer.Option(True, "--include-retry-delay/--no-include-retry-delay", help="Scale retry_delay_ms fields"),
    include_type_delay: bool = typer.Option(True, "--include-type-delay/--no-include-type-delay", help="Scale TypeText.delay_ms_per_char"),
    include_timeouts: bool = typer.Option(False, "--include-timeouts", help="Also scale timeout_ms fields in wait steps"),
    include_polling: bool = typer.Option(False, "--include-polling", help="Also scale poll_ms/max_poll_ms/jitter_ms fields"),
    quiet: bool = typer.Option(False, "--quiet", help="Do not print a summary to stderr"),
):
    """Retiming pass to speed up / slow down recorded macros.

    This command scales explicit Delay/RandomWait steps, and optionally a few
    other delay-like fields (per-step delays, retry delays, and type delays).

    Timeouts and polling intervals are left unchanged by default to avoid
    accidentally making macros flaky; opt in with --include-timeouts or
    --include-polling.
    """

    if in_place and out is not None:
        raise typer.BadParameter("Use either --in-place or --out, not both.")

    if speed is not None:
        if speed <= 0:
            raise typer.BadParameter("--speed must be > 0")
        factor = 1.0 / float(speed)

    raw = macro_path.read_text()
    payload = yaml.safe_load(raw)
    if not isinstance(payload, dict) or "steps" not in payload:
        raise typer.BadParameter("Macro YAML must be a mapping containing a 'steps:' list.")
    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise typer.BadParameter("'steps' must be a list.")

    retimed, stats = retime_steps(
        steps,
        factor=float(factor),
        min_ms=min_ms,
        max_ms=max_ms,
        include_step_delay=include_step_delay,
        include_retry_delay=include_retry_delay,
        include_type_delay=include_type_delay,
        include_timeouts=include_timeouts,
        include_polling=include_polling,
    )

    payload2 = dict(payload)
    payload2["steps"] = retimed
    text = yaml.safe_dump(payload2, sort_keys=False)

    if in_place:
        macro_path.write_text(text)
        if not quiet:
            console.print(
                f"Retimed [bold]{macro_path}[/bold] (factor={float(factor):.4g}): "
                f"Delay={stats.scaled_delay_steps}, RandomWait={stats.scaled_random_waits}, "
                f"step_delay={stats.scaled_step_delays}, retry_delay={stats.scaled_retry_delays}, "
                f"type_delay={stats.scaled_type_delays}, skipped_non_numeric={stats.skipped_non_numeric}"
            )
        return

    if out is not None:
        out = out.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        if not quiet:
            console.print(f"Wrote retimed macro: [bold]{out}[/bold] (factor={float(factor):.4g})")
        return

    if not quiet:
        console_err.print(
            f"[dim]# retimed factor={float(factor):.4g}: "
            f"Delay={stats.scaled_delay_steps}, RandomWait={stats.scaled_random_waits}, "
            f"step_delay={stats.scaled_step_delays}, retry_delay={stats.scaled_retry_delays}, "
            f"type_delay={stats.scaled_type_delays}, timeouts={stats.scaled_timeouts}, polling={stats.scaled_polling}, "
            f"skipped_non_numeric={stats.skipped_non_numeric}[/dim]"
        )
    sys.stdout.write(text)


@app.command()
def retime_project(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, help="Project folder containing macros/"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Write retimed macros into this folder (preserves filenames)"),
    in_place: bool = typer.Option(False, "--in-place", help="Overwrite macro YAML files in-place"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write files; only report what would change"),
    speed: float | None = typer.Option(None, "--speed", min=0.0001, help="Playback speed multiplier (2.0 = twice as fast; delays are divided by this value)"),
    factor: float = typer.Option(1.0, "--factor", min=0.0, help="Multiply delays by this factor (ignored if --speed is provided)"),
    min_ms: int | None = typer.Option(None, "--min-ms", min=0, help="Clamp retimed values to at least this many ms"),
    max_ms: int | None = typer.Option(None, "--max-ms", min=0, help="Clamp retimed values to at most this many ms"),
    include_step_delay: bool = typer.Option(True, "--include-step-delay/--no-include-step-delay", help="Scale per-step delay_ms fields"),
    include_retry_delay: bool = typer.Option(True, "--include-retry-delay/--no-include-retry-delay", help="Scale retry_delay_ms fields"),
    include_type_delay: bool = typer.Option(True, "--include-type-delay/--no-include-type-delay", help="Scale TypeText.delay_ms_per_char"),
    include_timeouts: bool = typer.Option(False, "--include-timeouts", help="Also scale timeout_ms fields in wait steps"),
    include_polling: bool = typer.Option(False, "--include-polling", help="Also scale poll_ms/max_poll_ms/jitter_ms fields"),
    quiet: bool = typer.Option(False, "--quiet", help="Do not print per-file summaries"),
):
    """Retiming pass for every macro in a project."""

    if in_place and out_dir is not None:
        raise typer.BadParameter("Use either --in-place or --out-dir, not both.")
    if not in_place and out_dir is None:
        raise typer.BadParameter("Choose either --out-dir or --in-place.")

    if speed is not None:
        if speed <= 0:
            raise typer.BadParameter("--speed must be > 0")
        factor = 1.0 / float(speed)

    project_dir = project_dir.resolve()
    try:
        _ = load_project(project_dir)
    except Exception as exc:
        raise typer.BadParameter(f"Invalid project: {exc}")

    macros_dir = project_dir / "macros"
    if not macros_dir.exists():
        raise typer.BadParameter("Project has no macros/ directory.")

    macro_files = sorted(list(macros_dir.glob("*.yaml")) + list(macros_dir.glob("*.yml")))
    if not macro_files:
        raise typer.BadParameter("No macro YAML files found under macros/.")

    if out_dir is not None:
        out_dir = out_dir.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

    changed = 0
    skipped = 0
    total_scaled = 0

    for mp in macro_files:
        raw = mp.read_text()
        payload = yaml.safe_load(raw)
        if not isinstance(payload, dict) or "steps" not in payload or not isinstance(payload.get("steps"), list):
            skipped += 1
            if not quiet:
                console_err.print(f"[yellow]Skipping[/yellow] {mp}: not a macro mapping with 'steps:' list")
            continue

        steps = payload.get("steps") or []
        retimed, stats = retime_steps(
            steps,
            factor=float(factor),
            min_ms=min_ms,
            max_ms=max_ms,
            include_step_delay=include_step_delay,
            include_retry_delay=include_retry_delay,
            include_type_delay=include_type_delay,
            include_timeouts=include_timeouts,
            include_polling=include_polling,
        )

        did_change = (
            stats.scaled_delay_steps
            or stats.scaled_random_waits
            or stats.scaled_step_delays
            or stats.scaled_retry_delays
            or stats.scaled_type_delays
            or stats.scaled_timeouts
            or stats.scaled_polling
        )
        if did_change:
            changed += 1
        total_scaled += (
            stats.scaled_delay_steps
            + stats.scaled_random_waits
            + stats.scaled_step_delays
            + stats.scaled_retry_delays
            + stats.scaled_type_delays
            + stats.scaled_timeouts
            + stats.scaled_polling
        )

        payload2 = dict(payload)
        payload2["steps"] = retimed
        text = yaml.safe_dump(payload2, sort_keys=False)

        if dry_run:
            if not quiet:
                console_err.print(
                    f"[dim]{mp.name}: scaled={did_change} (Delay={stats.scaled_delay_steps}, RandomWait={stats.scaled_random_waits}, "
                    f"step_delay={stats.scaled_step_delays}, retry_delay={stats.scaled_retry_delays}, type_delay={stats.scaled_type_delays}, "
                    f"timeouts={stats.scaled_timeouts}, polling={stats.scaled_polling})[/dim]"
                )
            continue

        if in_place:
            mp.write_text(text)
            if not quiet:
                console_err.print(f"Retimed {mp} (factor={float(factor):.4g})")
            continue

        assert out_dir is not None
        dst = out_dir / mp.name
        dst.write_text(text)
        if not quiet:
            console_err.print(f"Wrote {dst} (factor={float(factor):.4g})")

    console.print(
        f"Retimed {len(macro_files) - skipped} macros"
        + (" (dry-run)" if dry_run else "")
        + f": files_changed={changed}, skipped={skipped}, scaled_fields={total_scaled}, factor={float(factor):.4g}"
    )


@app.command()
def gen_i3_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
    via_bus: bool = typer.Option(False, "--via-bus", help="Emit bus events instead of running macros directly"),
    bus_event: str = typer.Option("hotkey", "--bus-event", help="Bus event name to emit when using --via-bus"),
    emit_cmd: str = typer.Option("vhk-emit", "--emit-cmd", help="Emitter command (default: vhk-emit)"),
):
    """Generate i3 bindsym lines from project.yaml bindings."""

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_wm_bindings(project_dir, project, wm="i3", via_bus=via_bus, bus_event=bus_event, emit_cmd=emit_cmd)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote i3 config snippet: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


@app.command()
def gen_hyprland_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
    via_bus: bool = typer.Option(False, "--via-bus", help="Emit bus events instead of running macros directly"),
    bus_event: str = typer.Option("hotkey", "--bus-event", help="Bus event name to emit when using --via-bus"),
    emit_cmd: str = typer.Option("vhk-emit", "--emit-cmd", help="Emitter command (default: vhk-emit)"),
):
    """Generate Hyprland bind lines from project.yaml bindings.

    Uses `bindr` (release trigger) by default and falls back to VHK's
    `--require-window` gate for any binding that specifies a `when:` selector.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_wm_bindings(project_dir, project, wm="hyprland", via_bus=via_bus, bus_event=bus_event, emit_cmd=emit_cmd)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote hyprland config snippet: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


def _binding_label(b, idx: int) -> str:
    name = (getattr(b, "name", None) or "").strip()
    if name:
        return name
    desc = (getattr(b, "description", None) or "").strip()
    if desc:
        return desc
    macro = (getattr(b, "macro", None) or "").strip()
    if macro:
        return macro
    keys = (getattr(b, "keys", None) or "").strip()
    return keys or f"binding_{idx}"


def _bus_emit_cmd(
    sock_path: Path,
    *,
    emit_cmd: str,
    bus_event: str,
    macro: str,
    vars: dict[str, Any] | None,
    binding: str,
    keys: str,
    require_window: dict[str, Any] | None,
) -> str:
    payload: dict[str, Any] = {
        "macro": macro,
        "vars": vars or {},
        "binding": binding,
        "keys": keys,
    }
    if require_window:
        payload["require_window"] = require_window
    args = [emit_cmd, "--socket", str(sock_path), bus_event, "--data", json.dumps(payload, ensure_ascii=False)]
    return " ".join(shlex.quote(a) for a in args)


def _generate_wm_bindings(project_dir: Path, project, *, wm: str, via_bus: bool = False, bus_event: str = "hotkey", emit_cmd: str = "vhk-emit") -> str:
    lines: list[str] = []
    lines.append(f"# VHK {wm} bindings for project: {project.name}")
    lines.append(f"# Add these lines to your {wm} config.")
    if wm in {"i3", "sway"}:
        lines.append("# Uses `bindsym --release` to avoid running macros while the keyboard is grabbed.")
    elif wm == "hyprland":
        lines.append("# Uses the `r` (release) flag to avoid triggering while the key is being held.")
        lines.append("# Note: Hyprland binds are comma-separated; avoid trailing commas.")

    bindings = list(getattr(project, "bindings", []) or [])
    if not bindings:
        lines.append("# (No bindings defined. Add a 'bindings:' list to project.yaml.)")

    sock_path: Path | None = None
    if via_bus:
        sock_path = get_bus_socket_path(project_dir, configured=project.settings.bus_socket)
        lines.append(f"# via bus: event='{bus_event}', socket='{sock_path}'")
        lines.append("# NOTE: run a bus watcher with dispatch=true (see docs/BUS_EVENTS.md).")

    def _parse_i3_keys_for_hypr(keys: str) -> tuple[str, str]:
        """Parse an i3-style Mod+Shift+K string into (mods, key) for Hyprland."""

        parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
        if not parts:
            return "", ""

        key = parts[-1]
        mods_raw = parts[:-1]

        mod_map = {
            "mod4": "SUPER",
            "super": "SUPER",
            "mod1": "ALT",
            "alt": "ALT",
            "control": "CTRL",
            "ctrl": "CTRL",
            "shift": "SHIFT",
        }

        mods: list[str] = []
        for m in mods_raw:
            mm = mod_map.get(m.lower())
            mods.append(mm if mm else m)

        # Hyprland key name is case-sensitive; normalize single letters.
        if len(key) == 1:
            key = key.upper()

        return " ".join(mods), key

    for idx, b in enumerate(bindings):
        binding_label = _binding_label(b, idx)
        if via_bus:
            assert sock_path is not None
            rw = b.when.model_dump(by_alias=True) if getattr(b, "when", None) else None
            cmd = _bus_emit_cmd(
                sock_path,
                emit_cmd=emit_cmd,
                bus_event=bus_event,
                macro=b.macro,
                vars=getattr(b, "vars", None) or {},
                binding=binding_label,
                keys=b.keys,
                require_window=rw,
            )
        else:
            args = ["vhk", "run", str(project_dir), b.macro]
            if b.vars:
                args += ["--vars", json.dumps(b.vars)]
            cmd = " ".join(shlex.quote(a) for a in args)
        desc = f"  # {b.description}" if b.description else ""

        if wm in {"i3", "sway"}:
            criteria = _selector_to_criteria(b.when, wm=wm) + " " if b.when else ""

            if wm == "i3":
                lines.append(f"bindsym --release {b.keys} {criteria}exec --no-startup-id {cmd}{desc}")
            else:
                # sway has no --no-startup-id.
                lines.append(f"bindsym --release {b.keys} {criteria}exec {cmd}{desc}")
            continue

        if wm == "hyprland":
            mods, key = _parse_i3_keys_for_hypr(b.keys)
            # Hyprland doesn't support i3-style criteria scoping inside binds.
            # If we're not using bus dispatch, use VHK's --require-window gate as a portable workaround.
            if b.when and not via_bus:
                args2 = ["vhk", "run", str(project_dir), b.macro]
                if b.vars:
                    args2 += ["--vars", json.dumps(b.vars)]
                args2 += ["--require-window", b.when.model_dump_json(by_alias=True)]
                cmd = " ".join(shlex.quote(a) for a in args2)

            kw = "bindr"
            if b.description and "," not in b.description:
                kw = "bindrd"
                lines.append(f"{kw} = {mods}, {key}, {b.description}, exec, {cmd}")
                continue

            # No description or unsafe description.
            lines.append(f"{kw} = {mods}, {key}, exec, {cmd}{desc}")
            continue

        raise ValueError(f"unsupported wm: {wm}")

    return "\n".join(lines) + "\n"


def _generate_wm_mode_bindings(
    project_dir: Path,
    project_name: str,
    bindings,
    *,
    wm: str,
    mode_name: str,
    enter_keys: str,
    strip_mods: list[str],
    exit_keys: list[str],
    one_shot: bool,
    via_bus: bool = False,
    bus_event: str = "hotkey",
    emit_cmd: str = "vhk-emit",
) -> str:
    """Generate an i3/sway mode or Hyprland submap snippet.

    Rationale
    ---------
    Both i3/sway "binding modes" and Hyprland "submaps" are widely used to
    create leader-key style keymaps (e.g. the default i3 resize mode, Hyprland
    submap examples). This keeps global keybind space uncluttered and makes it
    easier to share a consistent VHK macro layer across environments.
    """

    mode_name = (mode_name or "vhk").strip() or "vhk"
    enter_keys = (enter_keys or "").strip()
    if not enter_keys:
        raise ValueError("enter_keys is required for mode/submap generation")

    # Normalize modifier names for stripping.
    strip_set = {m.strip().lower() for m in strip_mods if m.strip()}

    def _strip_prefix(keys: str) -> str:
        parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
        if not parts:
            return keys
        key = parts[-1]
        mods = parts[:-1]
        mods2 = [m for m in mods if m.lower() not in strip_set]

        # For i3/sway, uppercase key can represent Shift+letter.
        if wm in {"i3", "sway"}:
            if len(key) == 1 and any(m.lower() == "shift" for m in mods2):
                mods2 = [m for m in mods2 if m.lower() != "shift"]
                key = key.upper()

        return "+".join(mods2 + [key]) if mods2 else key

    lines: list[str] = []
    sock_path: Path | None = None
    if via_bus:
        sock_path = get_bus_socket_path(project_dir, configured=load_project(project_dir).settings.bus_socket)
    if wm in {"i3", "sway"}:
        lines.append(f"# VHK {wm} mode bindings for project: {project_name}")
        lines.append(f"# Add these lines to your {wm} config.")
        lines.append(f"# Enter mode '{mode_name}' with: {enter_keys}")
        lines.append("# Tip: one-shot modes are a common 'launch mode' pattern.")

        # Enter mode on key press (standard i3/sway pattern).
        lines.append(f"bindsym {enter_keys} mode \"{mode_name}\"")
        lines.append(f"mode \"{mode_name}\" {{")

        # Exit keys.
        for ek in exit_keys:
            ek2 = (ek or "").strip()
            if ek2:
                lines.append(f"    bindsym {ek2} mode \"default\"")

        if not bindings:
            lines.append("    # (No bindings defined. Add a 'bindings:' list to project.yaml.)")

        if via_bus:
            lines.append(f"    # via bus: event='{bus_event}', socket='{sock_path}'")
            lines.append("    # NOTE: run a bus watcher with dispatch=true (see docs/BUS_EVENTS.md).")

        for idx, b in enumerate(bindings):
            inner_keys = _strip_prefix(b.keys)
            binding_label = _binding_label(b, idx)
            if via_bus:
                assert sock_path is not None
                rw = b.when.model_dump(by_alias=True) if getattr(b, "when", None) else None
                cmd = _bus_emit_cmd(
                    sock_path,
                    emit_cmd=emit_cmd,
                    bus_event=bus_event,
                    macro=b.macro,
                    vars=getattr(b, "vars", None) or {},
                    binding=binding_label,
                    keys=b.keys,
                    require_window=rw,
                )
            else:
                args = ["vhk", "run", str(project_dir), b.macro]
                if b.vars:
                    args += ["--vars", json.dumps(b.vars)]
                cmd = " ".join(shlex.quote(a) for a in args)
            criteria = _selector_to_criteria(b.when, wm=wm) + " " if b.when else ""
            desc = f"  # {b.description}" if b.description else ""

            # i3 supports --no-startup-id; sway does not.
            if wm == "i3":
                exec_part = f"{criteria}exec --no-startup-id {cmd}"
            else:
                exec_part = f"{criteria}exec {cmd}"

            if one_shot:
                exec_part += f"; mode \"default\""

            lines.append(f"    bindsym --release {inner_keys} {exec_part}{desc}")

        lines.append("}")
        return "\n".join(lines) + "\n"

    if wm == "hyprland":
        lines.append(f"# VHK hyprland submap bindings for project: {project_name}")
        lines.append("# Add these lines to your hyprland config.")
        lines.append("# Note: Hyprland binds are comma-separated; avoid trailing commas.")
        lines.append(f"# Enter submap '{mode_name}' with: {enter_keys}")

        # Parse enter combo as i3-style and translate to Hyprland.
        def _parse_i3_keys_for_hypr(keys: str) -> tuple[str, str]:
            parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
            if not parts:
                return "", ""
            key = parts[-1]
            mods_raw = parts[:-1]
            mod_map = {
                "mod4": "SUPER",
                "super": "SUPER",
                "mod1": "ALT",
                "alt": "ALT",
                "control": "CTRL",
                "ctrl": "CTRL",
                "shift": "SHIFT",
            }
            mods: list[str] = []
            for m in mods_raw:
                mm = mod_map.get(m.lower())
                mods.append(mm if mm else m)
            if len(key) == 1:
                key = key.upper()
            return " ".join(mods), key

        enter_mods, enter_key = _parse_i3_keys_for_hypr(enter_keys)
        lines.append(f"bind = {enter_mods}, {enter_key}, submap, {mode_name}")
        lines.append("")

        # Define the submap. Optionally auto-reset after any dispatch.
        if one_shot:
            lines.append(f"submap = {mode_name}, reset")
        else:
            lines.append(f"submap = {mode_name}")

        # Exit keys.
        for ek in exit_keys:
            ek2 = (ek or "").strip()
            if not ek2:
                continue
            # Hyprland expects key names, not i3 syntax. Best-effort: handle common names.
            emods, ekey = _parse_i3_keys_for_hypr(ek2)
            lines.append(f"bind = {emods}, {ekey}, submap, reset")

        if not bindings:
            lines.append("# (No bindings defined. Add a 'bindings:' list to project.yaml.)")

        if via_bus:
            lines.append(f"# via bus: event='{bus_event}', socket='{sock_path}'")
            lines.append("# NOTE: run a bus watcher with dispatch=true (see docs/BUS_EVENTS.md).")

        for idx, b in enumerate(bindings):
            inner = _strip_prefix(b.keys)
            mods, key = _parse_i3_keys_for_hypr(inner)
            binding_label = _binding_label(b, idx)
            if via_bus:
                assert sock_path is not None
                rw = b.when.model_dump(by_alias=True) if getattr(b, "when", None) else None
                cmd = _bus_emit_cmd(
                    sock_path,
                    emit_cmd=emit_cmd,
                    bus_event=bus_event,
                    macro=b.macro,
                    vars=getattr(b, "vars", None) or {},
                    binding=binding_label,
                    keys=b.keys,
                    require_window=rw,
                )
            else:
                args = ["vhk", "run", str(project_dir), b.macro]
                if b.vars:
                    args += ["--vars", json.dumps(b.vars)]
                # Hyprland doesn't support i3-style criteria scoping in binds; use VHK gate.
                if b.when:
                    args += ["--require-window", b.when.model_dump_json(by_alias=True)]
                cmd = " ".join(shlex.quote(a) for a in args)

            kw = "bindr"
            if b.description and "," not in b.description:
                kw = "bindrd"
                lines.append(f"{kw} = {mods}, {key}, {b.description}, exec, {cmd}")
            else:
                desc = f"  # {b.description}" if b.description else ""
                lines.append(f"{kw} = {mods}, {key}, exec, {cmd}{desc}")

        lines.append("submap = reset")
        return "\n".join(lines) + "\n"

    raise ValueError(f"unsupported wm for mode generation: {wm}")


@app.command()
def gen_wm_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    wm: str = typer.Option("auto", "--wm", help="Target window manager: auto, i3, sway, hyprland"),
    mode_enter: str | None = typer.Option(
        None,
        "--mode-enter",
        help="Generate a WM mode/submap snippet. Provide the key combo used to enter it (e.g. Mod4+R).",
    ),
    mode_name: str = typer.Option("vhk", "--mode-name", help="Mode/submap name (default: vhk)"),
    mode_strip_mods: str = typer.Option(
        "Mod4",
        "--mode-strip-mods",
        help="Comma-separated modifier names to strip from binding keys inside the mode/submap (default: Mod4).",
    ),
    mode_exit_keys: str = typer.Option(
        "Escape,Return",
        "--mode-exit-keys",
        help="Comma-separated keys inside mode/submap that exit back to default (default: Escape,Return).",
    ),
    mode_one_shot: bool = typer.Option(
        True,
        "--mode-one-shot/--mode-sticky",
        help="Auto-exit mode/submap after running a macro (default: one-shot).",
    ),
    via_bus: bool = typer.Option(False, "--via-bus", help="Emit bus events instead of running macros directly"),
    bus_event: str = typer.Option("hotkey", "--bus-event", help="Bus event name to emit when using --via-bus"),
    emit_cmd: str = typer.Option("vhk-emit", "--emit-cmd", help="Emitter command (default: vhk-emit)"),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
):
    """Generate keybind config snippets for common Linux window managers.

    - i3: uses `exec --no-startup-id`
    - sway: uses `exec` (no --no-startup-id)
    - hyprland: uses `bindr = MODS, KEY, exec, ...` (release trigger)
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)
    wm2 = wm.strip().lower()
    if wm2 == "auto":
        wm2 = _default_wm()
    if wm2 not in {"i3", "sway", "hyprland"}:
        raise typer.BadParameter("wm must be one of: auto, i3, sway, hyprland")

    if mode_enter:
        strip_mods = [m.strip() for m in mode_strip_mods.split(",") if m.strip()]
        exit_keys = [k.strip() for k in mode_exit_keys.split(",") if k.strip()]
        text = _generate_wm_mode_bindings(
            project_dir,
            project.name,
            project.bindings,
            wm=wm2,
            mode_name=mode_name,
            enter_keys=mode_enter,
            strip_mods=strip_mods,
            exit_keys=exit_keys,
            one_shot=mode_one_shot,
            via_bus=via_bus,
            bus_event=bus_event,
            emit_cmd=emit_cmd,
        )
    else:
        text = _generate_wm_bindings(project_dir, project, wm=wm2, via_bus=via_bus, bus_event=bus_event, emit_cmd=emit_cmd)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote {wm2} config snippet: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


def _kanata_key_from_i3(key: str) -> str:
    """Best-effort mapping from i3 key names to Kanata key names.

    Kanata key names are mostly based on Linux input key codes. For common
    alphanumerics and function keys, lowercase forms generally work.

    Notes
    -----
    This intentionally aims for "good enough" defaults rather than an exhaustive
    translation table.
    """

    k = (key or "").strip()
    if not k:
        return ""

    specials = {
        "return": "ret",
        "enter": "ret",
        "space": "spc",
        "tab": "tab",
        "escape": "esc",
        "esc": "esc",
        "backspace": "bspc",
        "delete": "del",
        "insert": "ins",
        "home": "home",
        "end": "end",
        "prior": "pgup",
        "next": "pgdn",
        "page_up": "pgup",
        "page_down": "pgdn",
        "left": "left",
        "right": "rght",
        "up": "up",
        "down": "down",
        "print": "prtsc",
        "pause": "pause",
        # i3 uses ISO_Left_Tab for shift+tab sometimes.
        "iso_left_tab": "tab",
    }

    low = k.lower()
    if low in specials:
        return specials[low]

    # Function keys.
    if re.fullmatch(r"f\d{1,2}", low):
        return low

    # Single letters: i3 often uses uppercase.
    if len(k) == 1 and k.isalpha():
        return k.lower()

    # Digits / punctuation in i3 config are typically literal.
    if len(k) == 1:
        return k

    # Common keypad naming differences.
    if low.startswith("kp_"):
        return "kp" + low[3:]

    return low


def _kanata_quote_arg(arg: str) -> str:
    """Quote an argument for Kanata's s-expression string token rules."""
    a = str(arg)
    # Safe unquoted token.
    if re.fullmatch(r"[A-Za-z0-9_./:+\-=]+", a) and '"' not in a:
        return a
    # Escape backslashes and quotes.
    a = a.replace("\\", "\\\\").replace('"', "\\\"")
    return f'"{a}"'


def _parse_i3_hotkey_to_kanata(keys: str) -> tuple[set[str], str]:
    """Parse an i3-style Mod4+Shift+P key string into (mods, key)."""

    parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
    if not parts:
        return set(), ""
    key = _kanata_key_from_i3(parts[-1])
    mod_raw = [p.lower() for p in parts[:-1]]

    mod_map = {
        "mod4": "lmet",
        "super": "lmet",
        "win": "lmet",
        "meta": "lmet",
        "mod1": "lalt",
        "alt": "lalt",
        "control": "lctl",
        "ctrl": "lctl",
        "shift": "lsft",
    }

    mods: set[str] = set()
    for m in mod_raw:
        mm = mod_map.get(m)
        if mm:
            mods.add(mm)

    return mods, key


def _generate_kanata_config(
    project_dir: Path,
    project,
    *,
    vhk_cmd: str = "vhk",
    run_on_release: bool = True,
    strict_mods: bool = False,
) -> str:
    """Generate a Kanata config focused on running VHK macros.

    The approach here is deliberately non-invasive:

    - Use `defsrc` with `deflayermap` to map only the keys VHK needs.
    - Enable `process-unmapped-keys yes` so modifier state is tracked even for
      keys outside `defsrc` (required for switch/unmod logic).
    - Use virtual keys + on-release wrappers to avoid key-repeat firing macros.
    """

    lines: list[str] = []
    lines.append(f"# VHK kanata bindings for project: {project.name}")
    lines.append("# Generated by: vhk gen-kanata-config")
    lines.append("#")
    lines.append("# Notes:")
    lines.append("# - Requires kanata with cmd enabled and `danger-enable-cmd yes`.")
    lines.append("# - Prefer running kanata as your user if your macros depend on")
    lines.append("#   user-session tools (Wayland portals, notification daemons, etc.).")
    lines.append("")

    lines.append("(defcfg")
    lines.append("  process-unmapped-keys yes")
    lines.append("  danger-enable-cmd yes")
    lines.append(")")
    lines.append("")

    # Minimal defsrc (required by kanata).
    lines.append("(defsrc)")
    lines.append("")

    bindings = list(getattr(project, "bindings", []) or [])
    if not bindings:
        lines.append(";; No bindings found. Add a `bindings:` list to project.yaml.")
        return "\n".join(lines) + "\n"

    # Per-binding virtual key definition.
    vk_defs: list[tuple[str, str, str | None]] = []  # (vk_name, cmd_expr, comment)
    # Group bindings by trigger key.
    by_key: dict[str, list[tuple[set[str], object, str]]] = {}

    for idx, b in enumerate(bindings, start=1):
        mods, key = _parse_i3_hotkey_to_kanata(getattr(b, "keys", ""))
        if not key:
            continue

        args = [vhk_cmd, "run", str(project_dir), b.macro, "--quiet"]
        if getattr(b, "vars", None):
            args += ["--vars", json.dumps(b.vars, ensure_ascii=False)]
        if getattr(b, "when", None):
            args += ["--require-window", b.when.model_dump_json(by_alias=True)]

        cmd_tokens = " ".join(_kanata_quote_arg(a) for a in args)
        # Use cmd-log to avoid noisy stdout in the kanata process.
        cmd_expr = f"(cmd-log none error {cmd_tokens})"
        vk_name = f"vhk_{idx:03d}"
        comment = getattr(b, "description", None)
        vk_defs.append((vk_name, cmd_expr, comment))

        by_key.setdefault(key, []).append((mods, b, vk_name))

    if not vk_defs:
        lines.append(";; No supported bindings (could not parse key names).")
        return "\n".join(lines) + "\n"

    lines.append("(defvirtualkeys")
    for (vk_name, cmd_expr, comment) in vk_defs:
        if comment:
            lines.append(f"  ;; {comment}")
        lines.append(f"  {vk_name} {cmd_expr}")
    lines.append(")")
    lines.append("")

    # Build per-trigger-key switch aliases.
    post_action = "on-release" if run_on_release else "on-press"

    def _logic_for_mods(mods: set[str]) -> str:
        if not mods:
            return "()"
        items = [f"(input real {m})" for m in sorted(mods)]
        if len(items) == 1:
            return f"(({items[0]}))"
        return f"((and {' '.join(items)}))"

    def _logic_no_extra_mods(required: set[str]) -> str:
        # Constrain to *exactly* the required modifier set (l/r variants not
        # handled; this is a best-effort strict mode).
        all_mods = {"lctl", "lalt", "lsft", "lmet", "rctl", "ralt", "rsft", "rmet"}
        req = set(required)
        extra = sorted(all_mods - req)
        items: list[str] = []
        for m in sorted(req):
            items.append(f"(input real {m})")
        for m in extra:
            items.append(f"(not (input real {m}))")
        if not items:
            return "()"
        if len(items) == 1:
            return f"(({items[0]}))"
        return f"((and {' '.join(items)}))"

    lines.append("(defalias")
    for key, entries in sorted(by_key.items()):
        alias_name = f"vhk_key_{re.sub(r'[^A-Za-z0-9]+', '_', key)}"
        lines.append(f"  {alias_name} (switch")

        # More specific combos first.
        entries_sorted = sorted(entries, key=lambda t: len(t[0]), reverse=True)
        for mods, b, vk_name in entries_sorted:
            logic = _logic_no_extra_mods(mods) if strict_mods else _logic_for_mods(mods)
            # Run the vkey on release (default) and suppress typing the key.
            action = f"(multi XX ({post_action} tap-vkey {vk_name}))"
            lines.append(f"    {logic} {action} break")
        # Default: preserve original behaviour.
        lines.append(f"    () {key} break")
        lines.append("  )")
    lines.append(")")
    lines.append("")

    lines.append("(deflayermap (base)")
    # Make everything else transparent.
    lines.append("  ___ _")
    for key in sorted(by_key.keys()):
        alias_name = f"vhk_key_{re.sub(r'[^A-Za-z0-9]+', '_', key)}"
        lines.append(f"  {key} @{alias_name}")
    lines.append(")")
    lines.append("")

    return "\n".join(lines) + "\n"


@app.command()
def gen_kanata_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to invoke VHK (default: vhk)"),
    on_release: bool = typer.Option(True, "--on-release/--on-press", help="Trigger macros on key release (default)"),
    strict_mods: bool = typer.Option(
        False,
        "--strict-mods",
        help="Require an exact modifier set (no extra modifiers held). Default is i3-like superset matching.",
    ),
):
    """Generate a Kanata config that runs project hotkeys.

    This is a practical path for Wayland environments where compositor-native
    keybinds are limited or unavailable.

    See docs/KANATA.md.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_kanata_config(project_dir, project, vhk_cmd=vhk_cmd, run_on_release=on_release, strict_mods=strict_mods)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote kanata config: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


def _keyd_key_from_i3(key: str) -> str:
    """Best-effort mapping from i3 key names to keyd key names.

    keyd's key names generally track Linux input key names (see `keyd list-keys`).
    We aim for pragmatic coverage of common automation keys.
    """

    k = (key or "").strip()
    if not k:
        return ""

    low = k.lower()
    specials = {
        "return": "enter",
        "enter": "enter",
        "space": "space",
        "tab": "tab",
        "escape": "esc",
        "esc": "esc",
        "backspace": "backspace",
        "delete": "delete",
        "insert": "insert",
        "home": "home",
        "end": "end",
        "prior": "pageup",
        "next": "pagedown",
        "page_up": "pageup",
        "page_down": "pagedown",
        "left": "left",
        "right": "right",
        "up": "up",
        "down": "down",
        "print": "print",
        "pause": "pause",
        "iso_left_tab": "tab",
        # Common multimedia / XF86 names.
        "xf86audiolowervolume": "volumedown",
        "xf86audioraisevolume": "volumeup",
        "xf86audiomute": "mute",
        "xf86audioplay": "playpause",
        "xf86audiopause": "playpause",
        "xf86audionext": "nextsong",
        "xf86audioprev": "previoussong",
        "xf86audiostop": "stopcd",
        "xf86monbrightnessup": "brightnessup",
        "xf86monbrightnessdown": "brightnessdown",
    }
    if low in specials:
        return specials[low]

    # Function keys.
    if re.fullmatch(r"f\d{1,2}", low):
        return low

    # Single letters: i3 often uses uppercase.
    if len(k) == 1 and k.isalpha():
        return k.lower()

    # Digits / punctuation in i3 config are typically literal.
    if len(k) == 1:
        return k

    # Common keypad naming differences.
    if low.startswith("kp_"):
        return "kp" + low[3:]

    return low


def _parse_i3_hotkey_to_keyd(keys: str) -> tuple[list[str], str]:
    """Parse i3-style Mod4+Shift+P into (layers, key)."""

    parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
    if not parts:
        return [], ""

    key = _keyd_key_from_i3(parts[-1])
    mod_raw = [p.lower() for p in parts[:-1]]

    mod_map = {
        "mod4": "meta",
        "super": "meta",
        "win": "meta",
        "meta": "meta",
        "mod1": "alt",
        "alt": "alt",
        "control": "control",
        "ctrl": "control",
        "shift": "shift",
    }

    layers: list[str] = []
    for m in mod_raw:
        lm = mod_map.get(m)
        if lm and lm not in layers:
            layers.append(lm)

    return layers, key


def _generate_keyd_config(
    project_dir: Path,
    project,
    *,
    vhk_cmd: str = "vhk",
    ids: list[str] | None = None,
    command_prefix: str | None = None,
) -> str:
    """Generate a keyd config that runs project hotkeys.

    keyd can execute shell commands using the `command(...)` action.
    keyd itself typically runs as root, so users may need a wrapper that
    re-enters the user session environment when calling VHK.
    """

    ids2 = ids or ["*"]
    lines: list[str] = []
    lines.append(f"# VHK keyd bindings for project: {project.name}")
    lines.append("# Generated by: vhk gen-keyd-config")
    lines.append("#")
    lines.append("# Notes:")
    lines.append("# - keyd usually runs as root; VHK macros that need Wayland portals")
    lines.append("#   or a user notification daemon may require a wrapper command.")
    lines.append("# - Use `keyd monitor` or `keyd list-keys` to discover key names.")
    lines.append("")

    lines.append("[ids]")
    for ident in ids2:
        lines.append(str(ident))
    lines.append("")

    bindings = list(getattr(project, "bindings", []) or [])
    if not bindings:
        lines.append("# No bindings found. Add a `bindings:` list to project.yaml.")
        return "\n".join(lines) + "\n"

    # Organize bindings into keyd layers.
    layer_map: dict[tuple[str, ...], dict[str, list[str]]] = {}

    # Prefer a stable modifier ordering to avoid generating both meta+shift and shift+meta.
    # Canonicalize with meta first (matches common Mod4 notation), then the rest.
    mod_order = {"meta": 0, "control": 1, "alt": 2, "shift": 3}

    for b in bindings:
        layers, key = _parse_i3_hotkey_to_keyd(getattr(b, "keys", ""))
        if not key:
            continue

        # Canonicalize layer ordering.
        layers_sorted = sorted(layers, key=lambda x: mod_order.get(x, 99))
        layer_key = tuple(layers_sorted)

        args = [vhk_cmd, "run", str(project_dir), b.macro, "--quiet"]
        if getattr(b, "vars", None):
            args += ["--vars", json.dumps(b.vars, ensure_ascii=False)]
        if getattr(b, "when", None):
            args += ["--require-window", b.when.model_dump_json(by_alias=True)]

        cmd = " ".join(shlex.quote(a) for a in args)
        if command_prefix:
            cmd = f"{command_prefix} {cmd}".strip()

        action = f"command({cmd})"
        layer_map.setdefault(layer_key, {}).setdefault(key, []).append(action)

    if not layer_map:
        lines.append("# No supported bindings (could not parse key names).")
        return "\n".join(lines) + "\n"

    # Emit layers.
    def _emit_layer_header(layer_key: tuple[str, ...]) -> str:
        if not layer_key:
            return "[main]"
        if len(layer_key) == 1:
            return f"[{layer_key[0]}]"
        return "[" + "+".join(layer_key) + "]"

    # Ensure composite layers are defined after their constituents.
    ordered_layers = sorted(layer_map.keys(), key=lambda lk: (len(lk), lk))
    for lk in ordered_layers:
        lines.append(_emit_layer_header(lk))
        key_to_actions = layer_map[lk]
        for key in sorted(key_to_actions.keys()):
            actions = key_to_actions[key]
            # If multiple bindings collide, keep the last binding (keyd resolves by last occurrence).
            lines.append(f"{key} = {actions[-1]}")
        lines.append("")

    return "\n".join(lines) + "\n"


@app.command()
def gen_keyd_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to invoke VHK (default: vhk)"),
    ids: list[str] = typer.Option(["*"], "--id", help="keyd device id(s) to match; repeatable. Default '*'"),
    command_prefix: str | None = typer.Option(
        None,
        "--command-prefix",
        help="Prefix inserted before the VHK command inside keyd's command(...). Useful for wrappers or env re-entry.",
    ),
):
    """Generate a keyd config that runs project hotkeys.

    keyd is a system-wide remapping daemon that can execute shell commands using
    the `command(...)` action. This is useful for Wayland setups where compositor
    hotkeys are limited.

    See docs/KEYD.md.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_keyd_config(project_dir, project, vhk_cmd=vhk_cmd, ids=ids, command_prefix=command_prefix)
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote keyd config: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)





def _kmonad_key_from_i3(key: str) -> str:
    """Best-effort mapping from i3 key names to KMonad keycodes.

    KMonad keycodes are largely Linux keycode names in lowercase, plus short
    aliases (e.g. `bspc`, `ret`, `spc`).

    Important: KMonad treats `\\` as an escape character, so a literal backslash
    keycode must be written as `\\\\` in config output.
    """

    k = (key or "").strip()
    if not k:
        return ""

    low = k.lower()
    specials = {
        "return": "ret",
        "enter": "ret",
        "space": "spc",
        "tab": "tab",
        "escape": "esc",
        "esc": "esc",
        "backspace": "bspc",
        "delete": "del",
        "insert": "ins",
        "home": "home",
        "end": "end",
        "prior": "pgup",
        "next": "pgdn",
        "page_up": "pgup",
        "page_down": "pgdn",
        "left": "left",
        "right": "right",
        "up": "up",
        "down": "down",
        "capslock": "caps",
        "caps": "caps",
    }
    if low in specials:
        return specials[low]

    # Function keys.
    if re.fullmatch(r"f\d{1,2}", low):
        return low

    # Single letters.
    if len(k) == 1 and k.isalpha():
        return k.lower()

    # Digits / punctuation.
    if len(k) == 1:
        if k == "\\":
            return "\\\\"  # literal backslash keycode in KMonad configs
        return k

    # Common keypad naming differences.
    if low.startswith("kp_"):
        # KMonad uses e.g. kp7, kp+, etc.
        return "kp" + low[3:]

    # Best effort: lower-case token.
    return low


def _parse_i3_hotkey_to_kmonad_key(keys: str) -> str:
    parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
    if not parts:
        return ""
    return _kmonad_key_from_i3(parts[-1])


def _kmonad_escape_string_literal(s: str) -> str:
    # KMonad uses double-quoted strings in cmd-button.
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _generate_kmonad_config(
    project_dir: Path,
    project,
    *,
    vhk_cmd: str = "vhk",
    leader_key: str = "caps",
    leader_tap: str | None = None,
    leader_timeout_ms: int = 200,
    run_on_release: bool = False,
    input_expr: str = 'device-file "$KBD_DEV" :ignore-missing true',
    output_expr: str = 'uinput-sink "VHK KMonad output"',
) -> str:
    """Generate a KMonad config focused on running VHK macros.

    Design intent
    -------------
    KMonad doesn't natively express WM-style modifier-scoped keybinds the same
    way i3/sway do. The most portable pattern is a *macro layer*: a single
    leader key (default: Caps) momentarily toggles a layer in which selected keys
    run commands.

    This generator uses a minimal `defsrc` containing only the leader key,
    optional collision selector keys, and the trigger keys referenced by your
    `bindings:`. With `fallthrough true`, keys outside `defsrc` are re-emitted.
    """

    bindings = list(getattr(project, "bindings", []) or [])

    lines: list[str] = []
    lines.append(f";; VHK KMonad bindings for project: {project.name}")
    lines.append(";; Generated by: vhk gen-kmonad-config")
    lines.append(";;")
    lines.append(";; Notes:")
    lines.append(";; - Requires allow-cmd true to enable cmd-button (dangerous if configs are untrusted).")
    lines.append(";; - Set $KBD_DEV to a device under /dev/input/by-id or edit input(...) below.")
    lines.append(";; - KMonad needs /dev/input + /dev/uinput permissions; see docs/KMONAD.md.")
    lines.append("")

    leader = _kmonad_key_from_i3(leader_key)
    if not leader:
        leader = "caps"

    # Default tap behaviour: Caps-as-Esc when used as the leader.
    if leader_tap is None:
        leader_tap = "esc" if leader == "caps" else leader
    leader_tap_k = _kmonad_key_from_i3(leader_tap) or leader_tap

    # Parse bindings into key -> list[HotkeyBinding]
    by_key: dict[str, list[object]] = {}
    for b in bindings:
        key = _parse_i3_hotkey_to_kmonad_key(getattr(b, "keys", ""))
        if not key:
            continue
        by_key.setdefault(key, []).append(b)

    if not by_key:
        lines.append(";; No supported bindings (could not parse key names).")
        return "\n".join(lines) + "\n"

    # Determine collisions (same trigger key used by multiple bindings).
    extras_by_key: dict[str, list[object]] = {}
    for k, lst in by_key.items():
        if len(lst) > 1:
            extras_by_key[k] = lst[1:]

    max_extra = max((len(v) for v in extras_by_key.values()), default=0)

    # Choose selector keys for collision layers.
    trigger_keys = set(by_key.keys())
    reserved = {leader} | trigger_keys
    candidates = [str(i) for i in range(1, 10)] + ["0"] + [f"f{i}" for i in range(1, 13)]
    alt_keys: list[str] = []
    for c in candidates:
        if len(alt_keys) >= max_extra:
            break
        if c not in reserved:
            alt_keys.append(c)
            reserved.add(c)

    # Build a stable key order for defsrc/deflayer columns.
    defsrc_keys: list[str] = [leader] + alt_keys + sorted(trigger_keys)

    # Build command aliases.
    cmd_aliases: list[tuple[str, str, str | None]] = []  # (name, expr, comment)

    def _binding_cmd(b) -> str:
        args = [vhk_cmd, "run", str(project_dir), b.macro, "--quiet"]
        if getattr(b, "vars", None):
            args += ["--vars", json.dumps(b.vars, ensure_ascii=False)]
        if getattr(b, "when", None):
            args += ["--require-window", b.when.model_dump_json(by_alias=True)]
        shell_cmd = " ".join(shlex.quote(a) for a in args)
        if run_on_release:
            # cmd-button takes (press_cmd, release_cmd). Use a POSIX no-op on press.
            return f"(cmd-button {_kmonad_escape_string_literal(':')} {_kmonad_escape_string_literal(shell_cmd)})"
        return f"(cmd-button {_kmonad_escape_string_literal(shell_cmd)})"

    # Primary mapping: first binding per trigger key.
    primary_for_key: dict[str, str] = {}
    # Alt mapping: layer index -> key -> alias
    alt_for_layer: list[dict[str, str]] = [dict() for _ in range(max_extra)]

    alias_idx = 0
    for key in sorted(by_key.keys()):
        lst = by_key[key]
        for j, b in enumerate(lst):
            alias_idx += 1
            a_name = f"m{alias_idx:03d}"
            expr = _binding_cmd(b)
            comment = getattr(b, "description", None) or f"{getattr(b, 'keys', key)} -> {b.macro}"
            cmd_aliases.append((a_name, expr, comment))

            if j == 0:
                primary_for_key[key] = a_name
            else:
                # j-1 maps to alt layer index.
                if j - 1 < len(alt_for_layer):
                    alt_for_layer[j - 1][key] = a_name

    # Leader + alt-switch aliases.
    lines.append("(defcfg")
    lines.append(f"  input ({input_expr})")
    lines.append(f"  output ({output_expr})")
    lines.append("  fallthrough true")
    lines.append("  allow-cmd true")
    lines.append(")")
    lines.append("")

    lines.append("(defsrc")
    lines.append("  " + " ".join(defsrc_keys))
    lines.append(")")
    lines.append("")

    lines.append("(defalias")
    lines.append(f"  vhk (tap-hold {leader_timeout_ms} {leader_tap_k} (layer-toggle vhk))")

    for i, ak in enumerate(alt_keys, start=1):
        # layer-next lets you pick the next keypress from that layer.
        lines.append(f"  alt{i} (layer-next vhk_alt{i})")

    for (name, expr, comment) in cmd_aliases:
        if comment:
            safe = str(comment).replace("\n", " ").strip()
            if safe:
                lines.append(f"  ;; {safe}")
        lines.append(f"  {name} {expr}")

    # Collision commentary.
    if extras_by_key:
        lines.append("  ;;")
        lines.append("  ;; Collision handling:")
        lines.append("  ;; - If multiple bindings share the same trigger key, the first binding is mapped directly.")
        lines.append("  ;; - Additional bindings are accessible by pressing the selector key (e.g. 1/2/3) then the trigger key.")

    lines.append(")")
    lines.append("")

    def _layer_row(mapping: dict[str, str] | None, *, selector: bool = False) -> str:
        out: list[str] = []
        for k in defsrc_keys:
            if k == leader:
                out.append("@vhk" if mapping is None else "_")
                continue
            # selector keys (alt keys)
            if k in alt_keys:
                if mapping is None:
                    out.append("_")
                else:
                    if selector:
                        idx = alt_keys.index(k) + 1
                        out.append(f"@alt{idx}")
                    else:
                        out.append("_")
                continue
            if mapping is None:
                out.append("_")
            else:
                a = mapping.get(k)
                out.append(f"@{a}" if a else "_")
        return "  " + " ".join(out)

    # Base layer: leader activates vhk; everything else passes through.
    lines.append("(deflayer base")
    lines.append(_layer_row(None))
    lines.append(")")
    lines.append("")

    # VHK layer: selector keys pick alt layers; trigger keys run primary mappings.
    prim_map = {k: primary_for_key.get(k, "") for k in defsrc_keys}
    lines.append("(deflayer vhk")
    lines.append(_layer_row(primary_for_key, selector=True))
    lines.append(")")
    lines.append("")

    # Alt layers.
    for i in range(max_extra):
        lines.append(f"(deflayer vhk_alt{i+1}")
        lines.append(_layer_row(alt_for_layer[i], selector=False))
        lines.append(")")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"




def _sxhkd_key_from_i3(key: str) -> str:
    """Best-effort mapping from i3 key names to sxhkd keysym names.

    sxhkd expects X11 keysym names (see `xev -event keyboard`).
    We keep this pragmatic: letters become lowercase, common names are normalized,
    and everything else is passed through.
    """

    k = (key or "").strip()
    if not k:
        return ""

    low = k.lower()
    specials = {
        "return": "Return",
        "enter": "Return",
        "space": "space",
        "tab": "Tab",
        "escape": "Escape",
        "esc": "Escape",
        "backspace": "BackSpace",
        "delete": "Delete",
        "insert": "Insert",
        "home": "Home",
        "end": "End",
        "prior": "Prior",  # PageUp
        "next": "Next",    # PageDown
        "page_up": "Prior",
        "page_down": "Next",
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
        "print": "Print",
        "pause": "Pause",
        "iso_left_tab": "Tab",
    }
    if low in specials:
        return specials[low]

    # Function keys.
    if re.fullmatch(r"f\d{1,2}", low):
        return low.upper()

    # Single letters: i3 configs often use uppercase.
    if len(k) == 1 and k.isalpha():
        return k.lower()

    return k


def _parse_i3_hotkey_to_sxhkd(keys: str) -> tuple[list[str], str]:
    """Parse i3-style Mod4+Shift+P into (mods, keysym)."""

    parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
    if not parts:
        return [], ""

    key = _sxhkd_key_from_i3(parts[-1])
    mod_raw = [p.lower() for p in parts[:-1]]

    mod_map = {
        "mod4": "super",
        "super": "super",
        "win": "super",
        "meta": "super",
        "mod1": "alt",
        "alt": "alt",
        "control": "ctrl",
        "ctrl": "ctrl",
        "shift": "shift",
    }

    mods: list[str] = []
    for m in mod_raw:
        mm = mod_map.get(m, None)
        if not mm:
            # Preserve raw "mod2/mod3..." for power users (xmodmap setups).
            if re.fullmatch(r"mod[1-5]", m):
                mm = m
        if mm and mm not in mods:
            mods.append(mm)

    # Canonical modifier ordering (matches most sxhkd configs).
    order = {"super": 0, "ctrl": 1, "control": 1, "alt": 2, "shift": 3}
    mods_sorted = sorted(mods, key=lambda x: order.get(x, 99))
    return mods_sorted, key


def _sxhkd_chord(mods: list[str], key: str, *, on_release: bool = False, passthrough: bool = False) -> str:
    key2 = key
    if on_release:
        key2 = "@" + key2
    if passthrough:
        key2 = "~" + key2
    if mods:
        return " + ".join(mods + [key2])
    return key2


def _generate_sxhkd_config(
    project_dir: Path,
    project,
    *,
    vhk_cmd: str = "vhk",
    leader: str | None = None,
    sticky_leader: bool = False,
    on_release: bool = False,
    passthrough: bool = False,
    via_bus: bool = False,
    bus_event: str = "hotkey",
    emit_cmd: str = "vhk-emit",
) -> str:
    """Generate an sxhkd config that runs project hotkeys.

    Notes
    -----
    - sxhkd is X11-only. On Wayland, prefer compositor binds, kanata, keyd, or kmonad exports.
    - Context filters (`when`) are implemented by passing `--require-window` to VHK,
      or (with --via-bus) by embedding a `require_window` selector into the bus payload.
    """

    lines: list[str] = []
    lines.append(f"# VHK sxhkd bindings for project: {project.name}")
    lines.append("# Generated by: vhk gen-sxhkd-config")
    lines.append("# Reload sxhkd after edits: pkill -USR1 -x sxhkd")
    lines.append("#")
    lines.append("# Notes:")
    lines.append("# - sxhkd uses X11 keysyms; see `xev -event keyboard` for names.")
    lines.append("# - If you want a leader/chord layer, use --leader (see man sxhkd).")
    if via_bus:
        sock_path = get_bus_socket_path(project_dir, configured=project.settings.bus_socket)
        lines.append(f"# - via bus: event='{bus_event}', socket='{sock_path}'")
        lines.append("#   NOTE: run a bus watcher with dispatch=true (see docs/BUS_EVENTS.md).")
    lines.append("")

    bindings = list(getattr(project, "bindings", []) or [])
    if not bindings:
        lines.append("# No bindings found. Add a `bindings:` list to project.yaml.")
        return "\n".join(lines) + "\n"

    leader_chord: str | None = None
    chord_sep = ":" if sticky_leader else ";"
    if leader:
        lmods, lkey = _parse_i3_hotkey_to_sxhkd(leader)
        if not lkey:
            raise ValueError(f"Could not parse leader hotkey: {leader!r}")
        leader_chord = _sxhkd_chord(lmods, lkey, on_release=on_release, passthrough=passthrough)

    # Track duplicates to help users notice collisions.
    seen: dict[str, int] = {}

    for idx, b in enumerate(bindings):
        mods, key = _parse_i3_hotkey_to_sxhkd(getattr(b, "keys", ""))
        if not key:
            continue

        chord = _sxhkd_chord(mods, key, on_release=on_release, passthrough=passthrough)
        hotkey = chord
        if leader_chord:
            hotkey = f"{leader_chord} {chord_sep} {chord}"

        seen[hotkey] = seen.get(hotkey, 0) + 1

        comment = getattr(b, "description", None)
        if comment:
            lines.append(f"# {comment}")

        if via_bus:
            rw = b.when.model_dump(by_alias=True) if getattr(b, "when", None) else None
            cmd = _bus_emit_cmd(
                sock_path,
                emit_cmd=emit_cmd,
                bus_event=bus_event,
                macro=b.macro,
                vars=getattr(b, "vars", None) or {},
                binding=_binding_label(b, idx),
                keys=b.keys,
                require_window=rw,
            )
        else:
            args = [vhk_cmd, "run", str(project_dir), b.macro, "--quiet"]
            if getattr(b, "vars", None):
                args += ["--vars", json.dumps(b.vars, ensure_ascii=False)]
            if getattr(b, "when", None):
                args += ["--require-window", b.when.model_dump_json(by_alias=True)]

            cmd = " ".join(shlex.quote(a) for a in args)

        lines.append(hotkey)
        lines.append(f"    {cmd}")
        lines.append("")

    # Warn about collisions in a friendly way (sxhkd uses last definition).
    collisions = [k for k, n in seen.items() if n > 1]
    if collisions:
        lines.append("# WARNING: duplicate hotkeys detected (sxhkd will use the last matching command).")
        for k in collisions:
            lines.append(f"# - {k}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


@app.command()
def gen_sxhkd_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to invoke VHK (default: vhk)"),
    leader: str | None = typer.Option(
        None,
        "--leader",
        help='Optional leader chord in i3-style notation (e.g. "Mod4+Space"). When set, bindings are emitted as chord chains.',
    ),
    sticky_leader: bool = typer.Option(
        False,
        "--sticky-leader",
        help="Use ':' instead of ';' for chord chains (keeps chain active until aborted).",
    ),
    on_release: bool = typer.Option(False, "--on-release", help="Trigger macros on key release (sxhkd '@' prefix)"),
    passthrough: bool = typer.Option(False, "--passthrough", help="Replay the captured key event to other clients (sxhkd '~' prefix)"),
    via_bus: bool = typer.Option(False, "--via-bus", help="Emit bus events instead of running macros directly"),
    bus_event: str = typer.Option("hotkey", "--bus-event", help="Bus event name to emit when using --via-bus"),
    emit_cmd: str = typer.Option("vhk-emit", "--emit-cmd", help="Emitter command (default: vhk-emit)"),
):
    """Generate an sxhkd config that runs project hotkeys.

    sxhkd is a popular X11 hotkey daemon (commonly used with bspwm/dwm/i3).
    VHK can export project bindings so you can keep hotkeys next to macros.

    See docs/SXHKD.md.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_sxhkd_config(
        project_dir,
        project,
        vhk_cmd=vhk_cmd,
        leader=leader,
        sticky_leader=sticky_leader,
        on_release=on_release,
        passthrough=passthrough,
        via_bus=via_bus,
        bus_event=bus_event,
        emit_cmd=emit_cmd,
    )
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote sxhkd config: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)



@app.command()
def gen_kmonad_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to invoke VHK (default: vhk)"),
    leader: str = typer.Option("caps", "--leader", help="Leader key used to activate the VHK macro layer (default: caps)"),
    leader_tap: str | None = typer.Option(None, "--leader-tap", help="Key emitted when leader is tapped (default: esc if leader=caps else leader)"),
    leader_timeout_ms: int = typer.Option(200, "--leader-timeout-ms", help="Tap/hold threshold for leader (default: 200ms)"),
    on_release: bool = typer.Option(False, "--on-release/--on-press", help="Run macros on release (default: press)"),
    input_expr: str = typer.Option(
        'device-file "$KBD_DEV" :ignore-missing true',
        "--input",
        help='KMonad defcfg input expression (without outer parentheses). Default uses $KBD_DEV.',
    ),
    output_expr: str = typer.Option(
        'uinput-sink "VHK KMonad output"',
        "--output",
        help='KMonad defcfg output expression (without outer parentheses).',
    ),
):
    """Generate a KMonad config that runs project hotkeys.

    Unlike i3/sway config snippets, this generator produces a *macro layer*
    config (leader key + trigger keys) that is portable across X11/Wayland/TTY.

    See docs/KMONAD.md.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_kmonad_config(
        project_dir,
        project,
        vhk_cmd=vhk_cmd,
        leader_key=leader,
        leader_tap=leader_tap,
        leader_timeout_ms=leader_timeout_ms,
        run_on_release=on_release,
        input_expr=input_expr,
        output_expr=output_expr,
    )

    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote KMonad config: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


def _xremap_key_from_i3(key: str) -> str:
    """Best-effort mapping from i3 key names to xremap key tokens."""

    k = (key or "").strip()
    if not k:
        return ""

    low = k.lower()
    specials = {
        "return": "Enter",
        "enter": "Enter",
        "space": "Space",
        "tab": "Tab",
        "escape": "Esc",
        "esc": "Esc",
        "backspace": "Backspace",
        "delete": "Delete",
        "insert": "Insert",
        "home": "Home",
        "end": "End",
        "prior": "PageUp",
        "next": "PageDown",
        "page_up": "PageUp",
        "page_down": "PageDown",
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
        "print": "Print",
        "pause": "Pause",
        "capslock": "CapsLock",
        "xf86audiolowervolume": "VolumeDown",
        "xf86audioraisevolume": "VolumeUp",
        "xf86audiomute": "Mute",
        "xf86audioplay": "PlayPause",
        "xf86audiopause": "PlayPause",
        "xf86audionext": "NextSong",
        "xf86audioprev": "PreviousSong",
        "xf86audiostop": "StopCD",
        "xf86monbrightnessup": "BrightnessUp",
        "xf86monbrightnessdown": "BrightnessDown",
    }
    if low in specials:
        return specials[low]

    if re.fullmatch(r"f\d{1,2}", low):
        return low.upper()

    if len(k) == 1 and k.isalpha():
        return k.lower()

    if len(k) == 1:
        return k

    if low.startswith("kp_"):
        return "kp" + low[3:]

    return low


def _parse_i3_hotkey_to_xremap(keys: str) -> str:
    """Parse an i3-style key chord into xremap's MOD-KEY syntax."""

    parts = [p.strip() for p in (keys or "").split("+") if p.strip()]
    if not parts:
        return ""

    key = _xremap_key_from_i3(parts[-1])
    if not key:
        return ""

    mod_map = {
        "control": "C",
        "ctrl": "C",
        "mod1": "Alt",
        "alt": "Alt",
        "shift": "Shift",
        "mod4": "SUPER",
        "super": "SUPER",
        "win": "SUPER",
        "meta": "SUPER",
    }
    mod_order = {"C": 0, "Alt": 1, "SUPER": 2, "Shift": 3}
    mods = []
    for raw in parts[:-1]:
        token = mod_map.get(raw.lower())
        if token and token not in mods:
            mods.append(token)
    mods.sort(key=lambda item: mod_order.get(item, 99))
    if not mods:
        return key
    return "-".join([*mods, key])


def _xremap_regex_literal(pattern: str) -> str:
    escaped = str(pattern).replace('\\', '\\\\').replace('/', '\\/')
    return f"/{escaped}/"


def _xremap_filter_value(value: str, *, regex: bool) -> str:
    if regex:
        return _xremap_regex_literal(str(value))
    return str(value)


def _xremap_selector_filters(selector: I3WindowSelector | None) -> dict[str, Any]:
    """Translate a VHK window selector into the subset xremap can express.

    xremap can scope on application names (exact strings or `/regex/`) and
    window-title regexes, but it does not model the full VHK selector contract.
    The generator still passes `--require-window` to VHK at runtime so the
    original selector remains the final authority.
    """

    if selector is None:
        return {}

    out: dict[str, Any] = {}
    app_tokens: list[str] = []
    if getattr(selector, 'app_id', None):
        app_tokens.append(
            _xremap_filter_value(
                str(getattr(selector, 'app_id')),
                regex=bool(getattr(selector, 'app_id_regex', False)),
            )
        )
    if getattr(selector, 'wm_class', None):
        wm_class = str(getattr(selector, 'wm_class'))
        if wm_class not in app_tokens:
            app_tokens.append(wm_class)
    if app_tokens:
        out['application'] = {'only': app_tokens if len(app_tokens) > 1 else app_tokens[0]}
    if getattr(selector, 'title', None):
        title = str(getattr(selector, 'title'))
        if bool(getattr(selector, 'title_regex', False)):
            window_filter = _xremap_regex_literal(title)
        else:
            window_filter = f"/^{re.escape(title)}$/"
        out['window'] = {'only': window_filter}
    return out


def _xremap_selector_export_gaps(selector: I3WindowSelector | None) -> list[str]:
    if selector is None:
        return []
    unsupported: list[str] = []
    for field in (
        'instance',
        'window_role',
        'pid',
        'workspace',
        'urgent',
        'focused',
        'visible',
        'fullscreen',
        'fullscreen_mode',
        'floating',
        'sticky',
        'minimized',
        'hidden',
        'mapped',
        'pinned',
    ):
        value = getattr(selector, field, None)
        if value is not None:
            unsupported.append(field)
    return unsupported


def _xremap_selector_specificity(selector: I3WindowSelector | None) -> int:
    if selector is None:
        return 0
    score = 0
    if getattr(selector, 'app_id', None):
        score += 4
    if getattr(selector, 'wm_class', None):
        score += 3
    if getattr(selector, 'title', None):
        score += 2
    if getattr(selector, 'pid', None):
        score += 1
    if getattr(selector, 'workspace', None):
        score += 1
    return score


def _generate_xremap_config(
    project_dir: Path,
    project,
    *,
    vhk_cmd: str = 'vhk',
    exact_match: bool = True,
    keypress_delay_ms: int = 0,
    throttle_ms: int = 0,
) -> str:
    """Generate an xremap config that launches VHK macros.

    This keeps app-aware remap ownership in xremap while still letting VHK own
    the macro graph. Generated entries stay intentionally narrow: one keymap
    item per binding, ordered from most-specific selector to least-specific, so
    application/window-scoped overrides behave like xremap's README describes.
    """

    lines: list[str] = []
    lines.append(f"# VHK xremap bindings for project: {project.name}")
    lines.append("# Generated by: vhk gen-xremap-config")
    lines.append("#")
    lines.append("# Notes:")
    lines.append("# - xremap keymaps launch on key press; combo on-release hooks are not available in the same way as Kanata/KMonad.")
    lines.append("# - VHK still receives --require-window for scoped bindings so the original selector remains the final gate.")
    lines.append("# - app_id / WM_CLASS values vary by compositor/desktop; validate them with xremap's window-listing tools on the target host.")
    lines.append("")

    bindings = list(getattr(project, 'bindings', []) or [])
    if not bindings:
        lines.append("keymap: []")
        return "\n".join(lines) + "\n"

    config: dict[str, Any] = {}
    if keypress_delay_ms > 0:
        config['keypress_delay_ms'] = int(keypress_delay_ms)
    if throttle_ms > 0:
        config['throttle_ms'] = int(throttle_ms)

    keymaps: list[dict[str, Any]] = []
    sorted_bindings = sorted(
        bindings,
        key=lambda item: (
            -_xremap_selector_specificity(getattr(item, 'when', None)),
            str(getattr(item, 'keys', '') or ''),
            str(getattr(item, 'macro', '') or ''),
        ),
    )

    for idx, binding in enumerate(sorted_bindings, start=1):
        combo = _parse_i3_hotkey_to_xremap(getattr(binding, 'keys', ''))
        if not combo:
            continue

        args = [vhk_cmd, 'run', str(project_dir), binding.macro, '--quiet']
        if getattr(binding, 'vars', None):
            args += ['--vars', json.dumps(binding.vars, ensure_ascii=False)]
        if getattr(binding, 'when', None):
            args += ['--require-window', binding.when.model_dump_json(by_alias=True)]

        item: dict[str, Any] = {
            'name': str(getattr(binding, 'description', None) or getattr(binding, 'macro', None) or f'VHK binding {idx}'),
            'remap': {
                combo: {
                    'launch': args,
                }
            },
        }
        if exact_match:
            item['exact_match'] = True
        item.update(_xremap_selector_filters(getattr(binding, 'when', None)))
        keymaps.append(item)

    if not keymaps:
        lines.append("keymap: []")
        return "\n".join(lines) + "\n"

    config['keymap'] = keymaps
    lines.append(yaml.safe_dump(config, sort_keys=False, allow_unicode=True).rstrip())
    return "\n".join(lines) + "\n"


@app.command()
def gen_xremap_config(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, '--out', help='Write to a file instead of stdout'),
    vhk_cmd: str = typer.Option('vhk', '--vhk-cmd', help='Command to invoke VHK (default: vhk)'),
    exact_match: bool = typer.Option(True, '--exact-match/--superset-match', help='Require an exact modifier set for generated bindings (default: exact-match).'),
    keypress_delay_ms: int = typer.Option(0, '--keypress-delay-ms', min=0, help='Optional xremap keypress_delay_ms value for apps that miss fast synthetic keys.'),
    throttle_ms: int = typer.Option(0, '--throttle-ms', min=0, help='Optional xremap throttle_ms value for conservative Wayland apps.'),
):
    """Generate an xremap config that runs project hotkeys.

    This is the app-aware remapper/export lane for Linux sessions where xremap
    owns the trigger path and VHK owns the macro/runtime path.

    See docs/XREMAP.md.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    text = _generate_xremap_config(
        project_dir,
        project,
        vhk_cmd=vhk_cmd,
        exact_match=exact_match,
        keypress_delay_ms=keypress_delay_ms,
        throttle_ms=throttle_ms,
    )
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote xremap config: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)



def _espanso_regex_literal(text: str) -> str:
    return _I3_REGEX_META_RE.sub(r"\\", text)


def _extract_form_fields(layout: str) -> list[str]:
    fields: list[str] = []
    for m in re.finditer(r"\[\[([A-Za-z_][A-Za-z0-9_]*)\]\]", layout or ""):
        name = m.group(1)
        if name not in fields:
            fields.append(name)
    return fields


def _espanso_filters_from_selector(sel: I3WindowSelector) -> dict[str, str]:
    filters: dict[str, str] = {}

    class_parts: list[str] = []
    if sel.wm_class:
        class_parts.append(_espanso_regex_literal(sel.wm_class))
    if getattr(sel, "app_id", None):
        app_id = getattr(sel, "app_id")
        app_id_regex = bool(getattr(sel, "app_id_regex", False))
        class_parts.append(app_id if app_id_regex else _espanso_regex_literal(app_id))
    if class_parts:
        filters["filter_class"] = "|".join(class_parts)

    if sel.title:
        filters["filter_title"] = sel.title if sel.title_regex else _espanso_regex_literal(sel.title)

    return filters


def _slugify_filters(filters: dict[str, str]) -> str:
    pieces: list[str] = []
    for k in sorted(filters.keys()):
        v = filters[k]
        short = re.sub(r"[^A-Za-z0-9]+", "_", v).strip("_")
        if len(short) > 32:
            short = short[:32]
        pieces.append(f"{k.replace('filter_', '')}_{short}" if short else k.replace('filter_', ''))
    base = "__".join(pieces) if pieces else "scoped"
    digest = hashlib.sha1("|".join(f"{k}={filters[k]}" for k in sorted(filters.keys())).encode("utf-8")).hexdigest()[:8]
    return f"{base}__{digest}"


def _espanso_filter_key(filters: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(k), str(v)) for k, v in filters.items()))


def _espanso_filters_from_key(key: tuple[tuple[str, str], ...]) -> dict[str, str]:
    return {k: v for k, v in key}


def _espanso_filters_compatible(left: dict[str, str], right: dict[str, str]) -> bool:
    for k in set(left.keys()).intersection(right.keys()):
        if left[k] != right[k]:
            return False
    return True


def _espanso_filter_subset(subset_filters: dict[str, str], superset_filters: dict[str, str]) -> bool:
    for k, v in subset_filters.items():
        if superset_filters.get(k) != v:
            return False
    return True


def _plan_espanso_scoped_configs(
    actual_groups: dict[tuple[tuple[str, str], ...], dict[str, object]],
) -> list[dict[str, object]]:
    all_keys: set[tuple[tuple[str, str], ...]] = set(actual_groups.keys())
    changed = True
    while changed:
        changed = False
        current = list(all_keys)
        for i, left_key in enumerate(current):
            left = _espanso_filters_from_key(left_key)
            for right_key in current[i + 1 :]:
                right = _espanso_filters_from_key(right_key)
                if not _espanso_filters_compatible(left, right):
                    continue
                merged = {**left, **right}
                merged_key = _espanso_filter_key(merged)
                if merged_key not in all_keys:
                    all_keys.add(merged_key)
                    changed = True

    configs: list[dict[str, object]] = []
    for key in all_keys:
        filters = _espanso_filters_from_key(key)
        include_keys = [
            actual_key
            for actual_key in actual_groups.keys()
            if _espanso_filter_subset(_espanso_filters_from_key(actual_key), filters)
        ]
        configs.append(
            {
                "key": key,
                "filters": filters,
                "slug": _slugify_filters(filters),
                "synthetic": key not in actual_groups,
                "specificity": len(filters),
                "include_keys": sorted(
                    include_keys,
                    key=lambda item: (
                        -len(item),
                        _slugify_filters(_espanso_filters_from_key(item)),
                    ),
                ),
            }
        )

    configs.sort(
        key=lambda item: (
            -int(item["specificity"]),
            -len(item["include_keys"]),
            str(item["slug"]),
        )
    )
    return configs


def _render_espanso_package_readme(
    *,
    project_name: str,
    global_match_filename: str | None,
    config_entries: list[dict[str, object]],
) -> str:
    lines: list[str] = []
    lines.append(f"# VHK Espanso package: {project_name}")
    lines.append("")
    lines.append("Generated by `vhk gen-espanso --package-dir`.")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Espanso app-specific configurations are not supported on Wayland.")
    lines.append("- Espanso activates only one app-specific config at a time, so VHK prefixes config filenames by specificity so more-specific configs sort earlier.")
    lines.append("- When VHK can prove scoped configs overlap cleanly, it generates composite configs that include the less-specific match files they subsume.")
    lines.append("")
    lines.append("## Global matches")
    lines.append("")
    if global_match_filename:
        lines.append(f"- `match/{global_match_filename}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Scoped configs")
    lines.append("")
    if not config_entries:
        lines.append("- none")
    for entry in config_entries:
        config_file = entry.get("config_filename")
        filters = entry.get("filters") or {}
        include_files = entry.get("extra_includes") or []
        synthetic = bool(entry.get("synthetic"))
        filter_bits = ", ".join(f"{k}={v}" for k, v in sorted(filters.items())) or "(none)"
        lines.append(f"- `config/{config_file}` — {filter_bits}{' [synthetic composite]' if synthetic else ''}")
        for rel in include_files:
            lines.append(f"  - includes `{rel}`")
    lines.append("")
    return "\n".join(lines) + "\n"

@app.command()
def gen_espanso(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path | None = typer.Option(None, "--out", help="Write to a file instead of stdout"),
    package_dir: Path | None = typer.Option(
        None,
        "--package-dir",
        help="Write an Espanso-ready directory tree (match/ + config/) instead of a single match file",
    ),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to invoke VHK (default: vhk)"),
    include_disabled: bool = typer.Option(False, "--include-disabled", help="Include disabled hotstrings"),
    include_scoped: bool = typer.Option(
        False,
        "--include-scoped",
        help="Include hotstrings with 'when' even when generating a single match file (they will be global)",
    ),
    as_json: bool = typer.Option(False, "--json", help="Output JSON instead of YAML"),
):
    """Generate an Espanso match file from project.yaml hotstrings.

    This enables 'hotstrings' (text expansion triggers) without VHK needing to
    intercept global keyboard input itself.

    See docs/HOTSTRINGS.md for recommended patterns.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    def _espanso_regex_literal(text: str) -> str:
        # Espanso filters are regex-based.
        return _I3_REGEX_META_RE.sub(r"\\\1", text)

    def _extract_form_fields(layout: str) -> list[str]:
        fields: list[str] = []
        for m in re.finditer(r"\[\[([A-Za-z_][A-Za-z0-9_]*)\]\]", layout or ""):
            name = m.group(1)
            if name not in fields:
                fields.append(name)
        return fields

    def _espanso_filters_from_selector(sel: I3WindowSelector) -> dict[str, str]:
        filters: dict[str, str] = {}

        class_parts: list[str] = []
        if sel.wm_class:
            class_parts.append(_espanso_regex_literal(sel.wm_class))
        if getattr(sel, "app_id", None):
            app_id = getattr(sel, "app_id")
            app_id_regex = bool(getattr(sel, "app_id_regex", False))
            class_parts.append(app_id if app_id_regex else _espanso_regex_literal(app_id))
        if class_parts:
            # Use alternation if both are present.
            filters["filter_class"] = "|".join(class_parts)

        if sel.title:
            filters["filter_title"] = sel.title if sel.title_regex else _espanso_regex_literal(sel.title)

        return filters

    def _slugify_filters(filters: dict[str, str]) -> str:
        pieces: list[str] = []
        for k in sorted(filters.keys()):
            v = filters[k]
            short = re.sub(r"[^A-Za-z0-9]+", "_", v).strip("_")
            if len(short) > 32:
                short = short[:32]
            pieces.append(f"{k.replace('filter_', '')}_{short}" if short else k.replace('filter_', ''))
        base = "__".join(pieces) if pieces else "scoped"
        digest = hashlib.sha1("|".join(f"{k}={filters[k]}" for k in sorted(filters.keys())).encode("utf-8")).hexdigest()[:8]
        return f"{base}__{digest}"

    def _build_match(hs) -> dict:
        # If this hotstring defines a form, inject fields into the initial vars.
        form_var_name = "form1"
        form_vars: dict[str, str] = {}
        form_entry: dict | None = None
        if hs.form_layout:
            form_entry = {
                "name": form_var_name,
                "type": "form",
                "params": {"layout": hs.form_layout},
            }
            for field in _extract_form_fields(hs.form_layout):
                form_vars[field] = f"{{{{{form_var_name}.{field}}}}}"

        initial_vars = {**hs.vars, **form_vars} if (hs.vars or form_vars) else {}

        args = [vhk_cmd, "run", str(project_dir), hs.macro, "--quiet"]
        if initial_vars:
            args += ["--vars", json.dumps(initial_vars, ensure_ascii=False)]
        if hs.mode == "return":
            args += ["--print-return", "--return-var", hs.return_var]

        cmd = " ".join(shlex.quote(a) for a in args)

        var_list: list[dict] = []
        if form_entry:
            var_list.append(form_entry)
        var_list.append({"name": "output", "type": "shell", "params": {"cmd": cmd}})

        match: dict = {
            "trigger": hs.trigger,
            "replace": "{{output}}",
            "vars": var_list,
        }
        if hs.description:
            match["label"] = hs.description
        if hs.force_mode:
            match["force_mode"] = hs.force_mode
        return match

    if package_dir:
        package_dir = package_dir.expanduser().resolve()
        match_dir = package_dir / "match"
        config_dir = package_dir / "config"
        match_dir.mkdir(parents=True, exist_ok=True)
        config_dir.mkdir(parents=True, exist_ok=True)

        global_matches: list[dict] = []
        grouped: dict[tuple[tuple[str, str], ...], dict[str, object]] = {}

        for hs in project.hotstrings:
            if (not hs.enabled) and (not include_disabled):
                continue
            if hs.when:
                filters = _espanso_filters_from_selector(hs.when)
                key = _espanso_filter_key(filters)
                if key not in grouped:
                    grouped[key] = {"filters": filters, "hotstrings": []}
                grouped[key]["hotstrings"].append(hs)
            else:
                global_matches.append(_build_match(hs))

        written: list[Path] = []
        global_filename: str | None = None

        if global_matches:
            global_filename = f"vhk_{project.name}.yml"
            global_path = match_dir / global_filename
            global_path.write_text(yaml.safe_dump({"matches": global_matches}, sort_keys=False))
            written.append(global_path)

        match_files: dict[tuple[tuple[str, str], ...], str] = {}
        for key, entry in grouped.items():
            filters = entry["filters"]  # type: ignore[assignment]
            hotstrings = entry["hotstrings"]  # type: ignore[assignment]
            slug = _slugify_filters(filters)
            match_filename = f"_vhk_{project.name}__{slug}.yml"
            match_path = match_dir / match_filename
            match_path.write_text(yaml.safe_dump({"matches": [_build_match(hs) for hs in hotstrings]}, sort_keys=False))
            written.append(match_path)
            match_files[key] = match_filename

        config_entries = _plan_espanso_scoped_configs(grouped)
        rendered_configs: list[dict[str, object]] = []
        for order, entry in enumerate(config_entries):
            filters = entry["filters"]  # type: ignore[assignment]
            include_keys = entry["include_keys"]  # type: ignore[assignment]
            slug = str(entry["slug"])
            config_filename = f"vhk_{project.name}__{order:02d}__{slug}.yml"
            extra_includes = [f"../match/{match_files[item]}" for item in include_keys if item in match_files]
            cfg = {**filters, "extra_includes": extra_includes}
            config_path = config_dir / config_filename
            config_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
            written.append(config_path)
            rendered_configs.append(
                {
                    "config_filename": config_filename,
                    "filters": filters,
                    "synthetic": bool(entry["synthetic"]),
                    "extra_includes": extra_includes,
                    "specificity": int(entry["specificity"]),
                    "include_keys": [list(item) for item in include_keys],
                }
            )

        readme_path = package_dir / "README.md"
        readme_path.write_text(
            _render_espanso_package_readme(
                project_name=project.name,
                global_match_filename=global_filename,
                config_entries=rendered_configs,
            )
        )
        written.append(readme_path)

        manifest_path = package_dir / "pack.json"
        manifest = {
            "project": project.name,
            "global_match_filename": global_filename,
            "scoped_match_file_count": len(match_files),
            "scoped_config_count": len(rendered_configs),
            "synthetic_config_count": sum(1 for item in rendered_configs if item["synthetic"]),
            "configs": rendered_configs,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        written.append(manifest_path)

        console.print(f"Wrote Espanso package directory: [bold]{package_dir}[/bold]")
        for p in written:
            console.print(f"  - {p.relative_to(package_dir)}")
        return

    matches: list[dict] = []
    for hs in project.hotstrings:
        if (not hs.enabled) and (not include_disabled):
            continue

        if hs.when and (not include_scoped):
            # Espanso can't scope matches per app within a single match file;
            # users should generate app-specific config files with --package-dir.
            continue

        matches.append(_build_match(hs))

    payload = {"matches": matches}

    if as_json:
        text = json.dumps(payload, indent=2) + "\n"
    else:
        text = yaml.safe_dump(payload, sort_keys=False)

    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        console.print(f"Wrote Espanso match file: [bold]{out_path}[/bold]")
    else:
        sys.stdout.write(text)


@app.command()
def bundle(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path = typer.Argument(..., help="Output .zip path"),
    deterministic: bool = typer.Option(False, "--deterministic", help="Normalize timestamps/order for best-effort reproducible bundles"),
    source_date_epoch: int | None = typer.Option(None, "--source-date-epoch", min=0, help="UTC epoch used for deterministic bundle timestamps (overrides SOURCE_DATE_EPOCH)"),
):
    """Create a shareable bundle (zip) for the project folder."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_project(project_dir, out_path, deterministic=deterministic, source_date_epoch=source_date_epoch)
    console.print(f"Wrote bundle: [bold]{out_path}[/bold]")


@app.command("bundle-stage")
def bundle_stage_cmd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_path: Path = typer.Argument(..., help="Output .zip path"),
    target_profile: str = typer.Option(..., "--target-profile", help="Release-stage profile to bundle (for example gnome-wayland)"),
    deterministic: bool = typer.Option(False, "--deterministic", help="Normalize timestamps/order for best-effort reproducible bundles"),
    source_date_epoch: int | None = typer.Option(None, "--source-date-epoch", min=0, help="UTC epoch used for deterministic bundle timestamps (overrides SOURCE_DATE_EPOCH)"),
):
    """Create a shareable bundle from one materialized release-stage lane."""

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_release_stage(
        project_dir,
        out_path,
        profile_id=target_profile,
        deterministic=deterministic,
        source_date_epoch=source_date_epoch,
    )
    console.print(f"Wrote release-stage bundle: [bold]{out_path}[/bold]")


@app.command("materialize-bundle")
def materialize_bundle_cmd(
    bundle_zip: Path = typer.Argument(..., exists=True, dir_okay=False, file_okay=True, help="Bundle .zip to extract"),
    out_dir: Path = typer.Argument(..., help="Target directory that will receive the extracted bundle root"),
    verify: bool = typer.Option(True, "--verify/--no-verify", help="Verify the embedded bundle manifest before extraction"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable extraction metadata"),
):
    """Safely materialize a VHK bundle into one target directory."""

    try:
        payload = materialize_bundle(bundle_zip, out_dir, verify=verify, force=True)
    except BundleMaterializeError as exc:
        if as_json:
            sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}, indent=2) + "\n")
        else:
            console.print(f"[red]Failed to materialize bundle:[/red] {exc}")
        raise typer.Exit(code=1)

    if as_json:
        sys.stdout.write(json.dumps({"ok": True, **payload}, indent=2) + "\n")
        raise typer.Exit(0)

    console.print(f"[green]Materialized bundle:[/green] {bundle_zip}")
    console.print(f"[dim]Extract root:[/dim] {payload.get('extract_root')}")
    console.print(f"[dim]Project root:[/dim] {payload.get('project_root')}")
    raise typer.Exit(0)


@app.command("verify-bundle")
def verify_bundle_cmd(
    bundle_zip: Path = typer.Argument(..., exists=True, dir_okay=False, file_okay=True, help="Bundle .zip to verify"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable JSON"),
):
    """Verify a bundle against its embedded manifest (checksums + sizes)."""

    ok, errors = verify_bundle(bundle_zip)
    if as_json:
        sys.stdout.write(json.dumps({"ok": ok, "errors": errors}, indent=2) + "\n")
        raise typer.Exit(0 if ok else 1)

    if ok:
        console.print("[green]OK[/green] Bundle matches manifest")
        raise typer.Exit(0)

    console.print("[red]FAIL[/red] Bundle failed verification")
    for e in errors:
        console.print(f"- {e}")
    raise typer.Exit(1)


@app.command("inspect-bundle")
def inspect_bundle_cmd(
    bundle_zip: Path = typer.Argument(..., exists=True, dir_okay=False, file_okay=True, help="Bundle .zip to inspect"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable JSON"),
):
    """Inspect bundle metadata, including embedded support-claim snapshots when present."""

    payload = inspect_bundle(bundle_zip)
    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        raise typer.Exit(0)

    console.print(f"[bold]Bundle:[/bold] {payload.get('bundle')}")
    console.print(f"[dim]Kind:[/dim] {payload.get('bundle_kind') or 'project'}")
    console.print(f"[dim]Project:[/dim] {payload.get('project_dir_name') or '?'}")
    if payload.get('bundle_root_name') and payload.get('bundle_root_name') != payload.get('project_dir_name'):
        console.print(f"[dim]Bundle root:[/dim] {payload.get('bundle_root_name')}")
    console.print(f"[dim]Created:[/dim] {payload.get('created_at') or '?'}")
    console.print(f"[dim]Files:[/dim] {payload.get('file_count') or 0} ({payload.get('total_bytes') or 0} bytes)")
    if payload.get('deterministic'):
        console.print(f"[dim]Deterministic:[/dim] yes ({payload.get('source_date_epoch')})")

    stage = payload.get('release_stage')
    if isinstance(stage, dict):
        console.print("")
        console.print("[bold]Embedded release-stage snapshot[/bold]")
        console.print(f"[dim]Profile:[/dim] {stage.get('profile_id') or '?'}")
        console.print(f"[dim]Title:[/dim] {stage.get('title') or '?'}")
        console.print(f"[dim]Release level:[/dim] {stage.get('release_level') or '?'}")
        console.print(f"[dim]Deploy style:[/dim] {stage.get('deploy_style') or '?'}")

    support = payload.get('support')
    if not isinstance(support, dict):
        console.print("[yellow]No bundle support metadata embedded.[/yellow]")
        raise typer.Exit(0)

    if support.get('error'):
        console.print(f"[red]Support metadata unavailable:[/red] {support.get('error')}")
        raise typer.Exit(0)

    console.print("")
    console.print("[bold]Embedded support snapshot[/bold]")
    console.print(f"[dim]Source:[/dim] {support.get('claim_source') or 'unknown'}")
    if support.get('claims_file_present'):
        console.print("[dim]Claims file:[/dim] present")
    level_counts = support.get('level_counts') or {}
    if isinstance(level_counts, dict) and level_counts:
        level_bits = [f"{key}={level_counts[key]}" for key in sorted(level_counts)]
        console.print(f"[dim]Claim levels:[/dim] {' · '.join(level_bits)}")
    status_counts = support.get('status_counts') or {}
    if isinstance(status_counts, dict) and status_counts:
        status_bits = [f"{key}={status_counts[key]}" for key in sorted(status_counts)]
        console.print(f"[dim]Audit status:[/dim] {' · '.join(status_bits)}")
    publish_docs_present = [str(x) for x in list(support.get('publish_docs_present') or []) if str(x)]
    if publish_docs_present:
        console.print(f"[dim]Publish docs:[/dim] {len(publish_docs_present)} embedded")

    targets = [dict(item) for item in list(support.get('targets') or []) if isinstance(item, dict)]
    if targets:
        tbl = Table(title="Bundle target claims")
        tbl.add_column("Target")
        tbl.add_column("Claim")
        tbl.add_column("Recommended")
        tbl.add_column("Status")
        tbl.add_column("Proof")
        for item in targets[:10]:
            missing = int(len(list(item.get('artifacts_missing') or [])))
            present = int(len(list(item.get('artifacts_present') or [])))
            proof = f"{present} ok"
            if missing:
                proof += f" / {missing} missing"
            tbl.add_row(
                str(item.get('title') or item.get('target') or 'target'),
                str(item.get('claim_level') or 'unsupported'),
                str(item.get('recommended_level') or 'unsupported'),
                str(item.get('status') or 'unknown'),
                proof,
            )
        console.print(tbl)
    raise typer.Exit(0)


@app.command("select-region")
def select_region_cmd(
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON"),
    project_dir: Path | None = typer.Option(None, "--project", exists=True, file_okay=False, dir_okay=True, help="Optional project folder to write the region into"),
    name: str | None = typer.Option(None, "--name", help="Optional region name (writes to project.yaml regions)"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite an existing region with the same name"),
):
    """Interactively select a rectangle (slop on X11, slurp on Wayland).

    If --project and --name are provided, the region is saved into the project's
    `project.yaml` under `regions:` and can be referenced in macros as `region: "@<name>"`.
    """

    r = select_region()

    wrote = False
    if project_dir is not None and name is not None:
        import yaml

        project_dir = project_dir.expanduser().resolve()
        manifest = project_dir / "project.yaml"
        if not manifest.exists():
            raise FileNotFoundError(f"Missing project.yaml in {project_dir}")

        doc = yaml.safe_load(manifest.read_text())
        if doc is None:
            doc = {}
        if not isinstance(doc, dict):
            raise ValueError("project.yaml must be a mapping")

        regions = doc.get("regions") or {}
        if not isinstance(regions, dict):
            raise ValueError("project.yaml 'regions' must be a mapping when present")

        key = str(name).strip()
        if not key:
            raise ValueError("--name must be non-empty")
        if (key in regions) and not overwrite:
            raise ValueError(f"Region {key!r} already exists. Use --overwrite to replace it.")

        regions[key] = r.model_dump()
        doc["regions"] = regions
        manifest.write_text(yaml.safe_dump(doc, sort_keys=False))
        wrote = True

    payload = r.model_dump()
    if name is not None:
        payload["name"] = str(name)
    if wrote:
        payload["saved_to"] = str((project_dir / "project.yaml") if project_dir else "")

    if as_json:
        sys.stdout.write(json.dumps(payload) + "\n")
    else:
        sys.stdout.write(f"{r.w}x{r.h}+{r.x}+{r.y}\n")


@app.command("select-region-cmd")
def select_region_cmd_alias(
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON"),
    project_dir: Path | None = typer.Option(None, "--project", exists=True, file_okay=False, dir_okay=True, help="Optional project folder to write the region into"),
    name: str | None = typer.Option(None, "--name", help="Optional region name (writes to project.yaml regions)"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite an existing region with the same name"),
):
    """Deprecated alias for `vhk select-region` (kept for backwards-compatibility)."""

    return select_region_cmd(as_json=as_json, project_dir=project_dir, name=name, overwrite=overwrite)


@app.command()
def portal_screenshot(
    out_path: Path | None = typer.Option(None, "--out", help="Copy the portal screenshot to this path"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Hint for portal UI customization"),
    timeout_s: float = typer.Option(90.0, "--timeout", help="Time to wait for the portal response"),
    as_json: bool = typer.Option(False, "--json", help="Print JSON with the returned URI"),
):
    """Take a screenshot via the XDG Desktop Portal (best-effort).

    This is a cross-desktop fallback for Wayland setups where grim/slurp are
    unavailable (or blocked). The portal is typically interactive and will
    prompt for permission.
    """

    from vhk.system.portal import portal_screenshot_uri, save_portal_screenshot

    if out_path is not None:
        out_path = out_path.expanduser().resolve()
        saved, uri = save_portal_screenshot(out_path, interactive=interactive, timeout_s=timeout_s)
        payload = {"status": "ok", "path": str(saved), "uri": uri}
    else:
        resp = portal_screenshot_uri(interactive=interactive, timeout_s=timeout_s)
        payload = {"status": "ok" if resp.response == 0 else "fail", "response": resp.response, "uri": resp.uri}

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        if payload.get("uri"):
            sys.stdout.write(str(payload["uri"]) + "\n")
        else:
            sys.stdout.write(f"Portal screenshot failed (response={payload.get('response')})\n")


@app.command()
def portal_pick_color(
    timeout_s: float = typer.Option(90.0, "--timeout", help="Time to wait for the portal response"),
    as_json: bool = typer.Option(False, "--json", help="Print JSON"),
):
    """Pick a pixel color via the XDG Desktop Portal (best-effort)."""

    import vhk.system.portal as portal_mod

    resp = portal_mod.portal_pick_color(timeout_s=timeout_s)
    if resp.response != 0 or not resp.color:
        payload = {"status": "fail", "response": resp.response}
    else:
        payload = {
            "status": "ok",
            "response": resp.response,
            "rgb01": [resp.color[0], resp.color[1], resp.color[2]],
            "hex": portal_mod.rgb01_to_hex(resp.color),
        }

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        if payload.get("status") == "ok":
            sys.stdout.write(f"{payload['hex']}\n")
        else:
            sys.stdout.write(f"Portal pick-color failed (response={payload.get('response')})\n")

@app.command()
def pick_color(
    x: int | None = typer.Option(None, "--x", help="X coordinate (screen pixels)"),
    y: int | None = typer.Option(None, "--y", help="Y coordinate (screen pixels)"),
    portal: bool = typer.Option(False, "--portal", help="Force XDG portal pick-color (Wayland; interactive)"),
    timeout_s: float = typer.Option(90.0, "--timeout", help="Portal timeout (seconds)"),
    as_json: bool = typer.Option(False, "--json", help="Print JSON"),
):
    """Pick the color at a screen coordinate (or at the current cursor position).

    This is intended as a *macro authoring* helper:
    - On X11, it samples the pixel under the cursor using a 1x1 screenshot.
    - On Wayland, global cursor position or screenshot capture may be restricted;
      if needed, VHK falls back to the XDG Desktop Portal color picker
      (typically interactive).
    """

    from vhk.vision.pixel import pixel_get_color_file

    # Resolve coordinates.
    if x is None or y is None:
        if portal or detect_backend() == "wayland":
            try:
                import vhk.system.portal as portal_mod

                resp = portal_mod.portal_pick_color(timeout_s=timeout_s)
                if resp.response == 0 and resp.color:
                    payload = {
                        "status": "ok",
                        "method": "portal",
                        "hex": portal_mod.rgb01_to_hex(resp.color),
                        "rgb01": [resp.color[0], resp.color[1], resp.color[2]],
                    }
                    if as_json:
                        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
                    else:
                        sys.stdout.write(payload["hex"] + "\n")
                    return
            except Exception:
                # Fall through to cursor-pos path below if possible.
                pass

        # Cursor-pos sampling path.
        pos = cursor_pos_mod.get_cursor_pos()
        x = pos.x
        y = pos.y

    # Sample via a minimal screenshot (fast).
    import tempfile

    with tempfile.TemporaryDirectory(prefix="vhk_pick_color_") as td:
        img = Path(td) / "px.png"
        try:
            # Capture a 1x1 at the point to keep this fast.
            screenshot_mod.capture(img, region=parse_geometry(f"1x1+{int(x)}+{int(y)}"))
            c = pixel_get_color_file(img, x=0, y=0)
            payload = {
                "status": "ok",
                "method": "screenshot",
                "x": int(x),
                "y": int(y),
                "hex": c.hex,
                "ahk_hex": c.ahk_hex,
                "rgb": [c.r, c.g, c.b],
            }
        except Exception as e:
            # Last resort on Wayland: portal picker.
            if detect_backend() == "wayland" and (portal or True):
                try:
                    import vhk.system.portal as portal_mod

                    resp = portal_mod.portal_pick_color(timeout_s=timeout_s)
                    if resp.response == 0 and resp.color:
                        payload = {
                            "status": "ok",
                            "method": "portal",
                            "hex": portal_mod.rgb01_to_hex(resp.color),
                            "rgb01": [resp.color[0], resp.color[1], resp.color[2]],
                            "note": "screenshot sampling failed; used portal picker",
                        }
                    else:
                        payload = {"status": "fail", "error": str(e), "portal_response": resp.response}
                except Exception as e2:
                    payload = {"status": "fail", "error": str(e), "portal_error": str(e2)}
            else:
                payload = {"status": "fail", "error": str(e)}

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        if payload.get("status") == "ok":
            sys.stdout.write(str(payload.get("hex")) + "\n")
        else:
            sys.stdout.write(f"pick-color failed: {payload.get('error')}\n")



@app.command()
def capture_needle(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    name: str = typer.Argument(..., help="Needle name (filename stem)"),
    out_dir: str = typer.Option("assets/needles", "--out-dir", help="Relative dir inside project"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags"),
    delay_ms: int = typer.Option(0, "--delay-ms", min=0, help="Delay before interactive capture begins (ms)"),
    with_click_point: bool = typer.Option(True, "--click-point/--no-click-point"),
):
    """Capture a needle image + openQA-style JSON metadata.

    Uses slop/slurp when available. On desktops where those tools are not
    available (notably GNOME/KDE Wayland), falls back to the native screenshot
    tools (e.g. spectacle or gnome-screenshot) in interactive region mode.
    """

    project_dir = project_dir.resolve()
    rel = Path(out_dir)
    out_path = (project_dir / rel / f"{name}.png").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    from vhk.system.screenshot import capture as capture_ss
    from vhk.system.screenshot import capture_interactive_region

    r = None
    if delay_ms:
        console.print(f"Delaying capture for {int(delay_ms)}ms...")
        time.sleep(max(0, int(delay_ms)) / 1000.0)
    try:
        r = select_region()
        capture_ss(out_path, region=r)
    except RuntimeError as exc:
        msg = str(exc).lower()
        if "requires" not in msg and "slurp" not in msg and "slop" not in msg:
            raise
        # Allow needle capture on desktops that don't support slurp/slop.
        capture_interactive_region(out_path)

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    # Derive metadata dimensions.
    if r is not None:
        w, h = r.w, r.h
    else:
        from PIL import Image

        with Image.open(out_path) as im:
            w, h = im.size

    meta = {
        "tags": tag_list,
        "area": [
            {
                "type": "match",
                "xpos": 0,
                "ypos": 0,
                "width": w,
                "height": h,
            }
        ],
    }

    if with_click_point:
        meta["area"][0]["click_point"] = {"xpos": w // 2, "ypos": h // 2}

    out_json = out_path.with_suffix(".json")
    out_json.write_text(json.dumps(meta, indent=2) + "\n")

    console.print(f"Wrote needle: [bold]{out_path}[/bold]")
    console.print(f"Wrote metadata: [bold]{out_json}[/bold]")




@app.command()
def capture_baseline(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    name: str = typer.Argument(..., help="Baseline name (filename stem)"),
    out_dir: str = typer.Option("assets/baselines", "--out-dir", help="Relative dir inside project"),
    tags: str = typer.Option("", "--tags", help="Comma-separated tags"),
    delay_ms: int = typer.Option(0, "--delay-ms", min=0, help="Delay before interactive capture begins (ms)"),
    with_stub_json: bool = typer.Option(True, "--json/--no-json", help="Write openQA-style sidecar JSON stub"),
):
    """Capture a visual baseline image for VisualAssert/Verify.

    The optional sidecar JSON uses the same openQA-style shape as needles, so you
    can add match/exclude areas later for more stable comparisons.
    """

    project_dir = project_dir.resolve()
    rel = Path(out_dir)
    out_path = (project_dir / rel / f"{name}.png").resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    from vhk.system.screenshot import capture as capture_ss
    from vhk.system.screenshot import capture_interactive_region

    r = None
    if delay_ms:
        console.print(f"Delaying capture for {int(delay_ms)}ms...")
        time.sleep(max(0, int(delay_ms)) / 1000.0)
    try:
        r = select_region()
        capture_ss(out_path, region=r)
    except RuntimeError as exc:
        msg = str(exc).lower()
        if "requires" not in msg and "slurp" not in msg and "slop" not in msg:
            raise
        capture_interactive_region(out_path)

    console.print(f"Wrote baseline: [bold]{out_path}[/bold]")

    if with_stub_json:
        if r is not None:
            w, h = r.w, r.h
        else:
            from PIL import Image

            with Image.open(out_path) as im:
                w, h = im.size

        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        meta = {
            "tags": tag_list,
            "area": [
                {
                    "type": "match",
                    "xpos": 0,
                    "ypos": 0,
                    "width": w,
                    "height": h,
                }
            ],
        }
        out_json = out_path.with_suffix(".json")
        out_json.write_text(json.dumps(meta, indent=2) + "\n")
        console.print(f"Wrote metadata stub: [bold]{out_json}[/bold]")

@app.command()
def needle_info(png_path: Path = typer.Argument(..., exists=True, dir_okay=False, help="Needle png path")):
    """Print needle metadata (openQA-style .json next to the .png)."""

    needle = load_needle(png_path)
    table = Table(title=f"Needle: {needle.name}")
    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Image", str(needle.image_path))
    table.add_row("Tags", ", ".join(needle.tags) if needle.tags else "(none)")
    table.add_row("Areas", str(len(needle.areas)))

    for i, a in enumerate(needle.areas):
        cp = ""
        if a.click_point:
            cid = f" id={a.click_point.id}" if a.click_point.id else ""
            cp = f" click=({a.click_point.xpos},{a.click_point.ypos}){cid}"
        mt = f" match={a.match}%" if a.match is not None else ""
        table.add_row(f"area[{i}]", f"{a.type}{mt} {a.width}x{a.height}+{a.xpos}+{a.ypos}{cp}")

    console.print(table)


@app.command()
def preview_needle(
    needle_path: Path = typer.Argument(..., exists=True, dir_okay=False, help="Needle png path"),
    haystack: Path | None = typer.Option(
        None,
        "--haystack",
        help="Haystack/screenshot image path to search (if omitted, capture current screen)",
    ),
    project_dir: Path | None = typer.Option(None, "--project", help="Resolve relative paths against this project folder"),
    threshold: float = typer.Option(0.8, "--threshold", help="Similarity threshold for OK/FAIL"),
    scales: str | None = typer.Option(
        None,
        "--scales",
        help="Optional scales list '0.9,1.0,1.1' or range '0.85:1.15:0.05' (multi-scale template matching)",
    ),
    auto_scale: bool = typer.Option(False, "--auto-scale", help="Shortcut for --scales 0.85:1.15:0.05"),
    region: str | None = typer.Option(None, "--region", help="Search geometry 'WxH+X+Y'"),
    select: bool = typer.Option(False, "--select-region", help="Interactively select search region"),
    click_point: str | None = typer.Option(None, "--click-point", help="Optional click_point id from needle metadata"),
    out_annotated: Path | None = typer.Option(None, "--out-annotated", help="Write an annotated haystack image"),
    as_json: bool = typer.Option(False, "--json", help="Print JSON instead of a table"),
    check: bool = typer.Option(True, "--check/--no-check", help="Exit non-zero if threshold not met"),
):
    """Preview/template-match a needle against a screenshot or live screen.

    This is a debugging helper inspired by the "match preview" workflow in tools
    like SikuliX and openQA. It always reports the best candidate, even when
    below the threshold, and can optionally write an annotated image.
    """

    if scales and auto_scale:
        raise typer.BadParameter("Use either --scales or --auto-scale, not both")

    if region and select:
        raise typer.BadParameter("Use either --region or --select-region, not both")

    def _parse_scales(spec: str) -> list[float]:
        spec = spec.strip()
        if ":" in spec:
            parts = [p.strip() for p in spec.split(":") if p.strip()]
            if len(parts) != 3:
                raise ValueError("scale range must be 'start:end:step'")
            start, end, step = (float(parts[0]), float(parts[1]), float(parts[2]))
            if step <= 0:
                raise ValueError("scale step must be > 0")
            out: list[float] = []
            v = start
            # Include end (with a small epsilon) to match user expectations.
            while v <= end + 1e-9:
                out.append(float(v))
                v += step
            return out
        return [float(p.strip()) for p in spec.split(",") if p.strip()]

    scale_list: list[float] | None = None
    if auto_scale:
        scale_list = _parse_scales("0.85:1.15:0.05")
    elif scales:
        try:
            scale_list = _parse_scales(scales)
        except Exception as exc:  # noqa: BLE001
            raise typer.BadParameter(str(exc))

    base_dir = project_dir.resolve() if project_dir else Path.cwd()

    npath = (base_dir / needle_path).resolve() if not needle_path.is_absolute() else needle_path.resolve()
    if not npath.exists():
        raise typer.BadParameter(f"Needle not found: {npath}")

    if haystack is not None:
        hpath = (base_dir / haystack).resolve() if not haystack.is_absolute() else haystack.resolve()
        if not hpath.exists():
            raise typer.BadParameter(f"Haystack not found: {hpath}")
    else:
        from vhk.system.screenshot import capture as capture_ss

        fd, tmp_name = tempfile.mkstemp(prefix="vhk_hay_", suffix=".png")
        os.close(fd)
        hpath = Path(tmp_name)
        capture_ss(hpath, region=None)

    r = None
    if select:
        r = select_region()
    elif region:
        try:
            r = parse_geometry(region)
        except Exception as exc:  # noqa: BLE001
            raise typer.BadParameter(str(exc))

    match, ok, err = preview_image_search_file(hpath, npath, region=r, threshold=float(threshold), scales=scale_list)

    meta = try_load_needle(npath)
    needle_obj: Needle
    if meta is None:
        needle_obj = Needle(name=npath.stem, image_path=npath, areas=[], tags=[])
    else:
        needle_obj = meta

    try:
        # Click points are expressed in needle pixels. If multi-scale matching
        # chose a different scale, scale the needle metadata so the click
        # offset stays aligned with the matched bbox.
        needle_for_click = scale_needle(needle_obj, float(getattr(match, "scale", 1.0)))
        dx, dy = compute_click_offset(needle_for_click, click_point_id=click_point)
    except Exception as exc:  # noqa: BLE001
        dx, dy = match.w // 2, match.h // 2
        err = (err + "\n" if err else "") + f"click_point error: {exc}"

    click_x, click_y = int(match.x + dx), int(match.y + dy)

    payload = {
        "needle": str(npath),
        "haystack": str(hpath),
        "region": r.model_dump() if r is not None else None,
        "threshold": float(threshold),
        "ok": bool(ok),
        "error": err,
        "match": {
            "x": match.x,
            "y": match.y,
            "w": match.w,
            "h": match.h,
            "score": float(match.score),
            "scale": float(getattr(match, "scale", 1.0)),
        },
        "click": {"x": click_x, "y": click_y, "dx": int(dx), "dy": int(dy), "id": click_point},
    }

    if out_annotated is not None:
        apath = (base_dir / out_annotated).resolve() if not out_annotated.is_absolute() else out_annotated.resolve()
        annotate_match(hpath, apath, match, needle_meta=meta, click_xy=(click_x, click_y), threshold=float(threshold), ok=ok)
        payload["annotated"] = str(apath)

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        title = f"Needle preview: {npath.name}"
        table = Table(title=title)
        table.add_column("Field")
        table.add_column("Value")
        table.add_row("Haystack", str(hpath))
        if r is not None:
            table.add_row("Region", f"{r.w}x{r.h}+{r.x}+{r.y}")
        table.add_row("Score", f"{match.score:.3f}")
        table.add_row("Threshold", f"{float(threshold):.3f}")
        table.add_row("OK", "yes" if ok else "no")
        table.add_row("Match", f"({match.x},{match.y}) {match.w}x{match.h}")
        table.add_row("Click", f"({click_x},{click_y})  (dx={dx}, dy={dy})")
        if out_annotated is not None:
            table.add_row("Annotated", payload.get("annotated", ""))
        if err:
            table.add_row("Note", err)
        console.print(table)

        snippet = {
            "type": "ClickNeedle",
            "needle_path": os.path.relpath(npath, start=base_dir),
            "threshold": float(threshold),
        }
        if scale_list is not None:
            snippet["scales"] = [float(s) for s in scale_list]
        if click_point:
            snippet["click_point_id"] = click_point
        sys.stdout.write("\n# Suggested step:\n")
        sys.stdout.write(yaml.safe_dump(snippet, sort_keys=False))

    if check and not ok:
        raise typer.Exit(code=1)


@app.command()
def panic(project_dir: Path | None = typer.Option(None, "--project", help="Use project settings (panic_file)")):
    """Create the global panic file to stop long-running macros ASAP."""

    if project_dir:
        project = load_project(project_dir)
        cfg = PanicConfig(panic_file=project.settings.panic_file)
    else:
        cfg = PanicConfig()

    p = set_panic(cfg)
    console.print(f"[yellow]PANIC enabled[/yellow]: {p}")


@app.command()
def unpanic(project_dir: Path | None = typer.Option(None, "--project", help="Use project settings (panic_file)")):
    """Remove the global panic file."""

    if project_dir:
        project = load_project(project_dir)
        cfg = PanicConfig(panic_file=project.settings.panic_file)
    else:
        cfg = PanicConfig()

    clear_panic(cfg)
    console.print("[green]PANIC cleared[/green]")


@app.command()
def doctor(as_json: bool = typer.Option(False, "--json", help="Print machine-readable diagnostics")):
    """Print environment diagnostics (lightweight).

    This is our CLI placeholder for the eventual Studio "Modules" page: what
    helpers are installed, what capabilities they provide, and quick version info.
    """

    ss = screenshot_backend()
    cb = clipboard_backend()
    nb = notify_backend()
    kb = choose_keyboard_backend()
    pb = choose_pointer_backend()
    db = choose_dialog_backend()
    chb = choose_choice_backend()
    cur = cursor_backend()

    modules = {
        "screenshot": {
            "backend": ss.name if ss else None,
            "version": (
                _tool_version("grim", "--version") if (ss and ss.name == "grim")
                else (_tool_version("maim", "--version") if (ss and ss.name == "maim")
                else (_tool_version("scrot", "--version") if (ss and ss.name == "scrot")
                else (_tool_version("import", "-version") if (ss and ss.name == "import")
                else ((str(Path(ss.converter_exe).name) + " + " + _tool_version(Path(ss.converter_exe).name, "--version").splitlines()[0]) if (ss and ss.name == "xwd+convert" and ss.converter_exe) else "(not found)"))))),
            "available": bool(ss),
        },
        "cursor": {
            "backend": cur.name if cur else None,
            "version": _tool_version("unclutter", "--version") if (cur and cur.name == "unclutter" and shutil.which("unclutter")) else (_tool_version("unclutter-xfixes", "--version") if (cur and cur.name == "unclutter" and shutil.which("unclutter-xfixes")) else (_tool_version("xbanish", "-V") if (cur and cur.name == "xbanish") else "(not found)")),
            "available": bool(cur),
        },
        "clipboard": {
            "backend": cb.name if cb else None,
            "version": _tool_version("wl-paste", "--version") if (cb and cb.name == "wl-clipboard") else (_tool_version("xclip", "-version") if (cb and cb.name == "xclip") else _tool_version("xsel", "--version")),
            "available": bool(cb),
        },
        "notify": {
            "backend": nb.name if nb else None,
            "version": _tool_version("dunstify", "--version") if shutil.which("dunstify") else _tool_version("notify-send", "--version"),
            "available": bool(nb),
        },
        "keyboard": {
            "backend": kb.name if kb else None,
            "version": (
                _tool_version("wtype", "--version") if (kb and kb.name == "wtype")
                else (_tool_version("xdotool", "-v") if (kb and kb.name == "xdotool")
                else (_tool_version("dotoolc", "--help") if (kb and kb.name == "dotoolc")
                else (_tool_version("dotool", "--help") if (kb and kb.name == "dotool")
                else _tool_version("ydotool", "--version"))))
            ),
            "available": bool(kb),
        },
        "pointer": {
            "backend": pb.name if pb else None,
            "version": (
                _tool_version("xdotool", "-v") if (pb and pb.name == "xdotool")
                else (_tool_version("dotoolc", "--help") if (pb and pb.name == "dotoolc")
                else (_tool_version("dotool", "--help") if (pb and pb.name == "dotool")
                else _tool_version("ydotool", "--version")))
            ),
            "available": bool(pb),
        },
        "dialogs": {
            "backend": db.name if db else None,
            "version": _tool_version("zenity", "--version") if (db and db.name == "zenity") else (_tool_version("yad", "--version") if (db and db.name == "yad") else (_tool_version("kdialog", "--version") if (db and db.name == "kdialog") else (_tool_version("dialog", "--version") if (db and db.name == "dialog") else "(console)"))),
            "available": bool(db),
        },
        "chooser": {
            "backend": chb.name if chb else None,
            "kind": getattr(chb, "kind", None),
            "version": (
                _tool_version("rofi", "-v") if (chb and chb.name == "rofi")
                else (_tool_version("dmenu", "-v") if (chb and chb.name == "dmenu")
                else (_tool_version("fuzzel", "--version") if (chb and chb.name == "fuzzel")
                else (_tool_version("wofi", "--version") if (chb and chb.name == "wofi")
                else (_tool_version("tofi", "--version") if (chb and chb.name == "tofi")
                else (_tool_version("zenity", "--version") if (chb and chb.name == "zenity")
                else (_tool_version("yad", "--version") if (chb and chb.name == "yad")
                else (_tool_version("kdialog", "--version") if (chb and chb.name == "kdialog")
                else (_tool_version("dialog", "--version") if (chb and chb.name == "dialog") else "(console)"))))))))),
            "available": bool(chb),
        },
    }

    payload = {
        "python": sys.version.split()[0],
        "platform": f"{platform.system()} {platform.release()}",
        "display": os.environ.get("DISPLAY"),
        "xauthority": os.environ.get("XAUTHORITY"),
        "desktop_backend": detect_backend(),
        "tesseract": {"available": bool(tesseract_available()), "version": _tool_version("tesseract", "--version")},
        "modules": modules,
        "helpers": {
            "slop": shutil.which("slop"),
            "slurp": shutil.which("slurp"),
            "keyd": shutil.which("keyd"),
            "intercept": shutil.which("intercept"),
            "uinput": shutil.which("uinput"),
            "evtest": shutil.which("evtest"),
            "xinput": shutil.which("xinput"),
            "wmctrl": shutil.which("wmctrl"),
            "xdpyinfo": shutil.which("xdpyinfo"),
            "setxkbmap": shutil.which("setxkbmap"),
            "clipnotify": shutil.which("clipnotify"),
            "autocutsel": shutil.which("autocutsel"),
            "xbanish": shutil.which("xbanish"),
            "unclutter": shutil.which("unclutter") or shutil.which("unclutter-xfixes"),
            "scrot": shutil.which("scrot"),
            "xwd": shutil.which("xwd"),
            "magick": shutil.which("magick"),
            "convert": shutil.which("convert"),
            "copyq": shutil.which("copyq"),
            "clipmenud": shutil.which("clipmenud"),
            "cliphist": shutil.which("cliphist"),
            "inotifywait": shutil.which("inotifywait"),
            "xvkbd": shutil.which("xvkbd"),
            "x11vnc": shutil.which("x11vnc"),
            "xdotool": shutil.which("xdotool"),
            "wtype": shutil.which("wtype"),
            "ydotool": shutil.which("ydotool"),
            "dotool": shutil.which("dotool"),
            "dotoolc": shutil.which("dotoolc"),
            "dotoold": shutil.which("dotoold"),
            "kdotool": shutil.which("kdotool"),
            "busctl": shutil.which("busctl"),
            "gsettings": shutil.which("gsettings"),
            "xdg_open": shutil.which("xdg-open"),
            "xdg_email": shutil.which("xdg-email"),
            "zenity": shutil.which("zenity"),
            "yad": shutil.which("yad"),
            "kdialog": shutil.which("kdialog"),
            "dialog": shutil.which("dialog"),
            "rofi": shutil.which("rofi"),
            "dmenu": shutil.which("dmenu"),
            "wofi": shutil.which("wofi"),
            "fuzzel": shutil.which("fuzzel"),
            "tofi": shutil.which("tofi"),
            "i3": shutil.which("i3"),
            "sway": shutil.which("sway"),
            "hyprctl": shutil.which("hyprctl"),
            "sxhkd": shutil.which("sxhkd"),
            "wev": shutil.which("wev"),
            "jq": shutil.which("jq"),
            "espanso": shutil.which("espanso"),
            "kmonad": shutil.which("kmonad"),
            "kanata": shutil.which("kanata"),
        },
        "env": {
            "XDG_SESSION_TYPE": os.environ.get("XDG_SESSION_TYPE"),
            "WAYLAND_DISPLAY": os.environ.get("WAYLAND_DISPLAY"),
            "I3SOCK": os.environ.get("I3SOCK"),
            "SWAYSOCK": os.environ.get("SWAYSOCK"),
            "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR"),
            "HYPRLAND_INSTANCE_SIGNATURE": os.environ.get("HYPRLAND_INSTANCE_SIGNATURE"),
            "NO_AT_BRIDGE": os.environ.get("NO_AT_BRIDGE"),
            "GTK_MODULES": os.environ.get("GTK_MODULES"),
        },
    }
    payload["screenshot_probe"] = probe_screenshot_capture()
    payload["tesseract"].update(probe_tesseract_languages())
    payload["a11y"] = probe_accessibility_bus()
    payload["xdg_portal"] = probe_xdg_portal_screenshot()
    payload["xdg_portal_screencast"] = probe_xdg_portal_screencast()
    payload["xdg_portal_input_capture"] = probe_xdg_portal_input_capture()
    payload["xdg_portal_backend_config"] = probe_xdg_portal_backend_config()
    payload["xdg_portal_backend_manifests"] = probe_xdg_portal_backend_manifests()
    payload["xdg_portal_global_shortcuts"] = probe_xdg_portal_global_shortcuts()
    payload["xdg_portal_remote_desktop"] = probe_xdg_portal_remote_desktop()
    payload["x11"] = probe_x11_extensions()
    payload["xkb"] = probe_xkb_layout()
    payload["displays"] = probe_display_geometry()
    payload["i3"] = probe_i3_ipc()
    payload["uinput"] = probe_uinput()
    payload["wayland_protocols"] = probe_wayland_protocols()
    payload["wayland_virtual_screen"] = probe_wayland_virtual_screen()
    payload["ydotool_socket"] = probe_ydotool_socket()
    payload["dotoold"] = probe_dotoold()
    payload["kdotool"] = probe_kdotool()
    payload["recovery"] = {"clear_stuck_keys": build_clear_stuck_keys_hint()}
    payload["capability_matrix"] = build_doctor_capability_matrix(
        desktop_backend=payload["desktop_backend"],
        helpers=payload["helpers"],
        screenshot=payload["screenshot_probe"],
        x11=payload["x11"],
        i3=payload["i3"],
        kdotool=payload.get("kdotool"),
        wayland_protocols=payload.get("wayland_protocols"),
        uinput=payload.get("uinput"),
        ydotool_socket=payload.get("ydotool_socket"),
        dotoold=payload.get("dotoold"),
        xdg_portal_screenshot=payload.get("xdg_portal"),
        xdg_portal_screencast=payload.get("xdg_portal_screencast"),
        xdg_portal_global_shortcuts=payload.get("xdg_portal_global_shortcuts"),
        xdg_portal_remote_desktop=payload.get("xdg_portal_remote_desktop"),
        xdg_portal_input_capture=payload.get("xdg_portal_input_capture"),
        xdg_portal_backend_config=payload.get("xdg_portal_backend_config"),
        xdg_portal_backend_manifests=payload.get("xdg_portal_backend_manifests"),
    )
    payload["advice"] = build_doctor_advice(
        desktop_backend=payload["desktop_backend"],
        helpers=payload["helpers"],
        uinput=payload.get("uinput"),
        wayland_protocols=payload.get("wayland_protocols"),
        ydotool_socket=payload.get("ydotool_socket"),
        dotoold=payload.get("dotoold"),
        a11y=payload["a11y"],
        recovery=payload["recovery"]["clear_stuck_keys"],
        screenshot=payload["screenshot_probe"],
        xdg_portal=payload.get("xdg_portal"),
        xdg_portal_screencast=payload.get("xdg_portal_screencast"),
        xdg_global_shortcuts=payload.get("xdg_portal_global_shortcuts"),
        xdg_remote_desktop=payload.get("xdg_portal_remote_desktop"),
        xdg_input_capture=payload.get("xdg_portal_input_capture"),
        xdg_portal_backend_config=payload.get("xdg_portal_backend_config"),
        xdg_portal_backend_manifests=payload.get("xdg_portal_backend_manifests"),
        tesseract=payload["tesseract"],
        displays=payload["displays"],
        x11=payload["x11"],
        i3=payload["i3"],
        xkb=payload["xkb"],
    )

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return

    table = Table(title="VHK doctor")
    table.add_column("Check")
    table.add_column("Result")

    table.add_row("Python", payload["python"])
    table.add_row("Platform", payload["platform"])
    table.add_row("DISPLAY", payload["display"] or "(not set)")
    table.add_row("XAUTHORITY", payload["xauthority"] or "(not set)")
    table.add_row("Desktop backend", payload["desktop_backend"])
    table.add_row("Tesseract", payload["tesseract"]["version"] if payload["tesseract"]["available"] else "MISSING")
    table.add_row("OCR languages", f"{payload['tesseract']['language_count']} | {', '.join(payload['tesseract']['languages'][:5]) if payload['tesseract']['languages'] else payload['tesseract']['status']}")
    table.add_row("Screenshot module", f"{modules['screenshot']['backend'] or 'MISSING'} | {modules['screenshot']['version']}")
    table.add_row("Screenshot self-test", payload['screenshot_probe']['status'])
    table.add_row("Screenshot bytes", str(payload['screenshot_probe']['bytes']) if payload['screenshot_probe']['bytes'] is not None else (payload['screenshot_probe']['error'] or '(n/a)'))
    table.add_row("Cursor module", f"{modules['cursor']['backend'] or 'MISSING'} | {modules['cursor']['version']}")
    table.add_row("Clipboard module", f"{modules['clipboard']['backend'] or 'MISSING'} | {modules['clipboard']['version']}")
    table.add_row("Notify module", f"{modules['notify']['backend'] or 'MISSING'} | {modules['notify']['version']}")
    table.add_row("Keyboard module", f"{modules['keyboard']['backend'] or 'MISSING'} | {modules['keyboard']['version']}")
    table.add_row("Pointer module", f"{modules['pointer']['backend'] or 'MISSING'} | {modules['pointer']['version']}")
    table.add_row("Dialog module", f"{modules['dialogs']['backend'] or 'MISSING'} | {modules['dialogs']['version']}")
    table.add_row("Chooser module", f"{modules['chooser']['backend'] or 'MISSING'} | {modules['chooser']['version']}")
    table.add_row("clipnotify", payload['helpers']['clipnotify'] or "(not found)")
    table.add_row("autocutsel", payload['helpers']['autocutsel'] or "(not found)")
    table.add_row("xbanish", payload['helpers']['xbanish'] or "(not found)")
    table.add_row("unclutter", payload['helpers']['unclutter'] or "(not found)")
    table.add_row("scrot", payload['helpers']['scrot'] or "(not found)")
    table.add_row("xwd", payload['helpers']['xwd'] or "(not found)")
    table.add_row("magick", payload['helpers']['magick'] or "(not found)")
    table.add_row("convert", payload['helpers']['convert'] or "(not found)")
    table.add_row("CopyQ", payload['helpers']['copyq'] or "(not found)")
    table.add_row("clipmenud", payload['helpers']['clipmenud'] or "(not found)")
    table.add_row("cliphist", payload['helpers']['cliphist'] or "(not found)")
    table.add_row("inotifywait", payload['helpers']['inotifywait'] or "(not found)")
    table.add_row("xvkbd", payload['helpers']['xvkbd'] or "(not found)")
    table.add_row("x11vnc", payload['helpers']['x11vnc'] or "(not found)")
    table.add_row("busctl", payload['helpers']['busctl'] or "(not found)")
    table.add_row("gsettings", payload['helpers']['gsettings'] or "(not found)")
    table.add_row("xdg-open", payload['helpers']['xdg_open'] or "(not found)")
    table.add_row("xdg-email", payload['helpers']['xdg_email'] or "(not found)")
    table.add_row("zenity", payload['helpers']['zenity'] or "(not found)")
    table.add_row("yad", payload['helpers']['yad'] or "(not found)")
    table.add_row("kdialog", payload['helpers']['kdialog'] or "(not found)")
    table.add_row("kdotool", payload['helpers'].get('kdotool') or "(not found)")
    table.add_row("dialog", payload['helpers']['dialog'] or "(not found)")
    table.add_row("rofi", payload['helpers']['rofi'] or "(not found)")
    table.add_row("dmenu", payload['helpers']['dmenu'] or "(not found)")
    table.add_row("wofi", payload['helpers']['wofi'] or "(not found)")
    table.add_row("fuzzel", payload['helpers']['fuzzel'] or "(not found)")
    table.add_row("tofi", payload['helpers']['tofi'] or "(not found)")
    table.add_row("slop", payload['helpers']['slop'] or "(not found)")
    table.add_row("slurp", payload['helpers']['slurp'] or "(not found)")
    table.add_row("keyd", payload['helpers']['keyd'] or "(not found)")
    table.add_row("intercept", payload['helpers']['intercept'] or "(not found)")
    table.add_row("uinput", payload['helpers']['uinput'] or "(not found)")
    table.add_row("evtest", payload['helpers']['evtest'] or "(not found)")
    table.add_row("xinput", payload['helpers']['xinput'] or "(not found)")
    table.add_row("wmctrl", payload['helpers']['wmctrl'] or "(not found)")
    table.add_row("xdpyinfo", payload['helpers']['xdpyinfo'] or "(not found)")
    table.add_row("setxkbmap", payload['helpers']['setxkbmap'] or "(not found)")
    table.add_row("sxhkd", payload['helpers'].get('sxhkd') or "(not found)")
    table.add_row("XDG_SESSION_TYPE", payload['env']['XDG_SESSION_TYPE'] or "(not set)")
    table.add_row("WAYLAND_DISPLAY", payload['env']['WAYLAND_DISPLAY'] or "(not set)")
    table.add_row("I3SOCK env", payload['env']['I3SOCK'] or "(not set)")
    table.add_row("SWAYSOCK env", payload['env']['SWAYSOCK'] or "(not set)")
    table.add_row("XDG_RUNTIME_DIR", payload['env']['XDG_RUNTIME_DIR'] or "(not set)")
    table.add_row("NO_AT_BRIDGE", payload['env']['NO_AT_BRIDGE'] or "(not set)")
    table.add_row("GTK_MODULES", payload['env']['GTK_MODULES'] or "(not set)")
    table.add_row("X11 extensions", payload['x11']['status'])
    table.add_row("X11 XTEST", str(payload['x11']['xtest_available']))
    table.add_row("X11 RECORD", str(payload['x11']['record_available']))
    table.add_row("X11 XInput", str(payload['x11']['xinput_available']))
    table.add_row("Display geometry", payload['displays']['status'])
    table.add_row("Display screen", (f"{payload['displays']['screen']['current_width']}x{payload['displays']['screen']['current_height']}" if payload['displays']['screen'] else '(unknown)'))
    table.add_row("Display monitors", str(payload['displays']['monitor_count']))
    table.add_row("Display DPI spread", str(payload['displays']['dpi_spread']) if payload['displays']['dpi_spread'] is not None else '(unknown)')
    table.add_row("Display mixed DPI", str(payload['displays']['mixed_dpi']))

    if payload["desktop_backend"] == "wayland":
        wvs = payload.get("wayland_virtual_screen") or {}
        if wvs.get("status") == "ok":
            table.add_row("Wayland virtual size", f"{wvs.get('width')}x{wvs.get('height')} via {wvs.get('probe')}")
        else:
            table.add_row("Wayland virtual size", wvs.get("status") or "(unknown)")
    table.add_row("XKB layout", payload['xkb']['layout'] or payload['xkb']['status'])
    table.add_row("XKB options", payload['xkb']['options'] or "(not set)")
    table.add_row("i3 IPC", payload['i3']['status'])
    table.add_row("i3 socket", payload['i3']['socket_path'] or "(not found)")
    table.add_row("A11y bus", payload['a11y']['status'])
    table.add_row("A11y registry", str(payload['a11y']['registry_available']))
    table.add_row("Portal Screenshot", payload['xdg_portal']['status'])
    table.add_row("Portal ScreenCast", payload['xdg_portal_screencast']['status'])
    table.add_row("Portal RemoteDesktop", payload['xdg_portal_remote_desktop']['status'])
    table.add_row("Portal InputCapture", payload['xdg_portal_input_capture']['status'])
    table.add_row("Portal GlobalShortcuts", payload['xdg_portal_global_shortcuts']['status'])
    portal_cfg = payload.get('xdg_portal_backend_config') or {}
    table.add_row("Portal config", portal_cfg.get('config_path') or portal_cfg.get('status') or '(unknown)')
    portal_manifests = payload.get('xdg_portal_backend_manifests') or {}
    manifest_names = [str(item.get('backend') or '') for item in list(portal_manifests.get('backends') or []) if str(item.get('backend') or '')]
    table.add_row("Portal manifests", ((portal_manifests.get('status') or '(unknown)') + (f" | {', '.join(manifest_names[:4])}" if manifest_names else "")))
    caps = payload.get('capability_matrix') or {}
    for key, label in [
        ('screen_capture', 'Capability: screen capture'),
        ('text_injection', 'Capability: text injection'),
        ('pointer_injection', 'Capability: pointer injection'),
        ('global_hotkeys', 'Capability: global hotkeys'),
        ('input_capture', 'Capability: input capture'),
        ('window_introspection', 'Capability: window introspection'),
    ]:
        item = caps.get(key) or {}
        mechs = ', '.join(item.get('mechanisms') or []) or '(none)'
        table.add_row(label, f"{item.get('status', '(unknown)')} | {mechs}")
    table.add_row("Clear stuck keys", payload['recovery']['clear_stuck_keys']['command'] or payload['recovery']['clear_stuck_keys']['reason'] or "(not available)")
    console.print(table)

    if payload["advice"]:
        console.print("\n[bold]Advice[/bold]")
        for item in payload["advice"]:
            console.print(f"- ({item['severity']}) {item['summary']}")



@app.command()
def report(
    event_log: Path | None = typer.Argument(
        None,
        help="Path to a run_*.jsonl event log (omit when using --project/--latest)",
    ),
    project_dir: Path | None = typer.Option(
        None,
        "--project",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Project directory (used with --latest to pick the most recent run log)",
    ),
    latest: bool = typer.Option(False, "--latest", help="Use the most recent run_*.jsonl from the project log dir"),
    durations: int = typer.Option(10, "--durations", min=1, help="Show the slowest N steps"),
    durations_min: float = typer.Option(0.005, "--durations-min", min=0.0, help="Only show steps slower than this many seconds"),
    show_waits: bool = typer.Option(True, "--waits/--no-waits", help="Include wait-attempt summary"),
    show_errors: bool = typer.Option(True, "--errors/--no-errors", help="Include failing step summary"),
    show_advice: bool = typer.Option(True, "--advice/--no-advice", help="Include heuristic optimization advice"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable summary"),
    check: bool = typer.Option(False, "--check", help="Exit non-zero if the run ended with ok=false"),
):
    """Summarize a VHK run event log.

    Think of this as the CLI counterpart to a "trace viewer": it highlights
    slow steps, retries, and wait loops.
    """

    from datetime import datetime

    if latest:
        if not project_dir:
            raise typer.BadParameter("--latest requires --project")
        project = load_project(project_dir)
        log_dir = Path(project.root_dir) / project.settings.log_dir
        chosen = find_latest_event_log(log_dir)
        if not chosen:
            raise typer.BadParameter(f"No run_*.jsonl logs found in {log_dir}")
        event_log = chosen

    if event_log is None:
        raise typer.BadParameter("Provide EVENT_LOG, or use --project ... --latest")

    events = read_event_log(event_log)
    summary = summarize_event_log(events)

    if as_json:
        sys.stdout.write(json.dumps({"path": str(event_log), **summary}, indent=2) + "\n")
        if check and summary["run"].get("ok") is False:
            raise typer.Exit(code=1)
        return

    run = summary["run"]
    run_ok = run.get("ok")
    started_ts = run.get("started_ts")
    ended_ts = run.get("ended_ts")

    def _fmt_ts(ts: Any) -> str:
        try:
            if ts is None:
                return "(unknown)"
            return datetime.fromtimestamp(float(ts)).isoformat(sep=" ", timespec="seconds")
        except Exception:
            return str(ts)

    overview = Table(title="VHK report")
    # Typer's test runner captures output at a fairly small width, and Rich
    # will otherwise ellipsize long values (like log paths). Use "fold"
    # overflow so tests (and users copying paths) can see the full string.
    overview.add_column("Field", no_wrap=True)
    overview.add_column("Value", overflow="fold")
    overview.add_row("Log", str(event_log))
    overview.add_row("Run ID", str(run.get("run_id") or "(unknown)"))
    overview.add_row("Project", str(run.get("project") or "(unknown)"))
    overview.add_row("Macro", str(run.get("macro") or "(unknown)"))
    overview.add_row("Started", _fmt_ts(started_ts))
    overview.add_row("Ended", _fmt_ts(ended_ts))
    overview.add_row("Duration", str(run.get("duration_s")) + "s" if run.get("duration_s") is not None else "(unknown)")
    overview.add_row("OK", str(run_ok))
    if run.get("error"):
        overview.add_row("Error", str(run.get("error")))
    console.print(overview)

    # Slow steps (pytest --durations style).
    steps = list(summary.get("steps") or [])
    threshold_ms = int(float(durations_min) * 1000)
    slow = [s for s in steps if int(s.get("total_duration_ms") or 0) >= threshold_ms]
    slow.sort(key=lambda s: int(s.get("total_duration_ms") or 0), reverse=True)
    slow = slow[: int(durations)]

    if slow:
        table = Table(title=f"Slowest steps (top {len(slow)})")
        table.add_column("Step", no_wrap=True)
        # Prevent truncation of common step types (e.g. "WaitForImage") in
        # narrow terminals / captured output.
        table.add_column("Type", overflow="fold", min_width=12)
        table.add_column("Calls", justify="right")
        table.add_column("Retries", justify="right")
        table.add_column("Fails", justify="right")
        table.add_column("Total (s)", justify="right")
        table.add_column("Avg (ms)", justify="right")
        table.add_column("Max (ms)", justify="right")
        for s in slow:
            total_s = (int(s.get("total_duration_ms") or 0)) / 1000.0
            table.add_row(
                str(s.get("step_id")),
                str(s.get("step_type")),
                str(s.get("count")),
                str(s.get("retry_count")),
                str(s.get("fail_count")),
                f"{total_s:.3f}",
                str(s.get("avg_duration_ms")),
                str(s.get("max_duration_ms")),
            )
        console.print("\n")
        console.print(table)

    if show_waits and summary.get("waits"):
        waits = list(summary.get("waits") or [])
        wt = Table(title="Wait attempts")
        wt.add_column("Kind")
        wt.add_column("Count", justify="right")
        for item in waits[:20]:
            wt.add_row(str(item.get("kind")), str(item.get("count")))
        console.print("\n")
        console.print(wt)

    if show_waits and summary.get("wait_durations"):
        durs = list(summary.get("wait_durations") or [])
        if durs:
            wd = Table(title="Wait durations")
            wd.add_column("Kind")
            wd.add_column("Count", justify="right")
            wd.add_column("OK", justify="right")
            wd.add_column("Fail", justify="right")
            wd.add_column("Total (s)", justify="right")
            wd.add_column("Avg (ms)", justify="right")
            wd.add_column("Max (ms)", justify="right")
            for w in durs[:20]:
                total_s = (int(w.get("total_duration_ms") or 0)) / 1000.0
                wd.add_row(
                    str(w.get("kind")),
                    str(w.get("count")),
                    str(w.get("ok_count")),
                    str(w.get("fail_count")),
                    f"{total_s:.3f}",
                    str(w.get("avg_duration_ms")),
                    str(w.get("max_duration_ms")),
                )
            console.print("\n")
            console.print(wd)

    if show_errors and summary.get("errors"):
        errs = list(summary.get("errors") or [])
        et = Table(title=f"Failing steps ({len(errs)})")
        et.add_column("Step")
        et.add_column("Type")
        et.add_column("Error")
        et.add_column("Screenshot")
        for e in errs[:20]:
            et.add_row(
                str(e.get("step_id")),
                str(e.get("step_type")),
                str(e.get("error_type") or "") + (": " + str(e.get("error")) if e.get("error") else ""),
                str(e.get("screenshot") or ""),
            )
        console.print("\n")
        console.print(et)

    if show_advice:
        adv = list(summary.get("advice") or [])
        if adv:
            at = Table(title="Optimization advice")
            at.add_column("Severity", no_wrap=True)
            at.add_column("Finding", overflow="fold", min_width=16)
            at.add_column("Recommendation", overflow="fold")
            for item in adv[:12]:
                at.add_row(str(item.get("severity") or "info").upper(), str(item.get("summary") or ""), str(item.get("details") or ""))
            console.print("\n")
            console.print(at)

    if check and run_ok is False:
        raise typer.Exit(code=1)


@app.command()
def trace(
    event_log: Path | None = typer.Argument(
        None,
        help="Path to a run_*.jsonl event log (omit when using --project/--latest)",
    ),
    project_dir: Path | None = typer.Option(
        None,
        "--project",
        exists=True,
        file_okay=False,
        dir_okay=True,
        help="Project directory (used with --latest to pick the most recent run log)",
    ),
    latest: bool = typer.Option(False, "--latest", help="Use the most recent run_*.jsonl from the project log dir"),
    out: Path | None = typer.Option(None, "--out", help="Write trace JSON to this file (default: stdout)"),
    pid: int = typer.Option(1, "--pid", min=0, help="Trace process id (pid)"),
    pretty: bool = typer.Option(True, "--pretty/--no-pretty", help="Pretty-print JSON output"),
    check: bool = typer.Option(False, "--check", help="Exit non-zero if the run ended with ok=false"),
):
    """Export a VHK event log to a trace viewer JSON.

    The output uses the widely supported "Chrome Trace Event" JSON format.
    You can drag-and-drop the resulting file into Perfetto UI (legacy JSON)
    or open it with Chrome's trace viewer.
    """

    if latest:
        if not project_dir:
            raise typer.BadParameter("--latest requires --project")
        project = load_project(project_dir)
        log_dir = Path(project.root_dir) / project.settings.log_dir
        chosen = find_latest_event_log(log_dir)
        if not chosen:
            raise typer.BadParameter(f"No run_*.jsonl logs found in {log_dir}")
        event_log = chosen

    if event_log is None:
        raise typer.BadParameter("Provide EVENT_LOG, or use --project ... --latest")

    events = read_event_log(event_log)
    payload = eventlog_to_chrome_trace(events, pid=pid)

    # Match report --check semantics by inspecting the run_end event.
    run_ok = None
    for e in events:
        if str(e.get("type")) == "run_end":
            run_ok = e.get("ok")
            break

    txt = json.dumps(payload, indent=2 if pretty else None)
    if out is None:
        sys.stdout.write(txt + "\n")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(txt + "\n", encoding="utf-8")
        console.print(f"Wrote trace to [bold]{out}[/bold]")

    if check and run_ok is False:
        raise typer.Exit(code=1)


@app.command()
def history(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    limit: int = typer.Option(20, "--limit", min=1, help="Maximum number of runs to show"),
    status: str = typer.Option("all", "--status", help="Filter runs: all|ok|fail"),
    macro: str | None = typer.Option(None, "--macro", help="Filter to a specific macro name"),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable output"),
    csv_out: Path | None = typer.Option(None, "--csv", help="Write results to a CSV file"),
    check: bool = typer.Option(False, "--check", help="Exit non-zero if any listed run ended with ok=false"),
):
    """Show a table of recent runs for a project.

    This is a lightweight "run history" view: OK/fail, duration, retries, and
    wait-loop counts.
    """

    from datetime import datetime
    import csv

    project = load_project(project_dir)
    log_dir = Path(project.root_dir) / project.settings.log_dir
    try:
        rows = collect_history(log_dir, limit=limit, status=status, macro=macro)
    except ValueError as ve:
        raise typer.BadParameter(str(ve))

    payload = {
        "project": str(project.root_dir),
        "log_dir": str(log_dir),
        "count": len(rows),
        "runs": [r.to_dict() for r in rows],
    }

    if csv_out is not None:
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        with csv_out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(
                f,
                fieldnames=[
                    "ended_ts",
                    "macro",
                    "ok",
                    "duration_s",
                    "retries",
                    "wait_attempts",
                    "run_id",
                    "path",
                    "error",
                ],
            )
            w.writeheader()
            for r in rows:
                w.writerow(
                    {
                        "ended_ts": r.ended_ts,
                        "macro": r.macro,
                        "ok": r.ok,
                        "duration_s": r.duration_s,
                        "retries": r.retries,
                        "wait_attempts": r.wait_attempts,
                        "run_id": r.run_id,
                        "path": r.path,
                        "error": r.error,
                    }
                )
        if not as_json:
            console.print(f"Wrote CSV to [bold]{csv_out}[/bold]")

    if as_json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        if check and any(r.ok is False for r in rows):
            raise typer.Exit(code=1)
        return

    def _fmt_ts(ts: float | None) -> str:
        try:
            if ts is None:
                return "(unknown)"
            return datetime.fromtimestamp(float(ts)).isoformat(sep=" ", timespec="seconds")
        except Exception:
            return str(ts)

    table = Table(title=f"VHK history ({len(rows)})")
    table.add_column("Ended")
    table.add_column("Macro")
    table.add_column("OK")
    table.add_column("Duration (s)", justify="right")
    table.add_column("Retries", justify="right")
    table.add_column("Wait attempts", justify="right")
    table.add_column("Log")

    for r in rows:
        table.add_row(
            _fmt_ts(r.ended_ts),
            str(r.macro or "(unknown)"),
            str(r.ok),
            f"{float(r.duration_s):.3f}" if r.duration_s is not None else "(unknown)",
            str(r.retries),
            str(r.wait_attempts),
            str(Path(r.path).name),
        )

    console.print(table)

    if check and any(r.ok is False for r in rows):
        raise typer.Exit(code=1)


@app.command()
def render(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    macro: str = typer.Argument(..., help="Macro name to render"),
):
    """Render a readable "script view" for a macro.

    This is intentionally *not* a full free-form editor; the goal is a stable,
    round-trippable view that matches the workflow graph.
    """

    project = load_project(project_dir)
    if macro not in project.macros:
        raise typer.BadParameter(f"Unknown macro '{macro}'. Available: {', '.join(project.macros.keys())}")

    m = project.macros[macro]

    def _render_steps(steps, indent: int = 0) -> list[str]:
        out: list[str] = []
        pad = "  " * indent
        for s in steps:
            if not s.enabled:
                out.append(pad + f"# (disabled) {s.type}")
                continue
            if s.comment:
                out.append(pad + f"# {s.comment}")
            if s.type == "If":
                cond = s.condition
                out.append(pad + f"if {cond}:")
                out.extend(_render_steps(s.then_steps, indent + 1))
                if s.else_steps:
                    out.append(pad + "else:")
                    out.extend(_render_steps(s.else_steps, indent + 1))
                continue
            if s.type == "While":
                out.append(pad + f"while {s.condition}:")
                out.extend(_render_steps(s.steps, indent + 1))
                continue
            if s.type == "Try":
                out.append(pad + "try:")
                out.extend(_render_steps(s.steps, indent + 1))
                if s.catch_steps:
                    extra = f" /{s.catch_pattern}/" if s.catch_pattern else ""
                    out.append(pad + f"catch{extra}:")
                    out.extend(_render_steps(s.catch_steps, indent + 1))
                if s.finally_steps:
                    out.append(pad + "finally:")
                    out.extend(_render_steps(s.finally_steps, indent + 1))
                continue

            # Compact one-liners for the common steps.
            d = s.model_dump(exclude={"enabled", "comment", "delay_ms", "repeat", "type", "retry_count", "retry_delay_ms", "retry_backoff", "continue_on_error"})
            # Make it pleasant to read.
            if s.type == "SetVar":
                out.append(pad + f"set {d['name']} = {d['value']!r}")
            elif s.type == "RunShell":
                out.append(pad + f"shell {d['command']!r}")
            elif s.type == "Key":
                out.append(pad + f"key {d['keys']!r}")
            elif s.type == "ResetModifiers":
                out.append(pad + "ResetModifiers")
            elif s.type == "TypeText":
                extra = []
                if d.get('backend') and d.get('backend') != 'auto':
                    extra.append(f"backend={d['backend']}")
                if d.get('paste_shortcut') and d.get('paste_shortcut') != 'auto':
                    extra.append(f"paste={d['paste_shortcut']}")
                suffix = (" " + " ".join(extra)) if extra else ""
                out.append(pad + f"type {d['text']!r}{suffix}")
            elif s.type in ("ImageSearchFile", "WaitForImageFile"):
                out.append(pad + f"{s.type} needle={d['needle_path']!r} hay={d.get('haystack_path')!r} thr={d.get('threshold')}")
            elif s.type in ("VisualAssert", "VisualVerify"):
                out.append(pad + f"{s.type} baseline={d['baseline_path']!r} max_pixels={d.get('max_changed_pixels')} max_ratio={d.get('max_change_ratio')}")
            elif s.type == "WaitForRegionChange":
                out.append(pad + f"WaitForRegionChange baseline={d.get('baseline_path')!r} min_pixels={d.get('min_changed_pixels')} min_ratio={d.get('min_change_ratio')}")
            elif s.type in ("WaitForWindow", "FocusWindow"):
                out.append(pad + f"{s.type} {d['selector']}")
            elif s.type == "WaitForFile":
                out.append(pad + f"WaitForFile path={d['path']!r} when={d['condition']!r}")
            elif s.type == "WaitForFileEvent":
                extra = []
                if d.get('recursive'):
                    extra.append('recursive=True')
                if d.get('exclude'):
                    extra.append(f"exclude={d['exclude']!r}")
                if int(d.get('min_size') or 0) != 0:
                    extra.append(f"min_size={int(d['min_size'])}")
                if int(d.get('stable_ms') or 0) != 0:
                    extra.append(f"stable_ms={int(d['stable_ms'])}")
                if int(d.get('quiet_ms') or 0) != 0:
                    extra.append(f"quiet_ms={int(d['quiet_ms'])}")
                suffix = (" " + " ".join(extra)) if extra else ""
                out.append(pad + f"WaitForFileEvent dir={d['directory']!r} event={d['event']!r} pattern={d['pattern']!r}{suffix}")
            elif s.type == "WaitForNewFile":
                extra = []
                if d.get('recursive'):
                    extra.append('recursive=True')
                if d.get('include_existing_changes') is False:
                    extra.append('include_existing_changes=False')
                if d.get('since_ns') is not None:
                    extra.append(f"since_ns={d['since_ns']!r}")
                if d.get('exclude'):
                    extra.append(f"exclude={d['exclude']!r}")
                if int(d.get('min_size') or 0) != 0:
                    extra.append(f"min_size={int(d['min_size'])}")
                if int(d.get('stable_ms') or 0) != 0:
                    extra.append(f"stable_ms={int(d['stable_ms'])}")
                suffix = (" " + " ".join(extra)) if extra else ""
                out.append(pad + f"WaitForNewFile dir={d['directory']!r} pattern={d['pattern']!r}{suffix}")
            elif s.type == "WaitForClipboardChange":
                out.append(pad + f"WaitForClipboardChange selection={d['selection']!r}")
            elif s.type == "WaitForDbusSignal":
                out.append(
                    pad
                    + "WaitForDbusSignal "
                    + f"bus={d['bus']!r} interface={d.get('interface')!r} member={d.get('member')!r} sender={d.get('sender')!r}"
                )
            elif s.type == "GetSystemdUnitState":
                out.append(pad + f"GetSystemdUnitState unit={d['unit']!r} scope={d['scope']!r}")
            elif s.type == "WaitForSystemdUnitState":
                out.append(
                    pad
                    + "WaitForSystemdUnitState "
                    + f"unit={d['unit']!r} scope={d['scope']!r} active_state={d.get('active_state')!r} sub_state={d.get('sub_state')!r} status={d.get('status')!r}"
                )
            elif s.type == "PasteClipboard":
                out.append(pad + f"PasteClipboard selection={d['selection']!r}")
            elif s.type == "OpenUrl":
                out.append(pad + f"OpenUrl {d['url']!r}")
            elif s.type == "ComposeEmail":
                out.append(pad + f"ComposeEmail to={d['to']!r} subject={d.get('subject')!r}")
            elif s.type == "HttpRequest":
                out.append(pad + f"HttpRequest {d['method']} {d['url']!r}")
            elif s.type == "DownloadFile":
                out.append(pad + f"DownloadFile {d['url']!r} -> {d['path']!r}")
            elif s.type == "ShowMessage":
                out.append(pad + f"ShowMessage level={d['level']!r} text={d['text']!r}")
            elif s.type == "AskYesNo":
                out.append(pad + f"AskYesNo {d['text']!r} -> {d['out_var']}")
            elif s.type == "InputBox":
                out.append(pad + f"InputBox {d['prompt']!r} -> {d['out_var']}")
            elif s.type == "PromptForm":
                out.append(pad + f"PromptForm fields={len(d['fields'])} -> {d['out_var']}")
            elif s.type == "ChooseFromList":
                out.append(pad + f"ChooseFromList {d['items_expr']} -> {d['out_var']}")
            elif s.type == "StartProcess":
                out.append(pad + f"StartProcess {d['command']!r} -> {d['out_pid']}")
            elif s.type == "WaitForProcessExit":
                out.append(pad + f"WaitForProcessExit pid={d['pid']!r}")
            elif s.type == "KillProcess":
                out.append(pad + f"KillProcess pid={d['pid']!r} signal={d['signal']!r}")
            elif s.type == "ForEach":
                out.append(pad + f"for {d['item_var']} in {d['items_expr']}:")
                out.extend(_render_steps(s.steps, indent + 1))
                continue
            elif s.type == "Break":
                out.append(pad + "break")
            elif s.type == "Continue":
                out.append(pad + "continue")
            elif s.type == "Return":
                out.append(pad + (f"return {d['value_expr']}" if d.get('value_expr') is not None else "return"))
            elif s.type == "ReadCsv":
                out.append(pad + f"ReadCsv {d['path']!r} -> {d['out_var']}")
            elif s.type == "WriteCsv":
                out.append(pad + f"WriteCsv {d['path']!r} rows={d['rows_expr']}")
            elif s.type == "ReadJson":
                out.append(pad + f"ReadJson {d['path']!r} -> {d['out_var']}")
            elif s.type == "WriteJson":
                out.append(pad + f"WriteJson {d['path']!r} value={d['value_expr']}")
            elif s.type == "RegexReplace":
                out.append(pad + f"RegexReplace /{d['pattern']}/ -> {d['out_var']}")
            elif s.type == "TrimText":
                out.append(pad + f"TrimText mode={d['mode']!r} -> {d['out_var']}")
            elif s.type == "SplitText":
                out.append(pad + f"SplitText sep={d.get('sep')!r} -> {d['out_var']}")
            elif s.type == "JoinText":
                out.append(pad + f"JoinText {d['items_expr']} -> {d['out_var']}")
            elif s.type == "ReadFile":
                out.append(pad + f"ReadFile {d['path']!r} -> {d['out_var']}")
            elif s.type in ("WriteFile", "AppendFile"):
                out.append(pad + f"{s.type} {d['path']!r}")
            elif s.type == "ListDirectory":
                out.append(pad + f"ListDirectory {d['path']!r} pattern={d.get('pattern')!r}")
            elif s.type == "MouseDrag":
                out.append(pad + f"MouseDrag ({d['x1']},{d['y1']}) -> ({d['x2']},{d['y2']})")
            elif s.type == "MouseWheel":
                out.append(pad + f"MouseWheel clicks={d['clicks']} axis={d['axis']!r}")
            elif s.type == "CursorHide":
                out.append(pad + "CursorHide")
            elif s.type == "CursorShow":
                out.append(pad + "CursorShow")
            else:
                out.append(pad + f"{s.type} {json.dumps(d, ensure_ascii=False)}")

        return out

    sys.stdout.write(f"# Macro: {m.name}\n")
    sys.stdout.write("\n".join(_render_steps(m.steps)) + "\n")


_XWININFO_GEOM_RE = re.compile(r"^\s*(Absolute upper-left X|Absolute upper-left Y|Width|Height):\s*(\d+)")


def _run_capture(cmd: list[str]) -> str:
    proc = shutil.which(cmd[0])
    if not proc:
        raise RuntimeError(f"Missing dependency: {cmd[0]}")
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"Command failed: {' '.join(cmd)}")
    return out.stdout


def _tool_version(cmd: str, *args: str) -> str:
    exe = shutil.which(cmd)
    if not exe:
        return "(not found)"
    try:
        proc = subprocess.run([exe, *args], capture_output=True, text=True, timeout=2)
        lines = (proc.stdout or proc.stderr).strip().splitlines()
        return lines[0] if lines else exe
    except Exception:
        return exe


def _pick_x11_window_id() -> str:
    if detect_backend() == "wayland":
        raise RuntimeError("pick/build-rule click selection is currently X11-only (uses xdotool/slop + xprop/xwininfo).")

    if shutil.which("xdotool"):
        wid = _run_capture(["xdotool", "selectwindow"]).strip()
    elif shutil.which("slop"):
        wid = _run_capture(["slop", "-f", "%i"]).strip()
    else:
        raise RuntimeError("Need xdotool or slop to pick a window")

    if not wid:
        raise RuntimeError("No window selected")

    if wid.startswith("0x"):
        return wid
    return hex(int(wid))


def _inspect_x11_window(wid_norm: str) -> dict[str, object]:
    xprop_out = _run_capture([
        "xprop",
        "-id",
        wid_norm,
        "WM_CLASS",
        "WM_WINDOW_ROLE",
        "_NET_WM_NAME",
        "WM_NAME",
        "_NET_WM_PID",
    ])

    wm_class = None
    instance = None
    window_role = None
    title = None
    pid = None

    for line in xprop_out.splitlines():
        if line.startswith("WM_CLASS") and "=" in line:
            parts = line.split("=", 1)[1].strip()
            vals = [v.strip().strip('"') for v in parts.split(",")]
            if len(vals) >= 2:
                instance, wm_class = vals[0], vals[1]
        if line.startswith("_NET_WM_NAME") and "=" in line:
            title = line.split("=", 1)[1].strip().strip('"')
        if line.startswith("WM_NAME") and "=" in line and not title:
            title = line.split("=", 1)[1].strip().strip('"')
        if line.startswith("WM_WINDOW_ROLE") and "=" in line:
            window_role = line.split("=", 1)[1].strip().strip('"')
        if line.startswith("_NET_WM_PID") and "=" in line:
            try:
                pid = int(line.split("=", 1)[1].strip())
            except Exception:
                pid = None

    geom_out = _run_capture(["xwininfo", "-id", wid_norm])
    gx = gy = gw = gh = None
    for line in geom_out.splitlines():
        m = _XWININFO_GEOM_RE.match(line)
        if not m:
            continue
        k, v = m.group(1), int(m.group(2))
        if k.endswith("X"):
            gx = v
        elif k.endswith("Y"):
            gy = v
        elif k == "Width":
            gw = v
        elif k == "Height":
            gh = v

    return {
        "window_id": wid_norm,
        "pid": pid,
        "class": wm_class,
        "instance": instance,
        "window_role": window_role,
        "title": title,
        "geometry": {"x": gx, "y": gy, "w": gw, "h": gh},
    }


def _quote_i3_command_token(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9:_./-]+", value):
        return value
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _lua_quote(value: str) -> str:
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _build_i3_rule_commands(
    *,
    workspace: str | None,
    mark: str | None,
    float_enable: bool,
    focus: bool,
    sticky: bool,
    pos_x: int | None,
    pos_y: int | None,
    width: int | None,
    height: int | None,
) -> tuple[list[str], list[str]]:
    commands: list[str] = []
    notes: list[str] = []

    if float_enable:
        commands.append("floating enable")
    if workspace:
        commands.append(f"move container to workspace {_quote_i3_command_token(workspace)}")
    if mark:
        commands.append(f"mark --add {_quote_i3_command_token(mark)}")
    if focus:
        commands.append("focus")
    if sticky:
        commands.append("sticky enable")

    if (pos_x is None) ^ (pos_y is None):
        notes.append("Need both --x and --y to emit an i3 move-position command.")
    elif pos_x is not None and pos_y is not None:
        if not float_enable:
            notes.append("i3 move position is mainly useful for floating windows; consider adding --float for predictable geometry rules.")
        commands.append(f"move position {pos_x} px {pos_y} px")

    if (width is None) ^ (height is None):
        notes.append("Need both --width and --height to emit an i3 resize-set command.")
    elif width is not None and height is not None:
        if not float_enable:
            notes.append("i3 resize set is most predictable for floating windows; tiling layouts may immediately rebalance it.")
        commands.append(f"resize set {width} px {height} px")

    return commands, notes


def _build_devilspie2_script(
    *,
    selector: I3WindowSelector,
    workspace: str | None,
    focus: bool,
    sticky: bool,
    above: bool,
    pos_x: int | None,
    pos_y: int | None,
    width: int | None,
    height: int | None,
) -> tuple[str | None, list[str]]:
    conditions: list[str] = []
    actions: list[str] = []
    notes: list[str] = []

    if selector.wm_class:
        conditions.append(f"get_window_class()=={_lua_quote(selector.wm_class)}")
    if selector.instance:
        conditions.append(f"get_class_instance_name()=={_lua_quote(selector.instance)}")
    if selector.window_role:
        conditions.append(f"get_window_role()=={_lua_quote(selector.window_role)}")
    if selector.title:
        conditions.append(f"get_window_name()=={_lua_quote(selector.title)}")
        notes.append("Title matching in devilspie2 is exact-string based and will be brittle if the app mutates its title.")

    if workspace:
        actions.append(f"set_window_workspace({_lua_quote(workspace)})")
    if focus:
        actions.append("focus_window()")
    if sticky:
        actions.append("pin_window()")
    if above:
        actions.append("make_always_on_top()")

    if pos_x is not None and pos_y is not None and width is not None and height is not None:
        actions.append(f"set_window_geometry({pos_x},{pos_y},{width},{height})")
    elif pos_x is not None and pos_y is not None:
        actions.append(f"set_window_position({pos_x},{pos_y})")
    elif width is not None or height is not None:
        notes.append("devilspie2 can set geometry, but width/height alone are not emitted because the API wants full geometry.")

    if not actions or not conditions:
        if not conditions:
            notes.append("Need at least one selector field (class/instance/role/title) before generating a devilspie2 snippet.")
        if not actions:
            notes.append("No devilspie2-compatible actions requested.")
        return None, notes

    lines = ["-- generated by VHK rule builder", f"if ({' and '.join(conditions)}) then"]
    for action in actions:
        lines.append(f"  {action}")
    lines.append("end")
    return "\n".join(lines), notes


def _build_wmctrl_commands(
    *,
    window_id: str | None,
    above: bool,
    sticky: bool,
    pos_x: int | None,
    pos_y: int | None,
    width: int | None,
    height: int | None,
) -> tuple[list[str], list[str]]:
    notes: list[str] = []
    if not window_id:
        return [], ["wmctrl snippets need a concrete X11 window id; use --pick when you want apply-once/fallback commands."]

    commands: list[str] = []
    base = f"wmctrl -i -r {window_id}"
    if above:
        commands.append(f"{base} -b add,above")
    if sticky:
        commands.append(f"{base} -b add,sticky")
    if any(v is not None for v in (pos_x, pos_y, width, height)):
        gx = -1 if pos_x is None else pos_x
        gy = -1 if pos_y is None else pos_y
        gw = -1 if width is None else width
        gh = -1 if height is None else height
        commands.append(f"{base} -e 0,{gx},{gy},{gw},{gh}")
    return commands, notes


@app.command()
def pick_window(as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON")):
    """Pick an X11 window by clicking it and print i3-style criteria.

    Inspired by the i3 FAQ "i3-get-window-criteria" helper script.
    """

    info = _inspect_x11_window(_pick_x11_window_id())
    wm_class = info.get("class")
    instance = info.get("instance")
    window_role = info.get("window_role")
    title = info.get("title")

    sel = I3WindowSelector.model_validate(
        {
            "class": wm_class,
            "instance": instance,
            "window_role": window_role,
            "title": title,
        }
    )
    criteria = _selector_to_i3_criteria(sel)
    stable_selector = _selector_without_title(sel)
    stable_criteria = _selector_to_i3_exact_criteria(stable_selector, include_title=False)
    exact_criteria = _selector_to_i3_exact_criteria(sel)
    preview = _preview_selector_against_i3(stable_selector, sel)

    title_warning = None
    if title:
        title_warning = (
            "Window titles are regex criteria in i3 and often change over time; prefer class/instance/window_role unless the title is known-stable."
        )

    payload = {
        **info,
        "i3_criteria": criteria,
        "i3_exact_criteria": exact_criteria,
        "selector_suggestions": {
            "stable": {
                "fields": [f for f in ["class" if wm_class else None, "instance" if instance else None, "window_role" if window_role else None] if f],
                "i3_criteria": stable_criteria,
            },
            "exact": {
                "fields": [
                    f
                    for f in [
                        "class" if wm_class else None,
                        "instance" if instance else None,
                        "window_role" if window_role else None,
                        "title" if title else None,
                    ]
                    if f
                ],
                "i3_criteria": exact_criteria,
            },
            "title_warning": title_warning,
        },
        "preview": preview,
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(stable_criteria + "\n")


@app.command()
def window_spy(
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON"),
    include_workspace: bool = typer.Option(False, "--include-workspace", help="Include workspace in suggested selectors"),
    include_title_in_stable: bool = typer.Option(False, "--include-title-in-stable", help="Include title in stable selector suggestion (fragile)"),
):
    """Print active-window info and selector suggestions (i3/sway/Hyprland).

    This is the Wayland-friendly sibling of `pick-window`:

    - `pick-window` is X11-only (click-based)
    - `window-spy` is focus-based and uses compositor APIs where available

    The JSON output is designed to be copy/pasted into `--require-window` and
    into `when:` selectors.
    """

    from vhk.system.active_window import ActiveWindowProbeError, get_active_window_geometry, get_active_window_info

    try:
        info, wm = get_active_window_info()
    except ActiveWindowProbeError as exc:
        console.print(f"[red]Active window probe failed:[/red] {exc}")
        raise typer.Exit(code=2)

    rect = None
    client = None
    try:
        rect, client, _wm2 = get_active_window_geometry()
    except Exception:
        # Geometry is best-effort; it depends on compositor APIs.
        rect = None
        client = None

    def _suggest(include_title: bool) -> dict[str, object]:
        data: dict[str, object] = {}
        if info.get("app_id"):
            data["app_id"] = str(info.get("app_id"))
        if info.get("class"):
            data["class"] = str(info.get("class"))
        if info.get("instance"):
            data["instance"] = str(info.get("instance"))
        if info.get("window_role"):
            data["window_role"] = str(info.get("window_role"))
        if include_workspace and info.get("workspace"):
            data["workspace"] = str(info.get("workspace"))
        if include_title and info.get("title"):
            data["title"] = str(info.get("title"))
            data["title_regex"] = False
        sel = I3WindowSelector.model_validate(data)
        return sel.model_dump(by_alias=True, exclude_none=True)

    stable = _suggest(include_title_in_stable)
    exact = _suggest(True)

    payload = {
        "wm": wm,
        "active": info,
        "geometry": {"rect": rect, "client": client} if rect is not None else None,
        "suggested": {
            "stable": stable,
            "exact": exact,
            "notes": [
                "Titles often change; prefer stable unless you truly need exact matching.",
                "i3/sway criteria treat title/class/instance as regexes; VHK selectors default to exact-string unless *_regex is true.",
            ],
        },
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        # Print the stable selector JSON for quick copy/paste.
        sys.stdout.write(json.dumps(stable, ensure_ascii=False) + "\n")


@app.command()
def window_list(
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON"),
    include_geometry: bool = typer.Option(False, "--geometry/--no-geometry", help="Include best-effort geometry"),
):
    """Print a best-effort list of currently open windows.

    This is the list-oriented sibling of ``window-spy``. It aims to be useful
    for AHK-style app scoping and quick diagnostics while remaining honest about
    Linux backend differences.
    """

    from vhk.system.active_window import ActiveWindowProbeError, get_window_list_snapshot

    try:
        windows, wm = get_window_list_snapshot(include_geometry=include_geometry)
    except ActiveWindowProbeError as exc:
        console.print(f"[red]Window list probe failed:[/red] {exc}")
        raise typer.Exit(code=2)

    payload = {"wm": wm, "count": len(windows), "windows": windows}
    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return

    for row in windows:
        mark = "*" if row.get("focused") else "-"
        title = str(row.get("title") or "")
        cls = str(row.get("class") or row.get("app_id") or "")
        ws = str(row.get("workspace") or "")
        wid = str(row.get("id") or row.get("address") or "")
        sys.stdout.write(f"{mark}\t{ws}\t{cls}\t{title}\t{wid}\n")


@app.command()
def window_at_cursor(
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON"),
    include_geometry: bool = typer.Option(True, "--geometry/--no-geometry", help="Include best-effort geometry"),
    require_window: bool = typer.Option(False, "--require-window", help="Exit non-zero when no window is detected under the pointer"),
):
    """Print the best-effort top-level window currently under the mouse pointer.

    This is the pointer-oriented sibling of ``window-spy`` and the CLI analogue
    of the runtime ``GetWindowAtCursor`` step.
    """

    from vhk.system.active_window import ActiveWindowProbeError, get_window_at_cursor_snapshot

    try:
        window, wm, cursor = get_window_at_cursor_snapshot(
            include_geometry=include_geometry,
            require_window=require_window,
        )
    except ActiveWindowProbeError as exc:
        console.print(f"[red]Window-at-cursor probe failed:[/red] {exc}")
        raise typer.Exit(code=2)

    stable = None
    exact = None
    if isinstance(window, dict):
        def _suggest(include_title: bool) -> dict[str, object]:
            data: dict[str, object] = {}
            if window.get("app_id"):
                data["app_id"] = str(window.get("app_id"))
            if window.get("class"):
                data["class"] = str(window.get("class"))
            if window.get("instance"):
                data["instance"] = str(window.get("instance"))
            if window.get("window_role"):
                data["window_role"] = str(window.get("window_role"))
            if include_title and window.get("title"):
                data["title"] = str(window.get("title"))
                data["title_regex"] = False
            sel = I3WindowSelector.model_validate(data)
            return sel.model_dump(by_alias=True, exclude_none=True)

        stable = _suggest(False)
        exact = _suggest(True)

    payload = {
        "wm": wm,
        "cursor": {"x": cursor.x, "y": cursor.y, "backend": cursor.backend},
        "window": window,
        "suggested": None if window is None else {
            "stable": stable,
            "exact": exact,
            "notes": [
                "Titles often change; prefer stable unless you truly need exact matching.",
                "On some Linux backends this is a best-effort top-level window match, not a child-control hit-test.",
            ],
        },
    }
    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
        return

    if window is None:
        sys.stdout.write("null\n")
        return
    sys.stdout.write(json.dumps(stable, ensure_ascii=False) + "\n")


@app.command()
def cursorpos(
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON payload or plain 'x y'"),
    copy: bool = typer.Option(False, "--copy", help="Copy 'x,y' to clipboard (best-effort)"),
):
    """Print the global cursor position (best-effort).

    Wayland note: global cursor position is not a generic protocol. VHK uses
    compositor/tool-specific helpers (Hyprland: `hyprctl cursorpos`, wlroots:
    `wl-find-cursor -p`).
    """

    from vhk.system.cursor_pos import get_cursor_pos

    pos = get_cursor_pos()
    payload = {"x": pos.x, "y": pos.y, "backend": pos.backend}

    if copy:
        from vhk.system.clipboard import write

        write(f"{pos.x},{pos.y}")

    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(f"{pos.x} {pos.y}\n")


@app.command()
def cursor_step(
    action: str = typer.Argument("click", help="Step type: click|move"),
    button: str = typer.Option("left", "--button", help="Click button for action=click (left|right|middle)"),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON instead of YAML"),
):
    """Print a macro step snippet at the current cursor position.

    This is a small authoring helper to reduce copy/paste friction when you
    already know where the pointer is.
    """

    from vhk.system.cursor_pos import get_cursor_pos

    pos = get_cursor_pos()
    act = (action or "").strip().lower()
    btn = (button or "left").strip().lower()
    if btn not in {"left", "right", "middle"}:
        raise typer.BadParameter("--button must be left/right/middle")

    if act == "move":
        step = {"type": "MouseMove", "x": pos.x, "y": pos.y}
    elif act == "click":
        step = {"type": "MouseClickAt", "x": pos.x, "y": pos.y, "button": btn}
    else:
        raise typer.BadParameter("action must be one of: click, move")

    if as_json:
        sys.stdout.write(json.dumps(step, ensure_ascii=False, indent=2) + "\n")
    else:
        # Print as a YAML list item for direct paste into `steps:`.
        sys.stdout.write(yaml.safe_dump([step], sort_keys=False))


@app.command()
def build_rule(
    pick: bool = typer.Option(False, "--pick", help="Click a window first and seed selector fields from it (X11 only)."),
    as_json: bool = typer.Option(True, "--json/--no-json", help="Print JSON payload or concise text"),
    wm_class: str | None = typer.Option(None, "--class", help="WM_CLASS class value"),
    instance: str | None = typer.Option(None, "--instance", help="WM_CLASS instance value"),
    window_role: str | None = typer.Option(None, "--window-role", help="WM_WINDOW_ROLE value"),
    title: str | None = typer.Option(None, "--title", help="Exact title to include (fragile)"),
    workspace: str | None = typer.Option(None, "--workspace", help="Target workspace / assignment name"),
    mark: str | None = typer.Option(None, "--mark", help="Mark to add in i3"),
    float_enable: bool = typer.Option(False, "--float", help="Generate floating-enable action"),
    focus: bool = typer.Option(False, "--focus", help="Generate focus action"),
    sticky: bool = typer.Option(False, "--sticky", help="Generate sticky/pin action when possible"),
    above: bool = typer.Option(False, "--above", help="Generate always-on-top fallback snippets (wmctrl/devilspie2)"),
    pos_x: int | None = typer.Option(None, "--x", help="Target X position in pixels"),
    pos_y: int | None = typer.Option(None, "--y", help="Target Y position in pixels"),
    width: int | None = typer.Option(None, "--width", help="Target width in pixels"),
    height: int | None = typer.Option(None, "--height", help="Target height in pixels"),
    include_title: bool = typer.Option(False, "--include-title", help="Use title in the recommended selector/rules"),
    apply_once: bool = typer.Option(False, "--apply-once", help="Apply the generated actions to matching windows right now when possible"),
):
    """Build i3/devilspie2/wmctrl rule snippets from selector fields or a clicked window."""

    picked_info: dict[str, object] | None = None
    if pick:
        picked_info = _inspect_x11_window(_pick_x11_window_id())
        wm_class = wm_class or (picked_info.get("class") if picked_info else None)
        instance = instance or (picked_info.get("instance") if picked_info else None)
        window_role = window_role or (picked_info.get("window_role") if picked_info else None)
        title = title or (picked_info.get("title") if picked_info else None)

    if not any([wm_class, instance, window_role, title]):
        raise typer.BadParameter("Need selector fields (for example --class/--instance) or use --pick.")

    selector_data = {
        "class": wm_class,
        "instance": instance,
        "window_role": window_role,
        "title": title if include_title else None,
    }
    selector = I3WindowSelector.model_validate(selector_data)
    stable_selector = _selector_without_title(selector)
    selector_for_rules = selector if include_title else stable_selector

    stable_criteria = _selector_to_i3_exact_criteria(stable_selector, include_title=False)
    exact_criteria = _selector_to_i3_exact_criteria(selector, include_title=bool(include_title))
    preview = _preview_selector_against_i3(stable_selector, selector if include_title else stable_selector)

    i3_commands, i3_notes = _build_i3_rule_commands(
        workspace=workspace,
        mark=mark,
        float_enable=float_enable,
        focus=focus,
        sticky=sticky,
        pos_x=pos_x,
        pos_y=pos_y,
        width=width,
        height=height,
    )
    devilspie2_script, devilspie2_notes = _build_devilspie2_script(
        selector=selector_for_rules,
        workspace=workspace,
        focus=focus,
        sticky=sticky,
        above=above,
        pos_x=pos_x,
        pos_y=pos_y,
        width=width,
        height=height,
    )
    wmctrl_commands, wmctrl_notes = _build_wmctrl_commands(
        window_id=picked_info.get("window_id") if picked_info else None,
        above=above,
        sticky=sticky,
        pos_x=pos_x,
        pos_y=pos_y,
        width=width,
        height=height,
    )

    recommendation_type = "for_window"
    recommendation_reason = "for_window can combine placement with other i3 commands."
    if workspace and not any([mark, float_enable, focus, sticky, pos_x is not None, pos_y is not None, width is not None, height is not None, above]):
        recommendation_type = "assign"
        recommendation_reason = (
            "assign is usually better for pure workspace placement because i3 applies it when the window maps, while for_window rules can re-fire when properties change."
        )

    if include_title and title:
        i3_notes.append("Title criteria are PCRE regexes in i3 and are often fragile; prefer class/instance/window_role unless the title is truly stable.")

    assign_rule = None
    if workspace:
        assign_rule = f"assign {stable_criteria} {_quote_i3_command_token(workspace)}"

    for_window_rule = None
    if i3_commands:
        for_window_rule = f"for_window {exact_criteria if include_title else stable_criteria} {', '.join(i3_commands)}"

    apply_result: dict[str, object] | None = None
    if apply_once:
        executed: list[str] = []
        errors: list[str] = []
        if i3_commands:
            try:
                socket_path = discover_socket_path()
                cmd = f"{exact_criteria if include_title else stable_criteria} {', '.join(i3_commands)}"
                I3Connection(socket_path=socket_path).command(cmd)
                executed.append(f"i3-msg: {cmd}")
            except Exception as exc:
                errors.append(f"i3 apply-once failed: {exc}")
        if wmctrl_commands:
            for raw in wmctrl_commands:
                try:
                    subprocess.run(shlex.split(raw), check=True, capture_output=True, text=True)
                    executed.append(raw)
                except Exception as exc:
                    errors.append(f"wmctrl apply-once failed: {exc}")
        apply_result = {"executed": executed, "errors": errors, "ok": not errors}

    payload = {
        "picked_window": picked_info,
        "selector": {
            "stable": stable_criteria,
            "exact": exact_criteria if include_title else None,
            "used_for_rules": exact_criteria if include_title else stable_criteria,
        },
        "preview": preview,
        "recommendation": {
            "preferred_rule_type": recommendation_type,
            "reason": recommendation_reason,
        },
        "rules": {
            "i3_for_window": for_window_rule,
            "i3_assign": assign_rule,
            "devilspie2_lua": devilspie2_script,
            "wmctrl_apply_once": wmctrl_commands,
        },
        "notes": sorted(set(i3_notes + devilspie2_notes + wmctrl_notes)),
        "apply_once": apply_result,
    }

    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        lines = []
        if recommendation_type == "assign" and assign_rule:
            lines.append(assign_rule)
        if for_window_rule:
            lines.append(for_window_rule)
        if devilspie2_script:
            lines.append("")
            lines.append(devilspie2_script)
        if payload["notes"]:
            lines.append("")
            lines.append("# Notes")
            lines.extend(f"- {note}" for note in payload["notes"])
        sys.stdout.write("\n".join(lines).rstrip() + "\n")


@app.command()
def gen_systemd(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    macro: str = typer.Argument(..., help="Macro name to run"),
    unit_name: str | None = typer.Option(None, "--name", help="Unit basename (no .service/.timer)"),
    on_calendar: str | None = typer.Option(None, "--on-calendar", help="systemd OnCalendar= expression"),
    on_active_sec: str | None = typer.Option(None, "--on-active-sec", help="systemd OnUnitActiveSec= duration (e.g. 10m)"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write unit files"),
):
    """Generate a systemd .service + .timer that runs a macro.

    This doesn't install/enable units automatically; it just writes the files.
    """

    project = load_project(project_dir)
    if macro not in project.macros:
        raise typer.BadParameter(f"Unknown macro '{macro}'. Available: {', '.join(project.macros.keys())}")

    if not on_calendar and not on_active_sec:
        on_active_sec = "10m"

    unit = unit_name or f"vhk-{project.name}-{macro}".replace(" ", "-")
    target_dir = out_dir or (Path.home() / ".config" / "systemd" / "user")
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    service_path = target_dir / f"{unit}.service"
    timer_path = target_dir / f"{unit}.timer"

    exec_cmd = " ".join(
        shlex.quote(x)
        for x in ["/usr/bin/env", "vhk", "run", str(Path(project.root_dir)), macro]
    )

    service = "\n".join(
        [
            "[Unit]",
            f"Description=VHK macro: {project.name}/{macro}",
            "",
            "[Service]",
            "Type=oneshot",
            f"ExecStart={exec_cmd}",
            "",
        ]
    )

    timer_lines = [
        "[Unit]",
        f"Description=Timer for VHK macro: {project.name}/{macro}",
        "",
        "[Timer]",
        "Persistent=true",
    ]
    if on_calendar:
        timer_lines.append(f"OnCalendar={on_calendar}")
    else:
        timer_lines.append(f"OnUnitActiveSec={on_active_sec}")

    timer_lines += [
        "",
        "[Install]",
        "WantedBy=timers.target",
        "",
    ]

    timer = "\n".join(timer_lines)

    service_path.write_text(service)
    timer_path.write_text(timer)

    console.print(f"Wrote: [bold]{service_path}[/bold]")
    console.print(f"Wrote: [bold]{timer_path}[/bold]")
    console.print("\nNext:\n  systemctl --user daemon-reload\n  systemctl --user enable --now " + f"{unit}.timer")


@app.command()
def gen_systemd_watcher(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    window: str | None = typer.Option(None, "--window", help="Window watcher name from project.yaml"),
    clipboard: str | None = typer.Option(None, "--clipboard", help="Clipboard watcher name from project.yaml"),
    file: str | None = typer.Option(None, "--file", help="File watcher name from project.yaml"),
    unit_name: str | None = typer.Option(None, "--name", help="Unit basename (no .service)"),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write the .service unit"),
    restart: str = typer.Option("on-failure", "--restart", help="systemd Restart= policy"),
    restart_sec: str = typer.Option("1", "--restart-sec", help="systemd RestartSec= (seconds)"),
    use_graphical_target: bool = typer.Option(False, "--graphical", help="Install under graphical-session.target (may not exist in some WM setups)"),
    poll_ms: int = typer.Option(200, "--poll-ms", min=50, help="Polling interval for unknown compositors (window watchers only)"),
):
    """Generate a long-running systemd user service for a watcher."""

    selected = [opt for opt in (window, clipboard, file) if opt]
    if len(selected) != 1:
        raise typer.BadParameter("Exactly one of --window, --clipboard, or --file is required")

    project = load_project(project_dir)

    unit = unit_name
    if not unit:
        if window:
            unit = f"vhk-{project.name}-window-{window}"
        elif clipboard:
            unit = f"vhk-{project.name}-clipboard-{clipboard}"
        else:
            unit = f"vhk-{project.name}-file-{file}"
        unit = unit.replace(" ", "-")

    target_dir = out_dir or (Path.home() / ".config" / "systemd" / "user")
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    service_path = target_dir / f"{unit}.service"

    if window:
        exec_args = ["/usr/bin/env", "vhk", "watch-window", str(Path(project.root_dir)), window, "--poll-ms", str(poll_ms)]
        desc = f"VHK window watcher: {project.name}/{window}"
    elif clipboard:
        exec_args = ["/usr/bin/env", "vhk", "watch-clipboard", str(Path(project.root_dir)), str(clipboard)]
        desc = f"VHK clipboard watcher: {project.name}/{clipboard}"
    else:
        exec_args = ["/usr/bin/env", "vhk", "watch-file", str(Path(project.root_dir)), str(file)]
        desc = f"VHK file watcher: {project.name}/{file}"

    exec_cmd = " ".join(shlex.quote(x) for x in exec_args)

    wanted_by = "graphical-session.target" if use_graphical_target else "default.target"
    unit_lines = [
        "[Unit]",
        f"Description={desc}",
        f"After={wanted_by}",
        "",
        "[Service]",
        "Type=simple",
        "Environment=PYTHONUNBUFFERED=1",
        f"ExecStart={exec_cmd}",
        f"Restart={restart}",
        f"RestartSec={restart_sec}",
        "",
        "[Install]",
        f"WantedBy={wanted_by}",
        "",
    ]

    service_path.write_text("\n".join(unit_lines))

    console.print(f"Wrote: [bold]{service_path}[/bold]")
    console.print("\nNext:\n  systemctl --user daemon-reload\n  systemctl --user enable --now " + f"{unit}.service")

def _generate_uinput_udev_rules(
    *,
    group: str = "uinput",
    mode: str = "0660",
    tag_uaccess: bool = False,
    static_node: bool = True,
    evdev_name: str | None = None,
    evdev_idvendor: str | None = None,
    evdev_idproduct: str | None = None,
) -> dict[str, str]:
    """Generate small udev snippets for /dev/uinput (and optional input devices).

    The uinput node is primarily about *sending* input (emulating devices).
    Reading real keystrokes generally requires access to /dev/input/event* which
    is more sensitive; we keep that optional and scoped.
    """

    # Normalize vendor/product to lowercase hex without 0x prefix.
    def _norm_hex(x: str | None) -> str | None:
        if not x:
            return None
        s = x.strip().lower()
        if s.startswith('0x'):
            s = s[2:]
        if not s:
            return None
        # Keep as 4-hex if possible; udev typically uses zero-padded ids.
        if all(c in '0123456789abcdef' for c in s) and len(s) <= 4:
            return s.zfill(4)
        return s

    evdev_idvendor = _norm_hex(evdev_idvendor)
    evdev_idproduct = _norm_hex(evdev_idproduct)

    # Rule for creating a persistent /dev/uinput node + permissions.
    parts: list[str] = ['KERNEL=="uinput"']
    if tag_uaccess:
        parts.append('SUBSYSTEM=="misc"')
        parts.append('TAG+="uaccess"')
    if group:
        parts.append(f'GROUP="{group}"')
    if mode:
        parts.append(f'MODE="{mode}"')
    if static_node:
        parts.append('OPTIONS+="static_node=uinput"')

    rules: dict[str, str] = {}
    rules['80-uinput-vhk.rules'] = (
        "# Generated by: vhk gen-udev-uinput\n"
        "# Note: some systemd-udevd versions ignore OWNER/GROUP for non-system users/groups.\n"
        "# If you use GROUP=\"uinput\", ensure it is a *system* group (e.g. `groupadd --system uinput`).\n"
        + ', '.join(parts)
        + "\n"
    )

    # Optional: grant seat user access to a *specific* input device node.
    # This is needed by evdev-based remappers like kmonad/kanata.
    if evdev_name or (evdev_idvendor and evdev_idproduct):
        iparts: list[str] = ['SUBSYSTEM=="input"', 'KERNEL=="event*"']
        if evdev_name:
            # ATTRS walks up the device tree; name is often set on the input node.
            esc = evdev_name.replace('\\', '\\\\').replace('"', '\\"')
            iparts.append(f'ATTRS{{name}}=="{esc}"')
        if evdev_idvendor and evdev_idproduct:
            iparts.append(f'ATTRS{{idVendor}}=="{evdev_idvendor}"')
            iparts.append(f'ATTRS{{idProduct}}=="{evdev_idproduct}"')
        iparts.append('TAG+="uaccess"')
        rules['90-input-vhk.rules'] = ', '.join(iparts) + '\n'

    # Optional: modules-load snippet for distros that load uinput lazily.
    rules['uinput.conf'] = 'uinput\n'

    return rules


@app.command()
def gen_udev_uinput(
    out_dir: Path | None = typer.Option(None, '--out-dir', help='Write multiple files (udev rules + modules-load snippet) into this directory'),
    out_path: Path | None = typer.Option(None, '--out', help='Write the udev rule (only) to a file instead of stdout'),
    group: str = typer.Option('uinput', '--group', help='Group to own /dev/uinput (common: uinput or input)'),
    mode: str = typer.Option('0660', '--mode', help='Permissions for /dev/uinput (e.g. 0660)'),
    uaccess: bool = typer.Option(False, '--uaccess', help='Also add TAG+="uaccess" for seat ACLs (broader; often used by Steam)'),
    no_static_node: bool = typer.Option(False, '--no-static-node', help='Do not force a persistent /dev/uinput static node'),
    evdev_name: str | None = typer.Option(None, '--evdev-name', help='Optional: also grant uaccess to a specific /dev/input/event* device by input name'),
    evdev_idvendor: str | None = typer.Option(None, '--evdev-idvendor', help='Optional: match input device by USB idVendor (hex, e.g. 046d)'),
    evdev_idproduct: str | None = typer.Option(None, '--evdev-idproduct', help='Optional: match input device by USB idProduct (hex, e.g. c31c)'),
):
    """Generate starter udev rules for uinput-based automation tooling.

    This helps tools like ydotool / kanata / kmonad run without sudo by making
    /dev/uinput writable for an explicit group or the current seat user.

    For evdev-based remappers (kmonad/kanata), you may additionally need scoped
    read access to a specific /dev/input/event* node; use --evdev-* options for
    a narrower uaccess rule instead of joining the global `input` group.
    """

    if out_dir and out_path:
        raise typer.BadParameter('Use only one of --out-dir or --out')

    rules = _generate_uinput_udev_rules(
        group=group,
        mode=mode,
        tag_uaccess=uaccess,
        static_node=not no_static_node,
        evdev_name=evdev_name,
        evdev_idvendor=evdev_idvendor,
        evdev_idproduct=evdev_idproduct,
    )

    if out_dir:
        out_dir = out_dir.expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, content in rules.items():
            (out_dir / name).write_text(content)
        console.print(f"Wrote {len(rules)} file(s) to: [bold]{out_dir}[/bold]")
        return

    # stdout / single-file mode only emits the udev rule.
    udev_text = rules['80-uinput-vhk.rules']
    if out_path:
        out_path = out_path.expanduser().resolve()
        out_path.write_text(udev_text)
        console.print(f"Wrote: [bold]{out_path}[/bold]")
    else:
        print(udev_text, end='')



@app.command()
def gen_ydotoold_service(
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write the unit file (default: ~/.config/systemd/user)"),
    unit_name: str = typer.Option("ydotoold-vhk", "--name", help="Unit basename (no .service)"),
    socket_perm: str = typer.Option("0660", "--socket-perm", help="ydotoold --socket-perm value (default: 0660)"),
    socket_path: str = typer.Option("%t/.ydotool_socket", "--socket-path", help="ydotoold --socket-path value (default: %t/.ydotool_socket)"),
):
    """Generate a systemd *user* service for ydotoold.

    ydotool requires a background daemon (ydotoold). Running ydotoold as a user
    service is often the least surprising setup when /dev/uinput permissions
    are granted via udev rules.

    The default socket path uses systemd's %t (XDG_RUNTIME_DIR) so it aligns
    with common per-user daemon setups.
    """

    target_dir = out_dir or (Path.home() / ".config" / "systemd" / "user")
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    unit = unit_name.strip() or "ydotoold-vhk"
    service_path = target_dir / f"{unit}.service"

    exec_cmd = " ".join(
        shlex.quote(x)
        for x in ["/usr/bin/env", "ydotoold", "--socket-path", socket_path, "--socket-perm", socket_perm]
    )

    service = "\n".join(
        [
            "[Unit]",
            "Description=ydotool daemon (VHK)",
            "After=default.target",
            "",
            "[Service]",
            "Type=simple",
            f"ExecStart={exec_cmd}",
            "Restart=on-failure",
            "RestartSec=1",
            "",
            "[Install]",
            "WantedBy=default.target",
            "",
        ]
    )

    service_path.write_text(service)
    console.print(f"Wrote: [bold]{service_path}[/bold]")
    console.print("\nNext:\n  systemctl --user daemon-reload\n  systemctl --user enable --now " + f"{unit}.service")


@app.command()
def gen_dotoold_service(
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write the unit file (default: ~/.config/systemd/user)"),
    unit_name: str = typer.Option("dotoold-vhk", "--name", help="Unit basename (no .service)"),
):
    """Generate a systemd *user* service for dotoold.

    dotool has an initial delay while registering virtual devices when used as
    a one-shot command. The dotoold/dotoolc pair keeps devices alive and makes
    hotkey-driven invocations much snappier.
    """

    target_dir = out_dir or (Path.home() / ".config" / "systemd" / "user")
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    unit = unit_name.strip() or "dotoold-vhk"
    service_path = target_dir / f"{unit}.service"

    exec_cmd = " ".join(shlex.quote(x) for x in ["/usr/bin/env", "dotoold"])

    service = "\n".join(
        [
            "[Unit]",
            "Description=dotool daemon (VHK)",
            "After=default.target",
            "",
            "[Service]",
            "Type=simple",
            f"ExecStart={exec_cmd}",
            "Restart=on-failure",
            "RestartSec=1",
            "",
            "[Install]",
            "WantedBy=default.target",
            "",
        ]
    )

    service_path.write_text(service)
    console.print(f"Wrote: [bold]{service_path}[/bold]")
    console.print("\nNext:\n  systemctl --user daemon-reload\n  systemctl --user enable --now " + f"{unit}.service")








@app.command()
def gen_vhk_busd_service(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write the unit file (default: ~/.config/systemd/user)"),
    unit_name: str | None = typer.Option(None, "--name", help="Unit basename (no .service). Default: vhk-busd-<project>"),
    watchers: list[str] = typer.Option([], "--watcher", help="Bus watcher(s) to run. Default runs all enabled watchers."),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to invoke VHK (default: vhk)"),
    force: bool = typer.Option(False, "--force", help="Include --force in ExecStart (reclaim stale bus sockets on boot)"),
):
    """Generate a systemd *user* service for `vhk busd`.

    This is the recommended way to run dispatch-style hotkey setups:

      - export keybinds to emit bus events (via `vhk-emit`)
      - run `vhk busd` as a long-lived user service

    See docs/BUS_DAEMON.md.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    target_dir = out_dir or (Path.home() / ".config" / "systemd" / "user")
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    base = unit_name.strip() if unit_name else f"vhk-busd-{re.sub(r'[^A-Za-z0-9]+', '-', project.name).strip('-') or 'project'}"
    service_path = target_dir / f"{base}.service"

    args = [vhk_cmd, "busd", str(project_dir)]
    for w in watchers:
        args += ["--watcher", w]
    if force:
        args.append("--force")

    exec_cmd = " ".join(shlex.quote(a) for a in ["/usr/bin/env", *args])

    service = "\n".join(
        [
            "[Unit]",
            f"Description=VHK bus daemon ({project.name})",
            "After=default.target",
            "",
            "[Service]",
            "Type=simple",
            f"ExecStart={exec_cmd}",
            "Restart=on-failure",
            "RestartSec=1",
            "",
            "[Install]",
            "WantedBy=default.target",
            "",
        ]
    )

    service_path.write_text(service)
    console.print(f"Wrote: [bold]{service_path}[/bold]")
    console.print("\nNext:\n  systemctl --user daemon-reload\n  systemctl --user enable --now " + f"{base}.service")

def main() -> None:
    app()


if __name__ == "__main__":
    main()


@app.command()
def gen_vhk_busd_socket_units(
    project_dir: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    out_dir: Path | None = typer.Option(None, "--out-dir", help="Where to write the unit files (default: ~/.config/systemd/user)"),
    unit_name: str | None = typer.Option(None, "--name", help="Unit basename (no .socket/.service). Default: vhk-busd-<project>"),
    watchers: list[str] = typer.Option([], "--watcher", help="Bus watcher(s) to run. Default runs all enabled watchers."),
    vhk_cmd: str = typer.Option("vhk", "--vhk-cmd", help="Command to invoke VHK (default: vhk)"),
    force: bool = typer.Option(False, "--force", help="Include --force in ExecStart (reclaim stale bus sockets on boot). With socket activation this is typically unnecessary."),
    fdname: str | None = typer.Option(None, "--fdname", help="FileDescriptorName= for the socket unit (also sets VHK_BUS_FDNAME in the service unit)."),
):
    """Generate a systemd *user* socket+service pair for a socket-activated `vhk busd`.

    Why socket activation?
      - systemd owns the bus socket path and can create it early
      - the service can start on-demand when the first event arrives
      - avoids bind races on login/boot

    The generated units are meant to be enabled via the *.socket unit:

      systemctl --user enable --now <name>.socket

    VHK auto-detects systemd socket activation using LISTEN_FDS/LISTEN_PID.
    """

    project_dir = project_dir.resolve()
    project = load_project(project_dir)

    target_dir = out_dir or (Path.home() / ".config" / "systemd" / "user")
    target_dir = target_dir.expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    base = unit_name.strip() if unit_name else f"vhk-busd-{re.sub(r'[^A-Za-z0-9]+', '-', project.name).strip('-') or 'project'}"

    sock_path = get_bus_socket_path(Path(project.root_dir), configured=project.settings.bus_socket)
    listen = str(sock_path)

    fdname_effective = (fdname or os.environ.get('VHK_BUS_FDNAME') or project.settings.bus_fdname or '').strip() or None

    # Prefer %t so the unit is portable across users/machines.
    xdg = os.environ.get("XDG_RUNTIME_DIR")
    if xdg:
        xdg = str(Path(xdg).resolve())
        if listen.startswith(xdg + os.sep):
            listen = "%t" + listen[len(xdg) :]

    socket_unit_path = target_dir / f"{base}.socket"
    service_unit_path = target_dir / f"{base}.service"

    args = [vhk_cmd, "busd", str(project_dir)]
    for w in watchers:
        args += ["--watcher", w]
    if force:
        args.append("--force")

    exec_cmd = " ".join(shlex.quote(a) for a in ["/usr/bin/env", *args])

    socket_unit = "\n".join(
        [
            "[Unit]",
            f"Description=VHK bus socket ({project.name})",
            f"PartOf={base}.service",
            "",
            "[Socket]",
            f"ListenDatagram={listen}",
            *([f"FileDescriptorName={fdname_effective}"] if fdname_effective else []),
            "SocketMode=0600",
            "RemoveOnStop=yes",
            "FlushPending=yes",
            "",
            "[Install]",
            "WantedBy=sockets.target",
            "",
        ]
    )

    service_unit = "\n".join(
        [
            "[Unit]",
            f"Description=VHK bus daemon ({project.name})",
            f"Requires={base}.socket",
            f"After={base}.socket",
            "",
            "[Service]",
            "Type=simple",
            f"ExecStart={exec_cmd}",
            *([f"Environment=VHK_BUS_FDNAME={fdname_effective}"] if fdname_effective else []),
            "Restart=on-failure",
            "RestartSec=1",
            "",
            "[Install]",
            "WantedBy=default.target",
            "",
        ]
    )

    socket_unit_path.write_text(socket_unit)
    service_unit_path.write_text(service_unit)

    console.print(f"Wrote: [bold]{socket_unit_path}[/bold]")
    console.print(f"Wrote: [bold]{service_unit_path}[/bold]")
    console.print(
        "\nNext:\n  systemctl --user daemon-reload\n  systemctl --user enable --now " + f"{base}.socket"
    )
