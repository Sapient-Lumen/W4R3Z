#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_test_contracts.json'
OUT_MD = ROOT / 'docs' / 'RUST_TEST_CONTRACTS.md'

TEST_DIR = ROOT / 'crates' / 'gr_engine' / 'tests'
SRC_DIR = ROOT / 'crates' / 'gr_engine' / 'src'

TEST_ATTR_RE = re.compile(r'^\s*#\[test\]\s*$')
FN_RE = re.compile(r'^\s*fn\s+([A-Za-z0-9_]+)\s*\(')
USE_RE = re.compile(r'^\s*use\s+gr_engine::([A-Za-z0-9_]+)', flags=re.MULTILINE)
CRATE_USE_RE = re.compile(r'^\s*use\s+crate::([A-Za-z0-9_]+)', flags=re.MULTILINE)
PROPTEST_BLOCK_RE = re.compile(r'proptest!\s*\{(?P<body>.*?)\n\}', flags=re.DOTALL)
PROPTEST_FN_RE = re.compile(r'#\[test\]\s*\n\s*fn\s+([A-Za-z0-9_]+)\s*\(')
ASSERT_EQ_RE = re.compile(r'assert_eq!\(')
UNWRAP_RE = re.compile(r'\.unwrap\(')

MODULES = sorted(path.stem for path in SRC_DIR.glob('*.rs'))


def path_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


class Contract(dict):
    pass


def extract_test_functions(text: str) -> list[tuple[str, int, int]]:
    lines = text.splitlines()
    out: list[tuple[str, int, int]] = []
    i = 0
    while i < len(lines):
        if TEST_ATTR_RE.match(lines[i]):
            j = i + 1
            while j < len(lines) and not FN_RE.match(lines[j]):
                j += 1
            if j >= len(lines):
                break
            match = FN_RE.match(lines[j])
            assert match is not None
            name = match.group(1)
            brace_depth = 0
            saw_open = False
            k = j
            while k < len(lines):
                brace_depth += lines[k].count('{')
                if lines[k].count('{'):
                    saw_open = True
                brace_depth -= lines[k].count('}')
                if saw_open and brace_depth <= 0:
                    out.append((name, j + 1, k + 1))
                    i = k
                    break
                k += 1
        i += 1
    return out


def extract_proptest_functions(text: str) -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    for block in PROPTEST_BLOCK_RE.finditer(text):
        block_text = block.group('body')
        start_offset = block.start('body')
        prefix = text[:start_offset]
        base_line = prefix.count('\n') + 1
        for match in PROPTEST_FN_RE.finditer(block_text):
            name = match.group(1)
            rel_line = block_text[:match.start()].count('\n')
            start_line = base_line + rel_line + 1
            tail = block_text[match.end():]
            extra_lines = tail.split('\n\n', 1)[0].count('\n') + 1
            out.append((name, start_line, start_line + extra_lines))
    return out


def infer_modules(path: Path, text: str) -> list[str]:
    mods = set(USE_RE.findall(text)) | set(CRATE_USE_RE.findall(text))
    stem = path.stem
    if stem in MODULES:
        mods.add(stem)
    elif stem.endswith('_run') and stem[:-4] in MODULES:
        mods.add(stem[:-4])
    elif stem.endswith('_spec') and stem[:-5] in MODULES:
        mods.add(stem[:-5])
    for module in MODULES:
        if f'gr_engine::{module}::' in text or f'crate::{module}::' in text:
            mods.add(module)
    return sorted(mods)


def infer_tags(name: str, body: str, path: Path) -> list[str]:
    lowered = f'{name} {body} {path.stem}'.lower()
    tags: set[str] = set()
    if any(token in lowered for token in ['deterministic', 'same_output', 'same_seed', 'same_task']):
        tags.add('determinism')
    if any(token in lowered for token in ['symmetry', 'swap_', 'swapp', 'player_swap']):
        tags.add('symmetry')
    if any(token in lowered for token in ['validation', 'validate', 'requires_', 'invalid_', 'unwrap_err', 'errors']):
        tags.add('validation')
    if any(token in lowered for token in ['diff_', '_diff_', 'changed', 'unchanged', 'first_diff']):
        tags.add('diff_consistency')
    if any(token in lowered for token in ['hash_', 'field_order', 'whitespace', 'formatting', 'hash_changed']):
        tags.add('hash_stability')
    if any(token in lowered for token in ['run_snapshot', 'build_snapshot', 'summarize_snapshot', 'snapshot_run']) or 'snapshot' in name.lower():
        tags.add('snapshot_embedding')
    if any(token in lowered for token in ['run_probe_suite', 'run_metamorphic_suite', 'run_scorecard_suite', 'validate_probe_suite', 'registry_and_suite', 'suite_']):
        tags.add('suite_execution')
    if any(token in lowered for token in ['geometric', 'termination', 'max_rounds', 'delta_', 'stats.rounds', 'rounds_summary']):
        tags.add('termination')
    if 'shrink_' in lowered:
        tags.add('shrinker')
    if any(token in lowered for token in ['assertion', 'passed', 'failures', 'skipped', 'warnings', 'failing']):
        tags.add('assertion_outcomes')
    if any(token in lowered for token in ['metamorphic', 'scaling_prefix']):
        tags.add('metamorphic')
    if ASSERT_EQ_RE.search(body) and 'determinism' not in tags and 'same' in lowered:
        tags.add('determinism')
    return sorted(tags)


def infer_signal(name: str, body: str, tags: list[str]) -> str:
    lowered = f'{name} {body}'.lower()
    if 'determinism' in tags:
        return 're-run and compare exact artifact equality'
    if 'symmetry' in tags:
        return 'swap players and confirm mirrored totals or skipped-ineligible behavior'
    if 'diff_consistency' in tags:
        return 'compare changed/unchanged and first-difference metadata'
    if 'validation' in tags:
        return 'feed invalid input and require structured error behavior'
    if 'hash_stability' in tags:
        return 'normalize formatting or field order and require stable hashes'
    if 'termination' in tags:
        return 'stress geometric/fixed stopping rules and rounds summaries'
    if 'shrinker' in tags:
        return 'minimize failing probes while preserving failure'
    if 'snapshot' in lowered:
        return 'confirm snapshot wiring or embedding survives round-trip execution'
    return 'replay contract once Rust lane returns and verify stated invariant still holds'


def summarize_contract(name: str, tags: list[str], modules: list[str]) -> str:
    if 'determinism' in tags:
        return 'deterministic rerun contract'
    if 'symmetry' in tags:
        return 'player-order symmetry contract'
    if 'diff_consistency' in tags:
        return 'artifact-diff consistency contract'
    if 'validation' in tags:
        return 'input-validation contract'
    if 'hash_stability' in tags:
        return 'hash/canonicalization stability contract'
    if 'termination' in tags:
        return 'termination/round-summary contract'
    if 'shrinker' in tags:
        return 'counterexample-shrinking contract'
    if 'snapshot_embedding' in tags:
        return 'snapshot embedding contract'
    if 'suite_execution' in tags:
        return 'suite orchestration contract'
    if modules:
        return f"{modules[0]} behavioral contract"
    return f'{name} contract'


def build_contract(path: Path, text: str, name: str, start_line: int, end_line: int, style: str) -> Contract:
    lines = text.splitlines()
    body = '\n'.join(lines[start_line - 1:end_line])
    modules = infer_modules(path, body)
    tags = infer_tags(name, body, path)
    return Contract(
        contract_id=f"{path.stem}:{name}",
        name=name,
        path=path.relative_to(ROOT).as_posix(),
        start_line=start_line,
        end_line=end_line,
        style=style,
        anchored_modules=modules,
        tags=tags,
        summary=summarize_contract(name, tags, modules),
        restart_signal=infer_signal(name, body, tags),
        uses_unwrap=bool(UNWRAP_RE.search(body)),
    )


def collect() -> dict[str, object]:
    contracts: list[Contract] = []
    for path in sorted(TEST_DIR.glob('*.rs')):
        text = path_text(path)
        proptests = extract_proptest_functions(text)
        proptest_start_lines = {start_line for _name, start_line, _end_line in proptests}
        for name, start_line, end_line in extract_test_functions(text):
            if start_line in proptest_start_lines:
                continue
            contracts.append(build_contract(path, text, name, start_line, end_line, 'external_test'))
        for name, start_line, end_line in proptests:
            contracts.append(build_contract(path, text, name, start_line, end_line, 'proptest'))
    for path in sorted(SRC_DIR.glob('*.rs')):
        text = path_text(path)
        if '#[cfg(test)]' not in text and '#[test]' not in text:
            continue
        for name, start_line, end_line in extract_test_functions(text):
            contracts.append(build_contract(path, text, name, start_line, end_line, 'inline_test'))
    seen = set()
    deduped: list[Contract] = []
    for row in contracts:
        key = (row['path'], row['name'], row['style'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    contracts = sorted(deduped, key=lambda row: (row['path'], row['start_line'], row['name']))
    family_counts = Counter(tag for row in contracts for tag in row['tags'])
    style_counts = Counter(row['style'] for row in contracts)
    module_rows = []
    anchored_by_module: dict[str, list[Contract]] = defaultdict(list)
    for row in contracts:
        for module in row['anchored_modules']:
            anchored_by_module[module].append(row)
    for module in sorted(MODULES):
        anchored = sorted(anchored_by_module[module], key=lambda row: (row['path'], row['start_line'], row['name']))
        family_cov = Counter(tag for row in anchored for tag in row['tags'])
        module_rows.append({
            'module': module,
            'contract_count': len(anchored),
            'contract_ids': [row['contract_id'] for row in anchored],
            'styles': dict(sorted(Counter(row['style'] for row in anchored).items())),
            'family_counts': dict(sorted(family_cov.items())),
            'priority_score': len(anchored) * 3 + len(family_cov) * 2 + sum(1 for row in anchored if row['style'] == 'inline_test'),
        })
    priority_modules = sorted(module_rows, key=lambda row: (-row['priority_score'], -row['contract_count'], row['module']))
    return {
        'inventory_version': '2026-03-23.rust_test_contracts.v1',
        'scope': {
            'crate': 'gr_engine',
            'external_test_glob': 'crates/gr_engine/tests/*.rs',
            'src_glob': 'crates/gr_engine/src/*.rs',
            'method': 'static_test_function_scan',
            'limitations': [
                'This ledger is source-text based and does not invoke rustc, cargo, macro expansion, or runtime execution.',
                'Contract families are heuristic tags inferred from test names and local source text.',
                'Anchored modules are approximated from use-paths and file stems, so cross-module helper coverage can be undercounted or over-attributed.',
            ],
        },
        'summary': {
            'contract_count': len(contracts),
            'style_counts': dict(sorted(style_counts.items())),
            'family_counts': dict(sorted(family_counts.items())),
            'modules_with_contracts': sum(1 for row in module_rows if row['contract_count'] > 0),
            'top_priority_module': priority_modules[0]['module'] if priority_modules else None,
        },
        'priority_modules': priority_modules,
        'contracts': contracts,
    }


def render_markdown(inventory: dict[str, object]) -> str:
    summary = inventory['summary']
    priority_modules = inventory['priority_modules']
    contracts = inventory['contracts']
    lines = [
        '# Rust Test Contracts',
        '',
        'Generated by `scripts/report/build_rust_test_contracts.py`. This is a static contract ledger for Rust-blocked sessions; it does not replace `cargo test`, property tests, or compiled CLI reruns.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- contracts_seen: {summary['contract_count']}",
        f"- top_priority_module: `{summary['top_priority_module']}`",
        f"- modules_with_contracts: {summary['modules_with_contracts']}",
        '',
        'Style counts:',
        '',
    ]
    for kind, count in summary['style_counts'].items():
        lines.append(f'- `{kind}`: {count}')
    lines.extend(['', 'Family counts:', ''])
    for kind, count in summary['family_counts'].items():
        lines.append(f'- `{kind}`: {count}')
    lines.extend([
        '', '## Priority rerun modules', '',
        'When the Rust lane returns, these modules provide the densest contract surface per static scan. Re-run their tests first because they cover the widest mix of invariants.',
        '', '| module | priority_score | contracts | family coverage | why rerun first |', '|---|---:|---:|---|---|',
    ])
    for row in priority_modules[:10]:
        fams = ', '.join(f'`{k}`×{v}' for k, v in row['family_counts'].items()) or '—'
        why = []
        if row['contract_count']:
            why.append(f"{row['contract_count']} contracts")
        if row['styles']:
            why.append(', '.join(f"{k}={v}" for k, v in row['styles'].items()))
        lines.append(f"| `{row['module']}` | {row['priority_score']} | {row['contract_count']} | {fams} | {'; '.join(why)} |")
    lines.extend(['', '## Contract ledger', '', '| contract | style | anchored modules | families | restart signal |', '|---|---|---|---|---|'])
    for row in contracts:
        modules = ', '.join(f"`{m}`" for m in row['anchored_modules']) or '—'
        tags = ', '.join(f"`{t}`" for t in row['tags']) or '—'
        lines.append(f"| `{row['name']}` | `{row['style']}` | {modules} | {tags} | {row['restart_signal']} |")
    lines.extend([
        '', '## Practical interpretation for Rust-blocked sessions', '',
        '1. Use the priority rerun table to choose the first `cargo test <target>` slice when a real Rust machine becomes available.',
        '2. Treat this ledger as a behavior map: it preserves what the tests are trying to guarantee, not just which files exist.',
        '3. Prefer families with many contracts (`determinism`, `diff_consistency`, `validation`) when deciding where a regression could silently break multiple archive promises.',
        '4. Keep the ledger generated and compact; do not preserve copied Rust test bodies in the archive.',
    ])
    return '\n'.join(lines) + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    inventory = collect()
    js = json.dumps(inventory, indent=2, sort_keys=False) + '\n'
    md = render_markdown(inventory)
    if args.write:
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
        print(f'wrote {OUT_MD.relative_to(ROOT).as_posix()}')
        return 0
    ok = True
    if not OUT_JSON.exists() or OUT_JSON.read_text(encoding='utf-8') != js:
        print(f'rust-test-contracts: stale {OUT_JSON.relative_to(ROOT).as_posix()}', file=sys.stderr)
        ok = False
    if not OUT_MD.exists() or OUT_MD.read_text(encoding='utf-8') != md:
        print(f'rust-test-contracts: stale {OUT_MD.relative_to(ROOT).as_posix()}', file=sys.stderr)
        ok = False
    if ok:
        print('rust-test-contracts: ok')
        return 0
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
