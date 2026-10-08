# CELL-328 — Adaptive Multiscale Expert Routing Toy

Priority: **P2**  
Status: `scouted`  
Idea: `IDEA-0326`  
Sources: SRC-0346

This P2 signal-domain toy is parked as a way to test operator/expert routing outside language-like tokens. It should not become P0 unless dynamic fusion beats fixed fusion under equal cost.

## Cheap first run

Generate synthetic periodic/noisy I/Q-like signals and route among short/medium/long resampled experts.

## Metrics

- `accuracy`
- `route_entropy`
- `noise_robustness`
- `cost`

## Stop condition

Only promote if dynamic fusion beats fixed fusion under equal cost.
