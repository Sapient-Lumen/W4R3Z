# RELAY-AGGREGATION-RULES

This note sketches the smallest honest rule family the archive can currently justify for reflected `profile_default` hook state when the system:
- crosses a relay or boundary
- or combines multiple sources

The archive still does **not** want a full provenance subsystem.
It does need a compact way to say what a boundary is allowed to do.

## Question

What is the smallest rule set for reflected hook state across relays and aggregation?

## Source pattern

Current timing systems already show that not all intermediates behave the same way.

- Some intermediates may modify or adjust timing packets while preserving the essential meaning of the flow.
- Boundary-clock style systems can terminate an input timing flow, recover timing locally, and then generate a new downstream flow from that recovered local reference.
- Telecom protection behavior also shows that a downstream chain may need to be told that a stronger upstream traceability condition no longer holds, at which point devices switch to holdover.

Those are different behaviors.
The archive should name them rather than blur them together.

## Smallest honest rule family

The current best rule family is:
- `preserve`
- `downgrade`
- `restate`
- `unknown`

These four rules are enough to govern most of the archive's current middle-tier concerns.

## 1. `preserve`

Use `preserve` when the boundary is passing the hook state through without materially changing its meaning,
and the archive can still justify the same state on the downstream side.

Typical shape:
- forwarding without semantic reinterpretation
- adjustments that do not break the meaning of the hook
- no stronger claim than what already held upstream

This is the most conservative positive case.

## 2. `downgrade`

Use `downgrade` when the downstream side can still say something meaningful,
but no longer at the same strength.

Typical shape:
- stronger upstream traceability is no longer justified downstream
- a requested surface becomes only partially supportable
- aggregation preserves the common lower state but not the stronger one

This rule carries forward the archive's earlier non-upgrade posture.

## 3. `restate`

Use `restate` when the boundary is no longer honestly acting as a pure pass-through,
but is instead creating a new downstream state from:
- locally recovered timing
- local policy
- or an aggregated combination of multiple inputs

Typical shape:
- boundary-clock-like behavior that terminates one timing flow and generates another from local recovered timing
- a relay that combines multiple sources into one assessed downstream state
- any case where the downstream hook state is now primarily a local restatement rather than an inherited upstream fact

`restate` is not a license to upgrade.
It means: say what you now believe locally, not what you merely received.

## 4. `unknown`

Use `unknown` when the boundary cannot honestly preserve, downgrade, or restate the hook state.

Typical shape:
- insufficient evidence
- conflicting inputs without a stable combination rule
- incomplete relay knowledge
- temporary transitions or recovery conditions where a stronger statement would be fake precision

This preserves honesty under uncertainty.

## Relay cases

### Pass-through style boundary
Preferred action:
- `preserve`, unless the boundary weakens evidence or loses a stronger condition

### Regenerating / boundary-clock style boundary
Preferred action:
- `restate`

Reason:
if the boundary recovers time locally and emits a new downstream flow,
its downstream hook state is no longer merely inherited.

### Protection / degraded fallback case
Preferred action:
- `downgrade` or `unknown`

Reason:
when a stronger reference condition is lost,
downstream participants should not continue to believe the stronger state silently survives.

## Aggregation cases

### Multiple agreeing inputs
Possible actions:
- `preserve` if the downstream object is still transparently representing one common state
- otherwise `restate` as a locally assessed combined state

### Multiple partially compatible inputs
Preferred action:
- `downgrade`

Reason:
the common lower state may still be honest even when the stronger state is not.

### Multiple conflicting inputs
Preferred action:
- `unknown` unless there is a profile-defined restatement rule strong enough to justify a new assessed state

## Hook fit

### `traceability_posture`
This hook uses the full rule family well.
- preserve a still-valid anchor/evidence posture
- downgrade when stronger traceability no longer holds
- restate when a local service or boundary is now honestly making its own assessed claim
- mark unknown when the boundary cannot justify more

### `sync_dimension`
This hook usually needs fewer transitions.
- preserve when the profile dimension still holds downstream
- restate when a boundary changes the effective operating mode or creates a new local combined state
- downgrade or unknown only when the dimension becomes less definite than before

This difference is acceptable.
The same rule family can still cover both hooks.

## Why this is enough for now

This note does **not** add:
- a provenance graph
- a source roster
- a relay workflow engine
- a sector-specific compliance lattice

It just says what kinds of honesty moves a boundary may make.
That is enough architectural guidance for the current archive stage.

## Current archive judgment

The smallest honest rule family for reflected hook state is:
- preserve
- downgrade
- restate
- unknown

This is the first relay/aggregation object the archive can justify without overbuilding.

## What this still does **not** settle

This note still does not decide:
- whether the same rule family needs a profile-specific ordering or precedence table
- how a boundary should annotate the reason for downgrade or restatement
- whether `unknown` must always propagate into downstream `applicability`
- how long a restated hook remains valid without refresh

Those remain open.

## Next useful move

Test whether the archive now needs a tiny reason vocabulary.
The next question is whether relay/restatement semantics stay legible with only the four rule names,
or whether a second tiny layer of reasons is needed for downgrade and restatement without turning into provenance sprawl.


## rev0044 note

rev0044 adds one small refinement:
the four relay verbs now look clearer with an **optional** tiny reason layer.

Current archive judgment:
- keep the verbs as primary
- allow reasons only when they materially improve honesty or legibility
- and keep the candidate reason set very small: `loss`, `recovery`, `conflict`, `reconfiguration`

## rev0045 note

rev0045 adds one downstream consequence clarification for `unknown`.

Current archive judgment:
- `unknown` does **not** automatically mean universally unusable
- it does mean that any stronger `applicability` claim depending on the now-unknown hook may no longer be asserted by default
- the exact fallback tier remains profile-local

This keeps the relay rule family small while preventing `unknown` from becoming a no-op for downstream consequence.

## rev0046 note

rev0046 adds a placement judgment for the optional reason layer.

Current archive judgment:
- reasons belong primarily with the **boundary action** that preserved, downgraded, restated, or marked state unknown
- a local assessed state may retain them
- the archive does **not** make them part of the minimal wire claim by default

This keeps relay semantics legible without turning the wire into a status catalog.

## rev0047 note

rev0047 names the smallest optional wrapper for retained boundary explanation.

Current archive judgment:
- when relay action and optional reason need to be retained beyond the immediate transition,
they should travel as `boundary_context`
- `boundary_context` currently contains only `action` plus optional `reason`
- the archive still refuses larger provenance or chain-history structures here

## rev0048 note

rev0048 adds a default lifetime rule for retained boundary explanation.

Current archive judgment:
- if relay action / reason is retained as `boundary_context`, it lives only as long as the local assessed state it explains
- a later recomputed state may attach a new wrapper or none
- history remains outside this runtime surface unless a profile explicitly adds it elsewhere

## rev0049 note

rev0049 adds a visibility rule for retained boundary explanation.

Current archive judgment:
- `boundary_context` should not be globally always-exported
- it should be requestable by default
- profiles may still require default export where omission would mislead active transition or control behavior
