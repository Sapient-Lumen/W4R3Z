#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_PLAN_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_cache_plan_snapshot_20260306.json'
REPORT_STEM = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_zero_noise_rule_classifier_snapshot_20260306'

ORDERED_RULES = [
    {
        'rule_id': 'zr00',
        'pattern': 'C****',
        'regime_id': 'none_r00',
        'note': 'Any C-only opener stays in the cooperative-start regime regardless of later support.',
    },
    {
        'rule_id': 'zr01',
        'pattern': '[DB]**BB',
        'regime_id': 'none_r01',
        'note': 'If the opener can defect and both retaliation states are bilateral, the quotient expands to the largest hostile branch.',
    },
    {
        'rule_id': 'zr02',
        'pattern': '[DB]**BD',
        'regime_id': 'none_r02',
        'note': 'Defect-capable opener plus bilateral DC support and D-only DD support.',
    },
    {
        'rule_id': 'zr03',
        'pattern': '[DB]**DB',
        'regime_id': 'none_r03',
        'note': 'Defect-capable opener plus D-only DC support and bilateral DD support.',
    },
    {
        'rule_id': 'zr04',
        'pattern': '[DB]**DD',
        'regime_id': 'none_r04',
        'note': 'Defect-capable opener plus D-only support in both retaliation states.',
    },
    {
        'rule_id': 'zr05',
        'pattern': '[DB]*[DB]CB',
        'regime_id': 'none_r05',
        'note': 'CC support remains mixed, CD excludes C, DC is C-only, DD is bilateral.',
    },
    {
        'rule_id': 'zr06',
        'pattern': '[DB]*[DB]CD',
        'regime_id': 'none_r06',
        'note': 'CC support remains mixed, CD excludes C, DC is C-only, DD is D-only.',
    },
    {
        'rule_id': 'zr07',
        'pattern': '[DB][DB]*BC',
        'regime_id': 'none_r07',
        'note': 'CC excludes C, CD remains mixed, DC is bilateral, DD is C-only.',
    },
    {
        'rule_id': 'zr08',
        'pattern': '[DB][DB]*DC',
        'regime_id': 'none_r08',
        'note': 'CC excludes C, CD remains mixed, DC is D-only, DD is C-only.',
    },
    {
        'rule_id': 'zr09',
        'pattern': '[DB][DB][DB]CC',
        'regime_id': 'none_r09',
        'note': 'All three non-start memory states exclude C, then both retaliation states are C-only.',
    },
    {
        'rule_id': 'zr10',
        'pattern': '[DB]C*BC',
        'regime_id': 'none_r10',
        'note': 'CC is C-only, DC is bilateral, DD is C-only.',
    },
    {
        'rule_id': 'zr11',
        'pattern': '[DB]*CCB',
        'regime_id': 'none_r11',
        'note': 'CD and DC are both C-only while DD is bilateral.',
    },
    {
        'rule_id': 'zr12',
        'pattern': '[DB]*CCD',
        'regime_id': 'none_r12',
        'note': 'CD and DC are both C-only while DD is D-only.',
    },
    {
        'rule_id': 'zr13',
        'pattern': '[DB]C*DC',
        'regime_id': 'none_r13',
        'note': 'CC is C-only, DC is D-only, DD is C-only.',
    },
    {
        'rule_id': 'zr14',
        'pattern': '[DB]C[DB]CC',
        'regime_id': 'none_r14',
        'note': 'CC is C-only, CD excludes C, and both retaliation states are C-only.',
    },
    {
        'rule_id': 'zr15',
        'pattern': '[DB][DB]CCC',
        'regime_id': 'none_r15',
        'note': 'CC excludes C while the remaining memory states are C-only.',
    },
    {
        'rule_id': 'zr16',
        'pattern': '[DB]CCCC',
        'regime_id': 'none_r16',
        'note': 'Only the initial support can defect; every remembered state is C-only.',
    },
]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def _regex(pattern: str) -> re.Pattern[str]:
    body = ''.join('.' if ch == '*' else ch for ch in pattern)
    return re.compile(f'^{body}$')


def _render_markdown(report: dict) -> str:
    lines = [
        '# Rematch-Proxy Zero-Noise Rule Classifier Snapshot (2026-03-06)',
        '',
        'Method:',
        '- loaded the current `deterministic no-noise` support-regime lookup from `artifacts/reports/rematch_proxy_cache_plan_snapshot_20260306.json`',
        '- replaced the 243-entry `signature -> regime` map with an ordered wildcard rule list over the five support positions `{start, CC, CD, DC, DD}`',
        '- validated that the ordered rule list reproduces the exact regime assignment for all 243 support signatures',
        '',
        'Main findings:',
        f"- the current zero-noise regime dispatch compresses from `{report['summary']['lookup_signature_count']}` explicit lookup entries to `{report['summary']['ordered_rule_count']}` exact ordered wildcard rules (`{report['summary']['lookup_to_rule_reduction_factor']}x` smaller).",
        f"- the largest rule bucket is `{report['summary']['largest_rule_id']}` / `{report['summary']['largest_pattern']}` with `{report['summary']['largest_rule_signature_count']}` signatures.",
        f"- the smallest rule bucket is `{report['summary']['smallest_rule_id']}` / `{report['summary']['smallest_pattern']}` with `{report['summary']['smallest_rule_signature_count']}` signatures.",
        '',
        'Exact ordered rules:',
    ]
    for row in report['rule_rows']:
        lines.append(
            f"- `{row['rule_id']}` — `{row['pattern']}` -> `{row['regime_id']}` (`{row['signature_count']}` signatures, family count `{row['quotient_family_count']}`)"
        )
    lines.extend([
        '',
        'Interpretation:',
        '- The current zero-noise planner no longer needs a bulky opaque `signature -> regime` table to be exact. A small ordered wildcard classifier is enough, which makes the planner easier to embed, diff, and audit.',
        '- Order matters: these rules are an exact decision list for the current proxy, not a claim about future rematch worlds.',
        '',
        'Implementor implication:',
        '- If the engine needs a zero-noise scratch classifier before rematch worlds expose planner metadata natively, prefer this ordered rule list over vendoring a 243-entry dispatch table. Regenerate it whenever entrant support, outside-option timing, memory depth, or noise semantics change.',
    ])
    return '\n'.join(lines)


def main() -> int:
    cache_plan = _read_json(CACHE_PLAN_PATH)
    none_row = next(row for row in cache_plan['mode_rows'] if row['id'] == 'none')
    regime_rows = {row['regime_id']: row for row in none_row['regime_rows']}
    signature_to_regime = none_row['signature_to_regime']

    claimed = set()
    rule_rows = []
    for rule in ORDERED_RULES:
        regex = _regex(rule['pattern'])
        matches = sorted(
            sig for sig in signature_to_regime
            if sig not in claimed and regex.fullmatch(sig)
        )
        if not matches:
            raise SystemExit(f"rule {rule['rule_id']} matched no new signatures")
        target_regimes = {signature_to_regime[sig] for sig in matches}
        if target_regimes != {rule['regime_id']}:
            raise SystemExit(
                f"rule {rule['rule_id']} pattern {rule['pattern']} crossed regimes: {sorted(target_regimes)}"
            )
        claimed.update(matches)
        regime = regime_rows[rule['regime_id']]
        rule_rows.append(
            {
                'rule_id': rule['rule_id'],
                'pattern': rule['pattern'],
                'regex': regex.pattern,
                'regime_id': rule['regime_id'],
                'signature_count': len(matches),
                'representative_signatures': matches[:5],
                'quotient_family_count': regime['quotient_family_count'],
                'quotient_family_examples': regime['quotient_family_examples'],
                'note': rule['note'],
            }
        )

    if claimed != set(signature_to_regime):
        missing = sorted(set(signature_to_regime) - claimed)
        raise SystemExit(f'unclaimed signatures remain: {missing[:5]}')

    largest = max(rule_rows, key=lambda row: row['signature_count'])
    smallest = min(rule_rows, key=lambda row: row['signature_count'])
    report = {
        'world': {
            'kind': 'rematch_proxy_zero_noise_rule_classifier',
            'description': 'Exact ordered wildcard classifier for the deterministic no-noise support-regime map in the current leave/rematch proxy.',
            'source_artifact': str(CACHE_PLAN_PATH.relative_to(ROOT)),
            'mode_id': 'none',
            'state_positions': ['start', 'CC', 'CD', 'DC', 'DD'],
            'alphabet': ['C', 'D', 'B'],
            'wildcard_symbol': '*',
            'support_signature_count': len(signature_to_regime),
            'regime_count': none_row['regime_count'],
        },
        'rule_rows': rule_rows,
        'summary': {
            'lookup_signature_count': len(signature_to_regime),
            'ordered_rule_count': len(rule_rows),
            'lookup_to_rule_reduction_factor': round(len(signature_to_regime) / len(rule_rows), 6),
            'largest_rule_id': largest['rule_id'],
            'largest_pattern': largest['pattern'],
            'largest_rule_signature_count': largest['signature_count'],
            'smallest_rule_id': smallest['rule_id'],
            'smallest_pattern': smallest['pattern'],
            'smallest_rule_signature_count': smallest['signature_count'],
            'exact_match': True,
        },
    }

    REPORT_STEM.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    REPORT_STEM.with_suffix('.md').write_text(_render_markdown(report) + '\n', encoding='utf-8')
    print(f"wrote {REPORT_STEM.with_suffix('.json')} and {REPORT_STEM.with_suffix('.md')}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
