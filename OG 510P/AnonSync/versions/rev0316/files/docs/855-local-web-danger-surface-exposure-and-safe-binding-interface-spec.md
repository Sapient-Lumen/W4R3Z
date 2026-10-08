
# Local-web danger-surface exposure and safe-binding interface spec

## Purpose

AnonSync is local-web-first.
That means some of the most important pages may be opened in a browser against a local daemon, service, appliance, or remotely-reached control endpoint.
This document decides what danger pages must say about exposure and trust before the browser projection is allowed to feel ordinary.

## Core decision

A local-web danger page must always keep **endpoint**, **binding**, **auth**, **trust**, and **seat capability** adjacent to the destructive review shell.
The page may support bootstrap trust flows.
It may not normalize ambiguous exposure or vague browser exceptions as the durable control contract.

## Fixed page order

1. **Control endpoint card**
2. **Exposure and binding card**
3. **Auth and trust card**
4. **Capability and escalation card**
5. **Attached destructive review shell**

### 1) Control endpoint card

Show:

- daemon/device label
- stable endpoint handle
- runtime class (`desktop app`, `service`, `server`, `appliance`, `container`, `unknown`)
- current operator seat
- last-seen freshness

This is the answer to:

> what system am I about to control from this browser tab?

### 2) Exposure and binding card

Show:

- listener binding (`127.0.0.1`, specific LAN address, all interfaces, tunnel endpoint, unknown)
- exposure grade (`local only`, `local network`, `relayed`, `internet exposed`, `unknown`)
- whether this page was reached directly or via handoff
- whether a broader listener than intended is active

This is the answer to:

> how wide is the control surface actually exposed right now?

### 3) Auth and trust card

Show:

- auth mechanism
- session age
- transport trust grade
- certificate/trust posture summary
- whether the current page is still on bootstrap trust

Allowed transport trust grades:

- `managed trust`
- `pinned trust`
- `self-issued reviewed trust`
- `bootstrap trust exception`
- `unknown`

A bootstrap trust exception must never be visually identical to steady-state trusted control.

### 4) Capability and escalation card

Show:

- current seat capability for destructive actions
- any required stronger auth or second actor
- any reason destructive commit is blocked on this projection
- explicit handoff target if another surface or actor is required

### 5) Attached destructive review shell

The destructive review shell attaches below these exposure cards.
The user must not need to navigate away to understand endpoint/trust/scope truth before approval.

## Copy rule

Forbidden durable copy patterns:

- `this warning is normal, continue`
- `open anyway`
- `unsafe but fine`

Allowed copy patterns:

- `bootstrap trust exception still active; destructive actions stay blocked until trust is reviewed`
- `listener is LAN-exposed; approval remains available because current seat and trust grade satisfy policy`
- `page reached through reverse tunnel; direct binding remains local-only`

## Public object

### Local-web danger-surface exposure page

Fields:

- `local_web_danger_surface_page_id`
- `endpoint_ref`
- `runtime_class`
- `listener_binding`
- `exposure_grade`
- `reach_method`
- `auth_posture`
- `session_age`
- `transport_trust_grade`
- `bootstrap_exception_active`
- `acting_seat_ref`
- `capability_rows[]`
- `attached_destructive_shell_ref`
- `generated_at`
