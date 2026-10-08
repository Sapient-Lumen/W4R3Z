# CELL-201 — Conversation-Level Agentic Scheduler Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0200`  
Sources: SRC-0215

## Cheap first run

No runnable probe yet; C++ event scheduler for first-turn prefill, one KV transfer, and pinned memory-bound tail.

## Metrics

- time to first effective token
- last-turn TBT
- KV movement bytes
- SLO violation rate

## Required baselines

- collocated
- per_turn_prediction
- conversation_level
- oracle_scheduler

## Stop condition

If turn-level prediction wins except under extreme error, quantify phase boundary and demote.
