# 46 — Aggregate correction authority and notification boundary

rev0083 closes FT-0082 by adding a compact correction-authority reference to aggregate revision lineage.

The reference exists because rev0082 could say that an aggregate verifier audit summary was corrected, withdrawn, superseded, or reconciled, but it could not say whether that publication change was authorized, whether recipients were notified within policy, or whether a compatible operator may safely interpret the correction chain.

## Placement

The field is required inside:

```text
aggregate_summary.aggregate_revision_lineage.correction_authority_reference
```

It is intentionally placed under aggregate revision lineage, not under TimeState, profile assessment, evidence summary, replay receipt, or transparency trust policy.

## Required surfaces

`correction_authority_reference` contains three bounded surfaces.

### `authority_binding`

This names only a digest-bound authority posture:

- authority role,
- authorization status,
- authorization basis,
- authority digest,
- authorization check time,
- optional authorization-policy digest.

It does not export authority rosters, key material, repository topology, credential chains, or legal process details.

### `notification_cadence`

This summarizes whether correction, withdrawal, supersession, or reconciliation notification is current enough for aggregate interpretation:

- notification state,
- notification scope,
- issued time,
- last notification time,
- maximum notification delay,
- staleness effect,
- optional notification-batch digest.

It does not export recipient rosters, recipient identities, delivery-channel details, notification payloads, or external notification records as TimeSync provenance.

### `portability_boundary`

This states whether a correction chain is local-only or digest-bound portable to compatible operators:

- same-operator or compatible-operator scope,
- authority equivalence posture,
- correction-chain portability state,
- optional compatibility-statement digest,
- optional portable correction-chain digest.

Compatible-operator portability requires digest-bound equivalent-or-stricter authority equivalence. A portable correction chain cannot be inferred from a shared label, alias, notification, or repository reference.

## Non-upgrade rule

A correction-authority reference can constrain aggregate publication interpretation only. It cannot:

- update TimeState,
- update profile conformance,
- update current actionability,
- satisfy profile obligations,
- upgrade individual replay visibility,
- rewrite prior aggregate publications,
- export suppressed deltas,
- identify verifiers or notification recipients,
- become TimeSync provenance.

## Failure semantics

A stale, failed, unknown, or unchecked notification cannot support current aggregate interpretation.

An unauthorized or unknown correction authority cannot support corrected, withdrawn, superseded, or reconciled aggregate lineage.

Compatible-operator correction-chain interpretation requires all of:

- compatible-operator digest-bound portability scope,
- digest-bound equivalent-or-stricter authority equivalence,
- profile compatibility-statement digest,
- portable correction-chain digest.

## Discovery

`aggregate_correction_authority_reference` may be returned through discovery as a nested object. Discovery-returned references are schema-validated and semantically checked with the same non-upgrade and non-leakage rules.

## Evidence class

`aggregate_correction_authority_summary` is a non-satisfying evidence class. It may appear in evidence summaries as review context, but cannot be used for `profile_obligation` or to mark an obligation as met.
