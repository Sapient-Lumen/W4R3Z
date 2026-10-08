# CELL-320 — Frequent Directions Streaming Memory Sketch

Priority: P1

Status: planned-native

Question: Can FD-style sketches preserve the right low-rank memory directions under drift without erasing rare directions?

Cheap first run: Implement FD/reservoir/random-projection/exact sketch C++ probe over drift and rare-direction streams.

Metrics: subspace_error, retrieval_error, rare_direction_miss, cost, regret

Required baselines: exact_covariance, frequent_directions, reservoir_sketch, random_projection

Stop condition: Do not promote if mean subspace error hides rare-direction failure.
