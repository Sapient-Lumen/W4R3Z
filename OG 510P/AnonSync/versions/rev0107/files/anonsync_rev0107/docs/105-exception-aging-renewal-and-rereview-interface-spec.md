
# Exception aging, renewal, and re-review interface spec

## Purpose

The archive now has standing-policy preview, subject attribution, drift classification, and reviewed realignment.
One gap still remained: after the operator intentionally keeps a non-current outcome, how long may that choice remain quiet before the product asks again, and what exactly happens when the review horizon is reached?

This document turns that question into one explicit interface contract.
It is the lifecycle companion to `104-subject-policy-drift-and-realignment-review-interface-spec.md`, the audit companion to `103-standing-policy-lineage-and-subject-attribution-interface-spec.md`, and the long-lived-memory companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful way.
`Sync functionality in detail`, `Sync Private Identity & Linking My Devices`, and `Folder Types and Management` together still describe a system where:

- approving a person once can remain enough for later sharing because the product retains certificate-based approval memory
- a remote user can choose to auto-approve all linked devices for future sharing after approving one
- later pending folders can auto-connect after prior approval
- all linked-device folders remain visible across the linked set
- current help mostly explains how remembered convenience works, not when old convenience memory should come back for explicit review

That is real convenience.
But once the operator intentionally keeps an older draft, path, bind, or approval-shaped outcome, the product still needs one first-class answer to:

- whether that intentional divergence is still within its ordinary review horizon
- whether it is due soon or overdue for reconsideration
- whether reaching that horizon changes anything automatically or only raises review urgency
- which receipt later proves renewal, explicit no-expiry acknowledgement, or return to current policy

AnonSync should not accept silent forever-policy here.
Any standing-policy family that allows intentional non-current outcomes should therefore also surface one explicit **aging, renewal, and re-review contract**.

## Core rule

A standing-policy family is not fully operational until the product can answer six questions in one place:

1. what intentional divergence exists for this subject right now
2. why that divergence was kept or pinned in the first place
3. what the current review horizon and aging class are
4. what definitely will **not** happen automatically when the horizon is reached
5. which reviewed outcomes are available now (`renew`, `return to current policy`, `keep without expiry`, or stronger review)
6. which receipt later proves the chosen renewal or reconsideration outcome

If the operator still has to combine drift rows, lineage history, remembered approval lore, and one old exception receipt to assemble those six answers, the surface is not explicit enough.

## Public objects

### Exception aging row

A compact read object describing one intentional non-current subject's current review-horizon posture.

Suggested fields:

- `exception_aging_row_id`
- `subject_ref`
- `seat_ref`
- `governed_scope`
- `current_policy_version_ref`
- `kept_applied_policy_version_ref`
- `exception_kind` (`grandfathered-keep`, `pinned-exception`)
- `aging_class` (`healthy`, `due-soon`, `overdue`, `blocked`, `no-expiry-acknowledged`)
- `review_horizon_at` nullable
- `last_review_receipt_ref`
- `difference_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Exception review population

A read object summarizing the current aging queue for one seat/scope.

Suggested fields:

- `exception_review_population_id`
- `seat_ref`
- `governed_scope`
- `summary_counts`
- `aging_rows[]`
- `generated_at`
- `generation_basis` (`live`, `cached`, `receipt-reconciled`)

### Exception renewal review plan

A prepared mutation object for one reviewed attempt to renew, retire, or explicitly broaden acknowledgement of an intentional exception.

Suggested fields:

- `exception_renewal_review_plan_id`
- `subject_ref`
- `seat_ref`
- `governed_scope`
- `current_policy_version_ref`
- `existing_exception_ref`
- `requested_outcome` (`renew-same-exception`, `return-to-current-policy`, `keep-without-expiry`, `open-stronger-review`)
- `new_review_horizon_at` nullable
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Exception review receipt

A durable object proving the result of one renewal or reconsideration review.

Suggested fields:

- `exception_review_receipt_id`
- `subject_ref`
- `seat_ref`
- `previous_exception_ref`
- `outcome`
- `reviewed_at`
- `next_review_horizon_at` nullable
- `no_expiry_acknowledged` boolean
- `proof_refs[]`

## Fixed inspection order

Every exception-aging surface should preserve the same sections in the same order:

1. **Subject and current divergence**
2. **Why this exception exists**
3. **Review horizon and aging**
4. **What horizon reach does not do**
5. **Admissible outcomes**
6. **Receipts and proof links**

### 1) Subject and current divergence

This section should show:

- subject identity and stage
- current standing policy summary
- kept or pinned older outcome summary
- exception kind

The operator must be able to answer: **what intentional difference exists here right now?**

### 2) Why this exception exists

This section should show:

- original reason for keeping or pinning the older outcome
- whether the subject was `keep grandfathered` or `pin exception`
- the receipt or review that created that intentional divergence

The operator must be able to answer: **why was this difference allowed to persist at all?**

### 3) Review horizon and aging

This section should show:

- aging class
- next review horizon or explicit `no expiry acknowledged`
- last review time
- whether the queue entry is live or cached

The operator must be able to answer: **is this difference still within horizon, due soon, overdue, or explicitly acknowledged as no-expiry?**

### 4) What horizon reach does not do

This section is mandatory.
It should include the strongest easy-to-misread non-effects, for example:

- horizon reach does not silently move a bind to the current default root
- horizon reach does not silently evict local bytes
- horizon reach does not silently widen future approvals or claims
- horizon reach does not silently refresh siblings or seat-wide policy

The operator must be able to answer: **what tempting automatic story is false here?**

### 5) Admissible outcomes

This section should allow verbs such as:

- `Renew exception`
- `Return to current policy`
- `Keep without expiry`
- `Inspect drift`
- `Inspect lineage`

It must not flatten unlike outcomes into one vague `Keep`, `Reconnect`, or `Apply defaults` verb.

### 6) Receipts and proof links

The receipts section should show:

- the receipt that created the current exception
- the latest renewal or acknowledgement receipt, when present
- the receipt that will be produced by the current renewal or reconsideration outcome
- whether the current aging row was computed live or from cached lineage state

The operator must be able to answer: **what later proof confirms that this long-lived difference was renewed, acknowledged, or retired deliberately?**

## Aging classes

The product should preserve at least these classes:

- `healthy` — intentional divergence exists and is comfortably within review horizon
- `due-soon` — no immediate mutation is required, but re-review should happen soon
- `overdue` — re-review is past horizon and should be raised prominently
- `blocked` — re-review cannot proceed safely because current evidence or prerequisites are insufficient
- `no-expiry-acknowledged` — ordinary review horizon is intentionally disabled with a stronger acknowledgement receipt

## Row and card contract

A truthful compact row should keep these facts adjacent, in this order:

1. subject
2. current divergence summary
3. aging class
4. horizon fact or `no expiry acknowledged`
5. next honest action

Example due-soon row:

```text
Invoices-2025   pinned exception vs current v8 announce-only   due-soon   review in 10d   Renew exception
```

Example no-expiry row:

```text
Family-Archive   kept grandfathered under v6   no-expiry-acknowledged   inspect acknowledgement   Inspect exception
```

Example seat summary row:

```text
Home-NAS / family arrivals   2 healthy   1 due-soon   1 overdue   1 no-expiry   Review exceptions
```

## Renewal and reconsideration rules

The product must preserve these distinctions:

- `renew-same-exception` extends or refreshes reviewed permission for the same intentional divergence; it does not silently widen scope
- `return-to-current-policy` means the subject should move back toward current standing policy, but any bind, byte, or authority changes still require the appropriate stronger review when relevant
- `keep-without-expiry` removes the ordinary timer only with an explicit acknowledgement receipt; it is not the default result of ignoring the queue
- `overdue` does not mean `auto-reverted`; it means `review is now required or strongly urged`

## Batch rule

A batch containing `due-soon`, `overdue`, and `blocked` rows must split before apply.
The product may allow one renewal batch for homogeneous safe renewals, but it must separate:

- rows that can renew under the same divergence terms
- rows that need stronger review to return to current policy
- rows that only permit `keep without expiry` with stronger acknowledgement
- rows that are blocked by missing current evidence

## Why this matters

Without this contract, intentional divergence stops being deliberate state and starts becoming background folklore.
The product then recreates exactly the kind of `approved once`, `keep as-is`, or `it was grandfathered long ago` memory burden that this archive is trying to replace.

## Relationship to trust freshness

Exception aging is about intentional non-current subjects.
It is not the same thing as remembered approval freshness.
A subject may carry no intentional exception at all while the remembered trust that would otherwise have lowered friction for a new arrival has become `cooling`, `stale`, or `frozen`.
That separate lifecycle is defined in `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`.
