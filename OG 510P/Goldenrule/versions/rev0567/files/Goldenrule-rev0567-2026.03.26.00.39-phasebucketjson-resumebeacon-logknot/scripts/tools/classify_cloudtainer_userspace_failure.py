#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CARD_PATH = ROOT / 'artifacts' / 'reports' / 'cloudtainer_userspace_failure_resume_card.json'
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')


def _load_card() -> dict[str, Any]:
    return json.loads(CARD_PATH.read_text(encoding='utf-8'))


def _read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding='utf-8')
    return sys.stdin.read()


def _extract_json_rendered_text(text: str) -> tuple[str, list[str]]:
    rendered_parts: list[str] = []
    reasons: list[str] = []
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate.startswith('{'):
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        reason = str(payload.get('reason') or '')
        if reason:
            reasons.append(reason)
        message = payload.get('message')
        if isinstance(message, dict):
            rendered = message.get('rendered')
            if isinstance(rendered, str) and rendered.strip():
                rendered_parts.append(rendered)
        if reason == 'build-finished':
            rendered_parts.append(f"build-finished success={payload.get('success')}")
    return '\n'.join(rendered_parts), reasons


def _normalize(text: str) -> str:
    text = ANSI_RE.sub('', text)
    return text.lower()


def classify(text: str, *, command_key: str | None = None) -> dict[str, Any]:
    card = _load_card()
    json_rendered, json_reasons = _extract_json_rendered_text(text)
    normalized = _normalize(text)
    combined = normalized + ('\n' + _normalize(json_rendered) if json_rendered else '')

    classes = list(card.get('classes') or [])
    precedence = list(card.get('command_precedence') or [])
    precedence_rank = {class_id: idx for idx, class_id in enumerate(precedence)}

    scored: list[dict[str, Any]] = []
    for row in classes:
        matches = [marker for marker in row.get('markers') or [] if marker.lower() in combined]
        score = len(matches)
        class_id = str(row.get('class_id'))
        if command_key and row.get('resume_command_key') == command_key:
            score += 1
            if class_id in {'exact_witness_semantic_failure', 'lane_smoke_semantic_failure'}:
                score += 1
        if class_id == 'lane_smoke_semantic_failure' and command_key != 'offline_lane_smoke':
            score -= 1
        if class_id == 'exact_witness_semantic_failure' and command_key != 'offline_exact_witness':
            score -= 1
        if class_id == 'offline_cache_incomplete_or_lock_drift' and 'offline was specified' in combined:
            score += 3
        if class_id == 'warm_cache_transport_or_registry' and ('failed to download' in combined or 'spurious network error' in combined):
            score += 2
        if class_id == 'compile_surface_failure' and command_key == 'offline_compile' and not ('offline was specified' in combined or '--locked was passed' in combined):
            score += 1
        if score > 0:
            scored.append({
                'class_id': class_id,
                'score': score,
                'matches': matches,
                'row': row,
            })

    scored.sort(key=lambda item: (-int(item['score']), precedence_rank.get(item['class_id'], 999)))
    best = scored[0] if scored else None
    result: dict[str, Any] = {
        'command_key': command_key,
        'json_message_reasons': json_reasons,
        'matched_classes': [
            {
                'class_id': item['class_id'],
                'score': item['score'],
                'matches': item['matches'],
            }
            for item in scored
        ],
        'classification': None,
    }
    if best is not None:
        row = dict(best['row'])
        result['classification'] = {
            'class_id': row['class_id'],
            'phase_id': row['phase_id'],
            'resume_phase_id': row['resume_phase_id'],
            'resume_command_key': row['resume_command_key'],
            'resume_command': row['resume_command'],
            'summary': row['summary'],
            'next_step': row['next_step'],
            'capture_hint': row['capture_hint'],
            'matched_markers': best['matches'],
            'score': best['score'],
        }
    return result


def _render_text(result: dict[str, Any]) -> str:
    classification = result.get('classification')
    if not classification:
        return 'classification: unclassified\nnext_step: keep the raw log, then compare it manually against docs/CLOUDTAINER_USERSPACE_FAILURE_RESUME_CARD.md\n'
    lines = [
        f"classification: {classification['class_id']}",
        f"failed_phase: {classification['phase_id']}",
        f"resume_from: {classification['resume_phase_id']}",
        f"rerun: {classification['resume_command']}",
        f"why: {classification['summary']}",
        f"next_step: {classification['next_step']}",
    ]
    matched = classification.get('matched_markers') or []
    if matched:
        lines.append(f"matched_markers: {', '.join(matched)}")
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Classify later-machine userspace Rust failure logs into the preserved resume phases.')
    parser.add_argument('--input', help='path to a later-machine log file; stdin is used when omitted')
    parser.add_argument('--command-key', choices=['offline_compile', 'offline_exact_witness', 'offline_lane_smoke', 'warm_cache', 'patch_apply'], help='optional hint describing which preserved command produced the log')
    parser.add_argument('--format', choices=['json', 'text'], default='json')
    args = parser.parse_args()

    text = _read_input(args.input)
    result = classify(text, command_key=args.command_key)
    if args.format == 'json':
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_render_text(result), end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
