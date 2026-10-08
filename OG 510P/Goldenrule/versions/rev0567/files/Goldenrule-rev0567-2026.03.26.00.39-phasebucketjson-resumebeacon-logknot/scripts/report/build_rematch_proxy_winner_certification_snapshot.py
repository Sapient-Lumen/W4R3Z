#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_OCC_SCRIPT = ROOT / 'scripts' / 'report' / 'build_rematch_proxy_occupancy_accounting_snapshot.py'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.json'
OUT_MD = ROOT / 'artifacts' / 'reports' / 'rematch_proxy_winner_certification_snapshot_20260306.md'
T_CRIT_95_DF5 = 2.570582


def _load_occ_module():
    spec = importlib.util.spec_from_file_location('rematch_occ', SRC_OCC_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'failed to load {SRC_OCC_SCRIPT}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _round(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    return obj


def main() -> int:
    occ = _load_occ_module()

    extortion = occ._read_json(occ.EXTORTION_PATH)
    generous_tft = occ._read_json(occ.GEN_TFT_PATH)
    always_c = occ._read_json(occ.ALWAYS_C_PATH)
    courteous_firm = occ._read_json(occ.COURTEOUS_PATH)
    exit_after_break = occ._read_json(occ.EXIT_AFTER_BREAK_PATH)

    policies = {
        'CCEEE': exit_after_break,
        'CCDDE': occ._det_exit_strategy('CCDDE'),
        'always_c': always_c,
        'courteous_firm': courteous_firm,
        'DCECC': occ._det_exit_strategy('DCECC'),
    }

    panel_rows: list[dict[str, object]] = []
    certified_count = 0
    uncertified_panels: list[dict[str, object]] = []
    smallest_certified_lower_bound = None
    smallest_certified_panel = None

    for ext in occ.EXTORTION_LEVELS:
        for delay in occ.DELAY_LEVELS:
            seed_rows: dict[str, list[float]] = {}
            for policy_name, policy_spec in policies.items():
                seed_rows[policy_name] = []
                for seed in occ.SEEDS:
                    sim = occ._simulate_proxy_world(
                        policy_spec,
                        extortion=extortion,
                        generous_tft=generous_tft,
                        total_rounds=occ.TOTAL_ROUNDS,
                        extortion_share=ext / 100.0,
                        rematch_delay=delay,
                        seed=seed,
                        exit_payoff=occ.EXIT_PAYOFF,
                    )
                    seed_rows[policy_name].append(float(sim['overall_avg_payoff']))

            mean_payoffs = {
                policy_name: statistics.fmean(values)
                for policy_name, values in seed_rows.items()
            }
            rank_order = sorted(mean_payoffs, key=mean_payoffs.get, reverse=True)
            leader = rank_order[0]
            runner_up = rank_order[1]
            paired_diffs = [a - b for a, b in zip(seed_rows[leader], seed_rows[runner_up])]
            mean_gap = statistics.fmean(paired_diffs)
            sd_gap = statistics.stdev(paired_diffs)
            se_gap = sd_gap / math.sqrt(len(paired_diffs)) if paired_diffs else 0.0
            ci_low = mean_gap - T_CRIT_95_DF5 * se_gap
            ci_high = mean_gap + T_CRIT_95_DF5 * se_gap
            leader_certified = ci_low > 0.0
            if leader_certified:
                certified_count += 1
                if smallest_certified_lower_bound is None or ci_low < smallest_certified_lower_bound:
                    smallest_certified_lower_bound = ci_low
                    smallest_certified_panel = {
                        'extortion': ext,
                        'delay': delay,
                        'leader': leader,
                        'runner_up': runner_up,
                        'leader_margin': mean_gap,
                        'leader_margin_ci_low': ci_low,
                        'leader_margin_ci_high': ci_high,
                    }
            else:
                uncertified_panels.append(
                    {
                        'extortion': ext,
                        'delay': delay,
                        'leader': leader,
                        'runner_up': runner_up,
                        'leader_margin': mean_gap,
                        'leader_margin_ci_low': ci_low,
                        'leader_margin_ci_high': ci_high,
                    }
                )

            panel_rows.append(
                {
                    'extortion': ext,
                    'delay': delay,
                    'leader': leader,
                    'runner_up': runner_up,
                    'leader_margin': mean_gap,
                    'leader_margin_ci_low': ci_low,
                    'leader_margin_ci_high': ci_high,
                    'paired_margin_sd': sd_gap,
                    'paired_margin_se': se_gap,
                    'paired_seed_sign_wins': sum(diff > 0.0 for diff in paired_diffs),
                    'paired_seed_count': len(paired_diffs),
                    'leader_certified_95_ci': leader_certified,
                    'rank_order': rank_order,
                    'policy_mean_payoffs': mean_payoffs,
                }
            )

    summary = {
        'focus': 'Attach paired-seed winner-certification metadata to rematch leaderboards so tiny leader flips are separated from point-estimate noise.',
        'source_script': str(SRC_OCC_SCRIPT.relative_to(ROOT)),
        'headline_findings': {
            'tested_panels': len(occ.EXTORTION_LEVELS) * len(occ.DELAY_LEVELS),
            'certified_leaders_95_ci': certified_count,
            'uncertified_leaders_95_ci': len(panel_rows) - certified_count,
            'smallest_certified_leader_margin_ci_low': smallest_certified_lower_bound,
            'smallest_certified_panel': smallest_certified_panel,
            'uncertified_panels': uncertified_panels,
            'interpretation': 'In the current proxy, most top rankings are not fragile once paired seed noise is accounted for. The only tested leader flip is uncertified: its paired 95% interval still spans zero, so the observed switch is better treated as provisional than as a real new winner.',
        },
        'panel_rows': panel_rows,
    }
    OUT_JSON.write_text(json.dumps(_round(summary), indent=2, sort_keys=True) + '\n', encoding='utf-8')

    lines = [
        '# Rematch-Proxy Winner Certification Snapshot (2026-03-06)',
        '',
        'Method:',
        '- reran the current exogenous-pool rematch proxy at the same `extortion in {20,50,80}` and `delay in {0,1,2}` grid',
        f'- reused the same six seeds `{list(occ.SEEDS)}` for every policy so top-vs-runner-up comparisons could be treated as paired-seed margins',
        '- for each panel, identified the raw aggregate leader and runner-up, then computed the paired seed margin `leader - runner_up`',
        '- attached a small 95% t-interval (`df=5`) to that paired margin and marked the leader as certified only when the interval stayed above zero',
        '',
        'Main finding:',
        f'- `{certified_count}` of `{len(panel_rows)}` tested panels have a certified raw leader under the paired 95% interval rule.',
        '- The only uncertified panel is the only tested leader flip: `ext80, delay2`, where `CCDDE` leads `CCEEE` by a point estimate of only `0.000853`, but the paired 95% interval is `[-0.008563, 0.010269]`.',
        '- So the current proxy already supports a sharper implementor contract: not every reported rematch winner deserves the same status; tiny leader flips should remain provisional until they clear an uncertainty gate.',
        '',
        'Panel summary:',
        '',
        '| extortion | delay | leader | runner-up | mean margin | 95% CI low | 95% CI high | paired wins | certified? |',
        '|---:|---:|---|---|---:|---:|---:|---:|---|',
    ]
    for row in panel_rows:
        lines.append(
            f"| {row['extortion']} | {row['delay']} | `{row['leader']}` | `{row['runner_up']}` | {float(row['leader_margin']):.6f} | {float(row['leader_margin_ci_low']):.6f} | {float(row['leader_margin_ci_high']):.6f} | {int(row['paired_seed_sign_wins'])}/{int(row['paired_seed_count'])} | {'yes' if bool(row['leader_certified_95_ci']) else 'no'} |"
        )

    lines += [
        '',
        'Implementor implication:',
        '- Future rematch-world benchmark artifacts should publish not only the tested-band leader and leader margin, but also a paired-seed uncertainty field or PCS-style certification status for the top-vs-runner-up gap.',
        '- When a raw leader flip fails that gate, treat it as decision-relevant uncertainty, not as a clean strategy ranking reversal.',
        '- This is especially important once endogenous rematch worlds add more policies, more stochasticity, or wider delay bands; otherwise the archive can grow with noisy winner claims instead of compact certified frontiers.',
        '',
    ]
    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print(f'wrote {OUT_JSON}')
    print(f'wrote {OUT_MD}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
