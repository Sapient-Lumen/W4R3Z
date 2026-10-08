# Route evidence page — observed path, protocol, window, and switch witness interface spec

## Purpose

The archive already had live measurement and incident-timeline doctrine.
What it still lacked was one fixed page for another ordinary question:

> what route was actually observed, from what witnesses, across what window, and how stable was that route claim?

AnonSync should therefore add a dedicated **route evidence page** before any route statement is promoted into diagnosis, performance explanation, or policy-mismatch language.

## Core decision

A route statement must never be promoted from one icon, one peer row, or one anecdote.
The page exists to publish the actual observed route class, the witness basis, and the freshness window.

## Fixed review order

1. **Observed pair or cohort**
2. **Current effective path**
3. **Witness basis**
4. **Window and stability**
5. **Route-switch candidates**

## 1) Observed pair or cohort

Show the exact peer pair, uploader cohort, or route segment under observation.
A route statement without explicit subject coverage is invalid.

## 2) Current effective path

Publish at least these fields:

- direct / relayed / unresolved / mixed-by-window
- protocol row or transport witness
- local-vs-remote segment class
- current success/failure state
- confidence grade

The page must distinguish `currently relayed`, `previously relayed`, and `relay merely allowed`.

## 3) Witness basis

List the concrete witnesses used, such as:

- peer-list relay icon
- performance-table protocol row
- timed observation from live session
- benchmark or controlled run note
- support/debug evidence if available
- operator assertion only

Each witness gets one status:

- `strong current witness`
- `useful but stale`
- `indirect clue`
- `contradicted`

## 4) Window and stability

Publish:

- observation start / end
- whether the route remained stable through the window
- whether the route is only a point-in-time glimpse
- whether the route changed during the incident window
- strongest safe sentence from that window

The page must make short windows look short.

## 5) Route-switch candidates

Highlight any plausible route switches and their evidence status, for example:

- direct became relayed after firewall/NAT change
- tracker unavailable then restored
- predefined host path superseded tracker-discovered path
- mixed NIC routing produced unstable path class
- relay icon disappeared but no stable direct window yet

Each switch candidate gets one status:

- `observed`
- `plausible`
- `not supported`

## Compact rendering obligations

Any compact route-evidence card must still preserve:

- observed pair/cohort
- current route verdict
- evidence window
- witness strength
- route-switch status

## Anti-clone rule

Do not clone workflows where a current relay icon or protocol row silently becomes the story for the whole incident window.
