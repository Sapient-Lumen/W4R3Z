# Touch repair page: mtime cause proof and propagation risk interface spec

## Purpose

The archive already had rescan and repair ladders.
What it still lacked was one exact page for the smaller but dangerous operator question:

> should I manually nudge this artifact's freshness signal, and if I do, am I rediscovering real bytes or inventing a newer chronology claim?

Current official Resilio docs make this seam concrete.
They still openly suggest `touch` when mtime or size was not updated or not noticed.
That is useful.
It should not arrive only as a shell-command how-to.

## Core decision

AnonSync must expose one first-class **Touch repair** page whenever a manual freshness nudge, metadata-only restamp, or equivalent synthetic rediscovery action is available.

The page exists to answer five things in one place:

1. whether manual touch is actually indicated
2. what evidence suggests detection missed a real change
3. what alternative repair is less distorting
4. what chronology claim a touch would create
5. what peers would observe after apply

## Fixed page order

1. **Repair verdict**
2. **Evidence for missed change**
3. **Counterfactual repairs**
4. **Propagation and chronology review**
5. **Apply gate and receipt**

### 1) Repair verdict

Show:

- `touch_repair_page_id`
- artifact in scope
- current `repair_verdict` (`not-needed`, `likely-correct`, `possible-but-weak`, `wrong-repair`, `dangerous-unreviewed`)
- strongest honest summary
- last evaluated time

### 2) Evidence for missed change

Show the strongest facts supporting a touch recommendation, such as:

- content changed but no new publication event exists
- detection source is degraded or absent
- mtime or size stayed unchanged despite operator-confirmed edits
- lock or writer state previously suppressed publication
- alternate proof such as rescan still failed

The page must separate **proof of missed detection** from mere impatience.

### 3) Counterfactual repairs

Before offering touch, show alternatives and why they rank higher or lower:

- `Wait for current delay`
- `Run rescan`
- `Reopen or close writer cleanly`
- `Clear lock and retry`
- `Fetch fresher remote copy`
- `Touch local artifact`

Each row must say:

- what signal it changes
- whether bytes change or only freshness evidence changes
- whether it can still produce the intended publication outcome
- which risk it avoids or introduces

### 4) Propagation and chronology review

Show:

- whether touch would claim `this local copy is newer`
- whether peers might archive or overwrite another version because of that claim
- whether the current peer is the correct authority to advance chronology
- whether the operator has inspected the most recent peer evidence

### 5) Apply gate and receipt

The actual apply gate must require:

- explicit acknowledgement of chronology effect
- operator rationale
- preview of expected peer-visible outcome
- durable receipt containing pre-action evidence

Receipt fields should include:

- actor
- artifact
- prior detection state
- chosen repair
- chronology warning shown
- resulting publication outcome when later known

## Public object

Fields:

- `touch_repair_page_id`
- `artifact_ref`
- `repair_verdict`
- `evidence_rows[]`
- `counterfactual_rows[]`
- `propagation_review`
- `apply_gate`
- `receipt_rows[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. artifact
2. repair verdict
3. strongest supporting evidence
4. safer alternative if any
5. propagation risk chip

Example:

```text
jira.txt     likely-correct     editor saved without mtime change; rescan still saw no update     rescan already exhausted     medium chronology risk
```

## Non-goals

This page does **not** replace long-form conflict review or archive-restore review.
It proves only **whether a manual freshness nudge is justified, what less-distorting repairs exist, and what chronology claim the action would assert**.
