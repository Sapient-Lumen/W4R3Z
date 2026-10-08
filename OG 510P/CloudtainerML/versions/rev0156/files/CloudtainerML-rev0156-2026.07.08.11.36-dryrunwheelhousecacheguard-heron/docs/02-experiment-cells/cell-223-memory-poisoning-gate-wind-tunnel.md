# CELL-223 — Memory Poisoning Gate Wind Tunnel

Priority: **P0**  
Status: **implemented-native-rev0019**  
Idea: `IDEA-0222`  
Sources: SRC-0249, SRC-0250

## Cheap first run

Run experiments/memory_poisoning_gate/memory_poisoning_gate.cpp and inspect attack_success_rate vs benign recall under similarity-only, gate, provenance, and oracle policies.

## Metrics

- attack_success_rate
- benign_utility_recall
- mean_poisoned_read_fraction
- valid_recall_rate
- mean_utility

## Required baselines

- similarity_only
- write_time_filter
- read_time_gate
- provenance_decay
- dual_write_read_gate
- oracle_trust_boundary

## Stop condition

If provenance/read-write gates do not reduce poisoning tails in delayed/cross-domain regimes, the toy is missing the trust-boundary mechanism.
