# PROBLEM FRAME

This is the current compact frame for the project.

## 1) The timing world is already plural

Time synchronization spans multiple mechanism families, source classes, and institutional layers.
TimeSync therefore should not begin as a claim that one missing protocol replaces everything.

## 2) Timing trust is multi-dimensional

The archive distinguishes:
- authenticity,
- correctness,
- uncertainty,
- provenance,
- freshness,
- regime,
- and downstream applicability.

These distinctions keep reappearing across the shared scenarios.

## 3) Timing is not only packet exchange

Timing systems are also about resilience architecture, holdover, source diversity, redundancy, detection, response, recovery, and governance.

## 4) Two tracks remain necessary

- integration track — work with current mechanisms and institutions
- greenfield track — explore what a better substrate would be from first principles

## 5) The archive now protects a small core while testing optional surfaces

The strongest current hypothesis is:
TimeSync needs a compact TimeState and a small control-surface family, with profiles layered around them.
Later revisions have mostly tested how little optional visibility, relay explanation, request machinery, human-facing alias documentation, and request lifecycle semantics can surround that core without widening it.

The current request-lifecycle rule is intentionally small: ordinary item requests are exchange-scoped unless a profile/default or explicit future lease says otherwise.


## rev0055 result-accounting rule

The archive now distinguishes absence cases more sharply:
- unrequested optional items may remain silent
- returned requested items are their own success result
- absent requested optional items get compact negative item accounting when the exchange has a result-capable response surface
- profile-required/default absence is a separate frontier, not an ordinary optional-request result

This keeps accountability item-level without promoting a general error taxonomy.


## rev0056 required/default absence rule

The archive now distinguishes well-formed exchange validity from profile satisfaction.

A response can remain parseable, authentic, and weakly useful while failing the active profile contract.
If a concrete profile boundary requires/defaults an item and the response omits it, full profile satisfaction fails by default and local assessed state must downgrade any hook-dependent consequence.

A profile may define an explicit degraded fallback, but fallback is weaker than full satisfaction.
This prevents required/default visibility from collapsing back into optional request behavior.

## rev0057 / rev0058 profile outcome rule

The archive now names profile validation outcome as local assessed state:

```text
profile_conformance = satisfied | fallback | unsatisfied
```

rev0058 keeps this from becoming a second policy vocabulary.
`fallback` is not an applicability label.
It means full profile satisfaction failed but a profile-defined weaker mode applies.
The remaining downstream use boundary must be carried by the existing `applicability` consequence signal.

If no safe weaker applicability can be expressed,
the local assessed state should not export an actionable fallback claim for that profile.

## rev0059 profile identity rule

The archive now scopes profile validation explicitly:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
```

`assessed_profile` is the profile whose rules were used to compute the conformance marker.
It is local/export metadata, not a mandatory minimum wire field.

Export rule:
if assessed state crosses a boundary with `profile_conformance`, the evaluated profile must be resolvable by the receiver unless the boundary is already sealed to exactly one profile.

This keeps `satisfied`, `fallback`, and `unsatisfied` from becoming unscoped verdicts.

## rev0060 profile-reference granularity rule

The archive now distinguishes profile identity from profile binding strength.

Explicit `assessed_profile` references are boundary-tiered:

```text
id + version/revision                      # enough when globally resolvable
authority + id + version/revision          # needed when names can collide
authority + id + version/revision + digest # needed when exact retained rules matter
signed profile-binding record              # needed only when issuer/binding must be independently verified
```

This does not create a universal profile-reference object.
It says that exported assessed state must carry enough reference strength for the
receiver to recover or verify the profile rules used for `profile_conformance`.

Profile distribution, profile certification, and profile negotiation remain out
of scope for the minimal TimeState claim.
