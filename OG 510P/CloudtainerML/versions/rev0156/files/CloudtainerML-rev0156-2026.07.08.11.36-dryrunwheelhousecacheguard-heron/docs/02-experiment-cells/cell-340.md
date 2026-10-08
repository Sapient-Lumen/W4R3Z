# CELL-340 — Entropy-Guided Progressive Depth Looping Scout

Priority: **P1**  
Status: **scouted**

## Question

Can high-entropy-head looping make tiny copy/head emergence smoother or faster than fixed recurrent depth?

## Cheap first run

Future tiny trained copy/modular task with head entropy measurements and loop-depth schedules.

## Metrics

- `steps_to_threshold`
- `entropy_precursor`
- `extra_compute`
- `abruptness`

## Required baselines

- `fixed_loop`
- `no_loop`
- `random_head_loop`

## Stop condition

Promote only if entropy-guided looping improves convergence or monitorability under equal compute.
