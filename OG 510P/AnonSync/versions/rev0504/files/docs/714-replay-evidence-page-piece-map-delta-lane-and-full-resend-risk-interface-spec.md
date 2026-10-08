# Replay evidence page: piece map, delta lane, and full-resend risk interface spec

## Purpose

Provide proof adjacent to the claim:

> why is this subject using this replay class right now, and what evidence supports the claim that the next mutation will replay cheaply or expensively?

## Evidence classes

The page should classify evidence as one or more of:

- `policy only`
- `hash dataset present`
- `piece map present`
- `rolling / diff lane available`
- `full-resend forced by class`
- `shift-risk inferred from edit shape`
- `observed replay outcome`
- `unknown`

## Required sections

### 1) Current replay proof

Show:

- current replay class
- evidence strength (`weak`, `moderate`, `strong`)
- whether the claim is predictive or observed
- last observed replay outcome if available

### 2) Hash and map availability

Show what proof material actually exists:

- file hash present yes/no
- block/piece hashes present yes/no
- retained between runs yes/no
- owner-only availability yes/no
- evidence tied to current absolute path yes/no

### 3) Delta lane health

Show whether the stronger lane is usable now:

- rolling checksum lane active / inactive / unavailable
- diff-delta lane active / inactive / unavailable
- disabled by policy / edition / seat / substrate
- notes about why the lane is unavailable

### 4) Full-resend risk explanation

Explain the strongest current reason full resend may still happen:

- edit likely shifts many later offsets
- hashes unavailable
- policy intentionally prefers resend
- current class does not support stronger delta
- evidence insufficient

### 5) Observed outcomes

If historical evidence exists, show a compact ledger:

- timestamp
- edit-shape summary
- replay class actually used
- bytes rechecked locally
- bytes replayed over network
- whether whole resend occurred

## Required actions

- `Open replay posture`
- `Review replay cost change`
- `Export replay evidence`
- `Recompute evidence now`

## Data model

- `replay_evidence_id`
- `subject_id`
- `current_replay_class`
- `evidence_strength`
- `policy_basis[]`
- `file_hash_present`
- `piece_hashes_present`
- `retained_hash_dataset_present`
- `owner_only_hash_dependence`
- `path_binding_status`
- `delta_lane_status`
- `full_resend_risk_reason[]`
- `observed_outcomes[]`
- `last_recomputed_at`

## Failure this page prevents

Without evidence, a product can say `incremental replay active` even when the current seat only has policy rhetoric and no surviving piece/hash evidence to support that claim.

AnonSync should require proof before it over-speaks about changed-part replay.
