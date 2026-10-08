#!/usr/bin/env python3
"""Report the local FT-0181 field lane without creating evidence.

This is a small cloudtainer hygiene utility: it summarizes what the live field
lane currently contains, flags legacy/shared scratch residue, and quotes the
router's one next action. It writes only scratch/external report artifacts and
must not be used as owner evidence, custody, public-claim support, or closure.
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from decide_ft0181_field_next_action import CLAIM_CEILING, decision_for, is_router_ignored_scratch_path
from ft0181_field_guards import operator_today_iso, output_allowed

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRATCH_ROOT = ROOT / 'scratch' / 'field' / 'ft0181'
DEFAULT_OUTPUT_ROOT = DEFAULT_SCRATCH_ROOT / 'field-lane-reports'
ALLOWED_TOP_LEVEL_SCRATCH = {'field', 'checks'}

KIND_BY_FILENAME = {
    'packet-manifest.json': 'owner_request_packet',
    'send-log.json': 'owner_send_log',
    'reask-log.json': 'owner_reask_log',
    'route-block.json': 'owner_route_block',
    'contact-status.json': 'owner_contact_status',
    'bundle-manifest.json': 'owner_reply_intake_bundle',
    'workbench-seed.json': 'workbench_seed',
    'review-brief.json': 'workbench_review_brief',
    'workbench-review.json': 'workbench_review',
    'decision-brief.json': 'first_packet_decision_brief',
    'first-packet-decision.json': 'first_packet_decision',
    'change-ticket-brief.json': 'post_decision_change_ticket_brief',
    'post-decision-change-ticket.json': 'post_decision_change_ticket',
    'activation-live-window-brief.json': 'activation_live_window_brief',
    'activation-receipt.json': 'activation_receipt',
    'live-window-card.json': 'live_window_card',
    'terminal-brief.json': 'live_window_terminal_brief',
    'live-window-readout-brief.json': 'live_window_readout_brief',
    'live-window-readout.json': 'live_window_readout',
    'post-readout-action-brief.json': 'post_readout_action_brief',
    'post-readout-action.json': 'post_readout_action',
    'post-readout-recheck-brief.json': 'post_readout_recheck_brief',
    'post-readout-recheck.json': 'post_readout_recheck',
    'post-readout-context-receipt.json': 'post_readout_context_receipt',
    'field-next-action.json': 'field_next_action_docket',
    'safe-local-field-session.json': 'safe_local_field_session',
}

DATE_KEYS = {
    'sent_date',
    'response_due_date',
    'status_date',
    'block_date',
    'requested_return_date',
    'check_date',
    'due_or_recheck_date',
    'window_start_date',
    'window_end_date',
}

FUTURE_CLOCK_KEYS = {
    'sent_date',
    'status_date',
    'block_date',
    'check_date',
    'window_start_date',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Summarize the local FT-0181 field scratch lane without creating evidence.')
    parser.add_argument('--scratch-root', type=Path, default=DEFAULT_SCRATCH_ROOT, help='FT-0181 live field lane to summarize.')
    parser.add_argument('--as-of-date', default=operator_today_iso(), help='Operator-local date, YYYY-MM-DD. Defaults through CUBE_AS_OF_DATE/CUBE_OPERATOR_TIMEZONE.')
    parser.add_argument('--output-dir', type=Path, help='Scratch/external directory for the report. Defaults under scratch/field/ft0181/field-lane-reports/.')
    parser.add_argument('--overwrite', action='store_true', help='Replace an existing report directory.')
    parser.add_argument('--json', action='store_true', help='Print the report JSON after writing it.')
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def parse_date_value(value: Any) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    text = value.strip()
    try:
        if text.endswith('Z'):
            return datetime.fromisoformat(text[:-1] + '+00:00').astimezone(timezone.utc).date()
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def extract_dates(data: dict[str, Any]) -> dict[str, str]:
    dates: dict[str, str] = {}
    for key in DATE_KEYS:
        value = data.get(key)
        parsed = parse_date_value(value)
        if parsed is not None:
            dates[key] = parsed.isoformat()
    return dates


def scan_lane(scratch_root: Path, as_of: date) -> dict[str, Any]:
    root = scratch_root if scratch_root.is_absolute() else ROOT / scratch_root
    counts: dict[str, int] = {}
    artifacts: list[dict[str, Any]] = []
    future_clock_artifacts: list[dict[str, Any]] = []
    ignored_fixture_artifacts: list[str] = []
    if root.exists():
        for path in sorted(root.rglob('*.json')):
            if is_router_ignored_scratch_path(path, root):
                ignored_fixture_artifacts.append(rel(path))
                continue
            data = load_json(path)
            if data is None:
                continue
            kind = KIND_BY_FILENAME.get(path.name, 'other_json')
            counts[kind] = counts.get(kind, 0) + 1
            dates = extract_dates(data)
            future_dates = {
                key: value
                for key, value in dates.items()
                if key in FUTURE_CLOCK_KEYS and date.fromisoformat(value) > as_of
            }
            row = {
                'kind': kind,
                'path': rel(path),
                'dates': dates,
                'future_relative_to_as_of': future_dates,
            }
            artifacts.append(row)
            if future_dates:
                future_clock_artifacts.append(row)
    legacy_scratch: list[str] = []
    scratch_top = ROOT / 'scratch'
    if scratch_top.exists():
        for child in sorted(scratch_top.iterdir()):
            if child.name not in ALLOWED_TOP_LEVEL_SCRATCH:
                legacy_scratch.append(rel(child))
    return {
        'scratch_root': rel(root),
        'artifact_counts': counts,
        'artifact_count_total': sum(counts.values()),
        'future_clock_artifacts': future_clock_artifacts,
        'legacy_non_lane_scratch_items': legacy_scratch,
        'ignored_validation_fixture_artifact_count': len(ignored_fixture_artifacts),
        'ignored_validation_fixture_artifact_samples': ignored_fixture_artifacts[:25],
        'sample_artifacts': artifacts[:25],
        'truncated_sample': len(artifacts) > 25,
    }


def default_output(as_of_date: str) -> Path:
    return DEFAULT_OUTPUT_ROOT / f'aiedu-sr-003-{as_of_date}'


def report_markdown(report: dict[str, Any]) -> str:
    decision = report.get('router_decision', {}) if isinstance(report.get('router_decision'), dict) else {}
    scan = report.get('field_lane_scan', {}) if isinstance(report.get('field_lane_scan'), dict) else {}
    lines = [
        '# FT-0181 field lane cleanliness report',
        '',
        f"Report state: `{report.get('report_state')}`",
        f"Operator-local date: `{report.get('as_of_date')}`",
        'Evidence effect: `not_evidence`',
        'Closure effect: `does_not_close_ft0181`',
        'Public claim effect: `none`',
        '',
        'This report is a scratch hygiene aid only. It summarizes local field-lane state and must not be cited as owner evidence, custody, public-summary support, service-record authority, lifecycle movement, or FT-0181 closure.',
        '',
        '## Router next action',
        '',
        f"Outcome: `{decision.get('outcome')}`",
        '',
        '```bash',
        str(decision.get('recommended_command') or 'none'),
        '```',
        '',
        '## Field-lane counts',
        '',
        '```json',
        json.dumps(scan.get('artifact_counts', {}), indent=2, sort_keys=True),
        '```',
        '',
        '## Warnings',
        '',
    ]
    warnings = report.get('warnings', [])
    if warnings:
        for warning in warnings:
            lines.append(f'- {warning}')
    else:
        lines.append('- No lane hygiene warning was detected by this local report.')
    lines.extend([
        '',
        '## Claim boundary',
        '',
        CLAIM_CEILING,
    ])
    return '\n'.join(lines) + '\n'


def build_report(*, scratch_root: Path, as_of_date: str) -> dict[str, Any]:
    as_of = date.fromisoformat(as_of_date)
    scan = scan_lane(scratch_root, as_of)
    decision = decision_for(scratch_root=scratch_root, returned_csv=None, as_of_date=as_of_date)
    warnings: list[str] = []
    if scan['legacy_non_lane_scratch_items']:
        warnings.append('legacy/shared scratch residue exists outside scratch/field and scratch/checks; do not point SCRATCH=scratch at it unless intentionally debugging')
    if scan['future_clock_artifacts']:
        warnings.append('one or more local scratch artifacts carry executed/recorded dates after the operator-local as_of date; rerun with CUBE_AS_OF_DATE or inspect before recording field clocks')
    if scan.get('ignored_validation_fixture_artifact_count'):
        warnings.append('validation fixture artifacts exist under the field lane but are ignored by router/report scans; do not treat them as live owner field state')
    if scan['artifact_count_total'] == 0:
        warnings.append('field lane is empty; the next useful local action is first-contact packet prep, not another doctrine surface')
    if decision.get('outcome') == 'PREPARE-FIRST-CONTACT-PACKET':
        warnings.append('no real owner-contact packet has been prepared in the selected lane')
    return {
        'report_type': 'FT-0181-field-lane-cleanliness-report',
        'report_state': 'LOCAL_SCRATCH_HYGIENE_NOT_EVIDENCE',
        'as_of_date': as_of_date,
        'created_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'field_lane_scan': scan,
        'router_decision': {
            'ok': decision.get('ok'),
            'outcome': decision.get('outcome'),
            'recommended_command': decision.get('recommended_command'),
            'source_artifact': decision.get('source_artifact'),
            'observed_artifact_counts': decision.get('observed_artifact_counts'),
        },
        'warnings': warnings,
        'evidence_effect': 'not_evidence',
        'closure_effect': 'does_not_close_ft0181',
        'public_claim_effect': 'none',
        'claim_ceiling': CLAIM_CEILING,
    }


def write_report(report: dict[str, Any], output_dir: Path, *, overwrite: bool) -> dict[str, Any]:
    allowed, boundary = output_allowed(output_dir, archive_root=ROOT)
    if not allowed:
        return {'ok': False, 'error': 'FIELD-LANE-REPORT-OUTPUT-BLOCKED', 'reason': boundary}
    if output_dir.exists() and any(output_dir.iterdir()):
        if not overwrite:
            return {'ok': False, 'error': 'FIELD-LANE-REPORT-OUTPUT-EXISTS', 'reason': 'use --overwrite or choose an empty output directory'}
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    enriched = dict(report)
    enriched['ok'] = True
    enriched['output_boundary'] = boundary
    enriched['output_dir'] = rel(output_dir)
    (output_dir / 'field-lane-report.json').write_text(json.dumps(enriched, indent=2) + '\n', encoding='utf-8')
    (output_dir / 'FIELD-LANE-REPORT.md').write_text(report_markdown(enriched), encoding='utf-8')
    return enriched


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or default_output(args.as_of_date)
    report = build_report(scratch_root=args.scratch_root, as_of_date=args.as_of_date)
    written = write_report(report, output_dir, overwrite=args.overwrite)
    if args.json:
        print(json.dumps(written, indent=2))
    elif written.get('ok'):
        print(f"report_ft0181_field_lane: OK ({written['output_dir']}, outcome={written['router_decision']['outcome']})")
    else:
        raise SystemExit(f"report_ft0181_field_lane: {written['error']} ({written['reason']})")
    return 0 if written.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
