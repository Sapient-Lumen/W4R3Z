# CELL-347 — Tiny Route/Gain Trained Readout

Priority: **P1**  
Status: **trained-probe-added**

## Question

Does route/gain decoupling survive a constrained trained readout, or can importance-in-route scoring replace explicit value gain?

## Cheap first run

Run experiments/tiny_route_gain_train/tiny_route_gain_train.py. Compare route-only, importance-in-route, gain-decoupled, hybrid and oracle gain readouts.

## Metrics

- `promotion_score`
- `final_acc`
- `route_error`
- `gain_error`
- `source_attention_mass`
- `distractor_attention_mass`
- `source_gain`
- `distractor_gain`

## Required baselines

- `route_only`
- `importance_in_route`
- `gain_decoupled`
- `oracle_gain`

## Stop condition

Keep route/gain as diagnostic if importance-in-route dominates; promote only if explicit gain wins held-out regimes without increasing distractor amplification.
