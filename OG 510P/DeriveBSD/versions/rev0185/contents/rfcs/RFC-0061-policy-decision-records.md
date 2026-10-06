# RFC-0061: Policy decision records

Status: Draft

## Summary

Introduce a **policy decision record** produced during Lock → Plan.
Its digest is included in the Plan digest so artifacts can prove *which policy allowed them*.

## Motivation

DeriveBSD promises **policy-governed** derivations and runtime launches.
Without an explicit, hashable record, policy can become an implicit side-channel:
- external datasets (vulnerability intel, allowlists) can silently change outcomes
- runtime constraints can be enforced inconsistently across implementations

A decision record makes policy:
- **auditable** (what was decided)
- **replayable** (why it was decided)
- **enforceable** (effective constraints are explicit)

## Proposal

Add a canonical JSON object:
- kind: `policy-decision`
- versioned schema (v0.1)
- JCS-canonicalized before hashing
- stored as a store object; referenced by digest

The record contains:
- policy engine identity (name/version + optional digest)
- input digests for policy-relevant datasets
- allow/deny + effective constraints
- stable decision trace

See: `docs/93-policy-decision-records.md` and `spec/policy.decision.schema.json`.

## Signing

Policy MAY require a signature over the record digest by a policy authority key.
Builder signatures are optional and not sufficient alone.

## Non-goals

- standardizing a single policy language
- encoding full evaluator semantics in the decision record

## Open questions

- Should decision records be wrapped in DSSE envelopes by default?
- How do we represent time-bounded inputs (expiry/epoch) without forcing wall-clock non-determinism?

