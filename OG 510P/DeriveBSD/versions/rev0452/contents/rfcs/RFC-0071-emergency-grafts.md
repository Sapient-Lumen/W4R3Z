# RFC-0071: Emergency patch mode (“grafts”, but auditable)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Define an explicit, time-bounded “emergency patch” mechanism that can deliver critical fixes quickly while preserving explainability and policy governance.

## Motivation

Functional package systems occasionally need a fast path for security updates.
Guix implements “grafts” to reduce rebuild work for urgent fixes.

DeriveBSD should support an equivalent only if it is:
- explicit
- policy-controlled
- auditable
- reversible

## Goals / Non-goals

Goals:
- emergency patch produces a new Plan + closure proof
- introduce an Override Record that explains the exception
- make it easy for policy to forbid by default

Non-goals:
- silently mutating a deployed generation

## Proposal

### Override record

A structured object that:
- identifies target (package/artifact)
- identifies replacement digest(s)
- cites CVE/OSV/incident id
- has expiry and revocation fields
- is signed by an “emergency approver” key class

The override record digest is included in Plan identity.

### Activation

Activation must:
- emit a blast-radius diff
- emit an explainability bundle that includes the override record

## Alternatives considered

- “just rebuild everything” always (often too slow)
- allow ad-hoc overrides outside the pipeline (breaks explainability)

## Backwards compatibility

Additive; existing flows unchanged.

## Security considerations

- require additional approvals (two-person integrity)
- require short expiry and transparency log submission (optional)

## Open questions

- how to represent override records in Lock vs Plan
- policy defaults for expiry and allowed targets
