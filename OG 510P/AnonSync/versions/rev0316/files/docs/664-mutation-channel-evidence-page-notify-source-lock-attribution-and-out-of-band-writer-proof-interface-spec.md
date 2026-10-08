# Mutation-channel evidence page — notify source, lock attribution, and out-of-band writer proof interface spec

## Purpose

This page explains how the product currently learns about changes and why mutation safety is or is not trustworthy on this seat.

It exists because `file changed`, `file locked`, and `sync delayed` are not root causes.
The operator needs one place that says whether the product is learning through notifications, rescans, manual repair, or unsafe competing writers.

## Core decision

Whenever a share/path pair is not on fully ordinary substrate, the system must render one first-class **Mutation-channel evidence** page.
It owns:

- actual mutation-discovery channels in play
- current lock evidence and retry basis
- evidence of out-of-band writers or protocol bypass
- strongest honest explanation for delay, churn, or corruption risk

## Page structure

1. evidence strip
2. discovery-channel list
3. lock and retry card
4. out-of-band writer card
5. evidence confidence and missing proof
6. linked reviews and receipts

### 1) Evidence strip

Show:

- share label
- path label
- current discovery mode: `notify`, `hybrid`, `rescan-only`, `manual`, `unknown`
- lock state: `none-visible`, `active-locks`, `repeating-locks`, `unknown`
- out-of-band writer risk: `none-seen`, `possible`, `likely`, `confirmed`, `unknown`

### 2) Discovery-channel list

For each active channel show:

- channel kind (`fs notification`, `scheduled scan`, `manual rescan`, `repair touch`, `other`)
- whether it is primary or fallback
- expected latency band
- known blind spots
- whether the operator can rely on it for ordinary freshness language

### 3) Lock and retry card

This card publishes:

- files or paths currently affected if known
- whether the locking process is attributable in-product or only externally investigable
- retry cadence and next retry time
- whether lock churn suggests app conflict rather than routine exclusive use
- whether delay tuning is currently masking edit-sync conflict

### 4) Out-of-band writer card

This card publishes:

- evidence that other applications or services mutate the same bytes outside the managed path contract
- whether those writers are observers, readers, or mutators
- whether protocol bypass creates rollback/corruption risk
- strongest safe statement about continuing local work on this topology

### 5) Evidence confidence and missing proof

Show:

- confidence class for notify evidence
- confidence class for lock evidence
- confidence class for out-of-band writer evidence
- what missing proof would let the product promote or demote the risk grade

### 6) Linked reviews and receipts

Link to:

- substrate posture
- latest substrate admission review
- latest substrate-risk receipt

## Public object

### `mutation_channel_evidence`

Fields:

- `mutation_channel_evidence_id`
- `share_ref`
- `path_ref`
- `primary_discovery_mode`
- `discovery_channels[]`
- `expected_latency_band`
- `lock_state`
- `lock_attribution_capability`
- `retry_policy`
- `out_of_band_writer_risk`
- `protocol_bypass_evidence[]`
- `confidence_summary`
- `strongest_safe_sentence`
- `stronger_forbidden_sentence`
- `issued_at`

## Honest outputs

The page may conclude:

- `Discovery mode: scheduled rescan every 10 minutes. Ordinary immediacy language is not supported on this seat.`
- `Lock attribution is external-only. The product can name affected paths but cannot name the locking process with current evidence.`
- `Mixed-writer risk is likely because the same bytes are reachable through SMB and direct local access on the host.`

It may not compress those truths into `sync delay`, `temporary lock`, or `network share`.
