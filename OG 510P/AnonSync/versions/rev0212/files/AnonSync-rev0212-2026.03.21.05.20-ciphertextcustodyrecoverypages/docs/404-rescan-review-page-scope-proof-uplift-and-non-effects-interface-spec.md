# Rescan review page — scope, proof uplift, and non-effects interface spec

## Purpose

The archive already treats rescan as real operational work.
What it still lacked was one public page for the ordinary question:

> if I run a rescan now, what exactly will it examine, what confidence will it improve, and what will it definitely not fix?

Current official Resilio docs make this seam concrete.
They still say scheduled rescan checks mtime and size, then rehashes if change is detected, that rescans can be periodic, manual, or startup-triggered, and that generic troubleshooting still leans on restart or even `touch` ritual when notifications are weak.
That is operational truth.
It deserves one review page.

## Core decision

AnonSync must expose one first-class **Rescan review** page before and after any non-trivial manual rescan, and as the explanation surface for scheduled/startup rescans when they materially affect freshness claims.

## Fixed page order

1. **Trigger and scope**
2. **Expected proof uplift**
3. **Known non-effects**
4. **Cost and interruption profile**
5. **Receipt**

### 1) Trigger and scope

Show:

- `rescan_review_page_id`
- trigger kind (`manual`, `scheduled`, `startup`)
- scope (`subject`, `bind`, `subtree`, `all-subjects`)
- why this rescan is being proposed or why it ran
- whether it is compensating for a known detection downgrade

### 2) Expected proof uplift

Show exactly what may improve:

- local name enumeration
- mtime/size refresh
- candidate hashing work
- late discovery of locally changed files
- stale placeholder / path-family reconciliation
- stronger freshness basis claim after completion

The operator must be able to answer:

> what kind of uncertainty will this rescan actually reduce?

### 3) Known non-effects

This section is mandatory.
It should explicitly state what rescan will **not** fix, such as:

- missing permissions
- absent source peers / absent byte witnesses
- blocked path portability or unsupported entries
- authority / approval / grant issues
- already-corrupt hidden state
- remote fetch or landing work that has not happened yet

The product must never treat `Rescan` as a generic repair verb.

### 4) Cost and interruption profile

Show:

- expected disk / CPU / metadata pressure
- whether hashing amplification is likely
- whether multiple shares may scan in parallel
- whether the action is compatible with current quiet-host posture
- whether current workloads make this safe now or better deferred

### 5) Receipt

The receipt must preserve:

- trigger kind
- scope
- evidence before rescan
- evidence after rescan
- uplift classes achieved
- promised non-effects that indeed remained non-effects

## Public object

### Rescan review page

Fields:

- `rescan_review_page_id`
- `subject_ref`
- `scope_class`
- `trigger_kind`
- `reason_rows[]`
- `expected_uplifts[]`
- `known_non_effects[]`
- `cost_rows[]`
- `receipt_ref` nullable
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. trigger kind
3. expected uplift
4. strongest non-effect
5. apply affordance

Example:

```text
Projects/video     manual     refresh local discovery proof     will not fix absent source peers     Review and run
```
