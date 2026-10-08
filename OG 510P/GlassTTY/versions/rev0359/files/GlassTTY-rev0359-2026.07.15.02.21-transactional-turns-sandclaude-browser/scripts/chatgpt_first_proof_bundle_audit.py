#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_first_proof_evaluator import (
    DEFAULT_INPUT,
    ROOT,
    SCHEMA_VERSION as EVALUATOR_SCHEMA_VERSION,
    action_record_witness,
    action_type,
    chatgpt_conversation_path,
    evaluate_payload,
    iter_evidence_records,
    read_json,
    record_sequence_index,
    record_tab_id,
    record_urls,
    required_check_registry_audit,
    sha256_file,
    write_json,
)

DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-first-proof-bundle-audit'
AUDIT_SCHEMA_VERSION = 1
ACTION_PREFIXES = ('prompt.', 'transcript.', 'fixture.', 'state.')


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def display_path(path: Path, *, root: Path = ROOT) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def _is_action_record(record: Any) -> bool:
    kind = action_type(record.item)
    return bool(kind and (kind.startswith(ACTION_PREFIXES) or kind in {'route.witness', 'privacy.review'}))


def _record_conversation_paths(record: Any) -> list[str]:
    paths = []
    seen: set[str] = set()
    for url in record_urls(record.item):
        path = chatgpt_conversation_path(url)
        if path and path not in seen:
            paths.append(path)
            seen.add(path)
    return paths


def _action_node(record: Any) -> dict[str, Any]:
    witness = action_record_witness(record)
    return {
        'node_id': f'{record.attempt_id}:{record.path}',
        'attempt_id': record.attempt_id,
        'path': record.path,
        'ordinal': record.ordinal,
        'type': witness['type'],
        'sequence_index': witness['sequence_index'],
        'tab_id': witness['tab_id'],
        'adapter_is_chatgpt': witness['adapter_is_chatgpt'],
        'host_is_chatgpt': witness['host_is_chatgpt'],
        'urls': witness['urls'],
        'conversation_route_paths': witness['conversation_route_paths'],
    }


def _sort_node_key(node: dict[str, Any]) -> tuple[int, int, str]:
    seq = node.get('sequence_index')
    seq_key = seq if isinstance(seq, int) else 10**9
    return (seq_key, int(node.get('ordinal') or 0), str(node.get('path') or ''))


def _edge_rows(nodes_by_attempt: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for attempt_id, nodes in sorted(nodes_by_attempt.items()):
        ordered = sorted(nodes, key=_sort_node_key)
        for before, after in zip(ordered, ordered[1:]):
            before_seq = before.get('sequence_index')
            after_seq = after.get('sequence_index')
            edges.append({
                'attempt_id': attempt_id,
                'from': before['node_id'],
                'to': after['node_id'],
                'from_type': before.get('type'),
                'to_type': after.get('type'),
                'sequence_delta': (after_seq - before_seq) if isinstance(before_seq, int) and isinstance(after_seq, int) else None,
                'same_tab': before.get('tab_id') == after.get('tab_id') if before.get('tab_id') is not None and after.get('tab_id') is not None else None,
            })
    return edges


def _attempt_summary(attempt_id: str, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    sequences = [node.get('sequence_index') for node in nodes if isinstance(node.get('sequence_index'), int)]
    missing_sequence_paths = [node['path'] for node in nodes if node.get('sequence_index') is None]
    duplicate_sequences = sorted({seq for seq in sequences if sequences.count(seq) > 1})
    tab_ids = sorted({node.get('tab_id') for node in nodes if isinstance(node.get('tab_id'), int)})
    conversation_paths = sorted({path for node in nodes for path in (node.get('conversation_route_paths') or [])})
    action_types = [node.get('type') for node in sorted(nodes, key=_sort_node_key) if node.get('type')]
    return {
        'attempt_id': attempt_id,
        'action_count': len(nodes),
        'action_types_in_sequence_order': action_types,
        'sequence_indices': sequences,
        'missing_sequence_index_paths': missing_sequence_paths,
        'duplicate_sequence_indices': duplicate_sequences,
        'tab_ids': tab_ids,
        'conversation_route_paths': conversation_paths,
        'has_root_to_conversation_shape': bool(any(t == 'prompt.submit' for t in action_types) and conversation_paths),
    }


def build_bundle_audit(payload: Any, *, root: Path = ROOT, input_path: Path | None = None) -> dict[str, Any]:
    records = iter_evidence_records(payload)
    action_records = [record for record in records if _is_action_record(record)]
    nodes = [_action_node(record) for record in action_records]
    nodes_by_attempt: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        nodes_by_attempt[str(node['attempt_id'])].append(node)
    attempts = [_attempt_summary(attempt_id, nodes) for attempt_id, nodes in sorted(nodes_by_attempt.items())]
    evaluation = evaluate_payload(payload, root=root, input_path=input_path)
    evaluator_summary = {
        'schema_version': evaluation.get('schema_version'),
        'ok': evaluation.get('ok'),
        'verdict': evaluation.get('verdict'),
        'winning_attempt_id': evaluation.get('winning_attempt_id'),
        'missing_required_checks': evaluation.get('missing_required_checks'),
        'support_claim_effect': evaluation.get('support_claim_effect'),
    }
    return {
        'schema_version': AUDIT_SCHEMA_VERSION,
        'audit_key': 'chatgpt-first-proof-bundle-audit',
        'generated_at': utcnow(),
        'project': 'GlassTTY',
        'surface_key': 'chatgpt',
        'input_path': display_path(input_path, root=root) if input_path else None,
        'input_sha256': sha256_file(input_path) if input_path and input_path.exists() else None,
        'evaluator_schema_version': EVALUATOR_SCHEMA_VERSION,
        'check_registry_audit': required_check_registry_audit(),
        'counts': {
            'evidence_record_count': len(records),
            'action_record_count': len(action_records),
            'attempt_count': len(nodes_by_attempt),
            'edge_count': sum(max(len(items) - 1, 0) for items in nodes_by_attempt.values()),
        },
        'attempts': attempts,
        'graph': {
            'node_count': len(nodes),
            'edge_count': sum(max(len(items) - 1, 0) for items in nodes_by_attempt.values()),
            'nodes': sorted(nodes, key=lambda node: (str(node.get('attempt_id')), *_sort_node_key(node))),
            'edges': _edge_rows(nodes_by_attempt),
        },
        'evaluator_summary': evaluator_summary,
        'support_claim_effect': 'none; this audit only describes local evidence shape and never widens support claims',
        'operator_notes': [
            'Use this audit before human review to catch action-sequence and registry drift at a glance.',
            'A reviewable evaluator summary is still local evidence only; it is not a public-citable support claim.',
            'Live proof remains absent until a real browser bundle is captured and privacy-reviewed.',
        ],
    }


def summary_markdown(audit: dict[str, Any]) -> str:
    evaluator = audit.get('evaluator_summary') or {}
    counts = audit.get('counts') or {}
    lines = [
        '# ChatGPT first-proof bundle audit',
        '',
        f"- generated_at: `{audit.get('generated_at')}`",
        f"- input: `{audit.get('input_path')}`",
        f"- input_sha256: `{audit.get('input_sha256')}`",
        f"- evaluator_schema_version: `{audit.get('evaluator_schema_version')}`",
        f"- evaluator_verdict: `{evaluator.get('verdict')}`",
        f"- evaluator_ok: `{evaluator.get('ok')}`",
        f"- winning_attempt_id: `{evaluator.get('winning_attempt_id')}`",
        f"- missing_required_checks: `{evaluator.get('missing_required_checks')}`",
        f"- action_record_count: `{counts.get('action_record_count')}`",
        f"- attempt_count: `{counts.get('attempt_count')}`",
        '',
        '## Attempt summaries',
        '',
    ]
    for attempt in audit.get('attempts') or []:
        lines.append(f"- `{attempt.get('attempt_id')}` actions={attempt.get('action_count')} seq={attempt.get('sequence_indices')} tabs={attempt.get('tab_ids')} conversations={attempt.get('conversation_route_paths')}")
    lines.extend(['', '## Operator notes', ''])
    for note in audit.get('operator_notes') or []:
        lines.append(f'- {note}')
    return '\n'.join(lines) + '\n'


def audit_file(input_path: Path, *, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    payload = read_json(input_path)
    audit = build_bundle_audit(payload, root=root, input_path=input_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'chatgpt-first-proof-bundle-audit.json', audit)
    (output_dir / 'SUMMARY.md').write_text(summary_markdown(audit), encoding='utf-8')
    return audit


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Audit a ChatGPT first-proof evidence bundle and render its local evidence graph.')
    parser.add_argument('--root', type=Path, default=ROOT)
    sub = parser.add_subparsers(dest='command')
    audit_cmd = sub.add_parser('audit', help='Audit a proof bundle JSON file')
    audit_cmd.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    audit_cmd.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    audit_cmd.add_argument('--pretty', action='store_true')
    audit_cmd.add_argument('--require-reviewable', action='store_true', help='Exit nonzero unless the evaluator summary is reviewable')
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in (None, 'audit'):
        input_path = getattr(args, 'input', DEFAULT_INPUT)
        output_dir = getattr(args, 'output_dir', DEFAULT_OUTPUT_DIR)
        audit = audit_file(input_path, root=args.root, output_dir=output_dir)
        print(json.dumps(audit, indent=2 if getattr(args, 'pretty', False) else None))
        if getattr(args, 'require_reviewable', False) and not (audit.get('evaluator_summary') or {}).get('ok'):
            return 1
        return 0
    parser.error(f'unknown command {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
