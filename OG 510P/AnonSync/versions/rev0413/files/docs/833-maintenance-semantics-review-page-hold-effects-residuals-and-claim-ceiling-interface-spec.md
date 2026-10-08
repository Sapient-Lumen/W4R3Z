# Maintenance semantics review page — hold effects, residuals, and claim ceiling interface spec

## Purpose

A chosen maintenance class is still too abstract unless the product shows what that class means for actual motion.
This page exists to prevent the classic lie:

> we said `pause`, so everyone now knows what that means.

Current official Resilio docs make the need concrete by spreading semantics across pause, scheduler, read-only, and backup articles.
AnonSync must gather those semantics into one reviewed matrix.

## Core decision

AnonSync must expose one first-class **Maintenance semantics review** page before a maintenance hold can be described as safe, quiet, frozen, preserved, or one-way.

The page exists to answer five things in one place:

1. what the chosen hold class blocks
2. what it still allows
3. which allowed residuals weaken the maintenance claim
4. what exact sentence is still safe
5. what stronger sentence must remain forbidden

## Fixed page order

1. **Chosen class and claim ceiling**
2. **Effects matrix**
3. **Residuals and risk-bearing allowances**
4. **Safe language review**
5. **Actions and receipts**

### 1) Chosen class and claim ceiling

Show:

- `maintenance_semantics_review_page_id`
- chosen `hold_class`
- source of choice (`operator`, `policy`, `template`, `incident successor`)
- current claim ceiling (`local only`, `cohort matched`, `destructive-safe`, `preserve-only`, `unknown`)
- strongest honest summary

The operator must be able to answer:

> what sentence is this hold actually strong enough to support?

### 2) Effects matrix

Show one row per motion class:

- uploads
- downloads
- delete propagation
- rename/move propagation
- local edit writeback
- remote edit landing
- indexing / rescan
- visibility-only state changes
- backlog growth
- backlog release debt

Each row must show:

- `blocked`
- `allowed`
- `allowed with caveat`
- `depends on counterpart`
- `unknown`

This is the authoritative page for:

> what does this maintenance class really do to each kind of motion?

### 3) Residuals and risk-bearing allowances

This section is mandatory whenever any row is not simply `blocked`.
Show:

- residuals that are allowed by design
- residuals that are tolerated but operationally risky
- destructive residuals that make a stronger maintenance sentence false
- residuals that are outside scope rather than inside the hold
- whether a residual is only visible, or claim-bearing

The operator must be able to answer:

> which surviving motion is harmless, and which surviving motion means I picked the wrong hold class?

### 4) Safe language review

Show two columns:

- allowed phrases
- forbidden stronger phrases

Examples:

- allowed: `byte transfer is held locally`
- forbidden: `nothing can change`
- allowed: `this seat will not write back`
- forbidden: `the dataset is frozen everywhere`
- allowed: `preservation semantics apply on this endpoint`
- forbidden: `ordinary two-way sync is paused`

This section exists so the claim ceiling becomes durable rather than remembered.

### 5) Actions and receipts

Actions may include:

- `Accept semantics`
- `Choose stricter class`
- `Choose weaker cheaper class`
- `Request counterpart match`
- `Open transition plan`
- `Abort hold`

Receipts must record the semantics matrix, residuals, and safe-language ceiling.

## Public object

### Maintenance semantics review page

Fields:

- `maintenance_semantics_review_page_id`
- `scope_ref`
- `hold_class`
- `choice_source`
- `effect_rows[]`
- `residual_rows[]`
- `claim_ceiling`
- `allowed_phrase_rows[]`
- `forbidden_phrase_rows[]`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. hold class
2. strongest allowed phrase
3. strongest risky residual
4. claim ceiling
5. next action

Example:

```text
drain-then-hold     in-flight work may finish then hold     remote deletes still unresolved     local only     Request counterpart match
```

## Non-goals

This page does **not** choose the transition steps.
It proves only the reviewed **maintenance semantics and claim ceiling**.
