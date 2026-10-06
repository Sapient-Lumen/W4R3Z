# ADR-0026: Policy is a pure function with stable traces (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
All DeriveBSD policy decisions are pure and deterministic: decision = f(policy_bundle, context_json).
Decisions emit a stable trace format with reason codes and obligations.

## Consequences
- reproducible decisions and audits
- allows multiple evaluators without fragmenting outputs
- aligns with LLM-centric tooling (lint/patch/validate loops)
