# CELL-162 — Native C++ Microkernel Promotion Lane

Priority: **P0**  
Status: **runnable-native-audit**  
Idea: `IDEA-0161` — Native C++ microkernel promotion lane

## Core question

Which probes are stable enough to promote from Python sketch to C++ high-volume sweep?

## Source anchors

- `SRC-0146` — Express Language Modeling (https://arxiv.org/abs/2606.10944)
- `SRC-0210` — Can LLMs Beat Classical Hyperparameter Optimization Algorithms? A Study on autoresearch (https://arxiv.org/abs/2603.24647)

## Cheap first run

Compile every experiments/*/*.cpp in temp dir; run smoke JSON; reject checked-in binaries.

## Metrics

- compiled probe count
- output JSON count
- audit pass/fail
- seconds per probe

## Required baselines

- Python probe where available
- source-only fallback
- audit failure mode

## Falsifier / stop condition

If native audit becomes brittle or slow, restrict C++ to selected kernels.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.
