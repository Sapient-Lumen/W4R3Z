# Operator attestation contract sheet page: assertion class, evidence basis, blast radius, and expiry interface spec

## Purpose

The archive already has warning pages, repair reviews, chronology proofs, and destructive-action reviews.
What it still lacked was one ordinary page for the narrower question:

> what exactly is the operator asserting here because product proof is incomplete, what evidence supports that assertion, how dangerous is it if wrong, and when does that assertion expire?

Current official Resilio docs make this seam concrete.
They still tell the operator to ignore certain warnings, proceed through non-empty-folder cases, touch files if the local version is believed to be newest, and recreate a sync instance after privately checking Archive.
That is useful truth.
It should not remain informal prose.

## Core decision

AnonSync must expose one first-class **Operator attestation contract sheet** whenever an operator assertion is materially changing what the product is allowed to do or say.

The sheet exists to answer six things in one place:

1. what assertion class is being made
2. what evidence basis supports it
3. which machine proof is still missing
4. what blast radius follows if the assertion is wrong
5. when the attestation expires
6. what stronger sentence remains blocked even if the attestation is accepted

## Fixed page order

1. **Assertion header**
2. **Evidence basis card**
3. **Missing machine proof card**
4. **Blast-radius card**
5. **Expiry and reopen triggers**
6. **Commit rail and blocked stronger sentence**

### 1) Assertion header

Show at minimum:

- `operator_attestation_id`
- actor handle
- assertion class
- scope (`single-file`, `subtree`, `subject`, `repair-rung`, `runtime`, `unknown`)
- strongest safe sentence
- stronger blocked sentence
- attestation freshness

Supported assertion classes must include:

- `warning-is-no-longer-actionable`
- `local-copy-is-newest`
- `non-empty-target-is-intended-same-tree`
- `archive-reviewed-nothing-critical-remains`
- `destructive-recreate-is-acceptable`
- `other-reviewed-human-assertion`

Example safe sentence:

- `Proceeding on operator attestation that this non-empty target is the previously bound tree, not a fresh merge target.`

### 2) Evidence basis card

Show evidence rows grouped by class:

- local observations reviewed
- peer observations reviewed
- archive/history reviewed
- path-lineage reviewed
- chronology reviewed
- file-presence reviewed
- unsupported / private memory only

Each row must show:

- evidence source
- freshness
- corroboration grade
- whether it is machine-observed or human-only
- whether it supports or weakens the attestation

The operator must be able to answer:

> what did I actually look at before asserting this?

### 3) Missing machine proof card

Show which stronger proof is absent, for example:

- no live corroboration from all peers
- no authoritative chronology winner proof
- no complete Archive / history scan proof
- no preserved path-lineage proof
- no byte-equivalence proof across trees
- no runtime witness for safe recreate

The product must say plainly when it is accepting an attestation because world proof is incomplete, not because the stronger proof does not matter.

### 4) Blast-radius card

Separate these consequences explicitly:

- visibility-only change
- warning-suppression change
- chronology reannouncement risk
- overwrite / delete risk
- successor-epoch creation risk
- peer-wide convergence risk
- irreversible residue loss risk

Each row must show worst-case if wrong, expected survivor classes, and whether rollback remains possible.

### 5) Expiry and reopen triggers

Every attestation must publish its expiry basis.
Possible reopen triggers include:

- offline peer returns
- rescan discovers new contradiction
- Archive / history view changes
- path identity no longer matches
- new clock / chronology evidence appears
- subject recreated or rebound
- new operator / seat reopens the same object

The operator must be able to answer:

> when will this attestation stop being trustworthy?

### 6) Commit rail and blocked stronger sentence

Only actions that match the attestation may appear, such as:

- `Accept visibility-only ignore`
- `Proceed with same-tree reconnect`
- `Republish using reviewed local-newest attestation`
- `Commit destructive recreate after archive review`
- `Decline attestation and reopen investigation`
- `Emit attestation receipt`

The rail must also show the strongest forbidden statement, for example:

- `All peers agree this file is gone.`
- `This recreate preserved continuity.`
- `This non-empty target is definitely byte-identical.`
- `No more recent version can still surface.`

## Public object

### Operator attestation contract sheet

Fields:

- `operator_attestation_id`
- `assertion_class`
- `scope_ref`
- `actor_ref`
- `evidence_rows[]`
- `missing_machine_proof_rows[]`
- `blast_radius_rows[]`
- `expiry_rows[]`
- `allowed_actions[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. assertion
2. evidence basis
3. missing proof
4. blast radius
5. expiry basis
6. strongest next action

Example:

```text
local-copy-is-newest     local mtime plus manual file inspection only     no corroboration from offline peer     republish may overwrite later-returning winner     expires if any absent peer returns or chronology evidence changes     Emit attestation receipt before republish
```

## Rules

### Rule 1 — the product must name the human assertion explicitly

Never hide a human-supplied truth inside a generic `Proceed`, `Ignore`, or `Retry` button.

### Rule 2 — visibility change and world change must stay separate

Muting a warning is not the same thing as proving the world condition is gone.

### Rule 3 — destructive attestation must carry expiry and residue duty

A human claim that `nothing important remains` must always publish what was reviewed, what was not reviewed, and what will be irretrievable if wrong.

### Rule 4 — accepting an attestation does not upgrade blocked machine proof

The UI may proceed on a reviewed assertion.
It may not silently upgrade that to universal proof.
