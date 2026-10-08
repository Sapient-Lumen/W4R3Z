from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))



def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def main() -> None:
    scenarios = load_json(ROOT / "data" / "rev0010_rules_scenarios_summary.json")
    fuzz = load_json(ROOT / "data" / "rev0010_fuzz_summary.json")
    profile = load_json(ROOT / "data" / "rev0010_simulator_profile_summary.json")
    all_scenarios = bool(scenarios.get("all_passed"))
    fuzz_ok = fuzz.get("failures") == 0 and int(fuzz.get("games", 0)) >= 300
    public_dps = float(profile.get("public_decision_frame", {}).get("decisions_per_second", 0) or 0)
    readiness = [
        {
            "level": "A: automated-play smoke simulator",
            "status": "green" if all_scenarios and fuzz_ok else "yellow",
            "meaning": "Random/scripted/public agents can play end-to-end MUC-5 games with invariants checked.",
        },
        {
            "level": "B: learning-loop beta simulator",
            "status": "yellow",
            "meaning": "DecisionFrame/action-mask boundary exists; more directed rule scenarios and regression fixtures should be added before trusting learned results.",
        },
        {
            "level": "C: research-claim tournament simulator",
            "status": "red",
            "meaning": "Not ready for strategic claims until payoff tables have higher reps, truncation policy is stress-tested, and known simplifications are either fixed or intentionally frozen.",
        },
    ]
    summary = {
        "revision": "rev0010",
        "short_answer": "The simulator is already working for automated beta play, but not yet trustworthy enough for strong learning/tournament conclusions.",
        "readiness_levels": readiness,
        "how_far": {
            "already_available": [
                "five-card deck construction",
                "London mulligan agent scaffold",
                "20/40 life dial",
                "public DecisionFrame legal-action interface",
                "automated agent games",
                "payoff-table smoke runs",
                "gametable external seat",
                "card-conservation/leakage/performance audits",
            ],
            "remaining_before_learning_grade": [
                "expand scenario suite around mulligan ordering, Jace top-card choices, combat/Jace damage, and postcombat main interactions",
                "formalize/freeze the known simplifications list",
                "keep fuzzing with invariant checks in every simulator revision",
                "reduce observation-construction overhead if public DecisionFrame becomes the rollout bottleneck",
            ],
            "remaining_before_tournament_claims": [
                "higher-rep payoff tables",
                "truncation/stall policy stress tests",
                "seat-order/life/mulligan stratification checks",
                "learned/evolved agents evaluated only through public frames",
            ],
        },
        "evidence": {
            "scenario_count": scenarios.get("scenario_count"),
            "scenario_failed": scenarios.get("failed"),
            "fuzz_games": fuzz.get("games"),
            "fuzz_decisions": fuzz.get("decisions"),
            "fuzz_failures": fuzz.get("failures"),
            "public_decision_frame_decisions_per_second": public_dps,
        },
    }
    out = ROOT / "data" / "rev0010_simulator_readiness.json"
    out.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not (all_scenarios and fuzz_ok):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
