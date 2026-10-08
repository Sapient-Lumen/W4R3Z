#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_contract_paths import active_contract_path
from chatgpt_first_proof_artifact_ledger import sha256_file
from chatgpt_proof_pack_check import check_pack
from chatgpt_proof_publish_verify import verify_publish_bundle

ROOT = Path(__file__).resolve().parent.parent
LATEST = ROOT / 'validation' / 'latest'
LIVE_PACK = ROOT / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'
DEFAULT_SUMMARY = LATEST / 'chatgpt-proof-operator-state.json'
DEFAULT_REHEARSAL_PACK = LATEST / 'chatgpt-proof-rehearsal-evidence-pack'
DEFAULT_LIVE_CAPTURE = LATEST / 'chatgpt-first-proof-capture.json'
DEFAULT_PUBLISH_BUNDLE = LATEST / 'chatgpt-proof-publish-bundle.zip'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def file_summary(path: Path) -> JsonDict:
    exists = path.exists()
    row: JsonDict = {
        'path': display_path(path),
        'exists': exists,
    }
    if exists and path.is_file():
        row.update({
            'bytes': path.stat().st_size,
            'sha256': sha256_file(path),
        })
    return row


def json_summary(path: Path, *, verdict_keys: tuple[str, ...] = ('verdict',)) -> JsonDict:
    row = file_summary(path)
    payload = read_json(path) if path.exists() else None
    row['parse_ok'] = isinstance(payload, dict)
    if isinstance(payload, dict):
        for key in verdict_keys:
            value = payload.get(key)
            if value is not None:
                row[key] = value
        if 'ok' in payload:
            row['ok'] = bool(payload.get('ok'))
        if 'blockers' in payload and isinstance(payload.get('blockers'), list):
            row['blocker_count'] = len(payload['blockers'])
        if 'warnings' in payload and isinstance(payload.get('warnings'), list):
            row['warning_count'] = len(payload['warnings'])
    return row


def command(*parts: str | Path) -> str:
    return ' '.join(str(part) for part in parts if str(part))


def live_pack_has_files(pack_dir: Path) -> bool:
    return pack_dir.exists() and any(p.is_file() and p.name not in {'README.md', '.gitkeep'} for p in pack_dir.rglob('*'))


def pack_status(pack_dir: Path, *, require_live: bool, require_privacy_pass: bool) -> JsonDict:
    if not live_pack_has_files(pack_dir):
        return {
            'path': display_path(pack_dir),
            'exists': pack_dir.exists(),
            'has_files': False,
            'ok': False,
            'verdict': 'evidence-pack-missing',
            'blockers': ['evidence pack directory is missing or empty'],
        }
    report = check_pack(
        pack_dir,
        summary_path=None,
        require_live=require_live,
        allow_rehearsal=not require_live,
        require_privacy_pass=require_privacy_pass,
    )
    return {
        'path': display_path(pack_dir),
        'exists': pack_dir.exists(),
        'has_files': True,
        'ok': bool(report.get('ok')),
        'verdict': report.get('verdict'),
        'require_live': require_live,
        'require_privacy_pass': require_privacy_pass,
        'blocker_count': len(report.get('blockers') or []),
        'warning_count': len(report.get('warnings') or []),
        'blockers': report.get('blockers') or [],
        'warnings': report.get('warnings') or [],
        'manifest': report.get('manifest'),
        'evaluation': report.get('evaluation'),
        'privacy_review': report.get('privacy_review'),
        'screenshot': report.get('screenshot'),
    }


def publish_verify_status(bundle: Path, *, require_live: bool, require_privacy_pass: bool) -> JsonDict:
    if not bundle.exists():
        return {
            'path': display_path(bundle),
            'exists': False,
            'ok': False,
            'verdict': 'publish-bundle-missing',
            'blockers': ['publish bundle zip is missing'],
        }
    report = verify_publish_bundle(
        bundle,
        summary_path=None,
        expected_sha256=None,
        require_live=require_live,
        require_privacy_pass=require_privacy_pass,
    )
    return {
        'path': display_path(bundle),
        'exists': True,
        'bytes': bundle.stat().st_size,
        'sha256': sha256_file(bundle),
        'ok': bool(report.get('ok')),
        'verdict': report.get('verdict'),
        'blocker_count': len(report.get('blockers') or []),
        'warning_count': len(report.get('warnings') or []),
        'blockers': report.get('blockers') or [],
        'warnings': report.get('warnings') or [],
    }


def build_next_action(
    *,
    contract: JsonDict,
    preflight: JsonDict,
    capture: JsonDict,
    live_pack: JsonDict,
    publish_bundle: JsonDict,
    require_live: bool,
) -> JsonDict:
    live_pack_dir = LIVE_PACK
    if not contract.get('exists'):
        return {
            'stage': 'surface-contract-missing',
            'label': 'Build or restore the active ChatGPT surface contract.',
            'command': command('glassttyd', 'surface-contract-build', '<known-good-surface-report.json>', '--out', active_contract_path(ROOT)),
            'reason': 'No active contract file exists, so live drift cannot be checked.',
        }
    if preflight.get('verdict') != 'ready-for-live-operator-attempt-not-a-live-proof':
        return {
            'stage': 'run-preflight',
            'label': 'Run proof preflight before a live operator attempt.',
            'command': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-preflight --pretty',
            'reason': 'The latest preflight summary is missing or not ready.',
        }
    if not capture.get('exists'):
        return {
            'stage': 'capture-live-proof',
            'label': 'Run the side-panel live gated checkpoint flow and download proof JSON.',
            'command': 'Use the extension side panel: Capture visible screenshot → Write checkpoint + capture → Check live gate → Submit checkpoint (gated) → Read latest + capture → Download proof JSON. If the panel reloaded, use Restore recovery vault or Download recovery JSON first.',
            'reason': 'No normalized live proof capture has been ingested yet.',
        }
    if capture.get('ok') is False or capture.get('verdict') not in {None, 'proof-ingest-ok'}:
        return {
            'stage': 'ingest-downloaded-proof-json',
            'label': 'Validate and normalize the downloaded proof JSON.',
            'command': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-ingest --input ~/Downloads/glasstty-chatgpt-proof-<attempt>.json --require-live-candidate --pretty',
            'reason': 'The current ingest summary is missing, failed, or not a live candidate.',
        }
    if not live_pack.get('has_files') or live_pack.get('verdict') != 'live-evidence-pack-review-ready':
        return {
            'stage': 'finalize-live-pack',
            'label': 'Finalize the ingested capture into the live 30-slot evidence pack.',
            'command': command(
                'PYTHONPATH=$PWD/daemon/src:$PWD/scripts',
                'glassttyd', 'proof-finalize-pack',
                '--input', 'validation/latest/chatgpt-first-proof-capture.json',
                '--pack-dir', 'validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack',
                '--require-live', '--clean', '--pretty',
            ),
            'reason': 'The live evidence pack is missing or does not yet pass live review-ready checks.',
        }
    privacy = live_pack.get('privacy_review') if isinstance(live_pack.get('privacy_review'), dict) else {}
    if privacy.get('verdict') != 'privacy-review-pass':
        return {
            'stage': 'privacy-review',
            'label': 'Complete human privacy/redaction review for the live evidence pack.',
            'command': command(
                'PYTHONPATH=$PWD/daemon/src:$PWD/scripts',
                'glassttyd', 'proof-privacy-review',
                '--pack-dir', 'validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack',
                '--require-live', '--require-pass',
                '--reviewer', '"<name>"',
                '--decision', 'pass',
                '--attest-screenshot-reviewed',
                '--attest-no-unrelated-content',
                '--attest-local-only',
                '--pretty',
            ),
            'reason': 'A live support bundle requires explicit privacy-review-pass attestation.',
        }
    if publish_bundle.get('verdict') != 'proof-publish-verify-ok':
        return {
            'stage': 'publish-and-verify',
            'label': 'Create and verify the support/publish zip.',
            'command': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-bundle --pretty && PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-verify --pretty',
            'reason': 'The live pack appears ready, but the publish bundle is missing or has not passed transfer verification.',
        }
    return {
        'stage': 'complete',
        'label': 'Verified live support/publish bundle is ready.',
        'command': 'No next command required; preserve the verified zip and SHA-256 from proof-publish-verify.',
        'reason': 'All live gates passed.',
    }


def build_status(
    *,
    summary_path: Path | None = DEFAULT_SUMMARY,
    live_pack_dir: Path = LIVE_PACK,
    rehearsal_pack_dir: Path = DEFAULT_REHEARSAL_PACK,
    publish_bundle_path: Path = DEFAULT_PUBLISH_BUNDLE,
    require_live: bool = True,
) -> JsonDict:
    contract_path = active_contract_path(ROOT)
    contract = json_summary(contract_path, verdict_keys=('contract_version',))
    preflight = json_summary(LATEST / 'chatgpt-proof-preflight.json')
    ingest_summary = json_summary(LATEST / 'chatgpt-proof-ingest-summary.json')
    capture = json_summary(DEFAULT_LIVE_CAPTURE)
    capture['ingest_summary'] = ingest_summary
    if ingest_summary.get('ok') is not None:
        capture['ok'] = bool(ingest_summary.get('ok'))
    if ingest_summary.get('verdict') is not None:
        capture['verdict'] = ingest_summary.get('verdict')
    rehearsal_pack = pack_status(rehearsal_pack_dir, require_live=False, require_privacy_pass=False)
    live_pack = pack_status(live_pack_dir, require_live=require_live, require_privacy_pass=False)
    live_pack_with_privacy = pack_status(live_pack_dir, require_live=require_live, require_privacy_pass=True)
    publish_summary = json_summary(LATEST / 'chatgpt-proof-publish-summary.json')
    publish_verify = publish_verify_status(publish_bundle_path, require_live=require_live, require_privacy_pass=True)
    next_action = build_next_action(
        contract=contract,
        preflight=preflight,
        capture=capture,
        live_pack=live_pack_with_privacy if live_pack_with_privacy.get('has_files') else live_pack,
        publish_bundle=publish_verify,
        require_live=require_live,
    )
    complete = next_action.get('stage') == 'complete'
    blockers: list[str] = []
    if require_live and not complete:
        blockers.append(f'live proof pipeline incomplete: next stage is {next_action.get("stage")}')
    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-status',
        'generated_at': utcnow(),
        'ok': complete if require_live else True,
        'verdict': 'live-proof-pipeline-complete' if complete else 'live-proof-pipeline-incomplete',
        'require_live': require_live,
        'current_stage': next_action.get('stage'),
        'next_action': next_action,
        'artifacts': {
            'active_surface_contract': contract,
            'preflight_summary': preflight,
            'normalized_capture': capture,
            'rehearsal_evidence_pack': rehearsal_pack,
            'live_evidence_pack': live_pack,
            'live_evidence_pack_with_privacy_gate': live_pack_with_privacy,
            'publish_summary': publish_summary,
            'publish_bundle_verify': publish_verify,
        },
        'operator_commands': {
            'preflight': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-preflight --pretty',
            'ingest_downloaded_json': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-ingest --input ~/Downloads/glasstty-chatgpt-proof-<attempt>.json --require-live-candidate --pretty',
            'finalize_live_pack': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-finalize-pack --input validation/latest/chatgpt-first-proof-capture.json --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --clean --pretty',
            'privacy_review_pass': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-privacy-review --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --require-pass --reviewer "<name>" --decision pass --attest-screenshot-reviewed --attest-no-unrelated-content --attest-local-only --pretty',
            'publish_bundle': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-bundle --pretty',
            'verify_publish_bundle': 'PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-verify --pretty',
        },
        'blockers': blockers,
        'warnings': [],
    }
    if summary_path:
        write_json(summary_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Report the resumable state of the ChatGPT live proof pipeline and the exact next operator command.')
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--live-pack-dir', type=Path, default=LIVE_PACK)
    parser.add_argument('--rehearsal-pack-dir', type=Path, default=DEFAULT_REHEARSAL_PACK)
    parser.add_argument('--publish-bundle', type=Path, default=DEFAULT_PUBLISH_BUNDLE)
    parser.add_argument('--no-require-live', action='store_true', help='Do not fail the status just because the live pipeline is incomplete')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_status(
        summary_path=args.summary_out,
        live_pack_dir=args.live_pack_dir,
        rehearsal_pack_dir=args.rehearsal_pack_dir,
        publish_bundle_path=args.publish_bundle,
        require_live=not args.no_require_live,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
