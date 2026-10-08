# Line-split migration watch page — v2/v3 linked-cohort conflict and Business block

## Purpose

This page exists because `compatible` is too weak a word when product lines diverge in entitlement logic.
The operator question is:

> can these seats exchange bytes, can they safely remain linked as one identity family, and is this upgrade lane actually supported for this entitlement class?

## Core decision

Any upgrade or link action that crosses a line-family boundary with known entitlement differences must open one dedicated **Line-split migration watch** page.

## Fixed page order

1. cohort headline
2. byte-compatibility vs topology-compatibility card
3. blocked entitlement lanes card
4. Business hard-stop card
5. staged migration ladder
6. migration proof summary

### 1) Cohort headline

Show:

- current cohort members
- version / line family mix
- whether they are linked, merely sharing, or both
- strongest safe summary

### 2) Byte-compatibility vs topology-compatibility card

Publish:

- whether byte sync remains compatible
- whether linked-identity topology remains safe
- whether license conflicts are documented for this mix
- whether UI/share configuration continuity is at risk

### 3) Blocked entitlement lanes card

Show:

- which line families may upgrade
- which may not
- whether the block is advisory, unsupported, or destructive-risk
- whether a personal/non-commercial lane exists where a business lane does not

### 4) Business hard-stop card

If Business is in scope, publish:

- current Business status
- v3 support verdict
- strongest blocked sentence
- likely survivor boundary if the operator ignores the block

### 5) Staged migration ladder

Offer only reviewed ladders such as:

- `upgrade all linked personal seats together`
- `unlink and split cohort before crossing line family`
- `keep Business cohort on v2`
- `replace product line, then rebuild governance explicitly`

### 6) Migration proof summary

Show what the product can honestly claim now:

- `safe byte compatibility only`
- `safe linked-cohort migration`
- `blocked due to line-family conflict`
- `blocked due to unsupported Business path`

## Rules

### Rule 1 — compatibility claims are two-part claims

The page must never let `protocol compatible` imply `safe to stay linked`.

### Rule 2 — Business block stays loud

An unsupported Business→v3 path may not hide behind normal upgrade UI.

### Rule 3 — mixed linked cohorts need explicit warning language

If official docs warn of license conflicts or lost UI/share configuration, that warning belongs on the page, not in support prose.

## Acceptance criteria

A later operator can:

- tell whether the cohort is only byte-compatible or truly migration-safe
- tell whether Business is hard-blocked
- tell whether linked identity must be split before migration
- reopen the right receipt proving why the upgrade was allowed or blocked