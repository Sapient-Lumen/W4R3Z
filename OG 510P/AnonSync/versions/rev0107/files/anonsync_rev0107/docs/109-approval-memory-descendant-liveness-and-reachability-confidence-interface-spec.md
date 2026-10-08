# Approval-memory descendant liveness and reachability-confidence interface spec

## Purpose

The archive already separates first approval from later matches, freshness, lineage, authorization trace, and family rebase after constellation mutation.
One gap still remained:

> after trust family membership is explained, the operator still needs one truthful answer to **which descendants are currently alive, recently witnessed, byte-capable, hidden-only, stale-unseen, or historical only, and how confident the product is about each claim**.

This document turns that question into one explicit interface contract.
It is the liveness companion to `108-approval-memory-constellation-mutation-and-family-rebase-interface-spec.md`, the availability companion to `91-fetchability-and-full-copy-witness-spec.md`, and the dormant-return companion to `70-dormant-peer-reentry-and-stale-state-review-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Synchronization Modes`, `My files don't sync`, `How to clear offline devices? (desktop only)`, `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.`, `Disconnecting and Removing Folders`, and `Sync Private Identity & Linking My Devices` together still describe a system where:

- at least one peer that actually has the files must be online for a selective-sync fetch to succeed
- the peers list distinguishes currently online peers from peers that have ever been connected, with disconnected peers shown in gray
- hidden offline devices are not the same thing as unlinked devices and can later reappear
- you cannot remotely unlink another device
- a visible placeholder or remembered linked-device descendant therefore does not, by itself, prove that the descendant is currently alive, reachable, or still a trustworthy byte source

That is not a criticism of peer-to-peer reality.
It is a criticism of any surface that lets remembered-family membership masquerade as current liveness.
AnonSync should therefore expose one explicit **descendant liveness and reachability-confidence contract** wherever remembered approval or linked-family convenience might otherwise imply too much.

## Core rule

Trust-family membership is not current liveness.

The product is not fully inspectable until it can answer seven questions in one place:

1. which descendant seat/member/device is being discussed
2. whether that descendant still belongs to the remembered-trust family for historical or future-reuse purposes
3. when that descendant was last directly witnessed alive
4. whether the current claim is based on live observation, receipt-reconciled history, hidden-device memory, or pure lineage reconstruction
5. whether the descendant is currently expected to be a byte source, approval seat, explanation-only historical node, or none of the above
6. what confidence the product has in the liveness claim
7. which receipt later proves that this descendant was live, stale, hidden-only, reappeared, historical only, or unknown

If the operator still has to infer from linked-device membership, old approval history, or placeholder presence whether a descendant is currently alive enough to justify lower-friction convenience, the surface is not explicit enough.

## Public objects

### Approval-memory descendant liveness row

A compact read object describing one descendant's current liveness and confidence posture relative to a remembered-trust family.

Suggested fields:

- `approval_memory_descendant_liveness_row_id`
- `approval_memory_ref`
- `seat_ref`
- `descendant_ref`
- `descendant_kind` (`reviewed-seat`, `linked-member`, `hidden-member`, `reappeared-member`, `historical-node`, `unknown`)
- `inheritance_posture` (`inherits-unchanged`, `inherits-cooled`, `inherits-frozen`, `fresh-required`, `split-into-child-family`, `revoked`, `historical-only`, `unknown`)
- `liveness_class` (`live-observed`, `recently-live`, `reachable-unproven`, `hidden-awaiting-return`, `reappeared-awaiting-proof`, `stale-unseen`, `historical-only`, `unknown`)
- `last_live_observed_at` nullable
- `last_byte_source_observed_at` nullable
- `confidence_class` (`high`, `guarded`, `low`, `unknown`)
- `current_expected_role` (`byte-source`, `approval-seat`, `explanation-only`, `none`, `unknown`)
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Descendant-liveness explanation

A read object explaining why one descendant currently carries a particular liveness/confidence posture.

Suggested fields:

- `approval_memory_descendant_liveness_explanation_id`
- `approval_memory_ref`
- `descendant_ref`
- `liveness_class`
- `confidence_class`
- `evidence_basis` (`live-observation`, `receipt-reconciled`, `hidden-device-memory`, `reappearance-proof`, `lineage-only`, `mixed`, `unknown`)
- `why`
- `non_effect_summary`
- `proof_refs[]`

### Descendant-liveness refresh plan

A prepared review object for one attempt to refresh stale descendant knowledge without silently renewing trust scope.

Suggested fields:

- `approval_memory_descendant_liveness_refresh_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `descendant_ref`
- `current_liveness_class`
- `requested_outcome` (`record-live-observation`, `mark-historical-only`, `freeze-reuse-until-live`, `require-fresh-approval-on-return`, `dismiss-false-reappearance`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Descendant-liveness receipt

A durable object proving the result of one reviewed descendant-liveness decision.

Suggested fields:

- `approval_memory_descendant_liveness_receipt_id`
- `approval_memory_ref`
- `descendant_ref`
- `previous_liveness_class`
- `outcome`
- `reviewed_at`
- `resulting_liveness_class`
- `resulting_confidence_class`
- `proof_refs[]`

## Liveness classes

### `live-observed`

Use when the product has recent direct evidence that the descendant is currently online and acting in the role being claimed.

### `recently-live`

Use when the descendant was observed alive recently enough that convenience claims can still rely on it, but the evidence is no longer immediate.

### `reachable-unproven`

Use when routing or identity evidence suggests the descendant may be reachable, but the product cannot yet prove byte-serving or approval-seat capability.

### `hidden-awaiting-return`

Use when the descendant is still part of historical lineage or linked-family memory but is currently hidden/offline and should not be treated as currently available convenience.

### `reappeared-awaiting-proof`

Use when a previously hidden or stale descendant has resurfaced but the product has not yet proven that prior convenience assumptions are safe to reuse.

### `stale-unseen`

Use when a descendant remains part of remembered lineage but has not been directly observed for too long to support strong present-tense claims.

### `historical-only`

Use when the descendant remains important for explanation and receipts but should not authorize current convenience or be counted as a live source.

### `unknown`

Use when the product lacks enough evidence to make an honest liveness claim.
Unknown is a proof problem, not a softer `recently-live`.

## Confidence classes

Every descendant-liveness row should also expose how strong the evidence actually is.

### `high`

Use when current direct observation or a fresh reviewed receipt supports the liveness claim.

### `guarded`

Use when the product has some credible evidence, but it is indirect, aging, or missing one capability proof.

### `low`

Use when the claim depends mostly on stale history, hidden-device memory, or incomplete reappearance evidence.

### `unknown`

Use when the product cannot honestly explain why it believes the liveness claim at all.

## Fixed inspection order

Every descendant-liveness surface should preserve the same sections in the same order:

1. **Descendant identity and family posture**
2. **Current liveness and confidence**
3. **What roles this descendant may honestly fill now**
4. **What definitely is not being claimed**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Descendant identity and family posture

This section should show:

- which remembered-approval family is in view
- which descendant seat/member/device is being discussed
- descendant kind
- current inheritance posture
- next honest action

The operator must be able to answer: **who is this descendant in the trust family, before we say anything about whether it is alive now?**

### 2) Current liveness and confidence

This section should show:

- liveness class
- confidence class
- last live observation time
- last byte-source observation time, if any
- evidence basis

The operator must be able to answer: **how alive does the product think this descendant is, and how sure is it really?**

### 3) What roles this descendant may honestly fill now

This section should show:

- whether the descendant may currently be counted as a byte source
- whether the descendant may currently be counted as an approval-capable seat
- whether the descendant is explanation-only historical lineage
- whether future convenience is blocked until fresher proof exists

The operator must be able to answer: **what present-tense role can this descendant honestly play right now?**

### 4) What definitely is not being claimed

This section should show:

- that family membership alone does not prove online reachability
- that placeholder visibility does not prove any descendant still has bytes
- that hidden-device memory does not silently count as current approval-seat availability
- that liveness review does not itself renew trust freshness, widen scope, claim arrivals, bind paths, or materialize bytes

The operator must be able to answer: **what tempting but unsafe conclusion is the product refusing to make for me?**

### 5) Admissible reviewed outcomes

This section should show the distinct reviewed outcomes:

- `Record live observation`
- `Mark historical only`
- `Freeze reuse until live`
- `Require fresh approval on return`
- `Dismiss false reappearance`

The operator must be able to answer: **what can I honestly do about this descendant now?**

### 6) Receipts and proof links

This section should show:

- live-observation receipts, if any
- hidden/reappearance receipts, if any
- trust-lineage or rebase receipts, if needed for context
- the reviewed descendant-liveness receipt proving the current posture
- any missing proof that forced `unknown`

The operator must be able to answer: **what evidence later proves why this descendant counted as live, stale, hidden, or historical only?**

## Decision rules

### No liveness by family-membership rule

A descendant must not inherit `live` posture merely because it still belongs to the remembered-trust family.

### No byte-source by placeholder rule

A placeholder or visible name must not cause the product to imply that this descendant still has retrievable bytes.

### No approval-seat by stale-return rule

A descendant that reappears after long dormancy must not silently count as an approval-capable seat without current proof or explicit policy.

### Historical explanation survives liveness downgrade

A descendant can remain important for explanation and lineage even after it stops counting as a live convenience target.

## Dense-row contract

Every dense/mobile row should keep five facts adjacent:

1. descendant identity
2. family/inheritance posture
3. liveness class
4. confidence class or witness age
5. next honest action

Good examples:

- `tablet-citrine · inherits frozen · hidden awaiting return · low confidence · Freeze reuse until live`
- `desktop-ash · split child family · reappeared awaiting proof · guarded confidence · Require fresh approval on return`
- `home-nas · inherits unchanged · live observed 4m ago · high confidence · Record live observation`

Bad examples:

- `Known device`
- `Available before`
- `Probably online`
- `Connected family`

## CLI sketch

```text
anonsync approval memory descendants list --seat self --scope family-arrivals
anonsync approval memory descendants show --memory apm_01J... --seat self
anonsync approval memory descendants show --memory apm_01J... --descendant tablet-citrine
anonsync approval memory descendants refresh --memory apm_01J... --descendant tablet-citrine --outcome freeze-reuse-until-live --plan
anonsync approval memory descendants apply apdl_01J...
```

## Why this matters

A weaker product shape would let the operator see that a descendant still belongs to the remembered-trust family and then quietly rely on that fact as if it also proved the descendant is alive enough to serve bytes, approve new convenience, or explain future lower-friction behavior.
AnonSync should do better.
The surface must keep **family membership**, **current liveness**, **role honesty**, and **confidence** adjacent, so convenience does not quietly outrun evidence.
