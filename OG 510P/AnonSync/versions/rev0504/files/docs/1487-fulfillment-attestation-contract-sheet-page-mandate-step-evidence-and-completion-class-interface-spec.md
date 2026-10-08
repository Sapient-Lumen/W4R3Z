# Fulfillment attestation contract sheet page: mandate, step, evidence, and completion class interface spec

## Purpose

After the archive learned how to issue a bounded action mandate, it still needed one ordinary page for the next operator question:

> the delegate says the work is done — done in what sense, against which mandate, with what evidence, and with what unfinished remainder still attached?

## Core decision

AnonSync must expose one first-class **Fulfillment attestation contract sheet** whenever a delegate, operator, automation lane, or successor returns a claim that issued work is complete, partially complete, blocked, or superseded.

## Fixed page order

1. **Return header**
2. **Mandate linkage card**
3. **Claimed completion card**
4. **Evidence bundle card**
5. **Residual-duty card**
6. **Decision sentence**

### 1) Return header

Show:

- fulfillment attestation id
- source mandate id
- assignee / execution lane
- return time
- current review status
- strongest currently safe sentence
- latest superseding attestation id if any

Supported `review_status` values:

- `drafting`
- `returned-pending-review`
- `returned-needs-more-evidence`
- `accepted-complete`
- `accepted-partial`
- `accepted-blocked-remainder`
- `disputed`
- `superseded`
- `withdrawn`

Hard rule:

A mandate does not become complete merely because the assignee marked it done locally.
The review status must stay visible until a reviewer accepts, disputes, or supersedes the claim.

### 2) Mandate linkage card

Required rows:

- source mandate title
- requested outcome
- specific step / sub-scope this return covers
- authority lane that executed it
- world / subject scope touched
- preconditions that were or were not met

Hard rule:

A return may not claim to cover the full mandate unless it names the exact mandate scope and explicitly states whether any portion was intentionally not attempted.

### 3) Claimed completion card

Required rows:

- claimed completion class
- assignee sentence
- requested stronger sentence
- unsafe overclaim to suppress
- side effects introduced
- known blocked remainder

Supported `claimed_completion_class` values:

- `attempted-no-effect-proven`
- `attempted-effect-observed`
- `partial-complete`
- `complete-self-claimed`
- `complete-with-evidence`
- `complete-but-side-effected`
- `blocked`
- `not-attempted-because-invalidated`

Hard rule:

`done` is not a valid stored class.
The assignee must choose a typed completion class.

### 4) Evidence bundle card

Required rows:

- inline evidence summary
- linked run / case / certificate objects
- screenshots or logs attached
- live observation included
- freshness of evidence
- missing witness that blocks stronger acceptance

Supported `freshness_class` values:

- `live-now`
- `same-window`
- `recent-but-not-live`
- `historical-only`
- `unknown`

Hard rule:

Evidence that only proves activity happened may be attached, but it must be labeled weaker than evidence that proves requested scope and effect.

### 5) Residual-duty card

Required rows:

- residual work remaining
- residual risk remaining
- who owns the remainder
- next required action
- next forbidden overclaim
- reopen trigger tied to this return

Supported `residual_duty_class` values:

- `none`
- `cleanup-still-required`
- `observe-window-still-required`
- `peer-confirmation-still-required`
- `requester-acceptance-still-required`
- `follow-on-mandate-required`
- `case-reopen-still-possible`

Hard rule:

A return that leaves any material residual duty may not be rendered as full completion.

### 6) Decision sentence

Render one sentence only:

- `This return claims [class] for [scope], is currently [review_status], and still blocks the stronger sentence that [overclaim].`

## Required interactions

- **Request more evidence**
- **Accept exact scope only**
- **Accept partial and split remainder**
- **Dispute overclaim**
- **Supersede with newer return**
- **Spawn follow-on mandate**

## Empty and failure states

If no evidence exists yet, show:

- `Return received, but no attached witness yet.`

If the return references a canceled or superseded mandate, show:

- `Return cannot close the original mandate because the source authority changed.`
