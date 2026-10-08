from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.decision import PublicHeuristicAgent, PublicRandomAgent
from src.muc5.payoff import load_seed_decks
from src.muc5.replay import record_public_decision_trace, replay_public_decision_trace, write_trace_jsonl
from src.muc5.reward_guard import audit_reward_packet, reward_packet_from_state
from src.muc5.mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS, POLICY_KEEP_ALWAYS


def main() -> None:
    decks = load_seed_decks(ROOT / "data" / "seed_decks.json")
    deck_pairs = [
        ("forty_force_jace_pressure", "forty_overlord_impending"),
        ("forty_land_light_force_comboish", "sixty_counterwall_jace"),
        ("sixty_overlord_heavy", "forty_minimal_threat_decking_gambit"),
        ("sixty_no_overlord_jace_only", "sixty_drawless_control_big"),
    ]
    agent_pairs = [
        (PublicHeuristicAgent(), PublicHeuristicAgent()),
        (PublicHeuristicAgent(), PublicRandomAgent()),
        (PublicRandomAgent(), PublicHeuristicAgent()),
    ]
    lives = [20, 40]
    policies = [POLICY_KEEP_ALWAYS, POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS]

    traces = []
    rows = []
    failures = []
    idx = 0
    for d0_name, d1_name in deck_pairs:
        for a0, a1 in agent_pairs:
            for starting_life in lives:
                pol = policies[idx % len(policies)]
                idx += 1
                seed = 17000 + idx
                trace = record_public_decision_trace(
                    decks[d0_name],
                    decks[d1_name],
                    a0,
                    a1,
                    seed=seed,
                    transition_seed=seed + 100,
                    agent_seed=seed + 200,
                    starting_player=idx % 2,
                    starting_life=starting_life,
                    max_decisions=180,
                    mulligan_policy=pol,
                )
                result = replay_public_decision_trace(trace)
                if not result.passed:
                    failures.append({"idx": idx, "errors": list(result.errors)})
                # Reconstruct final reward safety from trace final only for row labels.
                rows.append(
                    {
                        "trace_id": f"rev0011_trace_{idx:03d}",
                        "deck0": d0_name,
                        "deck1": d1_name,
                        "agent0": trace["config"]["agent0"],
                        "agent1": trace["config"]["agent1"],
                        "starting_life": starting_life,
                        "mulligan_policy": str(pol),
                        "starting_player": trace["config"]["starting_player"],
                        "decisions": trace["final"]["decisions"],
                        "winner": trace["final"]["winner"],
                        "loss_reason": trace["final"]["loss_reason"],
                        "truncated": trace["final"]["truncated"],
                        "replay_passed": result.passed,
                        "checked_steps": result.checked_steps,
                        "final_fingerprint": result.final_fingerprint,
                    }
                )
                trace["trace_id"] = rows[-1]["trace_id"]
                traces.append(trace)

    out_traces = ROOT / "data" / "rev0011_replay_traces.jsonl"
    write_trace_jsonl(traces, out_traces)
    import csv

    out_rows = ROOT / "data" / "rev0011_replay_probe.csv"
    with out_rows.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "revision": "rev0011",
        "trace_count": len(traces),
        "total_recorded_decisions": sum(int(r["decisions"]) for r in rows),
        "replay_failures": failures,
        "all_replays_passed": not failures,
        "life_totals": sorted({int(r["starting_life"]) for r in rows}),
        "mulligan_policies": sorted({str(r["mulligan_policy"]) for r in rows}),
        "agents": sorted({str(r["agent0"]) for r in rows} | {str(r["agent1"]) for r in rows}),
        "note": "Trace path uses separate agent_rng and transition_rng so replay does not depend on tie-break RNG consumption by the agent.",
    }
    out_summary = ROOT / "data" / "rev0011_replay_probe_summary.json"
    out_summary.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
