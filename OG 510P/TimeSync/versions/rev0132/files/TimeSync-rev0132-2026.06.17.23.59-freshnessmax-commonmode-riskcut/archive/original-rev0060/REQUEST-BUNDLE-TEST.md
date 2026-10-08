# REQUEST-BUNDLE-TEST

This note tests whether profiles need named request bundles.

The archive already decided:
- one shared discovery/request mechanism
- one flat request list
- distinct item names
- no extra namespace hierarchy

The remaining question is whether profiles should be able to request named groups of items, rather than naming each requested item directly.

## Question

Do profile-level named bundles earn themselves,
or are item-level requests still enough?

A bundle would be a machine-facing alias such as:
- request bundle X
- receive the items implied by X
- treat the bundle as a shared request subject

That is different from a profile simply requiring default visibility.
It is also different from a human operator preset that expands locally before the request is sent.

## Source pattern

The source pattern is mixed, but it does not yet justify a native bundle layer.

- NTPv5 keeps optional behavior at the typed extension-field level: a request includes specific fields, and absence in the response can indicate unsupported fields.
- Roughtime keeps request/response structure tag-based; compatibility is carried through explicit version tags and fixed required tags, not through named bundles of optional semantics.
- PTP profiles do bundle many choices at the profile/configuration layer, but unicast negotiation and signaling still operate through specific message/service requests rather than arbitrary cross-semantic aliases.
- Synchrophasor timing pushes traceability, accuracy, leap-status, and time-quality visibility together, but that pressure is profile-default measurement semantics, not request shorthand.
- The PTP Enterprise Profile is a useful negative case: a profile can forbid whole optional mechanisms while still not needing per-exchange bundle aliases.

The recurring pattern is therefore:
profiles may be bundles above the request surface,
but the shared request surface stays item-specific.

## Smallest answer that survives the pressure

No native named bundles yet.

The current best rule is:

> the shared request surface remains item-level;
> profiles may define local aliases only if they lower to explicit item names before entering the shared request surface.

Current native request subjects remain examples like:
- `traceability_posture`
- `sync_dimension`
- `boundary_context`

A profile may say that all three are normally useful together.
That still does not make their group a new shared request subject.

## Why native bundles do not yet earn themselves

### 1. Bundle status would blur item status

The existing exposure vocabulary is item-level:
- `required`
- `requestable`
- `unavailable`
- `unknown`

A bundle can contain mixed results.
For example:
- `traceability_posture` may be `required`
- `boundary_context` may be `requestable`
- `sync_dimension` may be profile-declared and already known

A single bundle result would either hide those differences or require a second result model.
That is not reduction-friendly.

### 2. P4 clusters are not stable enough

P4-like telecom cases repeatedly cluster:
- synchronization dimension
- traceability or reference quality
- holdover / protection transition explanation

But the exact cluster changes across frequency-only, phase/time, full-timing-support, partial-timing-support, and enterprise/profile cases.
That is profile structure, not a stable request bundle.

### 3. P5 clusters are mostly default requirements

P5-like measurement cases repeatedly cluster:
- UTC traceability
- time accuracy / quality
- leap-second status
- phase/frequency measurement meaning

But these are usually part of the measurement/reporting contract.
They argue for profile-default visibility, not a request alias.

### 4. Aliases are still useful, but elsewhere

Human-facing tooling may reasonably expose presets such as:
- show timing evidence
- show boundary explanation
- show measurement timing context

The archive should not forbid that.
It should only refuse to promote those presets into shared machine-facing syntax before recurrence proves they are more than convenience.

## Current archive rule

For now:
- native shared requests name individual items
- any operator/profile alias must expand locally to explicit item names
- exposure and response status remain item-level
- a profile may require a set of items by default without creating a request bundle

This keeps the request surface flat and honest.

## Non-upgrade rule for aliases

An alias cannot strengthen semantics.

If an alias expands to three items and one item is `unknown` or `unavailable`, the alias does not preserve the stronger combined meaning by itself.
The local assessed state still has to apply the ordinary item-level consequence rules.

## Promotion test for future bundles

A native bundle may be reconsidered only if all of these become true:

1. the same exact item set recurs across multiple profiles or boundaries;
2. item-level requests are causing repeated operational or implementation errors;
3. the group has an all-or-nothing consequence not reducible to its members;
4. the name remains stable across both integration and greenfield tracks;
5. mixed item-level exposure results would not be hidden.

The archive does not currently meet that bar.

## Current archive judgment

Profile-level named bundles do not earn native shared-surface status yet.

The archive keeps:
- one flat request list
- explicit item names
- no namespace hierarchy
- no native bundle layer

It allows:
- profile-local defaults
- operator-facing presets
- local aliases that lower to explicit item requests

## What this still does **not** settle

This note still does not decide:
- whether some future profile will create a true all-or-nothing bundle
- whether a future explicit lease/subscription surface would reuse the same item names
- whether profile satisfaction needs a compact local marker

## Next useful move

Test the profile-conformance marker after rev0056's required/default absence decision.

## rev0053 follow-on

rev0053 resolves this note's operator-alias frontier by adding a thin local documentation boundary.

That follow-on does not weaken the rev0052 result:
- native shared bundles remain rejected
- operator aliases remain non-interoperable local conveniences
- aliases must expand to explicit item names before the shared request surface
- mixed item-level results may not be hidden behind the alias label


## rev0054 follow-on

rev0054 settles ordinary request lifetime as exchange-scoped.

That strengthens this note's bundle decision:
- a bundle alias cannot become sticky by being used once
- repeated local presets must repeat explicit item names
- profile-required sets stay profile defaults
- any future leased/subscription surface must still report item-level results and must not hide mixed outcomes behind a bundle label


## rev0055 follow-on

rev0055 strengthens this note's bundle decision.

Because request results are negative-only and item-level:
- a bundle alias cannot receive one aggregate success/failure result
- returned content is success only for the item returned
- `unavailable`, `unknown`, and `omitted` attach to explicit item names
- mixed item outcomes remain visible after local alias expansion


## rev0056 follow-on

rev0056 keeps this note's anti-bundle boundary intact.

Required/default absence is assessed at the explicit item and profile-contract level:
- a bundle alias cannot make a missing required item profile-satisfying
- fallback is profile-defined and weaker than full satisfaction
- local downgrade remains tied to the missing item and its dependent consequences
