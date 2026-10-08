# Subject workspace and review stack interface spec

## Purpose

This document decides the fixed anatomy for subject pages.
The goal is not to make every page visually identical.
The goal is:

> every major subject page should answer the same class of operator questions in the same broad order.

That order is part of the safety model.

## Subject families covered here

The workspace grammar applies to at least:

- shares
- members / peers / contacts
- incoming share claims
- path bindings
- policies and member-policy views
- active exceptions and temporary overrides
- reports and review objects
- offers and capability artifacts
- releases / state-root transitions when rendered as review subjects

## Fixed workspace anatomy

Every substantial subject page should render these zones in this order.

### 1) Summary header

Must show:

- subject label
- stable handle or copy-safe ID
- high-signal chips
- last-change or freshness summary
- active lane / attention posture if any

This is the answer to `what am I looking at?`

### 2) Current answer strip

One sentence answering the page's dominant question.
Examples:

- `Visible here, not yet claimed, target path is non-empty, reconciliation review required before bind.`
- `This member is inheriting baseline discovery policy, but an active route lease temporarily widens direct known-host use until 18:00.`
- `This share is settled enough for backup, not yet settled enough for destructive re-home.`

This is the answer to `what is true right now?`

### 3) Truth cards

These are the cards needed to understand ordinary state before mutation.
Depending on subject, they may cover:

- materialization
- authority / seat / grant posture
- publication / arrival posture
- path / binding posture
- convergence or settlement posture
- preservation posture
- active exception / lease posture

This is the answer to `what are the important dimensions of truth here?`

### 4) Difference cards

Every page that can diverge from a baseline, template, expectation, or previous reviewed plan should show a focused difference zone.
Possible comparisons include:

- baseline vs effective
- expected vs observed
- before vs after draft
- source path vs target path
- current policy vs proposed policy

This is the answer to `what differs and why should I care?`

### 5) Action stack

The page should list actions in safety order:

1. safest next action
2. meaningful secondary actions
3. information-gathering actions
4. danger actions in their own separated region

This is the answer to `what should I do next from this exact page?`

### 6) Proof stack / drawer

Proof is not a hidden appendix.
The page should expose a stable proof region for:

- preflight
- comparison
- preservation
- convergence
- settlement
- exposure
- authority delta
- plan drift

This is the answer to `why should I believe the current answer and the suggested next action?`

### 7) Timeline and receipts

Recent subject history should appear as condensed timeline events with jumps to full receipts or audit records.
The timeline should say:

- what changed
- whether it changed trust, bytes, or presentation only
- which proof or plan it referenced

This is the answer to `how did we get here?`

### 8) Danger zone

Destructive or trust-expanding actions must sit apart from ordinary work.
They should not compete visually with the default next action.

This is the answer to `what remains possible but deserves stronger caution?`

## Review stack rules

### Rule 1 — explanation before override

If the page has enough evidence to explain a surprising state, it should surface that explanation before showing a risky override button.
The interface should not teach `act first, understand later`.

### Rule 2 — differences before mutation

If the action would change a baseline, bind into a non-empty path, widen reachability, or reuse prior approval, the page should show the relevant difference cards before the mutation control.

### Rule 3 — proof freshness must travel with the action

A proof drawer that says `stale` should downgrade or block the related apply action nearby.
The operator should not need to remember freshness from another page.

### Rule 4 — danger actions remain visible but separate

A page should not hide all danger actions behind obscure menus.
But it should make them obviously separate from the primary action.

## Compare mode

Some subject pages need a true compare layout.
When two columns are used, the order should stay stable:

- left = current / incumbent / local / baseline side
- right = incoming / candidate / proposed / target side

The page should not flip that ordering opportunistically.
Stable left/right meaning reduces operator mistakes.

## Page-local tabs are allowed, but not page-local semantics

Tabs such as `Overview`, `Differences`, `History`, or `Receipts` are acceptable.
What is not acceptable is changing the meaning of the page skeleton itself.
For example, one page should not place danger actions above truth cards just because its designer preferred a denser layout.

## Result

A good subject workspace should let the operator answer, from any major page:

1. what this subject is
2. what is true right now
3. what differs from the relevant baseline or expectation
4. what proof supports that answer
5. what the safest next action is
6. what dangerous actions remain available
7. how the subject got here

If the operator has to hunt across tabs, drawers, or unrelated pages for those answers, the workspace grammar is too loose.
