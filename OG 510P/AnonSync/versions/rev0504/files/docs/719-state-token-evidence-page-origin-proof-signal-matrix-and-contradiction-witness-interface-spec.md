# State token evidence page: origin proof, signal matrix, and contradiction witness interface spec

## Purpose

Provide proof adjacent to the claim:

> why does this visible state word mean what it means right now, and what evidence supports or contradicts that claim?

## Evidence classes

The page should classify evidence as one or more of:

- `origin assignment present`
- `policy matrix compiled`
- `runtime lane observation`
- `historical outcome observed`
- `contradiction detected`
- `wording only`
- `unknown`

## Required sections

### 1) Current state-token proof

Show:

- visible token
- origin
- evidence strength (`weak`, `moderate`, `strong`)
- whether the claim is policy-only or runtime-observed
- whether contradictions are currently known

### 2) Origin witness

Show what proves the origin:

- last manual action if any
- active scheduler rule if any
- inherited/runtime state source if any
- emergency overlay if any
- last state transition timestamp

### 3) Signal matrix witness

Show evidence for each lane:

- outbound-byte evidence
- inbound-byte evidence
- delete-propagation evidence
- indexing/discovery evidence
- whether evidence is compiled, observed, or unknown

### 4) Contradiction witness

When wording and matrix diverge, show a contradiction bundle:

- visible token text
- contradicting lane
- example observed behavior
- severity (`cosmetic`, `misleading`, `unsafe`)
- suggested wording repair

### 5) Observed outcomes

If historical evidence exists, show a compact ledger:

- timestamp
- token shown at time
- origin in force
- event type (`delete`, `upload`, `download`, `index advance`, `discovery`)
- outcome
- whether outcome surprised the visible token

## Required actions

- `Open state-token posture`
- `Review state-token change`
- `Export contradiction bundle`
- `Recompute matrix now`

## Data model

- `state_token_evidence_id`
- `scope_ref`
- `visible_token`
- `origin_kind`
- `evidence_strength`
- `origin_witness[]`
- `matrix_witness[]`
- `contradiction_witness[]`
- `observed_outcomes[]`
- `last_recomputed_at`

## Failure this page prevents

Without evidence, a product can keep saying `Paused` or `Protected` with high confidence even when runtime evidence shows the word is semantically unstable across origins.

AnonSync should require proof before it over-speaks about state words.
