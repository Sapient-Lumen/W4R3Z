# Case lineage receipt page: cause status, residual risk, and blocked stronger sentences interface spec

## Purpose

The archive already had receipts for interventions and remediation runs.
It still needed the durable handoff artifact for the case itself.

## Core decision

AnonSync must emit one **Case lineage receipt** whenever a case changes closure class, is handed off, is merged, is reopened, or exits a watch window.

## Required receipt fields

### Header

- `case_id`
- receipt time
- owner at issuance
- predecessor / successor receipt ids
- linked case ids if merged or split

### Case truth

- symptom cluster summary
- current favored cause
- cause-status class
- closure class
- confidence floor
- unresolved hypotheses count

Supported `cause-status class` values:

- `no-single-cause-established`
- `best-current-explanation`
- `supported-primary-cause`
- `combined-cause`
- `environmental-likely`
- `state-corruption-likely`
- `identity-corruption-likely`
- `topology-likely`
- `external-awaiting-proof`

### Risk and reopen truth

- residual risk summary
- reopen triggers
- reopen sensitivity
- watch status
- next review time

### Blocked stronger sentences

The receipt must list at least:

- one strongest sentence that is safe now
- one stronger sentence still blocked
- why the stronger sentence is blocked

### Handoff truth

- next allowed action
- next forbidden action
- evidence that would most efficiently change the case
- whether support / forum / external follow-up is still pending

## Mandatory rules

- A reopened case must cite the receipt it invalidated.
- A merged case must preserve both predecessor cause postures in the receipt lineage.
- A receipt may not round `unknown but stable` upward into `resolved`.
- Residual risk must survive into the receipt even when the watch window is quiet.

## Why this page exists

The operator who receives the handoff should inherit the strongest honest sentence, not the most optimistic memory.
