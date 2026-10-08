# CELL-226 — Agent Memory Lifecycle Cost Frontier

Priority: **P1**  
Status: **implemented-native-rev0019**  
Idea: `IDEA-0225`  
Sources: SRC-0252

## Cheap first run

Run experiments/agent_memory_lifecycle_cost/memory_lifecycle_cost_probe.cpp and sweep query count, mutation, structure need, and staleness.

## Metrics

- mean_accuracy
- mean_freshness
- mean_construction_cost
- mean_serve_cost
- mean_total_cost
- mean_utility

## Required baselines

- bm25_flat
- embed_rag
- structured_triples
- agentic_control_flow
- on_demand_structure
- freshness_scheduled_hybrid
- oracle_lifecycle

## Stop condition

If lifecycle cost has no effect on winner, replace toy constants with measured timings from real small retrieval stacks.
