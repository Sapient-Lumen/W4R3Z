# Extortion Metric Snapshot (2026-03-06)

Local artifact readout:
- `search_vs_extortion.json` found a short-horizon candidate with `avg_a = 2.58` and a favorable payoff gap (`avg_b - avg_a = -0.20`).
- `random_search_vs_extortion_500.json` found a higher-`avg_a` candidate (`1.993`) that still handed the extortioner a much larger score (`avg_b - avg_a = 1.41`).
- `hill_climb_vs_extortion.json` reduced the gap (`0.535`) but at lower self-payoff (`1.852`).
- `vampire_result.json` failed overall; `noisy_vampire_result.json` passed but still shows strong exploitation of Always-Cooperate under noise.

Conclusion:
A payoff-only objective is not enough for Golden-Rule-like strategy search in vampire settings.
