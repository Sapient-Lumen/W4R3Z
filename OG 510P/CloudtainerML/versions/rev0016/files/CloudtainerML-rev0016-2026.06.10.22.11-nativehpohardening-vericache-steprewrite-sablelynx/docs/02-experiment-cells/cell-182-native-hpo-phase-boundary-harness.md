# CELL-182: Native HPO Phase Boundary Harness

Priority: P0

Status: runnable

Idea: IDEA-0181

Source: SRC-0210, SRC-0041, SRC-0145

Cheap first run: C++ optimizer arena over synthetic phase diagrams; output artifact REV0015_NATIVE_HPO_PHASE_SMOKE.json.

Metrics:
- mean regret to dense-grid optimum
- winner counts
- budget sensitivity

Baselines:
- grid
- random
- domain prior
- cross entropy
- Centaur-style state prior

Stop condition: If hybrid wins only when prior matches the hidden optimum, use it only as exploratory automation.
