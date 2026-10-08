# Member policy card and future-arrival-default review interface spec

## Purpose

The archive now has:

- reviewed per-subject publication
- living subject × member publication matrix truth
- role-first arrival/adoption review
- delta previews for publication-affecting edits

What still remained too easy to hide was the operator question that sits one level above all of those:

> for this one member, what future-arrival defaults actually exist, what root/path hints do they carry, what kinds of arrivals may stage automatically, what is only a suggestion, and what exceptions already bend that default story?

If the answer still lives in one compressed mode label, one settings panel, or remembered lore, the product has not really escaped the Resilio seam.

This document defines the member policy card and review surfaces required to keep future-arrival defaults public without confusing them with current publication truth.

## Core rule

Every member must have one explicit **member policy card** whose future-arrival defaults are inspectable separately from current subject/member cell truth.

The member policy card is not the publication matrix and is not the arrival role sheet.
It explains the member's **default future posture**, not its currently claimed per-subject state.

Every member policy surface must keep seven truths adjacent:

1. who this member is and what class it belongs to
2. what future arrivals this member is eligible to receive by default
3. what arrival posture those future subjects take by default
4. what default root or path hints exist and whether they are only suggestions
5. what exceptions or overrides already diverge from the default
6. what changing the default would and would not rewrite now
7. what receipt proves the member policy currently in force

## Why this needs its own spec

Current Resilio docs still describe linked-device synchronization modes and default folder locations as the main answer for how future arrivals land on one member.
That is concise, but it compresses too much meaning:

- future-visibility eligibility
- staging posture
- byte posture
- default placement
- remembered exceptions

AnonSync should refuse that compression.
The operator should be able to open one member card and answer the future-default question directly, without confusing it with the member's current claimed role on any one subject.

## Public objects

### Member policy card

A read projection over one member's future-arrival defaults and related exception lineage.

Suggested fields:

- `member_policy_card_id`
- `member_ref`
- `member_class`
- `relationship_summary`
- `future_arrival_default_ref`
- `default_root_refs[]`
- `exception_refs[]`
- `current_publication_counts`
- `latest_receipt_ref`
- `generated_at`

### Future-arrival default

A reviewed object describing the member's default posture for future eligible arrivals.

Suggested fields:

- `future_arrival_default_id`
- `member_ref`
- `eligibility_scope`
- `arrival_posture` (`announce-only`, `claim-review-required`, `staged-placeholders`, `metadata-only`, `encrypted-store`, `do-not-stage`)
- `default_root_hint_ref` nullable
- `materialization_hint_ref` nullable
- `auto_stage_policy`
- `non_effect_summary`
- `receipt_refs[]`

### Member policy review

A reviewed object for changing one member's defaults.

Suggested fields:

- `member_policy_review_id`
- `member_ref`
- `current_default_ref`
- `requested_default_ref`
- `exception_findings[]`
- `requires_delta_preview` boolean
- `effect_summary`
- `non_effect_summary`
- `receipt_promise`

## Fixed inspection order

Every member policy surface should preserve the same order:

1. **Member identity and relationship**
2. **Current publication state summary**
3. **Future-arrival defaults**
4. **Default roots and path hints**
5. **Exceptions and override lineage**
6. **What changing the default does not rewrite now**
7. **Receipt and latest policy change**

### 1) Member identity and relationship

This section should say:

- which member is in scope
- what class it belongs to
- what relationship or trust family it is part of
- whether this member is eligible for publication at all

### 2) Current publication state summary

The card may summarize current state, for example:

- `12 subjects published here`
- `4 locally claimed`
- `2 encrypted-only`

But it must keep that summary visually separate from future defaults.

### 3) Future-arrival defaults

This section should answer:

- what newly eligible subjects do by default on this member
- whether they stage only, require claim, land as metadata only, or stay encrypted-only
- whether the default is broad, narrow, or intentionally empty

### 4) Default roots and path hints

This section should state:

- which default root or root family is suggested
- whether it is only a hint
- whether different subject classes map to different roots
- whether path choice still remains local later

### 5) Exceptions and override lineage

This section should list:

- subjects that diverge from the member default
- template-driven exceptions
- direct overrides
- withdrawn exceptions

### 6) What changing the default does not rewrite now

This section should aggressively publish non-effects.
Examples:

- changing the default root does not move already claimed subjects
- changing future staging does not promote existing observer cells to writer
- changing eligibility does not silently withdraw already published subjects unless explicitly reviewed elsewhere
- changing the default does not erase per-subject overrides

### 7) Receipt and latest policy change

This section should link to the latest receipt and, when relevant, open the delta preview required before the policy change was applied.

## Action ordering rules

### Rule 1 — no compressed mode labels as the only explanation

`Laptop default: selective` or `NAS default: synced` is not an adequate member policy surface.
The card must unpack what that means in terms of eligibility, staging, roots, and non-effects.

### Rule 2 — current truth and future defaults must stay visually distinct

Do not let badges, colors, or rows imply that current published/claimed state is the same thing as future-arrival default posture.

### Rule 3 — changing a member default may require delta preview

If the requested default change would alter existing subject/member cells, the flow must open the publication-delta preview before apply.

### Rule 4 — default roots are hints unless a later bind says otherwise

A default root or root family must not masquerade as a current path bind for any one subject.

### Rule 5 — exception lineage remains inspectable

A member card should let the operator answer whether current divergence comes from a template, a direct override, a withdrawal, or a local adoption choice.

## Dense card contract

A dense member card should preserve these labels in this order:

- `Member`
- `Current published here`
- `Future default`
- `Default root`
- `Exceptions`
- `Latest receipt`

## Acceptance test

The member policy card is good enough when a cautious operator can answer all of the following from one surface:

- what this member is eligible to receive by default in the future
- how those future arrivals stage or do not stage
- what root/path hints exist and whether they are only hints
- how many current subjects already diverge from the default
- what changing the default would not rewrite now
- what receipt proves the current member policy in force
