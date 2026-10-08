# Cargo script workbench lane boundaries — 2026-03-22

Keep **P-0435** separate from these adjacent lanes.

## 1. Not generic workspace-boundary diagnosis

If the primary question is “which workspace am I in and why did parent manifests/configs affect me?”, that broader lane remains separate.

P-0435 owns **single-file-package discovery scope**, not every Cargo workspace-discovery problem.

## 2. Not build-dir consumer migration

If the primary question is “which tools depend on Cargo’s internal build-dir layout and how should they migrate?”, that belongs primarily to **P-0489**.

P-0435 may record cache residency, but it is not the general build-layout migration planner.

## 3. Not lock contention

If the primary question is “which actors blocked each other on shared roots or locks?”, that belongs primarily to **P-0490 Cargo Lock Contention Witness Kit**.

P-0435 owns where script cache/lock state lived, not a full contention diagnosis.

## 4. Not generic package-export tooling

If the primary question is massaging ordinary Cargo packages, templates, or scaffolds, that remains separate.

P-0435 owns **export lineage from a single-file package**, not general project generation.

## 5. Not script execution sandbox policy

If the primary question is what filesystem/network capabilities a script run should have, that belongs to compile-time or runtime sandbox lanes.

P-0435 owns script portability/support truth, not capability policy.
