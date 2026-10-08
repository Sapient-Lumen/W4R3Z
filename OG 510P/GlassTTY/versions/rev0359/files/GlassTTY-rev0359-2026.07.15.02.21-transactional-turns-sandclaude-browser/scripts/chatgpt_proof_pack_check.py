#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_first_proof_artifact_ledger import ARTIFACT_SLOTS, build_artifact_ledger, sha256_file
from chatgpt_first_proof_evaluator import REVIEWABLE_VERDICT, REHEARSAL_VERDICT

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-pack-check-summary.json'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


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


def read_json_or_error(path: Path) -> tuple[Any | None, str | None]:
    try:
        return read_json(path), None
    except Exception as exc:  # pragma: no cover - exact parser exception is not important
        return None, str(exc)


def png_dimensions(path: Path) -> JsonDict:
    if not path.exists():
        return {'ok': False, 'error': 'missing'}
    try:
        data = path.read_bytes()[:32]
        if len(data) < 24 or data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
            return {'ok': False, 'error': 'not-a-png'}
        width, height = struct.unpack('>II', data[16:24])
        return {'ok': True, 'width': width, 'height': height}
    except Exception as exc:  # pragma: no cover
        return {'ok': False, 'error': str(exc)}


def artifact_row_map(ledger: JsonDict) -> dict[str, JsonDict]:
    rows = ledger.get('slots')
    if not isinstance(rows, list):
        rows = ledger.get('artifacts')
    if not isinstance(rows, list):
        return {}
    out: dict[str, JsonDict] = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get('filename'), str):
            out[row['filename']] = row
    return out


def check_pack(
    pack_dir: Path = DEFAULT_PACK_DIR,
    *,
    summary_path: Path | None = DEFAULT_SUMMARY,
    require_live: bool = False,
    allow_rehearsal: bool = True,
    require_privacy_pass: bool = False,
) -> JsonDict:
    pack_dir = pack_dir.resolve()
    ledger = build_artifact_ledger(pack_dir, readiness_level='publication-review-ready')
    rows_by_name = artifact_row_map(ledger)
    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    expected_filenames = [slot.filename for slot in ARTIFACT_SLOTS]
    missing = [filename for filename in expected_filenames if not (pack_dir / filename).exists()]
    empty_required = [
        filename for filename in expected_filenames
        if (pack_dir / filename).exists()
        and rows_by_name.get(filename, {}).get('nonempty') is False
    ]
    json_parse_failures = [
        filename for filename in expected_filenames
        if rows_by_name.get(filename, {}).get('artifact_type') == 'json'
        and rows_by_name.get(filename, {}).get('parse_ok') is False
    ]
    if missing:
        blockers.append(f'missing artifact slots: {", ".join(missing)}')
    if empty_required:
        blockers.append(f'empty artifact slots: {", ".join(empty_required)}')
    if json_parse_failures:
        blockers.append(f'json parse failures: {", ".join(json_parse_failures)}')

    manifest, manifest_error = read_json_or_error(pack_dir / 'bundle-manifest.json')
    evaluation, evaluation_error = read_json_or_error(pack_dir / 'chatgpt-first-proof-evaluation.json')
    screenshot_meta, screenshot_meta_error = read_json_or_error(pack_dir / 'surface-screenshot.metadata.json')
    privacy_review, privacy_review_error = read_json_or_error(pack_dir / 'privacy-redaction-review.json')

    if manifest_error:
        blockers.append(f'bundle-manifest.json failed to parse: {manifest_error}')
        manifest = {}
    if evaluation_error:
        blockers.append(f'chatgpt-first-proof-evaluation.json failed to parse: {evaluation_error}')
        evaluation = {}
    if screenshot_meta_error:
        blockers.append(f'surface-screenshot.metadata.json failed to parse: {screenshot_meta_error}')
        screenshot_meta = {}
    if privacy_review_error:
        privacy_review = {}

    manifest_obj = manifest if isinstance(manifest, dict) else {}
    evaluation_obj = evaluation if isinstance(evaluation, dict) else {}
    screenshot_meta_obj = screenshot_meta if isinstance(screenshot_meta, dict) else {}
    privacy_review_obj = privacy_review if isinstance(privacy_review, dict) else {}

    rehearsal_only = bool(manifest_obj.get('rehearsal_only'))
    proof_mode = manifest_obj.get('proof_mode') if isinstance(manifest_obj.get('proof_mode'), str) else None
    evaluator_verdict = evaluation_obj.get('verdict') if isinstance(evaluation_obj.get('verdict'), str) else None
    evaluator_harness_ok = bool(evaluation_obj.get('harness_ok'))
    screenshot_path = pack_dir / 'surface-screenshot.png'
    screenshot_dims = png_dimensions(screenshot_path)
    screenshot_placeholder = bool(screenshot_meta_obj.get('placeholder_not_live'))
    screenshot_source = screenshot_meta_obj.get('source') if isinstance(screenshot_meta_obj.get('source'), str) else None
    privacy_review_verdict = privacy_review_obj.get('verdict') if isinstance(privacy_review_obj.get('verdict'), str) else None
    privacy_review_ok = privacy_review_obj.get('ok') if isinstance(privacy_review_obj.get('ok'), bool) else None
    privacy_review_human_complete = bool(privacy_review_obj.get('human_attestation_complete'))

    if not screenshot_path.exists():
        blockers.append('surface-screenshot.png is missing')
    elif not screenshot_dims.get('ok'):
        blockers.append(f'surface-screenshot.png is not a readable PNG: {screenshot_dims.get("error")}')
    elif screenshot_dims.get('width') == 1 and screenshot_dims.get('height') == 1:
        warnings.append('surface-screenshot.png is a 1x1 placeholder-sized image')

    if screenshot_placeholder:
        warnings.append('surface-screenshot.metadata.json marks screenshot as placeholder_not_live')

    if require_privacy_pass and privacy_review_verdict != 'privacy-review-pass':
        blockers.append(f'require-privacy-pass was set, but privacy review verdict is {privacy_review_verdict!r}')
    if require_live:
        if rehearsal_only:
            blockers.append('require-live was set, but bundle-manifest.json declares rehearsal_only=true')
        if screenshot_placeholder:
            blockers.append('require-live was set, but screenshot metadata marks a non-live placeholder')
        if screenshot_dims.get('width') == 1 and screenshot_dims.get('height') == 1:
            blockers.append('require-live was set, but screenshot dimensions are placeholder-sized 1x1')
        if evaluator_verdict != REVIEWABLE_VERDICT:
            blockers.append(f'require-live was set, but evaluator verdict is {evaluator_verdict!r}')
    elif rehearsal_only and not allow_rehearsal:
        blockers.append('rehearsal evidence pack supplied but rehearsals are not allowed for this check')

    if rehearsal_only and evaluator_verdict != REHEARSAL_VERDICT:
        blockers.append(f'rehearsal bundle must evaluate as {REHEARSAL_VERDICT}, got {evaluator_verdict!r}')
    if not evaluator_harness_ok:
        blockers.append('evaluator harness_ok is false or missing')

    consistency = ledger.get('attempt_id_consistency') if isinstance(ledger.get('attempt_id_consistency'), dict) else {}
    attempt_ids = consistency.get('observed_attempt_ids') if isinstance(consistency.get('observed_attempt_ids'), list) else []
    if not attempt_ids and isinstance(manifest_obj.get('attempt_id'), str):
        attempt_ids = [manifest_obj['attempt_id']]
    if len(attempt_ids) > 1:
        warnings.append(f'multiple attempt IDs appear in the evidence pack: {attempt_ids}')

    complete_artifact_set = not missing and len([p for p in expected_filenames if (pack_dir / p).exists()]) == len(expected_filenames)
    structurally_ok = complete_artifact_set and not empty_required and not json_parse_failures and bool(ledger.get('ready')) and evaluator_harness_ok
    ok = structurally_ok and not blockers

    if require_live and ok:
        verdict = 'live-evidence-pack-review-ready'
    elif rehearsal_only and ok:
        verdict = 'rehearsal-evidence-pack-check-ok-not-live'
    elif ok:
        verdict = 'evidence-pack-structurally-ok-live-status-unconfirmed'
    else:
        verdict = 'evidence-pack-check-blocked'

    if not ok:
        recommendations.append('Fix blockers before treating this pack as evaluator/review evidence.')
    if rehearsal_only:
        recommendations.append('This pack is an offline rehearsal. Do not publish it or treat it as a live ChatGPT proof.')
    if screenshot_placeholder:
        recommendations.append('For live proof, capture a real visible ChatGPT screenshot from the side panel and export the pack again.')
    if privacy_review_verdict is None:
        recommendations.append('Run proof-privacy-review before publication/support use.')
    elif privacy_review_verdict != 'privacy-review-pass':
        recommendations.append(f'Privacy review status is {privacy_review_verdict!r}; live publication/support use still needs an explicit pass attestation.')
    if not require_live and not rehearsal_only:
        recommendations.append('Rerun with --require-live before claiming a live reviewable proof pack.')

    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-pack-check',
        'generated_at': utcnow(),
        'ok': ok,
        'verdict': verdict,
        'pack_dir': display_path(pack_dir),
        'require_live': require_live,
        'require_privacy_pass': require_privacy_pass,
        'expected_artifact_count': len(expected_filenames),
        'present_artifact_count': len([filename for filename in expected_filenames if (pack_dir / filename).exists()]),
        'complete_artifact_set': complete_artifact_set,
        'ledger_ready_publication_level': bool(ledger.get('ready')),
        'ledger_missing_required': ledger.get('missing_required_artifacts'),
        'missing_artifacts': missing,
        'empty_artifacts': empty_required,
        'json_parse_failures': json_parse_failures,
        'attempt_ids': attempt_ids,
        'manifest': {
            'proof_mode': proof_mode,
            'rehearsal_only': rehearsal_only,
            'attempt_id': manifest_obj.get('attempt_id'),
        },
        'screenshot': {
            'exists': screenshot_path.exists(),
            'sha256': sha256_file(screenshot_path) if screenshot_path.exists() else None,
            'metadata_source': screenshot_source,
            'placeholder_not_live': screenshot_placeholder,
            'dimensions': screenshot_dims,
        },
        'evaluation': {
            'verdict': evaluator_verdict,
            'harness_ok': evaluator_harness_ok,
            'missing_required_checks': evaluation_obj.get('missing_required_checks'),
        },
        'privacy_review': {
            'json_exists': (pack_dir / 'privacy-redaction-review.json').exists(),
            'markdown_exists': (pack_dir / 'privacy-redaction-review.md').exists(),
            'verdict': privacy_review_verdict,
            'ok': privacy_review_ok,
            'human_attestation_complete': privacy_review_human_complete,
            'publishable_without_additional_redaction': bool(privacy_review_obj.get('publishable_without_additional_redaction')),
        },
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
    }
    if summary_path:
        write_json(summary_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Check a 30-slot ChatGPT proof evidence pack for completeness and live/rehearsal safety.')
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--require-live', action='store_true', help='Fail unless the pack is a live reviewable proof pack with a real screenshot and live evaluator verdict')
    parser.add_argument('--no-rehearsal', action='store_true', help='Fail rehearsal packs even without --require-live')
    parser.add_argument('--require-privacy-pass', action='store_true', help='Fail unless privacy-redaction-review.json records privacy-review-pass')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = check_pack(
        args.pack_dir,
        summary_path=args.summary_out,
        require_live=args.require_live,
        allow_rehearsal=not args.no_rehearsal,
        require_privacy_pass=args.require_privacy_pass,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
