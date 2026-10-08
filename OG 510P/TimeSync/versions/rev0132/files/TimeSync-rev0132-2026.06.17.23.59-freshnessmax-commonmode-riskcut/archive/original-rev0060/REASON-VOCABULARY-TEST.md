# REASON-VOCABULARY-TEST

This note tests whether the archive's relay/aggregation rule family needs a second tiny layer of reasons.

The archive already has:
- `preserve`
- `downgrade`
- `restate`
- `unknown`

The question is whether those verbs are enough on their own.

## Question

Does the archive need a tiny reason vocabulary for `downgrade` and `restate`, or would that already be too much machinery?

## Source pattern

Current timing systems often do carry compact reason-like distinctions.

- Telecom timing distinguishes packet timing signal failure cases such as `lossSync`, `lossAnnounce`, and `unusable`.
- NTP has compact reason-coded error/status behavior such as Kiss-o'-Death codes.
- Roughtime gives a path for cryptographic malfeasance / inconsistency reporting.

The point is not to copy any of these literally.
The point is that bare state transitions are sometimes not enough to stay legible.

## Archive judgment

Yes — the archive now has enough justification for a **tiny optional reason vocabulary**.

But it should stay very small.
It should annotate only the cases where the bare rule name would otherwise hide a materially different cause.

## Smallest useful reason set

The current best candidate set is:
- `loss`
- `recovery`
- `conflict`
- `reconfiguration`

## Why these four

### `loss`
Use when a stronger upstream basis has been lost or become unusable.

Examples:
- lost sync input
- lost announce / reference visibility
- stronger traceability no longer justified

This is the main companion reason for `downgrade`.

### `recovery`
Use when the boundary is now producing downstream state from locally recovered timing rather than transparently passing the upstream state through.

Examples:
- local holdover recovery
- boundary-clock-like regeneration
- locally re-originated state after loss of a prior reference path

This is the cleanest companion reason for `restate`.

### `conflict`
Use when multiple inputs disagree or malfeasance / inconsistency has made simple preservation impossible.

Examples:
- source disagreement without a stronger common state
- aggregated inputs that do not admit a clean shared result
- cryptographic or evidentiary inconsistency strong enough to block silent carry-forward

This is useful for both `downgrade` and `unknown`.

### `reconfiguration`
Use when the operating mode, profile context, or selected synchronization path has changed in a way that changes the meaning of the reflected state.

Examples:
- a new backup path is selected
- a dimension or profile context changes
- a boundary is now restating the state under a different local operating mode

This is the main reason that keeps `sync_dimension` legible without requiring a large mode taxonomy.

## What this reason layer should **not** become

It should **not** become:
- a fault tree
- a provenance ledger
- a sector-specific codebook
- a substitute for observability systems
- a large status registry

It is a tiny semantic aid, not an operations console.

## Recommended placement

The reason layer should be:
- **optional**
- attached mainly to `downgrade`, `restate`, or `unknown`
- omitted when the bare rule already says enough

The archive does **not** need every boundary transition to carry a reason.

## Hook fit

### `traceability_posture`
This hook benefits strongly from the reason layer.
- `downgrade + loss`
- `restate + recovery`
- `unknown + conflict`

These pairings carry genuinely different meanings.

### `sync_dimension`
This hook benefits more selectively.
- `restate + reconfiguration`
- `unknown + conflict`

It often does not need as many cause distinctions as traceability.
That is acceptable.

## Why this is worth adding

Without a tiny reason layer,
`downgrade` and `restate` can hide importantly different causes.
The archive now has enough evidence that those distinctions matter,
but still not enough to justify anything larger than a four-reason set.

## Current archive judgment

The archive should keep:
- the four relay verbs
- plus an **optional** tiny reason vocabulary of:
  - `loss`
  - `recovery`
  - `conflict`
  - `reconfiguration`

That is still small enough to fit the archive's discipline.

## What this still does **not** settle

This note still does not decide:
- whether reasons should ever be surfaced directly to downstream clients
- whether `unknown` without a reason should be treated differently from `unknown + conflict`
- whether reasons belong in wire state, boundary metadata, or local assessed state only
- whether some profiles should forbid certain reason combinations

Those remain open.

## Next useful move

Test the downstream consequence of `unknown`.
The next question is whether the archive now needs a tiny consequence rule for how `unknown` affects `applicability`, or whether that should remain entirely profile-local.
