# Maintenance transition plan page — entry trigger, drain behavior, and counterpart requirements interface spec

## Purpose

A maintenance contract is not operational until the product owns how the hold begins.
Some holds should start immediately.
Some should let in-flight work drain first.
Some only become honest after counterpart acknowledgement.
This page exists to stop `enter maintenance` from collapsing all of those paths into one button.

## Core decision

AnonSync must expose one first-class **Maintenance transition plan** page whenever a maintenance hold has non-trivial entry conditions, drain behavior, or counterpart dependencies.

The page exists to answer five things in one place:

1. what event actually starts the hold
2. whether in-flight work drains, cancels, or keeps running
3. what counterpart or cohort proof is required
4. what temporary risk exists during entry
5. what receipt proves the hold was entered honestly

## Fixed page order

1. **Entry verdict**
2. **Entry trigger and timing**
3. **Drain / cutover behavior**
4. **Counterpart dependencies and temporary risk**
5. **Actions and receipts**

### 1) Entry verdict

Show:

- `maintenance_transition_plan_page_id`
- scope
- chosen hold class
- current entry class (`immediate`, `drain-first`, `ack-required`, `staged`, `not-ready`)
- strongest honest summary
- next irreversible step

The operator must be able to answer:

> how does this hold actually begin?

### 2) Entry trigger and timing

Show:

- triggering event (`manual now`, `scheduled window`, `counterpart quorum`, `queue empty`, `receipt successor`)
- earliest honest entry time
- latest desired entry time
- pre-entry checks still missing
- whether earlier entry would silently weaken the claim

The interface must answer:

> what exact event makes the hold active rather than merely requested?

### 3) Drain / cutover behavior

This section is mandatory.
Show rows for:

- current in-flight transfers
- queued transfers not yet started
- pending deletes or rename propagation
- already-accepted remote changes
- backlog released after exit
- residual activity allowed during drain

Each row must show whether it will:

- `finish before hold`
- `stop at entry`
- `remain visible but not claim-bearing`
- `carry into successor receipt`
- `unknown`

The operator must be able to answer:

> what is allowed to finish, what is cut off, and what debt survives into the hold?

### 4) Counterpart dependencies and temporary risk

Show:

- required counterpart seats or cohorts
- acknowledgement status
- uncovered seats
- temporary exposure during the drain/cutover window
- whether destructive motion is still possible before full entry
- strongest safe sentence during entry versus after entry

The page must answer:

> what could still go wrong before the hold is honestly in force?

### 5) Actions and receipts

Actions may include:

- `Enter now`
- `Wait for drain`
- `Wait for counterpart`
- `Widen scope`
- `Narrow claim`
- `Open receipt preview`

Receipts must record entry class, trigger, drain behavior, counterpart coverage, and temporary-risk boundary.

## Public object

### Maintenance transition plan page

Fields:

- `maintenance_transition_plan_page_id`
- `scope_ref`
- `hold_class`
- `entry_class`
- `entry_trigger`
- `timing_rows[]`
- `drain_rows[]`
- `counterpart_dependency_rows[]`
- `temporary_risk_rows[]`
- `strongest_safe_sentence_during_entry`
- `strongest_safe_sentence_after_entry`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. entry class
3. decisive blocker or trigger
4. strongest temporary risk
5. next action

Example:

```text
Project Alpha     drain-first     wait for in-flight uploader to finish     deletes still possible until counterpart match     Wait for counterpart
```

## Non-goals

This page does **not** prove the hold stayed intact after entry.
It proves only the reviewed **entry trigger, drain behavior, and temporary-risk boundary**.
