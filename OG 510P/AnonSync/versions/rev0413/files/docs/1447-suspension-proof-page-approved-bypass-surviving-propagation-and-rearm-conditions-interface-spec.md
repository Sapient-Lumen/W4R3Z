# Suspension proof page: approved bypass, surviving propagation, and re-arm conditions interface spec

## Purpose

Once a stop-like override is approved, the archive needs one explicit page for the next question:

> what exactly was armed, what evidence proves the bypass really took effect, what propagation still survived, and what must happen before we can claim the original guardrail is back?

## Core decision

AnonSync must expose one first-class **Suspension proof** whenever a control bypass, pause, detachment, or temporary narrowing is armed or resumed.

## Fixed page order

1. **Proof header**
2. **Arm-evidence card**
3. **Surviving-propagation card**
4. **Expiry and extension card**
5. **Re-arm proof card**
6. **Proof sentence**

### 1) Proof header

Show:

- suspension id
- arm time
- arm owner
- active scope
- arm verdict
- expiry class
- current bypass truth
- resulting trust state of underlying control

Supported `arm_verdict` values:

- `armed-as-designed`
- `armed-but-weaker-than-requested`
- `armed-with-surviving-side-effects`
- `inconclusive-arm-state`
- `resume-completed-awaiting-attestation`

### 2) Arm-evidence card

Required rows:

- surface or mechanism used to arm
- direct evidence the bypass is active
- evidence that lower-cost alternative was not chosen instead
- missing evidence if any
- observers and timestamps

Supported `arm_evidence_class` values:

- `ui-state-change`
- `environment-gate-triggered`
- `topology-state-changed`
- `peer-update-revoked`
- `scheduled-window-entered`
- `system-priority-change`

Hard rule:

A badge change alone cannot prove a deeper topological or network stop unless the product says that is all it is claiming.

### 3) Surviving-propagation card

Required rows:

- propagation still occurring
- propagation definitively blocked
- ambiguous effects still under watch
- impact on queued work
- impact on detection / indexing / metadata
- impact on related peers or lanes

Supported `surviving_propagation_verdict` values:

- `deletes-survive`
- `indexing-survives`
- `uploads-survive`
- `future-updates-revoked`
- `peer-discovery-blocked`
- `new-work-deferred-until-resume`
- `resume-may-create-new-path`
- `placeholder-only-local-state-remains`

### 4) Expiry and extension card

Required rows:

- expiry deadline or window end
- who may extend
- max allowed extension class
- alert path on missed expiry
- what sentence auto-withdraws if extension is not approved

Supported `max_allowed_extension_class` values:

- `none-hard-stop`
- `single-review-extension`
- `rolling-reviewed-extension`
- `maintenance-window-bound`
- `environment-condition-bound`

### 5) Re-arm proof card

Required rows:

- how resume happens
- what evidence proves resume happened
- whether trust restoration is automatic or pending
- next required attestation
- reopened case / rollout / control if resume fails

Hard rule:

`resumed` may not imply `trusted again` unless the original control contract explicitly allows that weaker claim.

### 6) Proof sentence

The page must end with one sentence in this shape:

> `Suspension <id> is <arm verdict> across <scope>; while active, <surviving propagation> remains true, and after resume the control still requires <re-arm proof or attestation> before <stronger sentence> returns.`
