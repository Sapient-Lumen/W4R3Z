#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_first_proof_artifact_ledger import sha256_file
from chatgpt_proof_pack_check import check_pack

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK_DIR = ROOT / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'
DEFAULT_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-proof-publish-bundle.zip'
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-publish-summary.json'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def file_inventory(pack_dir: Path) -> list[JsonDict]:
    rows: list[JsonDict] = []
    for path in sorted(pack_dir.rglob('*')):
        if not path.is_file():
            continue
        rows.append({
            'path': path.relative_to(pack_dir).as_posix(),
            'bytes': path.stat().st_size,
            'sha256': sha256_file(path),
        })
    return rows


def build_publish_readme(summary: JsonDict) -> str:
    lines = [
        '# GlassTTY ChatGPT proof publish bundle',
        '',
        f"- verdict: `{summary.get('verdict')}`",
        f"- ok: `{summary.get('ok')}`",
        f"- generated_at: `{summary.get('generated_at')}`",
        f"- source_pack_dir: `{summary.get('pack_dir')}`",
        f"- evidence_file_count: `{summary.get('evidence_file_count')}`",
        '- zip_sha256: run `proof-publish-verify` or use the external publish summary; the zip cannot self-report its final hash from inside itself.',
        '',
        'This bundle is intended for support/review handoff only when the verdict is `proof-publish-bundle-ready`.',
        'It should contain a live ChatGPT checkpoint proof, a real screenshot, evaluator output, and a passing privacy/redaction review.',
        '',
    ]
    check = summary.get('check') if isinstance(summary.get('check'), dict) else {}
    lines.extend([
        '## Gate summary',
        '',
        f"- pack_check_verdict: `{check.get('verdict')}`",
        f"- privacy_review_verdict: `{(check.get('privacy_review') or {}).get('verdict') if isinstance(check.get('privacy_review'), dict) else None}`",
        f"- evaluator_verdict: `{(check.get('evaluation') or {}).get('verdict') if isinstance(check.get('evaluation'), dict) else None}`",
        '',
    ])
    if summary.get('blockers'):
        lines.extend(['## Blockers', ''])
        for blocker in summary.get('blockers') or []:
            lines.append(f'- {blocker}')
        lines.append('')
    return '\n'.join(lines)


def create_zip(pack_dir: Path, out_zip: Path, *, extra_files: list[Path]) -> None:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack_dir.rglob('*')):
            if not path.is_file():
                continue
            if path.resolve() == out_zip.resolve():
                continue
            zf.write(path, f'chatgpt-proof-evidence-pack/{path.relative_to(pack_dir).as_posix()}')
        for path in extra_files:
            if path.exists() and path.is_file():
                zf.write(path, path.name)


def publish_bundle(
    pack_dir: Path = DEFAULT_PACK_DIR,
    out_zip: Path = DEFAULT_OUT,
    *,
    summary_path: Path = DEFAULT_SUMMARY,
    require_live: bool = True,
    require_privacy_pass: bool = True,
) -> JsonDict:
    pack_dir = pack_dir.resolve()
    out_zip = out_zip.resolve()
    check_report = check_pack(
        pack_dir,
        summary_path=None,
        require_live=require_live,
        allow_rehearsal=not require_live,
        require_privacy_pass=require_privacy_pass,
    )
    blockers = [b for b in check_report.get('blockers', []) if isinstance(b, str)]
    check_ok = bool(check_report.get('ok'))
    ok = check_ok and not blockers
    if ok:
        verdict = 'proof-publish-bundle-ready'
    else:
        verdict = 'proof-publish-bundle-blocked'

    inventory = file_inventory(pack_dir) if pack_dir.exists() else []
    summary: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-publish-bundle',
        'generated_at': utcnow(),
        'ok': ok,
        'verdict': verdict,
        'pack_dir': display_path(pack_dir),
        'out_zip': display_path(out_zip),
        'require_live': require_live,
        'require_privacy_pass': require_privacy_pass,
        'evidence_file_count': len(inventory),
        'check': check_report,
        'blockers': blockers,
        'recommendations': [
            'Only publish or share the zip when verdict is proof-publish-bundle-ready.',
            'If blocked, fix the evidence pack and rerun proof-publish-bundle.',
        ],
        'zip_created': False,
        'zip_sha256': None,
    }

    if not ok:
        if summary_path:
            write_json(summary_path, summary)
        return summary

    manifest_path = pack_dir / 'publish-bundle-manifest.json'
    readme_path = pack_dir / 'PUBLISH-README.md'
    manifest: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-publish-bundle-manifest',
        'generated_at': utcnow(),
        'pack_dir': display_path(pack_dir),
        'manifest_scope': 'evidence-pack-files-excluding-publish-bundle-manifest-and-publish-readme',
        'pack_check_verdict': check_report.get('verdict'),
        'privacy_review_verdict': (check_report.get('privacy_review') or {}).get('verdict') if isinstance(check_report.get('privacy_review'), dict) else None,
        'evaluator_verdict': (check_report.get('evaluation') or {}).get('verdict') if isinstance(check_report.get('evaluation'), dict) else None,
        'files': inventory,
    }
    write_json(manifest_path, manifest)
    # Refresh inventory after writing the manifest.
    summary['evidence_file_count'] = len(file_inventory(pack_dir))
    write_text(readme_path, build_publish_readme(summary))
    create_zip(pack_dir, out_zip, extra_files=[])
    summary['zip_created'] = True
    # The zip hash is intentionally written only to the external summary.
    # Putting the final zip hash into a file inside the zip would make the hash self-referential.
    summary['zip_sha256'] = sha256_file(out_zip)
    if summary_path:
        write_json(summary_path, summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Create a support/publish zip from a live, privacy-reviewed ChatGPT proof evidence pack.')
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--no-require-live', action='store_true', help='Do not require a live proof pack. Intended only for diagnostics; the command will still report its verdict.')
    parser.add_argument('--no-require-privacy-pass', action='store_true', help='Do not require privacy-review-pass. Intended only for diagnostics.')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = publish_bundle(
        args.pack_dir,
        args.out,
        summary_path=args.summary_out,
        require_live=not args.no_require_live,
        require_privacy_pass=not args.no_require_privacy_pass,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
