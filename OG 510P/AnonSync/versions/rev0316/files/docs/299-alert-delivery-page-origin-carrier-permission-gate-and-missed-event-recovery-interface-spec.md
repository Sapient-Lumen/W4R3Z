# Alert delivery page — origin, carrier, permission gate, and missed-event recovery interface spec

## Purpose

The archive already has attention lanes and notification parity language.
What it still lacked was one ordinary page for a more practical operator question:

> for this event on this seat, could the system really have told me, through which carrier, and where could that delivery have been suppressed or lost?

This page exists so `notifications on` does not impersonate a real delivery guarantee.

## Core rule

Alert delivery is a pipeline, not a toggle.
The product must distinguish at least:

- event origin
- chosen carrier
- local/UI-only fallback
- OS/browser/permission gate
- suppression, mute, or miss-recovery state

If the operator still has to inspect preferences, OS permissions, platform caveats, and event history separately to know whether an alert could have reached them, the page is not explicit enough.

## Fixed review order

Every serious alert-delivery page should render the same sections in the same order:

1. **Effective delivery verdict**
2. **Origin and carrier matrix**
3. **Gates, suppressors, and misses**
4. **Recovery and escalation paths**
5. **Receipts and history**

### 1) Effective delivery verdict

This section should answer:

- which seat, surface, and event family are under review
- whether the current posture is `reliably delivered`, `local-only`, `carrier-gated`, `suppressed`, `missed-but-recoverable`, or `undeliverable`
- whether the verdict is host-wide or event-family-specific
- whether the product is relying on in-product polling/history rather than ambient alerts

The operator must be able to answer: **could this event really have reached me in time?**

### 2) Origin and carrier matrix

This section should have stable rows for:

- approval request
- destructive-risk warning
- connectivity/degradation warning
- transfer completion or failure
- review item due/overdue

For each row the page should show:

- `origin`
- `allowed carriers` (in-app, local-web banner, desktop system notification, mobile push, etc.)
- `currently active carrier`
- `delivery grade`
- `fallback if carrier absent`

The operator must be able to answer: **what carrier was supposed to carry this event?**

### 3) Gates, suppressors, and misses

This section should show:

- local preference mute/scope rules
- OS/browser permission gates
- platform limitations such as UI-only or no-background delivery
- session/cookie/login dependence where relevant
- whether the event expired, was coalesced, or remained only in history/review shelf

The operator must be able to answer: **where exactly could delivery have been blocked or degraded?**

### 4) Recovery and escalation paths

This section should show:

- where the missed event can still be seen
- whether acknowledgment or approval can still be acted on safely
- whether the event should be reissued or escalated
- how to strengthen delivery for the future

The operator must be able to answer: **I may have missed it — what is the clean recovery path now?**

### 5) Receipts and history

This section should show:

- delivery attempts and outcomes
- suppressor changes
- permission-grant receipts
- recovered or reissued event receipts

The operator must be able to answer: **what proof explains why the alert did or did not reach me?**

## States

Use a small stable vocabulary:

- `reliably delivered`
- `local-only`
- `carrier-gated`
- `suppressed`
- `missed-but-recoverable`
- `undeliverable`

## Main surface

A compact **Alert delivery** card should show:

- delivery verdict
- current carrier
- strongest gate or suppressor
- strongest recovery action

## Key prohibitions

The product must not:

- use one generic bell icon as the whole explanation of alert reachability
- let `notifications enabled` imply push/system delivery when only in-product history exists
- hide platform-specific impossibility behind the same cheerful wording used for reliable carriers
- make the operator dig through event history just to learn that delivery was never possible here
