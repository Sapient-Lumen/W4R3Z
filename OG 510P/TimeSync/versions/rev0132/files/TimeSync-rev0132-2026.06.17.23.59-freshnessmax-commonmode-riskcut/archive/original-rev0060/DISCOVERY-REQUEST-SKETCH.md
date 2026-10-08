# DISCOVERY-REQUEST-SKETCH

This note sketches the thinnest discovery/request surface the archive can currently justify.

It is intentionally architectural.
It is **not** a packet grammar.
It is **not** a capability catalog.
It is just enough structure to let the archive mean:
- profile-fixed where needed
- discoverable/requestable where allowed
- and still small

## Question

What is the smallest shared surface that can express, for a `profile_default` hook:
- required
- requestable
- unavailable
- unknown

without turning into a general negotiation system?

## Design constraints

The archive already knows four things:

1. Some boundaries want the surface by default.
2. Some boundaries only want it when asked for or discovered.
3. Some boundaries do not support it.
4. Some participants may not know.

The sketch must carry exactly that much, and not much more.

## Smallest shared shape

The current best sketch is a two-part shape:

### Part A — exposure class
Each hook is classified, at the relevant boundary, as one of:
- `required`
- `requestable`
- `unavailable`
- `unknown`

This is the main vocabulary.
It is intentionally small.

### Part B — optional request list
If the boundary allows request-driven behavior,
a participant may request one or more hooks by name.

Current archive examples:
- `traceability_posture`
- `sync_dimension`
- `boundary_context`

That request list is only meaningful for subjects whose exposure class is `requestable`.

As of rev0054, the default lifetime of this list is **one exchange**.
A participant that wants the same optional item repeatedly repeats the explicit item request, relies on a profile-required default, or uses a future explicit lease/subscription surface if one earns itself.

## Why this is enough

### `required`
The hook must be surfaced by default because omission would already be misleading under the profile.

### `requestable`
The hook is natively supported but not always present unless requested, discovered, or otherwise enabled by profile behavior.

### `unavailable`
The boundary does not surface this hook.
No further bargaining is implied.

### `unknown`
The participant cannot currently determine whether the hook is meaningfully available.
This preserves honesty without forcing false negatives.

## Why this is smaller than a capability catalog

The sketch does **not** add:
- per-hook numeric ranges
- complex preference ordering
- alternative encodings
- bilateral option selection trees
- policy negotiation
- or free-form feature advertisement

It names only four exposure classes and an optional request list.
That is small enough for the archive.

## Why one shared surface can serve both current hooks

### `traceability_posture`
- `required` at some P5-like boundaries
- `requestable` in some lighter or integration-shaped boundaries
- `unavailable` where no honest traceability surface exists
- `unknown` where the participant cannot currently tell

### `sync_dimension`
- often effectively `required` by profile semantics
- sometimes still worth making `requestable` at an interface where explicit reflection is optional
- `unavailable` or `unknown` remain possible in simpler or legacy boundaries

So one shared exposure vocabulary appears sufficient for both hooks.
That is a good sign.

## Minimal response idea

This note does not define a grammar,
but the current response behavior is now sharper:
- `required` hooks appear by default
- `requestable` hooks may appear when requested or when local/profile policy says to include them
- a returned requested item is its own success result
- an explicitly requested optional item that is absent should get a compact negative item result when the exchange has a result-capable response surface
- `unavailable` and `unknown` remain the main absence meanings, with `omitted` reserved for exchange-local non-return that does not assert durable unavailability or unknownness

That is enough architectural clarity for now.

## Why this still is not negotiation-heavy

Nothing here implies:
- bargaining over values
- hook-specific policy exchange
- multi-round convergence
- or a universal capability matrix

This is still closer to:
- small discovery
- small request
- explicit absence classes

than to full negotiation.

## Current archive judgment

The thinnest honest discovery/request surface is currently:
- one shared exposure vocabulary
- plus one optional request list

This is enough to stabilize the idea without forcing a protocol draft.

## What this still does **not** settle

This note still does not decide:
- whether exposure class is carried on the wire, in profile metadata, or in local boundary contracts
- how relays should preserve, downgrade, or restate reflected hook state
- whether local assessed state needs an explicit profile-conformance marker
- whether `omitted` ever needs mandatory reasons

Those remain open.

## Current next useful move

Test the profile-conformance marker.
Now that missing required/default visibility is profile-nonconforming by default and locally downgrade-triggering, the next question is whether that outcome needs a compact shared local marker or can remain profile-specific validation logic.

## rev0050 note

rev0050 extends the current discovery/request sketch by reusing it for `boundary_context`.

Current archive judgment:
- the mechanism stays shared
- the requested subjects stay distinct
- the archive still rejects a second discovery channel just for explanation visibility

## rev0051 note

rev0051 keeps the shared discovery/request surface flat.

Current archive judgment:
- one request list is enough
- distinct item names are enough
- explicit namespace hierarchy does not earn itself yet


## rev0052 note

rev0052 keeps the shared discovery/request surface item-level.

Current archive judgment:
- no native named bundle layer yet
- profiles may define defaults without creating request aliases
- operator-facing presets may exist only as local conveniences
- any alias must lower to explicit item names before entering the shared machine-facing request surface

The important result is that exposure and response status stay item-level.
A bundle name is not allowed to hide `unknown`, `unavailable`, or mixed exposure results inside a single convenience label.

## rev0053 note

rev0053 keeps operator-facing aliases outside the shared request surface.

Current archive judgment:
- aliases may be documented locally as human-facing expansion sheets
- alias names are not shared request subjects
- expansion happens before the machine-facing request list
- item-level exposure and response status remain the accountable surface

This preserves the rev0052 flat request surface while acknowledging that tools and operators may still need friendly local names.
The shared request list remains explicit and item-level.

## rev0054 note

rev0054 settles request lifetime for the ordinary shared request list.

Current archive judgment:
- the request list is exchange-scoped by default
- sticky/session behavior is not implied by a prior request
- profile-fixed visibility is represented by `required` or profile default, not by remembered requests
- a future sticky surface must be an explicit lease/subscription object with expiry, renewal, and item-level results

The shared request surface therefore remains flat and stateless by default.


## rev0055 note

rev0055 settles response result shape for explicitly requested optional items.

Current archive judgment:
- present requested item content is the success result
- absent requested optional items get negative item-level accounting when the exchange is result-capable
- the base negative results are `unavailable`, `unknown`, and `omitted`
- `unsupported` folds into `unavailable`
- generic `denied` does not enter the base vocabulary yet
- silence remains acceptable for unrequested, invalid, unauthenticated, profile-forbidden, legacy, or non-result-capable cases

The discovery/request surface therefore remains flat, item-level, and reason-light.


## rev0056 note

rev0056 separates optional request accounting from required/default profile conformance.

Current archive judgment:
- absent requested optional items use negative item-level accounting when result-capable
- absent profile-required/default items fail full profile satisfaction by default
- local assessed state must withdraw hook-dependent stronger consequences
- explicit fallback is possible only as a profile-defined weaker mode

The shared discovery/request surface therefore remains small:
exposure and request results do not become a universal profile-error system.

## rev0057 note

rev0057 does not change the discovery/request surface.

Current archive judgment:
- exposure class remains item-level
- request results remain item-level
- `profile_conformance` is a later local assessed-state outcome, not another exposure class and not a bundle result
- the same missing item can matter differently depending on the active profile and exported applicability

## rev0058 note

rev0058 still does not change the discovery/request surface.

Fallback vocabulary is resolved in local assessed state:
- `profile_conformance = fallback` says full profile satisfaction failed but a weaker profile-defined mode applies
- the lowered use boundary is exported through `applicability`
- item-level exposure and request results do not become fallback labels
- aliases and bundles still do not get result status

The discovery/request surface remains item-level and exchange-scoped.

## rev0059 note

rev0059 still does not change the discovery/request surface.

`assessed_profile` is not a request item, exposure class, alias, or bundle name.
It is local/export assessment scope for `profile_conformance`.

Current archive judgment:
- item-level exposure and request results remain the accountable shared request surface
- profile identity is resolved by profile/configuration/export context
- an explicit `assessed_profile` may travel with local assessed state when needed
- no profile manifest or profile-negotiation channel is added here

The discovery/request surface remains item-level and exchange-scoped.

## rev0060 note

rev0060 still does not change the discovery/request surface.

Profile-reference binding is not a request item, exposure class, alias, or
bundle result. It is export metadata for local assessed state when
`profile_conformance` crosses a boundary.

The shared request surface remains item-level and exchange-scoped.
