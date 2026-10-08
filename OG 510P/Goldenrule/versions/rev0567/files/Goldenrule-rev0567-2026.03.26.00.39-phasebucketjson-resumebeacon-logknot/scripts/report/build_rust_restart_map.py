#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_restart_map.json'
OUT_MD = ROOT / 'docs' / 'RUST_RESTART_MAP.md'
SRC_DIR = ROOT / 'crates' / 'gr_engine' / 'src'
TEST_DIR = ROOT / 'crates' / 'gr_engine' / 'tests'
BIN_DIR = SRC_DIR / 'bin'

PUBLIC_PATTERNS: list[tuple[str, str]] = [
    ('fn', r'^\s*pub(?:\([^)]*\))?\s+fn\s+([A-Za-z0-9_]+)'),
    ('struct', r'^\s*pub\s+struct\s+([A-Za-z0-9_]+)'),
    ('enum', r'^\s*pub\s+enum\s+([A-Za-z0-9_]+)'),
    ('trait', r'^\s*pub\s+trait\s+([A-Za-z0-9_]+)'),
    ('type', r'^\s*pub\s+type\s+([A-Za-z0-9_]+)'),
    ('const', r'^\s*pub\s+const\s+([A-Za-z0-9_]+)'),
]
USE_RE = re.compile(r'^\s*use\s+crate::([A-Za-z0-9_]+)', flags=re.MULTILINE)
TEST_RE = re.compile(r'#\[test\]')
PROPTEST_RE = re.compile(r'proptest!')
MODULE_PATH_RE_TEMPLATE = r'(?:gr_engine|crate)::%s(?:::\w+)?'

HAZARD_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ('unwrap', re.compile(r'\bunwrap\s*\(')),
    ('expect', re.compile(r'\bexpect\s*\(')),
    ('todo', re.compile(r'\btodo\s*!')),
    ('unimplemented', re.compile(r'\bunimplemented\s*!')),
    ('panic', re.compile(r'\bpanic\s*!')),
    ('unsafe', re.compile(r'\bunsafe\b')),
    ('dbg', re.compile(r'\bdbg\s*!')),
]


def line_number(text: str, offset: int) -> int:
    return text.count('\n', 0, offset) + 1


def find_inline_test_spans(text: str) -> list[tuple[int, int]]:
    lines = text.splitlines(keepends=True)
    offsets = []
    cursor = 0
    for line in lines:
        offsets.append(cursor)
        cursor += len(line)
    joined = ''.join(lines)
    spans: list[tuple[int, int]] = []
    cfg_positions = [m.start() for m in re.finditer(r'^\s*#\[cfg\(test\)\]\s*$', joined, flags=re.MULTILINE)]
    for pos in cfg_positions:
        mod_match = re.search(r'mod\s+tests\s*\{', joined[pos:])
        if not mod_match:
            continue
        open_index = pos + mod_match.end() - 1
        depth = 0
        end_index = len(joined)
        for idx in range(open_index, len(joined)):
            ch = joined[idx]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end_index = idx + 1
                    break
        spans.append((pos, end_index))
    return spans


def extract_public_items(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for kind, pattern in PUBLIC_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            items.append({'kind': kind, 'name': match.group(1)})
    items.sort(key=lambda row: (row['kind'], row['name']))
    return items


def classify_anchor(module: str, path: Path, text: str) -> bool:
    if path.stem == module or path.stem.startswith(f'{module}_'):
        return True
    pattern = re.compile(MODULE_PATH_RE_TEMPLATE % re.escape(module))
    return bool(pattern.search(text))


def collect() -> dict[str, object]:
    src_files = sorted(path for path in SRC_DIR.glob('*.rs') if path.name != 'mod.rs')
    test_files = sorted(TEST_DIR.glob('*.rs'))
    bin_files = sorted(BIN_DIR.glob('*.rs')) if BIN_DIR.exists() else []

    modules: dict[str, dict[str, object]] = {}
    inbound_refs = Counter()
    public_kind_counts = Counter()

    for path in src_files:
        text = path.read_text(encoding='utf-8')
        module = path.stem
        outbound_deps = sorted(dep for dep in USE_RE.findall(text) if dep != module)
        for dep in outbound_deps:
            inbound_refs[dep] += 1
        public_items = extract_public_items(text)
        for item in public_items:
            public_kind_counts[item['kind']] += 1

        test_spans = find_inline_test_spans(text)
        implementation_hazards: list[dict[str, object]] = []
        inline_test_hazards: list[dict[str, object]] = []
        for hazard_kind, pattern in HAZARD_PATTERNS:
            for match in pattern.finditer(text):
                row = {
                    'kind': hazard_kind,
                    'line': line_number(text, match.start()),
                    'snippet': text.splitlines()[line_number(text, match.start()) - 1].strip(),
                }
                if any(start <= match.start() < end for start, end in test_spans):
                    inline_test_hazards.append(row)
                else:
                    implementation_hazards.append(row)
        implementation_hazards.sort(key=lambda row: (row['line'], row['kind']))
        inline_test_hazards.sort(key=lambda row: (row['line'], row['kind']))
        implementation_hazard_kind_counts = Counter(row['kind'] for row in implementation_hazards)
        inline_test_hazard_kind_counts = Counter(row['kind'] for row in inline_test_hazards)

        modules[module] = {
            'module': module,
            'path': path.relative_to(ROOT).as_posix(),
            'lines': text.count('\n') + 1,
            'public_item_count': len(public_items),
            'public_items': public_items,
            'inline_test_count': len(TEST_RE.findall(text)),
            'inline_proptest_macro_count': len(PROPTEST_RE.findall(text)),
            'outbound_src_deps': outbound_deps,
            'outbound_src_dep_count': len(outbound_deps),
            'implementation_hazard_count': len(implementation_hazards),
            'implementation_hazard_kind_counts': dict(sorted(implementation_hazard_kind_counts.items())),
            'implementation_hazards': implementation_hazards,
            'inline_test_hazard_count': len(inline_test_hazards),
            'inline_test_hazard_kind_counts': dict(sorted(inline_test_hazard_kind_counts.items())),
            'inline_test_hazards': inline_test_hazards,
        }

    for module, row in modules.items():
        row['inbound_src_ref_count'] = inbound_refs[module]

    test_anchor_total = 0
    for module, row in modules.items():
        anchored_tests = []
        for path in test_files:
            text = path.read_text(encoding='utf-8')
            if classify_anchor(module, path, text):
                test_count = len(TEST_RE.findall(text))
                anchored_tests.append(
                    {
                        'path': path.relative_to(ROOT).as_posix(),
                        'test_count': test_count,
                        'proptest_macro_count': len(PROPTEST_RE.findall(text)),
                    }
                )
        anchored_tests.sort(key=lambda item: item['path'])
        row['test_anchors'] = anchored_tests
        row['test_anchor_count'] = len(anchored_tests)
        row['anchored_test_count'] = sum(item['test_count'] for item in anchored_tests)
        test_anchor_total += len(anchored_tests)

    bin_anchor_total = 0
    for module, row in modules.items():
        anchored_bins = []
        for path in bin_files:
            text = path.read_text(encoding='utf-8')
            if classify_anchor(module, path, text):
                anchored_bins.append({'path': path.relative_to(ROOT).as_posix()})
        anchored_bins.sort(key=lambda item: item['path'])
        row['bin_anchors'] = anchored_bins
        row['bin_anchor_count'] = len(anchored_bins)
        bin_anchor_total += len(anchored_bins)

    def restart_score(row: dict[str, object]) -> int:
        line_weight = min(int(row['lines']) // 50, 10)
        return (
            8 * int(row['implementation_hazard_count'])
            + 2 * int(row['inline_test_hazard_count'])
            + 4 * int(row['inbound_src_ref_count'])
            + 3 * int(row['public_item_count'])
            + 2 * int(row['test_anchor_count'])
            + 2 * int(row['bin_anchor_count'])
            + line_weight
        )

    for row in modules.values():
        row['restart_score'] = restart_score(row)

    restart_queue = []
    for row in sorted(
        modules.values(),
        key=lambda item: (
            -int(item['restart_score']),
            -int(item['implementation_hazard_count']),
            -int(item['inline_test_hazard_count']),
            -int(item['inbound_src_ref_count']),
            item['module'],
        ),
    ):
        why_bits = []
        if row['implementation_hazard_count']:
            why_bits.append(f"{row['implementation_hazard_count']} implementation hazards")
        if row['inline_test_hazard_count']:
            why_bits.append(f"{row['inline_test_hazard_count']} inline-test hazards")
        if row['inbound_src_ref_count']:
            why_bits.append(f"{row['inbound_src_ref_count']} inbound src refs")
        if row['test_anchor_count']:
            why_bits.append(f"{row['test_anchor_count']} test anchors")
        if row['bin_anchor_count']:
            why_bits.append(f"{row['bin_anchor_count']} bin anchors")
        if row['public_item_count']:
            why_bits.append(f"{row['public_item_count']} public items")
        restart_queue.append(
            {
                'module': row['module'],
                'path': row['path'],
                'restart_score': row['restart_score'],
                'why': why_bits or ['small isolated surface'],
            }
        )

    implementation_hazard_modules = [row['module'] for row in modules.values() if row['implementation_hazard_count']]
    hazard_rows = [
        {
            'module': row['module'],
            'path': row['path'],
            'implementation_hazard_count': row['implementation_hazard_count'],
            'implementation_hazard_kind_counts': row['implementation_hazard_kind_counts'],
            'implementation_hazards': row['implementation_hazards'],
            'inline_test_hazard_count': row['inline_test_hazard_count'],
            'inline_test_hazard_kind_counts': row['inline_test_hazard_kind_counts'],
            'inline_test_hazards': row['inline_test_hazards'],
            'test_anchor_count': row['test_anchor_count'],
            'bin_anchor_count': row['bin_anchor_count'],
        }
        for row in sorted(modules.values(), key=lambda item: (-int(item['implementation_hazard_count']), -int(item['inline_test_hazard_count']), item['module']))
        if row['implementation_hazard_count'] or row['inline_test_hazard_count']
    ]

    inventory = {
        'inventory_version': '2026-03-23.rust_restart_map.v1',
        'scope': {
            'crate': 'gr_engine',
            'src_glob': 'crates/gr_engine/src/*.rs',
            'test_glob': 'crates/gr_engine/tests/*.rs',
            'bin_glob': 'crates/gr_engine/src/bin/*.rs',
            'method': 'static_regex_scan',
            'limitations': [
                'This map is source-text based and does not invoke rustc, cargo, macro expansion, or type checking.',
                'Test/bin anchors are heuristic matches from file stems and module-path regexes.',
                'Hazard markers are restart heuristics, not correctness proofs or lints.',
            ],
        },
        'summary': {
            'src_module_count': len(src_files),
            'test_file_count': len(test_files),
            'bin_file_count': len(bin_files),
            'public_item_count': sum(int(row['public_item_count']) for row in modules.values()),
            'public_item_kind_counts': dict(sorted(public_kind_counts.items())),
            'implementation_hazard_count': sum(int(row['implementation_hazard_count']) for row in modules.values()),
            'implementation_hazard_module_count': len(implementation_hazard_modules),
            'inline_test_hazard_count': sum(int(row['inline_test_hazard_count']) for row in modules.values()),
            'hazard_anchor_link_count': sum(int(row['test_anchor_count']) for row in modules.values() if row['implementation_hazard_count'] or row['inline_test_hazard_count']),
            'test_anchor_link_count': test_anchor_total,
            'bin_anchor_link_count': bin_anchor_total,
            'top_restart_module': restart_queue[0]['module'] if restart_queue else None,
        },
        'restart_queue': restart_queue,
        'hazard_modules': hazard_rows,
        'modules': [modules[name] for name in sorted(modules)],
    }
    return inventory



def render_markdown(inventory: dict[str, object]) -> str:
    summary = inventory['summary']
    restart_queue = inventory['restart_queue']
    hazard_modules = inventory['hazard_modules']
    modules = inventory['modules']

    lines = [
        '# Rust Restart Map',
        '',
        'Generated by `scripts/report/build_rust_restart_map.py`. This is a static restart-oriented source map for Rust-blocked sessions; it does not replace `cargo`, `rustc`, or runtime tests.',
        '',
        '## Snapshot',
        '',
        '- crate: `gr_engine`',
        f"- src_modules: {summary['src_module_count']}",
        f"- test_files: {summary['test_file_count']}",
        f"- bin_files: {summary['bin_file_count']}",
        f"- public_items: {summary['public_item_count']}",
        f"- implementation_hazards_seen: {summary['implementation_hazard_count']} across {summary['implementation_hazard_module_count']} src module(s)",
        f"- inline_test_hazards_seen: {summary['inline_test_hazard_count']}",
        f"- test_anchor_links: {summary['test_anchor_link_count']}",
        f"- bin_anchor_links: {summary['bin_anchor_link_count']}",
        f"- top_restart_module: `{summary['top_restart_module']}`",
        '',
        'Public item kinds:',
        '',
    ]
    for kind, count in summary['public_item_kind_counts'].items():
        lines.append(f'- `{kind}`: {count}')

    lines.extend(
        [
            '',
            '## Priority restart queue',
            '',
            'Use this order when local Rust execution is blocked and the inheritor needs the shortest path back to high-leverage source review.',
            '',
            '| module | restart_score | why it matters first |',
            '|---|---:|---|',
        ]
    )
    for row in restart_queue[:8]:
        lines.append(f"| `{row['module']}` | {row['restart_score']} | {'; '.join(row['why'])} |")

    lines.extend(['', '## Source hazard seams', '', 'These are source-text markers only. They are restart hints, not proof of a bug.', '', '| module | implementation_hazard_counts | inline_test_hazard_counts | anchor surface |', '|---|---|---|---|'])
    if hazard_modules:
        for row in hazard_modules:
            implementation_counts = ', '.join(f"`{kind}`={count}" for kind, count in row['implementation_hazard_kind_counts'].items()) or 'none'
            inline_counts = ', '.join(f"`{kind}`={count}" for kind, count in row['inline_test_hazard_kind_counts'].items()) or 'none'
            lines.append(
                f"| `{row['module']}` | {implementation_counts} | {inline_counts} | tests={row['test_anchor_count']}, bins={row['bin_anchor_count']} |"
            )
        lines.extend(['', '### Hazard details', ''])
        for row in hazard_modules:
            lines.append(f"#### `{row['module']}`")
            lines.append('')
            lines.append(f"- path: `{row['path']}`")
            lines.append(f"- tests anchored: {row['test_anchor_count']}")
            lines.append(f"- bins anchored: {row['bin_anchor_count']}")
            if row['implementation_hazards']:
                lines.append('- implementation occurrences:')
                for hit in row['implementation_hazards'][:12]:
                    safe_snippet = hit['snippet'].replace('|', '\\|')
                    lines.append(f"  - line {hit['line']}: `{hit['kind']}` → `{safe_snippet}`")
                if len(row['implementation_hazards']) > 12:
                    lines.append(f"  - … {len(row['implementation_hazards']) - 12} more implementation occurrence(s)")
            if row['inline_test_hazards']:
                lines.append('- inline-test occurrences:')
                for hit in row['inline_test_hazards'][:12]:
                    safe_snippet = hit['snippet'].replace('|', '\\|')
                    lines.append(f"  - line {hit['line']}: `{hit['kind']}` → `{safe_snippet}`")
                if len(row['inline_test_hazards']) > 12:
                    lines.append(f"  - … {len(row['inline_test_hazards']) - 12} more inline-test occurrence(s)")
            lines.append('')
    else:
        lines.append('| — | none | none | — |')

    lines.extend(
        [
            '## Module anchor map',
            '',
            '| module | lines | public_items | inbound_src_refs | test_anchors | bin_anchors | source_hazards |',
            '|---|---:|---:|---:|---:|---:|---:|',
        ]
    )
    for row in sorted(modules, key=lambda item: (-int(item['restart_score']), item['module'])):
        lines.append(
            f"| `{row['module']}` | {row['lines']} | {row['public_item_count']} | {row['inbound_src_ref_count']} | {row['test_anchor_count']} | {row['bin_anchor_count']} | {row['implementation_hazard_count'] + row['inline_test_hazard_count']} |"
        )

    lines.extend(
        [
            '',
            '## Practical interpretation for Rust-blocked sessions',
            '',
            '1. Start with the top row in the priority restart queue when you need the fastest route back to meaningful Rust review.',
            '2. Treat hazard markers as places to scrutinize once `cargo test` returns, especially where they coincide with many anchors.',
            '3. Prefer modules with both many inbound refs and many test anchors when deciding what deserves the first compiled rerun.',
            '4. Keep this map small and generated; do not preserve large copied code slices in the archive just to explain restart order.',
        ]
    )

    return '\n'.join(lines) + '\n'



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)

    inventory = collect()
    md = render_markdown(inventory)
    js = json.dumps(inventory, indent=2, sort_keys=False) + '\n'

    if args.write:
        OUT_JSON.write_text(js, encoding='utf-8')
        OUT_MD.write_text(md, encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT).as_posix()}')
        print(f'wrote {OUT_MD.relative_to(ROOT).as_posix()}')
        return 0

    ok = True
    if not OUT_JSON.exists() or OUT_JSON.read_text(encoding='utf-8') != js:
        print(f'rust-restart-map: stale {OUT_JSON.relative_to(ROOT).as_posix()}', file=sys.stderr)
        ok = False
    if not OUT_MD.exists() or OUT_MD.read_text(encoding='utf-8') != md:
        print(f'rust-restart-map: stale {OUT_MD.relative_to(ROOT).as_posix()}', file=sys.stderr)
        ok = False
    if ok:
        print('rust-restart-map: ok')
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
