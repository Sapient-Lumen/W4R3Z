# CELL-334 — Sessa Feedback State Tail Scout

Priority: **P1**  
Status: **scouted**

## Question

Does putting attention inside a recurrent feedback path create a different old-evidence decay law than one-shot attention plus recurrent state?

## Cheap first run

Draft a future influence-tail C++ probe comparing one-shot attention, recurrent state, xLSTM gate correction, and feedback attention.

## Metrics

- `tail_exponent_proxy`
- `selective_retrieval`
- `state_cost`
- `old_needle_recall`

## Required baselines

- `transformer_one_shot`
- `xLSTM_like_gate`
- `linear_state`

## Stop condition

Do not promote without a non-symbolic retrieval or influence-tail screen.
