# FT-0084 closure — rev0085

FT-0084 asked whether aggregate correction-authority lifecycle events should be rolled up across periods and compatible operators, including contestation resolution and emergency-withdrawal notification resynchronization, without exposing parties, incidents, authority identities, notification recipients, or provenance.

rev0085 closes the ticket with four changes.

## 1. Executable lifecycle decision table

Added:

```text
schema/aggregate-lifecycle-decision-table.schema.json
tests/aggregate-lifecycle-decision-table.yaml
```

The table defines the closed rev0085 decision vocabulary and required rows for active, pending-rotation, expired, revoked, emergency-withdrawal, contested, and unknown/redacted lifecycle states.

Lifecycle-bearing correction-authority references now require:

```text
decision_table_digest
current_interpretation_decision
```

The validator derives the expected decision from the lifecycle posture and rejects mismatches.

## 2. Emergency-withdrawal resynchronization

Emergency withdrawal now carries `resynchronization_state`. Concrete emergency withdrawal requires digest-bound withdrawal and resynchronization policy references. The summary can expose aggregate state and count buckets, but not notification recipients, delivery channels, response plans, incident forensics, or exact incident timing.

## 3. Contestation-resolution rollup

Contestation state is now closed by digest requirements. Any non-empty contestation state requires `contestation_digest`, including resolved-upheld contestation. Pending, overturned, and unknown contestation suppress current interpretation.

## 4. Lifecycle portability aggregation

Aggregate lifecycle rollups now include a portability aggregation surface. Portable compatible-operator interpretation requires a profile compatibility statement digest. Portability failure cannot coexist with current-supported rollup decisions.

## Preserved boundary

The rev0085 closure does not add an authority registry, revocation service, notification system, emergency-response workflow, transparency log, privacy accountant, legal-process system, or provenance graph. It constrains aggregate correction interpretation only.
