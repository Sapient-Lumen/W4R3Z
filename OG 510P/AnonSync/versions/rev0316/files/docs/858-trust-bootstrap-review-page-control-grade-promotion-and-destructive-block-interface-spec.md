# Trust bootstrap review page — control-grade promotion and destructive-action block interface spec

## Purpose

The archive already has control-trust, endpoint attestation, and danger-surface exposure doctrine.
What it still lacked was the page that ties trust bootstrap directly to destructive authority.

This page exists to answer:

> if the current dangerous browser/control session is still on bootstrap trust, what exactly is blocked, what trust promotion paths exist, and what must be re-proved before destructive approval can continue?

## Core decision

AnonSync must expose one first-class **Trust bootstrap review** page whenever a dangerous action is approached from a control session whose trust grade is:

- `bootstrap trust exception`
- `unknown`
- `degraded`

Hard decision:

> **bootstrap trust exception is never sufficient for destructive commit.**

Observation and non-destructive review may continue.
Destructive approval and destructive execution stay blocked until trust is promoted or the action is handed to a stronger control path.

## Fixed page order

1. **Current endpoint and block verdict**
2. **Why destructive approval is blocked**
3. **Trust promotion paths**
4. **Consequences and reproof requirements**
5. **Continuation path**

### 1) Current endpoint and block verdict

Show:

- `trust_bootstrap_review_page_id`
- endpoint watermark
- acting seat
- current control modality
- current trust grade
- block verdict (`review-only`, `promotion-required`, `handoff-required`, `unknown-endpoint-stop`)
- strongest honest summary

This is the answer to:

> what control path am I on, and why is destructive commit blocked here?

### 2) Why destructive approval is blocked

Show structured blocker rows such as:

- endpoint attribution incomplete
- bootstrap exception still active
- transport grade too weak for destructive commit
- browser residue / certificate exception still in effect
- current page reached by weaker route than policy allows

Each blocker row must include:

- blocker class
- current proof
- stronger proof needed
- whether observation may continue meanwhile

### 3) Trust promotion paths

Allowed promotion paths may include:

- `pin this local endpoint`
- `accept reviewed self-issued trust`
- `switch to managed trust`
- `move to stronger local control path`
- `handoff destructive action to another actor or surface`

Each path must state:

- resulting trust grade
- restart or reconnect cost
- whether endpoint re-attestation is required
- whether existing dangerous-session objects survive or must be reissued

### 4) Consequences and reproof requirements

Show:

- whether capsule/rail survive intact
- whether basis freshness resets
- whether approval barrier must be regenerated
- whether salvage export receipts remain valid
- whether a new destructive execution ticket will later be required

The operator must be able to answer:

> if I strengthen trust now, what must be reviewed again afterward?

### 5) Continuation path

Controls may include:

- `Promote trust now`
- `Open safer control path`
- `Continue review without destructive approval`
- `Cancel dangerous action`

A successful promotion must continue into:

- endpoint re-attestation if needed
- refreshed destructive review shell
- regenerated approval barrier if basis changed

## Copy rule

Forbidden durable copy:

- `trust warning is expected, continue anyway`
- `unsafe is okay for local repair`
- `same browser session so approval can continue`

Allowed durable copy:

- `bootstrap trust exception still active; destructive approval remains blocked`
- `observation may continue, but approval must move to reviewed trust`
- `trust promotion changes the control grade and requires refreshed destructive approval`

## Public object

### Trust bootstrap review page

Fields:

- `trust_bootstrap_review_page_id`
- `endpoint_ref`
- `acting_seat_ref`
- `current_trust_grade`
- `blocker_rows[]`
- `promotion_path_rows[]`
- `reproof_rows[]`
- `current_danger_session_capsule_ref`
- `continuation_controls[]`
- `generated_at`
