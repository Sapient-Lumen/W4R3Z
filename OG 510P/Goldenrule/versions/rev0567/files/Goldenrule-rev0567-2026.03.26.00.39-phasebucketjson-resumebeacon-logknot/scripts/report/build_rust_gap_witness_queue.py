#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

from build_rust_test_scenario_coverage import collect as collect_scenario_coverage

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_gap_witness_queue.json'
OUT_MD = ROOT / 'docs' / 'RUST_GAP_WITNESS_QUEUE.md'

SEARCH_ROOTS = [
    ROOT / 'examples',
    ROOT / 'crates' / 'gr_engine' / 'src',
    ROOT / 'crates' / 'gr_engine' / 'tests',
    ROOT / 'docs' / 'LIBRARY',
    ROOT / 'Original-Starting-Place',
]
SEARCH_EXTS = {'.rs', '.json', '.md', '.yaml', '.yml', '.toml'}
EXCLUDED_PATHS = {
    'docs/RUST_SURFACE_INVENTORY.md',
    'docs/RUST_RESTART_MAP.md',
    'docs/RUST_TEST_CONTRACTS.md',
    'docs/RUST_TEST_SCENARIO_COVERAGE.md',
    'docs/RUST_GAP_WITNESS_QUEUE.md',
    'docs/AGENT_LOG.md',
    'CHANGELOG.md',
}

STATUS_PRIORITY = {'unseen': 0, 'inline_only': 1, 'sparse': 2}
WITNESS_TYPE_PRIORITY = {'example': 0, 'rust_test': 1, 'rust_source': 2, 'design_doc': 3}
EXAMPLE_KIND_PRIORITY = {
    'examples/probes/direct': 0,
    'examples/probes/holdouts': 1,
    'examples/probes/registry': 2,
    'examples/worlds': 3,
    'examples/strategies': 4,
    'examples/metamorphic': 5,
    'examples/snapshots': 6,
    'examples/scorecards': 7,
    'examples': 8,
}


def snake_to_camel(text: str) -> str:
    return ''.join(part.title() for part in text.split('_'))


def extra_tokens(family: str, variant: str) -> list[str]:
    del family
    return [snake_to_camel(variant), variant]


def classify_path(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith('examples/'):
        return 'example'
    if rel.startswith('crates/gr_engine/tests/'):
        return 'rust_test'
    if rel.startswith('crates/gr_engine/src/'):
        return 'rust_source'
    return 'design_doc'


def example_kind(rel_path: str) -> str:
    if rel_path.startswith('examples/probes/holdouts/'):
        return 'examples/probes/holdouts'
    if rel_path.startswith('examples/probes/registry'):
        return 'examples/probes/registry'
    if rel_path.startswith('examples/probes/'):
        return 'examples/probes/direct'
    for prefix in ('examples/worlds', 'examples/strategies', 'examples/metamorphic', 'examples/snapshots', 'examples/scorecards', 'examples'):
        if rel_path.startswith(prefix):
            return prefix
    return 'examples'


def example_probe_loadability(rel_path: str) -> str:
    payload = load_json_object(rel_path)
    if not isinstance(payload, dict):
        return 'non_json'
    if 'world' not in payload or 'matchups' not in payload:
        return 'not_probe_like'
    matchups = payload.get('matchups')
    if not isinstance(matchups, list) or not matchups:
        return 'not_probe_like'
    saw_null_strategy = False
    for matchup in matchups:
        if not isinstance(matchup, dict):
            return 'not_probe_like'
        for slot in ('strategy_a', 'strategy_b'):
            strategy = matchup.get(slot)
            if strategy is None:
                saw_null_strategy = True
                continue
            if not isinstance(strategy, dict):
                return 'not_probe_like'
    if saw_null_strategy:
        return 'probe_template'
    return 'direct_probe'


@lru_cache(maxsize=None)
def load_json_object(path: str) -> object | None:
    full = ROOT / path
    if not full.exists():
        return None
    try:
        return json.loads(full.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def has_exact_example_match(payload: object, family: str, variant: str, trail: tuple[str, ...] = ()) -> bool:
    if isinstance(payload, dict):
        if family == 'strategy_family' and payload.get('family') == variant:
            return True
        if family == 'noise_kind' and trail and trail[-1] == 'noise' and payload.get('kind') == variant:
            return True
        if family == 'reputation_kind' and trail and trail[-1] == 'reputation' and payload.get('kind') == variant:
            return True
        if family == 'assertion_kind' and 'assertions' in trail and payload.get('kind') == variant:
            return True
        if family == 'metamorphic_kind' and payload.get('kind') == variant and ('probe' in payload or 'scaling_prefix' in payload):
            return True
        if family == 'standing_update_rule' and 'update_rule' in payload:
            update_rule = payload['update_rule']
            if isinstance(update_rule, str) and update_rule == variant:
                return True
            if isinstance(update_rule, dict) and variant in update_rule:
                return True
        for key, value in payload.items():
            if has_exact_example_match(value, family, variant, trail + (str(key),)):
                return True
        return False
    if isinstance(payload, list):
        return any(has_exact_example_match(item, family, variant, trail) for item in payload)
    return False


def example_exact_variant_match(rel_path: str, family: str, variant: str) -> bool:
    payload = load_json_object(rel_path)
    if payload is None:
        return False
    return has_exact_example_match(payload, family, variant)


def collect_candidate_paths() -> list[Path]:
    paths: list[Path] = []
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob('*'):
            if not path.is_file() or path.suffix not in SEARCH_EXTS:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in EXCLUDED_PATHS:
                continue
            paths.append(path)
    return sorted(paths)


def scan_witnesses(family: str, variant: str, candidates: list[Path]) -> list[dict[str, object]]:
    tokens = extra_tokens(family, variant)
    lowered_tokens = [token.lower() for token in tokens]
    witnesses: list[dict[str, object]] = []
    for path in candidates:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding='utf-8')
        first_hit_line = None
        first_hit_token = None
        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            for raw, lowered_token in zip(tokens, lowered_tokens):
                if lowered_token in lowered:
                    first_hit_line = line_no
                    first_hit_token = raw
                    break
            if first_hit_line is not None:
                break
        if first_hit_line is None:
            continue
        witness_type = classify_path(path)
        row = {
            'path': rel,
            'line': first_hit_line,
            'kind': witness_type,
            'match_token': first_hit_token,
        }
        if witness_type == 'example':
            row['example_kind'] = example_kind(rel)
            row['exact_variant_match'] = example_exact_variant_match(rel, family, variant)
            row['probe_loadability'] = example_probe_loadability(rel)
        witnesses.append(row)
    witnesses.sort(
        key=lambda row: (
            WITNESS_TYPE_PRIORITY[row['kind']],
            0 if str(row.get('probe_loadability', '')) == 'direct_probe' else (1 if str(row.get('probe_loadability', '')) == 'probe_template' else 2),
            EXAMPLE_KIND_PRIORITY.get(str(row.get('example_kind', '')), 99),
            0 if bool(row.get('exact_variant_match', False)) else 1,
            str(row['path']),
            int(row['line']),
        )
    )
    return witnesses


def classify_readiness(witness_counts: Counter[str]) -> str:
    if witness_counts['example'] > 0:
        return 'fixture_ready'
    if witness_counts['rust_source'] > 0 or witness_counts['rust_test'] > 0:
        return 'source_ready'
    if witness_counts['design_doc'] > 0:
        return 'doc_ready'
    return 'no_witness'


def suggested_action(status: str, readiness: str, family: str) -> str:
    if status == 'inline_only':
        return 'promote the inline-only scenario into an external Rust test so it survives outside source-local test code'
    if readiness == 'fixture_ready':
        if family == 'assertion_kind':
            return 'lift an existing example with a nearby assertion surface into a dedicated external Rust assertion test'
        return 'promote an existing example witness into a dedicated external Rust test before inventing new fixtures'
    if readiness == 'source_ready':
        return 'encode one minimal JSON fixture/example for this declared variant, then attach an external Rust test to it'
    if readiness == 'doc_ready':
        return 'translate the design-only semantic into the first executable fixture, then add a narrow Rust test'
    return 'create the first explicit fixture and external Rust test anchor for this gap'


def command_hint(tokens: list[str]) -> str:
    pattern = '|'.join(re.escape(piece) for piece in tokens if piece)
    return f"rg -n '{pattern}' examples crates/gr_engine docs Original-Starting-Place"


def compact_witnesses(rows: list[dict[str, object]], kind: str, limit: int) -> list[str]:
    chosen = [row for row in rows if row['kind'] == kind][:limit]
    return [f"{row['path']}:{row['line']}" for row in chosen]


def build_queue() -> dict[str, object]:
    scenario = collect_scenario_coverage()
    attention = list(scenario['attention_queue'])
    candidates = collect_candidate_paths()
    queue: list[dict[str, object]] = []
    readiness_counts: Counter[str] = Counter()
    for row in attention:
        family = str(row['family'])
        variant = str(row['variant'])
        status = str(row['status'])
        tokens = extra_tokens(family, variant)
        witnesses = scan_witnesses(family, variant, candidates)
        witness_counts: Counter[str] = Counter(str(item['kind']) for item in witnesses)
        readiness = classify_readiness(witness_counts)
        readiness_counts[readiness] += 1
        queue.append(
            {
                'family': family,
                'variant': variant,
                'status': status,
                'contract_count': int(row['contract_count']),
                'sample_contract_ids': list(row['sample_contract_ids']),
                'search_tokens': tokens,
                'readiness': readiness,
                'witness_counts': {
                    'example': witness_counts['example'],
                    'rust_test': witness_counts['rust_test'],
                    'rust_source': witness_counts['rust_source'],
                    'design_doc': witness_counts['design_doc'],
                },
                'example_witnesses': compact_witnesses(witnesses, 'example', 4),
                'rust_test_witnesses': compact_witnesses(witnesses, 'rust_test', 3),
                'rust_source_witnesses': compact_witnesses(witnesses, 'rust_source', 3),
                'design_doc_witnesses': compact_witnesses(witnesses, 'design_doc', 3),
                'suggested_action': suggested_action(status, readiness, family),
                'command_hint': command_hint(tokens),
            }
        )
    queue.sort(
        key=lambda row: (
            STATUS_PRIORITY[row['status']],
            {'fixture_ready': 0, 'source_ready': 1, 'doc_ready': 2, 'no_witness': 3}[row['readiness']],
            -row['witness_counts']['example'],
            -row['witness_counts']['rust_source'],
            row['family'],
            row['variant'],
        )
    )
    return {
        'metadata': {
            'inventory_version': '2026-03-23.rust_gap_witness_queue.v1',
            'crate': 'gr_engine',
            'source_attention_entries': len(attention),
            'search_roots': [path.relative_to(ROOT).as_posix() for path in SEARCH_ROOTS],
            'excluded_paths': sorted(EXCLUDED_PATHS),
        },
        'summary': {
            'queue_entries': len(queue),
            'fixture_ready': readiness_counts['fixture_ready'],
            'source_ready': readiness_counts['source_ready'],
            'doc_ready': readiness_counts['doc_ready'],
            'no_witness': readiness_counts['no_witness'],
            'unseen_entries': sum(1 for row in queue if row['status'] == 'unseen'),
            'inline_only_entries': sum(1 for row in queue if row['status'] == 'inline_only'),
            'sparse_entries': sum(1 for row in queue if row['status'] == 'sparse'),
        },
        'priority_queue': queue,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report['summary']
    queue = report['priority_queue']
    lines = [
        '# Rust Gap Witness Queue',
        '',
        'Generated by `scripts/report/build_rust_gap_witness_queue.py`. This is a static bridge from the Rust scenario-gap ledger to concrete repo witnesses that can seed future external Rust tests once a real toolchain returns.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- queue_entries: {summary['queue_entries']}",
        f"- fixture_ready: {summary['fixture_ready']}",
        f"- source_ready: {summary['source_ready']}",
        f"- doc_ready: {summary['doc_ready']}",
        f"- no_witness: {summary['no_witness']}",
        f"- unseen_entries: {summary['unseen_entries']}",
        f"- inline_only_entries: {summary['inline_only_entries']}",
        f"- sparse_entries: {summary['sparse_entries']}",
        '',
        '## Priority queue',
        '',
        'Treat this as a restart helper for the eventual Rust-capable inheritor: it says which weak scenario rows already have nearby fixtures/examples/source anchors, and therefore which tests can likely be revived fastest.',
        '',
        '| family | variant | status | readiness | example seeds | source anchors | suggested action |',
        '|---|---|---|---|---:|---:|---|',
    ]
    for row in queue:
        source_anchors = row['witness_counts']['rust_source'] + row['witness_counts']['rust_test'] + row['witness_counts']['design_doc']
        lines.append(
            f"| `{row['family']}` | `{row['variant']}` | `{row['status']}` | `{row['readiness']}` | {row['witness_counts']['example']} | {source_anchors} | {row['suggested_action']} |"
        )
    lines.extend([
        '',
        '## Ready-to-lift gaps',
        '',
        'These rows already have example witnesses, so the next inheritor can probably write a targeted external Rust test without first inventing new fixtures.',
        '',
        '| family | variant | status | example witnesses | sample contracts |',
        '|---|---|---|---|---|',
    ])
    ready_rows = [row for row in queue if row['readiness'] == 'fixture_ready']
    for row in ready_rows:
        witnesses = ', '.join(f'`{item}`' for item in row['example_witnesses']) or '—'
        contracts = ', '.join(f'`{item}`' for item in row['sample_contract_ids']) or '—'
        lines.append(f"| `{row['family']}` | `{row['variant']}` | `{row['status']}` | {witnesses} | {contracts} |")
    if not ready_rows:
        lines.append('| — | — | — | — | — |')
    lines.extend([
        '',
        '## Source-first gaps',
        '',
        'These rows have no example fixtures yet, but the variant is already declared or handled in Rust source. They are good candidates for “add one minimal fixture, then one external test.”',
        '',
        '| family | variant | status | rust/source witnesses | command hint |',
        '|---|---|---|---|---|',
    ])
    source_rows = [row for row in queue if row['readiness'] == 'source_ready']
    for row in source_rows:
        witnesses = row['rust_source_witnesses'] + row['rust_test_witnesses']
        witness_text = ', '.join(f'`{item}`' for item in witnesses[:4]) or '—'
        lines.append(f"| `{row['family']}` | `{row['variant']}` | `{row['status']}` | {witness_text} | `{row['command_hint']}` |")
    if not source_rows:
        lines.append('| — | — | — | — | — |')
    lines.extend([
        '',
        '## Per-gap witness details',
        '',
    ])
    for row in queue:
        lines.extend([
            f"### `{row['family']}` / `{row['variant']}`",
            '',
            f"- status: `{row['status']}`",
            f"- readiness: `{row['readiness']}`",
            f"- contracts_seen: {row['contract_count']}",
            f"- sample_contract_ids: {', '.join(f'`{item}`' for item in row['sample_contract_ids']) or 'none'}",
            f"- search_tokens: {', '.join(f'`{item}`' for item in row['search_tokens'])}",
            f"- suggested_action: {row['suggested_action']}",
            f"- command_hint: `{row['command_hint']}`",
            f"- example_witnesses: {', '.join(f'`{item}`' for item in row['example_witnesses']) or 'none'}",
            f"- rust_test_witnesses: {', '.join(f'`{item}`' for item in row['rust_test_witnesses']) or 'none'}",
            f"- rust_source_witnesses: {', '.join(f'`{item}`' for item in row['rust_source_witnesses']) or 'none'}",
            f"- design_doc_witnesses: {', '.join(f'`{item}`' for item in row['design_doc_witnesses']) or 'none'}",
            '',
        ])
    lines.extend([
        '## Practical interpretation for Rust-blocked sessions',
        '',
        '1. Prefer `fixture_ready` gaps first: they already have example material in the repo, so the later Rust-capable pass can add tests without reopening the semantics search.',
        '2. Treat `source_ready` gaps as declaration-rich but fixture-poor: the implementation knows about them, but the examples/tests lag behind.',
        '3. Use the `command_hint` only as a local locator; do not preserve large copied snippets in the archive.',
        '4. Keep this queue generated and compact. It should point to anchors, not duplicate them.',
    ])
    return '\n'.join(lines) + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    report = build_queue()
    js = json.dumps(report, indent=2, sort_keys=False) + '\n'
    md = render_markdown(report)
    if args.write:
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f"wrote {OUT_JSON.relative_to(ROOT).as_posix()}")
        print(f"wrote {OUT_MD.relative_to(ROOT).as_posix()}")
        return 0
    ok = True
    if not OUT_JSON.exists() or OUT_JSON.read_text(encoding='utf-8') != js:
        print(f"rust-gap-witness-queue: stale {OUT_JSON.relative_to(ROOT).as_posix()}", file=sys.stderr)
        ok = False
    if not OUT_MD.exists() or OUT_MD.read_text(encoding='utf-8') != md:
        print(f"rust-gap-witness-queue: stale {OUT_MD.relative_to(ROOT).as_posix()}", file=sys.stderr)
        ok = False
    if ok:
        print('rust-gap-witness-queue: ok')
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
