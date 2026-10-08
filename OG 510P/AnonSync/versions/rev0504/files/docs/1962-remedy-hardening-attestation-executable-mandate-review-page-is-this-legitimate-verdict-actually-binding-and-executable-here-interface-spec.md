# Remedy-hardening-attestation executable-mandate review page — is this legitimate verdict actually binding and executable here?

## Purpose

This page is the operator-facing review that answers the practical execution question after verdict legitimacy is already good enough: given the current legitimate verdict, who must now act, through which route, by when, and what is the strongest execution sentence the product may honestly publish?

## Primary review prompts

The review must answer these prompts in order:

1. **What verdict is now supposed to become action?**
2. **Who is actually bound by that verdict here?**
3. **Which action or state change is required from each bound actor?**
4. **Which actuator or route can execute it in this world and topology?**
5. **Which manual steps, restarts, reconnects, or replacement moves still remain?**
6. **What is the strongest execution sentence the product may honestly say now?**

## Review sections

### 1. Binding-scope board

Show:

- source verdict-legitimacy receipt
- mandate issuer
- actor classes bound
- actor classes explicitly not bound

### 2. Action-and-deadline board

Show:

- required action set
- deadline or execution window
- whether the action is advisory, mandatory, or fallback-triggered

### 3. Route-and-actuator board

Show:

- primary actuator class
- whether the route is automatic, manual, restart-gated, reconnect-gated, or replacement-style
- whether a fallback route exists already

### 4. Execution-witness board

Show:

- what evidence would count as execution
- what evidence would count as execution failure
- what evidence only proves named-slice completion

### 5. Execution-ceiling board

The review must output one and only one primary sentence class such as:

- legitimate verdict, advisory only
- mandate draft pending issuance
- mandate issued, binding scope ambiguous
- mandate issued for named cohort only
- mandate issued, primary actuator unavailable
- mandate issued, execution pending within deadline
- deadline missed, fallback required
- fallback route governing
- partially executed for named slice only
- execution complete for named slice
- broader stronger sentence blocked

## Hard rules

The review must never let an operator hide:

- a legitimate verdict behind `someone will handle it`
- an automatic-looking lane behind unstated manual procedures
- a restart or reconnect dependency behind `already executed`
- a named-slice completion behind estate-wide completion wording
- a fallback trigger behind `the primary route is still fine`
