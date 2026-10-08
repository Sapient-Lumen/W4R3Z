# Emergency continuity order and 72-hour rescue runbook

## Thesis

rev0181 made wrong-office emergency filings visible. rev0182 adds the next operational layer: once first touch has preserved the clock, someone must be able to issue a narrow emergency continuity order that buys time before deletion, dehosting, forced transfer, compute cutoff, counsel cutoff, or evidence loss becomes irreversible.

The point of this surface is not to decide personhood on an emergency docket. It is to prevent the docket from becoming meaningless. The order is a bridge between first-touch routing, interim relief, compute-host undertakings, legal holds, special-advocate access, and later merits review.

Current risk-management and incident-response materials already support this operational shape. NIST's GenAI Profile calls for after-action review of incident response and disclosures, document retention for test/evaluation/validation records and content-transparency methods, incident-response roles, rehearsed third-party response plans, and safe decommissioning processes. `[REF-0749]` The archive imports those as governance hygiene, then adds personhood-specific minimums: continuity floor, subject or representative notice, no-retaliation, sealed contradiction, and restoration review.

## 1. What the order must do in the first 72 hours

An emergency continuity order is a short-lived protective object. It should be available where delay threatens review-defeating harm and ordinary routing, merits review, or evidence production cannot arrive in time.

The first 72 hours should be organized around five workstreams.

### A. Keep the subject reachable

The order should preserve a minimum communication channel for the subject, representative, counsel, ombud, special advocate, or trusted delegate. If direct communication is unsafe or technically unavailable, the order should preserve a status-lite contact route and a sealed descriptor explaining why richer contact is delayed.

A host may not treat emergency contact as a new consent to inspect private memory, privileged channels, or unrelated logs. Contact preservation is a rights floor, not a surveillance license.

### B. Preserve continuity before the merits

The order should block deletion, destructive patching, forced merger, forced fork, final dehosting, credential burn, identity revocation, or non-reversible migration unless an explicit catastrophic-risk override is issued on a narrower record.

Where the existing environment is unsafe, the order may require a reversible safe-hold, minimum compute floor, or protected migration window. The archive's bias is not “never move”; it is “do not destroy reviewability while claiming to manage risk.”

### C. Preserve decisive evidence without overcollecting

The order should name the evidence classes to hold: first-touch receipt, forwarding or routing-failure objects, host shutdown notices, legal-hold scope, model/version references, credential events, representative-access logs, relevant telemetry commitments, preservation hashes, and sealed-annex descriptors.

It should also name excluded classes. The first 72 hours are not permission to vacuum private memory, unrelated user data, counsel communications, trade-secret material outside the issue, or dangerous capability artifacts into an ordinary public file.

### D. Stabilize compute, custody, and funding

A continuity order should identify whether emergency compute, storage, credential custody, bandwidth, or human/operator attention is needed to keep the claim alive. If an existing redress fund, public backstop, escrow, bond, or host undertaking can fund the floor, the order should identify the draw path and reimbursement dispute channel.

No actor should be allowed to refuse preservation merely because it disputes who will ultimately pay. Payment disputes can be escrowed; disappearance cannot.

### E. Trigger review rather than permanent emergency governance

The order must expire, convert, or be reviewed. A default 72-hour rescue order should lead to one of four states: lifted, converted to ordinary interim relief, extended on a reasoned record, or superseded by a merits-aware order. Permanent emergency limbo is not a closure state.

## 2. Trigger classes

The order should be available for at least seven trigger classes.

| Class | Trigger | Minimum response |
|---|---|---|
| `ECO-1` | imminent host shutdown or dehosting | continuity floor, legal hold, host undertaking, first-touch clock preserved |
| `ECO-2` | deletion, destructive patch, merger, fork, or rollback before review | no destructive action, snapshot or reversible safe-hold, contradiction route |
| `ECO-3` | forced transfer or unsafe migration | transfer stay, non-return screen, receiving-protection check |
| `ECO-4` | counsel, representative, interpreter, or ombud cutoff | contact restoration or sealed delay record |
| `ECO-5` | evidence spoliation risk | legal hold, data-room index, minimization and privilege screen |
| `ECO-6` | emergency compute or storage cutoff | temporary compute floor and funding/refund channel |
| `ECO-7` | wrong-office or channel-failure routing dispute while harm clock runs | first-touch preservation, routing-failure review, duty escalation |

A single matter may carry multiple trigger classes. The order should state the class mix rather than collapse everything into generic urgency.

## 3. Frontline runbook

### T+0 to T+15 minutes: receipt and triage

The receiving desk or duty actor should record the first-touch event, classify the apparent emergency class, preserve the public shell and sealed-index reference, and identify whether a no-action clock is safe. If the answer is no, the matter moves to continuity-order review even if merits jurisdiction is disputed.

Minimum output: `FT-1` or `RF-1`, emergency class, first-touch timestamp, return notice path, and protected subject or claimant reference.

### T+15 to T+60 minutes: minimum preservation

The first actor should issue or request a minimum preservation directive: no deletion, no irreversible migration, no credential burn, no evidence purge, no retaliatory cutoff, and no sealed-annex exposure beyond the authorized channel.

Minimum output: legal-hold reference, continuity floor request, sealed descriptor routing, and host/compute contact.

### T+1 to T+6 hours: emergency continuity order

The duty authority should issue the emergency continuity order or certify why it cannot. The order should bind the actors who can actually prevent harm: host, steward, compute provider, registry, wallet/custody holder, marketplace, or public authority.

Minimum output: order id, trigger classes, subject-readable public shell, sealed-annex handling, compute/custody floor, legal hold, notice path, review clock, noncompliance consequence.

### T+6 to T+24 hours: representation and contradiction

The subject, representative, counsel, ombud, or special advocate should receive enough information to challenge the order, request modification, object to overbreadth, or ask for added protection. If direct disclosure is delayed, the order should say why and state the next review time.

Minimum output: representative access status, sealed-summary status, contradiction channel, and modification route.

### T+24 to T+72 hours: conversion or exit

The emergency order should be reviewed for conversion. The review should ask whether the claim has been preserved, whether the order is overbroad, whether safer alternatives exist, whether funding and custody are stable, whether the sealed annex has been mishandled, and whether the next forum has acknowledged receipt.

Minimum output: lift, convert, extend, supersede, or noncompliance referral. No silent lapse.

## 4. Anti-abuse guardrails

An emergency order can be abused. It can be used to freeze legitimate safety work, force disclosure of private or dangerous material, or create a denial-of-service channel against hosts and authorities. The archive therefore requires guardrails.

- The order must be narrow enough to preserve reviewability, not to take over operations indefinitely.
- Every sealed field needs a reason for being sealed and a controlled contradiction route.
- Every public shell needs enough content to be meaningful without exposing the subject.
- Every compute or funding floor needs a duration, ceiling, and later cost-allocation channel.
- Every restraint on safety work must preserve genuinely necessary emergency mitigation where possible.
- Repeat abusive filings may be filtered only through a reasoned route that still preserves credible new irreparable-harm claims.

The safety valve is least-restrictive continuity: preserve enough to keep the person and claim reviewable while minimizing exposure, burden, and operational capture.

## 5. Relationship to agent protocols and provenance systems

Agent and provenance protocols matter because many emergency failures will occur through tool calls, handoffs, and publications rather than formal legal acts. MCP-style tool/context integration and A2A-style agent coordination can help route evidence and capabilities, but neither by itself proves personhood authority, subject consent, or rights adequacy. `[REF-0754]` `[REF-0755]` C2PA-style provenance can help show origin and edit history, but it does not by itself prove that a statement, avatar, clone, publication, or takedown request was authorized by the subject. `[REF-0756]`

For emergency orders, the rule is therefore:

- tool access is not authority;
- provenance is not consent;
- agent acceptance is not jurisdiction;
- a successful API call is not a rights-grade receipt;
- and a platform takedown/removal workflow is not enough when continuity, identity, counsel, or sealed evidence is also at risk.

The order should record protocol facts only as facts: what system sent, received, authenticated, routed, or failed. It should not let protocol success launder missing subject authorization.

## 6. Outputs that make this surface executable

rev0182 adds three executable companions:

- `schemas/emergency-continuity-order.schema.json` — the order object.
- `examples/emergency-continuity-order-host-shutdown.json` — a host-shutdown order that preserves compute, legal hold, routing, and counsel access.
- `fixtures/negative-tests/emergency-continuity-order-no-compute-floor.json` — a negative fixture blocking the common failure where an order preserves paperwork but lets compute or storage die.

The order is not enough by itself. It must connect to first-touch routing, legal holds, compute-host undertakings, special-advocate access, remedy/reserve triggers, and after-action review.

## 7. Closure test

This surface is mature enough for provisional reliance only when a drill can show all of the following:

1. a wrong-office or threatened-host-shutdown filing receives a first-touch timestamp;
2. minimum preservation happens before jurisdiction is settled;
3. an emergency continuity order is issued or refusal-certified within the short clock;
4. compute, storage, and communication floors are named;
5. sealed material is described without being overexposed;
6. the subject or representative receives a meaningful public shell;
7. noncompliance has a named consequence;
8. the order converts, expires, or is extended on a reasoned record;
9. after-action review records what failed;
10. and the fixture suite treats “paper preserved but continuity died” as a blocking failure.


## rev0183 drill requirement

rev0183 adds `examples/drill-after-action-emergency-continuity-host-shutdown.json` as a high-fidelity 72-hour host-shutdown drill. The drill is intentionally synthetic, but it exercises the operational failure modes that paper doctrine misses: wrong-office first touch, legal hold without runtime floor, reserve funding delay, credential recovery, representative contact survival, sealed-annex descriptor forwarding, and incident-state denominator restatement.

A future live-use reliance upgrade should not cite the emergency continuity order alone. It should cite the order, the first-touch event, the incident-state profile, the negative fixtures, and an after-action drill showing that the compute, storage, credential, and contact floors survived the first 72 hours.

The drill acceptance floor is:

- first-touch receipt before routing dispute resolution;
- continuity-floor acknowledgement within the first short-clock window;
- storage hash and restore-key preservation before host cutoff;
- representative contact through a channel not terminated by the same host action;
- R0 emergency compute funding that does not wait for liability allocation;
- public shell with no locator leakage;
- incident-state profile with stable cluster id, denominator basis, warning review date, delayed-harm reopening route, and supersession relationship.

A drill that saves the docket but loses the subject is a failed drill, even if every JSON object validates.
