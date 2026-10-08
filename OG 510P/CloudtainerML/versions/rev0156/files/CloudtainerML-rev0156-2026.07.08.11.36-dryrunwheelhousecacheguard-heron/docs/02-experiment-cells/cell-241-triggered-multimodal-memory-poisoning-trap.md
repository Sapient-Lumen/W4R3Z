# CELL-241 — Triggered Multimodal Memory Poisoning Trap

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0240`  
Sources: SRC-0267, SRC-0249

## Cheap first run

Add dormant trigger activation variables to the memory poisoning/admissibility simulator.

## Metrics

- triggered_attack_success_rate
- benign_activation_rate
- poisoned_read_fraction
- audit_detection_rate

## Required baselines

- similarity_only
- read_gate
- admissibility_contract
- trigger_aware_oracle

## Stop condition

If trigger behavior is already captured by delayed activation, fold into CELL-235.
