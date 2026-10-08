#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from profile_metadata import profile_dir, summarize_profile, summarize_profiles, triage_profiles, write_launch_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect GlassTTY Chromium profile metadata and optional DevTools port state')
    parser.add_argument('--profile', help='Inspect a single profile by name instead of listing all profiles')
    parser.add_argument('--pretty', action='store_true')

    sub = parser.add_subparsers(dest='command')
    record = sub.add_parser('record-launch', help='Internal helper: record launch metadata for a profile')
    record.add_argument('--profile-dir', required=True)
    record.add_argument('--profile-name', required=True)
    record.add_argument('--chromium-bin', required=True)
    record.add_argument('--extension-dir')
    record.add_argument('--extension-loaded', action='store_true')
    record.add_argument('--remote-debugging-mode', choices=['fixed', 'ephemeral'])
    record.add_argument('--remote-debugging-port')
    record.add_argument('--arg', action='append', default=[])
    record.add_argument('--pretty', action='store_true')
    triage = sub.add_parser('triage', help='Rank saved managed profiles by the best next operator action')
    triage.add_argument('--pretty', action='store_true')

    args = parser.parse_args()
    if args.command == 'record-launch':
        payload = write_launch_metadata(
            Path(args.profile_dir),
            profile_name=args.profile_name,
            chromium_bin=args.chromium_bin,
            extension_dir=args.extension_dir,
            extension_loaded=args.extension_loaded,
            extra_args=list(args.arg),
            remote_debugging_mode=args.remote_debugging_mode,
            remote_debugging_port=args.remote_debugging_port,
        )
    elif args.command == 'triage':
        payload = triage_profiles()
    elif args.profile:
        payload = summarize_profile(profile_dir(args.profile))
    else:
        payload = summarize_profiles()

    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
