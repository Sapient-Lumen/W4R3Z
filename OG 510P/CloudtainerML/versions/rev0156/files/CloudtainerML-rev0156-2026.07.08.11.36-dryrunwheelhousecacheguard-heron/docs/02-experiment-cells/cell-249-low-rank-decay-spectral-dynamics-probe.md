# CELL-249 — Low-Rank Decay Spectral Dynamics Probe

Priority: **P0**  
Status: **candidate-with-runnable-native-probe**

## Cheap first run

Runnable C++ probe exists at experiments/low_rank_decay_dynamics/lrd_dynamics_probe.cpp; smoke output REV0022_LRD_DYNAMICS_PROBE_SMOKE.json.

## Metrics

- effective_rank
- signal_retention
- noise_retention
- generalization_proxy
- score

## Required baselines

- none_after_memorization
- l2_radial_decay
- hard_rank_cut
- oracle_spectrum

## Stop condition

If spectrum-only tests cannot separate LRD from hard rank-cut, escalate to a tiny modular-arithmetic trained run rather than more proxies.
