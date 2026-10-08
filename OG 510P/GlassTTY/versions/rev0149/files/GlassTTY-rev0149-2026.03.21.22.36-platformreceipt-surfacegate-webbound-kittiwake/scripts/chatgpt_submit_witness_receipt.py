#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_composer_witness_receipt import build_chatgpt_composer_witness_receipt, evaluate_chatgpt_composer_witness_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _MODULE = _load('chatgpt_composer_witness_receipt', 'chatgpt_composer_witness_receipt.py')
    build_chatgpt_composer_witness_receipt = _MODULE.build_chatgpt_composer_witness_receipt
    evaluate_chatgpt_composer_witness_receipt = _MODULE.evaluate_chatgpt_composer_witness_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-SUBMIT-WITNESS-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-submit-witness-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-submit-witness-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-submit-witness-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-submit-witness-receipt.py capture --output-dir validation/latest/chatgpt-submit-witness-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-submit-witness-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-submit-witness-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-submit-witness-receipt.py evaluate --witness path/to/submit-witness.json --pretty'
DEFAULT_EXPECTED_REPLY = 'GLASSTTY-CHECKPOINT'

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


def _submit_candidate_family(witness: Witness) -> str | None:
    for key in ('submit_candidate_family', 'submit_family', 'dispatch_candidate_family'):
        value = witness.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _submit_method(witness: Witness) -> str | None:
    for key in ('submit_method', 'dispatch_method', 'submit_trigger'):
        value = witness.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _submit_actionability(witness: Witness) -> dict[str, bool]:
    raw = witness.get('submit_actionability') if isinstance(witness.get('submit_actionability'), dict) else {}
    result: dict[str, bool] = {}
    for key in ('visible', 'enabled', 'stable', 'receives_events', 'composer_focused'):
        if key in raw:
            result[key] = _boolish(raw.get(key))
            continue
        alias = witness.get(f'submit_actionability_{key}')
        if alias is not None:
            result[key] = _boolish(alias)
    return result


def _submit_attempt_evidence(witness: Witness) -> Any:
    for key in ('submit_attempt', 'submit_attempted', 'dispatch_recorded', 'submit_timestamp', 'submit_event', 'dispatch_timestamp'):
        value = witness.get(key)
        if _present(value):
            return value
    return None


def _composer_state_change(witness: Witness) -> Any:
    for key in ('composer_cleared_after_submit', 'composer_after_submit', 'post_submit_composer_state', 'submit_side_effect'):
        value = witness.get(key)
        if _present(value):
            return value
    return None


def _generation_cues(witness: Witness) -> Any:
    for key in ('generation_cues', 'streaming_cues', 'response_started', 'streaming_state', 'stop_button_visible'):
        value = witness.get(key)
        if _present(value):
            return value
    return None


def _completion_cues(witness: Witness) -> Any:
    for key in ('completion_cues', 'response_completed', 'latest_turn_complete', 'response_actions_visible', 'final_stable_readback'):
        value = witness.get(key)
        if _present(value):
            return value
    return None


def _latest_turn_text(witness: Witness) -> Any:
    for key in ('latest_turn_text', 'assistant_latest_turn_text', 'latest_response_text', 'latest_turn_readback'):
        value = witness.get(key)
        if _present(value):
            return value
    return None


def _main_conversation_scoped(witness: Witness) -> bool:
    if _boolish(witness.get('main_region_scoped')):
        return True
    for key in ('latest_turn_scope', 'conversation_scope', 'response_scope'):
        value = witness.get(key)
        if isinstance(value, str) and 'main' in value.lower():
            return True
    return False


def _expected_reply(witness: Witness) -> str:
    for key in ('expected_exact_reply', 'expected_reply', 'expected_probe_text', 'probe_text', 'probe_prompt'):
        value = witness.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return DEFAULT_EXPECTED_REPLY


def _normalize_text(value: str) -> str:
    return ' '.join(value.strip().strip('"\'').split())


def _contains_expected(value: Any, expected: str) -> bool:
    if not expected:
        return False
    if isinstance(value, str):
        return expected in value
    if isinstance(value, list):
        return any(isinstance(item, str) and expected in item for item in value)
    return False


def _exact_reply_match(value: Any, expected: str) -> bool:
    if not expected:
        return False
    if isinstance(value, str):
        return _normalize_text(value) == _normalize_text(expected)
    if isinstance(value, list):
        return any(isinstance(item, str) and _normalize_text(item) == _normalize_text(expected) for item in value)
    return False


def _has_timeline(witness: Witness) -> bool:
    for key in ('generation_timeline', 'timeline_events', 'submit_timestamp', 'response_completed_at', 'latest_turn_timestamp'):
        if _present(witness.get(key)):
            return True
    return False


def _overlay_notes(witness: Witness) -> Any:
    for key in ('submit_blockers', 'overlay_notes', 'overlay_labels', 'intercept_notes'):
        value = witness.get(key)
        if _present(value):
            return value
    return None


def _field_scorecard(witness: Witness) -> list[dict[str, Any]]:
    family = _submit_candidate_family(witness)
    method = _submit_method(witness)
    actionability = _submit_actionability(witness)
    latest_turn = _latest_turn_text(witness)
    expected = _expected_reply(witness)
    keyboard_path = family == 'keyboard-submit' or (isinstance(method, str) and 'keyboard' in method.lower()) or (isinstance(method, str) and 'enter' in method.lower())
    actionability_ok = bool(actionability.get('composer_focused')) if keyboard_path else bool(actionability.get('visible')) and bool(actionability.get('enabled'))
    extended_actionability = bool(actionability.get('stable')) or bool(actionability.get('receives_events'))
    return [
        {'field_key': 'submit_candidate_family', 'weight': 2, 'required': True, 'present': _present(family), 'detail': 'a concrete submit family should be preserved so click and keyboard fallback paths are reviewable', 'value_summary': _value_summary(family)},
        {'field_key': 'submit_method', 'weight': 1, 'required': False, 'present': _present(method), 'detail': 'the receipt should record whether submission happened by button click, keyboard, or another path', 'value_summary': _value_summary(method)},
        {'field_key': 'submit_actionability', 'weight': 2, 'required': True, 'present': actionability_ok, 'detail': 'submit proof should preserve whether the dispatch path was actually actionable', 'value_summary': _value_summary(actionability)},
        {'field_key': 'extended_submit_actionability', 'weight': 1, 'required': False, 'present': extended_actionability, 'detail': 'stable or receives-events evidence makes a dispatch path less fragile under review', 'value_summary': _value_summary(actionability)},
        {'field_key': 'submit_attempt', 'weight': 2, 'required': True, 'present': _present(_submit_attempt_evidence(witness)), 'detail': 'submit proof should preserve an actual dispatch attempt, not just the existence of a control', 'value_summary': _value_summary(_submit_attempt_evidence(witness))},
        {'field_key': 'composer_state_change', 'weight': 1, 'required': False, 'present': _present(_composer_state_change(witness)), 'detail': 'composer clear or pending-state evidence strengthens the claim that submit was really sent to the active lane', 'value_summary': _value_summary(_composer_state_change(witness))},
        {'field_key': 'generation_cues', 'weight': 1, 'required': False, 'present': _present(_generation_cues(witness)), 'detail': 'a transient generation cue helps connect submit evidence to response production', 'value_summary': _value_summary(_generation_cues(witness))},
        {'field_key': 'completion_cues', 'weight': 2, 'required': True, 'present': _present(_completion_cues(witness)), 'detail': 'submit proof needs a stable completion cue, not only a transient streaming moment', 'value_summary': _value_summary(_completion_cues(witness))},
        {'field_key': 'main_conversation_scope', 'weight': 1, 'required': False, 'present': _main_conversation_scoped(witness), 'detail': 'latest-turn readback should stay anchored to the main conversation region', 'value_summary': _value_summary(witness.get('latest_turn_scope') or witness.get('conversation_scope') or witness.get('response_scope'))},
        {'field_key': 'latest_turn_readback', 'weight': 2, 'required': True, 'present': _present(latest_turn), 'detail': 'the receipt should preserve the latest visible assistant turn or equivalent final readback', 'value_summary': _value_summary(latest_turn)},
        {'field_key': 'expected_reply_match', 'weight': 2, 'required': False, 'present': _contains_expected(latest_turn, expected), 'detail': 'latest-turn readback should still preserve the benign expected reply text', 'value_summary': _value_summary(expected)},
        {'field_key': 'exact_reply_match', 'weight': 1, 'required': False, 'present': _exact_reply_match(latest_turn, expected), 'detail': 'an exact benign reply match makes the submit/result proof especially durable', 'value_summary': _value_summary(expected)},
        {'field_key': 'timeline', 'weight': 1, 'required': False, 'present': _has_timeline(witness), 'detail': 'submit proof is stronger when the capture preserves a minimal timeline', 'value_summary': _value_summary(witness.get('generation_timeline') or witness.get('timeline_events'))},
    ]


def evaluate_chatgpt_submit_witness_receipt(witness: Witness, *, root: Path = ROOT) -> dict[str, Any]:
    spec = build_chatgpt_submit_witness_receipt(root=root)
    composer_receipt = evaluate_chatgpt_composer_witness_receipt(witness, root=root)
    composer_readiness = str(composer_receipt.get('composer_readiness') or 'insufficient')
    route_receipt = composer_receipt.get('route_receipt') if isinstance(composer_receipt.get('route_receipt'), dict) else {}
    route_readiness = str(route_receipt.get('proof_readiness') or 'insufficient')

    scorecard = _field_scorecard(witness)
    score = sum(int(item['weight']) for item in scorecard if item['present'])
    max_score = sum(int(item['weight']) for item in scorecard)
    present_keys = [item['field_key'] for item in scorecard if item['present']]
    missing_keys = [item['field_key'] for item in scorecard if item.get('required') and not item['present']]
    quality = 'strong' if score >= 14 else 'usable' if score >= 10 else 'fragile' if score >= 5 else 'insufficient'

    family = _submit_candidate_family(witness)
    method = _submit_method(witness)
    actionability = _submit_actionability(witness)
    blockers: list[str] = []
    caution_flags: list[str] = []

    if family != 'keyboard-submit' and actionability and not actionability.get('visible', True):
        blockers.append('submit-not-visible')
    if family != 'keyboard-submit' and actionability and not actionability.get('enabled', True):
        blockers.append('submit-disabled')
    if family == 'keyboard-submit' and actionability and not actionability.get('composer_focused', True):
        blockers.append('composer-not-focused')
    if actionability and not actionability.get('receives_events', True):
        blockers.append('submit-not-receiving-events')
    for item in witness.get('submit_blockers') or []:
        if isinstance(item, str) and item not in blockers:
            blockers.append(item)
    if _present(_overlay_notes(witness)):
        blockers.append('overlay-or-intercept')

    if family == 'keyboard-submit' or (isinstance(method, str) and ('keyboard' in method.lower() or 'enter' in method.lower())):
        caution_flags.append('keyboard-submit-fallback')
    if not _main_conversation_scoped(witness):
        caution_flags.append('latest-turn-scope-not-explicit')
    if not _has_timeline(witness):
        caution_flags.append('timeline-missing')
    if not _exact_reply_match(_latest_turn_text(witness), _expected_reply(witness)):
        caution_flags.append('reply-not-exact')

    if route_readiness == 'stop':
        readiness = 'stop'
        readiness_reason = 'the route witness is outside the baseline lane, so submit proof should not continue'
    elif composer_readiness == 'blocked-by-route' or route_readiness in {'insufficient', 'hold-for-recapture'}:
        readiness = 'blocked-by-route'
        readiness_reason = 'route evidence is not proof-ready yet, so submit proof cannot honestly continue'
    elif composer_readiness in {'blocked', 'hold-for-recapture', 'insufficient'}:
        readiness = 'blocked-by-composer'
        readiness_reason = 'submit proof depends on a composer witness that is not yet honest enough to hand off'
    elif blockers:
        readiness = 'blocked'
        readiness_reason = 'a submit affordance or dispatch path exists, but actionability or interception evidence says it is not yet safe to trust'
    elif quality == 'insufficient':
        readiness = 'insufficient'
        readiness_reason = 'the submit/result witness is too thin to justify a completed turn claim'
    elif quality == 'fragile':
        readiness = 'hold-for-recapture'
        readiness_reason = 'submission evidence exists, but dispatch, completion, or final readback proof is still too thin for a durable handoff'
    elif caution_flags:
        readiness = 'ready-with-caution'
        readiness_reason = 'the submit/result witness is usable, but the receipt still carries fallback or thin-evidence cautions that should remain attached to the bundle'
    else:
        readiness = 'ready'
        readiness_reason = 'the witness preserves prerequisites, dispatch, completion, and latest-turn readback strongly enough to justify first-turn submit proof'

    if readiness == 'blocked-by-route':
        recommended_next_action = 'strengthen the route witness first, then recapture composer and submit evidence on the same pass'
    elif readiness == 'blocked-by-composer':
        recommended_next_action = 'repair composer writability or readback proof before claiming submit success'
    elif readiness == 'blocked':
        recommended_next_action = 'record the blocking submit state or overlay, then recapture a safe dispatch attempt with actionability evidence'
    elif readiness == 'hold-for-recapture':
        recommended_next_action = 'recapture the run with an explicit dispatch record, stable completion cue, and final latest-turn readback in the main conversation region'
    elif readiness == 'insufficient':
        recommended_next_action = 'capture a concrete submit path, generation/completion cues, and latest-turn readback before claiming the turn finished'
    elif readiness == 'ready-with-caution':
        recommended_next_action = 'continue toward bundle promotion, but keep the fallback and thin-evidence cautions attached to submit proof'
    elif readiness == 'stop':
        recommended_next_action = str(route_receipt.get('recommended_next_action') or 'return to the plain chat lane before continuing proof work')
    else:
        recommended_next_action = 'attach the submit/result receipt to the first proof bundle alongside route and composer receipts'

    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'witness_kind': 'chatgpt-submit-witness',
        'composer_receipt': composer_receipt,
        'route_receipt': route_receipt,
        'field_scorecard': scorecard,
        'score': score,
        'max_score': max_score,
        'submit_quality': quality,
        'submit_readiness': readiness,
        'readiness_reason': readiness_reason,
        'submit_candidate_family': family,
        'submit_method': method,
        'submit_actionability': actionability,
        'submit_blockers': blockers,
        'expected_reply': _expected_reply(witness),
        'present_field_keys': present_keys,
        'missing_field_keys': missing_keys,
        'caution_flags': caution_flags,
        'recommended_next_action': recommended_next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    states = payload.get('submit_readiness_states') or []
    tiers = payload.get('quality_tiers') or []
    lines = ['# ChatGPT submit witness receipt', '', f"- generated_at: `{payload.get('generated_at')}`", f"- upstream prerequisites: `{', '.join(payload.get('upstream_prerequisites') or [])}`", '', '## Quality tiers', '']
    for item in tiers:
        lines.append(f"- {item.get('quality')}: {item.get('rule')}")
    lines.extend(['', '## Submit readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    return '\n'.join(lines) + '\n'


def build_chatgpt_submit_witness_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    composer_receipt = build_chatgpt_composer_witness_receipt(root=root)
    composer_source_keys = [str(item) for item in composer_receipt.get('source_keys') or [] if str(item).strip()]
    source_keys = sorted(dict.fromkeys(composer_source_keys + ['playwright-actionability', 'playwright-test-assertions']))
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'grade whether a concrete ChatGPT submit-and-latest-turn witness is actually proof-ready, separate from merely proving route and composer readiness',
        'upstream_prerequisites': ['route witness ready or ready-with-caution', 'composer witness ready or ready-with-caution'],
        'design_principles': [
            'Submitting a prompt is different from proving that a stable assistant turn was produced and read back from the intended lane.',
            'The first proof should preserve dispatch evidence, generation or completion evidence, and final latest-turn readback rather than trusting any one cue alone.',
            'Keyboard-submit and other fallbacks can be valid, but they should carry explicit caution unless a direct submit control was ruled out honestly.',
        ],
        'witness_contract': {'required_fields': ['submit_candidate_family'], 'recommended_fields': ['submit_method', 'submit_actionability.enabled or submit_actionability.composer_focused', 'submit_attempt', 'completion_cues', 'latest_turn_text']},
        'quality_tiers': [
            {'quality': 'strong', 'rule': 'dispatch, stable completion, main-lane latest-turn readback, and exact benign-reply match are all preserved'},
            {'quality': 'usable', 'rule': 'submit/result evidence is sufficient to continue, though some secondary timing or fallback details may still be missing'},
            {'quality': 'fragile', 'rule': 'submission evidence exists, but the proof is too thin to trust as a durable handoff without recapture'},
            {'quality': 'insufficient', 'rule': 'the witness cannot honestly claim a completed submit-and-readback path yet'},
        ],
        'submit_readiness_states': [
            {'state': 'ready', 'rule': 'route and composer prerequisites passed and the submit/result witness preserves dispatch, completion, and latest-turn readback strongly enough to hand off'},
            {'state': 'ready-with-caution', 'rule': 'submit proof is usable, but fallback or thin-evidence cautions must remain attached to the bundle'},
            {'state': 'hold-for-recapture', 'rule': 'a submit/result path exists, but the evidence is too thin to survive drift review without recapture'},
            {'state': 'blocked', 'rule': 'submit actionability or interception evidence says the current dispatch path should not be trusted'},
            {'state': 'blocked-by-composer', 'rule': 'submit proof cannot proceed honestly because composer writability or readback has not cleared its own gate'},
            {'state': 'blocked-by-route', 'rule': 'submit proof cannot proceed honestly because route evidence is still too weak or off-lane'},
            {'state': 'insufficient', 'rule': 'the witness is missing core submit or latest-turn evidence and should not be treated as proof'},
            {'state': 'stop', 'rule': 'the shell has drifted out of the baseline lane and the proof should stop rather than reinterpret a richer branch'},
        ],
        'expected_reply_policy': {'exact_reply': DEFAULT_EXPECTED_REPLY, 'why': 'The exact-match benign probe keeps first submit/readback proof low-ambiguity and easy to audit.'},
        'commands': {'report': REPORT_COMMAND, 'capture_latest': CAPTURE_COMMAND, 'capture_history': HISTORY_COMMAND, 'write_root': WRITE_ROOT_COMMAND, 'evaluate': EVALUATE_COMMAND, 'composer_receipt': 'python scripts/chatgpt-composer-witness-receipt.py --pretty'},
        'source_keys': source_keys,
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_submit_witness_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_chatgpt_submit_witness_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'chatgpt-submit-witness-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(output_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')

    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    entry = {
        'captured_at': payload.get('generated_at'),
        'path': str(output_path),
        'summary_path': str(summary_path),
        'quality_tiers': [item.get('quality') for item in payload.get('quality_tiers') or []],
        'submit_readiness_states': [item.get('state') for item in payload.get('submit_readiness_states') or []],
        'source_keys': payload.get('source_keys') or [],
    }
    entries.append(entry)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'output_path': str(output_path), 'summary_path': str(summary_path), 'history_update': {'history_path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields': _changed_fields(previous, entry)}}


def write_root_chatgpt_submit_witness_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_submit_witness_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate a ChatGPT submit witness receipt.')
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
    evaluate_parser.add_argument('--witness', required=True)
    evaluate_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_chatgpt_submit_witness_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_submit_witness_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        witness = _read_json(Path(args.witness))
        payload = evaluate_chatgpt_submit_witness_receipt(witness, root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    print(json.dumps(build_chatgpt_submit_witness_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
