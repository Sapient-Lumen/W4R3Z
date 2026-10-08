#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.report import build_cloudtainer_rust_probe_oracles as oracle_mod
ORACLE_REPORT = ROOT / 'artifacts' / 'reports' / 'cloudtainer_rust_probe_oracles.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'cloudtainer_standing_bootstrap_delta.json'
OUT_MD = ROOT / 'docs' / 'CLOUDTAINER_STANDING_BOOTSTRAP_DELTA.md'

CODE_ANCHORS = {
    'simple_standing_declared': oracle_mod.CODE_ANCHORS['simple_standing_declared'],
    'task_default_standing': oracle_mod.CODE_ANCHORS['task_default_standing'],
    'probe_expansion_task_new': oracle_mod.CODE_ANCHORS['probe_expansion_task_new'],
    'sim_standing_bootstrap': oracle_mod.CODE_ANCHORS['sim_standing_bootstrap'],
    'sim_standing_update': oracle_mod.CODE_ANCHORS['sim_standing_update'],
    'strategy_selectors_ignore_opponent_standing': 'crates/gr_engine/src/sim.rs:55-290',
}


def _load_oracle_report() -> dict[str, Any]:
    if ORACLE_REPORT.exists():
        return json.loads(ORACLE_REPORT.read_text(encoding='utf-8'))
    return oracle_mod.collect()


def _simulate_exact_path_with_start(probe: dict[str, Any], *, declared_initial: bool) -> dict[str, Any]:
    matchup = probe['matchups'][0]
    world = probe['world']
    rounds = int(world['termination']['rounds'])
    payoffs = world['game']['payoffs']
    noise = world.get('noise') or {'kind': 'none'}
    if noise.get('kind') != 'none':
        raise ValueError('standing bootstrap delta only supports deterministic noise=none probes')

    reputation = world.get('reputation') or {'kind': 'none'}
    if declared_initial and reputation.get('kind') == 'simple_standing':
        current_standing_a = float(reputation['initial_standing'])
        current_standing_b = float(reputation['initial_standing'])
    else:
        current_standing_a = 1.0
        current_standing_b = 1.0

    state = oracle_mod.JointState(
        a=oracle_mod.PlayerState(
            last_self_intended=None,
            last_opp_observed=None,
            fsm_state=matchup['strategy_a'].get('initial_state'),
        ),
        b=oracle_mod.PlayerState(
            last_self_intended=None,
            last_opp_observed=None,
            fsm_state=matchup['strategy_b'].get('initial_state'),
        ),
    )

    trace: list[dict[str, Any]] = []
    totals = {
        'avg_payoff_a': 0.0,
        'avg_payoff_b': 0.0,
        'coop_rate_a': 0.0,
        'coop_rate_b': 0.0,
        'mutual_coop_rate': 0.0,
        'mutual_defect_rate': 0.0,
    }

    for round_index in range(rounds):
        dist_a = oracle_mod._decision_distribution(matchup['strategy_a'], state.a)
        dist_b = oracle_mod._decision_distribution(matchup['strategy_b'], state.b)
        if len(dist_a) != 1 or len(dist_b) != 1:
            raise ValueError('standing bootstrap delta expects deterministic seeds only')
        a_intended, _, next_state_a = dist_a[0]
        b_intended, _, next_state_b = dist_b[0]

        a_executed = a_intended
        b_executed = b_intended
        a_observed_opp = b_executed
        b_observed_opp = a_executed
        payoff_a, payoff_b = oracle_mod._payoff(payoffs, a_executed, b_executed)

        totals['avg_payoff_a'] += payoff_a
        totals['avg_payoff_b'] += payoff_b
        totals['coop_rate_a'] += 1.0 if a_executed == oracle_mod.ACTION_C else 0.0
        totals['coop_rate_b'] += 1.0 if b_executed == oracle_mod.ACTION_C else 0.0
        totals['mutual_coop_rate'] += 1.0 if (a_executed, b_executed) == (oracle_mod.ACTION_C, oracle_mod.ACTION_C) else 0.0
        totals['mutual_defect_rate'] += 1.0 if (a_executed, b_executed) == (oracle_mod.ACTION_D, oracle_mod.ACTION_D) else 0.0

        step = {
            'round': round_index,
            'standing_a_pre_update': oracle_mod._round6(current_standing_a),
            'standing_b_pre_update': oracle_mod._round6(current_standing_b),
            'a_intended': a_intended,
            'b_intended': b_intended,
            'a_executed': a_executed,
            'b_executed': b_executed,
            'a_observed_opp': a_observed_opp,
            'b_observed_opp': b_observed_opp,
            'payoff_a': oracle_mod._round6(payoff_a),
            'payoff_b': oracle_mod._round6(payoff_b),
        }

        if reputation.get('kind') == 'simple_standing':
            next_a = oracle_mod._update_standing(current_standing_a, a_executed, current_standing_b, reputation['update_rule'])
            next_b = oracle_mod._update_standing(current_standing_b, b_executed, current_standing_a, reputation['update_rule'])
            step['standing_a_post_update'] = oracle_mod._round6(next_a)
            step['standing_b_post_update'] = oracle_mod._round6(next_b)
            current_standing_a = next_a
            current_standing_b = next_b

        trace.append(step)
        state = oracle_mod.JointState(
            a=oracle_mod.PlayerState(
                last_self_intended=a_intended,
                last_opp_observed=a_observed_opp,
                fsm_state=next_state_a if next_state_a is not None else state.a.fsm_state,
            ),
            b=oracle_mod.PlayerState(
                last_self_intended=b_intended,
                last_opp_observed=b_observed_opp,
                fsm_state=next_state_b if next_state_b is not None else state.b.fsm_state,
            ),
        )
        if a_executed == oracle_mod.ACTION_EXIT or b_executed == oracle_mod.ACTION_EXIT:
            break

    rounds_executed = max(1, len(trace))
    mean_stats = {key: oracle_mod._round6(value / rounds_executed) for key, value in totals.items()}
    mean_stats['rounds'] = len(trace)
    return {
        'mode': 'declared_initial' if declared_initial else 'task_default',
        'probe_id': probe['id'],
        'matchup_id': matchup['id'],
        'replications': int(matchup.get('replications', 1)),
        'rounds_per_replication': len(trace),
        'mean_stats': mean_stats,
        'trace': trace,
    }


def _summarize_trace_delta(current: list[dict[str, Any]], declared: list[dict[str, Any]]) -> dict[str, Any]:
    first_any_diff_round: int | None = None
    first_standing_diff_round: int | None = None
    action_stream_changed = False
    payoff_stream_changed = False
    standing_stream_changed = False
    diff_fields: set[str] = set()

    for cur_step, dec_step in zip(current, declared):
        round_index = int(cur_step['round'])
        keys = sorted(set(cur_step) | set(dec_step))
        changed_fields = [key for key in keys if cur_step.get(key) != dec_step.get(key)]
        if changed_fields:
            if first_any_diff_round is None:
                first_any_diff_round = round_index
            diff_fields.update(changed_fields)
        if any(field.startswith('standing_') for field in changed_fields):
            standing_stream_changed = True
            if first_standing_diff_round is None:
                first_standing_diff_round = round_index
        if any(field in {'a_intended', 'b_intended', 'a_executed', 'b_executed', 'a_observed_opp', 'b_observed_opp'} for field in changed_fields):
            action_stream_changed = True
        if any(field in {'payoff_a', 'payoff_b'} for field in changed_fields):
            payoff_stream_changed = True

    return {
        'first_any_diff_round': first_any_diff_round,
        'first_standing_diff_round': first_standing_diff_round,
        'standing_stream_changed': standing_stream_changed,
        'action_stream_changed': action_stream_changed,
        'payoff_stream_changed': payoff_stream_changed,
        'changed_fields': sorted(diff_fields),
    }


def _seed_report(seed_path: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    probe = oracle_mod._load_json(ROOT / seed_path)
    current = _simulate_exact_path_with_start(probe, declared_initial=False)
    declared = _simulate_exact_path_with_start(probe, declared_initial=True)
    trace_delta = _summarize_trace_delta(current['trace'], declared['trace'])
    stats_invariant = current['mean_stats'] == declared['mean_stats']
    classification = 'trace_only' if stats_invariant and trace_delta['standing_stream_changed'] and not trace_delta['action_stream_changed'] and not trace_delta['payoff_stream_changed'] else 'wider_than_trace_only'
    reputation = probe['world'].get('reputation') or {'kind': 'none'}

    return {
        'seed_path': seed_path,
        'probe_id': probe['id'],
        'matchup_id': probe['matchups'][0]['id'],
        'declared_initial_standing': oracle_mod._round6(float(reputation['initial_standing'])),
        'current_task_initial_standing': 1.0,
        'update_rule': reputation['update_rule'],
        'queue_rows': [
            {
                'family': row['family'],
                'variant': row['variant'],
                'proposed_test_name': row['proposed_test_name'],
                'target_lane': row['target_lane'],
            }
            for row in rows
        ],
        'current_mean_stats': current['mean_stats'],
        'declared_mean_stats': declared['mean_stats'],
        'mean_stats_invariant': stats_invariant,
        'trace_delta': trace_delta,
        'classification': classification,
        'current_trace_excerpt': current['trace'][:4],
        'declared_trace_excerpt': declared['trace'][:4],
        'implementor_note': (
            'current strategy selectors in these seeds do not branch on opponent_standing, so honoring declared initial_standing changes only the carried standing trace and standing-update bookkeeping, not the executed action/payoff stream'
            if classification == 'trace_only'
            else 'bootstrap repair changes more than the standing trace for this seed and needs closer witness review'
        ),
    }


def collect() -> dict[str, Any]:
    oracle_report = _load_oracle_report()
    affected_rows = [row for row in oracle_report['rows'] if 'standing_bootstrap' in row]
    rows_by_seed: dict[str, list[dict[str, Any]]] = {}
    for row in affected_rows:
        rows_by_seed.setdefault(row['seed_path'], []).append(row)

    seed_reports = [_seed_report(seed_path, rows_by_seed[seed_path]) for seed_path in sorted(rows_by_seed)]
    summary = {
        'affected_queue_rows': len(affected_rows),
        'affected_unique_seed_count': len(seed_reports),
        'mean_stats_invariant_rows': sum(len(seed['queue_rows']) for seed in seed_reports if seed['mean_stats_invariant']),
        'trace_only_rows': sum(len(seed['queue_rows']) for seed in seed_reports if seed['classification'] == 'trace_only'),
        'action_sensitive_rows': sum(len(seed['queue_rows']) for seed in seed_reports if seed['trace_delta']['action_stream_changed']),
        'payoff_sensitive_rows': sum(len(seed['queue_rows']) for seed in seed_reports if seed['trace_delta']['payoff_stream_changed']),
        'first_standing_diff_round_min': min(seed['trace_delta']['first_standing_diff_round'] for seed in seed_reports),
        'trace_only_seed_paths': [seed['seed_path'] for seed in seed_reports if seed['classification'] == 'trace_only'],
    }
    return {
        'tool': 'build_cloudtainer_standing_bootstrap_delta',
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source_oracle_report': str(ORACLE_REPORT.relative_to(ROOT)),
        'code_anchors': dict(CODE_ANCHORS),
        'summary': summary,
        'seeds': seed_reports,
    }


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report['summary']
    lines = [
        '# Cloudtainer Standing Bootstrap Delta',
        '',
        'This card answers one narrow but useful blocked-session question: if a future Rust-capable inheritor fixes the current `simple_standing.initial_standing` bootstrap seam, which of the current comeback witnesses actually move?',
        '',
        '## Summary',
        '',
        f"- affected queue rows: `{summary['affected_queue_rows']}` from `artifacts/reports/cloudtainer_rust_probe_oracles.json`",
        f"- affected unique seeds: `{summary['affected_unique_seed_count']}`",
        f"- rows whose mean stats stay invariant under the bootstrap repair: `{summary['mean_stats_invariant_rows']}`",
        f"- rows currently classified as trace-only drift: `{summary['trace_only_rows']}`",
        f"- rows with action-stream drift: `{summary['action_sensitive_rows']}`",
        f"- rows with payoff-stream drift: `{summary['payoff_sensitive_rows']}`",
        f"- earliest standing-trace divergence round: `r{summary['first_standing_diff_round_min']}`",
        '',
        '## Why the current delta is trace-only',
        '',
        f"- probe expansion still builds each `TaskSpec` via `TaskSpec::new(...)`, which seeds `standing_a` and `standing_b` from a fixed `1.0` rather than from `world.reputation.initial_standing`: `{CODE_ANCHORS['probe_expansion_task_new']}`, `{CODE_ANCHORS['task_default_standing']}`",
        f"- `run_match(...)` bootstraps its live reputation state from those task fields, then updates standing each round using the active simple-standing rule: `{CODE_ANCHORS['sim_standing_bootstrap']}`, `{CODE_ANCHORS['sim_standing_update']}`",
        f"- for the current affected probe seeds, the active strategy selectors consult prior observed actions/signals but do not branch on `opponent_standing`, so bootstrap repair changes the recorded standing trajectory without changing the executed action/payoff stream: `{CODE_ANCHORS['strategy_selectors_ignore_opponent_standing']}`",
        '',
        '## Seed table',
        '',
        '| Preferred seed | Queue rows | Declared start | Current task start | Mean stats move? | Action stream moves? | First standing diff | Classification |',
        '| --- | ---: | ---: | ---: | --- | --- | --- | --- |',
    ]
    for seed in report['seeds']:
        delta = seed['trace_delta']
        lines.append(
            f"| `{seed['seed_path']}` | `{len(seed['queue_rows'])}` | `{oracle_mod._fmt_num(seed['declared_initial_standing'])}` | `{oracle_mod._fmt_num(seed['current_task_initial_standing'])}` | `{'no' if seed['mean_stats_invariant'] else 'yes'}` | `{'yes' if delta['action_stream_changed'] else 'no'}` | `r{delta['first_standing_diff_round']}` | `{seed['classification']}` |"
        )

    lines.extend(['', '## Seed details', ''])
    for seed in report['seeds']:
        lines.append(f"### `{seed['seed_path']}`")
        lines.append('')
        lines.append(f"- probe/matchup: `{seed['probe_id']}` / `{seed['matchup_id']}`")
        lines.append(f"- declared vs current bootstrap: `{oracle_mod._fmt_num(seed['declared_initial_standing'])}` vs `{oracle_mod._fmt_num(seed['current_task_initial_standing'])}`")
        lines.append(f"- classification: `{seed['classification']}`")
        lines.append(f"- implementor note: {seed['implementor_note']}")
        lines.append('- queue rows carried by this seed:')
        for row in seed['queue_rows']:
            lines.append(
                f"  - `{row['family']}` / `{row['variant']}` -> `{row['proposed_test_name']}` in `{row['target_lane']}`"
            )
        cur_stats = seed['current_mean_stats']
        dec_stats = seed['declared_mean_stats']
        lines.append(
            '- mean stats under current bootstrap: '
            + ', '.join(
                [
                    f"`avg_payoff_a={oracle_mod._fmt_num(cur_stats['avg_payoff_a'])}`",
                    f"`avg_payoff_b={oracle_mod._fmt_num(cur_stats['avg_payoff_b'])}`",
                    f"`coop_rate_a={oracle_mod._fmt_num(cur_stats['coop_rate_a'])}`",
                    f"`coop_rate_b={oracle_mod._fmt_num(cur_stats['coop_rate_b'])}`",
                    f"`mutual_coop_rate={oracle_mod._fmt_num(cur_stats['mutual_coop_rate'])}`",
                    f"`mutual_defect_rate={oracle_mod._fmt_num(cur_stats['mutual_defect_rate'])}`",
                ]
            )
        )
        lines.append(
            '- mean stats under declared bootstrap: '
            + ', '.join(
                [
                    f"`avg_payoff_a={oracle_mod._fmt_num(dec_stats['avg_payoff_a'])}`",
                    f"`avg_payoff_b={oracle_mod._fmt_num(dec_stats['avg_payoff_b'])}`",
                    f"`coop_rate_a={oracle_mod._fmt_num(dec_stats['coop_rate_a'])}`",
                    f"`coop_rate_b={oracle_mod._fmt_num(dec_stats['coop_rate_b'])}`",
                    f"`mutual_coop_rate={oracle_mod._fmt_num(dec_stats['mutual_coop_rate'])}`",
                    f"`mutual_defect_rate={oracle_mod._fmt_num(dec_stats['mutual_defect_rate'])}`",
                ]
            )
        )
        delta = seed['trace_delta']
        lines.append(
            f"- trace delta: first standing diff at `r{delta['first_standing_diff_round']}`, action-stream changed=`{str(delta['action_stream_changed']).lower()}`, payoff-stream changed=`{str(delta['payoff_stream_changed']).lower()}`, changed fields={', '.join(f'`{field}`' for field in delta['changed_fields'])}"
        )
        lines.append('- current bootstrap trace excerpt:')
        for step in seed['current_trace_excerpt']:
            lines.append(
                f"  - `r{step['round']}` pre=(`{oracle_mod._fmt_num(step['standing_a_pre_update'])}`, `{oracle_mod._fmt_num(step['standing_b_pre_update'])}`) exec=(`{step['a_executed']}`, `{step['b_executed']}`) post=(`{oracle_mod._fmt_num(step.get('standing_a_post_update', step['standing_a_pre_update']))}`, `{oracle_mod._fmt_num(step.get('standing_b_post_update', step['standing_b_pre_update']))}`)"
            )
        lines.append('- declared-bootstrap trace excerpt:')
        for step in seed['declared_trace_excerpt']:
            lines.append(
                f"  - `r{step['round']}` pre=(`{oracle_mod._fmt_num(step['standing_a_pre_update'])}`, `{oracle_mod._fmt_num(step['standing_b_pre_update'])}`) exec=(`{step['a_executed']}`, `{step['b_executed']}`) post=(`{oracle_mod._fmt_num(step.get('standing_a_post_update', step['standing_a_pre_update']))}`, `{oracle_mod._fmt_num(step.get('standing_b_post_update', step['standing_b_pre_update']))}`)"
            )
        lines.append('')

    lines.extend(
        [
            '## Implementor guidance',
            '',
            '1. A future bootstrap repair can keep the current payoff/cooperation witness headlines for these three queue rows; the current delta surface says the risk is trace-only, not mean-stat drift.',
            '2. Once Cargo returns, apply the narrow source repair from `docs/RUST_STANDING_BOOTSTRAP_REPAIR_PATCH.md`, then land the standalone guard from `docs/RUST_STANDING_BOOTSTRAP_GUARD.md` so the first recorded standing values equal the declared `world.reputation.initial_standing` for a simple-standing probe seed. That closes the blind spot directly without turning this trace seam into a vague engine-wide default change.',
            '3. Re-run this card whenever a strategy starts consulting `opponent_standing`; at that point the same seam can become action-sensitive instead of remaining trace-only.',
            '',
        ]
    )
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build the cloudtainer standing-bootstrap delta card for the current simple-standing probe seeds.')
    parser.add_argument('--write', action='store_true', help='write the JSON report and markdown card to their canonical paths')
    args = parser.parse_args()

    report = collect()
    markdown = _render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
    else:
        print(markdown)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
