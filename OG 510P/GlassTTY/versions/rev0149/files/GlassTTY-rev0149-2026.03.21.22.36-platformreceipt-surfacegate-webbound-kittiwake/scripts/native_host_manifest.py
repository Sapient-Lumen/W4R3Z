from __future__ import annotations

import json
import os
import platform
from pathlib import Path
from typing import Any

from browser_binaries import discover_browser_executable

HOST_NAME = 'com.glasstty.bridge'


def normalize_os_name(raw: str | None = None) -> str:
    value = (raw or platform.system()).lower()
    if value == 'darwin':
        return 'macos'
    if value == 'linux':
        return 'linux'
    return value


def default_target_dirs(os_name: str | None = None, *, home: Path | None = None) -> dict[str, Path]:
    os_name = normalize_os_name(os_name)
    home = (home or Path.home()).expanduser()
    if os_name == 'linux':
        return {
            'chromium': home / '.config' / 'chromium' / 'NativeMessagingHosts',
            'chrome': home / '.config' / 'google-chrome' / 'NativeMessagingHosts',
            'chrome-for-testing': home / '.config' / 'google-chrome-for-testing' / 'NativeMessagingHosts',
        }
    if os_name == 'macos':
        return {
            'chromium': home / 'Library' / 'Application Support' / 'Chromium' / 'NativeMessagingHosts',
            'chrome': home / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'NativeMessagingHosts',
            'chrome-for-testing': home / 'Library' / 'Application Support' / 'Google' / 'ChromeForTesting' / 'NativeMessagingHosts',
        }
    return {}


def resolve_target_dir(target: str, os_name: str | None = None, *, home: Path | None = None) -> Path:
    target = target.strip()
    if '/' in target or target.startswith('.') or target.startswith('~'):
        return Path(target).expanduser()
    dirs = default_target_dirs(os_name, home=home)
    try:
        return dirs[target]
    except KeyError as exc:
        raise ValueError(f'unsupported native-host target {target!r} for os {normalize_os_name(os_name)!r}') from exc


def manifest_path_for_target(target: str, os_name: str | None = None, *, home: Path | None = None, host_name: str = HOST_NAME) -> Path:
    return resolve_target_dir(target, os_name, home=home) / f'{host_name}.json'


def render_manifest(*, host_path: str | os.PathLike[str], extension_id: str, host_name: str = HOST_NAME) -> dict[str, Any]:
    return {
        'name': host_name,
        'description': 'GlassTTY native messaging host',
        'path': str(Path(host_path)),
        'type': 'stdio',
        'allowed_origins': [f'chrome-extension://{extension_id}/'],
    }


def _allowed_extension_ids(origins: list[Any]) -> list[str]:
    values: list[str] = []
    for origin in origins:
        if not isinstance(origin, str):
            continue
        prefix = 'chrome-extension://'
        if origin.startswith(prefix):
            remainder = origin[len(prefix):]
            ext_id = remainder.split('/', 1)[0]
            if ext_id:
                values.append(ext_id)
    return values


def inspect_manifest_file(manifest_path: Path, *, expected_extension_id: str | None = None, expected_host_path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    report: dict[str, Any] = {
        'manifest_path': str(manifest_path),
        'manifest_exists': manifest_path.exists(),
        'manifest_parse_ok': False,
        'manifest': None,
        'manifest_error': None,
        'allowed_extension_ids': [],
        'allowed_origins': [],
        'manifest_host_path': None,
        'manifest_host_path_is_absolute': None,
        'manifest_host_exists': None,
        'manifest_host_executable': None,
        'extension_id_match': None,
        'host_path_match': None,
    }
    if not manifest_path.exists():
        return report
    try:
        payload = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as exc:
        report['manifest_error'] = str(exc)
        return report
    report['manifest_parse_ok'] = True
    report['manifest'] = payload
    allowed_origins = payload.get('allowed_origins') if isinstance(payload, dict) else None
    if not isinstance(allowed_origins, list):
        allowed_origins = []
    allowed_extension_ids = _allowed_extension_ids(allowed_origins)
    host_path = payload.get('path') if isinstance(payload, dict) else None
    host_candidate = Path(host_path).expanduser() if isinstance(host_path, str) and host_path else None
    report.update(
        {
            'allowed_origins': allowed_origins,
            'allowed_extension_ids': allowed_extension_ids,
            'manifest_host_path': str(host_candidate) if host_candidate else None,
            'manifest_host_path_is_absolute': bool(host_candidate and host_candidate.is_absolute()),
            'manifest_host_exists': bool(host_candidate and host_candidate.exists()),
            'manifest_host_executable': bool(host_candidate and host_candidate.exists() and os.access(host_candidate, os.X_OK)),
        }
    )
    if expected_extension_id:
        report['extension_id_match'] = expected_extension_id in allowed_extension_ids
    if expected_host_path:
        report['host_path_match'] = (str(host_candidate) == str(Path(expected_host_path))) if host_candidate else False
    return report


def inspect_targets(
    *,
    os_name: str | None = None,
    extension_id: str | None = None,
    expected_host_path: str | os.PathLike[str] | None = None,
    home: Path | None = None,
    targets: list[str] | None = None,
) -> dict[str, Any]:
    os_name = normalize_os_name(os_name)
    known_targets = targets or list(default_target_dirs(os_name, home=home).keys())
    payload: dict[str, Any] = {}
    for target in known_targets:
        manifest_path = manifest_path_for_target(target, os_name, home=home)
        info = inspect_manifest_file(manifest_path, expected_extension_id=extension_id, expected_host_path=expected_host_path)
        info['target'] = target
        info['target_dir'] = str(manifest_path.parent)
        payload[target] = info
    return payload


def resolve_install_targets(
    requested_target: str,
    *,
    browser_choice: dict[str, Any] | None = None,
    all_recommended: bool = False,
    fallback_target: str = 'chromium',
) -> dict[str, Any]:
    target = requested_target.strip().lower()
    if target not in {'auto', 'recommended'}:
        return {
            'requested_target': requested_target,
            'resolved_targets': [requested_target],
            'browser_choice': browser_choice,
            'used_browser_recommendation': False,
            'all_recommended': all_recommended,
        }
    browser_choice = browser_choice or discover_browser_executable()
    recommended_targets = list((browser_choice or {}).get('native_messaging_targets') or [])
    if not recommended_targets:
        recommended_targets = [fallback_target]
    resolved_targets = recommended_targets if all_recommended else [recommended_targets[0]]
    return {
        'requested_target': requested_target,
        'resolved_targets': resolved_targets,
        'browser_choice': browser_choice,
        'used_browser_recommendation': True,
        'all_recommended': all_recommended,
    }
