# CELL-244 — Perturbation-Aware Multimodal Budget Toy

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0243`  
Sources: SRC-0265

## Cheap first run

Simulate two modalities with different perturbation curves and mixed queries.

## Metrics

- budget_utility
- modality_tail_loss
- query_mix_robustness

## Required baselines

- uniform_budget
- generic_salience
- perturbation_aware
- oracle_budget

## Stop condition

If multimodal specificity does not matter in toy regimes, defer.
