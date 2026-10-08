#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
DAEMON_SRC = SCRIPT_DIR.parent / 'daemon' / 'src'
if str(DAEMON_SRC) not in sys.path:
    sys.path.insert(0, str(DAEMON_SRC))

from browser_binaries import cft_root, detect_cft_platform, discover_browser_executable, latest_local_cft_install
from glassttyd.overflow_artifacts import summarize_overflow_inventory
from native_host_manifest import inspect_targets, normalize_os_name
from profile_metadata import summarize_profiles
from e2e_fixturelab_capture import summarize_capture_history as summarize_fixturelab_capture_history, summarize_report_file as summarize_fixturelab_report_file
from validate_release_capture import summarize_capture_history as summarize_validate_release_capture_history, summarize_report_file as summarize_validate_release_report_file
from operator_handoff import operator_handoff_commands
from operator_attempt import operator_attempt_commands, summarize_capture_history as summarize_operator_attempt_history, summarize_current_attempt
from playwright_browsers import PLAYWRIGHT_ALLOW_SYSTEM_ENV, audit_playwright_cache, discover_playwright_browser_install, inspect_playwright_registry, latest_local_playwright_browser_install, plan_playwright_cache_repair, playwright_browser_choice, playwright_browsers_root, playwright_extension_launch_plan, playwright_install_dry_run, playwright_install_list, sync_playwright_browser_packages

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HOME = Path(os.environ.get("GLASSTTY_HOME", Path.home() / ".local" / "share" / "glasstty"))
MANIFEST_PATH = ROOT / "extension" / "manifest.json"
WRAPPER_PATH = ROOT / "scripts" / "native-host-wrapper.sh"
SOCKET_PATH = DEFAULT_HOME / "run" / "daemon.sock"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


def native_host_overflow_info(home: Path = DEFAULT_HOME) -> dict[str, Any]:
    latest_path = home / 'state' / 'latest' / 'oversized-host-outbound.json'
    latest = read_json_if_exists(latest_path)
    artifact_path = Path(latest['artifact_path']).expanduser() if isinstance(latest, dict) and isinstance(latest.get('artifact_path'), str) and latest.get('artifact_path') else None
    artifact = read_json_if_exists(artifact_path) if artifact_path and artifact_path.exists() else None
    message = artifact.get('message') if isinstance(artifact, dict) and isinstance(artifact.get('message'), dict) else None
    payload = message.get('payload') if isinstance(message, dict) and isinstance(message.get('payload'), dict) else None
    return {
        'latest_path': str(latest_path),
        'latest_exists': latest_path.exists(),
        'latest_summary': latest,
        'artifact_exists': bool(artifact_path and artifact_path.exists()),
        'artifact_path': str(artifact_path) if artifact_path else None,
        'artifact_kind': artifact.get('kind') if isinstance(artifact, dict) else None,
        'artifact_captured_at': artifact.get('captured_at') if isinstance(artifact, dict) else None,
        'message_type': message.get('type') if isinstance(message, dict) else None,
        'request_id': message.get('request_id') if isinstance(message, dict) else None,
        'payload_keys': sorted(payload.keys()) if isinstance(payload, dict) else None,
        'inventory': summarize_overflow_inventory(home),
    }


def native_host_runtime_info(home: Path = DEFAULT_HOME) -> dict[str, Any]:
    run_dir = home / 'run'
    socket_path = run_dir / 'daemon.sock'
    lock_path = run_dir / 'daemon-broker.lock'
    metadata_path = run_dir / 'daemon-broker-owner.json'
    return {
        'run_dir': str(run_dir),
        'socket_path': str(socket_path),
        'socket_exists': socket_path.exists(),
        'lock_path': str(lock_path),
        'lock_exists': lock_path.exists(),
        'metadata_path': str(metadata_path),
        'metadata_exists': metadata_path.exists(),
        'owner_metadata': read_json_if_exists(metadata_path),
    }




def _ordered_targets(*groups: list[str] | tuple[str, ...] | None) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for target in group or []:
            normalized = str(target).strip()
            if not normalized or normalized in seen:
                continue
            ordered.append(normalized)
            seen.add(normalized)
    return ordered


def _native_host_install_command(*, target: str, extension_id: str | None, include_host_exe: bool = False) -> str:
    command = f"./scripts/install-native-host.sh --target {target} --extension-id {extension_id or 'auto'}"
    if include_host_exe:
        command += ' --host-exe ' + str(WRAPPER_PATH)
    return command


def _preferred_native_host_install_command(*, default_targets: list[str], playwright_targets: list[str], combined_targets: list[str], extension_id: str | None) -> str | None:
    if not combined_targets:
        return None
    if len(combined_targets) == 1:
        return _native_host_install_command(target=combined_targets[0], extension_id=extension_id)
    if combined_targets == playwright_targets and playwright_targets:
        return _native_host_install_command(target='playwright', extension_id=extension_id)
    if combined_targets == default_targets and default_targets:
        return _native_host_install_command(target='auto', extension_id=extension_id)
    return _native_host_install_command(target='combined', extension_id=extension_id)

def compute_extension_id() -> str | None:
    script = ROOT / "scripts" / "extension-id.py"
    try:
        result = subprocess.run([sys.executable, str(script), str(MANIFEST_PATH)], check=True, capture_output=True, text=True)
    except Exception:
        return None
    value = result.stdout.strip()
    return value or None


def command_info(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    info: dict[str, Any] = {"name": name, "path": path, "available": bool(path)}
    if path:
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            version = (result.stdout or result.stderr).splitlines()
            if version:
                info["version"] = version[0].strip()
        except Exception as exc:
            info["version_error"] = str(exc)
    return info


def fixture_lab_info() -> dict[str, Any]:
    script = ROOT / "scripts" / "fixture-lab.py"
    latest_smoke = summarize_fixturelab_report_file(ROOT / 'validation' / 'latest' / 'e2e-fixturelab.json')
    smoke_captures = summarize_fixturelab_capture_history(ROOT / 'validation' / 'e2e-fixturelab-captures.json')
    return {
        "script": str(script),
        "exists": script.exists(),
        "default_url": "http://127.0.0.1:8765/",
        "scenarios": ["/", "/contenteditable", "/thread", "/long", "/manifest.json"],
        "latest_smoke_report": latest_smoke,
        "smoke_capture_history": smoke_captures,
        "commands": {
            "capture_latest": "python scripts/e2e-fixturelab-capture.py --report validation/latest/e2e-fixturelab.json --output-dir validation/latest/e2e-fixturelab-capture",
            "capture_history": "python scripts/e2e-fixturelab-capture.py history --pretty",
        },
    }


def profile_info() -> dict[str, Any]:
    return summarize_profiles(DEFAULT_HOME)


def validation_info() -> dict[str, Any]:
    latest = summarize_validate_release_report_file(ROOT / 'validation' / 'latest')
    captures = summarize_validate_release_capture_history(ROOT / 'validation' / 'validate-release-captures.json')
    return {
        'latest_report': latest,
        'capture_history': captures,
        'commands': {
            'resume_latest': 'python scripts/validate-release.py --out-dir validation/latest --resume',
            'capture_latest': 'python scripts/validate-release-capture.py --source-dir validation/latest --output-dir validation/latest/validate-release-capture',
            'capture_history': 'python scripts/validate-release-capture.py history --pretty',
        },
    }


def readiness_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/readiness-report.py --pretty',
        'capture_latest': 'python scripts/readiness-report.py capture --output-dir validation/latest/readiness-report-capture',
        'capture_history': 'python scripts/readiness-report.py history --pretty',
    }


def control_plane_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/control-plane-report.py --pretty',
        'capture_latest': 'python scripts/control-plane-report.py capture --output-dir validation/latest/control-plane-report-capture',
        'capture_history': 'python scripts/control-plane-report.py history --pretty',
    }


def install_receipt_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/install-receipt.py --pretty',
        'capture_latest': 'python scripts/install-receipt.py capture --output-dir validation/latest/install-receipt-capture',
        'capture_history': 'python scripts/install-receipt.py history --pretty',
    }


def support_surface_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/support-surface-snapshot.py --pretty',
        'capture_latest': 'python scripts/support-surface-snapshot.py capture --output-dir validation/latest/support-surface-capture',
        'capture_history': 'python scripts/support-surface-snapshot.py history --pretty',
        'check_contract': 'python scripts/check-support-record-contract.py --pretty',
    }


def support_bundle_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/support-bundle-queue.py --pretty',
        'capture_latest': 'python scripts/support-bundle-queue.py capture --output-dir validation/latest/support-bundle-queue',
        'capture_history': 'python scripts/support-bundle-queue.py history --pretty',
        'check_contract': 'python scripts/check-support-bundle-contract.py --pretty',
        'write_root': 'python scripts/check-support-bundle-contract.py write-root',
    }


def published_support_surface_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/published-support-surface.py --pretty',
        'capture_latest': 'python scripts/published-support-surface.py capture --output-dir validation/latest/published-support-surface',
        'capture_history': 'python scripts/published-support-surface.py history --pretty',
        'write_root': 'python scripts/published-support-surface.py write-root',
        'transition_bundle': 'python scripts/support-bundle-transition.py --bundle <bundle-key> --to-state <candidate|hold|published-ready|published>',
    }


def support_publish_gate_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/support-publish-gate.py --pretty',
        'capture_latest': 'python scripts/support-publish-gate.py capture --output-dir validation/latest/support-publish-gate',
        'capture_history': 'python scripts/support-publish-gate.py history --pretty',
        'write_root': 'python scripts/support-publish-gate.py write-root',
    }


def support_source_baseline_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/support-source-baseline.py --pretty',
        'capture_latest': 'python scripts/support-source-baseline.py capture --output-dir validation/latest/support-source-baseline',
        'capture_history': 'python scripts/support-source-baseline.py history --pretty',
        'write_root': 'python scripts/support-source-baseline.py write-root',
    }


def opening_surface_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/check-opening-contract.py --pretty',
        'capture_latest': 'python scripts/check-opening-contract.py capture --output-dir validation/latest/opening-surface-capture',
        'capture_history': 'python scripts/check-opening-contract.py history --pretty',
        'write_root': 'python scripts/check-opening-contract.py write-root',
    }


def truth_surface_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/truth-surface-register.py --pretty',
        'capture_latest': 'python scripts/truth-surface-register.py capture --output-dir validation/latest/truth-surface-register',
        'refresh_all': 'python scripts/refresh-truth-surfaces.py --pretty',
    }


def truth_surface_warning_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/truth-surface-warnings.py --pretty',
        'capture_latest': 'python scripts/truth-surface-warnings.py capture --output-dir validation/latest/truth-surface-warnings',
    }


def validation_artifact_inventory_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/validation-artifact-inventory.py --pretty',
        'capture_latest': 'python scripts/validation-artifact-inventory.py capture --output-dir validation/latest/validation-artifact-inventory',
    }


def revision_receipt_commands() -> dict[str, str]:
    return {
        'report': 'python scripts/check-revision-receipt.py --pretty',
        'write_root': 'python scripts/check-revision-receipt.py write-root',
    }


def wrapper_info() -> dict[str, Any]:
    return {
        "path": str(WRAPPER_PATH),
        "exists": WRAPPER_PATH.exists(),
        "is_absolute": WRAPPER_PATH.is_absolute(),
        "executable": bool(WRAPPER_PATH.exists() and os.access(WRAPPER_PATH, os.X_OK)),
    }


def chrome_for_testing_info() -> dict[str, Any]:
    platform_tag = detect_cft_platform()
    root = cft_root()
    latest = latest_local_cft_install(binary='chrome', platform=platform_tag, root=root)
    return {
        'root': str(root),
        'platform': platform_tag,
        'latest_chrome': latest,
        'default_browser': discover_browser_executable(),
    }


def playwright_info() -> dict[str, Any]:
    root = playwright_browsers_root()
    install_list_raw = playwright_install_list(root=root, ensure_links=False)
    registry_raw = inspect_playwright_registry(root)
    install_list_prepared = playwright_install_list(root=root, ensure_links=True)
    browser_install = discover_playwright_browser_install(install_list=install_list_prepared)
    dry_run = browser_install.get('dry_run') if isinstance(browser_install, dict) else playwright_install_dry_run()
    install_list_report = browser_install.get('install_list') if isinstance(browser_install, dict) else install_list_prepared
    cache_audit = audit_playwright_cache(root=root, env={'PLAYWRIGHT_BROWSERS_PATH': str(root)}, install_list=install_list_raw, prepared_install_list=install_list_prepared, registry_report=registry_raw)
    repair_plan = plan_playwright_cache_repair(root=root, env={'PLAYWRIGHT_BROWSERS_PATH': str(root)}, audit_report=cache_audit, install_list=install_list_raw)
    plan = playwright_extension_launch_plan(browser_install=browser_install, repair_plan=repair_plan)
    sync_preview = sync_playwright_browser_packages(
        root=root,
        package_names=[plan.get('required_package_name') or 'chromium'],
        expected_packages=(browser_install.get('expected_packages') if isinstance(browser_install, dict) else None),
    )
    return {
        'root': str(root),
        'latest_local_install': latest_local_playwright_browser_install(root=root),
        'install_list_raw': install_list_raw,
        'install_list_prepared': install_list_report,
        'registry_raw': registry_raw,
        **browser_install,
        'dry_run': dry_run,
        'cache_audit': cache_audit,
        'repair_plan': repair_plan,
        'extension_launch_plan': plan,
        'sync_preview': sync_preview,
    }


def manifest_info() -> dict[str, Any]:
    manifest = read_json(MANIFEST_PATH)
    return {
        "path": str(MANIFEST_PATH),
        "version": manifest.get("version"),
        "minimum_chrome_version": manifest.get("minimum_chrome_version"),
        "has_key": bool(manifest.get("key")),
        "host_permissions": manifest.get("host_permissions", []),
        "commands": sorted(list((manifest.get("commands") or {}).keys())),
    }


def native_host_info(default_browser: dict[str, Any] | None = None, playwright: dict[str, Any] | None = None) -> dict[str, Any]:
    os_name = normalize_os_name()
    extension_id = compute_extension_id()
    wrapper = wrapper_info()
    targets = inspect_targets(os_name=os_name, extension_id=extension_id, expected_host_path=wrapper['path'])
    recommended_targets = list((default_browser or {}).get('native_messaging_targets') or ['chromium'])
    playwright_launch_plan = (playwright or {}).get('extension_launch_plan') if isinstance((playwright or {}).get('extension_launch_plan'), dict) else None
    playwright_browser = playwright_browser_choice(playwright if isinstance(playwright, dict) else None, launch_plan=playwright_launch_plan)
    if playwright_browser is None and isinstance(playwright, dict):
        playwright_browser = (playwright.get('extension_browser_choice') if isinstance(playwright.get('extension_browser_choice'), dict) else None) or (playwright.get('browser_choice') if isinstance(playwright.get('browser_choice'), dict) else None)
    playwright_targets = list((playwright_browser or {}).get('native_messaging_targets') or [])
    combined_targets = _ordered_targets(playwright_targets, recommended_targets)
    suggested_commands = [
        _native_host_install_command(target=target, extension_id=extension_id)
        for target in combined_targets
    ]
    suggested_matrix_command = _preferred_native_host_install_command(
        default_targets=recommended_targets,
        playwright_targets=playwright_targets,
        combined_targets=combined_targets,
        extension_id=extension_id,
    )
    return {
        "host_name": "com.glasstty.bridge",
        "os": os_name,
        "extension_id": extension_id,
        "wrapper": wrapper,
        "targets": targets,
        "default_browser": default_browser,
        "recommended_targets": recommended_targets,
        "playwright_browser": playwright_browser,
        "playwright_recommended_targets": playwright_targets,
        "combined_recommended_targets": combined_targets,
        "suggested_install_command": suggested_matrix_command or (suggested_commands[0] if suggested_commands else None),
        "suggested_install_commands": suggested_commands,
        "suggested_install_matrix_command": suggested_matrix_command,
        "recommended_target_notes": list((default_browser or {}).get('native_messaging_notes') or []),
        "playwright_target_notes": list((playwright_browser or {}).get('native_messaging_notes') or []),
        "last_oversized_host_message": native_host_overflow_info(),
        "runtime": native_host_runtime_info(),
    }


def socket_info() -> dict[str, Any]:
    return {"path": str(SOCKET_PATH), "exists": SOCKET_PATH.exists()}


def analyze_hints(manifest: dict[str, Any], native_host: dict[str, Any], socket: dict[str, Any], profiles: dict[str, Any], commands: list[dict[str, Any]], playwright: dict[str, Any], chrome_for_testing: dict[str, Any], fixture_lab: dict[str, Any], validation: dict[str, Any], operator_attempt: dict[str, Any]) -> list[str]:
    hints: list[str] = []
    command_map = {item.get("name"): item for item in commands if isinstance(item, dict)}
    chromium_available = bool((command_map.get("chromium") or {}).get("available") or (command_map.get("google-chrome") or {}).get("available"))
    node_available = bool((command_map.get("node") or {}).get("available"))
    npm_available = bool((command_map.get("npm") or {}).get("available"))
    running_as_root = hasattr(os, 'geteuid') and os.geteuid() == 0
    default_browser = chrome_for_testing.get('default_browser') if isinstance(chrome_for_testing, dict) else None
    if not chromium_available and not (isinstance(default_browser, dict) and default_browser.get('exists')):
        hints.append("No Chromium-family browser executable was found on PATH and no local Chrome for Testing bundle is installed; the live extension loop cannot be proven here yet.")
    elif running_as_root:
        hints.append("Chromium is being checked from a root account here; ChromeDriver guidance warns that running Chrome as root is unsupported, even if `--no-sandbox` can sometimes work for lab smoke tests.")
    if isinstance(default_browser, dict) and default_browser.get('source') == 'system-path':
        hints.append("GlassTTY is currently falling back to a system Chromium executable; installing a local Chrome for Testing bundle would make the browser lab more hermetic and better aligned with current Chrome automation guidance.")
    if isinstance(default_browser, dict) and default_browser.get('browser_family') == 'chrome-for-testing' and (default_browser.get('native_messaging_primary_target') == 'chrome'):
        hints.append("Current Chrome for Testing builds still need the Google Chrome native-host directory until Chrome 146, so use the doctor-recommended `chrome` target rather than assuming `chrome-for-testing`.")
    if not node_available or not npm_available:
        hints.append("Node/npm are missing from PATH; extension build and side-panel UI validation may fail until the dev shell is active.")
    if not native_host.get("extension_id"):
        hints.append("Could not compute a stable development extension ID; check manifest.key and scripts/extension-id.py.")
    target_map = native_host.get('targets') if isinstance(native_host, dict) else None
    recommended_targets = list(native_host.get('recommended_targets') or []) if isinstance(native_host, dict) else []
    playwright_targets = list(native_host.get('playwright_recommended_targets') or []) if isinstance(native_host, dict) else []
    combined_targets = list(native_host.get('combined_recommended_targets') or []) if isinstance(native_host, dict) else []
    if recommended_targets and playwright_targets and recommended_targets != playwright_targets:
        hints.append(f"The default browser and Playwright persistent extension lane want different native-host targets ({', '.join(recommended_targets)} vs {', '.join(playwright_targets)}); install the combined set {', '.join(combined_targets or recommended_targets)} before comparing persistent-lane failures with direct-browser fallback behavior.")
    if isinstance(target_map, dict):
        if combined_targets and not any((target_map.get(target) or {}).get('manifest_exists') for target in combined_targets):
            targets_text = ', '.join(combined_targets)
            hints.append(f"The browser-aware native-host manifest is missing for the required target set: {targets_text}; run the doctor-recommended install command(s) before expecting bridge traffic.")
        for target in combined_targets or recommended_targets:
            info = target_map.get(target) or {}
            if info.get('manifest_exists') and info.get('extension_id_match') is False:
                hints.append(f"The installed native-host manifest for {target} exists but does not allow the current GlassTTY extension ID; reinstall it after any manifest.key or unpacked-ID change.")
            if info.get('manifest_exists') and info.get('host_path_match') is False:
                hints.append(f"The installed native-host manifest for {target} points at a different host executable than scripts/native-host-wrapper.sh; verify the intended wrapper before debugging browser↔CLI failures.")
        if combined_targets and not all((target_map.get(target) or {}).get('manifest_exists') for target in combined_targets):
            for target, info in target_map.items():
                if target not in combined_targets and info.get('manifest_exists'):
                    hints.append(f"A native-host manifest exists for {target}, but the current browser matrix wants {', '.join(combined_targets)} instead; install the required target set to avoid browser-family path mismatches.")
                    break
    runtime_info = native_host.get('runtime') if isinstance(native_host, dict) else None
    if isinstance(runtime_info, dict) and runtime_info.get('metadata_exists'):
        owner = runtime_info.get('owner_metadata') if isinstance(runtime_info.get('owner_metadata'), dict) else None
        identity = owner.get('host_identity') if isinstance(owner, dict) and isinstance(owner.get('host_identity'), dict) else None
        if isinstance(identity, dict):
            hints.append(f"A live GlassTTY native-host broker owner is recorded at {runtime_info.get('metadata_path')}; one-shot sendNativeMessage diagnostics will run in secondary host processes until that owner exits (pid={identity.get('pid')}, boot_id={identity.get('boot_id')}).")
    overflow_info = native_host.get('last_oversized_host_message') if isinstance(native_host, dict) else None
    if isinstance(overflow_info, dict) and overflow_info.get('latest_exists'):
        artifact_path = overflow_info.get('artifact_path')
        message_type = overflow_info.get('message_type') or (overflow_info.get('latest_summary') or {}).get('original_type') if isinstance((overflow_info.get('latest_summary') or {}), dict) else None
        hints.append(f"The native host recently spilled an oversized outbound {message_type or 'message'} to disk; inspect it with `python -m glassttyd.cli overflow-report` or read {artifact_path or 'state/latest/oversized-host-outbound.json'} before assuming the browser never received a reply.")
        if overflow_info.get('artifact_path') and not overflow_info.get('artifact_exists'):
            hints.append("The native host overflow summary points at a missing artifact file; preserve or repair that state before relying on the saved path in future handoffs.")
        inventory = overflow_info.get('inventory') if isinstance(overflow_info.get('inventory'), dict) else None
        if isinstance(inventory, dict) and ((inventory.get('artifact_count') or 0) > 3 or (inventory.get('total_disk_bytes') or 0) > 2_000_000):
            hints.append(f"Oversized native-host spill artifacts are accumulating ({inventory.get('artifact_count')} file(s), {inventory.get('total_disk_bytes')} bytes on disk); review them with `python -m glassttyd.cli overflow-report` and trim older ones with `python -m glassttyd.cli overflow-prune --keep 3 --max-disk-bytes 2000000` when the evidence is preserved elsewhere.")
    if not socket.get("exists"):
        hints.append("Native-host broker socket is absent; launch Chromium with the extension and install the native host before expecting CLI browser reads.")
    profile_entries = list((profiles or {}).get('profiles') or [])
    triage = (profiles or {}).get('triage') if isinstance((profiles or {}).get('triage'), dict) else None
    fleet_history = (profiles or {}).get('fleet_capture_history') if isinstance((profiles or {}).get('fleet_capture_history'), dict) else None
    best_profile = triage.get('best_profile') if isinstance(triage, dict) and isinstance(triage.get('best_profile'), dict) else None
    if best_profile and best_profile.get('next_command'):
        hints.append(f"Managed profile triage currently prefers {best_profile.get('name')!r} ({best_profile.get('tier')}, score={best_profile.get('score')}); next step: {best_profile.get('next_step')} via `{best_profile.get('next_command')}`.")
        triage_commands = triage.get('commands') if isinstance(triage, dict) else {}
        fleet_capture_cmd = triage_commands.get('fleet_capture') if isinstance(triage_commands, dict) else None
        fleet_captures_cmd = triage_commands.get('fleet_captures') if isinstance(triage_commands, dict) else None
        if fleet_capture_cmd and fleet_captures_cmd:
            if isinstance(fleet_history, dict) and fleet_history.get('capture_count'):
                hints.append(f"A fleet-level managed-profile snapshot ledger already exists with {fleet_history.get('capture_count')} saved capture(s); inspect it with `{fleet_captures_cmd}` or freeze the current triage + doctor surface with `{fleet_capture_cmd}` before the next live browser attempt.")
            else:
                hints.append(f"No fleet-level managed-profile snapshot has been frozen yet; capture the current triage + doctor surface with `{fleet_capture_cmd}` so future sessions can compare profile drift without re-running discovery from scratch.")
    if profile_entries and not any((entry.get('metadata_exists') for entry in profile_entries if isinstance(entry, dict))):
        hints.append("GlassTTY profile directories exist but none carry launch metadata yet; prefer `./scripts/glasstty-profile.sh open ...` over ad hoc browser commands so profile/debug state stays inspectable.")
    if profile_entries and not any((entry.get('native_host_audit_exists') for entry in profile_entries if isinstance(entry, dict))):
        hints.append("Saved GlassTTY profiles do not yet carry browser-aware native-host audit snapshots; relaunch them through `./scripts/glasstty-profile.sh open ...` so each profile preserves its own native-host preflight evidence.")
    if profile_entries and not any(((entry.get('last_launch') or {}).get('remote_debugging') or {}).get('requested') for entry in profile_entries if isinstance(entry, dict) and isinstance(entry.get('last_launch'), dict)):
        replayable = next((entry for entry in profile_entries if isinstance(entry, dict) and isinstance(entry.get('reopen_debug_plan'), dict) and entry.get('reopen_debug_plan', {}).get('ok')), None)
        if replayable is not None:
            hints.append(f"No saved GlassTTY profile launch has requested remote debugging yet; reuse the existing profile recipe with `{(replayable.get('commands') or {}).get('reopen_debug')}` so Chrome 136+ still gets a non-default user-data-dir.")
        else:
            hints.append("No saved GlassTTY profile launch has requested remote debugging yet; for CDP inspection or browser-target archaeology, launch a profile with `./scripts/glasstty-profile.sh open NAME --remote-debugging-port auto ...` so Chrome 136+ still uses a non-default user-data-dir.")
    attach_ready_profile = None
    saved_resume_profile = None
    for entry in profile_entries:
        if not isinstance(entry, dict):
            continue
        audit = entry.get('native_host_audit') if isinstance(entry.get('native_host_audit'), dict) else None
        status = (audit or {}).get('recommended_target_status') if isinstance((audit or {}).get('recommended_target_status'), dict) else None
        reopen_plan = entry.get('reopen_plan') if isinstance(entry.get('reopen_plan'), dict) else None
        commands = entry.get('commands') if isinstance(entry.get('commands'), dict) else None
        if reopen_plan and reopen_plan.get('ok') and not reopen_plan.get('launchable_now'):
            saved_browser = reopen_plan.get('saved_browser') if isinstance(reopen_plan.get('saved_browser'), dict) else None
            portable = (commands or {}).get('reopen_portable') or reopen_plan.get('portable_reopen_command')
            if isinstance(saved_browser, dict) and saved_browser.get('path') and saved_browser.get('exists') is False:
                fallback_browser = reopen_plan.get('discovered_browser') if isinstance(reopen_plan.get('discovered_browser'), dict) else None
                fallback_text = f" Current discovered browser: {fallback_browser.get('path')}." if isinstance(fallback_browser, dict) and fallback_browser.get('path') else ''
                hint = f"Profile {entry.get('name')!r} remembers a saved browser path that is missing here ({saved_browser.get('path')}). Use `{portable}` or `./scripts/glasstty-profile.sh reopen {entry.get('name')} --chromium-bin /abs/path/to/browser` before treating the saved profile recipe as broken.{fallback_text}"
                install_commands = list(((reopen_plan.get('saved_browser_native_host') or {}).get('install_commands') or []))
                if install_commands:
                    hint += f" If you restore the original browser family, its native-host reinstall shortcut is `{install_commands[0]}`."
                hints.append(hint)
                break
        if status and status.get('primary_target') and status.get('primary_target_ready') is False:
            hints.append(f"Profile {entry.get('name')!r} was last launched with a browser whose primary native-host target {status.get('primary_target')!r} was not ready; reinstall the recommended manifest before blaming MV3 or the broker.")
            break
        cdp_hint = entry.get('cdp_endpoint_hint') if isinstance(entry.get('cdp_endpoint_hint'), dict) else None
        if cdp_hint and cdp_hint.get('ok') and cdp_hint.get('attach_ready') and isinstance(commands, dict) and commands.get('resume_proof'):
            attach_ready_profile = attach_ready_profile or (entry, cdp_hint, commands)
        elif cdp_hint and cdp_hint.get('ok') and not cdp_hint.get('attach_ready') and cdp_hint.get('remote_debugging_requested'):
            warning = cdp_hint.get('attach_warning') or 'DevToolsActivePort is present but not currently attachable.'
            reopen_debug = (commands or {}).get('reopen_debug') or f"./scripts/glasstty-profile.sh open {entry.get('name')} --remote-debugging-port auto ..."
            if reopen_plan and not reopen_plan.get('launchable_now'):
                reopen_debug = (commands or {}).get('reopen_debug_portable') or reopen_plan.get('portable_reopen_debug_command') or reopen_debug
            hints.append(f"Profile {entry.get('name')!r} remembers a CDP endpoint ({cdp_hint.get('preferred_endpoint')}), but it is not attach-ready right now: {warning} Replay that profile with `{reopen_debug}` before trying the resume harness.")
            break
        resume_summary = entry.get('mv3_resume_summary') if isinstance(entry.get('mv3_resume_summary'), dict) else None
        if resume_summary and not saved_resume_profile:
            saved_resume_profile = (entry, resume_summary)
    if attach_ready_profile is not None:
        entry, cdp_hint, commands = attach_ready_profile
        capture_cmd = commands.get('capture') if isinstance(commands, dict) else None
        captures_cmd = commands.get('captures') if isinstance(commands, dict) else None
        suffix = f" Then freeze the surrounding profile evidence with `{capture_cmd}`." if capture_cmd else ''
        if captures_cmd:
            suffix += f" Compare it against the saved ledger with `{captures_cmd}`."
        hints.append(f"Profile {entry.get('name')!r} is attach-ready for MV3 restart proof at {cdp_hint.get('preferred_endpoint')}; capture a fresh worker-restart artifact with `{commands.get('resume_proof')}`.{suffix}")
    if saved_resume_profile is not None:
        entry, resume_summary = saved_resume_profile
        proof_grade = resume_summary.get('proof_grade') or 'unknown-proof-grade'
        captured_at = resume_summary.get('captured_at') or 'an unknown time'
        capture_cmd = (entry.get('commands') or {}).get('capture') if isinstance(entry, dict) else None
        captures_cmd = (entry.get('commands') or {}).get('captures') if isinstance(entry, dict) else None
        suffix = f" Refresh the durable handoff bundle with `{capture_cmd}` after any new live run." if capture_cmd else ''
        if captures_cmd:
            suffix += f" Review earlier durable bundles with `{captures_cmd}` before discarding the old evidence."
        hints.append(f"Profile {entry.get('name')!r} already carries saved MV3 resume evidence ({proof_grade}, captured {captured_at}); inspect `./scripts/glasstty-profile.sh info {entry.get('name')} --pretty` before rerunning another restart proof.{suffix}")
    fixture_latest = fixture_lab.get('latest_smoke_report') if isinstance(fixture_lab, dict) else None
    fixture_history = fixture_lab.get('smoke_capture_history') if isinstance(fixture_lab, dict) else None
    fixture_commands = fixture_lab.get('commands') if isinstance(fixture_lab, dict) else None
    latest_summary = fixture_latest.get('summary') if isinstance(fixture_latest, dict) else None
    latest_capture = fixture_history.get('latest_capture') if isinstance(fixture_history, dict) else None
    capture_cmd = fixture_commands.get('capture_latest') if isinstance(fixture_commands, dict) else None
    capture_history_cmd = fixture_commands.get('capture_history') if isinstance(fixture_commands, dict) else None
    if isinstance(latest_summary, dict) and latest_summary.get('report_path'):
        diagnosis = latest_summary.get('latest_browser_attempt_diagnosis') if isinstance(latest_summary.get('latest_browser_attempt_diagnosis'), dict) else None
        if isinstance(diagnosis, dict) and diagnosis.get('summary'):
            diagnosis_hint = f"Latest fixture-lab browser attempt diagnosis: {diagnosis.get('summary')}"
            if diagnosis.get('category'):
                diagnosis_hint += f" (category={diagnosis.get('category')})"
            hints_list = diagnosis.get('hints') if isinstance(diagnosis.get('hints'), list) else []
            if hints_list:
                diagnosis_hint += f" Next check: {hints_list[0]}"
            hints.append(diagnosis_hint + '.')
        failed_setup_count = latest_summary.get('failed_setup_action_count') if isinstance(latest_summary.get('failed_setup_action_count'), int) else 0
        failed_setup_names = latest_summary.get('failed_setup_action_names') if isinstance(latest_summary.get('failed_setup_action_names'), list) else []
        if failed_setup_count:
            ledger_path = latest_summary.get('setup_ledger_path')
            summary_path = latest_summary.get('setup_summary_path')
            failed_fragment = ', '.join(str(item) for item in failed_setup_names[:3]) if failed_setup_names else 'the saved setup action list'
            hint = f"Latest fixture-lab smoke run had {failed_setup_count} failed setup action(s): {failed_fragment}."
            if summary_path:
                hint += f" Start with `{summary_path}` for the compact narrative."
            if ledger_path:
                hint += f" The machine-readable ledger lives at `{ledger_path}`."
            next_command = latest_summary.get('setup_recommended_next_command')
            next_summary = latest_summary.get('setup_recommended_next_summary')
            if next_summary:
                hint += f" Recommended next action: {next_summary}"
            if next_command:
                hint += f" Run `{next_command}`."
            hints.append(hint)
        already_captured = isinstance(latest_capture, dict) and latest_capture.get('report_timestamp') == latest_summary.get('report_timestamp')
        if not already_captured and capture_cmd:
            hints.append(f"A latest fixture-lab smoke report already exists at {latest_summary.get('report_path')}; freeze it with `{capture_cmd}` before the next browser attempt so traces/screenshots/report state stop drifting apart.")
        elif already_captured and capture_history_cmd and isinstance(fixture_history, dict) and fixture_history.get('capture_count'):
            hints.append(f"Fixture-lab smoke capture history already has {fixture_history.get('capture_count')} saved bundle(s); compare them with `{capture_history_cmd}` before rerunning another browser smoke.")

    validation_latest = validation.get('latest_report') if isinstance(validation, dict) else None
    validation_history = validation.get('capture_history') if isinstance(validation, dict) else None
    validation_commands = validation.get('commands') if isinstance(validation, dict) else None
    validation_summary = validation_latest.get('summary') if isinstance(validation_latest, dict) else None
    latest_validation_capture = validation_history.get('latest_capture') if isinstance(validation_history, dict) else None
    validation_capture_cmd = validation_commands.get('capture_latest') if isinstance(validation_commands, dict) else None
    validation_history_cmd = validation_commands.get('capture_history') if isinstance(validation_commands, dict) else None
    validation_resume_cmd = validation_commands.get('resume_latest') if isinstance(validation_commands, dict) else None
    if isinstance(validation_summary, dict):
        already_captured = isinstance(latest_validation_capture, dict) and latest_validation_capture.get('report_path') == validation_summary.get('path') and latest_validation_capture.get('running_step_name') == validation_summary.get('running_step_name') and latest_validation_capture.get('latest_completed_step') == validation_summary.get('latest_completed_step')
        if validation_summary.get('complete') is False and validation_resume_cmd:
            problem = validation_summary.get('running_step_name') or validation_summary.get('required_failed_step') or 'the latest required step'
            hints.append(f"The latest validate-release report is still incomplete around {problem!r}; resume it with `{validation_resume_cmd}` before starting a brand-new umbrella run.")
        if not already_captured and validation_capture_cmd and isinstance(validation_latest, dict) and validation_latest.get('exists'):
            hints.append(f"A validate-release report already exists at {validation_summary.get('path')}; freeze it with `{validation_capture_cmd}` so step logs, running-step state, and resume commands survive the next wrapper attempt.")
        elif already_captured and validation_history_cmd and isinstance(validation_history, dict) and validation_history.get('capture_count'):
            hints.append(f"validate-release capture history already has {validation_history.get('capture_count')} saved bundle(s); compare them with `{validation_history_cmd}` before rerunning another umbrella validation pass.")
        readiness = readiness_commands()
        control_plane = control_plane_commands()
        install_receipt = install_receipt_commands()
        support_surface = support_surface_commands()
        support_bundles = support_bundle_commands()
        published_support = published_support_surface_commands()
        support_publish_gate = support_publish_gate_commands()
        support_source_baseline = support_source_baseline_commands()
        opening_surface = opening_surface_commands()
        truth_surface = truth_surface_commands()
        truth_surface_warnings = truth_surface_warning_commands()
        validation_inventory = validation_artifact_inventory_commands()
        revision_receipt = revision_receipt_commands()
        handoff = operator_handoff_commands()
        hints.append(f"Condense the current profile/smoke/validation state into one next-action board with `{readiness['report']}`, then freeze that board for handoff with `{readiness['capture_latest']}`.")
        hints.append(f"Fuse doctor health, readiness, support-record review pressure, and truth-surface warnings into one operator snapshot with `{control_plane['report']}`, then freeze it with `{control_plane['capture_latest']}` when you want one combined handoff artifact.")
        hints.append(f"Freeze extension/native-host bootstrap truth into one install receipt with `{install_receipt['report']}`, then capture it with `{install_receipt['capture_latest']}` before blaming MV3 runtime behavior.")
        hints.append(f"Freeze the current machine-readable support surface from `docs/support-records/*.md` with `{support_surface['report']}`, then capture it with `{support_surface['capture_latest']}` when support claims or rollout priorities change.")
        hints.append(f"Inspect support-bundle publication pressure with `{support_bundles['report']}`, then freeze or lint that queue with `{support_bundles['capture_latest']}` / `{support_bundles['check_contract']}` before promoting a stronger surface claim.")
        hints.append(f"Keep citable/published support truth separate from the broader queue with `{published_support['report']}`; if a bundle is ready to execute, move it with `{published_support['transition_bundle']}` and refresh `{published_support['write_root']}`.")
        hints.append(f"Fail-closed publish decisions through `{support_publish_gate['report']}` before promoting a held bundle; freeze that gate with `{support_publish_gate['capture_latest']}` or refresh `SUPPORT-PUBLISH-GATE.json` via `{support_publish_gate['write_root']}` so future sessions can see why publication is blocked.")
        hints.append(f"Keep approved-source authority separate from repo evidence with `{support_source_baseline['report']}`; freeze that basis with `{support_source_baseline['capture_latest']}` or refresh `SUPPORT-SOURCE-BASELINE.json` via `{support_source_baseline['write_root']}` before strengthening a support claim.")
        hints.append(f"Check the declared opening contract and refresh `OPENING-SURFACE-CONFORMANCE.json` with `{opening_surface['report']}` or `{opening_surface['write_root']}` before trusting a cold-start path.")
        hints.append(f"Inspect only the non-citable or stale truth heads with `{truth_surface_warnings['report']}`, or freeze that warning queue with `{truth_surface_warnings['capture_latest']}` before citing the latest bundle blindly.")
        hints.append(f"Refresh the whole install/readiness/support/handoff truth stack with `{truth_surface['refresh_all']}`, then inspect lineage drift in one place with `{truth_surface['report']}`.")
        hints.append(f"Summarize validation/latest sprawl into stable artifact buckets with `{validation_inventory['report']}` before pruning, handoff packing, or adding another capture family.")
        hints.append(f"Check that `REVISION-RECEIPT.json` still matches the packaged archive identity and truth-surface counts with `{revision_receipt['report']}` or refresh `REVISION-RECEIPT-CONFORMANCE.json` via `{revision_receipt['write_root']}`.")
        hints.append(f"Freeze the current doctor/readiness state plus linked ledgers and latest evidence into one durable operator handoff bundle with `{handoff['capture_latest']}`.")
        attempt_commands = operator_attempt.get('commands') if isinstance(operator_attempt, dict) else None
        current_attempt = operator_attempt.get('current_attempt') if isinstance(operator_attempt, dict) else None
        attempt_history = operator_attempt.get('history') if isinstance(operator_attempt, dict) else None
        if isinstance(current_attempt, dict) and current_attempt.get('exists') and current_attempt.get('status') == 'in-progress' and isinstance(attempt_commands, dict):
            hints.append(f"An operator attempt is already in progress at {current_attempt.get('path')}; finish the paired after-state with `{attempt_commands.get('finish_latest')}` before starting another live or profile run.")
        elif isinstance(attempt_commands, dict):
            latest_best = ((profiles.get('triage') or {}).get('best_profile') if isinstance(profiles.get('triage'), dict) else None)
            next_command = None
            if isinstance(validation_summary, dict) and validation_summary.get('complete') is False and validation_resume_cmd:
                next_command = validation_resume_cmd
            elif isinstance(latest_best, dict):
                next_command = latest_best.get('next_command') or ((latest_best.get('commands') or {}).get('resume_proof') if isinstance(latest_best.get('commands'), dict) else None)
            if next_command:
                hints.append(f"Wrap the next high-value GlassTTY run in a paired attempt bundle with `{attempt_commands.get('start_latest')} --planned-command {json.dumps(next_command)}` before you execute it, then close the bundle with `{attempt_commands.get('finish_latest')}` so future sessions inherit a true before/after attempt diff instead of two unrelated snapshots.")
            elif isinstance(attempt_history, dict) and attempt_history.get('capture_count'):
                hints.append(f"GlassTTY already has {attempt_history.get('capture_count')} finished operator attempt bundle(s); compare them with `{attempt_commands.get('history')}` before opening a fresh attempt wrapper.")

    if not manifest.get("has_key"):
        hints.append("manifest.key is missing, so unpacked extension IDs may drift across machines or rebuilds.")
    playwright_plan = playwright.get('extension_launch_plan') if isinstance(playwright, dict) else None
    if not playwright.get('available'):
        hints.append("Playwright Python is unavailable; the persistent-context extension lab lane cannot run until it is installed.")
    elif isinstance(playwright_plan, dict) and playwright_plan.get('skip_reason') == 'missing-bundled-chromium':
        import_command = playwright_plan.get('recommended_import_command')
        sync_command = playwright_plan.get('recommended_sync_command')
        download_command = playwright_plan.get('recommended_download_command')
        hints.append("Playwright is installed, but GlassTTY is intentionally skipping the persistent extension lane because no Playwright-managed browser package is present; run `python -m playwright install chromium`, align the cache offline, use the new direct-download sync lane, or explicitly opt into the unsupported system-browser fallback.")
        if sync_command:
            hints.append(f"Offline alignment shortcut: {sync_command} (optionally add --include-headless-shell and/or --archive ...)")
        if download_command:
            hints.append(f"Direct-download shortcut: {download_command} (uses Playwright's current dry-run URLs and reports download failures instead of crashing)")
        elif import_command:
            hints.append(f"Offline fallback: {import_command}")
    elif isinstance(playwright_plan, dict) and playwright_plan.get('skip_reason') == 'no-playwright-browser':
        hints.append("Playwright can import, but no Playwright-managed browser package or system Chromium executable is available for persistent-context extension testing.")
    elif isinstance(playwright_plan, dict) and playwright_plan.get('risky_fallback'):
        hints.append(f"GlassTTY is using the Playwright system-browser fallback because {PLAYWRIGHT_ALLOW_SYSTEM_ENV}=1 is set; this is a best-effort lab path, not the recommended extension-testing route.")
    if isinstance(playwright_plan, dict) and playwright_plan.get('cache_alignment_status') == 'cache-install-name-drift':
        reason = playwright_plan.get('cache_alignment_reason') or 'The cached Playwright browser package name does not match the current expected package name.'
        channel_cmd = playwright_plan.get('recommended_channel_ready_command') or playwright_plan.get('recommended_realign_command') or playwright_plan.get('recommended_sync_command')
        hints.append(f"Playwright cache alignment warning: {reason} GlassTTY can still use explicit executable_path for now, but the official headless extension lane remains blocked until the cache is realigned.")
        if channel_cmd:
            hints.append(f"Playwright channel-alignment shortcut: {channel_cmd} (restores the documented `channel=\"chromium\"` path when the cache can be reconciled with the current Playwright package identity).")
    elif isinstance(playwright_plan, dict) and playwright_plan.get('cache_alignment_status') == 'system-browser-fallback':
        channel_cmd = playwright_plan.get('recommended_channel_ready_command') or playwright_plan.get('recommended_realign_command')
        if channel_cmd:
            hints.append(f"Playwright is on the opt-in system-browser fallback instead of the documented bundled Chromium lane; realign the cache with `{channel_cmd}` before comparing extension failures against the official Playwright path.")
    cache_audit = playwright.get('cache_audit') if isinstance(playwright, dict) else None
    if isinstance(cache_audit, dict):
        if (cache_audit.get('counts') or {}).get('current_unlinked_existing_browsers'):
            hints.append(f"Playwright cache truth warning: {(cache_audit.get('counts') or {}).get('current_unlinked_existing_browsers')} current-package browser install(s) exist on disk without the current driver link, so raw install --list and cache ownership may currently be coming from some other Playwright client or from no client at all.")
        if (cache_audit.get('counts') or {}).get('foreign_only_installs'):
            hints.append(f"Playwright cache ownership warning: {(cache_audit.get('counts') or {}).get('foreign_only_installs')} browser install(s) are currently kept alive only by non-current Playwright package links; repair the current link before treating this cache as self-owned.")
        if (cache_audit.get('counts') or {}).get('shadow_installs'):
            hints.append(f"Playwright cache truth warning: {(cache_audit.get('counts') or {}).get('shadow_installs')} browser install(s) exist on disk but are not referenced by any Playwright package link, so upstream install --list will ignore them and a future Playwright install may garbage-collect them.")
        if (cache_audit.get('counts') or {}).get('marker_missing_registered_browsers'):
            hints.append(f"Playwright cache marker warning: {(cache_audit.get('counts') or {}).get('marker_missing_registered_browsers')} Playwright-recognized browser install(s) are missing INSTALLATION_COMPLETE, so a future `python -m playwright install …` may delete them as stale before GlassTTY can use them.")
        elif (cache_audit.get('counts') or {}).get('marker_missing_installs'):
            hints.append(f"Playwright cache marker warning: {(cache_audit.get('counts') or {}).get('marker_missing_installs')} on-disk browser install(s) are missing INSTALLATION_COMPLETE, so future Playwright stale-browser cleanup may remove them unless the marker is restored or PLAYWRIGHT_SKIP_BROWSER_GC=1 is set.")
        if (cache_audit.get('counts') or {}).get('broken_links'):
            hints.append(f"Playwright cache registry warning: {(cache_audit.get('counts') or {}).get('broken_links')} broken .links reference(s) were found; a future Playwright install is likely to delete those broken registrations.")
        if (cache_audit.get('counts') or {}).get('stale_registered_browsers'):
            hints.append(f"Playwright cache registry tracks {(cache_audit.get('counts') or {}).get('stale_registered_browsers')} browser path(s) that are missing on disk; treat install --list output and cache cleanup as unstable until the cache is reconciled.")
        if (cache_audit.get('counts') or {}).get('gc_candidate_installs'):
            hints.append(f"Playwright GC warning: {(cache_audit.get('counts') or {}).get('gc_candidate_installs')} local browser install(s) currently satisfy Playwright's stale-browser deletion conditions.")
    repair_plan = playwright.get('repair_plan') if isinstance(playwright, dict) else None
    if isinstance(repair_plan, dict):
        if (repair_plan.get('counts') or {}).get('current_link_repairs'):
            hints.append(f"Playwright cache repair shortcut: {repair_plan.get('recommended_apply_command')} (restores the current Playwright package link so raw install --list and stale-browser ownership stop depending on foreign clients or cache prep).")
        elif (repair_plan.get('counts') or {}).get('repairable_shadow_installs'):
            hints.append(f"Playwright cache repair shortcut: {repair_plan.get('recommended_apply_command')} (aligns repairable shadow installs with the current Playwright package names instead of leaving them invisible to upstream install --list).")
        elif (repair_plan.get('counts') or {}).get('missing_marker_repairs'):
            hints.append(f"Playwright cache repair shortcut: {repair_plan.get('recommended_apply_command')} (restores INSTALLATION_COMPLETE so imported browsers survive the next Playwright install instead of being cleaned as stale).")
        elif (repair_plan.get('counts') or {}).get('broken_link_repairs'):
            hints.append(f"Playwright cache repair shortcut: {repair_plan.get('recommended_apply_command')} (removes broken registry links before a future Playwright install cleans them implicitly).")
    return hints


def build_report() -> dict[str, Any]:
    manifest = manifest_info()
    chrome_for_testing = chrome_for_testing_info()
    playwright = playwright_info()
    native_host = native_host_info(chrome_for_testing.get('default_browser') if isinstance(chrome_for_testing, dict) else None, playwright)
    socket = socket_info()
    profiles = profile_info()
    commands = [command_info("python3"), command_info("node"), command_info("npm"), command_info("chromium"), command_info("google-chrome"), command_info("playwright")]
    fixture_lab = fixture_lab_info()
    validation = validation_info()
    report = {
        "project": "GlassTTY",
        "root": str(ROOT),
        "glasstty_home": str(DEFAULT_HOME),
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "python": sys.version.split()[0], "geteuid": os.geteuid() if hasattr(os, "geteuid") else None},
        "manifest": manifest,
        "native_host": native_host,
        "socket": socket,
        "profiles": profiles,
        "fixture_lab": fixture_lab,
        "validation": validation,
        "readiness": {"commands": readiness_commands()},
        "control_plane": {"commands": control_plane_commands()},
        "install_receipt": {"commands": install_receipt_commands()},
        "support_surface": {"commands": support_surface_commands()},
        "support_bundles": {"commands": support_bundle_commands()},
        "published_support_surface": {"commands": published_support_surface_commands()},
        "support_source_baseline": {"commands": support_source_baseline_commands()},
        "opening_surface": {"commands": opening_surface_commands()},
        "truth_surface": {"commands": truth_surface_commands()},
        "truth_surface_warnings": {"commands": truth_surface_warning_commands()},
        "validation_artifact_inventory": {"commands": validation_artifact_inventory_commands()},
        "revision_receipt": {"commands": revision_receipt_commands()},
        "operator_handoff": {"commands": operator_handoff_commands()},
        "operator_attempt": {"commands": operator_attempt_commands(), "current_attempt": summarize_current_attempt(ROOT / 'validation' / 'latest' / 'operator-attempt'), "history": summarize_operator_attempt_history(ROOT / 'validation' / 'operator-attempts.json')},
        "playwright": playwright,
        "chrome_for_testing": chrome_for_testing,
        "commands": commands,
        "quickstart": [
            "./scripts/smoke.sh",
            "./scripts/glasstty-profile.sh open main chrome://extensions/",
            native_host.get("suggested_install_command") or "./scripts/install-native-host.sh --target chromium --extension-id auto",
            *native_host.get("suggested_install_commands", []),
            "python -m glassttyd.cli bridge-status --wait --timeout 10",
        ],
    }
    report['hints'] = analyze_hints(manifest, native_host, socket, profiles, commands, playwright, chrome_for_testing, fixture_lab, validation, report['operator_attempt'])
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect the local GlassTTY environment and print a JSON report")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    report = build_report()
    print(json.dumps(report, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
