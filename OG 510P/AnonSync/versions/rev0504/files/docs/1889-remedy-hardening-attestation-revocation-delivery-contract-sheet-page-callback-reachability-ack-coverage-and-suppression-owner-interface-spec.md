# Remedy-hardening-attestation-revocation-delivery contract sheet page — callback reachability, acknowledgement coverage, and suppression owner

## Purpose

This page is the operator's compact contract for a ruling whose downstream reliance graph already exists and now needs an explicit answer to whether the corrective wave actually reached the dependents, whether reachable dependents acknowledged, whether stale derivative surfaces were suppressed, and who still owns closure when some dependents remain unreachable or unverifiable.
It exists so the product can distinguish `revocation wave opened` from `delivery happened, acknowledgement happened where required, stale surfaces were suppressed, and the remaining residual risk is honestly named`.

## Core fields

- case identifier
- source reliance receipt identifier
- source revocation-wave identifier
- current governing receipt identifier
- current source sentence status
- current delivery-governance class
- current stale-surface class
- freeze-new-reliance flag
- reachable dependent count
- unreachable dependent count
- delivery-confirmed count
- acknowledgement-required count
- acknowledgement-received count
- successor-binding-required count
- successor-binding-complete count
- stale artifact count
- stale artifact suppressed count
- external stale artifact count
- disconnected-or-return-risk count
- unknown callback path risk grade
- last delivery attempt time
- last acknowledgement time
- oldest unsuppressed stale surface time
- closure threshold class
- delivery owner class
- acknowledgement owner class
- suppression owner class
- escalation owner class
- strongest blocked all-clear sentence
- strongest blocked historical-only-everywhere sentence
- next evidence that upgrades closure confidence
- next evidence that forces escalation now

## Delivery-governance classes

The page must model at least these distinct classes:

- revocation required, callback paths incomplete
- callback paths known, delivery not yet attempted
- delivery attempted, confirmation incomplete
- delivered to reachable cohort, acknowledgement pending
- delivered and acknowledged, suppression incomplete
- suppression complete for named cohort, external closure still open
- successor-bound and suppressed for required cohort
- residual-live-surface debt preserved, escalation active
- downstream-safe restored for named cohort only
- global downstream-safe sentence blocked

## Dependent classes

The page must support at least these consumer or stale-surface classes:

- internal automation with callback path
- external automation with callback path
- human decision maker
- dashboard or status surface
- exported file or packet
- downstream receipt quoting the source
- policy or template derived from the source
- disconnected or pending lane that may later return
- externally mirrored artifact without callback path

## Required distinctions

The page must keep these truths separate:

- registry known versus callback path known
- delivery attempted versus delivery confirmed
- delivery confirmed versus acknowledgement received
- acknowledgement received versus stale artifact suppressed
- successor receipt issued versus successor receipt bound by the dependent
- stale local residue versus publicly live stale surface
- named-cohort closure versus global closure
- historical-only source for one audience versus historical-only source everywhere

## Layout

The page should be organized into seven zones:

### 1) Governing correction rail

Always print:

- the current governing receipt
- whether new reliance is frozen
- the strongest blocked all-clear sentence
- the strongest blocked `historical only everywhere` sentence
- the exact reason each stronger sentence is blocked

### 2) Reachability rail

Show a table with at least these columns:

- dependent identifier
- dependent class
- callback path class
- last reachable time
- last confirmed delivery time
- acknowledgement requirement
- acknowledgement status
- successor-binding requirement
- stale-surface status
- current escalation status

The page must never collapse `registered`, `reachable`, `delivered`, `acknowledged`, and `suppressed` into one badge.

### 3) Delivery coverage rail

Show coverage as a ladder, not a binary:

- revocation required
- callback known
- delivery attempted
- delivery confirmed for reachable cohort
- acknowledgement complete for required cohort
- stale surfaces suppressed for named cohort
- closure threshold met
- global closure proven

The active rung must be highlighted and each blocked rung must show the exact missing evidence.

### 4) Residual-live-surface rail

Show why broad closure may still be blocked:

- unreachable dependent with prior observed consumption
- disconnected or pending lane may later reconnect
- exported copy lacks callback path
- dashboard or publication still visible
- downstream receipt still quoting superseded source
- archive or local residue not yet evaluated
- clone or fresh-instance ambiguity
- evidence horizon expired before confirmation

### 5) Closure obligations rail

Show every active obligation with status:

- deliver corrective notice
- obtain acknowledgement
- bind successor receipt
- hide or retract stale surface
- revalidate dependent decision
- reseal downstream receipt
- escalate unreachable dependent
- declare residual risk preserved
- close wave only after threshold is met

Status values must include:

- not started
- in progress
- blocked
- confirmed
- waived by policy
- unverifiable

### 6) Ownership rail

Show exactly who owns each action class:

- callback-path owner
- delivery owner
- acknowledgement owner
- stale-surface suppression owner
- successor-binding owner
- escalation owner
- final closure approver

### 7) Actions rail

The page must support explicit actions such as:

- attach callback evidence
- issue delivery attempt
- record confirmation
- request acknowledgement
- bind successor receipt
- mark stale surface hidden
- mark artifact retracted
- escalate unreachable dependent
- preserve residual-live-surface debt
- close named-cohort wave

## Operator promises

The contract sheet must let the operator say things like:

- `all registered internal automations were delivered the correction, but one external export remains live without callback proof`
- `delivery is confirmed for the reachable cohort, yet acknowledgement remains incomplete for two human decision makers`
- `the source is historical only for internal consumers, not yet for external consumers`
- `named-cohort closure is complete, but global downstream-safe language remains blocked because one disconnected lane may later return`

## Hard decisions frozen by this page

This interface family makes these product decisions explicit:

- no broad `everyone got the correction` sentence without callback and delivery basis
- no `downstream safe again` sentence while any unsuppressed stale surface remains live
- no `historical only everywhere` sentence while any dependent still lacks confirmed successor binding or suppression
- no passive notification substitute for closure when the old source still appears on live downstream surfaces
