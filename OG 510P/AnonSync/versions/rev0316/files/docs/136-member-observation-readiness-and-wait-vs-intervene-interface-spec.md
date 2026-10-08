# Member observation readiness and wait-vs-intervene interface spec

## Purpose

The archive now has:

- mutation ledgers with observation rows
- effective member policy explanation
- per-cell arrival causality explanation
- convergence windows with overdue classification

What still remained under-specified was the operator's next practical question:

> given this member and this unresolved gap, should I wait, re-announce, inspect route, repair local prerequisites, revise policy, or escalate?

Without one explicit decision sheet, the product still risks recreating the support-lore move it is trying to avoid.
The operator sees `not observed yet` and falls back to ritual: reconnect, toggle a default, retry a share, or tell themselves it will probably settle later.

This document defines the interface contract for **wait-vs-intervene** decisions.

## Core rule

Whenever a convergence window remains open and there is at least one materially different next action available, the product must be able to render one explicit **wait-vs-intervene decision sheet** that:

1. states the desired target state
2. summarizes why it has not happened yet
3. recommends exactly one strongest next move
4. names nearby moves that are available but not currently justified
5. records the evidence basis for that recommendation

The sheet is not a troubleshooting wizard.
It is a reviewed decision object derived from current public state.

## Why this needs its own spec

Current Resilio docs are helpful but distributed.
The operator may read one article saying sync starts immediately, another about trackers, another about relay servers, another about source peers being unavailable, and another about reconnect/custom-location recovery.
That is workable support material.
It is not the interface contract AnonSync wants.

AnonSync should compile that ambiguity into one disciplined verdict surface instead of asking the operator to improvise the next move.

## Public objects

### Wait-vs-intervene decision sheet

A synthesized decision object for one unresolved member-state gap.

Suggested fields:

- `wait_intervene_decision_sheet_id`
- `member_ref`
- `subject_ref` nullable
- `convergence_window_ref`
- `desired_target_summary`
- `current_gap_summary`
- `recommended_action` (`wait`, `re-announce`, `inspect-route`, `inspect-source`, `complete-local-review`, `revise-policy`, `supersession-clean-close`)
- `recommendation_reason`
- `blocked_actions[]`
- `alternative_actions[]`
- `generated_at`

### Action rationale row

One candidate action and the reason it is or is not currently justified.

Suggested fields:

- `action_rationale_row_id`
- `action_kind`
- `justification_state` (`recommended`, `allowed-but-not-needed`, `blocked`, `unsafe-under-current-evidence`)
- `reason_summary`
- `supporting_evidence_refs[]`

### Readiness blocker row

One blocker contributing to the current gap.

Suggested fields:

- `readiness_blocker_row_id`
- `blocker_kind` (`no-announcement`, `stale-liveness`, `route-failure`, `no-source-online`, `local-adoption-pending`, `policy-ineligible`, `superseded-target`)
- `severity` (`primary`, `secondary`, `context-only`)
- `summary`
- `clearing_action_kind` nullable

### Decision receipt

A durable exportable record of the recommendation rendered at one time.

Suggested fields:

- `decision_receipt_id`
- `wait_intervene_decision_sheet_ref`
- `actor_ref`
- `created_at`
- `recommended_action`
- `evidence_hash`

## Fixed inspection order

Every wait-vs-intervene surface should preserve this order:

1. **Desired state and current gap**
2. **Why the gap remains open**
3. **Recommended action now**
4. **Actions that are available but not justified**
5. **Actions blocked or unsafe under current evidence**
6. **What new evidence would change the recommendation**
7. **Receipt and follow-up boundary**

### 1) Desired state and current gap

This section should state plainly:

- which member and, when relevant, which subject are in view
- what target state the system is waiting for
- what current strongest convergence verdict applies
- whether the gap is sender-side, member-side, route-side, source-side, or policy-side

### 2) Why the gap remains open

This section should summarize the top blockers in operator language, for example:

- `member has not been observed recently enough`
- `announcement exists, but no eligible byte source is online`
- `member observed the subject, but local role-first adoption is unfinished`
- `current policy no longer wants the pending state`

### 3) Recommended action now

Exactly one strongest recommendation should appear.
Examples:

- `wait` — evidence still supports ordinary convergence without intervention
- `re-announce` — the cleanest next step is to refresh the member's awareness of the pending change
- `inspect-route` — route or liveness evidence is now the primary uncertainty
- `inspect-source` — the issue is source eligibility or byte availability, not publication truth
- `complete-local-review` — the member has seen the state, but local prerequisite work is unfinished
- `revise-policy` — the pending target no longer matches the current winning policy or eligibility story
- `supersession-clean-close` — a later mutation makes further intervention on this gap unnecessary

### 4) Actions that are available but not justified

This section should stop ritualized intervention by naming nearby moves and why they are not yet the best next step.
Examples:

- `Re-announce available, but not recommended because announcement freshness is still strong`
- `Inspect route available, but not recommended because recent liveness already rules out route as the primary blocker`

### 5) Actions blocked or unsafe under current evidence

This section is mandatory.
Examples:

- `Retry by changing member default mode` — blocked because standing-policy edits are not an honest fix for one unresolved cell
- `Withdraw and republish` — unsafe because the current issue is missing source bytes, not publication scope
- `Force bind to a new path` — blocked because the member has not yet accepted the role/path review

### 6) What new evidence would change the recommendation

Examples:

- fresh liveness proof would shift from `inspect-route` to `wait`
- a member observation receipt would shift from `re-announce` to `complete-local-review`
- source-availability confirmation would relax `inspect-source`
- policy supersession would collapse the gap into `clean close`

### 7) Receipt and follow-up boundary

Examples:

- `Record decision receipt`
- `Open route evidence`
- `Open member arrival review`
- `Open superseding mutation`
- `Recompute after new evidence`

## Public rules

### Rule 1 — recommendations compile from evidence, not habit

The product must not suggest reconnect-style or mode-toggle ritual unless the current evidence genuinely points there.

### Rule 2 — one strongest recommendation at a time

The page may show alternatives, but it must still name one current best move.

### Rule 3 — policy fixes and route fixes stay separate

The sheet must distinguish whether the gap exists because the desired target state is wrong, the route is weak, the source is absent, or local acceptance work is unfinished.

### Rule 4 — waiting can be an affirmative recommendation

`Wait` is not a non-answer when the evidence still supports ordinary convergence.
It should be presented as an explicit supported decision.

### Rule 5 — receipts record recommendation, not eternal truth

A decision receipt proves what the system recommended at one time from one evidence set.
It does not guarantee the same move remains best after later evidence.

## Dense row contract

A dense decision row should preserve these labels in this order:

- `Member/subject`
- `Desired state`
- `Gap now`
- `Recommended action`
- `Why`
- `Not justified`
- `Would change if`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one sheet:

- what target state the system is still waiting for
- why that target state has not yet been observed
- what one strongest next action is recommended now
- which nearby actions are possible but not currently justified
- which actions are blocked or unsafe under current evidence
- what new evidence would change the recommendation
