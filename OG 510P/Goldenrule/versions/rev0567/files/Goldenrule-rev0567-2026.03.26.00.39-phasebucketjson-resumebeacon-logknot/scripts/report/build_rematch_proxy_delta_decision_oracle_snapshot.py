#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECTIVE_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_projective_decision_cone_snapshot_20260306.json'
NORMAL_FORM_PATH = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_normal_form_snapshot_20260306.json'
ORACLE_PATH = ROOT / 'scripts' / 'analysis' / 'rematch_proxy_delta_decision_oracle.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_oracle_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_delta_decision_oracle_snapshot_20260306.md'


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_oracle_module():
    spec = importlib.util.spec_from_file_location('rematch_proxy_delta_decision_oracle', ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _build_summary() -> dict[str, object]:
    projective = _load_json(PROJECTIVE_PATH)
    normal_form = _load_json(NORMAL_FORM_PATH)
    oracle = _load_oracle_module()

    projective_findings = projective['headline_findings']
    normal_findings = normal_form['headline_findings']
    if projective_findings['canonical_policy_box'] != normal_findings['canonical_policy_box']:
        raise SystemExit('canonical policy-box mismatch between source reports')

    sample_direct = [
        {
            'example_label': 'robust_material_from_zero_hazard_axis',
            'mode': 'projective_coordinates',
            'input': {'B': '-1', 'H': '0'},
            'expected_closure_label': 'MMM',
        },
        {
            'example_label': 'single_reversal_from_positive_hazard_cone',
            'mode': 'projective_coordinates',
            'input': {'B': '-0.0002', 'H': '1'},
            'expected_closure_label': 'SMM',
        },
        {
            'example_label': 'double_reversal_from_positive_hazard_cone',
            'mode': 'projective_coordinates',
            'input': {'B': '0.0001', 'H': '1'},
            'expected_closure_label': 'SMS',
        },
        {
            'example_label': 'tie_at_cap_20_boundary_ray',
            'mode': 'projective_coordinates',
            'input': {'B': '0.000313597', 'H': '1'},
            'expected_closure_label': 'TIE_tau20',
        },
    ]
    sample_weight = {
        'example_label': 'weight_mode_low_cap_stability_then_material',
        'mode': 'weights',
        'input': {
            'w_width': '0',
            'w_buffer': '0',
            'w_knife': '0',
            'w_delta': '0',
            'w_material': '0',
            'w_undecided': '0',
            'w_ties': '0',
            'w_hazard': '1',
        },
        'expected_baseline_nonhazard_surplus': '0.000000',
        'expected_closure_label': 'SMM',
        'why': 'with all non-hazard weights zero and positive hazard weight, B = 0 lands between tau(10) and tau(10000), so the direct class is the single-reversal sector SMM',
    }

    direct_results = []
    for row in sample_direct:
        result = oracle.classify_from_direct_coordinates(row['input']['B'], row['input']['H'])
        if result['closure_label'] != row['expected_closure_label']:
            raise SystemExit(f"unexpected closure for {row['example_label']}: {result['closure_label']}")
        direct_results.append({**row, 'oracle_result': result})

    weight_result = oracle.classify_from_weights(sample_weight['input'])
    if weight_result['baseline_nonhazard_surplus'] != sample_weight['expected_baseline_nonhazard_surplus']:
        raise SystemExit('unexpected baseline_nonhazard_surplus for weight-mode example')
    if weight_result['closure_label'] != sample_weight['expected_closure_label']:
        raise SystemExit('unexpected closure for weight-mode example')

    return {
        'focus': 'Turn the family10 projective decision cone into a small executable oracle so inheritors can classify directly from declared weights or direct (B,H) coordinates instead of re-deriving the handoff rules from multiple reports.',
        'method_note': 'Loaded the projective decision-cone and decision-normal-form reports, packaged their exact thresholds and anchor names into an executable script, and checked that sample direct-coordinate and weight-mode invocations reproduce the expected strict sectors and boundary strata.',
        'headline_findings': {
            'material_anchor': projective_findings['material_anchor'],
            'stability_anchor': projective_findings['stability_anchor'],
            'canonical_policy_box': projective_findings['canonical_policy_box'],
            'oracle_script': str(ORACLE_PATH.relative_to(ROOT)),
            'accepted_input_modes': ['projective_coordinates', 'weights'],
            'projective_coordinate_mode_requires': ['B', 'H'],
            'weight_mode_requires': ['w_width', 'w_buffer', 'w_knife', 'w_delta', 'w_material', 'w_undecided', 'w_ties', 'w_hazard'],
            'zero_probe_when_weights_declared': True,
            'black_box_probes_are_fallback_only': True,
            'checked_caps': [10, 20, 10000],
            'exact_thresholds': projective_findings['strict_threshold_rays_in_increasing_slope_order'],
            'baseline_nonhazard_surplus_expression': projective_findings['baseline_nonhazard_surplus_expression'],
            'closure_labels_supported': ['MMM', 'SMM', 'SMS', 'SSS', 'TIE_tau10', 'TIE_tau10000', 'TIE_tau20', 'TIE_origin'],
            'most_compact_handoff_rule': 'run the oracle directly when declared weights or direct (B,H) coordinates are available; only route to probe contracts when the final choice must be diagnosed from winner symbols alone',
        },
        'sample_projective_coordinate_invocations': direct_results,
        'sample_weight_invocation': {**sample_weight, 'oracle_result': weight_result},
        'sources': [
            str(PROJECTIVE_PATH.relative_to(ROOT)),
            str(NORMAL_FORM_PATH.relative_to(ROOT)),
            str(ORACLE_PATH.relative_to(ROOT)),
        ],
        'source_script': str(Path(__file__).relative_to(ROOT)),
    }


def _render_md(summary: dict[str, object]) -> str:
    findings = summary['headline_findings']
    lines = [
        '# Rematch-Proxy Delta Decision Oracle Snapshot (2026-03-06)',
        '',
        '## Focus',
        f"- {summary['focus']}",
        '',
        '## Headline findings',
        f"- oracle script: `{findings['oracle_script']}`.",
        f"- accepted input modes: `{findings['accepted_input_modes']}`.",
        f"- checked caps: `{findings['checked_caps']}`.",
        f"- exact thresholds: `{findings['exact_thresholds']}`.",
        f"- baseline surplus expression: `{findings['baseline_nonhazard_surplus_expression']}`.",
        '- zero-probe direct classification is now executable when declared weights are available; black-box probes remain fallback only.',
        '',
        '## Sample direct coordinate invocations',
    ]
    for row in summary['sample_projective_coordinate_invocations']:
        result = row['oracle_result']
        lines.append(
            f"- `{row['input']}` -> closure `{result['closure_label']}`, robustness `{result['robustness_class']}`, checked-cap outcomes `{result['checked_cap_outcomes']}`."
        )
    lines.extend([
        '',
        '## Sample weight-mode invocation',
        f"- input weights `{summary['sample_weight_invocation']['input']}` -> baseline `{summary['sample_weight_invocation']['oracle_result']['baseline_nonhazard_surplus']}`, closure `{summary['sample_weight_invocation']['oracle_result']['closure_label']}`, checked-cap outcomes `{summary['sample_weight_invocation']['oracle_result']['checked_cap_outcomes']}`.",
        '',
        '## Why this matters',
        '- future inheritors no longer need to mentally translate the cone inequalities into one-off calculations; the direct classifier is now executable.',
        '- the executable oracle also preserves the archive\'s declaration-first routing rule: use weights or direct coordinates when available, and only fall back to cap probes for black-box diagnosis.',
        '',
        '## Sources',
    ])
    for src in summary['sources']:
        lines.append(f'- `{src}`')
    return '\n'.join(lines) + '\n'


def main() -> None:
    summary = _build_summary()
    OUT_JSON.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(_render_md(summary), encoding='utf-8')
    print(str(OUT_JSON.relative_to(ROOT)))
    print(str(OUT_MD.relative_to(ROOT)))


if __name__ == '__main__':
    main()
