from __future__ import annotations

import argparse
import json
import os
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

from browser_binaries import augment_browser_choice, discover_browser_executable
from native_host_manifest import HOST_NAME, inspect_targets, normalize_os_name, resolve_install_targets
from playwright_browsers import discover_playwright_browser_install, playwright_browser_choice, playwright_extension_launch_plan
from glassttyd.overflow_artifacts import summarize_overflow_inventory

ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = ROOT / 'extension' / 'manifest.json'
DEFAULT_WRAPPER = ROOT / 'scripts' / 'native-host-wrapper.sh'




def ordered_targets(*groups: list[str] | tuple[str, ...] | None) -> list[str]:
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


def compact_install_command(*, target: str, extension_id: str | None, host_exe: str) -> str:
    return f'./scripts/install-native-host.sh --target {target} --extension-id {extension_id or "auto"} --host-exe {host_exe}'


def explicit_install_commands(*, targets: list[str], extension_id: str | None, host_exe: str) -> list[str]:
    return [compact_install_command(target=target, extension_id=extension_id, host_exe=host_exe) for target in targets]


def preferred_matrix_install_command(*, default_targets: list[str], playwright_targets: list[str], combined_targets: list[str], extension_id: str | None, host_exe: str) -> str | None:
    if not combined_targets:
        return None
    if len(combined_targets) == 1:
        return compact_install_command(target=combined_targets[0], extension_id=extension_id, host_exe=host_exe)
    if combined_targets == playwright_targets and playwright_targets:
        return compact_install_command(target='playwright', extension_id=extension_id, host_exe=host_exe)
    if combined_targets == default_targets and default_targets:
        return compact_install_command(target='auto', extension_id=extension_id, host_exe=host_exe)
    return compact_install_command(target='combined', extension_id=extension_id, host_exe=host_exe)


def resolve_target_scope(*, target: str, all_recommended: bool, browser_choice: dict[str, Any] | None, playwright_choice: dict[str, Any] | None) -> dict[str, Any]:
    normalized_target = target.strip().lower()
    explicit_directory = '/' in target or target.startswith('.') or target.startswith('~')
    default_resolution = resolve_install_targets('auto', browser_choice=browser_choice, all_recommended=True)
    default_targets = list(default_resolution.get('resolved_targets') or [])
    playwright_targets = list((playwright_choice or {}).get('native_messaging_targets') or [])
    combined_targets = ordered_targets(playwright_targets, default_targets)
    if explicit_directory:
        resolved_targets = [target]
        selection_mode = 'explicit-directory'
        used_browser_recommendation = False
    elif normalized_target in {'auto', 'recommended', 'default', 'default-browser'}:
        resolved_targets = default_targets if all_recommended else default_targets[:1]
        selection_mode = 'default-browser'
        used_browser_recommendation = True
    elif normalized_target in {'playwright', 'playwright-recommended', 'extension-browser'}:
        lane_targets = playwright_targets or default_targets
        resolved_targets = lane_targets if all_recommended else lane_targets[:1]
        selection_mode = 'playwright-browser'
        used_browser_recommendation = True
    elif normalized_target in {'combined', 'matrix', 'combined-recommended'}:
        resolved_targets = combined_targets
        selection_mode = 'combined-browser-matrix'
        used_browser_recommendation = True
    else:
        resolved_targets = [target]
        selection_mode = 'explicit-target'
        used_browser_recommendation = False
    return {
        'requested_target': target,
        'resolved_targets': resolved_targets,
        'selection_mode': selection_mode,
        'browser_choice': browser_choice,
        'playwright_choice': playwright_choice,
        'default_browser_targets': default_targets,
        'playwright_targets': playwright_targets,
        'combined_targets': combined_targets,
        'used_browser_recommendation': used_browser_recommendation,
        'all_recommended': all_recommended,
    }

def compute_extension_id() -> str | None:
    script = ROOT / 'scripts' / 'extension-id.py'
    try:
        result = subprocess.run([sys.executable, str(script), str(MANIFEST_PATH)], check=True, capture_output=True, text=True)
    except Exception:
        return None
    value = result.stdout.strip()
    return value or None


def browser_choice_for_path(browser_bin: str | None) -> dict[str, Any] | None:
    if not browser_bin:
        return None
    path = str(Path(browser_bin).expanduser())
    return augment_browser_choice({'source': 'explicit-bin', 'path': path, 'exists': Path(path).exists()})


def summarize_recommended_targets(targets: dict[str, Any], recommended_targets: list[str]) -> dict[str, Any]:
    missing: list[str] = []
    extension_id_mismatches: list[str] = []
    host_path_mismatches: list[str] = []
    parse_failures: list[str] = []
    ready: list[str] = []
    for target in recommended_targets:
        info = targets.get(target) or {}
        if not info.get('manifest_exists'):
            missing.append(target)
            continue
        if not info.get('manifest_parse_ok'):
            parse_failures.append(target)
            continue
        if info.get('extension_id_match') is False:
            extension_id_mismatches.append(target)
        if info.get('host_path_match') is False:
            host_path_mismatches.append(target)
        if info.get('manifest_parse_ok') and info.get('extension_id_match') is not False and info.get('host_path_match') is not False:
            ready.append(target)
    primary = recommended_targets[0] if recommended_targets else None
    primary_info = targets.get(primary) if primary else None
    primary_ready = bool(primary and primary in ready)
    return {
        'ready_targets': ready,
        'missing_targets': missing,
        'parse_failure_targets': parse_failures,
        'extension_id_mismatch_targets': extension_id_mismatches,
        'host_path_mismatch_targets': host_path_mismatches,
        'all_recommended_ready': len(recommended_targets) > 0 and len(ready) == len(recommended_targets),
        'any_recommended_ready': bool(ready),
        'primary_target': primary,
        'primary_target_ready': primary_ready,
        'primary_target_info': primary_info,
    }


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def native_host_overflow_info(home: Path | None = None) -> dict[str, Any]:
    home = home or Path(os.environ.get('GLASSTTY_HOME', Path.home() / '.local' / 'share' / 'glasstty'))
    latest_path = home / 'state' / 'latest' / 'oversized-host-outbound.json'
    latest = read_json_if_exists(latest_path)
    artifact_path = Path(latest['artifact_path']).expanduser() if isinstance(latest, dict) and isinstance(latest.get('artifact_path'), str) and latest.get('artifact_path') else None
    return {
        'latest_path': str(latest_path),
        'latest_exists': latest_path.exists(),
        'latest_summary': latest,
        'artifact_path': str(artifact_path) if artifact_path else None,
        'artifact_exists': bool(artifact_path and artifact_path.exists()),
        'inventory': summarize_overflow_inventory(home),
    }


def native_host_runtime_info(home: Path | None = None) -> dict[str, Any]:
    home = home or Path(os.environ.get('GLASSTTY_HOME', Path.home() / '.local' / 'share' / 'glasstty'))
    run_dir = home / 'run'
    socket_path = run_dir / 'daemon.sock'
    lock_path = run_dir / 'daemon-broker.lock'
    metadata_path = run_dir / 'daemon-broker-owner.json'
    metadata = read_json_if_exists(metadata_path)
    return {
        'run_dir': str(run_dir),
        'socket_path': str(socket_path),
        'socket_exists': socket_path.exists(),
        'lock_path': str(lock_path),
        'lock_exists': lock_path.exists(),
        'metadata_path': str(metadata_path),
        'metadata_exists': metadata_path.exists(),
        'owner_metadata': metadata,
    }


def build_report(*, os_name: str | None = None, extension_id: str | None = None, host_exe: str | None = None, browser_bin: str | None = None, home: Path | None = None) -> dict[str, Any]:
    os_name = normalize_os_name(os_name)
    extension_id = extension_id or compute_extension_id()
    host_exe = str(Path(host_exe or DEFAULT_WRAPPER).expanduser())
    browser_choice = browser_choice_for_path(browser_bin) or discover_browser_executable()
    recommended = resolve_install_targets('auto', browser_choice=browser_choice, all_recommended=False)
    recommended_all = resolve_install_targets('auto', browser_choice=browser_choice, all_recommended=True)
    playwright_install = discover_playwright_browser_install()
    playwright_launch = playwright_extension_launch_plan(browser_install=playwright_install)
    playwright_choice = playwright_browser_choice(playwright_install, launch_plan=playwright_launch)
    playwright_targets = list((playwright_choice or {}).get('native_messaging_targets') or [])
    targets = inspect_targets(os_name=os_name, extension_id=extension_id, expected_host_path=host_exe, home=home)
    recommendation_status = summarize_recommended_targets(targets, list(recommended_all['resolved_targets']))
    playwright_status = summarize_recommended_targets(targets, playwright_targets) if playwright_targets else {
        'ready_targets': [],
        'missing_targets': [],
        'parse_failure_targets': [],
        'extension_id_mismatch_targets': [],
        'host_path_mismatch_targets': [],
        'all_recommended_ready': False,
        'any_recommended_ready': False,
        'primary_target': None,
        'primary_target_ready': False,
        'primary_target_info': None,
    }
    combined_targets = ordered_targets(playwright_targets, list(recommended_all['resolved_targets'] or []))
    combined_status = summarize_recommended_targets(targets, combined_targets) if combined_targets else playwright_status
    suggested_install_commands = explicit_install_commands(targets=combined_targets, extension_id=extension_id, host_exe=host_exe)
    suggested_install_matrix_command = preferred_matrix_install_command(
        default_targets=list(recommended_all['resolved_targets'] or []),
        playwright_targets=playwright_targets,
        combined_targets=combined_targets,
        extension_id=extension_id,
        host_exe=host_exe,
    )
    return {
        'host_name': HOST_NAME,
        'os': os_name,
        'extension_id': extension_id,
        'host_executable': host_exe,
        'host_executable_exists': Path(host_exe).exists(),
        'host_executable_executable': Path(host_exe).exists() and os.access(host_exe, os.X_OK),
        'browser_bin': str(Path(browser_bin).expanduser()) if browser_bin else None,
        'default_browser': browser_choice,
        'recommended_targets': recommended['resolved_targets'],
        'all_recommended_targets': recommended_all['resolved_targets'],
        'recommended_target_notes': list((browser_choice or {}).get('native_messaging_notes') or []),
        'recommended_target_status': recommendation_status,
        'playwright_browser_install': playwright_install,
        'playwright_launch_plan': playwright_launch,
        'playwright_browser_choice': playwright_choice,
        'playwright_recommended_targets': playwright_targets,
        'playwright_recommended_target_status': playwright_status,
        'combined_recommended_targets': combined_targets,
        'combined_recommended_target_status': combined_status,
        'targets': targets,
        'suggested_install_command': suggested_install_matrix_command or (suggested_install_commands[0] if suggested_install_commands else None),
        'suggested_install_commands': suggested_install_commands,
        'suggested_install_matrix_command': suggested_install_matrix_command,
        'last_oversized_host_message': native_host_overflow_info(home=home),
        'runtime': native_host_runtime_info(home=home),
    }


def build_resolve_targets(*, target: str, all_recommended: bool, browser_bin: str | None = None) -> dict[str, Any]:
    browser_choice = browser_choice_for_path(browser_bin) or discover_browser_executable()
    playwright_install = discover_playwright_browser_install()
    playwright_launch = playwright_extension_launch_plan(browser_install=playwright_install)
    playwright_choice = playwright_browser_choice(playwright_install, launch_plan=playwright_launch)
    payload = resolve_target_scope(target=target, all_recommended=all_recommended, browser_choice=browser_choice, playwright_choice=playwright_choice)
    payload['playwright_browser_install'] = playwright_install
    payload['playwright_launch_plan'] = playwright_launch
    return payload


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description='Inspect GlassTTY native-host installation state and browser-aware target recommendations')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--os', dest='os_name', choices=['linux', 'macos'])
    parser.add_argument('--extension-id')
    parser.add_argument('--host-exe')
    parser.add_argument('--browser-bin')
    sub = parser.add_subparsers(dest='command')
    resolve = sub.add_parser('resolve-targets', help='Resolve default-browser, Playwright-lane, or combined native-host install targets for the current environment')
    resolve.add_argument('--target', default='auto')
    resolve.add_argument('--all-recommended', action='store_true')
    resolve.add_argument('--print-targets', action='store_true')
    args = parser.parse_args(argv)

    if args.command == 'resolve-targets':
        payload = build_resolve_targets(target=args.target, all_recommended=args.all_recommended, browser_bin=args.browser_bin)
        if args.print_targets:
            print('\n'.join(payload['resolved_targets']))
            return
    else:
        payload = build_report(os_name=args.os_name, extension_id=args.extension_id, host_exe=args.host_exe, browser_bin=args.browser_bin)
    print(json.dumps(payload, indent=2 if args.pretty else None))
