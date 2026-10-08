# Adversarial Extortion Baselines

This note tracks adversarial baseline strategies that pressure-test reciprocity claims.

## Why this matters

- Reciprocity claims are weak unless tested against exploitative opponents.
- Extortion-style memory-one strategies provide a clear, reproducible adversarial benchmark.

## Practical controls

- Keep an adversarial suite in probe/gauntlet artifacts.
- Record seed, world hash, and strategy hash for every adversarial run.
- Require candidates to meet explicit payoff thresholds against adversarial baselines.

## Current artifacts

- `examples/strategies/extortion_chi3.json`
- `examples/strategies/adversaries/`
- `examples/gauntlet/gauntlet_v2.json`
