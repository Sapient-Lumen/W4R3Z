# Memory-One Tradeoff Snapshot (2026-03-06)

Method:
- analytic stationary-payoff search over `200000` random memory-one candidates
- seed: `20260306`
- scorecard opponents: extortion, self-play, always-cooperate, generous TFT

Main finding:
- No sampled memory-one candidate satisfied all three at once:
  1. nonnegative fairness versus extortion,
  2. self-play payoff >= 2.5,
  3. exploit gain versus Always-Cooperate <= 0.1.

Interpretation:
- Within this sampled memory-one space, anti-extortion fairness appears to trade off against durable cooperation and non-exploitative behavior.
- This strengthens the case for the next tranche to add either modestly longer memory or explicit exit/partner-choice mechanics before widening search.

Frontier witnesses (best fairness under minimum self-play threshold and low exploitation):

| min self-payoff | fairness vs extortion | extortion payoff_a | self-payoff | exploit gain vs allC | candidate id |
|---:|---:|---:|---:|---:|---|
| 2.9 | -0.077372 | 1.038686 | 2.977407 | 0.008715 | `rand_191821` |
| 2.7 | -0.037313 | 1.018657 | 2.730169 | 0.010129 | `rand_73803` |
| 2.4 | -0.024104 | 1.012052 | 2.455712 | 0.074616 | `rand_47112` |
| 2.0 | -0.016470 | 1.008235 | 2.076270 | 0.033338 | `rand_185159` |
| 1.5 | -0.012529 | 1.006265 | 1.504884 | 0.045800 | `rand_49091` |

Recommended witness baseline:
- `rand_73803` is the suggested handoff point for a compact baseline because it pushes fairness toward zero while preserving decent self-play and near-nonexploitation.
- params: p0=0.251163, p_cc=0.998360, p_cd=0.351544, p_dc=0.807921, p_dd=0.004668
- fairness vs extortion: -0.037313
- self-play payoff: 2.730169
- exploit gain vs Always-Cooperate: 0.010129
