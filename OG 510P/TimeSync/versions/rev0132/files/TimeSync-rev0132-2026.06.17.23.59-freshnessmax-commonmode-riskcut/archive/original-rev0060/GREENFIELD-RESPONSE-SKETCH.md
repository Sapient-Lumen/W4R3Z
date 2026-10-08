# GREENFIELD-RESPONSE-SKETCH

This note asks what the greenfield track should do **now** that the archive's `profile_default` tier appears stable.

The archive does not yet need a protocol.
It does need a thin response/state model that can carry the minimal core plus the two surviving middle-tier hooks without widening the archive-wide core.

## Question

What is the thinnest greenfield response/state layout that can carry:
- the minimal six-part core
- `traceability_posture`
- `sync_dimension`

when a demanding profile needs them?

## Source pattern

Current timing systems already suggest a split.

- NTPv5 is increasingly explicit about the **wire contract** while leaving client-side filtering, source selection, and clock discipline out of scope.
- NTS separates **initial authenticated setup** from later time-synchronization packets.
- Roughtime provides a compact **signed time claim** with a bounded uncertainty and delegated-key evidence.
- TrueTime-like systems expose a richer **client-side time API** with uncertainty semantics that are useful to downstream logic.

The common lesson is not that one protocol is about to win.
The lesson is that **wire claims** and **local assessed state** are different objects.

## Archive judgment

The thinnest useful greenfield shape is a **two-surface model**:

1. **Wire claim**
2. **Local assessed state**

This is the smallest move that lets the archive build with the stabilized tier without falsely promoting it into the archive-wide core.

## Surface 1 — Wire claim

The wire claim is what a source, server, or upstream relay actually says.
It should stay compact.

### Minimum wire claim
- `interval_claim`
- `timescale_claim`
- `identity_or_auth_proof`

This is the minimum because a greenfield system still has to answer:
- what time is being claimed
- in what timescale
- and by whom / under what cryptographic cover

### Native but not universal wire-adjacent claims
When a profile needs them, the wire claim may also carry:
- `traceability_posture_claim`
- `sync_dimension_claim`

These are the current `profile_default` members.
They are strong enough that a greenfield design should have a native place for them,
but not strong enough to force them into every minimal exchange.

### What does **not** belong in the minimum wire claim
The archive does not yet need the wire claim to carry:
- `freshness`
- `regime`
- `source_posture`
- `applicability`

Those are usually not pure upstream facts.
They are mostly local or aggregated judgments.

## Surface 2 — Local assessed state

The local assessed state is what a client, relay, appliance, or service currently believes after:
- receiving one or more wire claims
- applying source policy
- assessing freshness
- tracking regime changes
- and mapping the result to downstream consequences

### Minimum local assessed state
The existing minimal TimeState still fits best here:
- `interval`
- `timescale`
- `freshness`
- `regime`
- `source_posture`
- `applicability`

This note does **not** widen that core.
It only places it more clearly.

### Assessed middle-tier surfaces
When needed, local assessed state may also carry:
- `traceability_posture`
- `sync_dimension`

The archive should allow these to appear in local state even when they were absent on the wire,
provided they were inferred from trusted local configuration, profile policy, or a bounded integration context.

## Why this split matters

### 1. It protects the core from false promotion
The archive no longer has to choose between:
- pretending the middle-tier hooks are universal core fields
- or pretending they are merely optional decorations

The split gives them a third place:
- native surfaces when needed on the wire
- native assessed state when needed locally

### 2. It keeps claims separate from judgments
A server can claim:
- an interval
- a timescale
- maybe an anchor/evidence posture
- maybe a synchronization dimension

A client or aggregator can judge:
- freshness
- regime
- source posture
- applicability
- whether the upstream claims still survive the current boundary honestly

That distinction is load-bearing.

### 3. It gives aggregation somewhere honest to happen
Aggregators and relays are common in real time systems.
They need a place to transform claims into assessed state without pretending that every local judgment was itself an original upstream claim.

## First greenfield consequence

If the archive uses this split,
then the first greenfield response object should probably look more like:

### Wire claim object
- bounded time claim
- timescale
- proof / identity envelope
- optional `traceability_posture_claim`
- optional `sync_dimension_claim`

### Local assessed object
- minimal TimeState
- optional assessed `traceability_posture`
- optional assessed `sync_dimension`

This is still a sketch, not a spec.
But it is the thinnest sketch the current archive can justify.

## What this does **not** settle

This note does not yet decide:
- whether `traceability_posture` is best modeled as a source claim, a local assessment, or both
- whether `sync_dimension` should usually be negotiated, declared, or inferred
- how relays should preserve versus rewrite these hooks
- whether demanding profiles need a standard way to request these surfaces

Those are the next questions.

## Current archive judgment

The stabilized `profile_default` tier does **not** force a bigger core.
It does force a cleaner architecture:
- a thin wire claim
- and a richer local assessed state

That is the first greenfield design move that currently seems both real and small.

## Next useful move

Test each current `profile_default` hook against this split.
The next question is whether the archive should treat:
- `traceability_posture`
- `sync_dimension`

as source claims, local assessments, or dual-surface semantics.


## rev0039 provisional answer

The first hook tested against this split is `traceability_posture`.
Current archive judgment:
- it is **dual-surface**
- some demanding P5 boundaries want it carried live as part of time status / source-facing claim semantics
- some P3 boundaries establish it more honestly through local or service-assessed evidence

That result strengthens the split rather than weakening it.
It shows the archive did not create an empty distinction; it created a place for two different honest placements of the same hook.


## rev0040 provisional answer

The second hook tested against this split is `sync_dimension`.
Current archive judgment:
- it is **profile-declared first**
- some profiles may echo it on the wire
- local assessed state may reflect it for downstream consequence mapping

This means the two current `profile_default` hooks do not share one placement pattern.
The tier survives, but as a small family rather than a uniform class.


## rev0041 provisional answer

The archive has now tested whether the `profile_default` tier needs any additional interface surface.
Current judgment:
- yes to a **small discovery/request surface**
- no to a broad negotiation subsystem
- and preserve profile-fixed defaults where the profile already requires visibility

This keeps the architecture small while acknowledging that optional native surfaces still need a way to be discovered or requested without bloating the core.


## rev0042 provisional answer

The archive now has a first tiny sketch for discovery/request semantics.
Current judgment:
- one shared exposure vocabulary is enough for the current middle-tier hooks
- one optional request list is enough to make requestable behavior real
- broader capability negotiation still looks unnecessary

This keeps the architecture compact while making the discovery/request idea concrete.


## rev0043 provisional answer

The archive now has a first relay/aggregation rule family for reflected hook state.
Current judgment:
- boundaries may `preserve`, `downgrade`, `restate`, or report `unknown`
- this is enough to govern the current middle tier without adding provenance machinery
- `traceability_posture` uses the full family most naturally, while `sync_dimension` often needs only a subset

This gives the greenfield sketch its first compact cross-boundary honesty rules.


## rev0044 provisional answer

The archive now has a first tiny reason layer for relay/restatement semantics.
Current judgment:
- the relay verbs remain primary
- reasons are optional and only attach when needed for legibility
- the candidate reason set stays small: `loss`, `recovery`, `conflict`, `reconfiguration`

This gives the greenfield sketch a little more explanatory power without dragging it into status-taxonomy sprawl.

## rev0045 provisional answer

The archive now gives `unknown` one narrow downstream consequence rule.
Current judgment:
- this rule belongs primarily in **local assessed state**, because it changes what downstream systems may continue to believe or do
- a wire or relay surface may report `unknown`
- but the consequence itself is: do not keep asserting a stronger hook-dependent `applicability` claim unless a profile-defined fallback explicitly permits it

This keeps the wire/local split clean:
- `unknown` may originate upstream or at a boundary
- the guarded `applicability` consequence is computed locally

## rev0046 provisional answer

The archive now has a first placement judgment for the optional reason layer.
Current judgment:
- reasons are **boundary-first**
- they may also appear in local assessed state
- and they are only **wire-admissible** when a profile already has a compact source-originated status path that makes that honest and useful

This preserves the wire/local split:
- the wire stays thin by default
- boundaries keep a place to explain downgrade, restatement, or unknown
- local assessed state can still carry the result into applicability and regime consequences

## rev0047 provisional answer

The archive now names a tiny optional surface for retained boundary explanation.
Current judgment:
- `boundary_context` is the smallest named wrapper that now earns itself
- it contains only `action` plus optional `reason`
- it accompanies local assessed state when retained boundary explanation matters

This keeps the architecture small:
- `TimeState` still carries current timing belief and consequence
- `boundary_context` carries only the explanatory wrapper for boundary handling

## rev0048 provisional answer

The archive now has a default lifetime rule for `boundary_context`.
Current judgment:
- `boundary_context` is state-coupled
- it expires with the local assessed state it explains
- the archive does **not** add an independent timer or retention ladder for the current wrapper

This keeps the new surface tiny and prevents retention machinery from growing faster than the semantics it is meant to support.

## rev0049 provisional answer

The archive now has a visibility rule for `boundary_context`.
Current judgment:
- `boundary_context` is requestable by default
- some profiles may make it default-visible when the explanation itself is operationally load-bearing
- it is not part of the globally always-exported minimal response surface

This keeps the wrapper aligned with the archive's general pattern:
- default state where omission is unsafe
- requestable explanation where the state is usually enough

## rev0050 provisional answer

The archive now reuses one shared discovery/request surface across:
- `profile_default` hook visibility
- and `boundary_context` visibility

Current judgment:
- the same small mechanism can serve both
- what differs is the subject requested, not the existence of a separate channel
- this keeps the response architecture smaller and more legible

## rev0051 provisional answer

The archive now treats the shared discovery/request surface as intentionally flat.
Current judgment:
- the mechanism is shared
- the request list is flat
- distinct item names carry the remaining separation between state visibility and explanation visibility

This is the smallest form that still preserves the archive's semantic distinctions.


## rev0052 provisional answer

The archive now tests named request bundles and declines to make them native.
Current judgment:
- profile requirements may bundle items at the profile/configuration layer
- the shared request surface remains item-level
- operator-facing aliases are allowed only if they lower to explicit item names
- item-level exposure results must remain visible

This keeps the greenfield response architecture flat:
- no second request taxonomy
- no hidden policy layer under bundle names
- no new result model just to explain mixed bundle outcomes

## rev0053 provisional answer

The archive now gives operator-facing aliases a local documentation boundary.
Current judgment:
- aliases may exist for human convenience
- they expand before exchange
- they are not protocol objects, profile-default requirements, or shared request names
- item-level results remain visible after expansion

This keeps the greenfield response architecture legible:
- profiles can require defaults
- operators can use local shorthand
- machine-facing requests remain explicit item names


## rev0054 provisional answer

The archive now gives the shared request list a default lifetime.
Current judgment:
- ordinary item requests are exchange-scoped
- repeated local preferences can repeat explicit item names
- profile-required visibility remains profile/default behavior
- sticky delivery, if ever needed, must be an explicit leased/subscription surface rather than an implied property of the request list

This protects the greenfield split:
- wire/request behavior stays concrete and local to an exchange by default
- local assessed state may remember operator preferences or profile policy
- no remote participant silently inherits an old request as a standing obligation


## rev0055 provisional answer

The archive now gives explicit optional requests a response-accounting rule.
Current judgment:
- request results are **negative-only**
- returned item content is enough to indicate success
- absent requested optional items may be accounted for as `unavailable`, `unknown`, or `omitted`
- the result names explicit item names, never aliases or bundles
- the result envelope is response-adjacent, not part of minimal `TimeState`

This preserves the greenfield split:
- wire/request behavior can account for optional item absence when the response surface supports it
- local assessed state records the consequence
- the core timing state does not become an error-reporting object


## rev0056 provisional answer

The archive now separates response well-formedness from profile satisfaction.

Current judgment:
- a wire claim may be authentic and parseable while failing a demanding profile contract
- missing required/default visibility is profile-nonconforming by default
- local assessed state may still compute a weaker timing state, but it must not preserve stronger hook-dependent `applicability`
- explicit fallback belongs to profile/local assessment, not to a universal wire error object

This strengthens the wire/local split:
wire claims carry what was said,
profile validation decides whether that was enough,
and local assessed state carries the downgraded consequence.

## rev0057 provisional answer

The local assessed object now earns one compact profile-conformance marker:

- `profile_conformance: satisfied | fallback | unsatisfied`

This belongs with local assessed state rather than the minimum wire claim. It summarizes local profile validation after required/default checks, optional request results, and downgrade rules have been applied. It does not create a generic profile-error object or a manifest of missing items.

## rev0058 provisional answer

Fallback does not add a third surface.

The greenfield split remains:
- wire claim: what was said
- local assessed state: what the receiver/exporter now judges

Within local assessed state:
- `profile_conformance` carries the validation outcome
- `applicability` carries the downstream use boundary

A fallback state therefore does not need `fallback_applicability`, bundle status, or a universal downgrade table.
It needs a profile-defined lower consequence expressed through existing applicability semantics.

If the assessed-state model cannot express that lower consequence, it should not export actionable fallback for the profile.

## rev0059 provisional answer

The greenfield split now treats profile identity as local/export scope.

The minimum wire claim still does not grow.
But when a local assessed object exports profile conformance, it needs either:
- an explicit `assessed_profile`, or
- a sealed single-profile enclosing boundary.

The compact local/export shape is now:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
applicability: <downstream-use-boundary>
```

This is not a profile manifest.
It is just enough scope for a receiver to know which validation rules produced the conformance outcome.
If the same timing state is assessed under multiple profiles, the assessments should be scoped separately rather than collapsed into one top-level verdict.

## rev0060 provisional answer

The greenfield split keeps profile-reference binding at the local/export layer.

The compact local/export shape remains:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
applicability: <downstream-use-boundary>
```

`<profile-ref>` is not a fixed object schema. It is a reference whose strength
is earned by the consuming boundary:
- `id + version/revision` for stable public profiles
- `authority + id + version/revision` for deployment or cross-operator profiles
- digest-backed reference for detached/audit/safety/compliance retention
- signed binding only when the issuer or binding must be verified independently

This preserves the source-packet/local-assessment split while making exported
conformance durable enough for serious boundaries.
