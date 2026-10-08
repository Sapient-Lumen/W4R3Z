#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATES = ('candidate', 'hold', 'published-ready', 'published')



def _default_bundles_dir(root: Path) -> Path:
    return root / 'docs' / 'support-bundles'


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError(f'{path} is not a JSON object')
    return payload


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _find_bundle(name_or_key: str, *, bundles_dir: Path) -> tuple[str, Path]:
    for state in STATES:
        state_dir = bundles_dir / state
        if not state_dir.exists():
            continue
        for path in sorted(state_dir.glob('*.json')):
            if path.stem == name_or_key:
                return state, path
            payload = _read_json(path)
            if payload.get('bundle_key') == name_or_key:
                return state, path
    raise FileNotFoundError(f'support bundle not found: {name_or_key}')


def _load_publish_gate_module():
    try:
        import support_publish_gate as module  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
        import importlib.util

        module_path = Path(__file__).resolve().parent / 'support_publish_gate.py'
        spec = importlib.util.spec_from_file_location('support_publish_gate', module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
    return module


def _transition_receipt_history(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {'receipts': []}
    payload = _read_json(path)
    receipts = payload.get('receipts')
    if not isinstance(receipts, list):
        payload['receipts'] = []
    return payload


def _capture_transition_receipt(*, root: Path, receipt: dict[str, Any], output_dir: Path | None = None, history_path: Path | None = None) -> dict[str, Any]:
    output_dir = output_dir or (root / 'validation' / 'latest' / 'support-bundle-transition')
    history_path = history_path or (root / 'validation' / 'support-bundle-transition-receipts.json')
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / 'transition-receipt.json', receipt)
    summary_lines = [
        '# Support-bundle transition receipt',
        '',
        f"- bundle: `{receipt.get('bundle_key')}`",
        f"- transition: `{receipt.get('from_state')}` → `{receipt.get('to_state')}`",
        f"- gate checked: `{receipt.get('gate_checked')}`",
        f"- gate ok: `{receipt.get('gate_ok')}`",
    ]
    blocking = receipt.get('gate_blocking_reasons') or []
    if blocking:
        summary_lines.append(f"- blocking reasons: {'; '.join(str(item) for item in blocking)}")
    (output_dir / 'SUMMARY.md').write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')
    history_payload = _transition_receipt_history(history_path)
    receipts = history_payload.setdefault('receipts', [])
    receipts.append(receipt)
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', {
        'path': str(history_path),
        'exists': True,
        'capture_count': len(receipts),
        'latest_capture': receipt,
    })
    return {
        'output_dir': str(output_dir),
        'history_path': str(history_path),
        'capture_count_after_write': len(receipts),
    }


def transition_bundle(
    *,
    name_or_key: str,
    to_state: str,
    root: Path = ROOT,
    bundles_dir: Path | None = None,
    why: list[str] | None = None,
    publish_when: list[str] | None = None,
    next_action: str | None = None,
    allow_failed_gate: bool = False,
) -> dict[str, Any]:
    if to_state not in STATES:
        raise ValueError(f'unsupported state: {to_state!r}')
    bundles_dir = bundles_dir or _default_bundles_dir(root)
    from_state, source = _find_bundle(name_or_key, bundles_dir=bundles_dir)
    if from_state == to_state:
        raise ValueError('source and destination states are the same')
    payload = _read_json(source)

    gate_module = _load_publish_gate_module()
    allowed_targets = set(gate_module.ALLOWED_TRANSITIONS.get(from_state, set()))
    gate_summary: dict[str, Any] | None = None
    if to_state not in allowed_targets and not allow_failed_gate:
        raise ValueError(f'{from_state!r} cannot transition directly to {to_state!r}; allowed targets are {sorted(allowed_targets)}')
    if to_state in ('published-ready', 'published'):
        gate_summary = gate_module.evaluate_bundle_gate(bundle_path=source, root=root, target_state=to_state)
        if not gate_summary.get('ok') and not allow_failed_gate:
            reasons = '; '.join(gate_summary.get('blocking_reasons') or ['support publish gate failed'])
            raise ValueError(f'support publish gate failed for {name_or_key}: {reasons}')

    payload['bundle_status'] = to_state
    decision = payload.get('publication_decision')
    if not isinstance(decision, dict):
        decision = {}
    decision['decision'] = to_state
    if why is not None:
        decision['why'] = why
    if publish_when is not None:
        decision['publish_when'] = publish_when
    payload['publication_decision'] = decision
    result_summary = payload.get('result_summary')
    if not isinstance(result_summary, dict):
        result_summary = {}
    if next_action is not None:
        result_summary['next_action'] = next_action
    payload['result_summary'] = result_summary

    if to_state in ('published-ready', 'published'):
        gate_module.stamp_publish_guard(payload, root=root, target_state=to_state, gate_summary=gate_summary)

    transition_entry = {
        'transitioned_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'from_state': from_state,
        'to_state': to_state,
        'allow_failed_gate': allow_failed_gate,
    }
    if why is not None:
        transition_entry['why'] = why
    if publish_when is not None:
        transition_entry['publish_when'] = publish_when
    if next_action is not None:
        transition_entry['next_action'] = next_action
    history_entries = payload.get('transition_history') if isinstance(payload.get('transition_history'), list) else []
    history_entries.append(transition_entry)
    payload['transition_history'] = history_entries

    destination = bundles_dir / to_state / source.name
    if destination.exists() and destination != source:
        raise FileExistsError(f'destination bundle already exists: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    _write_json(destination, payload)
    if destination != source:
        source.unlink()

    if to_state in ('published-ready', 'published'):
        try:
            gate_module.write_root_support_publish_gate(root=root)
        except Exception:
            pass
    try:
        from published_support_surface import write_root_published_support_surface  # type: ignore
    except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
        import importlib.util

        module_path = Path(__file__).resolve().parent / 'published_support_surface.py'
        spec = importlib.util.spec_from_file_location('published_support_surface', module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        write_root_published_support_surface = module.write_root_published_support_surface
    try:
        write_root_published_support_surface(root=root)
    except Exception:
        pass

    receipt = {
        'bundle_key': payload.get('bundle_key') or source.stem,
        'from_state': from_state,
        'to_state': to_state,
        'source_path': str(source),
        'destination_path': str(destination),
        'captured_at': transition_entry['transitioned_at'],
        'allow_failed_gate': allow_failed_gate,
        'gate_checked': to_state in ('published-ready', 'published'),
        'gate_ok': gate_summary.get('ok') if isinstance(gate_summary, dict) else None,
        'gate_target_state': gate_summary.get('target_state') if isinstance(gate_summary, dict) else None,
        'gate_blocking_reasons': gate_summary.get('blocking_reasons') if isinstance(gate_summary, dict) else [],
        'publish_guard': payload.get('publish_guard'),
    }
    receipt_capture = _capture_transition_receipt(root=root, receipt=receipt)
    return {
        'bundle_key': payload.get('bundle_key') or source.stem,
        'from_state': from_state,
        'to_state': to_state,
        'source_path': str(source),
        'destination_path': str(destination),
        'gate': gate_summary,
        'receipt_capture': receipt_capture,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Move a GlassTTY support bundle manifest between queue states, enforce publish gates by default, and emit a transition receipt.')
    parser.add_argument('--bundle', required=True, help='Bundle stem or bundle_key.')
    parser.add_argument('--to-state', required=True, choices=STATES)
    parser.add_argument('--why', action='append', default=None, help='Optional replacement publication_decision.why entry; may be repeated.')
    parser.add_argument('--publish-when', action='append', default=None, help='Optional replacement publication_decision.publish_when entry; may be repeated.')
    parser.add_argument('--next-action', default=None, help='Optional replacement result_summary.next_action value.')
    parser.add_argument('--allow-failed-gate', action='store_true', help='Bypass the publish gate or direct-transition graph intentionally.')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    payload = transition_bundle(
        name_or_key=args.bundle,
        to_state=args.to_state,
        why=args.why,
        publish_when=args.publish_when,
        next_action=args.next_action,
        allow_failed_gate=args.allow_failed_gate,
    )
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
