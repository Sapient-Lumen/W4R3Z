# Router-side-effect warning page: network-equipment risk, scope, and safer alternative ladder interface spec

## Purpose

Some dangerous choices are not dangerous because they destroy bytes.
They are dangerous because they mutate infrastructure the operator may not fully own or may not expect to disturb.
This page exists to answer:

> what collateral network risk comes with requesting automatic port mapping here, and what less-invasive alternatives still achieve enough reachability?

## Core decision

Whenever the product can request automatic router mutation, it must own one first-class **Router-side-effect warning** page.

The page owns:

- infrastructure mutation warning
- affected scope hypothesis
- compatibility confidence
- less-invasive alternatives
- approval text

## Fixed page order

1. warning headline
2. affected-scope card
3. compatibility-confidence card
4. safer-alternative ladder
5. approval rail

### 1) Warning headline

State plainly:

- this action may ask the network edge to create or refresh a port mapping
- the request is outside ordinary file / subject state
- collateral device or service impact is possible

### 2) Affected-scope card

Show:

- likely network scope (`home router`, `office router`, `mobile hotspot`, `unknown shared network`, `unsupported`)
- whether the operator appears to control that scope
- whether shared-network caution should block one-click apply

### 3) Compatibility-confidence card

Render one of:

- `no compatibility evidence`
- `previously succeeded here`
- `previously degraded or problematic`
- `current environment changed since last success`
- `unsupported / unknown network edge`

### 4) Safer-alternative ladder

Offer least-strong alternatives in order, such as:

- keep helper/relay dependence
- use predefined hosts without automatic mapping
- perform manual forwarding with explicit external admin review
- remain LAN-scoped
- cancel

### 5) Approval rail

Require explicit acknowledgement text for any apply path that can request router mutation.

## Rules

### Rule 1 — collateral infrastructure risk is not hidden under performance language

The page must name the mutation as infrastructure-facing.

### Rule 2 — shared-network environments require stronger friction

If the operator may not own the network edge, the surface must tighten approval and safer alternatives.

### Rule 3 — alternatives are semantic, not merely technical

Each alternative must say what directness / helper / exposure claim it still does or does not earn.

## Acceptance criteria

A later operator can:

- tell why the action was considered infrastructure-facing
- tell what scope might be affected
- tell whether compatibility confidence was absent, positive, stale, or negative
- tell what less-invasive alternatives existed
- tell what explicit acknowledgement was accepted
