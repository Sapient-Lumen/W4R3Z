# CELL-094 — HIST Sliding-Window Order Probe

Priority: **P1**  
Status: **runnable**  
Idea: `IDEA-0094`  
Sources: SRC-0155

## Cheap first run

Infer outgoing token from histogram updates without PE.

## Baselines

- delta exact
- delta int8 noisy
- static hist mode
- static hist minority
- random

## Metrics

- outgoing_accuracy
- order_bit_accuracy
- invalid_delta_rate
- state_reconstruction_error

## Stop condition

If noisy delta brittle, keep theory lane only.
