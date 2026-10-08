# Approval-memory constellation-mutation and family-rebase interface spec

## Purpose

The archive already separates first approval from later matches, freshness, lineage, authorization trace, and policy drift.
One gap still remained:

> when the linked-device constellation or identity epoch changes underneath remembered approval, the operator must be able to ask **does this stay one trust family, split into descendants, freeze future reuse, or require fresh approval for some seats now?**

This document turns that question into one explicit interface contract.
It is the constellation-mutation companion to `61-personal-constellation-and-authority-domain-spec.md`, the freshness companion to `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`, and the historical companion to `107-approval-memory-lineage-and-authorization-trace-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync Private Identity & Linking My Devices`, `User Management`, and `How to clear offline devices? (desktop only)` together still describe a system where:

- all linked devices act as Owners when syncing across one identity
- approval can be issued from any linked device where the folder is active
- a remote user can choose to automatically approve all linked devices for future sharing after approving one
- linking already-initialized devices can make one device lose its certificate and take over the other's identity and configured shares
- offline linked devices can be hidden without unlinking, and if they later reappear online they continue sharing as before
- you cannot remotely unlink other devices

That is real convenience.
What current docs still do **not** expose as one first-class surface is the later answer to:

- what happens to old remembered approval when the device set behind one identity changes
- whether a hidden/reappeared device is still covered by the same remembered trust family
- whether a certificate takeover or re-link should branch trust history rather than silently continuing it
- which descendants of an old approval family remain safe to reuse and which must cool, freeze, or demand fresh approval
- which receipt later proves that split, carry-forward, or freeze decision

AnonSync should not accept reconstructive trust folklore here either.
Any remembered approval that can outlive identity/constellation mutation should therefore also expose one explicit **family-split and rebase contract**.

## Core rule

Remembered trust is not permanently monolithic across constellation mutation.

When the identity or linked-device constellation changes in a way that can change who may later benefit from remembered approval, the product must answer six questions in one place:

1. which remembered approval family is in view
2. which constellation or identity mutation triggered re-evaluation
3. which descendants or seats still inherit that memory safely
4. which descendants must cool, freeze, or require fresh approval
5. whether the product is carrying one family forward, splitting it into reviewed branches, or refusing reuse entirely
6. which receipts later prove that decision

If the operator still has to infer from device lists, hidden-offline state, unlink/relink steps, or approval history whether old trust silently followed a changed constellation, the surface is not explicit enough.

## Public objects

### Approval-memory rebase row

A compact read object describing one remembered-approval family whose safe reuse is affected by constellation or identity mutation.

Suggested fields:

- `approval_memory_rebase_row_id`
- `approval_memory_ref`
- `seat_ref`
- `current_head_ref`
- `triggering_mutation_ref`
- `mutation_class` (`identity-epoch-changed`, `linked-device-added`, `linked-device-hidden`, `hidden-device-reappeared`, `certificate-takeover`, `unlink-observed`, `manual-scope-narrowing-followup`, `unknown`)
- `current_family_posture` (`unchanged`, `review-required`, `split-recommended`, `freeze-descendants-recommended`, `fresh-required-for-descendants`, `revoked`)
- `affected_descendant_count`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Constellation-mutation impact explanation

A read object explaining why one trust family is no longer trivially reusable as-is.

Suggested fields:

- `approval_memory_mutation_impact_explanation_id`
- `approval_memory_ref`
- `triggering_mutation_ref`
- `previous_constellation_summary`
- `current_constellation_summary`
- `identity_epoch_compare`
- `descendant_postures[]`
- `non_effect_summary`
- `proof_refs[]`

### Approval-memory descendant posture

A read object describing how one descendant seat/member/device currently relates to a remembered approval family.

Suggested fields:

- `approval_memory_descendant_posture_id`
- `approval_memory_ref`
- `descendant_ref`
- `descendant_kind` (`reviewed-seat`, `linked-member`, `hidden-member`, `reappeared-member`, `successor-seat`, `unknown`)
- `inheritance_posture` (`inherits-unchanged`, `inherits-cooled`, `inherits-frozen`, `fresh-required`, `split-into-child-family`, `revoked`, `unknown`)
- `why`
- `last_observed_at`
- `proof_refs[]`

### Approval-memory rebase plan

A prepared reviewed action describing how one remembered-approval family will respond to a triggering mutation.

Suggested fields:

- `approval_memory_rebase_plan_id`
- `approval_memory_ref`
- `seat_ref`
- `triggering_mutation_ref`
- `requested_outcome` (`keep-current-family`, `split-reviewed-branches`, `freeze-descendants`, `require-fresh-for-selected-descendants`, `revoke-family`)
- `selected_descendant_outcomes[]`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Approval-memory rebase receipt

A durable record proving how one remembered-approval family was carried forward, split, or frozen after constellation mutation.

Suggested fields:

- `approval_memory_rebase_receipt_id`
- `approval_memory_ref`
- `triggering_mutation_ref`
- `outcome`
- `reviewed_at`
- `resulting_family_refs[]`
- `descendant_outcomes[]`
- `proof_refs[]`

## Fixed inspection order

Every approval-memory rebase surface should preserve the same sections in the same order:

1. **Remembered approval family and trigger**
2. **What constellation or identity changed**
3. **Which descendants still inherit what**
4. **What definitely does not happen automatically**
5. **Admissible outcomes**
6. **Receipts and proof links**

### 1) Remembered approval family and trigger

This section should show:

- which remembered approval family is in view
- its current lineage head
- the triggering mutation class
- current family posture
- next honest action

The operator must be able to answer: **what trust family are we reviewing, and why is it under rebase now?**

### 2) What constellation or identity changed

This section should show:

- previous versus current constellation summary
- previous versus current identity epoch or fingerprint posture
- whether the triggering event was certificate takeover, hidden-member reappearance, local unlink, or ordinary linked-member growth
- which seats were newly introduced, removed, hidden, or re-seen

The operator must be able to answer: **what actually changed underneath the trust family?**

### 3) Which descendants still inherit what

This section should show:

- each descendant seat/member/device
- whether it inherits unchanged, inherits cooled, inherits frozen, requires fresh approval, or splits into a child family
- the reason for that posture
- whether the descendant can still explain older subject matches historically even if future reuse is now blocked

The operator must be able to answer: **who still benefits from this remembered trust, and under what new limits?**

### 4) What definitely does not happen automatically

This section should show:

- that inspecting rebase does not renew trust
- that a hidden device reappearing does not silently regain `warm` shortcut status unless policy already proves it
- that certificate takeover does not silently merge two trust families into one timeless memory
- that hiding an offline device does not count as authority revocation on its own
- that rebase review does not claim arrivals, bind paths, or materialize bytes

The operator must be able to answer: **what convenience or continuity is *not* being assumed behind my back?**

### 5) Admissible outcomes

This section should show the distinct reviewed outcomes:

- `Keep current family as-is`
- `Split into reviewed child families`
- `Freeze descendant reuse`
- `Require fresh approval for selected descendants`
- `Revoke family`

The operator must be able to answer: **what can I honestly do now, and how far does each choice reach?**

### 6) Receipts and proof links

This section should show:

- the triggering mutation receipt
- any origin/freshness/lineage receipts still relevant to the family
- the reviewed rebase receipt proving branch creation, freeze, or fresh-required outcomes
- any missing proof that forces `unknown` descendant posture

The operator must be able to answer: **what exact evidence later proves how this trust family was carried forward or split?**

## Rebase rules

### No silent merge rule

A certificate takeover, re-link, or identity-epoch change must not silently merge unrelated remembered-approval families.
If continuity is desired, it must be reviewed and receipted.

### Hidden-member honesty rule

Hiding an offline linked device is presentation cleanup, not unlink.
If that member later reappears, the product must re-show its descendant posture explicitly instead of silently restoring the previous convenience temperature.

### Descendant split rule

If only part of a changed constellation should still inherit remembered approval, the product must create child-family or descendant-specific outcomes rather than keeping one broad family with hand-waved exceptions.

### Historical-proof rule

A descendant that loses future reuse may still need to preserve historical explanation for old matches.
The product must therefore separate `may explain past` from `may authorize future reuse`.

### Non-effect rule

Rebase inspection and rebase outcomes must not silently:

- renew trust freshness
- widen approval scope
- claim a subject
- bind a path
- materialize bytes

## Dense and mobile rules

A dense row or mobile card may compress wording, but it must still preserve four cues:

- remembered approval family
- mutation trigger
- current family posture
- next honest action

`Maya / photos-collab · certificate takeover 3d ago · split recommended · Rebase trust family` is acceptable compression.
`Known peer changed` is not.

## CLI contract

Minimal commands:

```text
anonsync approval memory rebase list --seat self --scope family-arrivals
anonsync approval memory rebase show --memory apm_01J... --seat self
anonsync approval memory rebase prepare --memory apm_01J... --event cmt_01J... --outcome split-reviewed-branches --plan
anonsync approval memory rebase prepare --memory apm_01J... --event cmt_01J... --outcome require-fresh-for-selected-descendants --descendant tablet-citrine --plan
anonsync approval memory rebase apply aprb_01J...
```

The verbs must stay literal.
Do not hide this family split work behind vague `relink trust`, `keep linked`, or `repair approval` verbs.

## Example

Good compact row:

```text
Maya / photos-collab   certificate takeover 3d ago   split recommended   2 descendants affected   Rebase trust family
```

Good descendant rows:

```text
home-nas        inherits unchanged        reviewed seat remained in same epoch
tablet-citrine  fresh required            hidden member reappeared after 214d offline
desktop-ash     split into child family   certificate takeover changed identity epoch
```

Bad compact row:

```text
Maya / photos-collab   linked devices changed   Keep
```

The bad form hides the trigger class, the branch posture, and whether any descendants must stop reusing old trust.

## Why this matters

Resilio's convenience model still proves that identity-level reuse and linked-device reach are genuinely useful.
But current docs also show enough about certificate takeover, hidden-device return, all-devices-as-owners, and non-remote unlinking to make one thing clear:

> once the constellation itself changes, old approval memory is no longer one harmless blob.

AnonSync should therefore keep the convenience ambition while insisting that remembered trust can branch, cool, freeze, or demand fresh approval in a reviewed and receipted way whenever the device set behind that trust actually changes.
