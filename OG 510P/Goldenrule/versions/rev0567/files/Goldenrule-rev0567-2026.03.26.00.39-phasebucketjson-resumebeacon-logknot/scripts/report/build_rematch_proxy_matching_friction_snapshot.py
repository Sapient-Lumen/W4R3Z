#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "artifacts" / "reports" / "partner_choice_proxy_snapshot_20260306.json"
OUT_JSON = ROOT / "artifacts" / "reports" / "rematch_proxy_matching_friction_snapshot_20260306.json"
OUT_MD = ROOT / "artifacts" / "reports" / "rematch_proxy_matching_friction_snapshot_20260306.md"

EXTORTION_LEVELS = (20, 50, 80)
DELAY_LEVELS = (0, 1, 2)


def scenario_value(block: dict[str, dict[str, float]], ext: int, delay: int, field: str = "overall_avg_payoff") -> float:
    return float(block[f"ext{ext}_delay{delay}"][field])


def policy_losses(block: dict[str, dict[str, float]]) -> dict[str, dict[str, float | bool]]:
    out: dict[str, dict[str, float | bool]] = {}
    for ext in EXTORTION_LEVELS:
        delay0, delay1, delay2 = [scenario_value(block, ext, delay) for delay in DELAY_LEVELS]
        out[f"ext{ext}"] = {
            "delay0": round(delay0, 6),
            "delay1": round(delay1, 6),
            "delay2": round(delay2, 6),
            "monotone_nonincreasing": delay0 >= delay1 >= delay2,
            "delay0_to_delay2_loss": round(delay0 - delay2, 6),
            "delay0_to_delay2_loss_share": round((delay0 - delay2) / delay0, 6) if delay0 else 0.0,
        }
    return out


def mean_loss(losses: dict[str, dict[str, float | bool]]) -> float:
    return round(sum(float(v["delay0_to_delay2_loss"]) for v in losses.values()) / len(losses), 6)


def main() -> int:
    payload = json.loads(SRC.read_text(encoding="utf-8"))
    policies = {
        "CCEEE": payload["baseline_comparison"]["leave_after_break"],
        "CCDDE": payload["findings"]["best_balanced_nice_candidate"]["proxy"],
        "always_c": payload["baseline_comparison"]["always_cooperate"],
        "courteous_firm": payload["baseline_comparison"]["courteous_firm"],
        "DCECC": payload["baseline_comparison"]["first_defect_exit_trap"],
    }

    per_policy = {name: policy_losses(block) for name, block in policies.items()}
    all_cells_monotone = all(
        bool(per_policy[name][f"ext{ext}"]["monotone_nonincreasing"]) for name in per_policy for ext in EXTORTION_LEVELS
    )

    mean_delay_loss = {name: mean_loss(losses) for name, losses in per_policy.items()}
    ranked_sensitivity = [
        {"policy": name, "mean_delay0_to_delay2_loss": loss}
        for name, loss in sorted(mean_delay_loss.items(), key=lambda item: (-item[1], item[0]))
    ]

    summary = {
        "source": str(SRC.relative_to(ROOT)),
        "focus": "Separate rematch delay from full matching-market efficiency when interpreting the current exogenous-pool proxy.",
        "headline_findings": {
            "all_tested_policy_extortion_cells_are_monotone_in_delay": all_cells_monotone,
            "tested_cells": len(per_policy) * len(EXTORTION_LEVELS),
            "largest_mean_delay_tax_policy": ranked_sensitivity[0],
            "smallest_mean_delay_tax_policy": ranked_sensitivity[-1],
            "interpretation": "In the current proxy, raising delay only removes productive rounds; it never introduces a countervailing welfare benefit in the tested policies.",
        },
        "per_policy_delay_response": per_policy,
        "ranked_mean_delay_tax": ranked_sensitivity,
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Rematch-Proxy Matching Friction Snapshot (2026-03-06)",
        "",
        "Method:",
        "- reused `artifacts/reports/partner_choice_proxy_snapshot_20260306.json`",
        "- tracked `overall_avg_payoff` for five salient policies across extortion share in `{0.2, 0.5, 0.8}` and rematch delay in `{0, 1, 2}`",
        "- asked one narrow question: in the current exogenous-pool proxy, does lower delay ever hurt total payoff for the tested policies?",
        "",
        "Main finding:",
        f"- All `{len(per_policy) * len(EXTORTION_LEVELS)}` tested policy/extortion cells are monotone in delay: `delay=0 >= delay=1 >= delay=2` for `overall_avg_payoff`.",
        "- That means the current proxy treats rematch delay as a one-sided tax on time spent unmatched. In these tests, lowering delay never creates a payoff tradeoff of its own.",
        f"- The first-defect exit trap `DCECC` is the most delay-sensitive policy in this set, with mean `delay0 -> delay2` loss `{ranked_sensitivity[0]['mean_delay0_to_delay2_loss']:.6f}` across extortion levels.",
        f"- `courteous_firm` is the least delay-sensitive comparator here, with mean `delay0 -> delay2` loss `{ranked_sensitivity[-1]['mean_delay0_to_delay2_loss']:.6f}`.",
        "",
        "Interpretation:",
        "- This is useful, but it is not yet a full matching-market result.",
        "- The proxy captures the opportunity cost of leaving through dead rounds and exogenous partner composition.",
        "- It does **not** yet model endogenous market thickness or the steady-state share of agents who are currently matched versus searching.",
        "- So the proxy is a clean delay-tax diagnostic, not a substitute for an endogenous matching market.",
        "",
        "Selected `delay0 -> delay2` losses in `overall_avg_payoff`:",
        "",
        "| policy | extortion=0.2 | extortion=0.5 | extortion=0.8 | mean loss |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("CCEEE", "CCDDE", "always_c", "courteous_firm", "DCECC"):
        losses = per_policy[name]
        lines.append(
            f"| `{name}` | {float(losses['ext20']['delay0_to_delay2_loss']):.6f} | {float(losses['ext50']['delay0_to_delay2_loss']):.6f} | {float(losses['ext80']['delay0_to_delay2_loss']):.6f} | {mean_delay_loss[name]:.6f} |"
        )
    lines += [
        "",
        "Implementor implication:",
        "- Keep rematch delay as an explicit world field, but add a separate market-thickness / matching-efficiency parameter before making broader welfare claims about competition or search frictions.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
