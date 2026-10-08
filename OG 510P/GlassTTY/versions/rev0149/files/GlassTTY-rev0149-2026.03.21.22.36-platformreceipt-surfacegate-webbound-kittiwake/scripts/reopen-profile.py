#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from profile_metadata import build_reopen_launch_plan, profile_dir

SCRIPT_DIR = Path(__file__).resolve().parent
LAUNCH_SCRIPT = SCRIPT_DIR / 'launch-chromium-profile.sh'


def main() -> None:
    parser = argparse.ArgumentParser(description='Relaunch a GlassTTY-managed Chromium profile from saved launch metadata.')
    parser.add_argument('profile', help='GlassTTY profile name to relaunch from saved metadata')
    parser.add_argument('--remote-debugging-port', default=None, help='Override saved remote-debugging mode: auto, off, or a numeric port')
    parser.add_argument('--chromium-bin', help='Override the saved Chromium binary path for this relaunch')
    parser.add_argument('--allow-discovered-browser-fallback', action='store_true', help='If the saved browser path is missing, reuse the currently discovered browser executable explicitly instead of failing')
    parser.add_argument('--arg', action='append', default=[], help='Append an extra Chromium arg after the saved launch args (repeatable)')
    parser.add_argument('--dry-run', action='store_true', help='Print the relaunch plan instead of execing Chromium')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output in --dry-run mode')
    args = parser.parse_args()

    plan = build_reopen_launch_plan(
        profile_dir(args.profile),
        remote_debugging_override=args.remote_debugging_port,
        chromium_bin_override=args.chromium_bin,
        append_args=args.arg,
        allow_discovered_browser_fallback=args.allow_discovered_browser_fallback,
    )
    if not plan.get('ok'):
        raise SystemExit(str(plan.get('error') or 'failed to build profile relaunch plan'))

    if args.dry_run:
        print(json.dumps(plan, indent=2 if args.pretty else None))
        return

    if not plan.get('launchable_now'):
        message = str(plan.get('error') or 'profile relaunch plan is not launchable right now')
        portable = plan.get('portable_reopen_command')
        saved_native = plan.get('saved_browser_native_host') if isinstance(plan.get('saved_browser_native_host'), dict) else None
        if portable and not args.allow_discovered_browser_fallback:
            message += f'\nPortable fallback: {portable}'
        install_commands = list((saved_native or {}).get('install_commands') or [])
        if install_commands:
            message += f'\nSaved-browser native-host follow-up: {install_commands[0]}'
        raise SystemExit(message)

    env = os.environ.copy()
    for key, value in (plan.get('env_overrides') or {}).items():
        if isinstance(value, str) and value:
            env[key] = value
    argv = [str(LAUNCH_SCRIPT), *[str(value) for value in (plan.get('argv') or [])[1:]]]
    os.execvpe(str(LAUNCH_SCRIPT), argv, env)


if __name__ == '__main__':
    main()
