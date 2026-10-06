# ADR-0046: MicroVM reason-code vocabulary is centrally registered

- Status: **accepted**
- Date: 2026-03-04

## Context

ADR-0045 established that microVM lifecycle receipts must include stable reason codes on non-success outcomes.
Without a single source of truth, reason codes drift quickly:

- different product shapes (A–D) invent different words for the same failure,
- fleet automation forks on message strings,
- and support bundles become non-deterministic.

We want a small, mechanical governance rule that keeps the vocabulary coherent without inventing a new subsystem.

## Decision

DeriveBSD maintains a single v0 registry for microVM receipt reason codes:

- `docs/456-microvm-receipt-reason-code-registry.md`

Rules:

- Any `reasons[].code` used by canonical example receipts MUST be present in the registry.
- Adding a new reason code requires updating the registry and adding an example that demonstrates it.

Enforcement:

- `tools/check_microvm_reason_code_registry.py` is wired into `python3 tools/hygiene.py`.

## Consequences

- The microVM “why” surface stays coherent across A–D without forks.
- Reviewers have a single place to evaluate whether a new reason code is warranted.
- CI catches silent drift in example vocabularies.

## Alternatives considered

- Allow ad-hoc codes without a registry.
  - Rejected: drift is guaranteed and the spec surface becomes unreviewable.

- Enumerate reason codes in JSON Schemas.
  - Deferred: too rigid for v0; prefer a doc registry + example enforcement first.
