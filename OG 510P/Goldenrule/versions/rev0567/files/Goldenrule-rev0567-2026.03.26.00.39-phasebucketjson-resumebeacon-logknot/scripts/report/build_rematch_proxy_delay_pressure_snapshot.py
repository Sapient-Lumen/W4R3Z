#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "artifacts" / "reports" / "partner_choice_proxy_snapshot_20260306.json"
OUT_JSON = ROOT / "artifacts" / "reports" / "rematch_proxy_delay_pressure_snapshot_20260306.json"
OUT_MD = ROOT / "artifacts" / "reports" / "rematch_proxy_delay_pressure_snapshot_20260306.md"


def scenario_value(block: dict[str, dict[str, float]], ext: int, delay: int) -> float:
    return float(block[f"ext{ext}_delay{delay}"]["overall_avg_payoff"])


def margins(a: dict[str, dict[str, float]], b: dict[str, dict[str, float]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for ext in (20, 50, 80):
        for delay in (0, 1, 2):
            key = f"ext{ext}_delay{delay}"
            out[key] = round(float(a[key]["overall_avg_payoff"]) - float(b[key]["overall_avg_payoff"]), 6)
    return out


def policy_block(payload: dict, key: str) -> dict[str, dict[str, float]]:
    return payload["baseline_comparison"][key]


def main() -> int:
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    leave_after_break = policy_block(payload, "leave_after_break")
    courteous_firm = policy_block(payload, "courteous_firm")
    always_c = policy_block(payload, "always_cooperate")
    first_defect_exit_trap = policy_block(payload, "first_defect_exit_trap")
    best_balanced_nice = payload["findings"]["best_balanced_nice_candidate"]["proxy"]

    policies = {
        "CCEEE": leave_after_break,
        "CCDDE": best_balanced_nice,
        "always_c": always_c,
        "courteous_firm": courteous_firm,
        "DCECC": first_defect_exit_trap,
    }

    delay_penalty: dict[str, dict[str, float]] = {}
    extortion_penalty: dict[str, dict[str, float]] = {}
    for name, block in policies.items():
        delay_penalty[name] = {
            f"ext{ext}": round(scenario_value(block, ext, 0) - scenario_value(block, ext, 2), 6)
            for ext in (20, 50, 80)
        }
        extortion_penalty[name] = {
            f"delay{delay}": round(scenario_value(block, 20, delay) - scenario_value(block, 80, delay), 6)
            for delay in (0, 1, 2)
        }

    cceee_vs = {
        "always_c": margins(leave_after_break, always_c),
        "courteous_firm": margins(leave_after_break, courteous_firm),
        "DCECC": margins(leave_after_break, first_defect_exit_trap),
        "CCDDE": margins(leave_after_break, best_balanced_nice),
    }

    summary = {
        "source": str(SRC.relative_to(ROOT)),
        "focus": "Treat rematch delay as a first-class world parameter in leave/rematch benchmarks.",
        "headline_findings": {
            "cceee_delay_penalty_rises_with_extortion_share": delay_penalty["CCEEE"],
            "ccdde_delay_penalty_rises_with_extortion_share": delay_penalty["CCDDE"],
            "cceee_beats_key_baselines_in_all_9_cells": {
                k: {
                    "min_margin": min(v.values()),
                    "max_margin": max(v.values()),
                    "wins_all_cells": all(x > 0 for x in v.values()),
                }
                for k, v in cceee_vs.items()
                if k != "CCDDE"
            },
            "cceee_vs_ccdde": {
                "min_margin": min(cceee_vs["CCDDE"].values()),
                "max_margin": max(cceee_vs["CCDDE"].values()),
                "only_loss_cell": [k for k, v in cceee_vs["CCDDE"].items() if v < 0],
            },
        },
        "delay_penalty": delay_penalty,
        "extortion_share_penalty": extortion_penalty,
        "scenario_margins_cceee": cceee_vs,
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Rematch-Proxy Delay Pressure Snapshot (2026-03-06)",
        "",
        "Method:",
        "- reused `artifacts/reports/partner_choice_proxy_snapshot_20260306.json`",
        "- compared the canonical handoff baseline `CCEEE` (`leave_after_break`) with `CCDDE`, `always_c`, `courteous_firm`, and the first-defect exit trap `DCECC`",
        "- summarized how much overall payoff is lost when rematch delay rises from `0` to `2` stage rounds, and how much is lost when extortion share rises from `0.2` to `0.8`",
        "",
        "Main finding:",
        "- Rematch delay is not cosmetic. In the current proxy it is a direct tax on leave-based policies, and that tax grows as extortion becomes more common.",
        "- For `CCEEE`, the delay penalty grows from `0.134055` at `extortion=0.2` to `0.301582` at `extortion=0.8`.",
        "- For `CCDDE`, the same penalty grows from `0.133138` to `0.263853`.",
        "- Even with that tax, `CCEEE` still beats `always_c`, `courteous_firm`, and `DCECC` in all `9` tested proxy cells.",
        "- Against `CCDDE`, `CCEEE` is nearly tied and only loses in the single harshest cell (`extortion=0.8`, `delay=2`).",
        "",
        "Interpretation:",
        "- Leave/rematch conclusions should not be reported at one hidden default delay. Delay changes which policy shapes look robust.",
        "- The archive's compact handoff baseline remains useful exactly because it is simple and stays competitive across the whole grid, not because delay is irrelevant.",
        "",
        "Implementor implication:",
        "- When the engine grows a real rematch world, make rematch delay / search friction an explicit world field, include it in benchmark sweeps, and treat claims that hold only at one delay as provisional.",
        "",
        "Selected margins for `CCEEE` (overall payoff advantage):",
        "",
        "| comparator | min margin across grid | max margin across grid | wins all 9 cells |",
        "|---|---:|---:|---:|",
        f"| `always_c` | {min(cceee_vs['always_c'].values()):.6f} | {max(cceee_vs['always_c'].values()):.6f} | yes |",
        f"| `courteous_firm` | {min(cceee_vs['courteous_firm'].values()):.6f} | {max(cceee_vs['courteous_firm'].values()):.6f} | yes |",
        f"| `DCECC` | {min(cceee_vs['DCECC'].values()):.6f} | {max(cceee_vs['DCECC'].values()):.6f} | yes |",
        f"| `CCDDE` | {min(cceee_vs['CCDDE'].values()):.6f} | {max(cceee_vs['CCDDE'].values()):.6f} | no |",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
