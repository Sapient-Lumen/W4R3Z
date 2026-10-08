#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_first_proof_kit import build_chatgpt_first_proof_kit
    from support_source_baseline import load_source_lock
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _KIT_PATH = Path(__file__).resolve().parent / 'chatgpt_first_proof_kit.py'
    _KIT_SPEC = importlib.util.spec_from_file_location('chatgpt_first_proof_kit', _KIT_PATH)
    _KIT_MODULE = importlib.util.module_from_spec(_KIT_SPEC)
    assert _KIT_SPEC.loader is not None
    _KIT_SPEC.loader.exec_module(_KIT_MODULE)
    build_chatgpt_first_proof_kit = _KIT_MODULE.build_chatgpt_first_proof_kit

    _SOURCE_PATH = Path(__file__).resolve().parent / 'support_source_baseline.py'
    _SOURCE_SPEC = importlib.util.spec_from_file_location('support_source_baseline', _SOURCE_PATH)
    _SOURCE_MODULE = importlib.util.module_from_spec(_SOURCE_SPEC)
    assert _SOURCE_SPEC.loader is not None
    _SOURCE_SPEC.loader.exec_module(_SOURCE_MODULE)
    load_source_lock = _SOURCE_MODULE.load_source_lock

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-POSTURE-MATRIX.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-posture-matrix'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-posture-matrix-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-posture-matrix.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-posture-matrix.py capture --output-dir validation/latest/chatgpt-posture-matrix'
HISTORY_COMMAND = 'python scripts/chatgpt-posture-matrix.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-posture-matrix.py write-root'


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError(f'{path} is not a JSON object')
    return payload


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


def _source_groups(*, lock: dict[str, Any], surface_key: str = 'chatgpt') -> dict[str, list[dict[str, Any]]]:
    product_sources: list[dict[str, Any]] = []
    for source in lock.get('sources') or []:
        if not isinstance(source, dict):
            continue
        surface_keys = {str(item) for item in source.get('surface_keys') or [] if str(item).strip()}
        if surface_key in surface_keys and source.get('tier') == 'first-party-product-surface':
            product_sources.append(source)
    product_sources.sort(key=lambda item: (not bool(item.get('required_for_publication')), str(item.get('source_key') or '')))
    return {'product_sources': product_sources}


def _summary_markdown(payload: dict[str, Any]) -> str:
    counts = payload.get('counts') or {}
    lines = [
        '# ChatGPT posture matrix',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- baseline posture count: `{counts.get('baseline_allowed_count')}`",
        f"- branch posture count: `{counts.get('branch_count')}`",
        f"- caution posture count: `{counts.get('caution_count')}`",
        '',
        '## Baseline-allowed postures',
        '',
    ]
    for posture in payload.get('baseline_allowed_postures') or []:
        lines.append(f"- `{posture}`")
    lines.extend(['', '## Branch postures', ''])
    for posture in payload.get('branch_postures') or []:
        lines.append(f"- `{posture}`")
    return '\n'.join(lines) + '\n'


def build_chatgpt_posture_matrix(*, root: Path = ROOT) -> dict[str, Any]:
    kit = build_chatgpt_first_proof_kit(root=root)
    lock = load_source_lock(root=root)
    groups = _source_groups(lock=lock)
    sources = {str(item.get('source_key')): item for item in groups['product_sources'] if item.get('source_key')}

    def source_ref(key: str) -> dict[str, Any]:
        source = sources.get(key) or {}
        return {
            'source_key': key,
            'title': source.get('title'),
            'url': source.get('url'),
            'reviewed_at': source.get('reviewed_at'),
            'review_status': source.get('review_status'),
        }

    route_hint = ((kit.get('selected_surface') or {}).get('primary_route_hint')) or 'https://chatgpt.com/'

    postures = [
        {
            'posture_key': 'guest-home-single-thread',
            'family': 'baseline',
            'baseline_policy': 'allowed',
            'auth_posture': 'logged-out',
            'route_hint': 'https://chatgpt.com/',
            'detection_cues': [
                'ChatGPT-branded shell on chatgpt.com',
                'visible prompt entry posture or explicit logged-out prompt box',
                'no project workspace, canvas split view, or GPT builder shell',
            ],
            'capture_focus': [
                'route/title/posture witness before composing',
                'single-thread limitation note when logged out',
                'composer candidate inventory in the main chat region',
            ],
            'continue_rule': 'Continue the first proof if a writable composer exists and the shell remains the plain chat surface.',
            'source_keys': ['chatgpt-home-page'],
        },
        {
            'posture_key': 'authenticated-home-chat',
            'family': 'baseline',
            'baseline_policy': 'allowed',
            'auth_posture': 'logged-in',
            'route_hint': 'https://chatgpt.com/',
            'detection_cues': [
                'ChatGPT home/chat shell on chatgpt.com',
                'sidebar or history may be visible without entering a project workspace',
                'main composer remains in the primary conversation region',
            ],
            'capture_focus': [
                'route/title/posture witness before first submit',
                'main-region composer discovery and writability proof',
                'latest-turn extraction anchored to the conversation region, not sidebar history',
            ],
            'continue_rule': 'Continue the first proof when the page is still the plain chat surface even if authenticated extras appear nearby.',
            'source_keys': ['chatgpt-home-page', 'chatgpt-product-overview'],
        },
        {
            'posture_key': 'search-capable-home-lane',
            'family': 'baseline-variant',
            'baseline_policy': 'allowed-with-caution',
            'auth_posture': 'logged-out-or-logged-in',
            'route_hint': 'https://chatgpt.com/',
            'detection_cues': [
                'plain chat/home shell remains active on chatgpt.com',
                'response or UI indicates web search is available or used',
                'composer and latest-turn targets remain in the main conversation lane',
            ],
            'capture_focus': [
                'note whether search was available before or after submit',
                'preserve latest-turn text separately from any source/citation panel',
                'record that search capability alone does not imply a route branch',
            ],
            'continue_rule': 'Continue the baseline if search appears inside the normal chat lane and does not displace the main composer or latest-turn target.',
            'source_keys': ['chatgpt-home-page', 'chatgpt-search', 'chatgpt-capabilities-overview'],
        },
        {
            'posture_key': 'project-workspace-shell',
            'family': 'branch',
            'baseline_policy': 'defer',
            'auth_posture': 'logged-in-required',
            'route_hint': route_hint,
            'detection_cues': [
                'project-named workspace or project sidebar entry',
                'files/instructions/chats grouped under one project shell',
                'surface entered through a Project rather than the plain home lane',
            ],
            'capture_focus': [
                'preserve route/posture evidence and stop baseline proof',
                'record that project context changes the shell and evidence meaning',
            ],
            'continue_rule': 'Stop baseline proof and preserve branch evidence; re-run from the plain chat route if possible.',
            'source_keys': ['chatgpt-projects', 'chatgpt-capabilities-overview'],
        },
        {
            'posture_key': 'canvas-workspace-split',
            'family': 'branch',
            'baseline_policy': 'defer',
            'auth_posture': 'varies',
            'route_hint': route_hint,
            'detection_cues': [
                'canvas editing surface or split workspace is visible',
                'inline editing/revision tools or canvas shortcut shell are active',
                'chat lane is no longer the only primary receiver surface',
            ],
            'capture_focus': [
                'preserve route and visible canvas posture',
                'record whether canvas was entered intentionally or auto-opened',
                'do not treat canvas selectors as baseline chat-lane selectors',
            ],
            'continue_rule': 'Stop baseline proof and preserve branch evidence; canvas is a follow-on mode.',
            'source_keys': ['chatgpt-canvas-feature', 'chatgpt-capabilities-overview'],
        },
        {
            'posture_key': 'gpts-builder-web-workspace',
            'family': 'branch',
            'baseline_policy': 'defer',
            'auth_posture': 'logged-in-web-builder',
            'route_hint': 'https://chatgpt.com/gpts',
            'detection_cues': [
                'Explore GPTs or Create builder route is active',
                'GPT configuration/testing workspace is visible',
                'surface is no longer the generic plain chat lane',
            ],
            'capture_focus': [
                'preserve route/posture evidence and stop baseline proof',
                'record that GPT builder is a distinct web-only workspace branch',
            ],
            'continue_rule': 'Stop baseline proof and preserve branch evidence; GPT builder is a later branch.',
            'source_keys': ['chatgpt-gpts-builder'],
        },
    ]

    baseline_allowed_postures = [item['posture_key'] for item in postures if item['baseline_policy'] == 'allowed']
    caution_postures = [item['posture_key'] for item in postures if item['baseline_policy'] == 'allowed-with-caution']
    branch_postures = [item['posture_key'] for item in postures if item['baseline_policy'] == 'defer']

    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'route_first_policy': {
            'selected_surface_primary_route_hint': route_hint,
            'continue_posture_families': ['baseline', 'baseline-variant'],
            'stop_posture_families': ['branch'],
            'stop_reasons': [
                'branch workspace replaces the plain chat shell',
                'receiver is no longer the main chat composer',
                'route or shell identity now implies Projects, Canvas, or GPT builder instead of plain chat',
            ],
        },
        'decision_rules': [
            'Continue the first proof only on the plain home/chat shell at chatgpt.com.',
            'Treat search-capable responses inside the normal home lane as a caution variant, not automatically as a branch failure.',
            'Stop and preserve branch evidence when Projects, Canvas, or the GPT builder workspace becomes the dominant shell.',
            'Capture auth posture, overlay posture, and route/title before trying to write or submit.',
        ],
        'postures': [{**item, 'source_refs': [source_ref(key) for key in item['source_keys']]} for item in postures],
        'baseline_allowed_postures': baseline_allowed_postures,
        'caution_postures': caution_postures,
        'branch_postures': branch_postures,
        'counts': {
            'posture_count': len(postures),
            'baseline_allowed_count': len(baseline_allowed_postures),
            'caution_count': len(caution_postures),
            'branch_count': len(branch_postures),
        },
        'artifact_targets': ['route-witness.json','surface-screenshot.png','receiver-posture.md','composer-candidates.json','latest-turn.txt','branch-note.md'],
        'source_keys': sorted({key for item in postures for key in item['source_keys']}),
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'proof_kit': 'python scripts/chatgpt-first-proof-kit.py --pretty',
        },
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_posture_matrix(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_chatgpt_posture_matrix(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'chatgpt-posture-matrix.json'
    summary_path = output_dir / 'SUMMARY.md'
    previous = _read_json(report_path) if report_path.exists() else None
    _write_json(report_path, payload)
    summary_path.write_text(payload.get('summary_markdown', ''), encoding='utf-8')
    entries = _history_entries(history_path)
    entry = {
        'captured_at': payload.get('generated_at'),
        'output_dir': str(output_dir),
        'report_path': str(report_path),
        'summary_path': str(summary_path),
        'baseline_allowed_postures': payload.get('baseline_allowed_postures'),
        'caution_postures': payload.get('caution_postures'),
        'branch_postures': payload.get('branch_postures'),
        'changed_fields': _changed_fields(previous, payload),
    }
    entries.append(entry)
    _write_json(history_path, _history_payload(entries))
    return {'matrix': payload, 'history_update': {'history_path': str(history_path), 'capture_count_after_write': len(entries), 'latest_capture': entry}}


def write_root_chatgpt_posture_matrix(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_posture_matrix(root=root)
    _write_json(root / 'CHATGPT-POSTURE-MATRIX.json', payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a machine-readable posture matrix for the ChatGPT route-first proof.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Write the latest capture into validation/latest/chatgpt-posture-matrix.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser = subparsers.add_parser('history', help='Summarize capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    subparsers.add_parser('write-root', help='Refresh CHATGPT-POSTURE-MATRIX.json at the repo root.')
    args = parser.parse_args()
    if args.command == 'capture':
        payload = capture_chatgpt_posture_matrix(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    elif args.command == 'history':
        payload = summarize_capture_history(path=Path(args.history_path))
    elif args.command == 'write-root':
        payload = write_root_chatgpt_posture_matrix(root=ROOT)
    else:
        payload = build_chatgpt_posture_matrix(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))

if __name__ == '__main__':
    main()
