# Compromise containment and trust-rotation interface spec

The archive already has exit plans, recovery bundles, successor cutover, access tokens, portable offers, and explicit revocation verbs.
This document answers the narrower practical question those abstractions still left open:

> what must a real compromise-response surface literally show before apply, so AnonSync does not drift back into unlink, uninstall, regenerate, and reshare ritual?

This is the incident-side companion to `65-exit-review-and-replacement-interface-spec.md` and the trust-rotation companion to `68-successor-cutover-and-rehome-interface-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
`If your device is stolen` recommends a sequence that runs through backup, remove shares, unlink from identity, remove synced data, reinstall Sync, regenerate identity, relink devices, and reshare folders.
`How to clear offline devices?` separately says clearing only hides the device and that it will reappear if it comes back online.
`Sync Private Identity & Linking My Devices` adds that you cannot remotely unlink other devices.
`How to uninstall Sync?` then adds more cleanup ritual around settings directories, service storage, and hidden `.sync/Archive` bytes.

The lesson is not that Resilio has no value.
The lesson is that a useful product can still scatter containment meaning across too many rituals.

AnonSync should therefore make these differences explicit before apply:

- this is suspicion review vs confirmed containment
- this freezes future authority now vs revokes durable authority now vs rotates identity later
- this prepares a reviewed successor vs intentionally chooses a clean break
- this only hides a stale row vs actually changes trust state
- this still leaves residue waiting on offline peers, provider TTLs, or unknown remote bytes

## Core rule

A non-trivial trust incident should always compile to a reviewed compromise surface.
That includes at least:

- suspected or confirmed stolen device response
- leaked access token, portable offer, or other bearer-style authority
- stale offline device reappearing in a way that suggests live authority rather than list clutter
- identity rotation after suspected key/certificate compromise
- any incident where continuity-preserving successor handling and trust revocation coexist

A channel may compress the review when risk is truly low.
It may not replace the meaning with vague `unlink`, `reinstall`, `reset`, `remove settings`, or `reshare` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench `Exits & Replacement` page
- a report-driven `Open compromise case` action from device, access, route, or offer surfaces
- device detail `Contain incident` action
- CLI `compromise open --subject ... --plan`
- CLI `recover rotate-identity --plan` or `recover revoke-device --plan` when the operator-visible meaning is incident response
- an incident-sensitive `exit prepare` action for urgent device decommission

But these must all converge on the same public compromise model.
The operator should never have to wonder whether one surface is only hiding a row while another is actually freezing authority, rotating identity, or preparing a successor.

## Fixed review order

Every non-trivial compromise review should render the same sections in the same order:

1. **Trigger and scope**
2. **Immediate freeze**
3. **Revocation and rotation**
4. **Continuity and successor**
5. **Residue and observation**
6. **Receipt promise**

### 1) Trigger and scope

This section should show:

- what triggered the case
- confidence posture (`suspected`, `probable`, `confirmed`)
- primary and related subjects
- whether the case is about device theft, bearer leak, stale identity reappearance, or broader trust compromise
- whether any prior reports, recovery receipts, or exit plans are already attached

The operator must be able to answer: **what exactly are we responding to, and how wide is the case?**

### 2) Immediate freeze

This section should show:

- which sessions, offers, route leases, approvals, or grants can freeze immediately
- which freeze effects are already active versus still only proposed
- what the freeze does **not** revoke yet
- whether any freeze effect is local-only, constellation-wide, or waiting on remote observation

The operator must be able to answer: **what future activity stops right now, before deeper cleanup or rotation finishes?**

### 3) Revocation and rotation

This section should show:

- which tokens, offers, grants, approvals, or memberships will be revoked
- whether identity or key rotation is required, recommended, or intentionally deferred
- whether revocation is blocked by missing proof, missing custody, or successor choice
- what rotates versus what is merely disabled or hidden

The operator must be able to answer: **what durable authority actually ends here, and what durable material must change?**

### 4) Continuity and successor

This section should show:

- whether successor continuity is recommended, available, blocked, or intentionally rejected
- which recovery bundle, predecessor evidence, or state-root proof continuity depends on
- which approvals, grants, or memberships carry forward versus stay frozen
- whether the reviewed alternative is a clean break rather than a successor

The operator must be able to answer: **are we preserving the right continuity, or intentionally breaking it?**

### 5) Residue and observation

This section should show:

- offline peers that have not yet observed revocation or freeze
- provider-cache or publication TTL residue
- local or remote bytes whose state cannot yet be attested
- preserved local state or recovery material that remains intentionally outside the containment action
- what follow-up still requires later observation rather than immediate mutation

The operator must be able to answer: **what still remains after apply, even if urgent containment succeeds?**

### 6) Receipt promise

This section should show:

- which receipt will exist after apply
- what it will later prove about trigger posture, freeze effects, revocations, rotations, continuity choice, and unresolved residue
- whether the receipt is provisional because observation is still pending
- what later audit survives after the draft or original report is gone

The operator must be able to answer: **what later evidence will prove what this compromise response actually changed?**

## Action hierarchy inside compromise review

The primary action should be the safest meaningful next step.
Examples:

- probable stolen device with live sessions → `Apply containment` may be primary
- weak or stale signal with little evidence → `Review trigger` or `Freeze minimally`, not `Rotate identity now`
- strong continuity evidence and clear successor candidate → `Prepare successor` may sit next to containment, but should not silently ride inside it

Confusing alternatives such as `Hide device`, `Reset identity`, or `Remove settings` should be visually separate and usually plan-bearing.

## What the surface must never imply

The compromise surface must never imply that these are the same thing:

- hiding a stale device row vs revoking its authority
- freezing a session vs rotating durable identity material
- preparing a successor vs confirming compromise cleanup
- deleting local bytes vs ending remote trust
- suspicion review vs durable containment receipt

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/WebUI parity rule

A Linux-first product has to assume that WebUI, TUI, CLI, and headless automation are not edge cases.
So the reviewed compromise grammar must survive across those channels.
It is not acceptable for one richer surface to show freeze/revoke/rotate truth while Linux/WebUI falls back to generic uninstall or relink guidance.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync compromise show <id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn what was frozen immediately, what durable authority is ending, what continuity remains possible, and what residue still waits on observation.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed compromise grammar is how the archive avoids rebuilding a system where theft and authority-leak response are individually scriptable and individually convenient, yet the full meaning still depends on which unlink, uninstall, or relink prompt happened to appear first.
