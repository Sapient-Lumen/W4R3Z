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

from browser_binaries import detect_cft_platform
from playwright_browsers import (
    PLAYWRIGHT_EXTENSION_PACKAGE,
    PlaywrightBrowserError,
    audit_playwright_cache,
    discover_playwright_browser_install,
    ensure_playwright_channel_ready,
    import_cft_into_playwright_cache,
    inspect_playwright_registry,
    install_playwright_browser_archive,
    latest_local_playwright_browser_install,
    local_playwright_browser_installations,
    plan_playwright_cache_repair,
    playwright_browsers_root,
    playwright_extension_launch_plan,
    playwright_install_dry_run,
    playwright_install_list,
    repair_playwright_cache,
    sync_playwright_browser_packages,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Inspect or seed the Playwright browser cache for GlassTTY labs.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    inspect_parser = subparsers.add_parser('inspect', help='Show local Playwright browser-cache state and extension-lane browser discovery.')
    inspect_parser.add_argument('--root')
    inspect_parser.add_argument('--platform', default='auto')
    inspect_parser.add_argument('--pretty', action='store_true')

    dry_run_parser = subparsers.add_parser('dry-run', help='Parse `python -m playwright install --dry-run chromium` into JSON.')
    dry_run_parser.add_argument('--pretty', action='store_true')

    list_parser = subparsers.add_parser('list', help='Run `python -m playwright install --list` with either raw or prepared GlassTTY cache state.')
    list_parser.add_argument('--root')
    list_parser.add_argument('--raw', action='store_true', help='Do not create or update the current Playwright .links registry entry before invoking install --list.')
    list_parser.add_argument('--pretty', action='store_true')

    audit_parser = subparsers.add_parser('audit', help='Compare on-disk Playwright browser installs with registry links and install --list visibility.')
    audit_parser.add_argument('--root')
    audit_parser.add_argument('--platform', default='auto')
    audit_parser.add_argument('--pretty', action='store_true')

    repair_parser = subparsers.add_parser('repair', help='Plan or apply safe Playwright cache repairs for shadow installs and broken registry links.')
    repair_parser.add_argument('--root')
    repair_parser.add_argument('--platform', default='auto')
    repair_parser.add_argument('--apply', action='store_true', help='Apply the selected cache repairs. Without this flag the command reports a dry-run plan only.')
    repair_parser.add_argument('--align-shadow-installs', action='store_true', help='Rename repairable shadow installs into the current Playwright package install names.')
    repair_parser.add_argument('--prune-broken-links', action='store_true', help='Remove broken Playwright .links registry entries.')
    repair_parser.add_argument('--write-missing-markers', action='store_true', help='Restore INSTALLATION_COMPLETE for imported Playwright browser installs so future Playwright installs do not garbage-collect them as stale.')
    repair_parser.add_argument('--pretty', action='store_true')

    local_exec_parser = subparsers.add_parser('local-executable', help='Print the latest cached Playwright browser executable path.')
    local_exec_parser.add_argument('--root')
    local_exec_parser.add_argument('--platform', default='auto')
    local_exec_parser.add_argument('--package', default=PLAYWRIGHT_EXTENSION_PACKAGE)

    import_archive_parser = subparsers.add_parser('import-archive', help='Import a local browser archive into the Playwright cache.')
    import_archive_parser.add_argument('--archive', required=True)
    import_archive_parser.add_argument('--root')
    import_archive_parser.add_argument('--platform', default='auto')
    import_archive_parser.add_argument('--package', default='auto')
    import_archive_parser.add_argument('--install-name')
    import_archive_parser.add_argument('--version')
    import_archive_parser.add_argument('--revision')
    import_archive_parser.add_argument('--source', default='archive-import')
    import_archive_parser.add_argument('--force', action='store_true')
    import_archive_parser.add_argument('--pretty', action='store_true')

    import_cft_parser = subparsers.add_parser('import-cft', help='Copy a local Chrome for Testing install into the Playwright browser cache.')
    import_cft_parser.add_argument('--version', default='latest')
    import_cft_parser.add_argument('--cft-root')
    import_cft_parser.add_argument('--root')
    import_cft_parser.add_argument('--platform', default='auto')
    import_cft_parser.add_argument('--package', default=PLAYWRIGHT_EXTENSION_PACKAGE)
    import_cft_parser.add_argument('--force', action='store_true')
    import_cft_parser.add_argument('--pretty', action='store_true')

    ensure_parser = subparsers.add_parser('ensure-channel-ready', help='Repair and sync the Playwright Chromium cache until the extension lane is channel-ready.')
    ensure_parser.add_argument('--root')
    ensure_parser.add_argument('--cft-root')
    ensure_parser.add_argument('--platform', default='auto')
    ensure_parser.add_argument('--include-headless-shell', action='store_true')
    ensure_parser.add_argument('--archive', action='append', default=[])
    ensure_parser.add_argument('--download', action='store_true', help='Download missing expected Playwright browser archives directly from the dry-run URLs when no local archive or local Chrome for Testing install is available.')
    ensure_parser.add_argument('--download-dir', help='Retain downloaded browser archives under this directory instead of using a temporary file.')
    ensure_parser.add_argument('--download-timeout', type=float, help='Timeout in seconds for each direct archive download attempt.')
    ensure_parser.add_argument('--force', action='store_true')
    ensure_parser.add_argument('--pretty', action='store_true')

    sync_parser = subparsers.add_parser('sync', help='Align local Playwright browser packages with the current Playwright dry-run package matrix.')
    sync_parser.add_argument('--root')
    sync_parser.add_argument('--cft-root')
    sync_parser.add_argument('--platform', default='auto')
    sync_parser.add_argument('--package', action='append')
    sync_parser.add_argument('--include-headless-shell', action='store_true')
    sync_parser.add_argument('--archive', action='append', default=[])
    sync_parser.add_argument('--download', action='store_true', help='Download missing expected Playwright browser archives directly from the dry-run URLs when no local archive or local Chrome for Testing install is available.')
    sync_parser.add_argument('--download-dir', help='Retain downloaded browser archives under this directory instead of using a temporary file.')
    sync_parser.add_argument('--download-timeout', type=float, help='Timeout in seconds for each direct archive download attempt.')
    sync_parser.add_argument('--force', action='store_true')
    sync_parser.add_argument('--pretty', action='store_true')

    return parser


def resolved_platform(value: str) -> str:
    return detect_cft_platform() if value == 'auto' else value


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == 'inspect':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            env = {'PLAYWRIGHT_BROWSERS_PATH': str(root)}
            install_list_raw = playwright_install_list(env=env, root=root, ensure_links=False)
            registry_raw = inspect_playwright_registry(root, platform=platform)
            cache_audit = audit_playwright_cache(root=root, env=env, platform=platform, install_list=install_list_raw, registry_report=registry_raw)
            install_list_prepared = playwright_install_list(env=env, root=root, ensure_links=True)
            discovered = discover_playwright_browser_install(env=env, install_list=install_list_prepared)
            repair_plan = plan_playwright_cache_repair(root=root, env=env, platform=platform, audit_report=cache_audit, install_list=install_list_raw)
            report: dict[str, Any] = {
                'root': str(root),
                'platform': platform,
                'local_installations': local_playwright_browser_installations(root=root, platform=platform),
                'latest_local_install': latest_local_playwright_browser_install(root=root, platform=platform),
                'install_list_raw': install_list_raw,
                'install_list_prepared': install_list_prepared,
                'registry_raw': registry_raw,
                'cache_audit': cache_audit,
                'repair_plan': repair_plan,
                'discovered_browser_install': discovered,
                'extension_launch_plan': playwright_extension_launch_plan(env=env, browser_install=discovered, repair_plan=repair_plan),
                'dry_run': playwright_install_dry_run(env=env),
            }
            print(json.dumps(report, indent=2 if args.pretty else None))
            return
        if args.command == 'dry-run':
            print(json.dumps(playwright_install_dry_run(), indent=2 if args.pretty else None))
            return
        if args.command == 'list':
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            print(json.dumps(playwright_install_list(root=root, ensure_links=not args.raw), indent=2 if args.pretty else None))
            return
        if args.command == 'audit':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            env = {'PLAYWRIGHT_BROWSERS_PATH': str(root)}
            raw_install_list = playwright_install_list(env=env, root=root, ensure_links=False)
            registry_raw = inspect_playwright_registry(root, platform=platform)
            prepared_install_list = playwright_install_list(env=env, root=root, ensure_links=True)
            print(json.dumps(audit_playwright_cache(root=root, env=env, platform=platform, install_list=raw_install_list, prepared_install_list=prepared_install_list, registry_report=registry_raw), indent=2 if args.pretty else None))
            return
        if args.command == 'repair':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            env = {'PLAYWRIGHT_BROWSERS_PATH': str(root)}
            result = repair_playwright_cache(
                root=root,
                env=env,
                platform=platform,
                align_shadow_installs=args.align_shadow_installs,
                prune_broken_links=args.prune_broken_links,
                write_missing_markers=args.write_missing_markers,
                apply=args.apply,
            )
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
        if args.command == 'local-executable':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            install = latest_local_playwright_browser_install(root=root, platform=platform, package_name=args.package)
            if not install:
                raise SystemExit(1)
            print(install['executable'])
            return
        if args.command == 'import-archive':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            result = install_playwright_browser_archive(
                archive_path=Path(args.archive),
                root=root,
                install_name=args.install_name,
                platform=platform,
                force=args.force,
                metadata={'version': args.version, 'revision': args.revision, 'source': args.source},
                package_name=args.package,
            )
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
        if args.command == 'import-cft':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            cft_root = Path(args.cft_root).expanduser() if args.cft_root else None
            result = import_cft_into_playwright_cache(version=args.version, cft_root=cft_root, playwright_root=root, platform=platform, force=args.force, package_name=args.package)
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
        if args.command == 'ensure-channel-ready':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            cft_root = Path(args.cft_root).expanduser() if args.cft_root else None
            result = ensure_playwright_channel_ready(
                root=root,
                cft_root=cft_root,
                platform=platform,
                include_headless_shell=args.include_headless_shell,
                archive_paths=[Path(item) for item in args.archive],
                force=args.force,
                download_missing=args.download,
                download_dir=Path(args.download_dir).expanduser() if args.download_dir else None,
                download_timeout=args.download_timeout,
            )
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
        if args.command == 'sync':
            platform = resolved_platform(args.platform)
            root = Path(args.root).expanduser() if args.root else playwright_browsers_root()
            cft_root = Path(args.cft_root).expanduser() if args.cft_root else None
            result = sync_playwright_browser_packages(
                root=root,
                cft_root=cft_root,
                platform=platform,
                package_names=args.package,
                include_headless_shell=args.include_headless_shell,
                archive_paths=[Path(item) for item in args.archive],
                force=args.force,
                download_missing=args.download,
                download_dir=Path(args.download_dir).expanduser() if args.download_dir else None,
                download_timeout=args.download_timeout,
            )
            print(json.dumps(result, indent=2 if args.pretty else None))
            return
    except PlaywrightBrowserError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == '__main__':
    main()
