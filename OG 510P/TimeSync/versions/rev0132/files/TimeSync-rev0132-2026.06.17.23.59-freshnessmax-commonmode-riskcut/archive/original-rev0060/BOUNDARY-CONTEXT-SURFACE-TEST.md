# BOUNDARY-CONTEXT-SURFACE-TEST

This note tests whether the archive now needs a named tiny surface for boundary metadata.

The archive already has:
- relay verbs
- a tiny optional reason layer
- a placement rule that says reasons are boundary-first

The remaining question is whether that is enough as an implicit pattern,
or whether a named minimal surface now earns itself.

## Question

Does boundary metadata need a named tiny surface of its own,
or can it remain implicit inside local assessed state plus relay rules?

## Source pattern

The source base now shows repeated cases where downstream behavior depends on retained boundary context,
not only on the recomputed time estimate itself.

- Telecom protection scenarios explicitly propagate the fact that a reference is no longer PRTC-traceable, and downstream applications change behavior while a new path is selected.
- Telecom and IEEE-1588-family material also includes path-trace and synchronization-uncertain style context that travels with or alongside timing state.
- NTPv5 reference-ID exchange exists specifically to carry chain context needed for loop detection, which is not the time estimate itself.

That does not force a large metadata subsystem.
It does make a named tiny surface look more honest than leaving the pattern purely implicit.

## Smallest named surface that earns itself

The current best answer is yes,
but keep it minimal.

The named surface should be:

## `boundary_context`
- `action`
- optional `reason`

Where:
- `action` is one of the existing relay verbs: `preserve`, `downgrade`, `restate`, `unknown`
- `reason` is optional and uses the existing tiny vocabulary when needed

Nothing else is promoted into the surface yet.

## Why the wrapper earns itself

### 1. It separates time belief from boundary explanation
`TimeState` should stay about current timing belief and consequence.
`boundary_context` is about how a boundary handled inherited semantics on the way to that state.

That separation is now useful enough to name.

### 2. It avoids smearing action/reason into core fields
Without a named surface,
there is pressure to leak boundary explanation into:
- `regime`
- `source_posture`
- `applicability`
- or ad hoc profile notes

The wrapper is smaller and cleaner than that.

### 3. It stays tiny
The archive is **not** adding:
- source rosters
- full provenance chains
- path histories
- hop counters
- loop filters
- or sector-specific status catalogs

It is only naming the already-existing explanatory pair when a boundary wants to retain it.

## Hook fit

### `traceability_posture`
This hook is the clearest beneficiary.
A downstream system may need to know not just that traceability is now weaker,
but whether that happened by downgrade, restatement, or unknown,
and optionally whether the trigger was loss, recovery, conflict, or reconfiguration.

### `sync_dimension`
This hook benefits less often,
but still enough to share the wrapper.
Reconfiguration and conflict around operating mode or lane selection can matter downstream
without forcing those semantics into the core state.

## Current archive judgment

Yes.
Boundary metadata now earns a named tiny surface.

But the surface should remain only:
- `boundary_context.action`
- `boundary_context.reason` (optional)

This is a wrapper,
not a new subsystem.

## What this still does **not** settle

This note still does not decide:
- whether `boundary_context` needs explicit expiry / retention semantics
- whether it should be exportable by default or only when requested / profile-required
- whether some future chain-context signals belong beside it or strictly outside it

## Next useful move

Test whether `boundary_context` needs its own expiry rule,
or whether it can safely piggyback on the freshness/lifetime of the local assessed state it accompanies.
