# Corroboration and conflict review page: independent support, duplicates, and unresolved mismatch interface spec

## Purpose

The operator needs one review page that answers:

> which sources truly reinforce each other, which only look additive, which conflict, and what is the exact cost of leaving a mismatch unresolved?

## Core decision

AnonSync must expose one first-class **Corroboration and conflict review** whenever a synthesis set contains two or more active sources.

## Fixed page order

1. **Review header**
2. **Independent-support section**
3. **Duplicate-and-restatement section**
4. **Conflict section**
5. **Discount-and-holdout section**
6. **Synthesis consequence section**
7. **Review sentence**

### 1) Review header

Show:

- target synthesis id
- active source count
- independent-support count
- duplicate/restatement count
- open conflict count
- current merged-claim ceiling

### 2) Independent-support section

For each source cluster judged genuinely independent, show:

- cluster id
- participating source ids
- independence basis
- question slice supported
- ceiling gained by this corroboration

Supported `independence_basis` values:

- `different-capture-channel`
- `different-observer-plane`
- `different-runtime-world`
- `different-time-window-same-conclusion`
- `different-measurement-method`
- `explicitly-not-independent`

Hard rule:

Two packets produced by the same underlying channel with only superficial reformatting must not be labeled as independent.

### 3) Duplicate-and-restatement section

For each duplicate or downstream restatement cluster, show:

- cluster id
- source ids
- common root observation
- why these do not add independence
- whether any one source is still retained as the canonical representative

Supported `duplicate_class` values:

- `same-packet-new-format`
- `same-event-new-view`
- `ui-restates-log`
- `history-restates-status`
- `summary-restates-raw`
- `unknown-possible-duplicate`

Hard rule:

A cluster marked `unknown-possible-duplicate` may not be counted toward strong corroboration.

### 4) Conflict section

For each material contradiction, show:

- conflict id
- source ids in tension
- exact propositions in conflict
- severity
- leading interpretations still live
- cheapest discriminator that would reduce this conflict
- current claim ceiling while unresolved

Supported `conflict_resolution_posture` values:

- `needs-no-action`
- `needs-cheap-discriminator`
- `needs-heavy-capture`
- `needs-route-reversal`
- `must-cap-claim-until-later`

Hard rule:

If the conflict is `route-reversing` or `world-invalidating`, the interface must publish at least one surviving alternative interpretation, not only the currently favored one.

### 5) Discount-and-holdout section

List sources that are not in the active weighted basis.
Required rows:

- source id
- holdout reason
- whether it still shadows the claim
- re-entry trigger

Supported `holdout_reason` values:

- `stale-window`
- `wrong-world`
- `wrong-scope`
- `duplicate-not-needed`
- `conflict-not-resolved`
- `inferior-version`
- `transform-too-lossy`

Hard rule:

A held-out source that still shadows the claim must continue to cap the stronger sentence until formally cleared or superseded.

### 6) Synthesis consequence section

Required rows:

- claim strengthened by independent support
- claim still capped by conflict
- sentence that would become safe if the cheapest discriminator landed
- sentence that remains impossible even after that discriminator

Hard rule:

The review must separate `claim could strengthen` from `claim has strengthened`.

### 7) Review sentence

Render exactly three lines:

- **What is genuinely corroborated**
- **What is merely repeated**
- **What still conflicts and what sentence that conflict blocks**
