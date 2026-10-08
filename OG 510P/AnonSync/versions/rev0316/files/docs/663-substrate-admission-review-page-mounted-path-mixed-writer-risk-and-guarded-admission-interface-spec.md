# Substrate admission review page — mounted path, mixed-writer risk, and guarded admission interface spec

## Purpose

This review is shown whenever a share is about to be created, adopted, migrated, or resumed on a substrate whose storage class may materially narrow the promptness or safety contract.

The review exists because the product must decide more than `path accepted`.
It must decide whether the honest result is:

- ordinary admission
- guarded admission with degraded claims
- quarantined admission with limited actions
- blocked admission pending migration or topology change

## Triggers

Show this review before any commit that includes:

- binding a share to SMB, NFS, FUSE, or another mounted/networked substrate
- admitting a path where notifications are unavailable or disabled
- detecting likely mixed-writer topology
- restoring or rehoming a share onto removable or latency-heavy storage
- resuming a share after evidence of lock churn or repeated stale detection

## Fixed page order

1. candidate summary
2. substrate evidence
3. topology and mixed-writer review
4. admission verdict ladder
5. claim ceiling after admission
6. commit and receipts

### 1) Candidate summary

Show:

- share or candidate subject
- requested path
- detected substrate class
- why this review is required
- operator intent in plain language

### 2) Substrate evidence

Show:

- detection evidence for protocol/storage class
- whether filesystem notifications are expected, degraded, or absent
- whether delay/rescan tuning is already in force
- whether runtime locality is direct or mounted-through another service
- evidence quality: `strong`, `mixed`, `weak`, `unknown`

### 3) Topology and mixed-writer review

Show:

- expected writer set: `managed-only`, `managed-plus-observers`, `mixed-writer`, `unknown`
- whether other applications or services can mutate the same bytes outside the share protocol
- whether lock semantics are native, server-defined, or untrusted
- whether this topology is merely slower or actually unsafe

### 4) Admission verdict ladder

Offer only one of these winning verdicts:

- `ordinary-admit`
- `guarded-admit`
- `quarantine-admit`
- `block-until-migrated`
- `block-until-topology-cleaned`

For each verdict publish:

- why it is allowed or blocked
- what claim ceiling will attach after commit
- what stronger sentence is forbidden afterward

### 5) Claim ceiling after admission

Show:

- strongest safe connected sentence after commit
- strongest safe promptness sentence after commit
- whether lock diagnosis remains in-product or requires external evidence
- whether mixed-writer access must stop immediately
- whether later row language will show `degraded`, `guarded`, or `unsafe`

### 6) Commit and receipts

On commit emit:

- one substrate-risk receipt
- one claim-ceiling binding for the share row
- one follow-up remediation task if the verdict is not `ordinary-admit`

## Public object

### `substrate_admission_review`

Fields:

- `substrate_admission_review_id`
- `share_ref`
- `path_ref`
- `operator_intent`
- `substrate_class`
- `protocol_family`
- `detection_basis`
- `writer_topology`
- `lock_behavior_grade`
- `mixed_writer_risk_grade`
- `winning_verdict`
- `claim_ceiling`
- `required_remedies[]`
- `rejected_alternatives[]`
- `issued_at`

## Honest outputs

The review may conclude:

- `Guarded admit: mounted SMB path accepted for managed storage, but change discovery is rescan-based and ordinary promptness claims are forbidden.`
- `Block until topology cleaned: unmanaged SMB access and direct local mutation can both touch the same bytes, so corruption risk is above the admission floor.`
- `Quarantine admit: remote arrivals may continue, but local editing is held behind stronger warnings until substrate risk is reduced.`

It may not reduce the decision to `path selected`, `folder added`, or `share resumed`.
