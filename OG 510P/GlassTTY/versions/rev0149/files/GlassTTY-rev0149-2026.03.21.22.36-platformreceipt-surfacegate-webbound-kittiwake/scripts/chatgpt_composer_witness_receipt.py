#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_route_witness_receipt import build_chatgpt_route_witness_receipt, evaluate_chatgpt_route_witness_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _MODULE = _load('chatgpt_route_witness_receipt', 'chatgpt_route_witness_receipt.py')
    build_chatgpt_route_witness_receipt = _MODULE.build_chatgpt_route_witness_receipt
    evaluate_chatgpt_route_witness_receipt = _MODULE.evaluate_chatgpt_route_witness_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-COMPOSER-WITNESS-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-composer-witness-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-composer-witness-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-composer-witness-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-composer-witness-receipt.py capture --output-dir validation/latest/chatgpt-composer-witness-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-composer-witness-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-composer-witness-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-composer-witness-receipt.py evaluate --witness path/to/composer-witness.json --pretty'
DEFAULT_PROBE_TEXT = 'GLASSTTY-CHECKPOINT'

Witness = dict[str, Any]


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


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _value_summary(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text[:120] if text else None
    if isinstance(value, list):
        return f'{len(value)} item(s)'
    if isinstance(value, dict):
        return f'{len(value)} key(s)'
    return str(value)


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'1', 'true', 'yes', 'y', 'present'}
    return bool(value)


def _candidate_family(witness: Witness) -> str | None:
    for key in ('composer_candidate_family', 'candidate_family', 'composer_family'):
        value = witness.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _probe_text(witness: Witness) -> str:
    for key in ('expected_probe_text', 'probe_text', 'probe_prompt'):
        value = witness.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return DEFAULT_PROBE_TEXT


def _actionability(witness: Witness) -> dict[str, bool]:
    raw = witness.get('actionability') if isinstance(witness.get('actionability'), dict) else {}
    result: dict[str, bool] = {}
    for key in ('visible', 'enabled', 'editable', 'stable', 'receives_events'):
        if key in raw:
            result[key] = _boolish(raw.get(key))
            continue
        alias = witness.get(f'actionability_{key}')
        if alias is not None:
            result[key] = _boolish(alias)
    return result


def _main_region_scoped(witness: Witness) -> bool:
    if _boolish(witness.get('main_region_scoped')):
        return True
    for key in ('candidate_scope', 'receiver_scope', 'composer_scope'):
        value = witness.get(key)
        if isinstance(value, str) and 'main' in value.lower():
            return True
    return False


def _before_state(witness: Witness) -> Any:
    for key in ('before_value', 'before_text', 'composer_before', 'pre_write_readback'):
        if _present(witness.get(key)):
            return witness.get(key)
    return None


def _after_state(witness: Witness) -> Any:
    for key in ('after_value', 'after_text', 'composer_after', 'post_write_readback', 'readback_text', 'readback_value'):
        if _present(witness.get(key)):
            return witness.get(key)
    return None


def _contains_probe(value: Any, probe: str) -> bool:
    if not probe:
        return False
    if isinstance(value, str):
        return probe in value
    if isinstance(value, list):
        return any(isinstance(item, str) and probe in item for item in value)
    return False


def _write_method(witness: Witness) -> str | None:
    for key in ('write_method', 'input_method', 'entry_method'):
        value = witness.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _fallback_accounted_for(witness: Witness, family: str | None) -> bool:
    if family in {None, '', 'accessible-textbox'}:
        return True
    rejected = witness.get('rejected_higher_priority_candidates')
    if isinstance(rejected, list) and rejected:
        return True
    notes = witness.get('fallback_notes') or witness.get('candidate_rejection_notes')
    return _present(notes)


def _field_scorecard(witness: Witness) -> list[dict[str, Any]]:
    family = _candidate_family(witness)
    actionability = _actionability(witness)
    before_state = _before_state(witness)
    after_state = _after_state(witness)
    probe = _probe_text(witness)
    core_actionability = all(actionability.get(key) for key in ('visible', 'enabled', 'editable'))
    extended_actionability = bool(actionability.get('stable')) or bool(actionability.get('receives_events'))
    checks = [
        {
            'field_key': 'candidate_family',
            'weight': 3,
            'required': True,
            'present': _present(family),
            'detail': 'a concrete composer family must be named before submit proof can be trusted',
            'value_summary': _value_summary(family),
        },
        {
            'field_key': 'locator_strategy',
            'weight': 1,
            'required': False,
            'present': _present(witness.get('locator_strategy') or witness.get('composer_locator')),
            'detail': 'the receipt should preserve how the candidate was resolved, not merely that it existed',
            'value_summary': _value_summary(witness.get('locator_strategy') or witness.get('composer_locator')),
        },
        {
            'field_key': 'main_region_scope',
            'weight': 2,
            'required': False,
            'present': _main_region_scoped(witness),
            'detail': 'composer evidence should remain anchored to the main chat lane rather than a sidebar or overlay clone',
            'value_summary': 'main region' if _main_region_scoped(witness) else None,
        },
        {
            'field_key': 'core_actionability',
            'weight': 4,
            'required': True,
            'present': core_actionability,
            'detail': 'visible, enabled, and editable together are the minimum honest write gate',
            'value_summary': ', '.join(f'{key}={actionability.get(key)}' for key in ('visible', 'enabled', 'editable') if key in actionability) or None,
        },
        {
            'field_key': 'extended_actionability',
            'weight': 1,
            'required': False,
            'present': extended_actionability,
            'detail': 'stable or receives-events evidence reduces the chance of overlay-intercepted writes',
            'value_summary': ', '.join(f'{key}={actionability.get(key)}' for key in ('stable', 'receives_events') if key in actionability) or None,
        },
        {
            'field_key': 'write_method',
            'weight': 1,
            'required': False,
            'present': _present(_write_method(witness)),
            'detail': 'fill versus type versus other entry paths should be recorded explicitly',
            'value_summary': _value_summary(_write_method(witness)),
        },
        {
            'field_key': 'before_state',
            'weight': 1,
            'required': False,
            'present': _present(before_state),
            'detail': 'a before snapshot helps explain whether the write replaced placeholder text or appended unexpectedly',
            'value_summary': _value_summary(before_state),
        },
        {
            'field_key': 'after_readback',
            'weight': 2,
            'required': True,
            'present': _present(after_state),
            'detail': 'write proof should preserve a post-write readback, not just a write attempt',
            'value_summary': _value_summary(after_state),
        },
        {
            'field_key': 'probe_echo',
            'weight': 2,
            'required': False,
            'present': _contains_probe(after_state, probe),
            'detail': 'the exact probe text appearing in readback shows that the intended prompt reached the active composer',
            'value_summary': probe if _contains_probe(after_state, probe) else None,
        },
        {
            'field_key': 'fallback_accounting',
            'weight': 1,
            'required': False,
            'present': _fallback_accounted_for(witness, family),
            'detail': 'lower-priority families should explain why stronger candidates were skipped or rejected',
            'value_summary': 'accounted' if _fallback_accounted_for(witness, family) else None,
        },
        {
            'field_key': 'overlay_notes',
            'weight': 1,
            'required': False,
            'present': _present(witness.get('overlay_labels') or witness.get('overlay_notes') or witness.get('actionability_failures')),
            'detail': 'overlay or interception notes are useful even when they did not fully block the write',
            'value_summary': _value_summary(witness.get('overlay_labels') or witness.get('overlay_notes') or witness.get('actionability_failures')),
        },
    ]
    for item in checks:
        item['earned_weight'] = item['weight'] if item['present'] else 0
    return checks


def _quality_from_score(score: int) -> str:
    if score >= 14:
        return 'strong'
    if score >= 10:
        return 'usable'
    if score >= 6:
        return 'fragile'
    return 'insufficient'


def evaluate_chatgpt_composer_witness_receipt(witness: Witness, *, root: Path = ROOT) -> dict[str, Any]:
    spec = build_chatgpt_composer_witness_receipt(root=root)
    route_receipt = evaluate_chatgpt_route_witness_receipt(witness, root=root)
    route_readiness = str(route_receipt.get('proof_readiness') or 'insufficient')
    scorecard = _field_scorecard(witness)
    score = sum(int(item.get('earned_weight') or 0) for item in scorecard)
    max_score = sum(int(item.get('weight') or 0) for item in scorecard)
    quality = _quality_from_score(score)
    present_keys = [str(item.get('field_key')) for item in scorecard if item.get('present')]
    missing_keys = [str(item.get('field_key')) for item in scorecard if not item.get('present')]
    if 'after_readback' in missing_keys and quality in {'strong', 'usable'}:
        quality = 'fragile'
    if 'candidate_family' in missing_keys or 'core_actionability' in missing_keys:
        quality = 'insufficient'
    family = _candidate_family(witness)
    actionability = _actionability(witness)
    blockers: list[str] = []
    if actionability and not actionability.get('visible', True):
        blockers.append('not-visible')
    if actionability and not actionability.get('enabled', True):
        blockers.append('disabled')
    if actionability and not actionability.get('editable', True):
        blockers.append('not-editable')
    for item in witness.get('actionability_failures') or []:
        if isinstance(item, str) and item.strip():
            blockers.append(item.strip())
    caution_flags: list[str] = []
    if route_readiness == 'ready-with-caution':
        caution_flags.append('route-caution')
    if family == 'contenteditable':
        caution_flags.append('contenteditable-fallback')
    if _boolish(witness.get('multiple_candidates')):
        caution_flags.append('multiple-candidates')
    if 'extended_actionability' in missing_keys:
        caution_flags.append('limited-actionability-evidence')
    if blockers:
        readiness = 'blocked'
        readiness_reason = 'the candidate exists, but actionability or overlay evidence says the composer is not yet safe to use'
    elif route_readiness == 'stop':
        readiness = 'stop'
        readiness_reason = 'the route witness is outside the baseline lane, so composer proof should not continue'
    elif route_readiness in {'insufficient', 'hold-for-recapture'}:
        readiness = 'blocked-by-route'
        readiness_reason = 'route evidence is not proof-ready yet, so composer evidence cannot independently promote the run'
    elif quality == 'insufficient':
        readiness = 'insufficient'
        readiness_reason = 'the composer witness is too thin to justify a write claim'
    elif quality == 'fragile':
        readiness = 'hold-for-recapture'
        readiness_reason = 'a candidate was found, but the write/readback evidence is still too thin for a durable handoff'
    elif caution_flags:
        readiness = 'ready-with-caution'
        readiness_reason = 'the composer witness is usable, but the receipt still carries fallback or caution flags that should remain attached to submit proof'
    else:
        readiness = 'ready'
        readiness_reason = 'the composer witness preserves enough scope, actionability, and readback evidence to justify submit proof'

    if readiness == 'blocked':
        recommended_next_action = 'remove or record the blocking overlay or actionability failure, then recapture visible, enabled, editable composer evidence'
    elif readiness == 'blocked-by-route':
        recommended_next_action = 'strengthen the route witness first, then re-evaluate the composer on the same baseline pass'
    elif readiness == 'hold-for-recapture':
        recommended_next_action = 'recapture the composer with main-region scope, explicit write method, and post-write readback containing the exact probe text'
    elif readiness == 'insufficient':
        recommended_next_action = 'capture a concrete composer candidate with actionability checks and a post-write readback before claiming writability'
    elif readiness == 'ready-with-caution':
        recommended_next_action = 'continue toward submit proof, but keep the fallback or caution notes attached to the bundle'
    elif readiness == 'stop':
        recommended_next_action = str(route_receipt.get('recommended_next_action') or 'return to the plain chat lane before continuing proof work')
    else:
        recommended_next_action = 'continue to submit-proof capture while preserving the composer candidate inventory and readback evidence'

    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'witness_kind': 'chatgpt-composer-witness',
        'route_receipt': route_receipt,
        'field_scorecard': scorecard,
        'score': score,
        'max_score': max_score,
        'composer_quality': quality,
        'composer_readiness': readiness,
        'readiness_reason': readiness_reason,
        'candidate_family': family,
        'actionability': actionability,
        'actionability_blockers': blockers,
        'present_field_keys': present_keys,
        'missing_field_keys': missing_keys,
        'caution_flags': caution_flags,
        'recommended_next_action': recommended_next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    states = payload.get('composer_readiness_states') or []
    tiers = payload.get('quality_tiers') or []
    lines = [
        '# ChatGPT composer witness receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- route prerequisite: `{payload.get('route_prerequisite')}`",
        '',
        '## Quality tiers',
        '',
    ]
    for item in tiers:
        lines.append(f"- {item.get('quality')}: {item.get('rule')}")
    lines.extend(['', '## Composer readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    return '\n'.join(lines) + '\n'


def build_chatgpt_composer_witness_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    route_receipt = build_chatgpt_route_witness_receipt(root=root)
    route_source_keys = [str(item) for item in route_receipt.get('source_keys') or [] if str(item).strip()]
    source_keys = sorted(dict.fromkeys(route_source_keys + ['playwright-input', 'playwright-test-assertions']))
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'grade whether a concrete ChatGPT composer witness is actually write-ready, separate from merely knowing the route looked plausible',
        'route_prerequisite': 'require a route witness that is already ready or ready-with-caution before the composer can become fully ready',
        'design_principles': [
            'A resolved composer candidate is not the same thing as a proved writable composer.',
            'Main-region scoping, actionability, and post-write readback should all be preserved so drift stays reviewable.',
            'Fallback families such as contenteditable can be valid, but they should carry explicit caution unless stronger candidates were ruled out honestly.',
        ],
        'witness_contract': {
            'required_fields': ['composer_candidate_family'],
            'recommended_fields': [
                'locator_strategy',
                'main_region_scoped',
                'actionability.visible',
                'actionability.enabled',
                'actionability.editable',
                'write_method',
                'after_value or readback_text',
            ],
        },
        'quality_tiers': [
            {'quality': 'strong', 'rule': 'main-region scope, core actionability, write method, and post-write readback are all preserved'},
            {'quality': 'usable', 'rule': 'composer evidence is sufficient to continue, though some secondary checks or fallback accounting may still be missing'},
            {'quality': 'fragile', 'rule': 'a candidate exists, but the write/readback evidence is too thin for durable handoff'},
            {'quality': 'insufficient', 'rule': 'the witness cannot honestly claim a usable composer path yet'},
        ],
        'composer_readiness_states': [
            {'state': 'ready', 'rule': 'route readiness is strong enough and the composer witness preserves scope, actionability, and readback evidence'},
            {'state': 'ready-with-caution', 'rule': 'the composer can likely be used, but fallback or caution cues should remain attached to submit proof'},
            {'state': 'hold-for-recapture', 'rule': 'a plausible candidate exists but the write or readback evidence is too thin for handoff'},
            {'state': 'blocked', 'rule': 'the candidate is blocked by actionability failure or overlay/interception evidence'},
            {'state': 'blocked-by-route', 'rule': 'composer evidence cannot promote a run whose route witness is not proof-ready'},
            {'state': 'insufficient', 'rule': 'there is not yet enough evidence to claim a writable composer'},
            {'state': 'stop', 'rule': 'the route witness says the shell is outside the baseline lane'},
        ],
        'artifact_targets': [
            'route-witness.json',
            'route-witness-receipt.json',
            'composer-candidates.json',
            'composer-before.txt',
            'composer-after.txt',
            'composer-witness-receipt.json',
        ],
        'source_keys': source_keys,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate_witness': EVALUATE_COMMAND,
            'route_receipt': 'python scripts/chatgpt-route-witness-receipt.py --pretty',
        },
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_composer_witness_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_chatgpt_composer_witness_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'chatgpt-composer-witness-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(report_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    current = {
        'captured_at': payload.get('generated_at'),
        'output_dir': str(output_dir),
        'report_path': str(report_path),
        'summary_path': str(summary_path),
        'quality_tier_count': len(payload.get('quality_tiers') or []),
        'composer_readiness_state_count': len(payload.get('composer_readiness_states') or []),
        'artifact_target_count': len(payload.get('artifact_targets') or []),
        'source_key_count': len(payload.get('source_keys') or []),
    }
    current['changed_fields'] = _changed_fields(previous, current)
    entries.append(current)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'history_update': {'path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields_vs_previous': current['changed_fields']}}


def write_root_chatgpt_composer_witness_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_composer_witness_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build and evaluate a witness-quality receipt for the ChatGPT composer before submit proof.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')
    evaluate_parser = subparsers.add_parser('evaluate')
    evaluate_parser.add_argument('--witness', required=True)
    subparsers.add_parser('write-root')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_chatgpt_composer_witness_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        payload = evaluate_chatgpt_composer_witness_receipt(_read_json(Path(args.witness)), root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_composer_witness_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    print(json.dumps(build_chatgpt_composer_witness_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
