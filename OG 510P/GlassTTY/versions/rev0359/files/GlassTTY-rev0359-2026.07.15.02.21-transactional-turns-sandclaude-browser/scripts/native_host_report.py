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

ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = ROOT / 'extension' / 'manifest.json'
DEFAULT_WRAPPER = ROOT / 'scripts' / 'native-host-wrapper.sh'


def compact_install_command(*, target: str, extension_id: str | None, host_exe: str) -> str:
    return f'./scripts/install-native-host.sh --target {target} --extension-id {extension_id or "auto"} --host-exe {host_exe}'


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
    return augment_browser_choice({'source': 'explicit-bin', 'path': path, 'exists': Path(path).exists(), 'version': path})


def summarize_recommended_targets(targets: dict[str, Any], recommended_targets: list[str]) -> dict[str, Any]:
    missing: list[str] = []
    ready: list[str] = []
    extension_id_mismatches: list[str] = []
    host_path_mismatches: list[str] = []
    parse_failures: list[str] = []
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
    return {
        'ready_targets': ready,
        'missing_targets': missing,
        'parse_failure_targets': parse_failures,
        'extension_id_mismatch_targets': extension_id_mismatches,
        'host_path_mismatch_targets': host_path_mismatches,
        'all_recommended_ready': bool(recommended_targets) and len(ready) == len(recommended_targets),
        'any_recommended_ready': bool(ready),
        'primary_target': primary,
        'primary_target_ready': bool(primary and primary in ready),
        'primary_target_info': targets.get(primary) if primary else None,
    }


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def native_host_overflow_info(home: Path | None = None) -> dict[str, Any]:
    from glassttyd.overflow_artifacts import compact_overflow_inventory_summary

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
        'inventory': compact_overflow_inventory_summary(home),
    }


def build_report(*, os_name: str | None = None, extension_id: str | None = None, host_exe: str | None = None, browser_bin: str | None = None, home: Path | None = None) -> dict[str, Any]:
    os_name = normalize_os_name(os_name)
    extension_id = extension_id or compute_extension_id()
    host_exe = str(Path(host_exe or DEFAULT_WRAPPER).expanduser())
    browser_choice = browser_choice_for_path(browser_bin) or discover_browser_executable()
    recommended = resolve_install_targets('auto', browser_choice=browser_choice, all_recommended=False)
    recommended_all = resolve_install_targets('auto', browser_choice=browser_choice, all_recommended=True)
    recommended_targets = list(recommended.get('resolved_targets') or [])
    all_recommended_targets = list(recommended_all.get('resolved_targets') or [])
    targets = inspect_targets(os_name=os_name, extension_id=extension_id, expected_host_path=host_exe, home=home)
    return {
        'schema_version': 2,
        'host_name': HOST_NAME,
        'provider_scope': 'chatgpt-only',
        'manifest_path': str(MANIFEST_PATH),
        'extension_id': extension_id,
        'host_exe': host_exe,
        'browser_choice': browser_choice,
        'recommended_targets': recommended_targets,
        'all_recommended_targets': all_recommended_targets,
        'targets': targets,
        'recommended_target_status': summarize_recommended_targets(targets, recommended_targets),
        'suggested_install_command': compact_install_command(target=recommended_targets[0] if recommended_targets else 'chromium', extension_id=extension_id, host_exe=host_exe),
        'overflow': native_host_overflow_info(home),
    }


def build_resolve_targets(*, target: str, all_recommended: bool = False, browser_bin: str | None = None) -> dict[str, Any]:
    target_key = target.strip().lower()
    browser_choice = None
    if target_key in {'auto', 'recommended'}:
        browser_choice = browser_choice_for_path(browser_bin) or discover_browser_executable()
    return resolve_install_targets(target, browser_choice=browser_choice, all_recommended=all_recommended)


def main() -> int:
    parser = argparse.ArgumentParser(description='Report or resolve native-host install targets for the ChatGPT-only cube.')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--os', dest='os_name')
    parser.add_argument('--extension-id')
    parser.add_argument('--host-exe')
    parser.add_argument('--browser-bin')
    parser.add_argument('--home')
    sub = parser.add_subparsers(dest='command')
    resolve = sub.add_parser('resolve-targets')
    resolve.add_argument('--target', default='auto')
    resolve.add_argument('--all-recommended', action='store_true')
    resolve.add_argument('--browser-bin', dest='resolve_browser_bin')
    resolve.add_argument('--print-targets', action='store_true')
    args = parser.parse_args()
    if args.command == 'resolve-targets':
        payload = build_resolve_targets(target=args.target, all_recommended=args.all_recommended, browser_bin=args.resolve_browser_bin or args.browser_bin)
        if args.print_targets:
            for target in payload.get('resolved_targets') or []:
                print(target)
        else:
            print(json.dumps(payload, indent=2 if args.pretty else None))
        return 0
    home = Path(args.home).expanduser() if args.home else None
    print(json.dumps(build_report(os_name=args.os_name, extension_id=args.extension_id, host_exe=args.host_exe, browser_bin=args.browser_bin, home=home), indent=2 if args.pretty else None))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
