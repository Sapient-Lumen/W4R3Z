# Remedy-hardening-attestation successor preview/commit binding review page — is this still the same run we reviewed, and may it execute now?

## Purpose

This page is the operator review surface for the last moment before execution.
It exists so the product can answer whether the reviewed picture is still the live picture, or whether a quiet but material change has already pushed the run outside its reviewed basis.

## Questions this page must force

### 1. Snapshot identity

- What exact snapshot did we review?
- Which surfaces and assumptions did that snapshot include?
- Was the preview merely informative, or already bound as a commit candidate?

### 2. Freshness

- Is the snapshot still inside its validity window?
- Did a restart, rescan, reconnect, settings save, approval reuse, or linked-device auto-arrival happen after preview?
- If yes, were those changes modeled as harmless or as invalidators?

### 3. Same-run test

- Are we still targeting the same beneficiaries, same objects, same permissions, same admissions, and same runtime world?
- Did any hidden convenience behavior widen the touched-set since preview?
- Has any background process made the world no longer identical to the reviewed one?

### 4. Execute-if-unchanged gate

- Which mandatory drift checks passed immediately before commit?
- Which checks are stale, missing, or observer-weak?
- If the run cannot prove sameness, is refresh enough, or is full re-review mandatory?

### 5. Sentence discipline

- What is the strongest honest sentence now?
- Which stronger `no surprise` sentence remains blocked?
- What exactly must happen before that stronger sentence becomes safe?

## Required layout

### Header

Show:

- action name
- reviewed snapshot id
- commit token state
- same-run verdict
- current strongest safe sentence

### Left column — snapshot versus now

Show a compact comparison of:

- reviewed touched-set
- live touched-set estimate
- reviewed approvals and admissions
- current approvals and admissions
- reviewed runtime world
- current runtime world

### Right column — drift analysis

Show:

- invalidators that stayed absent
- invalidators that fired
- unresolved ambiguities
- whether refresh is enough
- whether full re-review is mandatory

### Footer decision rail

The footer must expose:

- execute now / refresh preview / re-review required
- commit token valid / invalid / expired
- strongest honest sentence now
- strongest blocked stronger sentence now

## Prohibited shortcuts

The review must reject reasoning like:

- `the plan did not change, so the run is the same`
- `nobody complained, so the preview is still fresh`
- `the UI looks calm, so no drift matters`
- `the action is urgent, so snapshot expiry can be ignored`
- `pause kept things still enough`

## Strong-sentence discipline

The page must block stronger sentences such as:

- this run is exactly what was reviewed
- nothing material changed since preview
- commit is safe without refreshing
- execute-if-unchanged is satisfied
- no-surprise execution is guaranteed

unless the supporting freshness and drift-check fields are actually present.
