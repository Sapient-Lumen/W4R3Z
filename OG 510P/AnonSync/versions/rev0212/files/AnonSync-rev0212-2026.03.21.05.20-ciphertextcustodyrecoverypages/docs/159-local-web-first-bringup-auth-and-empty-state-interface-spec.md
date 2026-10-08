# Local web first bringup, auth, and empty-state interface spec

## Purpose

AnonSync is Linux-first.
That means many real installs will begin from:

- local web on a Linux workstation
- local web on a server or appliance
- local web attached to a background service
- maybe later a richer GUI or TUI, maybe not

So the product needs a stronger decision than `also offer a browser UI`.
The real question is:

> what must the local web surface teach and guarantee on first run so Linux/service operators are not treated as second-class users?

## Core decision

The **local web projection is primary**.
For ordinary operation it must support the same semantic contract as other first-class projections:

- read state
- explain state
- assemble draft
- review draft
- pass through commit barrier
- apply when current custody and policy allow it
- export or hand off context explicitly when they do not

This document focuses on first-run bringup, auth, and empty-state teaching because those are where second-class projection drift begins.

## First-run bringup goals

A good first-run local web surface should answer these questions immediately:

1. **What am I connected to right now?**
2. **What kind of authority do I have from this seat?**
3. **What are the first normal actions here?**
4. **What can this surface fully do by itself?**
5. **What would require a handoff and why?**

It should not feel like a thin remote shell for some other real product.

## Bringup anatomy

### 1) Control endpoint identity

Show:

- local daemon/device label
- endpoint scope (`local only`, `LAN exposed`, `reverse tunnel`, etc.)
- auth posture
- active seat identity or unauthenticated state

This is the answer to `what am I actually controlling?`

### 2) First-run safety posture

Before teaching product actions, the surface should state:

- whether this endpoint is local-only by default
- whether credentials are set
- whether TLS / trust posture is local-only, self-signed, or managed otherwise
- whether any wider exposure exists

The operator should not have to leave the page to infer whether the browser session is already a wider control channel.

### 3) First normal actions

The empty-state teaching region should recommend actions like:

- create or inspect local identity
- link or introduce a peer
- inspect an incoming claim
- create a share
- open diagnostics if health is already degraded
- configure exposure/auth only if relevant

The order matters.
The first-run page should teach the real product model, not merely showcase features.

### 4) Capability statement

The local web surface should explicitly state that it can:

- inspect subjects
- explain proof
- create and review drafts
- apply reviewed actions when custody allows

If anything is currently unavailable, the page should say why.
It should never imply there is a richer hidden desktop truth the operator ought to guess about.

## Auth rules

### Password / session setup

If authentication is required, setup should happen in product language, not browser lore.
The flow should state:

- who this credential protects
- which endpoint it protects
- whether it is local-browser only or LAN-reachable
- what later rotation or reset looks like

### Session continuity

Once authenticated, the local web shell should preserve:

- active seat
- current subject context
- currently open draft or report
- handoff destination if explicit handoff is chosen

Login should not drop the operator back into a vague home page that forgets why they came.

### Auth repair

Credential failure or expired session should keep context.
After re-auth, the operator should return to the same draft, report, or subject when safe.
Losing semantic continuity at auth boundaries is one of the fastest ways to make web feel second-class.

## Empty-state rules

A local web empty state should teach the model through absence.
Examples:

- `No shares yet. Create one, or inspect incoming visibility once peers are introduced.`
- `No items in Now. Nothing currently needs immediate review from this seat.`
- `No active drafts. High-signal work will appear here before apply.`

Bad empty states are decorative, salesy, or apologetic.

## Local web should refuse these anti-patterns

- `Install the desktop app for full control` as the normal answer
- hiding draft or explain capability behind desktop-only assumptions
- projection-specific truth vocabulary
- browser quirks silently removing the only primary action
- exposure/auth state that requires support articles to understand

If an action truly requires another projection or custody seat, the surface should say so directly and preserve context for handoff.

## Handoff rules

Handoff is allowed when legitimate.
But it must preserve:

- subject handle
- draft handle
- report/proof context
- current acting seat or custody requirement
- exact reason handoff is necessary

The operator should see `Continue on seat with filesystem custody` rather than `Unavailable here`.

## Narrow and service-hosted environments

The same local web rules apply when:

- running on a small device
- accessed through a tunneled connection
- backed by a long-lived service

Layout may differ, but the semantic promises do not.

## Result

A good local-web-first bringup prevents four failures:

- Linux/service users guessing whether they are in the real product or a fallback shell
- auth flows that sever context and force page archaeology
- empty states that teach features instead of the model
- handoff that hides whether the action is impossible, unauthorized, or simply requires another custody context

If the first browser session already feels like a degraded cousin of another interface, AnonSync has broken its Linux-first promise.
