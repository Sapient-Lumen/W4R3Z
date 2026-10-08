# CELL-215 — JANUS Goal Distortion Probe

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0214`  
Sources: SRC-0242, SRC-0248

## Cheap first run

Run experiments/janus_goal_distortion/janus_distortion_probe.cpp.

## Metrics

- adverse coverage
- favorable coverage
- distortion
- vagueness
- hallucination proxy
- utility

## Required baselines

- neutral balanced
- goal naive
- memory goal bias
- provenance balanced gate
- exact material contract

## Stop condition

If all methods have equal adverse coverage, add harder fact pools.
