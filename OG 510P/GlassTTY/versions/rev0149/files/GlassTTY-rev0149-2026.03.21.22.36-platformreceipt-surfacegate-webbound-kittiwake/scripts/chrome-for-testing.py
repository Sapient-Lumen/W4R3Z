#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from browser_binaries import (
    ChromeForTestingError,
    cft_root,
    detect_cft_platform,
    discover_browser_executable,
    fetch_cft_catalog,
    fetch_cft_version_manifest,
    install_cft_asset,
    latest_local_cft_install,
    local_cft_installations,
    resolve_cft_channel_asset,
    resolve_cft_version_asset,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Inspect or install Chrome for Testing assets for GlassTTY labs.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    inspect_parser = subparsers.add_parser('inspect', help='Show local Chrome for Testing state and default GlassTTY browser resolution.')
    inspect_parser.add_argument('--binary', default='chrome', choices=['chrome', 'chromedriver', 'chrome-headless-shell'])
    inspect_parser.add_argument('--platform', default='auto')
    inspect_parser.add_argument('--root')
    inspect_parser.add_argument('--pretty', action='store_true')

    local_exec_parser = subparsers.add_parser('local-executable', help='Print the latest locally installed Chrome for Testing browser executable path.')
    local_exec_parser.add_argument('--root')
    local_exec_parser.add_argument('--platform', default='auto')

    resolve_parser = subparsers.add_parser('resolve', help='Resolve a Chrome for Testing download asset via the official JSON APIs.')
    resolve_parser.add_argument('--channel', default='stable')
    resolve_parser.add_argument('--version')
    resolve_parser.add_argument('--binary', default='chrome', choices=['chrome', 'chromedriver', 'chrome-headless-shell'])
    resolve_parser.add_argument('--platform', default='auto')
    resolve_parser.add_argument('--catalog-url')
    resolve_parser.add_argument('--pretty', action='store_true')

    install_parser = subparsers.add_parser('install', help='Download and install a Chrome for Testing asset into the GlassTTY browser cache.')
    install_parser.add_argument('--channel', default='stable')
    install_parser.add_argument('--version')
    install_parser.add_argument('--binary', default='chrome', choices=['chrome', 'chromedriver', 'chrome-headless-shell'])
    install_parser.add_argument('--platform', default='auto')
    install_parser.add_argument('--catalog-url')
    install_parser.add_argument('--root')
    install_parser.add_argument('--archive-path')
    install_parser.add_argument('--force', action='store_true')
    install_parser.add_argument('--pretty', action='store_true')

    return parser


def resolved_platform(value: str) -> str:
    return detect_cft_platform() if value == 'auto' else value


def resolve_asset(args: argparse.Namespace) -> dict[str, Any]:
    platform = resolved_platform(args.platform)
    if getattr(args, 'version', None):
        manifest = fetch_cft_version_manifest(args.version)
        return resolve_cft_version_asset(manifest, binary=args.binary, platform=platform)
    catalog = fetch_cft_catalog(url=args.catalog_url) if getattr(args, 'catalog_url', None) else fetch_cft_catalog()
    return resolve_cft_channel_asset(catalog, channel=args.channel, binary=args.binary, platform=platform)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == 'inspect':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else cft_root()
            report = {
                'root': str(root),
                'binary': args.binary,
                'platform': platform,
                'local_installations': local_cft_installations(binary=args.binary, platform=platform, root=root),
                'latest_local_install': latest_local_cft_install(binary=args.binary, platform=platform, root=root),
                'default_browser': discover_browser_executable(),
            }
            print(json.dumps(report, indent=2 if args.pretty else None))
            return
        if args.command == 'local-executable':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else cft_root()
            install = latest_local_cft_install(binary='chrome', platform=platform, root=root)
            if not install:
                raise SystemExit(1)
            print(install['executable'])
            return
        if args.command == 'resolve':
            asset = resolve_asset(args)
            print(json.dumps(asset, indent=2 if args.pretty else None))
            return
        if args.command == 'install':
            root = Path(args.root).expanduser() if args.root else cft_root()
            if args.archive_path:
                platform = resolved_platform(args.platform)
                version = args.version or 'offline'
                asset = {
                    'source': 'local-archive',
                    'version': version,
                    'revision': None,
                    'binary': args.binary,
                    'platform': platform,
                    'url': Path(args.archive_path).expanduser().resolve().as_uri(),
                }
            else:
                asset = resolve_asset(args)
            result = install_cft_asset(asset=asset, root=root, force=args.force)
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
    except ChromeForTestingError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == '__main__':
    main()
