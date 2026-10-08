# Convergence evidence bundle and disambiguation ladder interface spec

## Purpose

The archive now has:

- convergence windows for unresolved post-change gaps
- wait-vs-intervene decision sheets for choosing the next honest move
- causality explanation for why a visible subject/member cell exists
- future simulation for standing member-policy drafts

What still remained under-specified was the evidence-collection seam between `something is unresolved` and `I know which intervention is justified`.

That seam is where products quietly drift back into support folklore.
The operator opens three different docs, runs ad hoc checks, remembers half of a previous incident, maybe gathers logs, maybe toggles a mode, and later cannot prove which evidence really changed the recommendation.

This document defines the interface contract for one first-class **convergence evidence bundle** and one explicit **disambiguation ladder**.

## Core rule

Whenever a convergence window cannot be resolved from already-fresh public state and the strongest recommendation is not simply `wait`, the product must be able to render one explicit evidence bundle that:

1. states the live hypotheses for the unresolved gap
2. groups already-known evidence by family
3. marks missing or stale evidence separately from negative evidence
4. lists which bounded probes or inspections are allowed next
5. says what each probe could clarify and what it still could not prove

The surface is not a troubleshooting wizard.
It is a bounded evidence object.

## Why this needs its own spec

Current Resilio material is honest enough to be useful, but still distributed:

- sync timing is documented in one place
- peer connectivity, tracker failure, relay fallback, and slow-speed explanations are elsewhere
- missing-source and ghost-placeholder cases are elsewhere again
- deeper troubleshooting can spill into log collection or external network testing

That is workable documentation.
It is not the interface contract AnonSync wants.
AnonSync should compile these branches into one inspected evidence bundle before it recommends or records an intervention.

## Public objects

### Convergence evidence bundle

A durable evidence packet for one unresolved convergence window.

Suggested fields:

- `convergence_evidence_bundle_id`
- `convergence_window_ref`
- `member_ref`
- `subject_ref` nullable
- `current_hypothesis_order[]` (`announcement-gap`, `route-gap`, `source-gap`, `local-prerequisite-gap`, `policy-gap`, `supersession-gap`)
- `current_primary_uncertainty`
- `fresh_evidence_count`
- `stale_evidence_count`
- `missing_evidence_count`
- `recommended_probe_kind` nullable
- `recommended_probe_reason`
- `generated_at`

### Evidence family verdict row

One summarized evidence family and what it currently supports.

Suggested fields:

- `evidence_family_verdict_row_id`
- `family_kind` (`announcement`, `route`, `liveness`, `source-availability`, `local-prerequisite`, `policy-eligibility`, `supersession`, `resource-health`)
- `current_state` (`fresh-supporting`, `fresh-contradicting`, `stale-supporting`, `stale-contradicting`, `missing`)
- `summary`
- `supports_hypotheses[]`
- `weakens_hypotheses[]`
- `evidence_refs[]`

### Probe candidate row

One bounded next check the product may recommend.

Suggested fields:

- `probe_candidate_row_id`
- `probe_kind` (`refresh-announcement-state`, `refresh-member-liveness`, `refresh-route-view`, `refresh-source-availability`, `refresh-local-prerequisite-state`, `recompute-policy-eligibility`, `gather-resource-health`)
- `justification_state` (`recommended`, `allowed-but-secondary`, `blocked`, `unsafe-under-current-scope`)
- `clarifies_hypotheses[]`
- `does_not_prove[]`
- `expected_artifacts[]`
- `requires_review_boundary` bool

### Evidence packet export

An exportable packet for later review, escalation, or support without forcing raw log archaeology.

Suggested fields:

- `evidence_packet_export_id`
- `convergence_evidence_bundle_ref`
- `included_evidence_refs[]`
- `redactions[]`
- `created_at`
- `created_by`
- `evidence_hash`

## Fixed inspection order

Every convergence evidence bundle should preserve this order:

1. **Gap in view and live hypotheses**
2. **Fresh evidence already in hand**
3. **Missing or stale evidence**
4. **Disambiguation ladder**
5. **Allowed bounded probes**
6. **What probes still cannot prove**
7. **Export and follow-up boundary**

### 1) Gap in view and live hypotheses

This section should state plainly:

- which convergence window is being investigated
- what desired state is still unresolved
- which hypothesis is currently strongest
- which nearby hypotheses remain plausible

Example summaries:

- `primary uncertainty: route or liveness`
- `primary uncertainty: no eligible source currently online`
- `primary uncertainty: member saw publication, but local adoption state is stale`

### 2) Fresh evidence already in hand

This section should group evidence by family rather than time alone.
Examples:

- last fresh announcement receipt
- last member-liveness proof
- last viable route proof
- last source-availability witness
- last local-prerequisite observation
- current winning policy eligibility

### 3) Missing or stale evidence

This section is mandatory.
It must distinguish:

- evidence that never existed for this gap
- evidence that once existed but is now stale
- evidence that was attempted but produced a negative result

`Missing` and `negative` are not the same truth.

### 4) Disambiguation ladder

This section should show the order in which the system would clarify ambiguity.
Examples:

1. refresh member liveness
2. if live, refresh route view
3. if route viable, refresh source availability
4. if source available, refresh local prerequisite state
5. if all of the above are positive, reopen convergence classification

The ladder is not a hidden algorithm.
It is part of the reviewed interface contract.

### 5) Allowed bounded probes

Every probe row should say:

- why it is allowed now
- what hypothesis it would strengthen or weaken
- what artifact it would produce
- whether it changes only evidence state or could also mutate public state

The default expectation is evidence refresh, not hidden mutation.

### 6) What probes still cannot prove

This section prevents probe inflation.
Examples:

- route freshness does not prove byte settlement
- source availability does not prove member acceptance
- local prerequisite completion does not prove future policy eligibility
- a negative tracker result does not alone prove impossibility
- a slow-resource signal does not prove route failure

### 7) Export and follow-up boundary

Examples:

- `Export evidence packet`
- `Open intervention attempt sheet`
- `Recompute convergence verdict after probe`
- `Return to wait-vs-intervene decision`

## Public rules

### Rule 1 — missing evidence and negative evidence must stay separate

The product must not present `not checked yet`, `stale`, and `checked negative` as the same state.

### Rule 2 — one unresolved gap may have several live hypotheses

The product should still name one primary uncertainty, but it must preserve nearby plausible alternatives.

### Rule 3 — probes must be bounded and named

The operator must be able to see which evidence-gathering action is being proposed and what public artifacts it may emit.

### Rule 4 — evidence collection is not silent intervention

A bundle may recommend a probe, but it must not silently mutate member-wide defaults, publication scope, or path binding just to gather evidence.

### Rule 5 — export should prefer reviewed packets over raw archaeology

When the operator needs to escalate or preserve state, the primary surface should export a reviewed evidence packet before it falls back to raw logs or external ad hoc notes.

### Rule 6 — the bundle explains uncertainty, not eternal truth

A bundle is a snapshot of current ambiguity and evidence freshness.
Later probes or mutations may reorder the hypothesis ladder.

## Dense row contract

A dense evidence-bundle row should preserve these labels in this order:

- `Gap`
- `Primary uncertainty`
- `Fresh evidence`
- `Missing/stale`
- `Recommended probe`
- `Clarifies`
- `Still not proven`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one bundle:

- what unresolved gap is being investigated
- which explanation is currently strongest and which remain plausible
- what evidence is already fresh enough to rely on
- what evidence is merely missing or stale
- which probe is best next and why
- what that probe could still not prove
