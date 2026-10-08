# Policy-delta preview and arrival-simulation interface spec

The archive already separates arrival announcement from local claim, claim from bind, standing approval memory from local admission, placement suggestion from committed bind, and standing seat templates from current share posture.
What still remained too easy to blur was the mutation question that appears when an operator changes one of those standing defaults:

> what exactly will this policy change alter for future unseen arrivals, already visible drafts, currently claimed-but-unbound subjects, existing bound shares, and previously remembered trust — and what definitely will *not* change?

This document turns that question into one explicit interface contract.
It is the mutation-preview companion to `58-policy-origin-defaults-and-precedence-spec.md`, the standing-template companion to `100-standing-arrival-template-and-default-root-review-interface-spec.md`, and the explanation/counterfactual companion to `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`.

A later audit surface must also be able to point from any subject affected here to the exact policy version and receipt that actually handled it.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Synchronization Modes`, `Selective Sync`, `Sync Private Identity & Linking My Devices`, `Folder Types and Management`, `How to manually set the location of the folders synced across linked devices?`, `Folders are duplicating with an index (i) in their name.`, and `Simple Mode (Android)` together still describe a system where:

- the selected linked-device mode applies to newly added folders
- current folders remain as they are after a standing mode change
- prior approval can let later pending folders auto-connect
- linked-device convenience and default folder behavior still influence later arrivals before per-arrival review
- mobile `Simple mode` still changes where new shares land and whether same-name arrivals become `(1)` duplicates

That is genuine convenience.
But it still means the operator often has to infer retroactivity from folklore:
which current subjects are grandfathered, which open drafts will change, which already bound paths stay untouched, and whether remembered approval scope is being tightened, widened, or left alone.

AnonSync should not accept that reconstruction burden.
Any durable change to later-arrival policy should therefore surface one explicit **policy-delta preview** with effect buckets, sample subjects, and explicit non-effects.

## Core rule

A standing-policy mutation is not complete until the product can answer five questions in one place:

1. which governed scope is changing
2. which subject classes will change automatically
3. which subject classes will only change if explicitly refreshed
4. which subject classes are guaranteed unchanged
5. which example arrivals prove that the preview is honest

If the operator still has to remember old mode semantics, mobile simplification rules, default paths, or prior approval folklore to answer those five questions, the surface is not ready to apply.

## Public objects

### Policy delta preview

A read object summarizing the practical effect of one proposed standing-policy change for one reviewed seat and governed scope.

Suggested fields:

- `policy_delta_preview_id`
- `seat_ref`
- `governed_scope`
- `current_policy_refs[]`
- `proposed_policy_delta`
- `effect_buckets[]`
- `example_subjects[]`
- `non_effect_guarantees[]`
- `risk_flags[]`
- `computed_at`

### Effect bucket

A stable preview bucket saying what happens to one subject class.

Required buckets:

- `future-unseen-arrivals`
- `announced-unclaimed`
- `claimed-unbound`
- `bound`
- `materialized-bytes`
- `approval-memory-and-matches`

Suggested fields:

- `bucket_kind`
- `effect_kind` (`unchanged`, `new-default`, `refresh-optional`, `refresh-required`, `blocked`, `subset-review-required`)
- `summary`
- `subject_count` nullable
- `requires_explicit_subject_list`
- `example_subject_refs[]`

### Example subject

A concrete representative subject included so the operator does not have to imagine the preview abstractly.

Suggested fields:

- `subject_ref`
- `current_stage`
- `predicted_stage_after_apply`
- `change_class` (`unchanged`, `draft-updated`, `needs-manual-review`, `future-only`)
- `difference_summary`

### Non-effect guarantee

A durable statement of something the proposed change definitely does not do.

Suggested fields:

- `guarantee_kind` (`no-rebind`, `no-evict`, `no-auto-claim`, `no-memory-widen`, `no-sibling-withdraw`, `no-current-byte-change`)
- `summary`
- `confidence` (`hard`, `policy-hard`, `subject-hard`)

## Fixed review order

Every policy-delta review should preserve the same sections in the same order:

1. **Acting seat and governed scope**
2. **Current policy and proposed delta**
3. **Effect buckets**
4. **Example subjects**
5. **Explicit non-effects**
6. **Admissible actions**
7. **Receipt promise**

### 1) Acting seat and governed scope

This section should show:

- which reviewed seat is changing policy
- which governed scope is affected
- which standing objects are changing (`approval memory`, `arrival template`, `default root`, `collision default`, `materialization suggestion`)
- whether the change is narrow, future-reaching, or mixed

The operator must be able to answer: **what universe of later behavior am I editing?**

### 2) Current policy and proposed delta

This section should show:

- the effective policy now
- the proposed changed fields
- unchanged fields kept explicitly visible
- policy origin / precedence

The operator must be able to answer: **what exact policy is changing rather than merely being re-described?**

### 3) Effect buckets

This section is mandatory.
It should show one stable row per required bucket.

Examples:

- `future unseen arrivals -> announce-only instead of claim-suggested`
- `announced but unclaimed -> unchanged unless you explicitly refresh drafts`
- `claimed but unbound -> unchanged; subset review required for any refresh`
- `bound -> unchanged`
- `materialized bytes -> unchanged`
- `approval memory and matches -> unchanged`

The operator must be able to answer: **which classes move now, later, never, or only under extra review?**

### 4) Example subjects

This section should always show at least one concrete subject whenever the relevant bucket contains current subjects.

Example:

```text
Photos-2026   announced-unclaimed -> unchanged   old draft preserved unless refresh is selected
Scans-2025    bound -> unchanged   current bind and local bytes stay untouched
Maya approval memory   unchanged   future arrivals still match identity but do not auto-claim
```

The operator must be able to answer: **what will happen to real things I already know by name?**

### 5) Explicit non-effects

This section is mandatory.
It should include the strongest easy-to-misread non-effects, for example:

- changing the default root does **not** rebind already bound shares
- tightening approval memory does **not** hide already announced subjects
- changing arrival admission from `claim-suggested` to `announce-only` does **not** evict materialized bytes from current shares
- disabling a convenience template does **not** silently rewrite sibling seats

The operator must be able to answer: **what plausible scary thing is not happening?**

### 6) Admissible actions

This section should allow verbs such as:

- `Apply for future arrivals only`
- `Apply and refresh unclaimed drafts`
- `Open claimed-subject subset review`
- `Keep current policy`
- `Open narrower-scope policy edit`

It must not flatten unlike outcomes into one generic `Save settings`.

### 7) Receipt promise

The receipt promise should show:

- acting seat and governed scope
- changed policy fields
- reviewed effect buckets
- chosen refresh mode
- guaranteed unchanged classes
- whether example-subject previews were computed from live state

The operator must be able to answer: **what later receipt proves the exact retroactivity boundary I accepted?**

## Row and card contract

A truthful compact row should keep these facts adjacent, in this order:

1. seat + scope
2. proposed delta summary
3. strongest effect bucket
4. strongest non-effect
5. next honest action

Example:

```text
Home-NAS / family arrivals   announce-only + new default root   future-only unless drafts refreshed   bound shares unchanged   Preview impact
```

Opening the row should reveal effect buckets and example subjects before any apply button.

## Simulation rule

The product should support a lightweight `simulate` view for standing-policy edits.
This simulation is not a second planner and not a mutation on its own.
It is a read projection over the same policy delta preview that answers:

- what a named subject would look like after the delta
- what future unseen arrivals would do by default
- what currently visible subjects would not change without refresh

This matters because operators often trust examples faster than they trust category prose.

## Dense/mobile rule

Dense and mobile clients may compress wording, but they must still preserve:

- proposed delta summary
- one strongest effect bucket
- one explicit non-effect
- an entry point to example subjects
- an honest apply label that matches the chosen retroactivity boundary

A dense client may shorten `Apply for future arrivals only` to `Future only`, but it may not hide whether open drafts remain unchanged.

## CLI contract

The CLI should expose the preview as a first-class read surface:

```text
anonsync policy delta preview --seat home-nas --scope family-arrivals --admission announce-only --path-template /tank/family/{{share_name}}
anonsync policy delta preview show pdp_01J...
anonsync policy delta simulate --preview pdp_01J... --subject incoming:photos-2026
anonsync policy delta apply pdp_01J... --refresh unclaimed-only
anonsync policy delta receipt show pdr_01J...
```

The CLI should never reduce this to `settings set mode=disconnected` or equivalent folklore.

## What must never be implied

The interface must never imply that:

- changing a standing policy automatically rebinds already bound shares
- changing a future-arrival policy automatically evicts current bytes
- tightening remembered approval automatically withdraws already visible arrivals
- mobile convenience settings are harmless enough to skip retroactivity preview
- one example subject preview is the same as a whole effect-bucket guarantee

The truthful contract is: **preview classes first, named examples second, receipt-backed apply last**.
