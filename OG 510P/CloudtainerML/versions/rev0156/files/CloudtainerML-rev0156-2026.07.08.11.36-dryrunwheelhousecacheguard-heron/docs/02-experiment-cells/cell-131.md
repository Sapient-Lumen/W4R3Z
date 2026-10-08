# CELL-131 — Compression Role Taxonomy Pass v2

Priority: **P0**  
Status: **active-refactor**  
Idea: `IDEA-0130`  
Sources: SRC-0179, SRC-0180, SRC-0186, SRC-0187

## Cheap first run

Tag mechanisms by role: supervision, parametric prior, compactor, transition label.

## Metrics

- role coverage
- ambiguous roles
- priority changes

## Required baselines

- family-only grouping
- role-tag grouping

## Stop condition

If role tags do not affect priorities, delete them.
