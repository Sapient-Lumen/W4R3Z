# 36 — Verifier Economics + Default Registry (v0.19)

You said it cleanly: **votes win, evidence moves votes**. Verifiers are how evidence becomes cheap, legible, and repeatable.

This doc defines the “economics layer”:
- what checks exist
- what they cost
- when the router/MetaLLM should suggest them
- how to keep raw logs out of WS

## 1) Evidence is a product (priced, cached, and scoped)
A verifier run should emit an E# Evidence Card:
- `kind`: test|build|lint|proof|repro|bench
- `result`: pass|fail|flaky|unknown
- `signal`: 1–5 lines (the punchline)
- `repro`: verifier name + args (not raw command unless whitelisted)
- `scope`: what it supports/refutes (C#/P#/CE#)

All long logs go to Ledger. WS only gets the punchline + pointers.

## 2) The default cost model
We use **cost classes**, not times (time varies across machines).

- Cheap: <= 2s typical (lint, format, typecheck-lite, tiny unit subset)
- Medium: 2–30s typical (full unit suite, targeted integration)
- Expensive: 30s+ (full integration, benchmarks, proof searches)

Router budgets should assume:
- you can run cheap checks frequently
- medium checks occasionally
- expensive checks rarely and only when they decide something

## 3) Default verifier registry (suggested starter set)
V0 registry (names are placeholders; you’ll tailor them):

Cheap:
- `fmt_check`
- `lint_fast`
- `typecheck_fast`
- `unit_fast` (subset / smoke)
- `build_fast` (compile only)

Medium:
- `unit_full`
- `integration_targeted` (tagged)
- `property_small` (few seeds)
- `doc_tests`

Expensive:
- `integration_full`
- `bench_smoke`
- `property_heavy`
- `proof_search` (if you have it)

## 4) When the router should suggest checks (policy)
Router/MetaLLM should suggest a verifier when:
- a patch is selected (run cheap checks immediately)
- a CE is proposed (run the minimal repro to certify)
- agents disagree on a claim that can be tested (run the discriminative check)
- deadlock occurs without new evidence (force “checks vote”)

## 5) Voting tie-in (keep it tiny)
Agents vote:
- `checks{unit_fast=3,typecheck_fast=2}`
Router converts tally → queue of verifier runs under a cost budget.

## 6) Caching
Each verifier should define a cache key:
- commit hash (or workspace snapshot id) + verifier name + args + env tag
If cache hits: emit E# with “cached=true” and avoid reruns.

## 7) Anti-spaghetti rule
A verifier must be:
- deterministic enough to move votes
- bounded in output
- described in one short line in views

If it can’t meet this, it belongs in Ledger-only ad-hoc execution, not in the registry.

Counterexamples become decisive only when replayable; see 65_counterexample_certification_playbook.md.
