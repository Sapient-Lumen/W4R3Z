from __future__ import annotations

import json
import os
import shlex
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from browser_binaries import augment_browser_choice, discover_browser_executable
from native_host_manifest import resolve_install_targets


LOCAL_PROBE_HOSTS = {'127.0.0.1', 'localhost', '::1'}


def glasstty_home() -> Path:
    return Path(os.environ.get('GLASSTTY_HOME', Path.home() / '.local' / 'share' / 'glasstty'))


def profiles_root(home: Path | None = None) -> Path:
    return (home or glasstty_home()) / 'profiles'


def profile_dir(name: str, home: Path | None = None) -> Path:
    return profiles_root(home) / name


def metadata_path(profile: Path) -> Path:
    return profile / 'glasstty-profile.json'


def native_host_audit_path(profile: Path) -> Path:
    return profile / 'glasstty-native-host.json'


def devtools_active_port_path(profile: Path) -> Path:
    return profile / 'DevToolsActivePort'


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def mv3_resume_report_path(profile: Path) -> Path:
    return profile / 'glasstty-mv3-worker-resume.json'


def mv3_resume_summary_path(profile: Path) -> Path:
    return profile / 'glasstty-mv3-worker-resume-summary.json'


def capture_history_path(profile: Path) -> Path:
    return profile / 'glasstty-profile-captures.json'


def fleet_capture_history_path(home: Path | None = None) -> Path:
    return (home or glasstty_home()) / 'glasstty-profile-fleet-captures.json'


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        return None
    except Exception:
        return {'_read_error': f'could not parse {path.name}'}
    return data if isinstance(data, dict) else {'_read_error': f'{path.name} was not a JSON object'}


def _first_non_flag_arg(args: Iterable[str]) -> str | None:
    for value in args:
        if value == '--':
            continue
        if value.startswith('-'):
            continue
        return value
    return None


def _path_timestamp(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _probe_tcp_endpoint(host: str, port: str, *, timeout: float = 0.25) -> dict[str, Any]:
    info: dict[str, Any] = {'attempted': False, 'host': host, 'port': port, 'timeout_seconds': timeout}
    if host not in LOCAL_PROBE_HOSTS:
        info['skipped'] = True
        info['reason'] = 'tcp probe only runs for loopback hosts'
        return info
    if not str(port).isdigit():
        info['skipped'] = True
        info['reason'] = 'port is not numeric'
        return info
    info['attempted'] = True
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            info['ok'] = True
            return info
    except Exception as exc:  # noqa: BLE001
        info['ok'] = False
        info['error'] = str(exc)
        return info


def _remote_debugging_value(mode: str | None, port: Any) -> str | None:
    if mode == 'ephemeral' or port in ('0', 0):
        return 'auto'
    if port in (None, ''):
        return None
    return str(port).strip()


def _browser_choice_for_path(path: str | os.PathLike[str] | None, *, source: str) -> dict[str, Any] | None:
    if not path:
        return None
    candidate = Path(path).expanduser()
    return augment_browser_choice({'source': source, 'path': str(candidate), 'exists': candidate.exists()})


def _native_host_recommendation(browser_choice: dict[str, Any] | None) -> dict[str, Any]:
    resolution = resolve_install_targets('recommended', browser_choice=browser_choice, all_recommended=True)
    targets = [str(value) for value in (resolution.get('resolved_targets') or [])]
    return {
        'browser_choice': browser_choice,
        'recommended_targets': targets,
        'install_commands': [f'./scripts/install-native-host.sh --target {target} --extension-id auto' for target in targets],
    }


def _portable_reopen_command(profile_name: str, *, remote_debugging: str | None = None) -> str:
    command = ['./scripts/glasstty-profile.sh', 'reopen', profile_name, '--allow-discovered-browser-fallback']
    if remote_debugging is not None:
        command.extend(['--remote-debugging-port', remote_debugging])
    return shlex.join(command)


def _capture_history_payload(profile: Path) -> dict[str, Any] | None:
    data = _read_json(capture_history_path(profile))
    return data if isinstance(data, dict) else None


def summarize_capture_history(profile: Path) -> dict[str, Any]:
    path = capture_history_path(profile)
    payload = _capture_history_payload(profile)
    entries_raw = payload.get('entries') if isinstance(payload, dict) else None
    entries = [entry for entry in entries_raw if isinstance(entry, dict)] if isinstance(entries_raw, list) else []
    latest = entries[-1] if entries else None
    previous = entries[-2] if len(entries) > 1 else None
    latest_bundle_summary = Path(str(latest.get('bundle_summary_path'))).expanduser() if isinstance(latest, dict) and isinstance(latest.get('bundle_summary_path'), str) and latest.get('bundle_summary_path') else None
    latest_summary_markdown = Path(str(latest.get('summary_markdown_path'))).expanduser() if isinstance(latest, dict) and isinstance(latest.get('summary_markdown_path'), str) and latest.get('summary_markdown_path') else None
    return {
        'path': str(path),
        'exists': path.exists(),
        'capture_count': len(entries),
        'updated_at': payload.get('updated_at') if isinstance(payload, dict) else None,
        'latest_capture': latest,
        'previous_capture': previous,
        'latest_bundle_summary_exists': bool(latest_bundle_summary and latest_bundle_summary.exists()),
        'latest_summary_markdown_exists': bool(latest_summary_markdown and latest_summary_markdown.exists()),
        'history': payload,
    }

def summarize_fleet_capture_history(home: Path | None = None) -> dict[str, Any]:
    path = fleet_capture_history_path(home)
    payload = _read_json(path)
    entries_raw = payload.get('entries') if isinstance(payload, dict) else None
    entries = [entry for entry in entries_raw if isinstance(entry, dict)] if isinstance(entries_raw, list) else []
    latest = entries[-1] if entries else None
    previous = entries[-2] if len(entries) > 1 else None
    latest_bundle_summary = Path(str(latest.get('bundle_summary_path'))).expanduser() if isinstance(latest, dict) and isinstance(latest.get('bundle_summary_path'), str) and latest.get('bundle_summary_path') else None
    latest_summary_markdown = Path(str(latest.get('summary_markdown_path'))).expanduser() if isinstance(latest, dict) and isinstance(latest.get('summary_markdown_path'), str) and latest.get('summary_markdown_path') else None
    return {
        'path': str(path),
        'exists': path.exists(),
        'capture_count': len(entries),
        'updated_at': payload.get('updated_at') if isinstance(payload, dict) else None,
        'latest_capture': latest,
        'previous_capture': previous,
        'latest_bundle_summary_exists': bool(latest_bundle_summary and latest_bundle_summary.exists()),
        'latest_summary_markdown_exists': bool(latest_summary_markdown and latest_summary_markdown.exists()),
        'history': payload,
    }


def _saved_launch_metadata(profile: Path) -> dict[str, Any] | None:
    data = _read_json(metadata_path(profile))
    return data if isinstance(data, dict) else None


def build_reopen_launch_plan(
    profile: Path,
    *,
    remote_debugging_override: str | None = None,
    chromium_bin_override: str | None = None,
    append_args: Iterable[str] = (),
    allow_discovered_browser_fallback: bool = False,
) -> dict[str, Any]:
    last_launch = _saved_launch_metadata(profile)
    plan: dict[str, Any] = {
        'profile': str(profile),
        'profile_name': profile.name,
        'metadata_path': str(metadata_path(profile)),
        'metadata_exists': metadata_path(profile).exists(),
        'ok': False,
        'launchable_now': False,
        'remote_debugging_override': remote_debugging_override,
        'append_args': list(append_args),
        'allow_discovered_browser_fallback': allow_discovered_browser_fallback,
        'portable_reopen_command': _portable_reopen_command(profile.name),
        'portable_reopen_debug_command': _portable_reopen_command(profile.name, remote_debugging='auto'),
    }
    if not isinstance(last_launch, dict):
        plan['error'] = 'profile does not have readable launch metadata yet'
        return plan
    extra_args_raw = last_launch.get('extra_args')
    if not isinstance(extra_args_raw, list) or not all(isinstance(value, str) for value in extra_args_raw):
        plan['error'] = 'saved launch metadata does not contain a valid extra_args list'
        return plan
    remote_debugging = last_launch.get('remote_debugging') if isinstance(last_launch.get('remote_debugging'), dict) else {}
    effective_remote_debugging = remote_debugging_override
    if effective_remote_debugging is None:
        if remote_debugging.get('requested'):
            effective_remote_debugging = _remote_debugging_value(remote_debugging.get('mode'), remote_debugging.get('port'))
        else:
            effective_remote_debugging = 'off'
    override_normalized = str(effective_remote_debugging).strip() if effective_remote_debugging is not None else 'off'
    if override_normalized not in {'off', 'auto'} and not override_normalized.isdigit():
        plan['error'] = f'invalid remote debugging override: {effective_remote_debugging!r}'
        return plan

    launch_args = [profile.name]
    if not bool(last_launch.get('extension_loaded', True)):
        launch_args.append('--skip-extension')
    if override_normalized != 'off':
        launch_args.extend(['--remote-debugging-port', override_normalized])
    launch_args.extend(extra_args_raw)
    launch_args.extend(str(value) for value in append_args)

    saved_browser = _browser_choice_for_path(last_launch.get('chromium_bin'), source='saved-launch')
    discovered_browser = discover_browser_executable()
    effective_browser = _browser_choice_for_path(chromium_bin_override, source='override') if chromium_bin_override else saved_browser
    used_discovered_browser_fallback = False
    warnings: list[str] = []
    if chromium_bin_override and not effective_browser:
        warnings.append('explicit chromium override was empty after normalization')
    if not chromium_bin_override and saved_browser and not saved_browser.get('exists'):
        warnings.append('saved browser path no longer exists on this machine')
        if allow_discovered_browser_fallback and isinstance(discovered_browser, dict) and discovered_browser.get('exists'):
            effective_browser = discovered_browser
            used_discovered_browser_fallback = True

    env_overrides: dict[str, str] = {}
    effective_browser_path = (effective_browser or {}).get('path') if isinstance(effective_browser, dict) else None
    if isinstance(effective_browser_path, str) and effective_browser_path.strip():
        env_overrides['CHROMIUM_BIN'] = effective_browser_path.strip()
    elif isinstance(last_launch.get('chromium_bin'), str) and str(last_launch.get('chromium_bin')).strip():
        env_overrides['CHROMIUM_BIN'] = str(last_launch.get('chromium_bin')).strip()

    shell_parts = []
    if env_overrides.get('CHROMIUM_BIN'):
        shell_parts.append(f"CHROMIUM_BIN={shlex.quote(env_overrides['CHROMIUM_BIN'])}")
    shell_parts.append(shlex.join(['./scripts/launch-chromium-profile.sh', *launch_args]))

    effective_browser_native_host = _native_host_recommendation(effective_browser if isinstance(effective_browser, dict) else None)
    saved_browser_native_host = _native_host_recommendation(saved_browser if isinstance(saved_browser, dict) else None)
    launchable_now = bool(env_overrides.get('CHROMIUM_BIN'))
    if isinstance(effective_browser, dict):
        launchable_now = launchable_now and bool(effective_browser.get('exists'))
    if not env_overrides.get('CHROMIUM_BIN') and isinstance(discovered_browser, dict) and discovered_browser.get('exists'):
        warnings.append('relaunch would currently depend on launch-chromium-profile.sh browser discovery instead of a recorded browser path')
    if not launchable_now:
        if isinstance(saved_browser, dict) and not saved_browser.get('exists'):
            plan['error'] = 'saved browser path is missing; reopen with --chromium-bin PATH or --allow-discovered-browser-fallback'
        else:
            plan['error'] = 'no runnable browser path is available for this relaunch plan yet'

    plan.update(
        {
            'ok': True,
            'launchable_now': launchable_now,
            'last_launch': last_launch,
            'saved_browser': saved_browser,
            'discovered_browser': discovered_browser,
            'effective_browser': effective_browser,
            'used_discovered_browser_fallback': used_discovered_browser_fallback,
            'saved_browser_native_host': saved_browser_native_host,
            'effective_browser_native_host': effective_browser_native_host,
            'remote_debugging_value': None if override_normalized == 'off' else override_normalized,
            'replayed_extra_args': list(extra_args_raw),
            'argv': ['./scripts/launch-chromium-profile.sh', *launch_args],
            'env_overrides': env_overrides,
            'shell_command': ' '.join(shell_parts),
            'warnings': warnings,
        }
    )
    return plan


def build_profile_commands(profile: Path) -> dict[str, str]:
    name = profile.name
    output = f'validation/latest/mv3-worker-resume-{name}.json'
    reopen_plan = build_reopen_launch_plan(profile)
    reopen_debug_plan = build_reopen_launch_plan(profile, remote_debugging_override='auto')
    reopen = reopen_plan.get('shell_command') if reopen_plan.get('ok') else f'./scripts/glasstty-profile.sh open {name} chrome://extensions/'
    reopen_debug = reopen_debug_plan.get('shell_command') if reopen_debug_plan.get('ok') else f'./scripts/glasstty-profile.sh open {name} --remote-debugging-port auto chrome://extensions/'
    return {
        'open_extensions': f'./scripts/glasstty-profile.sh open {name} chrome://extensions/',
        'open_debug': f'./scripts/glasstty-profile.sh open {name} --remote-debugging-port auto chrome://extensions/',
        'reopen': str(reopen),
        'reopen_debug': str(reopen_debug),
        'reopen_portable': _portable_reopen_command(name),
        'reopen_debug_portable': _portable_reopen_command(name, remote_debugging='auto'),
        'info': f'./scripts/glasstty-profile.sh info {name} --pretty',
        'captures': f'./scripts/glasstty-profile.sh captures {name} --pretty',
        'capture': f'./scripts/glasstty-profile.sh capture {name} --output-dir validation/latest/profile-capture-{name}',
        'resume_proof': f'./scripts/glasstty-profile.sh resume-proof {name} --output {output} --timeout 25',
        'resume_proof_direct': f'python scripts/mv3-worker-resume.py --profile {name} --output {output} --timeout 25',
    }


def parse_devtools_active_port(profile: Path) -> dict[str, Any]:
    path = devtools_active_port_path(profile)
    info: dict[str, Any] = {'path': str(path), 'exists': path.exists(), 'last_modified': _path_timestamp(path)}
    if not path.exists():
        return info
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except Exception as exc:
        info['read_error'] = str(exc)
        return info
    if lines:
        info['port'] = lines[0].strip()
    if len(lines) > 1:
        info['browser_websocket_path'] = lines[1].strip()
    return info


def resolve_cdp_endpoint(profile: Path, *, host: str = '127.0.0.1') -> dict[str, Any]:
    last_launch = _saved_launch_metadata(profile) or {}
    devtools = parse_devtools_active_port(profile)
    commands = build_profile_commands(profile)
    capture_history = summarize_capture_history(profile)
    info: dict[str, Any] = {
        'host': host,
        'profile': str(profile),
        'profile_name': profile.name,
        'metadata_path': str(metadata_path(profile)),
        'metadata_exists': metadata_path(profile).exists(),
        'devtools_active_port': devtools,
        'last_launch': last_launch,
        'commands': commands,
        'capture_history_path': str(capture_history_path(profile)),
        'capture_history_exists': capture_history.get('exists'),
        'capture_history': capture_history,
        'ok': False,
        'attach_ready': False,
    }
    remote_debugging = last_launch.get('remote_debugging') if isinstance(last_launch, dict) else None
    if isinstance(remote_debugging, dict):
        info['remote_debugging_requested'] = bool(remote_debugging.get('requested'))
        info['requested_port'] = remote_debugging.get('port')
        info['requested_mode'] = remote_debugging.get('mode')
    else:
        info['remote_debugging_requested'] = False
    port_source = 'devtools_active_port' if devtools.get('port') not in (None, '') else 'launch_metadata'
    port = devtools.get('port') or info.get('requested_port')
    if port in (None, '', '0', 0):
        if info.get('requested_mode') == 'ephemeral':
            info['error'] = 'profile requested ephemeral remote debugging, but DevToolsActivePort does not expose a concrete port yet'
        else:
            info['error'] = 'profile does not expose a concrete remote-debugging port yet'
        if commands.get('reopen_debug'):
            info['reopen_debug_command'] = commands['reopen_debug']
        return info
    port_str = str(port).strip()
    if not port_str.isdigit():
        info['error'] = f'invalid DevTools port: {port_str!r}'
        return info
    info['port'] = port_str
    info['port_source'] = port_source
    info['http_endpoint'] = f'http://{host}:{port_str}'
    ws_path = devtools.get('browser_websocket_path')
    info['websocket_endpoint'] = f"ws://{host}:{port_str}{ws_path if isinstance(ws_path, str) and ws_path.startswith('/') else '/' + ws_path}" if isinstance(ws_path, str) and ws_path else None
    info['preferred_endpoint'] = str(info['http_endpoint'])
    tcp_probe = _probe_tcp_endpoint(host, port_str)
    info['tcp_probe'] = tcp_probe
    info['ok'] = True
    if tcp_probe.get('attempted'):
        info['attach_ready'] = bool(tcp_probe.get('ok'))
        if not info['attach_ready']:
            info['attach_warning'] = 'DevTools port is not accepting local TCP connections right now; the saved DevToolsActivePort may be stale or the browser may no longer be running.'
            if commands.get('reopen_debug'):
                info['reopen_debug_command'] = commands['reopen_debug']
    else:
        info['attach_ready'] = True
    return info


def write_mv3_resume_artifacts(profile: Path, report: dict[str, Any]) -> dict[str, Any]:
    profile.mkdir(parents=True, exist_ok=True)
    report_path = mv3_resume_report_path(profile)
    summary_path = mv3_resume_summary_path(profile)
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    resume_proof = report.get('resume_proof') if isinstance(report.get('resume_proof'), dict) else {}
    summary: dict[str, Any] = {
        'captured_at': utc_now_iso(),
        'profile': str(profile),
        'report_path': str(report_path),
        'ok': report.get('ok'),
        'phase': report.get('phase'),
        'error': report.get('error'),
        'attach_mode': report.get('attach_mode'),
        'cdp_endpoint': report.get('cdp_endpoint'),
        'extension_id': report.get('extension_id'),
        'proof_grade': resume_proof.get('proof_grade'),
        'boot_changed': resume_proof.get('boot_changed'),
        'boot_count_increased': resume_proof.get('boot_count_increased'),
        'native_recovered': resume_proof.get('native_recovered'),
        'context_evidence_available': resume_proof.get('context_evidence_available'),
        'report_output_path': report.get('output_path'),
    }
    summary_path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    return {'profile': str(profile), 'report_path': str(report_path), 'summary_path': str(summary_path), 'summary': summary}


def write_launch_metadata(profile: Path, *, profile_name: str, chromium_bin: str, extension_dir: str | None, extension_loaded: bool, extra_args: list[str], remote_debugging_mode: str | None, remote_debugging_port: str | None) -> dict[str, Any]:
    profile.mkdir(parents=True, exist_ok=True)
    payload = {
        'schema_version': 1,
        'profile_name': profile_name,
        'profile_dir': str(profile),
        'launched_at': utc_now_iso(),
        'chromium_bin': chromium_bin,
        'browser': _browser_choice_for_path(chromium_bin, source='recorded-launch'),
        'extension_dir': extension_dir,
        'extension_loaded': extension_loaded,
        'start_url': _first_non_flag_arg(extra_args),
        'extra_args': extra_args,
        'remote_debugging': {
            'requested': remote_debugging_mode is not None,
            'mode': remote_debugging_mode,
            'port': remote_debugging_port,
            'devtools_active_port_path': str(devtools_active_port_path(profile)),
        },
        'native_host_audit_path': str(native_host_audit_path(profile)),
    }
    metadata_path(profile).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    return payload


def summarize_profile(profile: Path) -> dict[str, Any]:
    native_host_path = native_host_audit_path(profile)
    resume_report_path = mv3_resume_report_path(profile)
    resume_summary_path = mv3_resume_summary_path(profile)
    capture_history = summarize_capture_history(profile)
    reopen_plan = build_reopen_launch_plan(profile)
    reopen_debug_plan = build_reopen_launch_plan(profile, remote_debugging_override='auto')
    commands = build_profile_commands(profile)
    info: dict[str, Any] = {
        'name': profile.name,
        'path': str(profile),
        'exists': profile.exists(),
        'metadata_path': str(metadata_path(profile)),
        'metadata_exists': metadata_path(profile).exists(),
        'last_launch': _saved_launch_metadata(profile),
        'native_host_audit_path': str(native_host_path),
        'native_host_audit_exists': native_host_path.exists(),
        'native_host_audit': _read_json(native_host_path),
        'devtools_active_port': parse_devtools_active_port(profile),
        'cdp_endpoint_hint': resolve_cdp_endpoint(profile),
        'reopen_plan': reopen_plan,
        'reopen_debug_plan': reopen_debug_plan,
        'commands': commands,
        'capture_history_path': str(capture_history_path(profile)),
        'capture_history_exists': capture_history.get('exists'),
        'capture_history': capture_history,
        'mv3_resume_report_path': str(resume_report_path),
        'mv3_resume_report_exists': resume_report_path.exists(),
        'mv3_resume_summary_path': str(resume_summary_path),
        'mv3_resume_summary_exists': resume_summary_path.exists(),
        'mv3_resume_summary': _read_json(resume_summary_path),
    }
    if profile.exists():
        stat = profile.stat()
        info['last_modified'] = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    return info



def triage_profile(profile: Path, summary: dict[str, Any] | None = None) -> dict[str, Any]:
    summary = summary or summarize_profile(profile)
    commands = summary.get('commands') if isinstance(summary.get('commands'), dict) else {}
    cdp_hint = summary.get('cdp_endpoint_hint') if isinstance(summary.get('cdp_endpoint_hint'), dict) else {}
    reopen_plan = summary.get('reopen_plan') if isinstance(summary.get('reopen_plan'), dict) else {}
    reopen_debug_plan = summary.get('reopen_debug_plan') if isinstance(summary.get('reopen_debug_plan'), dict) else {}
    portable_reopen_plan = build_reopen_launch_plan(profile, allow_discovered_browser_fallback=True)
    portable_reopen_debug_plan = build_reopen_launch_plan(profile, remote_debugging_override='auto', allow_discovered_browser_fallback=True)
    capture_history = summary.get('capture_history') if isinstance(summary.get('capture_history'), dict) else {}
    resume_summary = summary.get('mv3_resume_summary') if isinstance(summary.get('mv3_resume_summary'), dict) else {}
    reasons: list[str] = []
    warnings: list[str] = []
    tier = 'cold'
    score = 0
    next_command = commands.get('open_debug')
    next_step = 'open a managed debug profile from scratch'

    if cdp_hint.get('attach_ready'):
        tier = 'attach-ready'
        score = 100
        next_command = commands.get('resume_proof') or commands.get('capture') or commands.get('info')
        next_step = 'capture a fresh MV3 restart-proof run against the live managed profile'
        reasons.append(f"CDP endpoint is attach-ready at {cdp_hint.get('preferred_endpoint')}")
    elif portable_reopen_debug_plan.get('launchable_now'):
        tier = 'portable-reopen'
        score = 82
        next_command = commands.get('reopen_debug_portable')
        next_step = 'reopen the saved profile with an explicit discovered-browser fallback'
        reasons.append('saved launch metadata exists and GlassTTY can replay it with a discovered browser fallback')
        if portable_reopen_debug_plan.get('used_discovered_browser_fallback'):
            warnings.append('this replay depends on a newly discovered browser, not the originally recorded browser path')
    elif reopen_debug_plan.get('launchable_now'):
        tier = 'reopen-debug'
        score = 80
        next_command = commands.get('reopen_debug')
        next_step = 'reopen the saved profile with remote debugging enabled'
        reasons.append('saved launch metadata exists and the recorded browser path is still runnable')
    elif reopen_plan.get('launchable_now'):
        tier = 'reopen'
        score = 72
        next_command = commands.get('reopen')
        next_step = 'reopen the saved profile using the recorded launch recipe'
        reasons.append('saved launch metadata exists and the profile can be replayed now')
    elif summary.get('metadata_exists'):
        tier = 'metadata-only'
        score = 55
        next_command = commands.get('open_debug')
        next_step = 'recreate the managed profile using a fresh debug launch'
        reasons.append('saved launch metadata exists, but the previous launch recipe is not currently runnable')
    elif summary.get('exists'):
        tier = 'fresh-open'
        score = 40
        next_command = commands.get('open_debug')
        next_step = 'open the managed profile with remote debugging from scratch'
        reasons.append('profile directory exists but has no reusable launch metadata yet')

    if cdp_hint.get('ok') and not cdp_hint.get('attach_ready'):
        warnings.append(cdp_hint.get('attach_warning') or 'saved DevToolsActivePort is not attach-ready right now')
    if isinstance(reopen_debug_plan.get('error'), str):
        warnings.append(reopen_debug_plan['error'])
    for plan in (reopen_plan, reopen_debug_plan, portable_reopen_plan, portable_reopen_debug_plan):
        extra_warnings = plan.get('warnings') if isinstance(plan, dict) else None
        if isinstance(extra_warnings, list):
            warnings.extend(str(value) for value in extra_warnings if isinstance(value, str))

    capture_count = int(capture_history.get('capture_count') or 0) if isinstance(capture_history, dict) else 0
    if capture_count:
        score += min(capture_count, 3)
        reasons.append(f'{capture_count} saved durable capture bundle(s) already exist for comparison')
    proof_grade = resume_summary.get('proof_grade') if isinstance(resume_summary, dict) else None
    if proof_grade:
        score += 4
        reasons.append(f'saved MV3 restart evidence already exists ({proof_grade})')

    unique_warnings: list[str] = []
    for warning in warnings:
        normalized = str(warning).strip()
        if normalized and normalized not in unique_warnings:
            unique_warnings.append(normalized)

    cdp_endpoint = cdp_hint.get('preferred_endpoint') if isinstance(cdp_hint, dict) else None
    return {
        'name': summary.get('name') or profile.name,
        'path': summary.get('path') or str(profile),
        'tier': tier,
        'score': score,
        'next_step': next_step,
        'next_command': next_command,
        'followup_capture_command': commands.get('capture'),
        'history_command': commands.get('captures'),
        'resume_proof_command': commands.get('resume_proof'),
        'reasons': reasons,
        'warnings': unique_warnings,
        'attach_ready': bool(cdp_hint.get('attach_ready')),
        'cdp_endpoint': cdp_endpoint,
        'capture_count': capture_count,
        'has_saved_resume': bool(proof_grade),
        'proof_grade': proof_grade,
        'strict_reopen_launchable': bool(reopen_debug_plan.get('launchable_now')),
        'portable_reopen_launchable': bool(portable_reopen_debug_plan.get('launchable_now')),
        'used_discovered_browser_fallback': bool(portable_reopen_debug_plan.get('used_discovered_browser_fallback')),
        'metadata_exists': bool(summary.get('metadata_exists')),
    }


def triage_profiles(home: Path | None = None) -> dict[str, Any]:
    root = profiles_root(home)
    profiles = sorted([summarize_profile(path) for path in root.iterdir() if path.is_dir()], key=lambda item: item['name']) if root.exists() else []
    ranked = sorted((triage_profile(profile_dir(item['name'], home), item) for item in profiles), key=lambda item: (-int(item.get('score', 0)), str(item.get('name', ''))))
    best = ranked[0] if ranked else None
    return {
        'root': str(root),
        'exists': root.exists(),
        'profile_count': len(profiles),
        'ranked_profiles': ranked,
        'best_profile': best,
        'commands': {
            'triage': './scripts/glasstty-profile.sh triage --pretty',
            'doctor': './scripts/doctor.py --pretty',
            'fleet_capture': './scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture',
            'fleet_captures': './scripts/glasstty-profile.sh fleet-captures --pretty',
        },
    }


def summarize_profiles(home: Path | None = None) -> dict[str, Any]:
    root = profiles_root(home)
    profiles = sorted([summarize_profile(path) for path in root.iterdir() if path.is_dir()], key=lambda item: item['name']) if root.exists() else []
    triage = triage_profiles(home)
    return {
        'root': str(root),
        'exists': root.exists(),
        'profiles': profiles,
        'triage': triage,
        'fleet_capture_history': summarize_fleet_capture_history(home),
        'commands': {
            'triage': './scripts/glasstty-profile.sh triage --pretty',
            'fleet_capture': './scripts/glasstty-profile.sh fleet-capture --output-dir validation/latest/profile-fleet-capture',
            'fleet_captures': './scripts/glasstty-profile.sh fleet-captures --pretty',
        },
    }
