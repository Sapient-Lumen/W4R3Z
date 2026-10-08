#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_proof_bundle_receipt import build_chatgpt_proof_bundle_receipt, evaluate_chatgpt_proof_bundle_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _PROOF = _load('chatgpt_proof_bundle_receipt', 'chatgpt_proof_bundle_receipt.py')
    build_chatgpt_proof_bundle_receipt = _PROOF.build_chatgpt_proof_bundle_receipt
    evaluate_chatgpt_proof_bundle_receipt = _PROOF.evaluate_chatgpt_proof_bundle_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-PROMOTION-STABILITY-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-promotion-stability-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-promotion-stability-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-promotion-stability-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-promotion-stability-receipt.py capture --output-dir validation/latest/chatgpt-promotion-stability-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-promotion-stability-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-promotion-stability-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-promotion-stability-receipt.py evaluate --promotion path/to/promotion-window.json --pretty'

Payload = dict[str, Any]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _history_entries(path: Path) -> list[dict[str, Any]]:
    try:
        payload = _read_json(path)
    except Exception:
        return []
    entries = payload.get('entries') if isinstance(payload, dict) else None
    return [entry for entry in entries if isinstance(entry, dict)] if isinstance(entries, list) else []


def summarize_capture_history(path: Path | None = None) -> dict[str, Any]:
    history_path = path or DEFAULT_HISTORY_PATH
    entries = _history_entries(history_path)
    payload = _read_json(history_path) if history_path.exists() else None
    latest = entries[-1] if entries else None
    return {
        'path': str(history_path),
        'exists': history_path.exists(),
        'capture_count': len(entries),
        'latest_capture': latest,
        'history': payload,
    }


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def _history_payload(entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        'schema_version': 1,
        'updated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'capture_count': len(entries),
        'entries': entries,
    }


def _normalize_keyish(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace('_', '-').replace(' ', '-')
    return normalized or None


def _normalize_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = ' '.join(value.strip().lower().split())
    return normalized or None


def _artifact_rows(payload: Payload) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ('artifact_refs', 'artifacts', 'promotion_artifacts'):
        raw = payload.get(key)
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    rows.append(item)
    return rows


def _artifact_present(rows: list[dict[str, Any]], *, kind_needles: tuple[str, ...] = (), path_needles: tuple[str, ...] = (), role_needles: tuple[str, ...] = ()) -> bool:
    kinds = {item for item in (_normalize_keyish(value) for value in kind_needles) if item}
    paths = {item for item in (_normalize_keyish(value) for value in path_needles) if item}
    roles = {item for item in (_normalize_keyish(value) for value in role_needles) if item}
    for row in rows:
        kind = _normalize_keyish(row.get('kind'))
        role = _normalize_keyish(row.get('role'))
        path = _normalize_keyish(row.get('path'))
        if kinds and kind in kinds:
            return True
        if roles and role in roles:
            return True
        if paths and any(path and needle in path for needle in paths):
            return True
    return False


def _window_payloads(promotion: Payload) -> list[Payload]:
    for key in ('proof_windows', 'windows', 'bundles', 'runs'):
        raw = promotion.get(key)
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
    single = promotion.get('proof_window')
    if isinstance(single, dict):
        return [single]
    bundle = promotion.get('bundle')
    if isinstance(bundle, dict):
        return [bundle]
    return []


def _window_evaluation(window: Payload, *, root: Path) -> Payload:
    if 'bundle_readiness' in window and 'route_receipt' in window and 'submit_receipt' in window:
        return window
    return evaluate_chatgpt_proof_bundle_receipt(window, root=root)


def _window_summary(index: int, payload: Payload) -> Payload:
    proof_window = payload.get('proof_window') if isinstance(payload.get('proof_window'), dict) else {}
    route_receipt = payload.get('route_receipt') if isinstance(payload.get('route_receipt'), dict) else {}
    composer_receipt = payload.get('composer_receipt') if isinstance(payload.get('composer_receipt'), dict) else {}
    submit_receipt = payload.get('submit_receipt') if isinstance(payload.get('submit_receipt'), dict) else {}
    route_witness = route_receipt.get('witness') if isinstance(route_receipt.get('witness'), dict) else {}
    composer_witness = {}
    if isinstance((composer_receipt.get('route_receipt') or {}).get('witness'), dict):
        composer_witness = dict((composer_receipt.get('route_receipt') or {}).get('witness') or {})
    if isinstance(payload.get('composer_witness'), dict):
        composer_witness.update(payload.get('composer_witness') or {})
    submit_witness = {}
    nested_submit_witness = (((submit_receipt.get('composer_receipt') or {}).get('route_receipt') or {}).get('witness'))
    if isinstance(nested_submit_witness, dict):
        submit_witness = dict(nested_submit_witness)
    if isinstance(payload.get('submit_witness'), dict):
        submit_witness.update(payload.get('submit_witness') or {})
    token = None
    tokens = proof_window.get('tokens')
    if isinstance(tokens, list) and len(tokens) == 1 and isinstance(tokens[0], str):
        token = tokens[0]
    probe_signature = (
        _normalize_text(submit_witness.get('expected_exact_reply'))
        or _normalize_text(composer_witness.get('expected_probe_text'))
        or _normalize_text(submit_witness.get('latest_turn_text'))
    )
    return {
        'window_index': index,
        'bundle_readiness': payload.get('bundle_readiness'),
        'recommended_bundle_status': payload.get('recommended_bundle_status'),
        'proof_window_status': proof_window.get('status'),
        'proof_window_token': token,
        'proof_window_tokens': tokens if isinstance(tokens, list) else [],
        'auth_posture': route_witness.get('auth_posture'),
        'route_path': route_witness.get('path'),
        'matched_posture_key': ((route_receipt.get('branch_evaluation') or {}).get('matched_posture_key') if isinstance(route_receipt.get('branch_evaluation'), dict) else None),
        'composer_locator_strategy': composer_witness.get('locator_strategy'),
        'submit_method': submit_witness.get('submit_method'),
        'latest_turn_text': submit_witness.get('latest_turn_text'),
        'probe_signature': probe_signature,
        'caution_flags': payload.get('caution_flags') or [],
    }


def _stability_scorecard(promotion: Payload, window_summaries: list[Payload]) -> list[Payload]:
    artifacts = _artifact_rows(promotion)
    reviewable = [item for item in window_summaries if item.get('bundle_readiness') in {'ready-for-held', 'ready-with-caution'}]
    strict_ready = [item for item in reviewable if item.get('bundle_readiness') == 'ready-for-held']
    tokens = [item.get('proof_window_token') for item in reviewable if isinstance(item.get('proof_window_token'), str)]
    probe_signatures = [item.get('probe_signature') for item in reviewable if isinstance(item.get('probe_signature'), str)]
    return [
        {
            'check_key': 'reviewable_window_count',
            'required': True,
            'present': len(reviewable) >= 2,
            'detail': 'stronger support language should rely on at least two reviewable live proof windows rather than one lucky pass',
            'actual_count': len(reviewable),
            'minimum_required': 2,
        },
        {
            'check_key': 'strict_ready_window_present',
            'required': True,
            'present': bool(strict_ready),
            'detail': 'at least one proof window should clear the held-bundle gate without only surviving on caution',
            'actual_count': len(strict_ready),
        },
        {
            'check_key': 'distinct_window_tokens',
            'required': True,
            'present': bool(reviewable) and all(item.get('proof_window_status') == 'coherent' for item in reviewable) and len(tokens) == len(reviewable) and len(set(tokens)) == len(tokens),
            'detail': 'repeat evidence should come from distinct coherent proof windows, not one token replayed or a split mixed pass',
            'tokens': tokens,
        },
        {
            'check_key': 'shared_probe_signature',
            'required': True,
            'present': len(reviewable) >= 2 and len(probe_signatures) == len(reviewable) and len(set(probe_signatures)) == 1,
            'detail': 'repeat evidence should preserve one stable benign probe or exact readback signature across reviewable windows',
            'probe_signatures': probe_signatures,
        },
        {
            'check_key': 'auth_posture_recorded',
            'required': True,
            'present': bool(reviewable) and all(isinstance(item.get('auth_posture'), str) and str(item.get('auth_posture')).strip() for item in reviewable),
            'detail': 'auth posture should be explicit for each reviewable window because ChatGPT baseline shape can vary by login state',
        },
        {
            'check_key': 'latest_turn_readback_recorded',
            'required': True,
            'present': bool(reviewable) and all(isinstance(item.get('latest_turn_text'), str) and str(item.get('latest_turn_text')).strip() for item in reviewable),
            'detail': 'each reviewable window should preserve final latest-turn text rather than only a submit attempt',
        },
        {
            'check_key': 'locator_strategy_recorded',
            'required': True,
            'present': bool(reviewable) and all(isinstance(item.get('composer_locator_strategy'), str) and str(item.get('composer_locator_strategy')).strip() for item in reviewable),
            'detail': 'repeat evidence should preserve the composer locator strategy so future drift review can tell whether replay is stable or accidental',
        },
        {
            'check_key': 'playwright_trace_or_debug_artifact',
            'required': False,
            'present': _artifact_present(artifacts, kind_needles=('trace', 'playwright-trace', 'debug-trace'), path_needles=('trace.zip', 'playwright-trace.zip', 'trace.json'), role_needles=('playwright trace', 'debug trace')),
            'detail': 'a trace or equivalent debug artifact makes repeat failures and actionability differences reviewable instead of anecdotal',
        },
        {
            'check_key': 'locator_replay_note',
            'required': False,
            'present': _artifact_present(artifacts, kind_needles=('locator-note', 'locator-playbook', 'codegen-locator-note'), path_needles=('locator-notes.md', 'locator-playbook.md', 'codegen-locators.md'), role_needles=('locator replay note', 'codegen locator note')),
            'detail': 'a locator replay note helps future sessions explain why the repeated windows should count as one stable lane instead of brittle one-offs',
        },
    ]


def evaluate_chatgpt_promotion_stability_receipt(promotion: Payload, *, root: Path = ROOT) -> Payload:
    spec = build_chatgpt_promotion_stability_receipt(root=root)
    windows = [_window_evaluation(item, root=root) for item in _window_payloads(promotion)]
    summaries = [_window_summary(index + 1, payload) for index, payload in enumerate(windows)]
    scorecard = _stability_scorecard(promotion, summaries)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if not item.get('required') and not item.get('present')]
    reviewable = [item for item in summaries if item.get('bundle_readiness') in {'ready-for-held', 'ready-with-caution'}]

    caution_flags: list[str] = []
    if any(item.get('bundle_readiness') == 'ready-with-caution' for item in reviewable):
        caution_flags.append('mixed-held-window-quality')
    if 'playwright_trace_or_debug_artifact' in missing_optional:
        caution_flags.append('missing-trace-artifact')
    if 'locator_replay_note' in missing_optional:
        caution_flags.append('missing-locator-replay-note')

    states = {str(item.get('bundle_readiness') or '') for item in summaries}
    if not summaries:
        readiness = 'planning-only'
        reason = 'no repeated proof windows were supplied yet, so the receipt still describes promotion criteria rather than promotion evidence'
    elif not reviewable:
        if 'stop' in states:
            readiness = 'stop'
            reason = 'at least one supplied window says the shell drifted out of the plain route-first baseline, so stronger promotion should stop rather than reinterpret the branch'
        elif 'blocked-by-route' in states:
            readiness = 'blocked-by-route'
            reason = 'the supplied windows do not clear route proof, so repeat-promotion cannot begin honestly'
        elif 'blocked-by-composer' in states:
            readiness = 'blocked-by-composer'
            reason = 'the supplied windows do not clear composer writability, so repeat-promotion cannot begin honestly'
        elif 'blocked' in states:
            readiness = 'blocked'
            reason = 'the supplied windows preserve a blocked action path rather than repeated completed proof windows'
        else:
            readiness = 'hold-for-recapture'
            reason = 'some windows exist, but none are reviewable enough to count as repeated held-bundle evidence'
    elif missing_required:
        readiness = 'hold-for-recapture'
        reason = 'at least one repeat-promotion requirement is still missing, so the evidence should stay held until the repeated windows are more coherent'
    elif caution_flags:
        readiness = 'ready-with-caution'
        reason = 'the repeated windows are reviewable enough to strengthen the ChatGPT story, but the missing replay materials or caution-bearing windows should remain attached'
    else:
        readiness = 'ready-for-provisional'
        reason = 'two or more distinct coherent proof windows preserve the same benign readback signature with explicit auth posture and locator evidence, so the support story is stable enough for a stronger provisional claim'

    recommended_tier = 'investigated'
    if readiness == 'ready-for-provisional':
        recommended_tier = 'provisional'
    elif readiness == 'ready-with-caution':
        recommended_tier = 'experimental'

    if readiness == 'planning-only':
        next_action = 'capture two live route-first ChatGPT proof windows with distinct proof-window tokens before using this receipt to strengthen support language'
    elif readiness in {'blocked', 'blocked-by-route', 'blocked-by-composer', 'hold-for-recapture', 'stop'}:
        next_action = 'keep the ChatGPT support story held, recapture the weak windows honestly, and do not widen support language until the missing repeat-promotion checks are satisfied'
    elif readiness == 'ready-with-caution':
        next_action = 'strengthen the ChatGPT support story cautiously, but preserve the missing replay artifacts and caution-bearing windows alongside the record'
    else:
        next_action = 'use the repeated proof windows to strengthen the ChatGPT support record toward provisional support while keeping the proof-window receipts attached'

    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'promotion_kind': 'chatgpt-routefirst-repeatability',
        'window_evaluations': windows,
        'window_summaries': summaries,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'stability_readiness': readiness,
        'stability_readiness_reason': reason,
        'recommended_support_record_tier': recommended_tier,
        'caution_flags': caution_flags,
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: Payload) -> str:
    tiers = payload.get('stability_tiers') or []
    states = payload.get('stability_readiness_states') or []
    lines = [
        '# ChatGPT promotion stability receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- target support tier: `{payload.get('target_support_tier')}`",
        '',
        '## Stability tiers',
        '',
    ]
    for item in tiers:
        lines.append(f"- {item.get('tier')}: {item.get('rule')}")
    lines.extend(['', '## Stability readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    return '\n'.join(lines) + '\n'


def build_chatgpt_promotion_stability_receipt(*, root: Path = ROOT) -> Payload:
    proof_spec = build_chatgpt_proof_bundle_receipt(root=root)
    source_keys = sorted(dict.fromkeys([*(proof_spec.get('source_keys') or []), 'playwright-best-practices', 'playwright-test-assertions']))
    payload: Payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'grade whether repeated ChatGPT route-first proof windows are stable enough to strengthen support language beyond one held bundle',
        'target_support_tier': 'provisional',
        'design_principles': [
            'One coherent proof window can justify a held bundle, but it should not automatically imply repeatable support.',
            'Stronger support language should preserve repeated proof windows with distinct tokens, stable benign probe readback, and explicit auth posture.',
            'Replay materials such as traces and locator notes should improve confidence, but missing replay materials should warn rather than silently disappear.',
        ],
        'promotion_contract': {
            'minimum_reviewable_windows': 2,
            'acceptable_window_states': ['ready-for-held', 'ready-with-caution'],
            'required_per_window_fields': ['proof_window_token', 'auth_posture', 'composer_locator_strategy', 'latest_turn_text', 'probe_signature'],
            'recommended_global_artifacts': ['playwright-trace.zip', 'locator-notes.md'],
        },
        'stability_tiers': [
            {'tier': 'durable', 'rule': 'distinct coherent proof windows preserve one stable benign probe signature with explicit replay materials'},
            {'tier': 'reviewable', 'rule': 'the repeated windows are good enough to strengthen the support story, but some caution-bearing evidence still needs to travel with it'},
            {'tier': 'seed-only', 'rule': 'one proof window exists, but it is still a seed rather than repeatable support evidence'},
            {'tier': 'planning-only', 'rule': 'the object still describes a desired repeatability gate rather than repeated live proof windows'},
        ],
        'stability_readiness_states': [
            {'state': 'ready-for-provisional', 'rule': 'two or more distinct coherent reviewable windows preserve the same benign probe/readback signature with explicit auth posture and locator evidence'},
            {'state': 'ready-with-caution', 'rule': 'the repeated windows are reviewable enough to strengthen the support story, but caution-bearing windows or missing replay artifacts must remain attached'},
            {'state': 'hold-for-recapture', 'rule': 'repeatability evidence exists, but the repeated windows are still too thin or inconsistent to strengthen support language honestly'},
            {'state': 'blocked', 'rule': 'the supplied windows preserve blocked action paths rather than repeated successful proof windows'},
            {'state': 'blocked-by-composer', 'rule': 'repeat-promotion cannot proceed because composer writability did not clear across the supplied windows'},
            {'state': 'blocked-by-route', 'rule': 'repeat-promotion cannot proceed because route proof did not clear across the supplied windows'},
            {'state': 'planning-only', 'rule': 'the receipt still describes intended promotion discipline and has not yet been fed repeated live windows'},
            {'state': 'stop', 'rule': 'the shell drifted out of the plain route-first baseline and promotion should stop rather than reinterpret a richer branch as stable support'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'proof_bundle_receipt': 'python scripts/chatgpt-proof-bundle-receipt.py --pretty',
        },
        'source_keys': source_keys,
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_promotion_stability_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> Payload:
    payload = build_chatgpt_promotion_stability_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'chatgpt-promotion-stability-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(output_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')

    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    entry = {
        'captured_at': payload.get('generated_at'),
        'path': str(output_path),
        'summary_path': str(summary_path),
        'target_support_tier': payload.get('target_support_tier'),
        'stability_readiness_states': [item.get('state') for item in payload.get('stability_readiness_states') or []],
        'source_keys': payload.get('source_keys') or [],
    }
    entries.append(entry)
    _write_json(history_path, _history_payload(entries))
    return {
        'receipt': payload,
        'output_path': str(output_path),
        'summary_path': str(summary_path),
        'history_update': {
            'history_path': str(history_path),
            'capture_count_after_write': len(entries),
            'changed_fields': _changed_fields(previous, entry),
        },
    }


def write_root_chatgpt_promotion_stability_receipt(*, root: Path = ROOT) -> Payload:
    payload = build_chatgpt_promotion_stability_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate a ChatGPT promotion stability receipt.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')
    write_root_parser = subparsers.add_parser('write-root')
    write_root_parser.add_argument('--pretty', action='store_true')
    evaluate_parser = subparsers.add_parser('evaluate')
    evaluate_parser.add_argument('--promotion', required=True)
    evaluate_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_chatgpt_promotion_stability_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_promotion_stability_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        promotion = _read_json(Path(args.promotion))
        payload = evaluate_chatgpt_promotion_stability_receipt(promotion, root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    print(json.dumps(build_chatgpt_promotion_stability_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
