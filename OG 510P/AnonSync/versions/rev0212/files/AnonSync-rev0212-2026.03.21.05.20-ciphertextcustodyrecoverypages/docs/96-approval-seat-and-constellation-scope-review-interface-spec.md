# Approval-seat and constellation-scope review interface spec

## Purpose

The archive already says that constellations, approvals, and member authority are separate facts.
What still remained too easy to blur was the live approval moment itself:

- a peer or share request arrives
- one current machine is about to speak for some authority seat
- that decision may affect only this share, or also future shares
- the operator may be approving as one reviewed member, not as an undifferentiated personal blob

Resilio's current docs still keep that seam too implicit.
They say linked devices make all folders visible across the linked set, all linked devices act as Owners for the user's own shares, a remote user can automatically approve all linked devices for future sharing after approving one, and a pending request can be approved from any linked device where the folder is already active.
That is useful convenience.
It is not yet one trustworthy explanation of **which seat is speaking**, **how far the approval travels**, or **what future auto-approval memory was just created**.

This document fixes that gap.

## Core rule

An approval is always spoken from a reviewed seat.

A reviewed seat is not the same thing as a whole constellation.

A per-share approval is not the same thing as a future approval memory.

The interface should therefore keep four facts adjacent whenever approval is offered:

1. `Requested subject`
2. `Acting seat`
3. `Approval horizon`
4. `Receipt promise`

Any surface that collapses those back into one cheerful `Approve` button has already started to recreate the Resilio seam we are explicitly rejecting.

## Stable approval line

Every approval-worthy request should be classifiable along one durable line:

1. **Pending** — request exists, no seat has accepted it yet
2. **Prepared for review** — one candidate seat and scope are being compared, but not yet applied
3. **Approved for this subject only** — acceptance is bounded to the current share/subject
4. **Approved for bounded future scope** — acceptance also creates future auto-approval memory inside a reviewed boundary
5. **Denied** — request refused, no positive authority granted
6. **Withdrawn / stale** — request no longer actionable because subject, authority, or source posture changed

The product must not pretend states 3 and 4 are the same.
`Approved now` and `approved for future requests too` are materially different outcomes.

## Approval queue row contract

A reviewed approval queue should exist so incoming requests can be triaged without pretending every available member speaks with the same horizon.

Every queue row should answer, in one stable order:

1. **Requested subject** — who wants what
2. **Candidate acting seat** — which member/device would be the approving seat if applied now
3. **Current horizon** — this subject only, named members only, reviewed future scope, or none yet
4. **Next honest action** — review, approve once, deny, or escalate scope review
5. **Overflow / scope details** — secondary actions and scope consequences

### Example rows

```text
Maya → Photos-2026        Seat: Laptop-Admin   No future scope        Review            Details
Printer-NAS → Scans       Seat: Studio-Node    This subject only      Approve once      Details
Phone-Backup → Archive    Seat: Travel-Laptop  Wider future scope     Continue review   Details
Unknown peer → Finance    No safe seat         Blocked pending review Deny / inspect    Details
```

The important part is that the row says **which seat is about to speak and how far that speech travels**.
It must not imply that any linked member may approve with identical consequences.

## Review-pane contract

When the operator opens a pending approval or a prepared approval review, the pane should preserve one fixed section order:

1. **Requested approval action**
2. **Acting seat and present authority**
3. **Approval horizon and blast radius**
4. **Share / constellation fallout**
5. **Admissible actions**
6. **Receipt promise**

### 1) Requested approval action

This section should say:

- who or what is requesting access
- which share, offer, contact edge, or subject is in play
- requested role or permission
- whether the current action is `approve-once`, `approve-bounded-future`, `deny`, `keep-pending`, or `escalate`

### 2) Acting seat and present authority

This section should say:

- which current member/device is the proposed acting seat
- why that seat is currently eligible to approve
- whether a different seat would have different authority or a narrower horizon
- whether the current seat is really acting as `self-only`, `share steward`, `constellation admin`, or some more limited reviewed role

The operator must be able to answer: **which seat is actually speaking right now?**

### 3) Approval horizon and blast radius

This section should say:

- whether the approval reaches only this request or also future requests
- whether any future memory is limited to this subject, a share class, named members, or a reviewed constellation scope
- whether the requested action would create standing approval memory
- whether sibling members inherit any effect now

The operator must be able to answer: **how far does this approval travel today, and what future shortcut does it create?**

### 4) Share / constellation fallout

This section should say:

- whether the action changes one share only or also the operator's wider constellation posture
- whether the approval broadens re-share, write, or successor posture
- whether the action touches only one current member or alters future behavior for other members too
- whether mixed-version or mixed-class constellation findings make the wider scope unsafe

The operator must be able to answer: **is this a one-share decision, or am I changing the future authority story of the constellation?**

### 5) Admissible actions

This section should say:

- whether the honest next step is `Approve once`, `Approve for reviewed scope`, `Keep pending`, `Deny`, or `Open broader review`
- which shortcuts are forbidden because they would hide seat or scope changes
- whether a safer narrower approval is available from the same pane
- what follow-up remains if the operator defers broader scope

The operator must be able to answer: **what can I safely do now without accidentally widening future authority?**

### 6) Receipt promise

This section should say:

- which receipt proves the approval or denial outcome
- whether the receipt proves only this subject acceptance or also a new future-approval memory
- which acting seat, horizon, and policy governed the decision
- what future expiration, review, or revocation remains open

The operator must be able to answer: **what later evidence will prove who spoke, for what scope, and with what horizon?**

## Allowed primary verbs

### Good primary verbs

- `Approve once`
- `Approve for reviewed scope`
- `Choose narrower seat`
- `Keep pending`
- `Deny request`
- `Escalate scope review`

### Dangerous ambiguous verbs

- `Approve`
- `Trust my devices`
- `Always approve`
- `Approve everywhere`
- `Remember this`

The archive does not ban those words in prose.
It bans them as the primary operator contract when they blur acting seat or blast radius.

## Seat-selection rules

A serious approval surface may offer more than one eligible acting seat, but it must make the differences legible.

Every candidate seat should display:

- member label and class
- current authority posture on the subject
- maximum approval horizon available from that seat
- constellation or compatibility findings that narrow or block it

### Example seat chooser

```text
Laptop-Admin     personal       may approve this share only       Safe narrower choice
Studio-Server    appliance      may not create future approval    Safer but limited
Travel-Phone     personal-lite  blocked: mixed release posture    Not admissible
```

The product must never imply that choosing one seat over another is only a cosmetic runtime preference.

## Batch rules

Approval queues may support batching, but only if the labels stay truthful.

### Acceptable labels

- `Approve 3 once`
- `Deny 2 requests`
- `Continue review for 4 wider-scope requests`

### Unacceptable labels

- `Approve selected`
- `Trust all`
- `Always allow from my devices`

A batch bar may not speak for a wider future scope than every selected row actually shares.

## Dense and mobile rules

A dense row or mobile card may compress wording, but it must still preserve three cues:

- which seat is speaking
- whether the horizon is current-only or future-reaching
- whether the safe verb is direct approval, denial, or broader review

`Seat: Laptop · once only · Approve once` is acceptable compression.
`Approve` is not.

## CLI contract

Minimal commands:

```text
anonsync approval queue
anonsync approval show aprq_01J...
anonsync approval review prepare aprq_01J... --seat mem_laptop --scope this-subject --plan
anonsync approval review prepare aprq_01J... --seat mem_laptop --scope reviewed-future:photos-collab --plan
anonsync approval review show aprv_01J...
anonsync approval approve aprv_01J...
anonsync approval deny aprq_01J...
anonsync approval receipt show aprc_01J...
```

These commands should answer:

- what is pending
- which seat is being asked to speak
- whether the horizon is current-only or future-reaching
- what narrower alternative remains available
- which receipt later proves the chosen scope

## Workbench contract

The workbench should expose an `Approvals` queue distinct from `Peers`, `Constellation`, and `Incoming shares`.
Its job is not merely to list requests.
Its job is to answer:

- what the request is
- which seat is being asked to approve it
- how far approval would travel
- whether a narrower safer approval is available
- what receipt will later prove the seat and scope

The queue should support:

- filtering by candidate seat, scope horizon, share, and blocker class
- opening one fixed review drawer that preserves the section order above
- switching seats inside review without losing sight of changed blast radius
- preparing a narrower approval from the same surface without forcing a different hidden wizard

## Report-language integration

The shared report language should support at least these families here:

- `approval-seat` — which current member is speaking and why
- `approval-horizon` — how far current or future approval would travel
- `approval-scope-risk` — why a wider scope is guarded, blocked, or requires fuller review

These reports should behave like any other report-backed finding: severity, freshness, scope, and safest next action remain explicit.

## Design tests

The model is not explicit enough if any of the following remains true:

- the operator can still approve a request without seeing which seat is speaking
- `Approve once` and `Approve for future requests` still share one primary button
- dense/mobile clients compress away the horizon and leave only a generic `Approve`
- a wider auto-approval memory can be created without a receipt proving which seat and policy created it
- switching seats changes scope silently instead of visibly
