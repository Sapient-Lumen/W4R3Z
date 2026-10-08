# Authoring delay page: file-class policy origin, live countdown, and release boundary interface spec

## Purpose

The archive already had generic delay and queue language.
What it still lacked was one exact page for the operator question:

> what delay policy is active for this file class, where did it come from, and when will this item actually be released?

Current official Resilio docs make this seam concrete.
They still expose authoring delay through `FileDelayConfig` in the storage folder, with JSON edits and restart semantics.
That is candid.
It should not be the primary product contract.

## Core decision

AnonSync must expose one first-class **Authoring delay** page whenever publication delay can be applied by file class, subject policy, or temporary operator hold.

The page exists to answer four things in one place:

1. which delay rule currently applies
2. where that rule came from
3. whether the countdown is live or still being extended by new writes
4. what changes if the operator edits or bypasses the delay

## Fixed page order

1. **Current delay verdict**
2. **Effective delay register**
3. **Live countdown lane**
4. **Origin and precedence**
5. **Bypass / shorten / extend review**
6. **Receipts**

### 1) Current delay verdict

Show:

- `authoring_delay_page_id`
- artifact or subject in scope
- current `delay_verdict` (`no-delay`, `delay-active`, `delay-expired`, `delay-extended-by-new-write`, `override-active`, `unknown`)
- strongest honest summary
- next release estimate

### 2) Effective delay register

List active rules with:

- matcher or file class
- delay duration
- rationale class (`authoring-safety`, `batching`, `manual-hold`, `temporary-throttle`)
- current source (`global-default`, `subject-override`, `artifact-override`, `temporary-review`)
- whether restart is required for policy mutation

### 3) Live countdown lane

For each pending artifact show:

- artifact ref
- first detected write
- most recent write
- release-at time
- whether the timer is currently stable
- extension reason if not stable

### 4) Origin and precedence

Show:

- which rule won
- which lower-precedence rules are shadowed
- whether the current value is inherited or frozen locally
- whether returning to `none` restores inheritance or merely clears the local override value

This section exists because current Resilio docs still let `manually set back to None` behave differently from true inheritance recovery for download priority, and AnonSync should keep similar precedence edges visible rather than surprising.

### 5) Bypass / shorten / extend review

Allowed actions may include:

- `Keep current delay`
- `Shorten once`
- `Skip for this artifact`
- `Create temporary hold`
- `Edit inherited rule`
- `Freeze local override`

Each row must show:

- scope touched
- whether currently waiting artifacts are affected
- whether restart is required
- authoring / chronology risk
- rollback availability

### 6) Receipts

Store durable receipts for:

- rule edits
- override creation or removal
- one-time bypasses
- timer expiry transitions
- forced release decisions

## Public object

Fields:

- `authoring_delay_page_id`
- `scope_ref`
- `delay_verdict`
- `delay_rule_rows[]`
- `countdown_rows[]`
- `precedence_rows[]`
- `action_rows[]`
- `receipt_rows[]`
- `generated_at`

## Non-goals

This page does **not** replace lock investigation or transfer-priority explanation.
It proves only **which delay policy currently applies, where it came from, when release becomes honest, and what a bypass would cost**.
