# GREENFIELD-TRACEABILITY

This note asks what changes if the greenfield TimeSync track treats the reduced `traceability_posture` hook as first-class from the beginning instead of reconstructing it later from side channels.

## Question

What concrete boundary changes follow if a from-scratch TimeSync design takes `traceability_posture` seriously from day one?

## Current comparison surface

### What current mechanisms already surface natively

- NTS gives strong server authentication and key establishment.
- NTPv5 is moving toward explicit timescale signaling and better extension structure.
- Roughtime gives signed time replies, bounded uncertainty, delegated keys, and malfeasance evidence.
- TrueTime-like systems show the value of making uncertainty a client-visible part of the contract.

### What they do **not** jointly surface as one small thing

They do not jointly give a compact native statement of:
- what reference family a claim is anchored to
- and the minimum evidence posture for that anchor

Today that is usually reconstructed from:
- operator configuration
- sector rules
- service documentation
- external calibration
- deployment topology
- or profile-local status objects

That is exactly the pattern the archive has been trying not to rely on.

## Greenfield judgment

If the greenfield track makes `traceability_posture` first-class, it changes **three boundaries** before it changes anything larger.

### 1. Source admission becomes a native contract

A source or server should not merely present identity and a time value.
It should present, natively:
- `timescale`
- `reference_anchor`
- `evidence_posture`

This is the first important distinction:
**who signed the reply** is not the same thing as **what reference the reply claims to be tied to**.

A greenfield design can keep these separate from the start.
That is better than inheriting a protocol where authentication is explicit but traceability is implicit.

### 2. Exported state gains a native adjacent hook

A greenfield design does not yet need to promote `traceability_posture` into the minimal core.
But it should give the client a native path to receive it together with the bounded time claim.

That suggests a response/state shape closer to:
- interval / radius semantics
- explicit timescale
- optional but native `traceability_posture`
- freshness/regime

This is different from the integration track, where the same conclusion often has to be inferred from stratum, server role, sector-specific status words, or external documentation.

### 3. Aggregation must obey a non-upgrade rule

If a greenfield system aggregates multiple sources or crosses a control boundary,
it should not silently strengthen `evidence_posture` or `reference_anchor`.

Working rule:
- aggregation may preserve or downgrade traceability posture
- it must not upgrade it without new evidence

Examples:
- a locally held-over replica should not continue to advertise a stronger anchor than its current regime justifies
- a service combining mixed sources should not claim a stronger evidence posture than the weakest boundary-bearing path can support

This is the cleanest greenfield-specific design consequence the current archive can justify.
It is also small.

## What this still does **not** force

This does **not** yet force:
- promotion of `traceability_posture` into the minimal core
- a full provenance ledger on the wire
- a compliance taxonomy
- a full governance subsystem in the protocol
- replacement of profile-local verification overlays

The archive should resist all of those until one of them is clearly boundary-bearing.

## Why this matters

The integration track often discovers traceability after the fact.
The greenfield track can avoid that trap by making traceability:
- explicit enough to survive relay and aggregation
- small enough to stay out of the way
- and separate enough from uncertainty and identity to remain honest

## Current archive judgment

The first concrete greenfield change caused by a stable `traceability_posture` hook is:
- not a new protocol family
- not a broader core object
- but a **native contract at source admission and exported-state boundaries**

That is a real design move and a small one.

## Next useful move

Test whether the greenfield track really needs this hook in the default client-visible state,
or whether a native optional extension would preserve nearly all of the value.
