# CELL-325 — Self-Routing Hidden-State Entropy Probe

Priority: **P1**  
Status: `native-probe-added`  
Idea: `IDEA-0323`  
Sources: SRC-0343, SRC-0345

This P1 probe asks whether hidden-state subspaces can act as router logits. The key guard is hidden-subspace alignment; self-routing should not be promoted unless it survives misalignment, rare expert, and drift regimes.

## Cheap first run

Compile/run experiments/self_routing_entropy/self_routing_entropy.cpp and measure entropy/balance/rare miss.

## Metrics

- `acc`
- `entropy`
- `imbalance`
- `rare_miss`
- `route_flip`
- `score`

## Stop condition

Promote only if self-routing wins beyond hidden-subspace-aligned regimes.
