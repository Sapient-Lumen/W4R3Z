# CELL-195 — Memory Provenance Phase Sweep

Priority: **P0**  
Status: **runnable_native_probe**  
Idea: `IDEA-0194`  
Sources: SRC-0221

## Cheap first run

Run experiments/memory_provenance_phase/memory_provenance_phase.cpp; native audit emits REV0019_MEMORY_PROVENANCE_PHASE_SMOKE.json.

## Metrics

- mean utility
- accuracy
- sycophancy rate
- abstention rate

## Required baselines

- no_persistent_memory
- belief_snippet_memory
- recency_memory
- provenance_balanced_memory
- skeptical_highstakes_memory
- correction_linked_memory
- oracle_provenance

## Stop condition

If correction-linked provenance cannot beat no-memory in high-risk regimes, memory must be opt-in there.
