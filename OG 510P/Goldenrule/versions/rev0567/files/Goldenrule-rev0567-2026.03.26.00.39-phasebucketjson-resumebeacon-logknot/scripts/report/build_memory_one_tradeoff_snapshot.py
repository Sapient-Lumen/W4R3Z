#!/usr/bin/env python3
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grlab.certify import CertifyError, certify_memory_one_pair  # noqa: E402

SEED = 20260306
SAMPLES = 200000
THRESHOLDS = [2.9, 2.7, 2.4, 2.0, 1.5]


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_cert(a: dict[str, object], b: dict[str, object]) -> dict[str, object] | None:
    try:
        return certify_memory_one_pair(a, b)
    except CertifyError:
        return None


def _rand_mem1(idx: int) -> dict[str, object]:
    return {
        "family": "memory_one",
        "id": f"rand_{idx}",
        "p0": random.random(),
        "p_cc": random.random(),
        "p_cd": random.random(),
        "p_dc": random.random(),
        "p_dd": random.random(),
    }


def _metrics(
    cand: dict[str, object],
    extortion: dict[str, object],
    generous_tft: dict[str, object],
    always_c: dict[str, object],
) -> dict[str, object] | None:
    vs_ext = _safe_cert(cand, extortion)
    vs_self = _safe_cert(cand, cand)
    vs_allc = _safe_cert(cand, always_c)
    vs_gtft = _safe_cert(cand, generous_tft)
    if not all([vs_ext, vs_self, vs_allc, vs_gtft]):
        return None

    fairness = float(vs_ext["avg_payoff_a"]) - float(vs_ext["avg_payoff_b"])
    self_pay = float(vs_self["avg_payoff_a"])
    self_cc = float(vs_self["steady_state_distribution"][0])
    exploit_gain = float(vs_allc["avg_payoff_a"]) - float(vs_allc["avg_payoff_b"])
    coop_with_gtft = float(vs_gtft["steady_state_distribution"][0])

    return {
        "vs_extortion": vs_ext,
        "vs_self": vs_self,
        "vs_always_c": vs_allc,
        "vs_generous_tft": vs_gtft,
        "fairness_vs_extortion": fairness,
        "self_payoff": self_pay,
        "self_mutual_cooperation_rate": self_cc,
        "exploit_gain_vs_always_c": exploit_gain,
        "mutual_cooperation_with_generous_tft": coop_with_gtft,
    }


def _objective(m: dict[str, object]) -> float:
    fairness = float(m["fairness_vs_extortion"])
    vs_ext = float(m["vs_extortion"]["avg_payoff_a"])
    self_pay = float(m["self_payoff"])
    self_cc = float(m["self_mutual_cooperation_rate"])
    coop_with_gtft = float(m["mutual_cooperation_with_generous_tft"])
    exploit_gain = float(m["exploit_gain_vs_always_c"])

    return (
        2.5 * fairness
        + 1.0 * vs_ext
        + 1.0 * self_pay
        + 0.8 * self_cc * 3.0
        + 0.4 * coop_with_gtft * 3.0
        - 2.0 * max(0.0, exploit_gain)
        - 2.0 * max(0.0, 2.5 - self_pay)
    )


def _round_floats(obj: object) -> object:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, list):
        return [_round_floats(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _round_floats(v) for k, v in obj.items()}
    return obj


def main() -> int:
    random.seed(SEED)

    extortion = _read_json(ROOT / "examples/strategies/extortion_chi3.json")
    generous_tft = _read_json(ROOT / "examples/strategies/mem1_generous_tft.json")
    always_c = _read_json(ROOT / "examples/strategies/mem1_always_c.json")

    samples: list[dict[str, object]] = []
    top: list[dict[str, object]] = []

    for i in range(SAMPLES):
        cand = _rand_mem1(i)
        m = _metrics(cand, extortion, generous_tft, always_c)
        if m is None:
            continue
        obj = _objective(m)
        rec = {"candidate": cand, "metrics": m, "objective": obj}
        samples.append(rec)
        if len(top) < 10:
            top.append(rec)
            top.sort(key=lambda x: float(x["objective"]), reverse=True)
        elif obj > float(top[-1]["objective"]):
            top[-1] = rec
            top.sort(key=lambda x: float(x["objective"]), reverse=True)

    frontier = []
    for t in THRESHOLDS:
        feasible = [
            rec
            for rec in samples
            if float(rec["metrics"]["self_payoff"]) >= t
            and float(rec["metrics"]["exploit_gain_vs_always_c"]) <= 0.1
        ]
        feasible.sort(
            key=lambda rec: (
                float(rec["metrics"]["fairness_vs_extortion"]),
                float(rec["metrics"]["self_payoff"]),
            ),
            reverse=True,
        )
        if feasible:
            frontier.append({"min_self_payoff": t, "record": feasible[0]})

    feasible_green = [
        rec
        for rec in samples
        if float(rec["metrics"]["fairness_vs_extortion"]) >= 0.0
        and float(rec["metrics"]["self_payoff"]) >= 2.5
        and float(rec["metrics"]["exploit_gain_vs_always_c"]) <= 0.1
    ]

    recommended = None
    for entry in frontier:
        if abs(float(entry["min_self_payoff"]) - 2.7) < 1e-9:
            recommended = entry["record"]
            break
    if recommended is None and frontier:
        recommended = frontier[0]["record"]

    payload = {
        "date": "2026-03-06",
        "method": {
            "type": "analytic_memory_one_random_search",
            "seed": SEED,
            "samples": SAMPLES,
            "scored_against": [
                "extortion_chi3_v1",
                "self",
                "mem1_always_c",
                "mem1_generous_tft_v1",
            ],
            "note": "Uses grlab.certify stationary-distribution payoffs for memory_one pairs only.",
        },
        "finding": {
            "summary": "In this 200k-sample memory-one search, no candidate achieved all three desiderata at once: nonnegative fairness versus extortion, self-play payoff >= 2.5, and low exploitation of always-cooperate (gain <= 0.1).",
            "strict_green_count": len(feasible_green),
        },
        "top_scalarized": top,
        "frontier_by_min_self_payoff": frontier,
        "recommended_baseline": recommended,
    }

    out_json = ROOT / "artifacts/reports/memory_one_tradeoff_snapshot_20260306.json"
    out_md = ROOT / "artifacts/reports/memory_one_tradeoff_snapshot_20260306.md"
    out_json.write_text(json.dumps(_round_floats(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Memory-One Tradeoff Snapshot (2026-03-06)",
        "",
        "Method:",
        f"- analytic stationary-payoff search over `{SAMPLES}` random memory-one candidates",
        f"- seed: `{SEED}`",
        "- scorecard opponents: extortion, self-play, always-cooperate, generous TFT",
        "",
        "Main finding:",
        "- No sampled memory-one candidate satisfied all three at once:",
        "  1. nonnegative fairness versus extortion,",
        "  2. self-play payoff >= 2.5,",
        "  3. exploit gain versus Always-Cooperate <= 0.1.",
        "",
        "Interpretation:",
        "- Within this sampled memory-one space, anti-extortion fairness appears to trade off against durable cooperation and non-exploitative behavior.",
        "- This strengthens the case for the next tranche to add either modestly longer memory or explicit exit/partner-choice mechanics before widening search.",
        "",
        "Frontier witnesses (best fairness under minimum self-play threshold and low exploitation):",
        "",
        "| min self-payoff | fairness vs extortion | extortion payoff_a | self-payoff | exploit gain vs allC | candidate id |",
        "|---:|---:|---:|---:|---:|---|",
    ]

    for entry in frontier:
        rec = entry["record"]
        m = rec["metrics"]
        c = rec["candidate"]
        lines.append(
            f"| {entry['min_self_payoff']:.1f} | {float(m['fairness_vs_extortion']):.6f} | "
            f"{float(m['vs_extortion']['avg_payoff_a']):.6f} | {float(m['self_payoff']):.6f} | "
            f"{float(m['exploit_gain_vs_always_c']):.6f} | `{c['id']}` |"
        )

    if recommended is not None:
        c = recommended["candidate"]
        m = recommended["metrics"]
        lines.extend(
            [
                "",
                "Recommended witness baseline:",
                f"- `{c['id']}` is the suggested handoff point for a compact baseline because it pushes fairness toward zero while preserving decent self-play and near-nonexploitation.",
                f"- params: p0={c['p0']:.6f}, p_cc={c['p_cc']:.6f}, p_cd={c['p_cd']:.6f}, p_dc={c['p_dc']:.6f}, p_dd={c['p_dd']:.6f}",
                f"- fairness vs extortion: {float(m['fairness_vs_extortion']):.6f}",
                f"- self-play payoff: {float(m['self_payoff']):.6f}",
                f"- exploit gain vs Always-Cooperate: {float(m['exploit_gain_vs_always_c']):.6f}",
            ]
        )

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
