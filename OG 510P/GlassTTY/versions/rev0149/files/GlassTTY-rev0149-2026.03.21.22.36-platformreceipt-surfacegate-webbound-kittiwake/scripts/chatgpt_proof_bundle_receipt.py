#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_route_witness_receipt import build_chatgpt_route_witness_receipt, evaluate_chatgpt_route_witness_receipt
    from chatgpt_composer_witness_receipt import build_chatgpt_composer_witness_receipt, evaluate_chatgpt_composer_witness_receipt
    from chatgpt_submit_witness_receipt import build_chatgpt_submit_witness_receipt, evaluate_chatgpt_submit_witness_receipt
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _ROUTE = _load('chatgpt_route_witness_receipt', 'chatgpt_route_witness_receipt.py')
    _COMPOSER = _load('chatgpt_composer_witness_receipt', 'chatgpt_composer_witness_receipt.py')
    _SUBMIT = _load('chatgpt_submit_witness_receipt', 'chatgpt_submit_witness_receipt.py')
    build_chatgpt_route_witness_receipt = _ROUTE.build_chatgpt_route_witness_receipt
    evaluate_chatgpt_route_witness_receipt = _ROUTE.evaluate_chatgpt_route_witness_receipt
    build_chatgpt_composer_witness_receipt = _COMPOSER.build_chatgpt_composer_witness_receipt
    evaluate_chatgpt_composer_witness_receipt = _COMPOSER.evaluate_chatgpt_composer_witness_receipt
    build_chatgpt_submit_witness_receipt = _SUBMIT.build_chatgpt_submit_witness_receipt
    evaluate_chatgpt_submit_witness_receipt = _SUBMIT.evaluate_chatgpt_submit_witness_receipt

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-PROOF-BUNDLE-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-proof-bundle-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-proof-bundle-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-proof-bundle-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-proof-bundle-receipt.py capture --output-dir validation/latest/chatgpt-proof-bundle-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-proof-bundle-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-proof-bundle-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-proof-bundle-receipt.py evaluate --bundle path/to/proof-bundle.json --pretty'

Bundle = dict[str, Any]


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


def _normalize_keyish(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace('_', '-').replace(' ', '-')
    return normalized or None


def _merge_dicts(*parts: Any) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for part in parts:
        if isinstance(part, dict):
            merged.update(part)
    return merged


def _witness(bundle: Bundle, *keys: str) -> dict[str, Any]:
    for key in keys:
        value = bundle.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _artifact_rows(bundle: Bundle) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ('artifact_refs', 'artifacts', 'bundle_artifacts'):
        raw = bundle.get(key)
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


def _capture_window_tokens(bundle: Bundle) -> list[str]:
    tokens: list[str] = []
    for value in [bundle.get('capture_window_id'), bundle.get('proof_window_id'), bundle.get('session_id'), bundle.get('run_id')]:
        if isinstance(value, str) and value.strip():
            tokens.append(value.strip())
    for witness in (_witness(bundle, 'route_witness', 'route'), _witness(bundle, 'composer_witness', 'composer'), _witness(bundle, 'submit_witness', 'submit')):
        for key in ('capture_window_id', 'proof_window_id', 'session_id', 'run_id'):
            value = witness.get(key)
            if isinstance(value, str) and value.strip():
                tokens.append(value.strip())
    return tokens


def _proof_window_status(bundle: Bundle) -> dict[str, Any]:
    tokens = _capture_window_tokens(bundle)
    unique = list(dict.fromkeys(tokens))
    if not unique:
        return {'status': 'missing', 'tokens': [], 'detail': 'no shared capture-window token was preserved across the proof window'}
    if len(unique) == 1:
        return {'status': 'coherent', 'tokens': unique, 'detail': 'all preserved window tokens agree on one proof window'}
    return {'status': 'split', 'tokens': unique, 'detail': 'multiple capture-window tokens were preserved, so the proof window may span unrelated passes'}


def _live_context(bundle: Bundle) -> bool:
    for key in ('live_capture', 'official_surface_live', 'captured_on_live_surface'):
        if bool(bundle.get(key)):
            return True
    for key in ('browser_lane', 'capture_lane', 'lane'):
        value = bundle.get(key)
        if isinstance(value, str) and value.strip().lower() == 'chromium-live':
            return True
    return False


def _bundle_scorecard(bundle: Bundle, route_receipt: dict[str, Any], composer_receipt: dict[str, Any], submit_receipt: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = _artifact_rows(bundle)
    window = _proof_window_status(bundle)
    return [
        {'check_key': 'live_context', 'required': True, 'present': _live_context(bundle), 'detail': 'the first real bundle should explicitly say it came from a live official-surface run such as chromium-live'},
        {'check_key': 'route_ready', 'required': True, 'present': str(route_receipt.get('proof_readiness') or '') in {'ready', 'ready-with-caution'}, 'detail': 'bundle promotion depends on a route witness that already cleared its own proof gate'},
        {'check_key': 'composer_ready', 'required': True, 'present': str(composer_receipt.get('composer_readiness') or '') in {'ready', 'ready-with-caution'}, 'detail': 'bundle promotion depends on a composer witness that already proved writability honestly'},
        {'check_key': 'submit_ready', 'required': True, 'present': str(submit_receipt.get('submit_readiness') or '') in {'ready', 'ready-with-caution'}, 'detail': 'bundle promotion depends on a submit/result witness that already proved dispatch and latest-turn readback honestly'},
        {'check_key': 'surface_screenshot', 'required': True, 'present': _artifact_present(artifacts, kind_needles=('surface-screenshot', 'screenshot'), path_needles=('surface-screenshot.png', 'screenshot.png')), 'detail': 'the first route bundle should preserve one screenshot of the landed official surface'},
        {'check_key': 'receiver_posture', 'required': True, 'present': _artifact_present(artifacts, kind_needles=('receiver-posture',), path_needles=('receiver-posture.md',), role_needles=('receiver posture note',)), 'detail': 'receiver posture should be preserved so a gated or overlay-blocked route is reviewable later'},
        {'check_key': 'composer_candidates', 'required': True, 'present': _artifact_present(artifacts, kind_needles=('composer-candidates',), path_needles=('composer-candidates.json',)), 'detail': 'the bundle should preserve the winning composer path and at least one failed candidate note'},
        {'check_key': 'submit_evidence', 'required': True, 'present': _artifact_present(artifacts, kind_needles=('submit-evidence',), path_needles=('submit-evidence.json',)), 'detail': 'the bundle should preserve a dispatch artifact rather than only the receipt summary'},
        {'check_key': 'latest_turn', 'required': True, 'present': _artifact_present(artifacts, kind_needles=('latest-turn',), path_needles=('latest-turn.txt',)), 'detail': 'the bundle should preserve the final stable latest-turn readback, not only a receipt verdict'},
        {'check_key': 'generation_timeline', 'required': False, 'present': _artifact_present(artifacts, kind_needles=('generation-timeline',), path_needles=('generation-timeline.json',)), 'detail': 'generation timeline evidence strengthens a bundle by keeping transient and stable cues separate'},
        {'check_key': 'probe_prompt', 'required': False, 'present': _artifact_present(artifacts, kind_needles=('probe-prompt',), path_needles=('probe-prompt.txt',)), 'detail': 'preserving the benign probe prompt makes later exact-match reply review easier'},
        {'check_key': 'proof_window_token', 'required': False, 'present': window['status'] == 'coherent', 'detail': window['detail'], 'value_summary': ', '.join(window['tokens']) if window['tokens'] else None},
    ]


def evaluate_chatgpt_proof_bundle_receipt(bundle: Bundle, *, root: Path = ROOT) -> dict[str, Any]:
    spec = build_chatgpt_proof_bundle_receipt(root=root)
    route_witness = _witness(bundle, 'route_witness', 'route')
    composer_only = _witness(bundle, 'composer_witness', 'composer')
    submit_only = _witness(bundle, 'submit_witness', 'submit')
    composer_witness = _merge_dicts(route_witness, composer_only)
    submit_witness = _merge_dicts(route_witness, composer_only, submit_only)

    route_receipt = evaluate_chatgpt_route_witness_receipt(route_witness, root=root)
    composer_receipt = evaluate_chatgpt_composer_witness_receipt(composer_witness, root=root)
    submit_receipt = evaluate_chatgpt_submit_witness_receipt(submit_witness, root=root)
    scorecard = _bundle_scorecard(bundle, route_receipt, composer_receipt, submit_receipt)
    present_checks = [item['check_key'] for item in scorecard if item.get('present')]
    missing_required = [item['check_key'] for item in scorecard if item.get('required') and not item.get('present')]
    missing_optional = [item['check_key'] for item in scorecard if (not item.get('required')) and not item.get('present')]

    route_readiness = str(route_receipt.get('proof_readiness') or 'insufficient')
    composer_readiness = str(composer_receipt.get('composer_readiness') or 'insufficient')
    submit_readiness = str(submit_receipt.get('submit_readiness') or 'insufficient')
    proof_window = _proof_window_status(bundle)

    caution_flags: list[str] = []
    for source in (route_receipt, composer_receipt, submit_receipt):
        for item in source.get('caution_flags') or []:
            if isinstance(item, str) and item not in caution_flags:
                caution_flags.append(item)
    if proof_window['status'] == 'missing':
        caution_flags.append('missing-proof-window-token')
    elif proof_window['status'] == 'split':
        caution_flags.append('split-proof-window-token')
    if 'generation_timeline' in missing_optional:
        caution_flags.append('missing-generation-timeline-artifact')
    if 'probe_prompt' in missing_optional:
        caution_flags.append('missing-probe-prompt-artifact')

    if 'stop' in {route_readiness, composer_readiness, submit_readiness}:
        readiness = 'stop'
        reason = 'the route-first proof drifted into a richer or off-lane shell, so the bundle should stop rather than reinterpret the run'
    elif not _live_context(bundle) and not _artifact_rows(bundle) and not route_witness and not composer_only and not submit_only:
        readiness = 'planning-only'
        reason = 'the bundle still looks like a planning object because it preserves no live-capture context, no witness payloads, and no first-proof artifacts'
    elif submit_readiness == 'blocked-by-route' or composer_readiness == 'blocked-by-route':
        readiness = 'blocked-by-route'
        reason = 'the bundle cannot be promoted because the route witness did not clear its own gate honestly'
    elif submit_readiness == 'blocked-by-composer':
        readiness = 'blocked-by-composer'
        reason = 'the bundle cannot be promoted because the composer witness did not clear its own gate honestly'
    elif submit_readiness == 'blocked' or composer_readiness == 'blocked':
        readiness = 'blocked'
        reason = 'the bundle preserves a blocked action path rather than a safe proof window'
    elif not _live_context(bundle) and not _artifact_rows(bundle):
        readiness = 'hold-for-recapture'
        reason = 'the bundle preserves some witness data, but it is still missing explicit live-capture context and first-proof artifacts'
    elif submit_readiness in {'hold-for-recapture', 'insufficient'} or composer_readiness in {'hold-for-recapture', 'insufficient'} or route_readiness in {'hold-for-recapture', 'insufficient'}:
        readiness = 'hold-for-recapture'
        reason = 'one of the upstream receipts is still too thin, so the bundle should hold for recapture instead of promoting partial proof'
    elif missing_required:
        readiness = 'hold-for-recapture'
        reason = 'the upstream receipts may be acceptable, but the named support bundle is missing one or more first-proof artifacts needed for durable review'
    elif caution_flags:
        readiness = 'ready-with-caution'
        reason = 'the bundle is coherent enough to move into a held review state, but caution flags and thin secondaries should remain attached'
    else:
        readiness = 'ready-for-held'
        reason = 'route, composer, and submit receipts all cleared honestly and the same proof window preserves the core artifacts needed for a held bundle'

    recommended_bundle_status = 'hold' if readiness in {'ready-for-held', 'ready-with-caution'} else 'candidate'

    if readiness == 'planning-only':
        next_action = 'capture one live chromium-live proof window with route screenshot, receiver posture, composer candidates, submit evidence, generation timeline, and latest-turn readback before trying to promote the bundle'
    elif readiness == 'hold-for-recapture':
        next_action = 'recapture the first proof window so the missing upstream receipt or missing artifact families are attached to one named live bundle'
    elif readiness == 'blocked-by-route':
        next_action = str(route_receipt.get('recommended_next_action') or 'repair the route witness first, then rebuild the bundle from the corrected proof window')
    elif readiness == 'blocked-by-composer':
        next_action = str(composer_receipt.get('recommended_next_action') or 'repair composer writability proof, then rebuild the bundle from that same pass')
    elif readiness == 'blocked':
        next_action = str(submit_receipt.get('recommended_next_action') or 'preserve the blocked submit path and recapture a safe dispatch path before promoting the bundle')
    elif readiness == 'stop':
        next_action = str(route_receipt.get('recommended_next_action') or 'return to the plain ChatGPT route before packaging a promotion bundle')
    elif readiness == 'ready-with-caution':
        next_action = 'attach the bundle to a held review state, but preserve the caution flags and missing-secondary notes inside the bundle summary'
    else:
        next_action = 'attach this proof window to a stronger held ChatGPT support bundle and keep publication claims capped until live review confirms the same evidence remains current'

    return {
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'bundle_kind': 'chatgpt-routefirst-proof-window',
        'route_receipt': route_receipt,
        'composer_receipt': composer_receipt,
        'submit_receipt': submit_receipt,
        'proof_window': proof_window,
        'field_scorecard': scorecard,
        'present_check_keys': present_checks,
        'missing_required_check_keys': missing_required,
        'missing_optional_check_keys': missing_optional,
        'bundle_readiness': readiness,
        'bundle_readiness_reason': reason,
        'recommended_bundle_status': recommended_bundle_status,
        'caution_flags': caution_flags,
        'recommended_next_action': next_action,
        'source_keys': spec.get('source_keys') or [],
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    states = payload.get('bundle_readiness_states') or []
    tiers = payload.get('bundle_quality_tiers') or []
    lines = ['# ChatGPT proof bundle receipt', '', f"- generated_at: `{payload.get('generated_at')}`", f"- target bundle state: `{payload.get('target_bundle_state')}`", '', '## Bundle quality tiers', '']
    for item in tiers:
        lines.append(f"- {item.get('quality')}: {item.get('rule')}")
    lines.extend(['', '## Bundle readiness states', ''])
    for item in states:
        lines.append(f"- {item.get('state')}: {item.get('rule')}")
    return '\n'.join(lines) + '\n'


def build_chatgpt_proof_bundle_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    route_spec = build_chatgpt_route_witness_receipt(root=root)
    composer_spec = build_chatgpt_composer_witness_receipt(root=root)
    submit_spec = build_chatgpt_submit_witness_receipt(root=root)
    source_keys = sorted(dict.fromkeys([str(item) for spec in (route_spec, composer_spec, submit_spec) for item in (spec.get('source_keys') or []) if str(item).strip()]))
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'grade whether one whole ChatGPT route-first proof window is coherent enough to attach to a stronger held support bundle, rather than promoting route, composer, and submit receipts in isolation',
        'target_bundle_state': 'hold',
        'design_principles': [
            'A route-first proof window is stronger than three isolated receipts only when the artifacts and capture context stay tied to the same live pass.',
            'Bundle promotion should preserve the route screenshot, receiver posture, composer candidate record, submit evidence, and final latest-turn readback so future drift review can replay the claim.',
            'Missing proof-window identity or missing secondaries should degrade bundle readiness instead of being silently ignored once per-step receipts happen to pass.',
        ],
        'bundle_contract': {
            'required_witnesses': ['route_witness', 'composer_witness', 'submit_witness'],
            'required_artifacts': ['surface-screenshot.png', 'receiver-posture.md', 'composer-candidates.json', 'submit-evidence.json', 'latest-turn.txt'],
            'recommended_artifacts': ['probe-prompt.txt', 'generation-timeline.json'],
            'live_context': 'chromium-live or an equivalent explicit live official-surface marker',
        },
        'bundle_quality_tiers': [
            {'quality': 'coherent', 'rule': 'all three upstream receipts clear honestly, the live proof window is explicit, and the core bundle artifacts are preserved'},
            {'quality': 'reviewable', 'rule': 'the bundle is usable for held review, but caution flags or missing secondaries still need to travel with it'},
            {'quality': 'partial', 'rule': 'some evidence exists, but the proof window or artifact set is too thin to promote beyond a candidate bundle'},
            {'quality': 'planning-only', 'rule': 'the object still describes a plan or receipt stack rather than a named live proof window'},
        ],
        'bundle_readiness_states': [
            {'state': 'ready-for-held', 'rule': 'route, composer, and submit receipts are honest and the same live proof window preserves the core route/composer/submit/latest-turn artifacts'},
            {'state': 'ready-with-caution', 'rule': 'the bundle can move to held review, but caution flags or thin secondary evidence must remain attached'},
            {'state': 'hold-for-recapture', 'rule': 'some part of the proof window or its artifact set is still too thin for durable held review'},
            {'state': 'blocked', 'rule': 'the current proof window preserves a blocked action path rather than a safe completed baseline'},
            {'state': 'blocked-by-composer', 'rule': 'bundle promotion cannot proceed because composer writability did not clear its own gate'},
            {'state': 'blocked-by-route', 'rule': 'bundle promotion cannot proceed because route proof did not clear its own gate'},
            {'state': 'planning-only', 'rule': 'the bundle is still planning or receipt scaffolding and has not yet become a live captured proof window'},
            {'state': 'stop', 'rule': 'the shell drifted out of the plain route-first baseline and the proof should stop instead of reinterpreting the branch'},
        ],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'route_receipt': 'python scripts/chatgpt-route-witness-receipt.py --pretty',
            'composer_receipt': 'python scripts/chatgpt-composer-witness-receipt.py --pretty',
            'submit_receipt': 'python scripts/chatgpt-submit-witness-receipt.py --pretty',
        },
        'source_keys': source_keys,
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_proof_bundle_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_chatgpt_proof_bundle_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'chatgpt-proof-bundle-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    _write_json(output_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')

    entries = _history_entries(history_path)
    previous = entries[-1] if entries else None
    entry = {
        'captured_at': payload.get('generated_at'),
        'path': str(output_path),
        'summary_path': str(summary_path),
        'target_bundle_state': payload.get('target_bundle_state'),
        'bundle_readiness_states': [item.get('state') for item in payload.get('bundle_readiness_states') or []],
        'source_keys': payload.get('source_keys') or [],
    }
    entries.append(entry)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'output_path': str(output_path), 'summary_path': str(summary_path), 'history_update': {'history_path': str(history_path), 'capture_count_after_write': len(entries), 'changed_fields': _changed_fields(previous, entry)}}


def write_root_chatgpt_proof_bundle_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_proof_bundle_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build or evaluate a ChatGPT proof bundle receipt.')
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
    evaluate_parser.add_argument('--bundle', required=True)
    evaluate_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_chatgpt_proof_bundle_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_chatgpt_proof_bundle_receipt(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'evaluate':
        bundle = _read_json(Path(args.bundle))
        payload = evaluate_chatgpt_proof_bundle_receipt(bundle, root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    print(json.dumps(build_chatgpt_proof_bundle_receipt(root=ROOT), indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
