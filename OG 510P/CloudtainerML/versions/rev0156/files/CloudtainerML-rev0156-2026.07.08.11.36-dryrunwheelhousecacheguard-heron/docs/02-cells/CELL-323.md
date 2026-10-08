# CELL-323 — Routing Absorption Gate Wind Tunnel

Priority: **P0**  
Status: `native-probe-added`  
Idea: `IDEA-0321`  
Sources: SRC-0341

This native wind tunnel checks whether sparse-attention gates fail because representations absorb the gate. The critical baselines are frozen random gates, posthoc gates on fixed QKV, and dense escape. Promote only if a learned gate beats random under deployment shift and rare-route pressure.

## Cheap first run

Compile/run experiments/routing_absorption_gate/routing_absorption_gate.cpp; compare frozen_random_gate, learned_gate_end2end, posthoc_gate_fixed_qkv, and gate_plus_dense_escape.

## Metrics

- `quality`
- `gate_f1`
- `deployment_loss`
- `absorption_gap`
- `rare_miss`
- `regret`
- `score`

## Stop condition

Promote only if posthoc/escape methods beat random without hiding deployment loss.
