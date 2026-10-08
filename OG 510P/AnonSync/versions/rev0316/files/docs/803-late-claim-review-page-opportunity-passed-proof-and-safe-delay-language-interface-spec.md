# Late-claim review page — opportunity-passed proof and safe-delay language interface spec

## Purpose

The archive already had freshness review and observation coverage.
What it still lacked was the review page for the human sentence that operators actually reach for:

> is it honest to call this late yet, or has the seat simply not reached its next real chance to notice or act?

AnonSync should therefore expose a dedicated **late-claim review** page.
The product must not let `late`, `stuck`, `missed`, or `not syncing` appear as if they were one self-evident fact.

## Core decision

Every serious delay claim must be reviewed against the next observation opportunity before strong language is allowed.
The page must preserve five truths:

1. claim being tested
2. opportunity that should have satisfied it
3. proof that the opportunity happened or did not happen
4. remaining blockers or ambiguity
5. strongest safe sentence and stronger rejected sentence

## Fixed review order

1. **Claim under test**
2. **Opportunity that would satisfy the claim**
3. **Opportunity-passed proof**
4. **Alternative explanations still alive**
5. **Allowed and forbidden sentences**
6. **Next action**

## 1) Claim under test

Show the candidate claim explicitly, for example:

- `change should already have been noticed`
- `download should already have begun`
- `seat should already have published its local edit`
- `delay is now beyond current budget`

## 2) Opportunity that would satisfy the claim

Reference the concrete opportunity object:

- scheduled wake
- periodic rescan
- foreground return
- restored network eligibility
- healthy notification event
- source return

## 3) Opportunity-passed proof

Required proof classes:

- `passed with witness`
- `not yet passed`
- `supposedly passed but weak evidence`
- `cannot prove because blocker remained`
- `contradictory evidence present`

Evidence rows may include:

- wake event witnessed
- rescan completion witnessed
- runtime resumed in foreground
- source peer online during window
- network eligibility restored during window
- watcher coverage healthy during window

## 4) Alternative explanations still alive

Examples:

- seat never reached the scheduled wake
- seat woke but source stayed absent
- due time moved because posture changed again
- route or network remained ineligible
- observation happened but publication / fetch remained blocked elsewhere

## 5) Allowed and forbidden sentences

Required output forms include:

- `not late yet under current posture`
- `late only if current wake/rescan witness is accepted`
- `overdue under current posture`
- `cannot yet call late because prerequisite remained absent`

The page must also state a stronger rejected sentence, such as:

- `definitely stuck`
- `seat ignored the change`
- `background sync failed`

## 6) Next action

Examples:

- wait honestly
- perform reviewed manual rescan
- restore duty precondition
- verify source presence
- reopen freshness claim after posture drift
- escalate as genuinely overdue

## Compact rendering obligations

Any compact late-claim row must still preserve:

- candidate claim
- opportunity-passed proof class
- strongest safe sentence
- stronger rejected sentence
- next action

## Anti-clone rule

Do not clone workflows where `late` is inferred from elapsed wall-clock time alone while wake cadence, rescan cadence, source absence, or network policy still leave the opportunity itself unproven.
