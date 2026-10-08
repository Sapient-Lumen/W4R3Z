# CELL-275 — Dynamic Short Convolution Repair HPO

- priority: P0
- status: implemented-native-rev0025
- idea: IDEA-0274
- sources: SRC-0253

## Cheap first run

Harden dynamic-conv lane with global-bypass and anti-alias repairs.

## Metrics

- accuracy
- cost
- alias_error
- score

## Required baselines

- vanilla_attention
- static_short_conv
- dynamic_short_conv
- dynamic_plus_global_bypass
- dynamic_antialias_gate
- oracle_regime_switch

## Stop condition

Promote if repair policies beat naive dynamic convolution in global/aliasing traps.
