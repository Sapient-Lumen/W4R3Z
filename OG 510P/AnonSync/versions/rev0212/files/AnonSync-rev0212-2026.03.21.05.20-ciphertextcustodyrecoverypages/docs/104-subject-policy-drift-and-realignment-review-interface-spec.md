# Subject-policy drift and realignment review interface spec

The archive now previews standing-policy edits before apply and preserves explicit lineage after those edits land.
What still remained too easy to lose was the **operational queue** between those two truths:

> after a few standing-policy changes, which current subjects still differ from today's policy, which of those differences are intentional grandfathering, and which can be safely realigned now?

This document turns that question into one explicit interface contract.
It is the remediation companion to `102-policy-delta-preview-and-arrival-simulation-interface-spec.md`, the operational companion to `103-standing-policy-lineage-and-subject-attribution-interface-spec.md`, and the review companion to `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Selective Sync`, `Synchronization Modes`, `Sync Private Identity & Linking My Devices`, `Folder Types and Management`, and `How to manually set the location of the folders synced across linked devices?` together still describe a system where:

- linked-device mode changes apply to newly added folders while current ones remain as they are
- prior approval can let later pending folders auto-connect
- all linked-device folders remain visible across the linked set
- default roots and connect rituals still shape later placement without revisiting earlier arrivals
- current help mostly explains current mode/default behavior, not which existing subjects now diverge from that current policy or whether they should be realigned

That is real convenience.
But after several policy edits the operator still needs one first-class answer to:

- which active subjects now differ from the current standing policy
- whether each difference is an intentional grandfathered outcome, a refreshable draft, a subset-review case, or a pinned exception
- which differences can be batch-realigned safely and which require stronger review
- which receipt later proves that a subject stayed grandfathered on purpose rather than merely being forgotten

AnonSync should not accept that reconstruction burden.
Any standing-policy family that can change later-arrival behavior should therefore also surface one explicit **drift and realignment contract**.

## Core rule

A standing-policy family is not fully operational until the product can answer seven questions in one place:

1. what current effective policy is being treated as the realignment target
2. which visible subjects differ from that target right now
3. how each differing subject is classified (`grandfathered`, `refresh-eligible`, `subset-review`, `pinned-exception`, `blocked`, `unknown`)
4. which subjects can be safely realigned together and which require stronger review
5. which subjects are intentionally left alone and why
6. what definitely will not change during the proposed realignment
7. which receipt later proves the reviewed keep/realign/exception outcome

If the operator still has to compare one lineage sheet, one arrival row, and one current settings page to assemble those seven answers, the surface is not explicit enough.

## Public objects

### Policy drift row

A compact read object describing how one current subject relates to the current effective standing policy.

Suggested fields:

- `policy_drift_row_id`
- `subject_ref`
- `seat_ref`
- `governed_scope`
- `current_subject_stage`
- `current_policy_version_ref`
- `applied_policy_version_ref`
- `drift_class` (`matches-current`, `grandfathered`, `refresh-eligible`, `subset-review-required`, `pinned-exception`, `blocked`, `unknown`)
- `difference_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Policy drift population

A read object summarizing one seat/scope's current divergence from the current effective standing policy.

Suggested fields:

- `policy_drift_population_id`
- `seat_ref`
- `governed_scope`
- `current_policy_version_ref`
- `summary_counts`
- `drift_rows[]`
- `generated_at`
- `generation_basis` (`live`, `cached`, `receipt-reconciled`)

### Realignment review plan

A prepared mutation object for one reviewed attempt to refresh or pin a selected subset of drifting subjects.

Suggested fields:

- `realignment_review_plan_id`
- `seat_ref`
- `governed_scope`
- `target_policy_version_ref`
- `selected_subject_refs[]`
- `selection_classes`
- `requested_outcome` (`refresh-drafts`, `recompute-eligible`, `pin-exception`, `keep-grandfathered`, `open-subset-review`)
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Subject exception pin

A durable object proving that one subject is intentionally allowed to keep a non-current outcome.

Suggested fields:

- `subject_exception_pin_id`
- `subject_ref`
- `seat_ref`
- `current_policy_version_ref`
- `kept_applied_policy_version_ref`
- `pin_reason`
- `review_receipt_ref`
- `review_expires_at` nullable

## Fixed inspection order

Every drift/realignment surface should preserve the same sections in the same order:

1. **Seat, scope, and target current policy**
2. **Drift population summary**
3. **Per-subject drift classes**
4. **Proposed realignment effects**
5. **What will stay grandfathered or pinned**
6. **Admissible actions**
7. **Receipts and proof links**

### 1) Seat, scope, and target current policy

This section should show:

- which reviewed seat is in view
- which governed scope is in view
- which current effective policy version is the proposed realignment target
- whether the population view is live or cached

The operator must be able to answer: **what current policy are these subjects being compared against?**

### 2) Drift population summary

This section should show:

- total visible subjects in scope
- how many match current policy already
- how many are grandfathered intentionally
- how many are refresh-eligible
- how many require subset review
- how many are pinned exceptions or blocked

The operator must be able to answer: **how much drift exists, and of what kinds?**

### 3) Per-subject drift classes

This section should show, for each drifting subject:

- subject name and current stage
- current policy version summary
- applied policy version summary
- drift class
- strongest difference summary
- next honest action

The operator must be able to answer: **what kind of difference is this specific subject carrying?**

### 4) Proposed realignment effects

This section is mandatory whenever the operator has selected one or more subjects.
It should show:

- which selected subjects can be safely refreshed together
- which selected subjects require stronger review before any change
- which selected subjects will remain untouched by design
- whether the request changes draft path, claim posture, bind posture, or only durable exception metadata

Example:

```text
Selected outcome: refresh eligible drafts to current v8
Will change: Photos-2026 draft path will be cleared and subject will return to announced-only
Will not change: Invoices-2025 stays bound at /srv/family and keeps current bytes
Escalation: Scans-2026 requires subset review because it is already claimed but unbound
```

The operator must be able to answer: **what exactly would realign here, and what would not?**

### 5) What will stay grandfathered or pinned

This section is mandatory.
It should include the strongest easy-to-misread non-effects, for example:

- keeping a grandfathered draft is a reviewed choice, not a forgotten stale state
- pinning an exception does not mutate the current standing policy
- refreshing one eligible draft does not rebind already bound siblings
- marking one subject `keep grandfathered` does not bless all older subjects automatically

The operator must be able to answer: **what difference is intentionally preserved, and what tempting false reading should I avoid?**

### 6) Admissible actions

This section should allow verbs such as:

- `Refresh eligible drafts`
- `Open claimed-subject subset review`
- `Pin as reviewed exception`
- `Keep grandfathered`
- `Inspect lineage`
- `Inspect current policy`

It must not flatten unlike outcomes into one vague `Update all`, `Reconnect all`, or `Apply defaults` verb.

### 7) Receipts and proof links

The receipts section should show:

- the receipt that established the current target policy
- the receipt that established the older applied policy, when relevant
- the receipt for any realignment or exception-pin action taken here
- whether the drift population was computed live or from cached lineage state

The operator must be able to answer: **what later proof confirms that this difference was refreshed, kept, or pinned on purpose?**

## Drift classes

The product should preserve at least these classes:

- `matches-current` — subject already reflects current policy
- `grandfathered` — subject differs from current policy but keeping that difference is currently acceptable without further mutation
- `refresh-eligible` — subject differs from current policy and can be safely refreshed to current policy without a stronger subset review
- `subset-review-required` — subject differs from current policy but touches bind, local bytes, or broader authority, so it cannot join a light batch
- `pinned-exception` — subject intentionally carries a durable reviewed exception against current policy
- `blocked` — realignment cannot proceed because prerequisites or proof are missing
- `unknown` — attribution or current state is too incomplete for safe realignment claims

## Row and card contract

A truthful compact row should keep these facts adjacent, in this order:

1. subject
2. current policy summary
3. applied policy summary
4. drift class
5. next honest action

Example refresh-eligible row:

```text
Photos-2026   current v8 announce-only /tank/family   applied v6 claim-suggested /srv/family   refresh-eligible   Refresh under current policy
```

Example intentional exception row:

```text
Invoices-2025   current v8 announce-only /tank/family   applied v6 bound /srv/family   pinned exception   Keep bind / inspect exception
```

Example seat summary row:

```text
Home-NAS / family arrivals   current v8 announce-only   4 refresh-eligible   2 subset review   3 pinned/grandfathered   Review drift
```

Opening the row should reveal drift class, strongest difference, non-effects, and receipts before any mutation verb.

## Dense/mobile rule

Dense and mobile clients may compress wording, but they must still preserve:

- current policy summary
- applied policy or `matches current`
- one explicit drift class
- one honest next action

A dense client may shorten `refresh-eligible under current policy` to `refresh-eligible v8`, but it may not hide whether the subject is safe to batch, intentionally grandfathered, or blocked.

## Batch rule

Mixed drift selections must split before apply.
At minimum the product should separate:

- refresh-eligible subjects that can be safely refreshed together
- subjects requiring subset review
- intentionally grandfathered or pinned subjects that are being kept, not changed
- blocked or unknown subjects that cannot be touched yet

A batch bar may say `Refresh 4 eligible drafts`, but it must not overclaim with `Realign 9 subjects` if only four are actually safe to change now.

## CLI contract

The CLI should expose drift and realignment as first-class surfaces:

```text
anonsync policy drift list --seat home-nas --scope family-arrivals
anonsync policy drift show --subject incoming:photos-2026 --seat home-nas
anonsync policy realignment review prepare --seat home-nas --scope family-arrivals --subjects incoming:photos-2026,incoming:letters-2026 --outcome refresh-drafts --plan
anonsync policy realignment apply prp_01J...
anonsync subject exception pin --subject share:invoices-2025 --seat home-nas --reason "legacy path intentionally retained"
anonsync policy receipt show prr_01J...
```

The CLI should never reduce this to `reconnect`, `save defaults`, or equivalent folklore.

## What must never be implied

The surface must never imply that:

- every subject differing from current policy is broken
- a grandfathered subject is merely forgotten clutter
- a current standing-policy edit automatically authorizes rebind or rematerialization of older subjects
- keeping one exception means older policy is still current everywhere
- one batch action safely realigns subjects whose risks are materially different

## Why this matters

A weaker product shape would stop after `preview this policy edit` and `show which old version handled this subject`.
That still leaves the operator doing one last dangerous reconstruction step: deciding which live differences are intentional, which are safe to refresh, and which need stronger review.
This document closes that last gap.
