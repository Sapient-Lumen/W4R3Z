from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-attempt-audit.json'
PROBE_TEXT = 'Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT'
EXPECTED_REPLY = 'GLASSTTY-CHECKPOINT'
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


def compact(value: Any) -> str:
    return ' '.join(value.split()).strip() if isinstance(value, str) else ''


def payload_of(row: JsonDict | None) -> JsonDict:
    if isinstance(row, dict) and isinstance(row.get('payload'), dict):
        return row['payload']  # type: ignore[return-value]
    return {}


def row_type(row: JsonDict) -> str:
    for key in ('type', 'request_type', 'response_type'):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ''


def rows_from_capture(source: JsonDict) -> list[JsonDict]:
    rows = source.get('actions')
    if isinstance(rows, list) and all(isinstance(row, dict) for row in rows):
        return list(rows)  # preserve side-panel/document order
    envelopes = source.get('raw_envelopes')
    if isinstance(envelopes, list):
        out = []
        for index, item in enumerate(envelopes):
            if not isinstance(item, dict):
                continue
            row = dict(item)
            row.setdefault('sequence_index', index)
            out.append(row)
        return out
    return []


def first_index(rows: list[JsonDict], kind: str, predicate: Any | None = None) -> int | None:
    for index, row in enumerate(rows):
        if row_type(row) != kind:
            continue
        if predicate is not None and not predicate(row):
            continue
        return index
    return None


def last_index(rows: list[JsonDict], kind: str, predicate: Any | None = None) -> int | None:
    found: int | None = None
    for index, row in enumerate(rows):
        if row_type(row) != kind:
            continue
        if predicate is not None and not predicate(row):
            continue
        found = index
    return found


def text_from_row(row: JsonDict | None, *keys: str) -> str:
    if row is None:
        return ''
    for container in (row, payload_of(row)):
        for key in keys:
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return compact(value)
    return ''


def bool_from_row(row: JsonDict | None, *keys: str) -> bool | None:
    if row is None:
        return None
    for container in (row, payload_of(row)):
        for key in keys:
            value = container.get(key)
            if isinstance(value, bool):
                return value
    return None


def action_ok(row: JsonDict | None) -> bool:
    value = bool_from_row(row, 'ok')
    return bool(value)


def is_gate_ok(row: JsonDict) -> bool:
    payload = payload_of(row)
    return row_type(row) == 'fixture.capture' and payload.get('proof_live_gate_ok') is True


def is_final_ready(row: JsonDict) -> bool:
    payload = payload_of(row)
    return (
        row_type(row) == 'proof.operator_readiness'
        and payload.get('ok') is True
        and payload.get('verdict') == 'proof-attempt-ready-to-download'
        and payload.get('next_stage') == 'download-proof-json'
    )


def audit_attempt(source: JsonDict, *, source_path: Path | None = None,
                  require_ready_to_download: bool = False) -> JsonDict:
    rows = rows_from_capture(source)
    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    if not rows:
        blockers.append('capture has no actions or raw_envelopes to audit')

    write_idx = first_index(rows, 'prompt.write')
    gate_idx = first_index(rows, 'fixture.capture', is_gate_ok)
    screenshot_idx = first_index(rows, 'proof.surface_screenshot')
    submit_idx = first_index(rows, 'prompt.submit')
    latest_idx = first_index(rows, 'transcript.latest')
    final_ready_idx = last_index(rows, 'proof.operator_readiness', is_final_ready)

    required = {
        'prompt.write': write_idx,
        'fixture.capture live gate ok': gate_idx,
        'proof.surface_screenshot': screenshot_idx,
        'prompt.submit': submit_idx,
        'transcript.latest': latest_idx,
    }
    for name, index in required.items():
        if index is None:
            blockers.append(f'missing {name} action in proof attempt sequence')

    if require_ready_to_download and final_ready_idx is None:
        blockers.append('missing final proof.operator_readiness envelope with verdict proof-attempt-ready-to-download')
    elif final_ready_idx is None:
        warnings.append('no final proof.operator_readiness ready-to-download envelope found; press Download proof JSON in rev0350+ to force this gate')

    ordered_pairs = [
        ('prompt.write', write_idx, 'live gate', gate_idx),
        ('live gate', gate_idx, 'visible screenshot', screenshot_idx),
        ('visible screenshot', screenshot_idx, 'prompt.submit', submit_idx),
        ('prompt.submit', submit_idx, 'transcript.latest', latest_idx),
    ]
    if require_ready_to_download:
        ordered_pairs.append(('transcript.latest', latest_idx, 'final readiness', final_ready_idx))
    for left_name, left, right_name, right in ordered_pairs:
        if left is not None and right is not None and not left < right:
            blockers.append(f'{left_name} must occur before {right_name}')

    write = rows[write_idx] if write_idx is not None and write_idx < len(rows) else None
    submit = rows[submit_idx] if submit_idx is not None and submit_idx < len(rows) else None
    latest = rows[latest_idx] if latest_idx is not None and latest_idx < len(rows) else None
    gate = rows[gate_idx] if gate_idx is not None and gate_idx < len(rows) else None
    screenshot = rows[screenshot_idx] if screenshot_idx is not None and screenshot_idx < len(rows) else None
    final_ready = rows[final_ready_idx] if final_ready_idx is not None and final_ready_idx < len(rows) else None

    if write is not None and not action_ok(write):
        blockers.append('prompt.write action is not ok')
    if submit is not None and not action_ok(submit):
        blockers.append('prompt.submit action is not ok')
    if latest is not None and not action_ok(latest):
        blockers.append('transcript.latest action is not ok')
    if screenshot is not None and not action_ok(screenshot):
        blockers.append('proof.surface_screenshot action is not ok')

    if write is not None and text_from_row(write, 'readback') != PROBE_TEXT:
        blockers.append('prompt.write readback does not exactly match checkpoint prompt')
    if submit is not None:
        submit_texts = [
            text_from_row(submit, 'composer_readback_before_submit'),
            text_from_row(submit, 'prompt_before_submit'),
            text_from_row(submit, 'submitted_prompt'),
        ]
        if PROBE_TEXT not in submit_texts:
            blockers.append('prompt.submit readback does not exactly match checkpoint prompt')
        if bool_from_row(submit, 'proof_live_gate_ok') is not True:
            blockers.append('prompt.submit lacks proof_live_gate_ok=true')
        if text_from_row(submit, 'proof_live_gate_verdict') != 'proof-live-gate-ok':
            blockers.append('prompt.submit lacks proof_live_gate_verdict=proof-live-gate-ok')
    if latest is not None and text_from_row(latest, 'text') != EXPECTED_REPLY:
        blockers.append('transcript.latest text does not exactly match GLASSTTY-CHECKPOINT')
    if latest is not None:
        payload = payload_of(latest)
        user_witness = payload.get('latest_user_turn_witness')
        if isinstance(user_witness, dict) and compact(user_witness.get('text')) != PROBE_TEXT:
            blockers.append('latest user-turn witness does not match checkpoint prompt')

    if screenshot is not None:
        data_url = payload_of(screenshot).get('visible_tab_screenshot_data_url')
        if not (isinstance(data_url, str) and data_url.startswith('data:image/png;base64,')):
            blockers.append('proof.surface_screenshot lacks a PNG data URL')

    if gate is not None:
        gate_payload = payload_of(gate)
        observed = gate_payload.get('proof_live_gate_observed')
        if isinstance(observed, dict):
            if observed.get('blocked_composer_control_disqualified') is not True:
                blockers.append('live gate did not prove the known non-send composer control was disqualified')
            selector = observed.get('submit_selector') or observed.get('observed_live_send_selector')
            if isinstance(selector, str) and '#composer-submit-button' not in selector:
                blockers.append('live gate strict send selector is not #composer-submit-button')

    if final_ready is not None:
        payload = payload_of(final_ready)
        checks = payload.get('checks')
        if isinstance(checks, dict):
            required_checks = [
                'checkpoint_write_readback',
                'live_gate_ok',
                'visible_screenshot_captured',
                'submit_readback_exact_probe',
                'latest_reply_exact_checkpoint',
                'latest_user_turn_exact_prompt',
            ]
            for check in required_checks:
                if checks.get(check) is not True:
                    blockers.append(f'final operator readiness check is not true: {check}')
        else:
            warnings.append('final operator readiness payload lacks checks map')

    if blockers:
        recommendations.append('Do not ingest/finalize this attempt as live. Re-run the side-panel flow in order and use Download proof JSON, not manual copy, so the final readiness gate is embedded.')
    else:
        recommendations.append('Attempt sequence is ordered and ready for proof-ingest/autopilot handoff.')
    if warnings:
        recommendations.append('Prefer rev0350+ Download proof JSON so the capture includes an auditable final readiness envelope.')

    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-attempt-audit',
        'generated_at': utcnow(),
        'source_path': display_path(source_path) if source_path is not None else None,
        'ok': not blockers,
        'verdict': 'proof-attempt-audit-ok' if not blockers else 'proof-attempt-audit-blocked',
        'require_ready_to_download': require_ready_to_download,
        'action_count': len(rows),
        'indices': {
            'prompt_write': write_idx,
            'live_gate_fixture': gate_idx,
            'visible_screenshot': screenshot_idx,
            'prompt_submit': submit_idx,
            'transcript_latest': latest_idx,
            'final_ready_to_download': final_ready_idx,
        },
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
    }
    return report


def audit_file(path: Path, *, summary_out: Path = DEFAULT_SUMMARY,
               require_ready_to_download: bool = False) -> JsonDict:
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f'{path} must contain a JSON object')
    report = audit_attempt(payload, source_path=path, require_ready_to_download=require_ready_to_download)
    write_json(summary_out, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Audit ordered side-panel ChatGPT proof-attempt events before proof-ingest/finalization.')
    parser.add_argument('--input', required=True, type=Path, help='Downloaded side-panel proof JSON or normalized capture JSON')
    parser.add_argument('--summary-out', default=DEFAULT_SUMMARY, type=Path)
    parser.add_argument('--require-ready-to-download', action='store_true', help='Require final proof.operator_readiness ready-to-download envelope')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = audit_file(args.input, summary_out=args.summary_out, require_ready_to_download=args.require_ready_to_download)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
