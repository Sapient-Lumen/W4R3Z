#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from chatgpt_posture_matrix import build_chatgpt_posture_matrix
    from chatgpt_first_proof_kit import build_chatgpt_first_proof_kit
    from support_source_baseline import load_source_lock
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    def _load(name: str, filename: str):
        path = Path(__file__).resolve().parent / filename
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    build_chatgpt_posture_matrix = _load('chatgpt_posture_matrix', 'chatgpt_posture_matrix.py').build_chatgpt_posture_matrix
    build_chatgpt_first_proof_kit = _load('chatgpt_first_proof_kit', 'chatgpt_first_proof_kit.py').build_chatgpt_first_proof_kit
    load_source_lock = _load('support_source_baseline', 'support_source_baseline.py').load_source_lock

ROOT = Path(__file__).resolve().parent.parent
ROOT_OUTPUT_PATH = ROOT / 'CHATGPT-BRANCH-GUARD.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-branch-guard'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'chatgpt-branch-guard-captures.json'
REPORT_COMMAND = 'python scripts/chatgpt-branch-guard.py --pretty'
CAPTURE_COMMAND = 'python scripts/chatgpt-branch-guard.py capture --output-dir validation/latest/chatgpt-branch-guard'
HISTORY_COMMAND = 'python scripts/chatgpt-branch-guard.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/chatgpt-branch-guard.py write-root'
EVALUATE_COMMAND = 'python scripts/chatgpt-branch-guard.py evaluate --witness path/to/route-witness.json --pretty'

CueSpec = dict[str, Any]
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


def _flatten_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, (list, tuple, set)):
        items: list[str] = []
        for item in value:
            items.extend(_flatten_strings(item))
        return items
    if isinstance(value, dict):
        items: list[str] = []
        for item in value.values():
            items.extend(_flatten_strings(item))
        return items
    return []


def _source_groups(*, lock: dict[str, Any], surface_key: str = 'chatgpt') -> dict[str, list[dict[str, Any]]]:
    product_sources: list[dict[str, Any]] = []
    shared_sources: list[dict[str, Any]] = []
    for source in lock.get('sources') or []:
        if not isinstance(source, dict):
            continue
        surface_keys = {str(item) for item in source.get('surface_keys') or [] if str(item).strip()}
        source_key = str(source.get('source_key') or '')
        if surface_key in surface_keys and source.get('tier') == 'first-party-product-surface':
            product_sources.append(source)
        if 'shared-browser-substrate' in surface_keys or source_key.startswith('playwright-'):
            shared_sources.append(source)
    product_sources.sort(key=lambda item: (not bool(item.get('required_for_publication')), str(item.get('source_key') or '')))
    shared_sources.sort(key=lambda item: str(item.get('source_key') or ''))
    return {
        'product_sources': product_sources,
        'shared_sources': shared_sources,
    }


def _source_ref(source: dict[str, Any]) -> dict[str, Any]:
    return {
        'source_key': source.get('source_key'),
        'title': source.get('title'),
        'url': source.get('url'),
        'reviewed_at': source.get('reviewed_at'),
        'review_status': source.get('review_status'),
    }


def _contains_any(texts_lower: list[str], patterns: list[str]) -> list[str]:
    hits: list[str] = []
    for pattern in patterns:
        needle = pattern.lower()
        if any(needle in text for text in texts_lower):
            hits.append(pattern)
    return hits


def _host_matches(observed_host: str, allowed_hosts: list[str]) -> bool:
    return bool(observed_host) and observed_host in {host.lower() for host in allowed_hosts}


def _witness_view(witness: Witness) -> dict[str, Any]:
    texts = _flatten_strings([
        witness.get('title'),
        witness.get('path'),
        witness.get('url'),
        witness.get('visible_text'),
        witness.get('ui_text'),
        witness.get('main_region_text'),
        witness.get('sidebar_text'),
        witness.get('overlay_labels'),
        witness.get('route_hints'),
        witness.get('mode_hints'),
    ])
    lowered = [item.lower() for item in texts]
    host = str(witness.get('host') or '').strip().lower()
    path = str(witness.get('path') or '').strip().lower()
    auth_posture = str(witness.get('auth_posture') or '').strip().lower()
    return {
        'texts': texts,
        'texts_lower': lowered,
        'host': host,
        'path': path,
        'auth_posture': auth_posture,
    }


def _cue(kind: str, value: str, detail: str, *, polarity: str = 'match', weight: int = 1) -> CueSpec:
    return {
        'kind': kind,
        'value': value,
        'detail': detail,
        'polarity': polarity,
        'weight': weight,
    }


def _match_posture(witness: Witness, posture: dict[str, Any], *, allowed_hosts: list[str]) -> list[CueSpec]:
    view = _witness_view(witness)
    matches: list[CueSpec] = []
    path = view['path']
    texts_lower = view['texts_lower']
    auth_posture = view['auth_posture']

    for cue in posture.get('cue_ledger', []):
        cue_type = cue.get('cue_type')
        values = [str(item) for item in cue.get('values') or [] if str(item).strip()]
        detail = str(cue.get('detail') or '')
        weight = int(cue.get('weight') or 1)
        if cue_type == 'allowed_host' and _host_matches(view['host'], allowed_hosts):
            matches.append(_cue('allowed_host', view['host'], detail or 'expected ChatGPT host observed', weight=weight))
        elif cue_type == 'path_prefix':
            for value in values:
                if path.startswith(value.lower()):
                    matches.append(_cue('path_prefix', value, detail, weight=weight))
        elif cue_type == 'text_contains':
            for hit in _contains_any(texts_lower, values):
                matches.append(_cue('text_contains', hit, detail, weight=weight))
        elif cue_type == 'auth_posture':
            for value in values:
                normalized = value.lower()
                if normalized == auth_posture or (normalized == 'logged-out-or-logged-in' and auth_posture in {'logged-out', 'logged-in'}):
                    matches.append(_cue('auth_posture', value, detail, weight=weight))
        elif cue_type == 'main_lane_guard':
            for hit in _contains_any(texts_lower, values):
                matches.append(_cue('main_lane_guard', hit, detail, weight=weight))
        elif cue_type == 'history_search_guard':
            for hit in _contains_any(texts_lower, values):
                matches.append(_cue('history_search_guard', hit, detail, weight=weight))
    return matches


def _negative_cues(witness: Witness, *, guard: dict[str, Any]) -> list[CueSpec]:
    view = _witness_view(witness)
    negatives: list[CueSpec] = []
    host = view['host']
    if host and host not in {item.lower() for item in guard.get('allowed_hosts') or []}:
        negatives.append(_cue('unexpected_host', host, 'witness host is outside the plain ChatGPT web surface', polarity='conflict', weight=3))
    if view['path'].startswith('/g/'):
        negatives.append(_cue('non_home_path', view['path'], 'direct conversation/share route should be preserved as evidence before baseline proof continues', polarity='conflict', weight=1))
    return negatives


def _posture_rank(posture: dict[str, Any]) -> tuple[int, int]:
    policy = posture.get('baseline_policy')
    if policy == 'defer':
        return (0, 0)
    if policy == 'allowed-with-caution':
        return (1, 0)
    return (2, 0)


def _decision_for_policy(policy: str) -> str:
    if policy == 'allowed':
        return 'continue'
    if policy == 'allowed-with-caution':
        return 'continue-with-caution'
    if policy == 'defer':
        return 'stop'
    return 'insufficient'


def evaluate_chatgpt_branch_guard(witness: Witness, *, root: Path = ROOT) -> dict[str, Any]:
    spec = build_chatgpt_branch_guard(root=root)
    postures = spec.get('postures') or []
    allowed_hosts = list(spec.get('route_guard', {}).get('allowed_hosts') or [])
    view = _witness_view(witness)
    scored: list[dict[str, Any]] = []
    for posture in postures:
        matches = _match_posture(witness, posture, allowed_hosts=allowed_hosts)
        if not matches:
            continue
        raw_score = sum(int(item.get('weight') or 1) for item in matches)
        policy_bonus = 6 if posture.get('baseline_policy') == 'defer' else 2 if posture.get('baseline_policy') == 'allowed-with-caution' else 0
        scored.append({
            'posture': posture,
            'score': raw_score + policy_bonus,
            'raw_score': raw_score,
            'matched_cues': matches,
        })
    negatives = _negative_cues(witness, guard=spec.get('route_guard') or {})
    scored.sort(key=lambda item: (item['score'], item['raw_score'], _posture_rank(item['posture'])), reverse=True)
    selected = scored[0] if scored else None
    if selected is None:
        return {
            'witness': witness,
            'decision': 'insufficient',
            'matched_posture_key': None,
            'baseline_policy': 'unknown',
            'confidence': 'low',
            'matched_cues': [],
            'conflicting_cues': negatives,
            'reason': 'no posture accumulated enough evidence to continue or stop confidently',
            'route_guard': spec.get('route_guard'),
            'commands': {'spec_report': REPORT_COMMAND, 'evaluate': EVALUATE_COMMAND},
        }
    posture = selected['posture']
    policy = str(posture.get('baseline_policy') or 'unknown')
    decision = _decision_for_policy(policy)
    raw_score = selected['raw_score']
    confidence = 'high' if raw_score >= 4 else 'medium' if raw_score >= 2 else 'low'
    if negatives and decision == 'continue':
        decision = 'continue-with-caution'
    if any(item.get('kind') == 'history_search_guard' for item in selected['matched_cues']) and posture.get('posture_key') == 'search-capable-home-lane':
        decision = 'continue-with-caution'
        confidence = 'medium'
    return {
        'witness': witness,
        'decision': decision,
        'matched_posture_key': posture.get('posture_key'),
        'matched_posture_family': posture.get('family'),
        'baseline_policy': policy,
        'confidence': confidence,
        'matched_cues': selected['matched_cues'],
        'conflicting_cues': negatives,
        'reason': posture.get('continue_rule'),
        'recommended_next_action': posture.get('recommended_next_action'),
        'artifact_targets': spec.get('artifact_targets'),
        'route_guard': spec.get('route_guard'),
        'commands': {'spec_report': REPORT_COMMAND, 'evaluate': EVALUATE_COMMAND},
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    counts = payload.get('counts') or {}
    lines = [
        '# ChatGPT branch guard',
        '',
        f"- generated_at: `{payload.get('generated_at')}`",
        f"- posture_count: `{counts.get('posture_count')}`",
        f"- stop_posture_count: `{counts.get('stop_posture_count')}`",
        f"- caution_posture_count: `{counts.get('caution_posture_count')}`",
        '',
        '## Route guard',
        '',
        f"- allowed hosts: `{', '.join(payload.get('route_guard', {}).get('allowed_hosts') or [])}`",
        f"- expected route prefix: `{payload.get('route_guard', {}).get('expected_primary_route')}`",
        '',
        '## Stop postures',
        '',
    ]
    for posture in payload.get('stop_postures') or []:
        lines.append(f"- `{posture}`")
    lines.extend(['', '## Caution postures', ''])
    for posture in payload.get('caution_postures') or []:
        lines.append(f"- `{posture}`")
    return '\n'.join(lines) + '\n'


def build_chatgpt_branch_guard(*, root: Path = ROOT) -> dict[str, Any]:
    matrix = build_chatgpt_posture_matrix(root=root)
    kit = build_chatgpt_first_proof_kit(root=root)
    lock = load_source_lock(root=root)
    groups = _source_groups(lock=lock)
    sources = {str(item.get('source_key')): item for item in groups['product_sources'] + groups['shared_sources'] if item.get('source_key')}

    expected_route = ((kit.get('selected_surface') or {}).get('primary_route_hint')) or 'https://chatgpt.com/'
    if 'chatgpt.com' not in str(expected_route) or 'help.openai.com' in str(expected_route):
        expected_route = 'https://chatgpt.com/'
    allowed_hosts = ['chatgpt.com']
    postures_by_key = {str(item.get('posture_key')): dict(item) for item in matrix.get('postures') or [] if item.get('posture_key')}

    cue_ledger_by_posture = {
        'guest-home-single-thread': [
            {'cue_type': 'allowed_host', 'values': ['chatgpt.com'], 'detail': 'plain ChatGPT host observed', 'weight': 1},
            {'cue_type': 'auth_posture', 'values': ['logged-out'], 'detail': 'logged-out baseline preserved', 'weight': 2},
            {'cue_type': 'text_contains', 'values': ['chatgpt', 'text box', 'textbox'], 'detail': 'home chat surface cues present', 'weight': 1},
        ],
        'authenticated-home-chat': [
            {'cue_type': 'allowed_host', 'values': ['chatgpt.com'], 'detail': 'plain ChatGPT host observed', 'weight': 1},
            {'cue_type': 'auth_posture', 'values': ['logged-in'], 'detail': 'authenticated home chat posture', 'weight': 2},
            {'cue_type': 'text_contains', 'values': ['chatgpt'], 'detail': 'ChatGPT shell branding remains visible', 'weight': 1},
        ],
        'search-capable-home-lane': [
            {'cue_type': 'allowed_host', 'values': ['chatgpt.com'], 'detail': 'plain ChatGPT host observed', 'weight': 1},
            {'cue_type': 'main_lane_guard', 'values': ['main', 'conversation'], 'detail': 'main conversation lane is still the active shell', 'weight': 1},
            {'cue_type': 'text_contains', 'values': ['search the web', 'web search', 'sources'], 'detail': 'web-search cues appear in the active chat lane', 'weight': 2},
            {'cue_type': 'history_search_guard', 'values': ['search chats', 'chat history', 'search your chat history'], 'detail': 'sidebar history search alone does not prove the search-capable home lane', 'weight': 1},
        ],
        'project-workspace-shell': [
            {'cue_type': 'path_prefix', 'values': ['/projects'], 'detail': 'projects route observed', 'weight': 3},
            {'cue_type': 'text_contains', 'values': ['project', 'shared project'], 'detail': 'project workspace text cues observed', 'weight': 2},
        ],
        'canvas-workspace-split': [
            {'cue_type': 'path_prefix', 'values': ['/canvas'], 'detail': 'canvas route observed', 'weight': 3},
            {'cue_type': 'text_contains', 'values': ['canvas'], 'detail': 'canvas workspace cues observed', 'weight': 2},
        ],
        'gpts-builder-web-workspace': [
            {'cue_type': 'path_prefix', 'values': ['/gpts'], 'detail': 'GPT builder route observed', 'weight': 3},
            {'cue_type': 'text_contains', 'values': ['create gpt', 'explore gpts', 'gpt builder'], 'detail': 'GPT builder workspace cues observed', 'weight': 2},
        ],
    }

    recommended_next_actions = {
        'guest-home-single-thread': 'continue the route-first proof, but preserve the single-thread logged-out limitation in the witness notes',
        'authenticated-home-chat': 'continue the route-first proof and keep latest-turn extraction anchored to the main conversation region, not sidebar history',
        'search-capable-home-lane': 'continue with caution, preserving latest-turn text separately from search/source sidecars and recording whether web search was active',
        'project-workspace-shell': 'stop baseline proof, preserve branch evidence, and relaunch from the plain chat route if possible',
        'canvas-workspace-split': 'stop baseline proof, preserve branch evidence, and avoid treating canvas selectors as baseline chat selectors',
        'gpts-builder-web-workspace': 'stop baseline proof, preserve builder evidence, and restart from the plain chat lane',
    }

    postures: list[dict[str, Any]] = []
    for posture_key, posture in postures_by_key.items():
        source_keys = [str(item.get('source_key')) for item in posture.get('source_refs') or [] if item.get('source_key')]
        shared_keys: list[str] = []
        if posture_key in {'guest-home-single-thread', 'authenticated-home-chat', 'search-capable-home-lane'}:
            shared_keys = [key for key in ['chatgpt-history-search', 'playwright-best-practices', 'playwright-actionability'] if key in sources]
        posture['cue_ledger'] = cue_ledger_by_posture.get(posture_key, [])
        posture['recommended_next_action'] = recommended_next_actions.get(posture_key)
        posture['source_keys'] = sorted(dict.fromkeys(source_keys + shared_keys))
        posture['source_refs'] = [_source_ref(sources[key]) for key in posture['source_keys'] if key in sources]
        postures.append(posture)

    postures.sort(key=lambda item: (item.get('baseline_policy') == 'defer', item.get('posture_key')))
    caution_postures = [item['posture_key'] for item in postures if item.get('baseline_policy') == 'allowed-with-caution']
    stop_postures = [item['posture_key'] for item in postures if item.get('baseline_policy') == 'defer']

    payload = {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'surface_key': 'chatgpt',
        'route_guard': {
            'allowed_hosts': allowed_hosts,
            'expected_primary_route': expected_route,
            'continue_decisions': ['continue', 'continue-with-caution'],
            'stop_decisions': ['stop'],
            'branch_stop_families': ['branch'],
            'primary_branch_guard_principle': 'Classify the landed shell from route, auth posture, and visible workspace cues before composing.',
            'history_search_guard_principle': 'Sidebar history search is not the same thing as web-search-in-the-main-chat-lane.',
        },
        'witness_contract': {
            'required_fields': ['host'],
            'optional_fields': ['path', 'title', 'auth_posture', 'url', 'visible_text', 'main_region_text', 'sidebar_text', 'overlay_labels', 'route_hints', 'mode_hints'],
            'evaluation_notes': [
                'A witness may be partial; missing fields lower confidence instead of hard-failing the classifier.',
                'The branch guard prefers route, title, and user-visible workspace text over brittle CSS evidence.',
                'Preserve both the matched posture and any conflicting host/path cues so drift review stays honest.',
            ],
        },
        'decision_rules': [
            'Continue only when the witness still looks like the plain ChatGPT home/chat shell on chatgpt.com.',
            'Treat web-search capability inside the normal lane as cautionary evidence, not as an automatic branch failure.',
            'Do not confuse sidebar history search with web search in the active conversation lane.',
            'Stop when Projects, Canvas, or GPT builder becomes the dominant workspace shell.',
        ],
        'artifact_targets': ['route-witness.json', 'surface-screenshot.png', 'receiver-posture.md', 'branch-guard-evaluation.json', 'branch-note.md'],
        'postures': postures,
        'caution_postures': caution_postures,
        'stop_postures': stop_postures,
        'counts': {
            'posture_count': len(postures),
            'stop_posture_count': len(stop_postures),
            'caution_posture_count': len(caution_postures),
        },
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
            'evaluate': EVALUATE_COMMAND,
            'proof_kit': 'python scripts/chatgpt-first-proof-kit.py --pretty',
            'posture_matrix': 'python scripts/chatgpt-posture-matrix.py --pretty',
        },
        'source_keys': sorted({key for posture in postures for key in posture.get('source_keys') or []}),
    }
    payload['summary_markdown'] = _summary_markdown(payload)
    return payload


def capture_chatgpt_branch_guard(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_chatgpt_branch_guard(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / 'chatgpt-branch-guard.json'
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
        'stop_postures': payload.get('stop_postures'),
        'caution_postures': payload.get('caution_postures'),
        'changed_fields': _changed_fields(previous, payload),
    }
    entries.append(entry)
    _write_json(history_path, _history_payload(entries))
    return {'guard': payload, 'history_update': {'history_path': str(history_path), 'capture_count_after_write': len(entries), 'latest_capture': entry}}


def write_root_chatgpt_branch_guard(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_chatgpt_branch_guard(root=root)
    _write_json(root / ROOT_OUTPUT_PATH.name, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Build and evaluate a route-first branch guard for the ChatGPT baseline proof.')
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
        payload = capture_chatgpt_branch_guard(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
    elif args.command == 'history':
        payload = summarize_capture_history(path=Path(args.history_path))
    elif args.command == 'evaluate':
        payload = evaluate_chatgpt_branch_guard(_read_json(Path(args.witness)), root=ROOT)
    elif args.command == 'write-root':
        payload = write_root_chatgpt_branch_guard(root=ROOT)
    else:
        payload = build_chatgpt_branch_guard(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
