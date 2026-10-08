# Effective arrival explanation and counterfactual interface spec

The archive already separates announcement from claim, claim from bind, standing approval memory from local claim, placement suggestion from committed bind, and standing seat templates from current share posture.
What still remained too easy to reconstruct from several places at once was the operator question that appears the moment a share arrives or reappears on one machine:

> why is this subject in *this* state on *this* machine right now, what exact standing memory or template influenced it, and what would have happened differently if one of those governing facts were narrower?

This document turns that question into one explicit interface contract.
It is the explanation companion to `58-policy-origin-defaults-and-precedence-spec.md`, the local-arrival companion to `95-announcement-inbox-and-local-claim-separation-spec.md`, the remembered-trust companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`, and the standing-template companion to `100-standing-arrival-template-and-default-root-review-interface-spec.md`.
For the mutation-time question `what will a standing-policy edit change later?`, see `102-policy-delta-preview-and-arrival-simulation-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a way that is useful for AnonSync design.
`Sync Private Identity & Linking My Devices`, `Sync functionality in detail`, `Folder Types and Management`, `Synchronization Modes`, and `How to manually set the location of the folders synced across linked devices?` together still describe later arrival behavior through a mixture of:

- linked-device automatic visibility of all folders
- prior approval memory and optional future linked-device auto-approval
- pending folders that can auto-connect after prior approval
- per-device synchronization mode (`Disconnected`, `Selective Sync`, `Synced`)
- default folder location / `Simple mode` placement behavior
- later `Connect` ritual for custom placement

That is real convenience.
It is not one operator-facing explanation surface.
The operator still has to reconstruct the answer to `why did this land this way here?` from several docs and several UI areas.

AnonSync should not accept that reconstruction burden.
Every arrived, matched, claimed, or bound subject should therefore expose one explicit explanation object that says:

- what stage this subject is in on this machine
- what standing memory or template influenced that stage
- which facts were merely explanatory versus actually acted upon
- what narrower or broader governing conditions would have changed
- which receipts later prove the local acts that really happened

## Core rule

Every local arrival-worthy subject should have a **why-here explanation**.
That explanation is not merely a log entry or a tooltip.
It is a stable projection over the public model that keeps six things adjacent:

1. current local stage
2. causal chain
3. governing standing state
4. explicit non-causes / untouched facts
5. counterfactual differences
6. next honest verbs

If the operator must jump between inbox rows, approval history, defaults pages, path review, and support text to answer those six questions, the interface is still too magical.

## Public objects

### Arrival explanation

A read object describing why one subject currently appears as announced, matched, claimed, unbound, placed, or bound on one seat.

Suggested fields:

- `arrival_explanation_id`
- `seat_ref`
- `subject_ref`
- `subject_kind` (`incoming-share`, `pending-folder`, `claimed-share`, `bound-share`, `re-entry`)
- `current_local_stage` (`announced`, `matched`, `claim-suggested`, `claimed-unbound`, `placement-reviewed`, `bound`, `hidden-local`, `blocked`)
- `causal_steps[]`
- `governing_refs[]`
- `counterfactuals[]`
- `next_actions[]`
- `receipt_refs[]`
- `computed_at`

### Causal step

One ordered statement in the explanation chain.
Each step should say what kind of fact it is and whether it changed local state or merely explained why lower-friction review was possible.

Suggested fields:

- `ordinal`
- `step_kind` (`announcement`, `approval-match`, `seat-template`, `policy-pin`, `claim`, `placement-suggestion`, `bind`, `materialization`, `manual-hide`, `blocker`)
- `effect_kind` (`explanatory-only`, `admitted-lower-friction`, `drafted`, `committed`, `prevented`, `unchanged`)
- `summary`
- `source_ref`
- `receipt_ref` nullable

### Counterfactual

A stable explanation of what would differ under one narrower or broader governing fact.
This exists so the operator can tell whether a remembered approval, template, or pin actually mattered.

Suggested fields:

- `counterfactual_id`
- `variant_kind` (`no-approval-memory`, `narrower-template`, `different-default-root`, `pinned-away`, `fresh-review-required`, `no-collision`, `seat-changed`)
- `predicted_stage`
- `predicted_next_action`
- `difference_summary`

## Fixed explanation order

Every full explanation surface should preserve the same sections in the same order:

1. **Subject and current stage**
2. **Why it is here now**
3. **Governing standing state**
4. **What did *not* happen**
5. **Counterfactuals**
6. **Next honest actions**
7. **Receipts and proofs**

### 1) Subject and current stage

This section should say:

- which seat we are talking about
- which subject we are talking about
- the current local stage
- whether bytes are announced only, claimed, bound, or materialized

The operator must be able to answer: **what is true right here, before explanation begins?**

### 2) Why it is here now

This section should render the causal chain in ordinary language.
For example:

```text
Announced from linked family scope
Matched prior approval memory for Maya (lower-friction only)
Seat template suggested claim under family-arrivals
No local claim was auto-applied
Suggested placement drafted /tank/family/Photos-2026
Bound path still pending review
```

The operator must be able to answer: **which facts actually caused this state and in what order?**

### 3) Governing standing state

This section should name the standing objects that influenced the current stage:

- approval memory or approval-match object
- seat template / default root
- pins or overrides
- scope and origin

The operator must be able to answer: **which standing policy or remembered trust influenced this subject?**

### 4) What did *not* happen

This section is mandatory.
It should explicitly name easy confusions that are false, for example:

- prior approval memory did **not** itself create a local bind
- seat template did **not** rewrite already bound sibling shares
- placement suggestion did **not** yet commit a path
- current arrival did **not** widen future approval memory

The operator must be able to answer: **what tempting but wrong story should I avoid?**

### 5) Counterfactuals

At least two counterfactuals should be available whenever standing memory or standing template materially influenced the stage.
Typical examples:

- `Without prior approval memory: this subject would be pending fresh review`
- `With announce-only seat template: this subject would remain announced with no claim suggestion`
- `With different default root: the drafted placement candidate would differ, but no bind would yet exist`

The operator must be able to answer: **which governing fact actually mattered, and how much?**

### 6) Next honest actions

This section should offer verbs that match the current stage and explanation truth, such as:

- `Open fresh approval review`
- `Claim here`
- `Open placement review`
- `Keep announced only`
- `Hide on this machine`
- `Inspect governing template`
- `Inspect approval memory`

It must not flatten unlike stages into one generic verb such as `Connect`, `Open`, or `Continue`.

### 7) Receipts and proofs

This section should link to the durable artifacts that prove any actual local act:

- approval receipt or approval-match receipt
- claim receipt
- placement receipt
- bind or policy receipt

A pure explanation with no local mutation may have no new receipt of its own, but it should still say which existing receipts support the chain.

## Row and card contract

A compact row should keep these facts adjacent, in this order:

1. subject
2. current local stage
3. strongest governing explanation
4. strongest non-cause / untouched fact
5. next honest action

Example:

```text
Photos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain
```

Opening the row should show a drawer with the fixed explanation order above.

## Dense/mobile rule

Dense and mobile clients may compress the prose, but they must still preserve:

- current local stage
- strongest governing cause
- one explicit non-cause
- one counterfactual entry point
- the next honest verb

A dense client may shorten `Without approval memory this would wait for fresh review` to `No memory => fresh review`, but it may not omit the counterfactual concept entirely.

## CLI contract

Minimal commands:

```text
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas --json
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas --counterfactual no-approval-memory
anonsync arrival trace --subject incoming:photos-2026 --seat home-nas
anonsync arrival receipts --subject incoming:photos-2026 --seat home-nas
```

The plain-text rendering should answer, without cross-referencing other pages:

- why the subject is visible here now
- whether remembered trust merely lowered friction or actually changed local state
- whether standing template only drafted placement or already committed a bind
- what one narrower governing fact would have changed
- which receipt proves any real local mutation

## Design tests

The model is not good enough if any of the following remains true:

- the operator still has to remember which settings page or support article explains why this arrival auto-connected, stayed pending, or drafted a path
- the surface still lets prior approval memory masquerade as a local bind
- the surface still lets a drafted default root masquerade as a committed path
- counterfactuals are unavailable, so the operator cannot tell whether standing memory or standing template actually mattered
- the next action is still a generic `Connect` or `Open` that hides whether the subject is announced, claimed, or bind-ready

## Why this matters

A mature AnonSync surface should let the operator move from `why is this here?` to `which prior trust or template influenced it?` to `what would have been different under a narrower policy?` without leaving the public model.
That is the explanation standard this document locks in.
