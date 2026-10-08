#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_first_proof_artifact_ledger import sha256_file
from chatgpt_proof_pack_check import check_pack

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUNDLE = ROOT / 'validation' / 'latest' / 'chatgpt-proof-publish-bundle.zip'
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-publish-verify-summary.json'
PACK_PREFIX = 'chatgpt-proof-evidence-pack/'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def safe_extract_bundle(bundle: Path, dest: Path) -> tuple[list[str], list[str]]:
    """Extract a zip without allowing absolute or parent-traversal paths."""
    entries: list[str] = []
    blockers: list[str] = []
    dest_resolved = dest.resolve()
    try:
        with zipfile.ZipFile(bundle, 'r') as zf:
            for info in zf.infolist():
                name = info.filename
                entries.append(name)
                if not name or name.endswith('/'):
                    continue
                path = Path(name)
                if path.is_absolute() or '..' in path.parts:
                    blockers.append(f'unsafe zip entry path: {name}')
                    continue
                target = (dest / path).resolve()
                try:
                    target.relative_to(dest_resolved)
                except ValueError:
                    blockers.append(f'zip entry escapes extraction root: {name}')
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(info))
    except zipfile.BadZipFile as exc:
        blockers.append(f'not a valid zip file: {exc}')
    except Exception as exc:  # pragma: no cover - defensive I/O guard
        blockers.append(f'failed to extract publish bundle: {exc}')
    return entries, blockers


def manifest_file_check(pack_dir: Path) -> JsonDict:
    manifest_path = pack_dir / 'publish-bundle-manifest.json'
    blockers: list[str] = []
    warnings: list[str] = []
    checked: list[JsonDict] = []
    if not manifest_path.exists():
        return {
            'ok': False,
            'manifest_exists': False,
            'checked_file_count': 0,
            'blockers': ['publish-bundle-manifest.json is missing from the evidence pack'],
            'warnings': [],
        }
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        return {
            'ok': False,
            'manifest_exists': True,
            'checked_file_count': 0,
            'blockers': [f'publish-bundle-manifest.json failed to parse: {exc}'],
            'warnings': [],
        }
    if not isinstance(manifest, dict):
        return {
            'ok': False,
            'manifest_exists': True,
            'checked_file_count': 0,
            'blockers': ['publish-bundle-manifest.json is not a JSON object'],
            'warnings': [],
        }
    rows = manifest.get('files')
    if not isinstance(rows, list) or not rows:
        blockers.append('publish-bundle-manifest.json has no non-empty files[] inventory')
        rows = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            blockers.append(f'manifest files[{index}] is not an object')
            continue
        rel = row.get('path')
        expected_bytes = row.get('bytes')
        expected_sha256 = row.get('sha256')
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or '..' in Path(rel).parts:
            blockers.append(f'manifest files[{index}] has unsafe path {rel!r}')
            continue
        path = pack_dir / rel
        record: JsonDict = {'path': rel, 'exists': path.exists()}
        if not path.exists():
            blockers.append(f'manifest-listed file is missing: {rel}')
            checked.append(record)
            continue
        actual_bytes = path.stat().st_size
        actual_sha256 = sha256_file(path)
        record.update({'bytes': actual_bytes, 'sha256': actual_sha256})
        if isinstance(expected_bytes, int) and expected_bytes != actual_bytes:
            blockers.append(f'manifest byte mismatch for {rel}: expected {expected_bytes}, got {actual_bytes}')
        elif not isinstance(expected_bytes, int):
            warnings.append(f'manifest does not record byte count for {rel}')
        if isinstance(expected_sha256, str) and expected_sha256 != actual_sha256:
            blockers.append(f'manifest sha256 mismatch for {rel}')
        elif not isinstance(expected_sha256, str):
            warnings.append(f'manifest does not record sha256 for {rel}')
        checked.append(record)
    all_files = [p.relative_to(pack_dir).as_posix() for p in sorted(pack_dir.rglob('*')) if p.is_file()]
    listed = {row.get('path') for row in rows if isinstance(row, dict) and isinstance(row.get('path'), str)}
    extras = [rel for rel in all_files if rel not in listed]
    allowed_extra = {'publish-bundle-manifest.json', 'PUBLISH-README.md'}
    unexpected_extras = [rel for rel in extras if rel not in allowed_extra]
    if unexpected_extras:
        warnings.append(f'{len(unexpected_extras)} file(s) are present but not listed by publish-bundle-manifest.json')
    return {
        'ok': not blockers,
        'manifest_exists': True,
        'checked_file_count': len(checked),
        'extra_files': extras,
        'unexpected_extra_files': unexpected_extras,
        'blockers': blockers,
        'warnings': warnings,
    }


def verify_publish_bundle(
    bundle: Path = DEFAULT_BUNDLE,
    *,
    summary_path: Path | None = DEFAULT_SUMMARY,
    expected_sha256: str | None = None,
    require_live: bool = True,
    require_privacy_pass: bool = True,
) -> JsonDict:
    bundle = bundle.resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    if not bundle.exists():
        blockers.append('publish bundle zip is missing')
        report: JsonDict = {
            'schema_version': SCHEMA_VERSION,
            'tool': 'glasstty-chatgpt-proof-publish-verify',
            'generated_at': utcnow(),
            'ok': False,
            'verdict': 'proof-publish-verify-blocked',
            'bundle': display_path(bundle),
            'bundle_exists': False,
            'blockers': blockers,
            'warnings': warnings,
            'recommendations': ['Create a live support bundle with proof-publish-bundle, then rerun proof-publish-verify.'],
        }
        if summary_path:
            write_json(summary_path, report)
        return report

    zip_sha256 = sha256_file(bundle)
    if expected_sha256 and expected_sha256.strip().lower() != zip_sha256:
        blockers.append('publish bundle sha256 does not match --expected-sha256')

    with tempfile.TemporaryDirectory(prefix='glasstty-publish-verify-') as tmp:
        extract_root = Path(tmp) / 'extract'
        entries, extract_blockers = safe_extract_bundle(bundle, extract_root)
        blockers.extend(extract_blockers)
        pack_dir = extract_root / 'chatgpt-proof-evidence-pack'
        if entries and not any(entry.startswith(PACK_PREFIX) for entry in entries):
            blockers.append(f'zip does not contain expected {PACK_PREFIX} prefix')
        if not pack_dir.exists():
            blockers.append('extracted zip does not contain chatgpt-proof-evidence-pack/')
        manifest_check = manifest_file_check(pack_dir) if pack_dir.exists() else {
            'ok': False,
            'manifest_exists': False,
            'checked_file_count': 0,
            'blockers': ['cannot check manifest because evidence-pack directory is missing'],
            'warnings': [],
        }
        blockers.extend([b for b in manifest_check.get('blockers', []) if isinstance(b, str)])
        warnings.extend([w for w in manifest_check.get('warnings', []) if isinstance(w, str)])
        if pack_dir.exists():
            pack_check = check_pack(
                pack_dir,
                summary_path=None,
                require_live=require_live,
                allow_rehearsal=not require_live,
                require_privacy_pass=require_privacy_pass,
            )
            blockers.extend([b for b in pack_check.get('blockers', []) if isinstance(b, str)])
            warnings.extend([w for w in pack_check.get('warnings', []) if isinstance(w, str)])
        else:
            pack_check = {'ok': False, 'verdict': 'evidence-pack-missing'}

        ok = not blockers and bool(manifest_check.get('ok')) and bool(pack_check.get('ok'))
        verdict = 'proof-publish-verify-ok' if ok else 'proof-publish-verify-blocked'
        report = {
            'schema_version': SCHEMA_VERSION,
            'tool': 'glasstty-chatgpt-proof-publish-verify',
            'generated_at': utcnow(),
            'ok': ok,
            'verdict': verdict,
            'bundle': display_path(bundle),
            'bundle_exists': True,
            'bundle_bytes': bundle.stat().st_size,
            'bundle_sha256': zip_sha256,
            'expected_sha256': expected_sha256,
            'expected_sha256_match': None if not expected_sha256 else expected_sha256.strip().lower() == zip_sha256,
            'zip_entry_count': len(entries),
            'require_live': require_live,
            'require_privacy_pass': require_privacy_pass,
            'manifest_check': manifest_check,
            'pack_check': pack_check,
            'blockers': blockers,
            'warnings': warnings,
            'recommendations': [
                'Treat proof-publish-verify-ok as the post-transfer support-bundle integrity gate.',
                'If blocked, rerun proof-publish-bundle from the source evidence pack and compare hashes.',
            ] if ok else [
                'Do not share this zip as a support/proof bundle until proof-publish-verify passes.',
                'If the zip was transferred, redownload or recreate it and rerun verification.',
            ],
        }
    if summary_path:
        write_json(summary_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Verify a ChatGPT proof publish/support zip after transfer by checking its manifest, hashes, and live/privacy pack gates.')
    parser.add_argument('--bundle', type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--expected-sha256')
    parser.add_argument('--no-require-live', action='store_true')
    parser.add_argument('--no-require-privacy-pass', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = verify_publish_bundle(
        args.bundle,
        summary_path=args.summary_out,
        expected_sha256=args.expected_sha256,
        require_live=not args.no_require_live,
        require_privacy_pass=not args.no_require_privacy_pass,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
