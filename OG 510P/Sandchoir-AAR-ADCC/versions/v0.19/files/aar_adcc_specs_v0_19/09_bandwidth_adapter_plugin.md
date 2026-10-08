# 09 — Bandwidth Adapter Plugin (v0.19)

Purpose: adapt AAR/ADCC behavior to unknown slice counts and truncation patterns.

## Inputs
- telemetry: time_to_ctrl, truncation_rate, header_repair_rate
- WS churn: updates per cursor, evictions, compaction frequency
- collision metrics: lease violations, conflicting patches
- per-agent CAP# capabilities (optional)

## Outputs
- per-agent view budgets (section caps)
- section ordering nudges (always keep H0+MANDATORY first)
- enable/disable discovery/random slots
- trigger header-repair asks when parse fails
- suggest strictness changes (S0→S2) when needed

## v0 heuristics (default)
- if time_to_ctrl high or truncation high:
  - shrink budgets, disable random, reduce role items
- if parse failures high:
  - enable header-only repair, optionally enable header constraints if CAP# supports
- if collisions high:
  - suggest PatchOnly or harden leases
- if WS churn high without progress:
  - force compaction and promote fewer HOT items

## Evaluation proxies
- % slices with valid CTRL
- median time_to_ctrl
- WS size stability
- rate of selected patches leading to passing checks
- “value density”: new evidence cards per 100 lines of view
