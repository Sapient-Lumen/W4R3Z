# 80 — Experiment Runner + A/B Testing (MetaLLM-Friendly) (v0.19)

Your key unknown is slice behavior. The system must make experimentation *pleasant* for MetaLLM.

## 1) Goals
- Compare routing/prompt policies under real CLI constraints.
- Produce simple reports from telemetry (no manual log archaeology).
- Keep the main long-running thread safe.

## 2) Experiment object: EXP#
Fields:
- `name`
- `thread_base` (thread id + optional snapshot)
- `variants`: list of configs (budget/mode/explore/stop-after-CTRL/prompt pack)
- `duration`: rounds or time window
- `metrics`: telemetry fields to compare
- `acceptance`: thresholds (e.g., ctrl_parse_success >= 0.8)

## 3) Variants (examples)
- View budgets: line-only vs line+token guard
- Parser: drain-after-CTRL (K=10) vs stop-after-CTRL
- Exploration: off vs DISCOVERY-only vs DISCOVERY+RANDOM
- Bootstrap: CI vs EK
- Mode policy: Normal-only vs adaptive transitions (69_)

## 4) Execution model: forked threads (“time travel”)
- start from snapshot
- fork into variant threads
- run for N rounds
- collect metrics and produce an EXP report

## 5) Commands
- `exp create <EXP_JSON>`
- `exp run <EXP#>`
- `exp status <EXP#>`
- `exp report <EXP#> [--json]`
- `exp archive <EXP#>` (bundle logs+configs)

## 6) Report contents (per variant)
- ctrl_parse_success (p50/p90)
- time_to_ctrl (p50/p90)
- truncation rate
- repair rate
- evidence density (E#/cursor window)
- patch throughput (P# selected→applied)
- deadlock time
- top parse failure reasons (reason codes)
- suppression summary (“why items were hidden”)

## 7) MetaLLM playbook
- propose 1 experiment at a time
- keep variants to 2–3
- optimize CTRL capture and evidence density first
