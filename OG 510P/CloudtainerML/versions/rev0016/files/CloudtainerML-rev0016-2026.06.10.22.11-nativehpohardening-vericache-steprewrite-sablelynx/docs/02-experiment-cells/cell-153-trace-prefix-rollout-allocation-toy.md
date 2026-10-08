# CELL-153 — TRACE Prefix Rollout Allocation Toy

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Question

Is rollout budget best spent at roots or at intermediate prefixes with high terminal-outcome contrast?

## Cheap first run

Runnable Python smoke test emits REV0013_TRACE_PREFIX_ROLLOUT_SMOKE.json.

## Metrics

- reward contrast
- success rate
- unique roots
- unique prefixes

## Stop condition

If prefix-level allocation is never better than uniform/root-level under sparse terminal rewards, demote agentic rollout allocation.
