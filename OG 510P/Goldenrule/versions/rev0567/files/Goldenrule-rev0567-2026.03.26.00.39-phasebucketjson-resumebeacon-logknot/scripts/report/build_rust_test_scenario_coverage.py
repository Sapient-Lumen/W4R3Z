#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_test_scenario_coverage.json'
OUT_MD = ROOT / 'docs' / 'RUST_TEST_SCENARIO_COVERAGE.md'

TEST_DIR = ROOT / 'crates' / 'gr_engine' / 'tests'
SRC_DIR = ROOT / 'crates' / 'gr_engine' / 'src'
SPEC_PATH = SRC_DIR / 'spec.rs'
PROBE_PATH = SRC_DIR / 'probe.rs'
METAMORPHIC_PATH = SRC_DIR / 'metamorphic.rs'

TEST_ATTR_RE = re.compile(r'^\s*#\[test\]\s*$')
FN_RE = re.compile(r'^\s*fn\s+([A-Za-z0-9_]+)\s*\(')
PROPTEST_BLOCK_RE = re.compile(r'proptest!\s*\{(?P<body>.*?)\n\}', flags=re.DOTALL)
PROPTEST_FN_RE = re.compile(r'#\[test\]\s*\n\s*fn\s+([A-Za-z0-9_]+)\s*\(')

RUST_FAMILY_PATTERNS = {
    'game_kind': re.compile(r'GameSpec::([A-Za-z0-9_]+)'),
    'noise_kind': re.compile(r'NoiseModelSpec::([A-Za-z0-9_]+)'),
    'termination_kind': re.compile(r'TerminationRuleSpec::([A-Za-z0-9_]+)'),
    'reputation_kind': re.compile(r'ReputationModelSpec::([A-Za-z0-9_]+)'),
    'standing_update_rule': re.compile(r'StandingUpdateRule::([A-Za-z0-9_]+)'),
    'strategy_family': re.compile(r'StrategySpec::([A-Za-z0-9_]+)'),
    'builtin_kind': re.compile(r'BuiltinKind::([A-Za-z0-9_]+)'),
    'assertion_kind': re.compile(r'AssertionSpec::([A-Za-z0-9_]+)'),
    'metamorphic_kind': re.compile(r'MetamorphicKind::([A-Za-z0-9_]+)'),
}

JSON_CONTEXT_PATTERNS = {
    'game_kind': re.compile(r'"game"\s*:\s*\{.*?"kind"\s*:\s*"([a-z_]+)"', flags=re.DOTALL),
    'noise_kind': re.compile(r'"noise"\s*:\s*\{.*?"kind"\s*:\s*"([a-z_]+)"', flags=re.DOTALL),
    'termination_kind': re.compile(r'"termination"\s*:\s*\{.*?"kind"\s*:\s*"([a-z_]+)"', flags=re.DOTALL),
    'reputation_kind': re.compile(r'"reputation"\s*:\s*\{.*?"kind"\s*:\s*"([a-z_]+)"', flags=re.DOTALL),
    'standing_update_rule': re.compile(r'"update_rule"\s*:\s*\{.*?"kind"\s*:\s*"([a-z_]+)"', flags=re.DOTALL),
    'strategy_family': re.compile(r'"family"\s*:\s*"([a-z_]+)"'),
}


def path_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


class Contract(dict):
    pass


def snake_case(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def extract_block(text: str, start_offset: int) -> str:
    open_index = text.find('{', start_offset)
    if open_index < 0:
        return ''
    depth = 0
    for idx in range(open_index, len(text)):
        ch = text[idx]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[open_index + 1:idx]
    return ''


def extract_enum_variants(path: Path, enum_name: str) -> list[str]:
    text = path_text(path)
    match = re.search(rf'pub\s+enum\s+{re.escape(enum_name)}\s*\{{', text)
    if not match:
        raise ValueError(f'could not find enum {enum_name} in {path}')
    body = extract_block(text, match.start())
    variants: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('#['):
            continue
        variant_match = re.match(r'([A-Z][A-Za-z0-9_]*)\b', stripped)
        if variant_match:
            variants.append(snake_case(variant_match.group(1)))
    deduped: list[str] = []
    seen = set()
    for variant in variants:
        if variant not in seen:
            deduped.append(variant)
            seen.add(variant)
    return deduped


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


def build_contract(path: Path, name: str, start_line: int, end_line: int, style: str, text: str) -> Contract:
    body = '\n'.join(text.splitlines()[start_line - 1:end_line])
    return Contract(
        contract_id=f'{path.stem}:{name}',
        name=name,
        path=path.relative_to(ROOT).as_posix(),
        style=style,
        start_line=start_line,
        end_line=end_line,
        body=body,
    )


def collect_contracts() -> list[Contract]:
    contracts: list[Contract] = []
    for path in sorted(TEST_DIR.glob('*.rs')):
        text = path_text(path)
        proptests = extract_proptest_functions(text)
        proptest_start_lines = {start_line for _name, start_line, _end_line in proptests}
        for name, start_line, end_line in extract_test_functions(text):
            if start_line in proptest_start_lines:
                continue
            contracts.append(build_contract(path, name, start_line, end_line, 'external_test', text))
        for name, start_line, end_line in proptests:
            contracts.append(build_contract(path, name, start_line, end_line, 'proptest', text))
    for path in sorted(SRC_DIR.glob('*.rs')):
        text = path_text(path)
        if '#[cfg(test)]' not in text and '#[test]' not in text:
            continue
        for name, start_line, end_line in extract_test_functions(text):
            contracts.append(build_contract(path, name, start_line, end_line, 'inline_test', text))
    deduped: list[Contract] = []
    seen = set()
    for row in contracts:
        key = (row['path'], row['name'], row['style'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return sorted(deduped, key=lambda row: (row['path'], row['start_line'], row['name']))


FAMILY_UNIVERSE = {
    'game_kind': lambda: extract_enum_variants(SPEC_PATH, 'GameSpec'),
    'noise_kind': lambda: extract_enum_variants(SPEC_PATH, 'NoiseModelSpec'),
    'termination_kind': lambda: extract_enum_variants(SPEC_PATH, 'TerminationRuleSpec'),
    'reputation_kind': lambda: extract_enum_variants(SPEC_PATH, 'ReputationModelSpec'),
    'standing_update_rule': lambda: extract_enum_variants(SPEC_PATH, 'StandingUpdateRule'),
    'strategy_family': lambda: extract_enum_variants(SPEC_PATH, 'StrategySpec'),
    'builtin_kind': lambda: extract_enum_variants(SPEC_PATH, 'BuiltinKind'),
    'assertion_kind': lambda: extract_enum_variants(PROBE_PATH, 'AssertionSpec'),
    'metamorphic_kind': lambda: extract_enum_variants(METAMORPHIC_PATH, 'MetamorphicKind'),
}


FAMILY_TITLES = {
    'game_kind': 'Game kinds',
    'noise_kind': 'Noise models',
    'termination_kind': 'Termination rules',
    'reputation_kind': 'Reputation models',
    'standing_update_rule': 'Standing update rules',
    'strategy_family': 'Strategy families',
    'builtin_kind': 'Builtin strategy kinds',
    'assertion_kind': 'Assertion kinds',
    'metamorphic_kind': 'Metamorphic check kinds',
}


def extract_family_variants(body: str, family: str, declared: list[str]) -> list[str]:
    variants: set[str] = set()
    rust_pattern = RUST_FAMILY_PATTERNS.get(family)
    if rust_pattern is not None:
        for match in rust_pattern.findall(body):
            token = snake_case(match)
            if token in declared:
                variants.add(token)
    json_pattern = JSON_CONTEXT_PATTERNS.get(family)
    if json_pattern is not None:
        for match in json_pattern.findall(body):
            if match in declared:
                variants.add(match)
    if family in {'builtin_kind', 'assertion_kind', 'metamorphic_kind'}:
        for token in declared:
            if token != 'none' and (f'"{token}"' in body or token in body):
                variants.add(token)
    return sorted(variants)


def collect() -> dict[str, object]:
    declared_by_family = {family: loader() for family, loader in FAMILY_UNIVERSE.items()}
    contracts = collect_contracts()
    summary_style_counts = Counter(row['style'] for row in contracts)
    family_rows = []
    all_variant_rows = []
    attention: list[dict[str, object]] = []

    for family, declared in declared_by_family.items():
        variant_to_contracts: dict[str, list[dict[str, object]]] = defaultdict(list)
        for contract in contracts:
            matched = extract_family_variants(str(contract['body']), family, declared)
            for token in matched:
                variant_to_contracts[token].append({
                    'contract_id': contract['contract_id'],
                    'path': contract['path'],
                    'name': contract['name'],
                    'style': contract['style'],
                })

        observed_total = 0
        inline_only = []
        unseen = []
        sparse = []
        variant_rows = []
        for token in declared:
            hits = sorted(
                variant_to_contracts.get(token, []),
                key=lambda row: (row['path'], row['name'], row['style']),
            )
            observed_total += len(hits)
            style_counts = Counter(row['style'] for row in hits)
            status = 'covered'
            if not hits:
                status = 'unseen'
                unseen.append(token)
            elif set(style_counts) == {'inline_test'}:
                status = 'inline_only'
                inline_only.append(token)
            elif len(hits) <= 2:
                status = 'sparse'
                sparse.append(token)
            variant_row = {
                'variant': token,
                'status': status,
                'contract_count': len(hits),
                'style_counts': dict(sorted(style_counts.items())),
                'sample_contract_ids': [row['contract_id'] for row in hits[:3]],
            }
            variant_rows.append(variant_row)
            all_variant_rows.append({'family': family, **variant_row})
            if status in {'unseen', 'inline_only', 'sparse'}:
                attention.append({
                    'family': family,
                    'variant': token,
                    'status': status,
                    'contract_count': len(hits),
                    'style_counts': dict(sorted(style_counts.items())),
                    'sample_contract_ids': [row['contract_id'] for row in hits[:3]],
                })

        family_rows.append({
            'family': family,
            'title': FAMILY_TITLES[family],
            'declared_variant_count': len(declared),
            'observed_variant_count': sum(1 for row in variant_rows if row['contract_count'] > 0),
            'observed_contract_mentions': observed_total,
            'coverage_ratio': round(sum(1 for row in variant_rows if row['contract_count'] > 0) / len(declared), 3) if declared else 0.0,
            'unseen_variants': unseen,
            'inline_only_variants': inline_only,
            'sparse_variants': sparse,
            'variants': variant_rows,
        })

    attention.sort(key=lambda row: ({'unseen': 0, 'inline_only': 1, 'sparse': 2}.get(row['status'], 9), row['family'], row['variant']))
    dominant_rows = sorted(
        (row for row in all_variant_rows if row['contract_count'] > 0),
        key=lambda row: (-row['contract_count'], row['family'], row['variant']),
    )[:10]

    return {
        'metadata': {
            'crate': 'gr_engine',
            'method': 'static_rust_test_scenario_scan',
            'external_test_glob': 'crates/gr_engine/tests/*.rs',
            'src_glob': 'crates/gr_engine/src/*.rs',
            'limitations': [
                'This ledger is source-text based and does not invoke rustc, cargo, macro expansion, or runtime execution.',
                'Scenario matches are heuristic and can miss values hidden behind helpers, defaults, or macro expansion.',
                'JSON-style extraction is context-aware for world/spec fields but intentionally approximate to keep the report compact.',
            ],
        },
        'summary': {
            'contract_count': len(contracts),
            'style_counts': dict(sorted(summary_style_counts.items())),
            'families_tracked': len(family_rows),
            'families_with_unseen_variants': sum(1 for row in family_rows if row['unseen_variants']),
            'families_with_inline_only_variants': sum(1 for row in family_rows if row['inline_only_variants']),
            'families_with_sparse_variants': sum(1 for row in family_rows if row['sparse_variants']),
        },
        'dominant_variants': dominant_rows,
        'attention_queue': attention,
        'families': family_rows,
    }


def render_markdown(report: dict[str, object]) -> str:
    summary = report['summary']
    dominant_rows = report['dominant_variants']
    attention = report['attention_queue']
    families = report['families']
    lines = [
        '# Rust Test Scenario Coverage',
        '',
        'Generated by `scripts/report/build_rust_test_scenario_coverage.py`. This is a static scenario-coverage ledger for Rust-blocked sessions; it preserves what kinds of worlds/strategies/assertions the Rust tests mention, not what has been revalidated at runtime.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- contracts_seen: {summary['contract_count']}",
        f"- families_tracked: {summary['families_tracked']}",
        f"- families_with_unseen_variants: {summary['families_with_unseen_variants']}",
        f"- families_with_inline_only_variants: {summary['families_with_inline_only_variants']}",
        f"- families_with_sparse_variants: {summary['families_with_sparse_variants']}",
        '',
        'Style counts:',
        '',
    ]
    for kind, count in summary['style_counts'].items():
        lines.append(f'- `{kind}`: {count}')
    lines.extend([
        '',
        '## Dominant observed variants',
        '',
        'These are the scenario values that dominate the current test corpus. Strong dominance is useful signal for what the archive protects well, but it also reveals where the test surface may be biased.',
        '',
        '| family | variant | contracts | styles |',
        '|---|---|---:|---|',
    ])
    for row in dominant_rows:
        styles = ', '.join(f"`{k}`×{v}" for k, v in row['style_counts'].items()) or '—'
        lines.append(f"| `{row['family']}` | `{row['variant']}` | {row['contract_count']} | {styles} |")
    lines.extend([
        '',
        '## Attention queue',
        '',
        'These are the highest-leverage scenario gaps or weak spots for the eventual Rust-capable inheritor.',
        '',
        '| family | variant | status | contracts | evidence anchor |',
        '|---|---|---|---:|---|',
    ])
    for row in attention[:20]:
        anchor = ', '.join(f"`{item}`" for item in row['sample_contract_ids']) or '—'
        lines.append(f"| `{row['family']}` | `{row['variant']}` | `{row['status']}` | {row['contract_count']} | {anchor} |")
    for family in families:
        lines.extend([
            '',
            f"## {family['title']}",
            '',
            f"- declared_variants: {family['declared_variant_count']}",
            f"- observed_variants: {family['observed_variant_count']}",
            f"- coverage_ratio: {family['coverage_ratio']}",
            f"- unseen_variants: {', '.join(f'`{item}`' for item in family['unseen_variants']) or 'none'}",
            f"- inline_only_variants: {', '.join(f'`{item}`' for item in family['inline_only_variants']) or 'none'}",
            f"- sparse_variants: {', '.join(f'`{item}`' for item in family['sparse_variants']) or 'none'}",
            '',
            '| variant | status | contracts | styles | sample contracts |',
            '|---|---|---:|---|---|',
        ])
        for row in family['variants']:
            styles = ', '.join(f"`{k}`×{v}" for k, v in row['style_counts'].items()) or '—'
            sample = ', '.join(f"`{item}`" for item in row['sample_contract_ids']) or '—'
            lines.append(f"| `{row['variant']}` | `{row['status']}` | {row['contract_count']} | {styles} | {sample} |")
    lines.extend([
        '',
        '## Practical interpretation for Rust-blocked sessions',
        '',
        '1. Treat `unseen` rows as the sharpest static test-gap candidates once `cargo test` returns.',
        '2. Treat `inline_only` rows carefully: they have some source-level coverage, but not a separate external-test anchor in the current corpus.',
        '3. Treat `sparse` rows as weakly-defended semantics; one regression could erase a whole scenario family from active protection.',
        '4. Keep this ledger generated and compact. Do not copy large Rust test bodies into the archive just to explain coverage gaps.',
    ])
    return '\n'.join(lines) + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    report = collect()
    js = json.dumps(report, indent=2, sort_keys=False) + '\n'
    md = render_markdown(report)
    if args.write:
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
        print(f'wrote {OUT_MD.relative_to(ROOT).as_posix()}')
        return 0
    ok = True
    if not OUT_JSON.exists() or OUT_JSON.read_text(encoding='utf-8') != js:
        print(f'rust-test-scenario-coverage: stale {OUT_JSON.relative_to(ROOT).as_posix()}', file=sys.stderr)
        ok = False
    if not OUT_MD.exists() or OUT_MD.read_text(encoding='utf-8') != md:
        print(f'rust-test-scenario-coverage: stale {OUT_MD.relative_to(ROOT).as_posix()}', file=sys.stderr)
        ok = False
    if ok:
        print('rust-test-scenario-coverage: ok')
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
