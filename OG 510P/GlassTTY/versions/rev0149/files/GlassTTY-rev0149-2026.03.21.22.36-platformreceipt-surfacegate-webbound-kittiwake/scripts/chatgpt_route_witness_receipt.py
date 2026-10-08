#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_branch_guard import build_chatgpt_branch_guard, evaluate_chatgpt_branch_guard
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    _MODULE = _load('chatgpt_branch_guard', 'chatgpt_branch_guard.py')
    build_chatgpt_branch_guard = _MODULE.build_chatgpt_branch_guard
    evaluate_chatgpt_branch_guard = _MODULE.evaluate_chatgpt_branch_guard

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-ROUTE-WITNESS-RECEIPT.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-route-witness-receipt'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-route-witness-receipt-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-route-witness-receipt.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-route-witness-receipt.py capture --output-dir validation/latest/chatgpt-route-witness-receipt'
HISTORY_COMMAND = 'python scripts/chatgpt-route-witness-receipt.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-route-witness-receipt.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-route-witness-receipt.py evaluate --witness path/to/route-witness.json --pretty'

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


def _field_value_summary(value: Any) -> str | None:
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


def _field_scorecard(witness: Witness) -> list[dict[str, Any]]:
    route_present = _present(witness.get('path')) or _present(witness.get('url'))
    shell_text_present = any(
        _present(witness.get(key)) for key in ['title', 'visible_text', 'main_region_text', 'sidebar_text']
    )
    hints_present = _present(witness.get('route_hints')) or _present(witness.get('mode_hints'))
    checks = [
        {
            'field_key': 'host',
            'weight': 3,
            'required': True,
            'present': _present(witness.get('host')),
            'detail': 'plain ChatGPT host is the minimum route anchor',
            'value_summary': _field_value_summary(witness.get('host')),
        },
        {
            'field_key': 'path_or_url',
            'weight': 2,
            'required': False,
            'present': route_present,
            'detail': 'path or full URL preserves which shell was actually reached',
            'value_summary': _field_value_summary(witness.get('path') or witness.get('url')),
        },
        {
            'field_key': 'title',
            'weight': 2,
            'required': False,
            'present': _present(witness.get('title')),
            'detail': 'page title helps separate the plain chat lane from richer workspaces',
            'value_summary': _field_value_summary(witness.get('title')),
        },
        {
            'field_key': 'auth_posture',
            'weight': 1,
            'required': False,
            'present': _present(witness.get('auth_posture')),
            'detail': 'logged-in vs logged-out posture affects what the baseline can honestly claim',
            'value_summary': _field_value_summary(witness.get('auth_posture')),
        },
        {
            'field_key': 'shell_text',
            'weight': 2,
            'required': False,
            'present': shell_text_present,
            'detail': 'visible user-facing shell text is preferred over brittle DOM clues',
            'value_summary': 'present' if shell_text_present else None,
        },
        {
            'field_key': 'main_region_text',
            'weight': 2,
            'required': False,
            'present': _present(witness.get('main_region_text')),
            'detail': 'main-lane text helps distinguish the active conversation area from sidebars or branch shells',
            'value_summary': _field_value_summary(witness.get('main_region_text')),
        },
        {
            'field_key': 'sidebar_text',
            'weight': 1,
            'required': False,
            'present': _present(witness.get('sidebar_text')),
            'detail': 'sidebar cues help identify history search without mistaking it for the main lane',
            'value_summary': _field_value_summary(witness.get('sidebar_text')),
        },
        {
            'field_key': 'overlay_labels',
            'weight': 1,
            'required': False,
            'present': _present(witness.get('overlay_labels')),
            'detail': 'overlay evidence preserves interruptions such as login or consent gates',
            'value_summary': _field_value_summary(witness.get('overlay_labels')),
        },
        {
            'field_key': 'route_or_mode_hints',
            'weight': 1,
            'required': False,
            'present': hints_present,
            'detail': 'route or mode hints help explain ambiguous shells without replacing route proof',
            'value_summary': 'present' if hints_present else None,
        },
    ]
    for item in checks:
        item['earned_weight'] = item['weight'] if item['present'] else 0
    return checks


def _quality_from_score(score: int) -> str:
    if score >= 11:
        return 'strong'
    if score >= 8:
        return 'usable'
    if score >= 4:
        return 'sparse'
    return 'insufficient'


def _downgrade_confidence(branch_confidence: str, quality: str) -> str:
    levels = ['low', 'medium', 'high']
    try:
        index = levels.index(branch_confidence)
    except ValueError:
        index = 0
    if quality == 'strong':
        return levels[index]
    if quality == 'usable':
        return levels[index]
    if quality == 'sparse':
        return levels[max(index - 1, 0)]
    return 'low'


def evaluate_chatgpt_route_witness_receipt(witness: Witness, *, root: Path = ROOT) -> dict[str, Any]:
    spec = build_chatgpt_route_witness_receipt(root=root)
    branch = evaluate_chatgpt_branch_guard(witness, root=root)
    scorecard = _field_scorecard(witness)
    score = sum(int(item.get('earned_weight') or 0) for item in scorecard)
    max_score = sum(int(item.get('weight') or 0) for item in scorecard)
    quality = _quality_from_score(score)
    present_keys = [str(item.get('field_key')) for item in scorecard if item.get('present')]
    missing_keys = [str(item.get('field_key')) for item in scorecard if not item.get('present')]

    core_gaps: list[str] = []
    if 'host' in missing_keys:
        core_gaps.append('host')
    if 'path_or_url' in missing_keys:
        core_gaps.append('path_or_url')
    if 'shell_text' in missing_keys:
        core_gaps.append('shell_text')
    if 'main_region_text' in missing_keys and branch.get('decision') in {'continue', 'continue-with-caution'}:
        core_gaps.append('main_region_text')

    effective_confidence = _downgrade_confidence(str(branch.get('confidence') or 'low'), quality)
    decision = str(branch.get('decision') or 'insufficient')
    if decision == 'stop':
        proof_readiness = 'stop'
        readiness_reason = 'branch guard says the landed shell is outside the baseline lane'
    elif decision == 'insufficient' or quality == 'insufficient':
        proof_readiness = 'insufficient'
        readiness_reason = 'the witness is too thin to safely continue the baseline proof'
    elif quality == 'sparse':
        proof_readiness = 'hold-for-recapture'
        readiness_reason = 'the witness classified, but it does not preserve enough route/title/text evidence for a durable proof handoff'
    elif decision == 'continue-with-caution':
        proof_readiness = 'ready-with-caution'
        readiness_reason = 'the witness is usable, but the shell still carries cautionary cues that should stay attached to the bundle'
    else:
        proof_readiness = 'ready'
        readiness_reason = 'the witness is strong enough to justify composer and submit proof on the baseline lane'

    if proof_readiness == 'hold-for-recapture':
        recommended_next_action = 'recapture the witness with host, path or URL, title or visible shell text, and main-lane text before continuing proof actions'
    elif proof_readiness == 'insufficient':
        recommended_next_action = 'capture a richer route witness before touching the composer, including route, title, auth posture, and visible text'
    else:
        recommended_next_action = branch.get('recommended_next_action')

    return {
        'witness': witness,
        'branch_evaluation': branch,
        'field_scorecard': scorecard,
        'witness_quality': quality,
        'coverage_score': score,
        'coverage_score_max': max_score,
        'coverage_ratio': round(score / max_score, 3) if max_score else 0.0,
        'present_field_keys': present_keys,
        'missing_field_keys': missing_keys,
        'core_gaps': core_gaps,
        'effective_confidence': effective_confidence,
        'proof_readiness': proof_readiness,
        'readiness_reason': readiness_reason,
        'recommended_next_action': recommended_next_action,
        'commands': {'spec_report': REPORT_COMMAND, 'evaluate': EVALUATE_COMMAND, 'branch_guard': 'python scripts/chatgpt-branch-guard.py --pretty'},
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    contract = payload.get('witness_contract') or {}
    lines = [
        '# ChatGPT route witness receipt',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- minimum_required_fields: `{', '.join(contract.get('required_fields') or [])}`",
        f"- recommended_field_count: `{len(contract.get('recommended_fields') or [])}`",
        '',
        '## Quality tiers',
        '',
    ]
    for item in payload.get('quality_tiers') or []:
        lines.append(f"- `{item.get('quality')}` — {item.get('rule')}")
    lines.extend(['', '## Proof readiness', ''])
    for item in payload.get('proof_readiness_states') or []:
        lines.append(f"- `{item.get('state')}` — {item.get('rule')}")
    return '\n'.join(lines) + '\n'


def build_chatgpt_route_witness_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    guard = build_chatgpt_branch_guard(root=root)
    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'purpose': 'grade route-witness completeness separately from shell classification so sparse evidence cannot overclaim baseline readiness',
        'witness_contract': {
            'required_fields': ['host'],
            'recommended_fields': ['path or url', 'title', 'auth_posture', 'visible_text', 'main_region_text', 'sidebar_text', 'overlay_labels', 'route_hints', 'mode_hints'],
            'capture_notes': [
                'A route witness can be partial, but proof readiness should degrade when route, title, or main-lane text is missing.',
                'Use user-facing route and text evidence before brittle DOM or CSS clues.',
                'A classification result is not the same thing as a durable proof-ready witness.',
            ],
        },
        'quality_tiers': [
            {'quality': 'strong', 'rule': '11-15 weighted points; suitable for durable handoff and proof continuation'},
            {'quality': 'usable', 'rule': '8-10 weighted points; acceptable for continuation when the branch decision stays in the baseline lane'},
            {'quality': 'sparse', 'rule': '4-7 weighted points; classification may be possible, but proof should pause for recapture'},
            {'quality': 'insufficient', 'rule': '0-3 weighted points; do not continue baseline proof'},
        ],
        'proof_readiness_states': [
            {'state': 'ready', 'rule': 'branch guard stays on continue and the witness quality is usable or strong'},
            {'state': 'ready-with-caution', 'rule': 'branch guard stays on continue-with-caution and the witness quality is usable or strong'},
            {'state': 'hold-for-recapture', 'rule': 'branch guard classified the shell, but the witness is too sparse for durable proof handoff'},
            {'state': 'insufficient', 'rule': 'the witness is too thin to justify proof actions even if one cue looked promising'},
            {'state': 'stop', 'rule': 'branch guard says the shell is a richer branch or otherwise outside the baseline lane'},
        ],
        'field_weights': [
            {'field_key': 'host', 'weight': 3},
            {'field_key': 'path_or_url', 'weight': 2},
            {'field_key': 'title', 'weight': 2},
            {'field_key': 'auth_posture', 'weight': 1},
            {'field_key': 'shell_text', 'weight': 2},
            {'field_key': 'main_region_text', 'weight': 2},
            {'field_key': 'sidebar_text', 'weight': 1},
            {'field_key': 'overlay_labels', 'weight': 1},
            {'field_key': 'route_or_mode_hints', 'weight': 1},
        ],
        'decision_rules': [
            'Run the branch guard first, then grade witness completeness.',
            'Do not let a sparse witness silently inherit the branch guard confidence unchanged.',
            'Require stronger route/title/text evidence before calling a witness proof-ready.',
            'Treat recapture as useful evidence work rather than as wasted setup.',
        ],
        'artifact_targets': ['route-witness.json', 'surface-screenshot.png', 'receiver-posture.md', 'branch-guard-evaluation.json', 'route-witness-receipt.json'],
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'branch_guard': 'python scripts/chatgpt-branch-guard.py --pretty',
            'proof_kit': 'python scripts/chatgpt-first-proof-kit.py --pretty',
        },
        'source_keys': list(guard.get('source_keys') or []),
        'source_refs': [
            ref
            for _, ref in sorted(
                {
                    (str(ref.get('source_key') or ''), str(ref.get('url') or '')): ref
                    for posture in guard.get('postures') or []
                    for ref in posture.get('source_refs') or []
                }.items(),
                key=lambda item: item[0],
            )
        ],
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_route_witness_receipt(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_chatgpt_route_witness_receipt(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'chatgpt-route-witness-receipt.json'
    summary_path = output_dir / 'SUMMARY.md'
    previous = _read_json(report_path) if report_path.exists() else None
    _write_json(report_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entry = {
        'captured_at': payload.get('generated_at'),
        'output_dir': str(output_dir),
        'report_path': str(report_path),
        'summary_path': str(summary_path),
        'quality_tiers': [item.get('quality') for item in payload.get('quality_tiers') or []],
        'proof_readiness_states': [item.get('state') for item in payload.get('proof_readiness_states') or []],
        'changed_fields': _changed_fields(previous, payload),
    }
    entries = _history_entries(history_path)
    entries.append(entry)
    _write_json(history_path, _history_payload(entries))
    return {'receipt': payload, 'history_update': {'history_path': str(history_path), 'capture_count_after_write': len(entries), 'latest_capture': entry}}


def write_root_chatgpt_route_witness_receipt(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_route_witness_receipt(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build and evaluate a witness-quality receipt for the ChatGPT route-first baseline proof.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    evaluate_parser = subparsers.add_parser('evaluate')
    evaluate_parser.add_argument('--witness', required=True)
    subparsers.add_parser('write-root')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_chatgpt_route_witness_receipt(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    elif args.command == 'history':
        payload = summarize_capture_history(path=Path(args.history_path))
    elif args.command == 'evaluate':
        payload = evaluate_chatgpt_route_witness_receipt(_read_json(Path(args.witness)), root=ROOT)
    elif args.command == 'write-root':
        payload = write_root_chatgpt_route_witness_receipt(root=ROOT)
    else:
        payload = build_chatgpt_route_witness_receipt(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
