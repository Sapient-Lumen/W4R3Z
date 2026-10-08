from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.sequential_race import load_mapelite_bundles, race_candidates
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, statistical_standings
from src.muc5.strategy_sets import code_policy_strategy_bundles


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.write_text("")
        return
    fields = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    data = ROOT / "data"
    candidates = load_mapelite_bundles(data / "rev0014_map_elites_archive.csv", limit=6)
    opponents = code_policy_strategy_bundles(data / "seed_decks.json")[:4]
    rows, stages, cand_standings = race_candidates(
        candidates,
        opponents,
        simulator_revision="rev0016",
        stage_reps=(1, 2),
        base_seed=1616000,
        max_decisions=500,
        eliminate_after_games=16,
    )
    standings = statistical_standings(rows, alpha=0.10, min_games_for_claim=24)
    pair_rows = pairwise_stat_rows(rows, alpha=0.10, min_games_for_claim=6)
    gate = audit_statistical_gate(rows, standings, pair_rows, min_raw_rows=1, max_truncation_rate=0.10)
    write_csv(data / "rev0016_sequential_race_games.csv", rows)
    write_csv(data / "rev0016_sequential_race_standings.csv", standings)
    write_csv(data / "rev0016_sequential_race_pairwise.csv", pair_rows)
    (data / "rev0016_sequential_race_stages.json").write_text(json.dumps([s.as_dict() for s in stages], indent=2, sort_keys=True))
    summary = {
        "simulator_revision": "rev0016",
        "codename": "cpplegalmenu-seqrace",
        "candidate_count": len(candidates),
        "opponent_count": len(opponents),
        "games": len(rows),
        "stage_count": len(stages),
        "stages": [s.as_dict() for s in stages],
        "candidate_standings_rows": len(cand_standings),
        "promotion_style_statistical_gate": gate.as_dict(),
        "truncations": sum(1 for r in rows if str(r.get("is_truncation")).lower() == "true"),
    }
    (data / "rev0016_sequential_race_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not gate.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
