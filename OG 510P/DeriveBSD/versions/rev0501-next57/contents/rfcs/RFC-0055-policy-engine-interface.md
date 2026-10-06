# RFC-0055: Policy engine interface + traces

- Status: draft
- Created: 2026-02-23

## Summary
Define the stable policy evaluation interface: context JSON in → decision + obligations + trace out (all JCS-hashable).

## Goals
- deterministic results
- stable reason codes
- minimal, LLM-friendly traces
- multi-backend evaluators (matchers, Cedar, OPA) without changing the contract

## References
- OPA/Rego docs
- Cedar docs
