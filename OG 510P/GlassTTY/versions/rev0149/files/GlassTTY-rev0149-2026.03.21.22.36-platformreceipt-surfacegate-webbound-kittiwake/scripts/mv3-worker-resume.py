#!/usr/bin/env python3
from __future__ import annotations

import argparse
import atexit
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent
for candidate in (str(SCRIPT_DIR), str(ROOT), str(ROOT / 'daemon' / 'src')):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from e2e_fixturelab import (  # type: ignore
    DEFAULT_WRITE_TEXT,
    DOCTOR_SCRIPT,
    EXTENSION_DIR,
    INSTALL_NATIVE_HOST,
    PLAYWRIGHT_IMPORT_ERROR,
    WRAPPER_PATH,
    append_step,
    browser_env,
    checkpoint_report,
    discover_browser_executable,
    discover_playwright_browser_install,
    extension_dist_ready,
    install_termination_checkpoint,
    playwright_browser_choice,
    attach_playwright_extension_context,
    launch_playwright_extension_context,
    make_tree_writable,
    native_host_install_targets,
    open_probe_page,
    playwright_extension_launch_plan,
    run,
    stop_extension_service_worker_playwright,
    sync_playwright,
    utc_now,
    worker_resume_summary,
)
from playwright_browsers import PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV
from profile_metadata import profile_dir as managed_profile_dir, resolve_cdp_endpoint, write_mv3_resume_artifacts

EXTENSION_ID_SCRIPT = ROOT / 'scripts' / 'extension-id.py'


def main() -> None:
    parser = argparse.ArgumentParser(description='Launch GlassTTY in a disposable Chromium profile, terminate the MV3 service worker, and capture a before/after resume proof bundle.')
    parser.add_argument('--output', required=True)
    parser.add_argument('--timeout', type=float, default=25.0)
    parser.add_argument('--write-text', default=DEFAULT_WRITE_TEXT)
    parser.add_argument('--extension-id', default='auto', help='Extension id to use. Defaults to computing it from extension/manifest.json instead of running doctor.')
    parser.add_argument('--include-doctor', action='store_true', help='Also capture scripts/doctor.py output before launch.')
    parser.add_argument('--cdp-endpoint', help='Attach to an already-running Chromium instance over CDP instead of launching a fresh temporary browser context.')
    parser.add_argument('--profile', help='Attach through a GlassTTY-managed profile name by reading its launch metadata and DevToolsActivePort file.')
    parser.add_argument('--profile-dir', help='Attach through a specific Chromium profile directory instead of resolving a managed profile name.')
    parser.add_argument('--profile-host', default='127.0.0.1', help='Host to use when constructing a CDP endpoint from profile metadata (default: 127.0.0.1).')
    parser.add_argument('--trace', action='store_true', help='Capture a Playwright trace in the temp workspace.')
    args = parser.parse_args()

    if args.cdp_endpoint and (args.profile or args.profile_dir):
        raise SystemExit('--cdp-endpoint cannot be combined with --profile or --profile-dir')
    if args.profile and args.profile_dir:
        raise SystemExit('--profile and --profile-dir are mutually exclusive')

    output_path = Path(args.output).resolve()
    report: dict[str, Any] = {
        'ok': False,
        'timestamp': utc_now(),
        'output_path': str(output_path),
        'steps': [],
        'events': [],
        'playwright': {'available': sync_playwright is not None, 'import_error': PLAYWRIGHT_IMPORT_ERROR},
        'resume_proof': {},
    }

    profile_artifact_dir: Path | None = None
    if args.profile_dir:
        profile_artifact_dir = Path(args.profile_dir).resolve()
        report['profile_attach'] = {'source': 'profile-dir', 'profile_dir': str(profile_artifact_dir)}
    elif args.profile:
        profile_artifact_dir = managed_profile_dir(args.profile).resolve()
        report['profile_attach'] = {'source': 'managed-profile', 'profile_name': args.profile, 'profile_dir': str(profile_artifact_dir)}
    if profile_artifact_dir is not None:
        resolved_profile_attach = resolve_cdp_endpoint(profile_artifact_dir, host=args.profile_host)
        report['profile_attach'] = {**(report.get('profile_attach') or {}), **resolved_profile_attach}
        if not resolved_profile_attach.get('ok'):
            checkpoint_report(report, output_path, phase='profile_attach_failed', note=str(resolved_profile_attach.get('error') or 'profile attach could not derive a CDP endpoint'))
            raise SystemExit(str(resolved_profile_attach.get('error') or 'profile attach could not derive a CDP endpoint'))
        args.cdp_endpoint = str(resolved_profile_attach.get('preferred_endpoint'))
        report['cdp_endpoint'] = args.cdp_endpoint

    atexit_state = {'enabled': True}

    def _atexit_checkpoint() -> None:
        if not atexit_state['enabled']:
            return
        try:
            checkpoint_report(report, output_path, phase=str(report.get('phase') or 'exiting'), note='atexit checkpoint', event={'kind': 'atexit'})
        except Exception:
            pass

    atexit.register(_atexit_checkpoint)
    restore_signal_handlers, _ = install_termination_checkpoint(report, output_path)
    checkpoint_report(report, output_path, phase='starting', note='initialized resume-proof report')

    temp_root = Path(tempfile.mkdtemp(prefix='glasstty-mv3-resume-'))
    report['temp_root'] = str(temp_root)
    temp_home = temp_root / 'home'
    temp_home.mkdir(parents=True, exist_ok=True)
    env = browser_env(temp_home)
    playwright_dry_run_timeout = max(1.0, min(4.0, args.timeout / 8.0))
    env.setdefault(PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV, f'{playwright_dry_run_timeout:.1f}')
    report['browser_env'] = {key: env[key] for key in ('HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME', 'XDG_RUNTIME_DIR', 'CHROME_CONFIG_HOME', 'GLASSTTY_HOME', 'PLAYWRIGHT_BROWSERS_PATH', PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV) if key in env}
    report['attach_mode'] = bool(args.cdp_endpoint)
    if args.cdp_endpoint:
        report['cdp_endpoint'] = args.cdp_endpoint
    checkpoint_report(report, output_path, phase='environment_ready', note='temporary browser environment prepared')

    cleanup: Callable[[], None] | None = None
    context = None
    initial_page = None
    resumed_page = None

    try:
        if args.include_doctor:
            report['doctor'] = json.loads(run([sys.executable, str(DOCTOR_SCRIPT)], env=env).stdout)
            append_step(report, 'doctor')
        if not args.cdp_endpoint:
            report['browser_choice'] = discover_browser_executable(env=env)
            report['playwright']['browser_install'] = discover_playwright_browser_install(
                env=env,
                playwright_available=sync_playwright is not None,
                import_error=PLAYWRIGHT_IMPORT_ERROR,
                dry_run_timeout=float(env.get(PLAYWRIGHT_DRY_RUN_TIMEOUT_ENV) or playwright_dry_run_timeout),
            )
            report['playwright']['launch_plan'] = playwright_extension_launch_plan(env=env, browser_install=report['playwright']['browser_install'])
            report['playwright']['browser_choice'] = playwright_browser_choice(report['playwright']['browser_install'], launch_plan=report['playwright']['launch_plan'])
        else:
            report['browser_choice'] = {'mode': 'attached-cdp', 'native_messaging_targets': []}
            report['playwright']['attach_plan'] = {'strategy': 'cdp-attach', 'supported': False, 'notes': ['CDP attach mode expects an already-running Chromium instance with GlassTTY loaded.', 'This path avoids fresh browser startup and is intended for constrained environments or manual proof runs.']}
        if args.extension_id == 'auto':
            report['extension_id_source'] = 'manifest.key'
            extension_id = run([sys.executable, str(EXTENSION_ID_SCRIPT), str(EXTENSION_DIR / 'manifest.json')], env=env).stdout.strip()
        else:
            report['extension_id_source'] = 'explicit'
            extension_id = args.extension_id.strip()
        if not extension_id:
            raise RuntimeError('failed to resolve extension id')
        report['extension_id'] = extension_id
        checkpoint_report(report, output_path, phase='discovery_complete', note='browser discovery and extension id resolved')

        make_tree_writable(EXTENSION_DIR / 'dist')
        try:
            run(['npm', 'run', 'build'], cwd=EXTENSION_DIR, env=env)
            report['extension_build'] = {'ok': True, 'fallback_used': False}
            append_step(report, 'extension_build')
        except Exception as exc:  # noqa: BLE001
            if extension_dist_ready(EXTENSION_DIR):
                report['extension_build'] = {'ok': True, 'fallback_used': True, 'warning': str(exc)}
                append_step(report, 'extension_build_fallback_ready')
            else:
                raise
        checkpoint_report(report, output_path, phase='extension_ready', note='extension bundle ready for resume proof')

        trace_path = temp_root / 'resume-proof-trace.zip' if args.trace else None
        if args.cdp_endpoint:
            report['native_host_install'] = {'skipped': True, 'reason': 'attached browser is expected to already have native-host manifests installed'}
            checkpoint_report(report, output_path, phase='native_host_ready', note='native host install skipped in CDP attach mode')
            context, launch_report, cleanup = attach_playwright_extension_context(
                cdp_endpoint=args.cdp_endpoint,
                expected_extension_id=str(extension_id),
                timeout=args.timeout,
                trace_path=trace_path,
            )
            report['playwright']['launch_report'] = launch_report
            append_step(report, 'playwright_attach')
            checkpoint_report(report, output_path, phase='browser_ready', note='attached Playwright Chromium context is ready')
        else:
            for helper_script in (WRAPPER_PATH, INSTALL_NATIVE_HOST):
                if helper_script.exists():
                    try:
                        helper_script.chmod(0o755)
                    except PermissionError:
                        pass
            install_targets = native_host_install_targets(report['browser_choice'], report['playwright'].get('browser_choice') if isinstance(report.get('playwright'), dict) else None)
            native_host_installs: list[dict[str, Any]] = []
            for target_name in install_targets:
                install = run([str(INSTALL_NATIVE_HOST), '--target', target_name, '--extension-id', 'auto', '--host-exe', str(WRAPPER_PATH)], env=env)
                native_host_installs.append({'target': target_name, 'stdout': install.stdout.strip()})
                append_step(report, f'native_host_install_{target_name}')
            report['native_host_install_targets'] = install_targets
            report['native_host_install'] = native_host_installs
            checkpoint_report(report, output_path, phase='native_host_ready', note='native host manifests installed into temp browser config')

            profile_dir = temp_root / 'profile'
            profile_dir.mkdir(parents=True, exist_ok=True)
            context, launch_report, cleanup = launch_playwright_extension_context(
                env=env,
                extension_dir=EXTENSION_DIR,
                profile_dir=profile_dir,
                expected_extension_id=str(extension_id),
                timeout=args.timeout,
                trace_path=trace_path,
                browser_install=report['playwright']['browser_install'],
                launch_plan=report['playwright']['launch_plan'],
            )
            report['playwright']['launch_report'] = launch_report
            append_step(report, 'playwright_launch')
            checkpoint_report(report, output_path, phase='browser_ready', note='persistent Playwright Chromium context is ready')

        initial_page, initial_dom, initial_probe, initial_console = open_probe_page(
            context,
            extension_id=str(launch_report.get('observed_extension_id') or extension_id),
            timeout=args.timeout,
            fixture_url=None,
            write_text=args.write_text,
            screenshot_path=temp_root / 'probe-before.png',
        )
        report['probe_before'] = {
            'dom': initial_dom,
            'probe_json': initial_probe,
            'console_messages': initial_console,
            'page_url': initial_page.url,
        }
        append_step(report, 'probe_before')
        checkpoint_report(report, output_path, phase='probe_before_ready', note='initial probe captured before worker termination')

        termination = stop_extension_service_worker_playwright(context.browser, extension_id=str(extension_id), timeout=min(3.0, args.timeout))
        report['service_worker_termination'] = termination
        append_step(report, 'service_worker_termination')
        if not termination.get('closed'):
            raise RuntimeError(termination.get('error') or 'failed to close extension service worker target via CDP')
        checkpoint_report(report, output_path, phase='service_worker_terminated', note='service worker terminated through browser CDP')

        resumed_page, resumed_dom, resumed_probe, resumed_console = open_probe_page(
            context,
            extension_id=str(launch_report.get('observed_extension_id') or extension_id),
            timeout=args.timeout,
            fixture_url=None,
            write_text=args.write_text,
            screenshot_path=temp_root / 'probe-after.png',
        )
        report['probe_after'] = {
            'dom': resumed_dom,
            'probe_json': resumed_probe,
            'console_messages': resumed_console,
            'page_url': resumed_page.url,
        }
        append_step(report, 'probe_after')
        checkpoint_report(report, output_path, phase='probe_after_ready', note='post-termination probe captured')

        resume_summary = worker_resume_summary(initial_probe, resumed_probe)
        report['resume_proof'] = resume_summary
        report['ok'] = bool(resume_summary.get('ok'))
        report['phase'] = 'completed'
        checkpoint_report(report, output_path, phase='completed', note='resume proof summary computed')
        if not report['ok']:
            raise RuntimeError(f"resume proof did not confirm worker recovery: {json.dumps(resume_summary, sort_keys=True)}")
    except Exception as exc:  # noqa: BLE001
        report['error'] = str(exc)
        report['ok'] = False
        checkpoint_report(report, output_path, phase='failed', note=str(exc), event={'kind': 'error', 'error': str(exc)})
        raise
    finally:
        if initial_page is not None:
            try:
                initial_page.close()
            except Exception:
                pass
        if resumed_page is not None:
            try:
                resumed_page.close()
            except Exception:
                pass
        if cleanup is not None:
            cleanup()
        if temp_root.exists():
            report['retained_temp_root'] = str(temp_root)
            checkpoint_report(report, output_path, phase=str(report.get('phase') or 'finished'), note='retained temp workspace for inspection')
        if profile_artifact_dir is not None:
            try:
                persisted = write_mv3_resume_artifacts(profile_artifact_dir, report)
                report['profile_artifacts'] = persisted
                checkpoint_report(report, output_path, phase=str(report.get('phase') or 'finished'), note='wrote profile-scoped resume artifacts')
            except Exception as exc:  # noqa: BLE001
                report['profile_artifacts_error'] = str(exc)
                checkpoint_report(report, output_path, phase=str(report.get('phase') or 'finished'), note=f'failed to write profile-scoped resume artifacts: {exc}')
        restore_signal_handlers()
        atexit_state['enabled'] = False


if __name__ == '__main__':
    main()
