# Incubation playbook

This file is a practical checklist for turning an “epic proposal” into a crate people actually adopt.

## 0) Pick a narrow 0.1

A 0.1 should:
- solve *one* user story end-to-end
- include a demo workspace (`fixtures/`) and a one-command reproduction
- include one “golden test” that prevents regressions

## 1) Define the contract surface

Write down:
- the public types and traits you plan to stabilize
- what you will not support (non-goals)
- what must remain configurable vs opinionated

Prefer: small core + optional adapters.

## 2) Design for maintenance

Before 0.1, decide:
- MSRV policy
- dependency budget (target count and “no heavy deps” list)
- governance (single maintainer? small team? succession plan?)
- security policy (how to report issues, how to triage)

## 3) Adoption plan

Answer:
- who is the first adopter (a real project)?
- what does migration look like from existing tools?
- what is the “default path” quickstart?

## 4) Evidence discipline

For each proposal, store:
- at least 2–3 links showing real demand
- an evidence snapshot (short excerpt + date) for the most important claim

## 5) Release checklist (0.1 → 1.0)

- Changelog discipline (keep a `CHANGELOG.md`)
- Semver + feature flags
- “How it fails” documentation (common errors and fixes)
- CI matrix and minimal conformance tests
- Benchmarks where performance is a selling point

## 6) When to stop

Sunset conditions:
- upstream or another crate fully solves the problem
- the ecosystem standardizes elsewhere
- maintenance costs exceed adoption value

Record sunsets in `meta/decision-log.md`.
