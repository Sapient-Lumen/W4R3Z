#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from chatgpt_first_proof_evaluator import payload_declares_rehearsal
from chatgpt_first_proof_kit import EXPECTED_REPLY, PROBE_TEXT
from chatgpt_proof_finalize_pack import DEFAULT_CHECK_SUMMARY, DEFAULT_EXPORT_SUMMARY, DEFAULT_FINAL_SUMMARY, finalize_pack

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-capture.json'
DEFAULT_REDACTED_OUT = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-capture.redacted.json'
DEFAULT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-ingest-summary.json'
DEFAULT_PACK_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-proof-ingest-evidence-pack'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def compact(value: Any) -> str:
    if not isinstance(value, str):
        return ''
    return ' '.join(value.split()).strip()


def actions(source: JsonDict) -> list[JsonDict]:
    rows = source.get('actions')
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def first_action(rows: list[JsonDict], kind: str) -> JsonDict | None:
    for row in rows:
        if row.get('type') == kind or row.get('request_type') == kind:
            return row
    return None


def action_payload(action: JsonDict | None) -> JsonDict:
    if isinstance(action, dict) and isinstance(action.get('payload'), dict):
        return action['payload']  # type: ignore[return-value]
    return {}


def action_text(action: JsonDict | None, *keys: str) -> str:
    if not isinstance(action, dict):
        return ''
    for container in (action, action_payload(action)):
        for key in keys:
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return compact(value)
    return ''


def action_bool(action: JsonDict | None, *keys: str) -> bool | None:
    if not isinstance(action, dict):
        return None
    for container in (action, action_payload(action)):
        for key in keys:
            value = container.get(key)
            if isinstance(value, bool):
                return value
    return None


def action_ok(action: JsonDict | None) -> bool:
    value = action_bool(action, 'ok')
    return bool(value)


def infer_attempt_id(source: JsonDict, rows: list[JsonDict]) -> str | None:
    for container in [source, *rows]:
        for key in ('attempt_id', 'capture_id', 'run_id', 'bundle_id', 'proof_id'):
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        payload = action_payload(container)
        for key in ('attempt_id', 'capture_id', 'run_id', 'bundle_id', 'proof_id'):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def host_from_action(action: JsonDict | None) -> str | None:
    for container in (action or {}, action_payload(action)):
        value = container.get('url') or container.get('payload_url')
        if isinstance(value, str) and value.strip():
            try:
                return urlparse(value).netloc
            except Exception:
                return None
    return None


def conversation_route_paths(source: JsonDict, rows: list[JsonDict]) -> list[str]:
    out: list[str] = []
    for value in source.get('observed_conversation_route_paths') or []:
        if isinstance(value, str) and value.startswith('/c/'):
            out.append(value)
    for action in rows:
        for container in (action, action_payload(action)):
            value = container.get('conversation_route_path') or container.get('payload_conversation_route_path')
            if isinstance(value, str) and value.startswith('/c/'):
                out.append(value)
            url = container.get('url') or container.get('payload_url')
            if isinstance(url, str):
                try:
                    parsed = urlparse(url)
                    if parsed.netloc.endswith('chatgpt.com') and parsed.path.startswith('/c/'):
                        out.append(parsed.path)
                except Exception:
                    pass
    return sorted(set(out))



def png_dimensions_from_bytes(data: bytes) -> JsonDict:
    if len(data) < 24 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
        return {'width': None, 'height': None, 'error': 'not-png'}
    return {
        'width': int.from_bytes(data[16:20], 'big'),
        'height': int.from_bytes(data[20:24], 'big'),
    }


def iter_screenshot_data_urls(source: JsonDict) -> list[tuple[str, str]]:
    candidates: list[tuple[str, Any]] = []
    for key in ('visible_tab_screenshot_data_url', 'surface_screenshot_data_url', 'screenshot_data_url'):
        candidates.append((key, source.get(key)))
    captures = source.get('captures')
    if isinstance(captures, dict):
        for name, capture in captures.items():
            if isinstance(capture, dict):
                for key in ('visible_tab_screenshot_data_url', 'surface_screenshot_data_url', 'screenshot_data_url'):
                    candidates.append((f'captures.{name}.{key}', capture.get(key)))
    for index, action in enumerate(actions(source)):
        for container_name, container in (('action', action), ('payload', action_payload(action))):
            for key in ('visible_tab_screenshot_data_url', 'surface_screenshot_data_url', 'screenshot_data_url'):
                candidates.append((f'actions.{index}.{container_name}.{key}', container.get(key)))
    return [(path, value.strip()) for path, value in candidates if isinstance(value, str) and value.strip().startswith('data:image/png;base64,')]


def png_info_from_data_url(data_url: str) -> JsonDict:
    prefix = 'data:image/png;base64,'
    if not data_url.startswith(prefix):
        return {'present': False, 'valid_png_data_url': False}
    try:
        data = base64.b64decode(data_url.split(',', 1)[1], validate=True)
    except Exception as exc:
        return {'present': True, 'valid_png_data_url': False, 'decode_error': str(exc)}
    valid = data.startswith(b'\x89PNG\r\n\x1a\n')
    dims = png_dimensions_from_bytes(data) if valid else {'width': None, 'height': None}
    return {
        'present': True,
        'valid_png_data_url': valid,
        'byte_length': len(data),
        'sha256': sha256_bytes(data),
        'dimensions': dims,
        'placeholder_sized': dims.get('width') == 1 and dims.get('height') == 1,
    }


def redact_large_data_urls(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: redact_large_data_urls(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_large_data_urls(item) for item in value]
    if isinstance(value, str) and value.startswith('data:image/png;base64,'):
        info = png_info_from_data_url(value)
        return {
            'redacted_data_url': True,
            'mime_type': 'image/png',
            'byte_length': info.get('byte_length'),
            'sha256': info.get('sha256'),
            'dimensions': info.get('dimensions'),
        }
    return value


def validate_capture(source: JsonDict, source_path: Path | None = None) -> JsonDict:
    rows = actions(source)
    write = first_action(rows, 'prompt.write')
    submit = first_action(rows, 'prompt.submit')
    latest = first_action(rows, 'transcript.latest')
    screenshot_candidates = iter_screenshot_data_urls(source)
    screenshot_info = png_info_from_data_url(screenshot_candidates[0][1]) if screenshot_candidates else {'present': False}
    rehearsal = payload_declares_rehearsal(source)
    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    if not isinstance(source.get('schema_version'), int):
        warnings.append('source JSON has no integer schema_version')
    if source.get('surface_key') not in (None, 'chatgpt'):
        blockers.append('surface_key is not chatgpt')
    if not rows:
        blockers.append('actions array is missing or empty')
    if write is None:
        blockers.append('missing prompt.write action')
    elif not action_ok(write):
        blockers.append('prompt.write action is not ok')
    if submit is None:
        blockers.append('missing prompt.submit action')
    elif not action_ok(submit):
        blockers.append('prompt.submit action is not ok')
    if latest is None:
        blockers.append('missing transcript.latest action')
    elif not action_ok(latest):
        blockers.append('transcript.latest action is not ok')

    write_readback = action_text(write, 'readback')
    submit_readback = action_text(submit, 'composer_readback_before_submit', 'prompt_before_submit', 'submitted_prompt')
    latest_text = action_text(latest, 'text')
    if write is not None and write_readback != PROBE_TEXT:
        blockers.append('prompt.write readback does not exactly match checkpoint prompt')
    if submit is not None and submit_readback != PROBE_TEXT:
        blockers.append('prompt.submit readback does not exactly match checkpoint prompt')
    if latest is not None and latest_text != EXPECTED_REPLY:
        blockers.append('transcript.latest text does not exactly match expected checkpoint reply')

    gate_ok = bool(source.get('proof_live_gate_ok_seen')) or action_bool(submit, 'proof_live_gate_ok') is True
    if not gate_ok:
        blockers.append('proof live gate ok evidence is missing before submit')
    if action_text(submit, 'proof_live_gate_verdict') not in ('proof-live-gate-ok', 'surface-contract-ok'):
        # Some future captures may keep the verdict in the source-level set rather than the action payload.
        verdicts = source.get('proof_live_gate_verdicts')
        if not (isinstance(verdicts, list) and any(v in ('proof-live-gate-ok', 'surface-contract-ok') for v in verdicts)):
            blockers.append('proof live gate verdict is missing or not ok')
    if action_text(submit, 'submit_selector') and action_text(submit, 'submit_selector') != '#composer-submit-button':
        blockers.append('submit selector is not #composer-submit-button')
    if action_text(submit, 'submit_data_testid') and action_text(submit, 'submit_data_testid') != 'send-button':
        blockers.append('submit data-testid is not send-button')
    if action_text(submit, 'submit_aria_label') and action_text(submit, 'submit_aria_label') != 'Send prompt':
        blockers.append('submit aria-label is not Send prompt')

    host = host_from_action(write) or host_from_action(submit) or host_from_action(latest)
    if host and not host.endswith('chatgpt.com'):
        blockers.append('proof actions are not on chatgpt.com')
    routes = conversation_route_paths(source, rows)
    if latest is not None and not routes:
        warnings.append('no /c/ conversation route path was detected in proof actions')
    if source.get('single_tab_context') is False:
        blockers.append('proof capture is not a single-tab context')
    if source.get('same_conversation_route_after_latest') is False:
        blockers.append('settled/latest evidence did not stay on the same conversation route')
    if source.get('write_readback_exact_probe_seen') is False:
        blockers.append('source-level write_readback_exact_probe_seen is false')
    if source.get('submit_readback_exact_probe_seen') is False:
        blockers.append('source-level submit_readback_exact_probe_seen is false')

    if not screenshot_candidates:
        if rehearsal:
            warnings.append('visible ChatGPT screenshot data URL is missing; acceptable only for rehearsal ingest')
        else:
            blockers.append('visible ChatGPT screenshot data URL is missing')
    elif not screenshot_info.get('valid_png_data_url'):
        blockers.append('visible screenshot is not a valid PNG data URL')
    elif screenshot_info.get('placeholder_sized'):
        if rehearsal:
            warnings.append('visible screenshot is 1x1 placeholder-sized; acceptable only for rehearsal ingest')
        else:
            blockers.append('visible screenshot is 1x1 placeholder-sized and not live evidence')

    if rehearsal:
        warnings.append('capture declares rehearsal_only; ingest can preserve it but cannot treat it as live')
    if source_path is not None and source_path.name.endswith('.txt'):
        warnings.append('input file has .txt extension; prefer the side-panel .json download')

    if blockers:
        recommendations.append('Do not finalize as live. Re-run the side-panel proof flow: write checkpoint, capture visible screenshot, gated submit, read latest, then Download proof JSON.')
    elif rehearsal:
        recommendations.append('Rehearsal capture passed ingest checks for plumbing only. Use an actual downloaded side-panel proof JSON before live finalization.')
    else:
        recommendations.append('Capture JSON passed ingest checks. Run proof-finalize-pack --require-live against the normalized output.')
    if rehearsal:
        recommendations.append('Rehearsal captures are useful for plumbing tests only and must remain excluded from live claims.')

    live_candidate = not blockers and not rehearsal
    verdict = 'proof-json-ingested-live-candidate' if live_candidate else ('proof-json-ingested-rehearsal-not-live' if rehearsal and not blockers else 'proof-json-ingest-blocked')
    return {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-ingest',
        'generated_at': utcnow(),
        'ok': not blockers,
        'verdict': verdict,
        'live_candidate': live_candidate,
        'rehearsal_only': rehearsal,
        'source_path': display_path(source_path) if source_path is not None else None,
        'source_sha256': sha256_file(source_path) if source_path is not None and source_path.exists() else None,
        'attempt_id': infer_attempt_id(source, rows),
        'capture_kind': source.get('capture_kind'),
        'action_counts': {
            'total': len(rows),
            'prompt_write': 1 if write is not None else 0,
            'prompt_submit': 1 if submit is not None else 0,
            'transcript_latest': 1 if latest is not None else 0,
        },
        'checkpoint': {
            'write_readback_exact': write_readback == PROBE_TEXT,
            'submit_readback_exact': submit_readback == PROBE_TEXT,
            'latest_reply_exact': latest_text == EXPECTED_REPLY,
        },
        'live_gate': {
            'ok_seen': gate_ok,
            'submit_verdict': action_text(submit, 'proof_live_gate_verdict'),
            'source_verdicts': source.get('proof_live_gate_verdicts') if isinstance(source.get('proof_live_gate_verdicts'), list) else [],
            'submit_selector': action_text(submit, 'submit_selector'),
            'submit_data_testid': action_text(submit, 'submit_data_testid'),
            'submit_aria_label': action_text(submit, 'submit_aria_label'),
        },
        'route': {
            'host': host,
            'conversation_route_paths': routes,
            'single_tab_context': source.get('single_tab_context'),
            'same_conversation_route_after_latest': source.get('same_conversation_route_after_latest'),
        },
        'screenshot': {
            **screenshot_info,
            'candidate_count': len(screenshot_candidates),
            'first_candidate_path': screenshot_candidates[0][0] if screenshot_candidates else None,
        },
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
    }


def ingest_capture(
    source_path: Path,
    *,
    out: Path = DEFAULT_OUT,
    redacted_out: Path | None = DEFAULT_REDACTED_OUT,
    summary_out: Path = DEFAULT_SUMMARY,
    require_live_candidate: bool = False,
    finalize: bool = False,
    pack_dir: Path = DEFAULT_PACK_DIR,
    final_summary_path: Path = DEFAULT_FINAL_SUMMARY,
    export_summary_path: Path = DEFAULT_EXPORT_SUMMARY,
    check_summary_path: Path = DEFAULT_CHECK_SUMMARY,
    clean: bool = False,
) -> JsonDict:
    source = read_json(source_path)
    if not isinstance(source, dict):
        raise ValueError(f'{source_path} must contain a JSON object')
    normalized = copy.deepcopy(source)
    ingest_summary = validate_capture(normalized, source_path=source_path)
    normalized.setdefault('ingest', {})
    if isinstance(normalized['ingest'], dict):
        normalized['ingest'].update({
            'ingested_at': ingest_summary['generated_at'],
            'source_path': ingest_summary['source_path'],
            'source_sha256': ingest_summary['source_sha256'],
            'verdict': ingest_summary['verdict'],
            'live_candidate': ingest_summary['live_candidate'],
        })
    write_json(out, normalized)
    if redacted_out is not None:
        write_json(redacted_out, redact_large_data_urls(normalized))
    finalization: JsonDict | None = None
    if finalize and (ingest_summary.get('ok') or not require_live_candidate):
        finalization = finalize_pack(
            out,
            pack_dir,
            final_summary_path=final_summary_path,
            export_summary_path=export_summary_path,
            check_summary_path=check_summary_path,
            clean=clean,
            require_live=require_live_candidate,
            allow_placeholder_screenshot=False if require_live_candidate else None,
        )
    elif finalize:
        finalization = {
            'ok': False,
            'verdict': 'proof-finalize-skipped-ingest-blocked',
            'reason': 'ingest did not pass and --require-live-candidate was requested',
        }
    report = {
        **ingest_summary,
        'normalized_output_path': display_path(out),
        'redacted_preview_path': display_path(redacted_out) if redacted_out is not None else None,
        'finalization': finalization,
    }
    if require_live_candidate and not report.get('live_candidate'):
        report['ok'] = False
        if report.get('verdict') == 'proof-json-ingested-rehearsal-not-live':
            report['verdict'] = 'proof-json-ingest-blocked-not-live'
    write_json(summary_out, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Validate and normalize a downloaded side-panel ChatGPT proof JSON before evidence-pack finalization.')
    parser.add_argument('--input', type=Path, required=True, help='Downloaded side-panel proof JSON')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT, help='Normalized capture output path')
    parser.add_argument('--redacted-out', type=Path, default=DEFAULT_REDACTED_OUT, help='Redacted preview output path; pass empty string to disable')
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--require-live-candidate', action='store_true', help='Fail if the capture is rehearsal or lacks live-ready evidence')
    parser.add_argument('--finalize', action='store_true', help='Run proof-finalize-pack after a successful ingest')
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument('--final-summary-out', type=Path, default=DEFAULT_FINAL_SUMMARY)
    parser.add_argument('--export-summary-out', type=Path, default=DEFAULT_EXPORT_SUMMARY)
    parser.add_argument('--check-summary-out', type=Path, default=DEFAULT_CHECK_SUMMARY)
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    redacted_out: Path | None = args.redacted_out
    if str(redacted_out) in {'', 'none', 'None', '-'}:
        redacted_out = None
    report = ingest_capture(
        args.input,
        out=args.out,
        redacted_out=redacted_out,
        summary_out=args.summary_out,
        require_live_candidate=args.require_live_candidate,
        finalize=args.finalize,
        pack_dir=args.pack_dir,
        final_summary_path=args.final_summary_out,
        export_summary_path=args.export_summary_out,
        check_summary_path=args.check_summary_out,
        clean=args.clean,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
