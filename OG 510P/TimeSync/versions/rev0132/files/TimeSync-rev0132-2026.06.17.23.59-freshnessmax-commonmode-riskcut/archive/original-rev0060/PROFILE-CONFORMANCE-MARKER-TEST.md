# PROFILE CONFORMANCE MARKER TEST

## Question

After rev0056 separates **well-formed exchange validity** from **profile satisfaction**, does local assessed state need a compact shared profile-conformance outcome?

Candidate outcome:
- `satisfied`
- `fallback`
- `unsatisfied`

## Pressure

rev0056 made missing profile-required/default visibility profile-nonconforming by default and locally downgrade-triggering.
That is enough for a single validator, but it is thin for downstream consumers that receive local assessed state from an agent, relay, appliance, service, or audit boundary.

Without a marker, each downstream consumer must rediscover profile validation from profile-specific hidden logic.
That repeats complexity and makes downgrade hard to see.

With too much marker machinery, the archive risks inventing a generic profile error layer, capability manifest, or policy workflow.
That would violate the current reduction discipline.

## Source pattern

Current sources support a small local outcome more strongly than a wire-level profile-error object.

- NTPv5 keeps the main wire protocol narrow and leaves source selection, filtering, and clock discipline outside the core wire exchange.
- NTPv5 algorithm guidance says algorithms need explicit behavior when required extension fields are not present.
- Roughtime carries compact signed time evidence and deliberately avoids a general protocol error-reporting mechanism for malformed or unsupported cases.
- PTP profiles constrain required, allowed, and forbidden behavior; conformance is therefore profile-shaped rather than just packet-shaped.

The common pattern is:
- profile satisfaction matters
- missing required supporting material needs explicit handling
- but the ordinary exchange should not become a broad diagnostic/error grammar

## Test result

The marker earns itself, but only as a **local assessed-state outcome**.

It should not be a mandatory wire field.
It should not be an alias result.
It should not be a replacement for item-level request accounting.
It should not enumerate all missing items.

## Proposed local field

`profile_conformance`

Allowed values:

### `satisfied`

The active profile's required/default obligations are met for the assessed state.

This does not mean the time is perfect.
It means the state is being judged under the named profile and the profile's required surfaces and constraints are satisfied enough to support the exported applicability.

### `fallback`

The full profile is not satisfied, but the active profile defines an explicit weaker mode that may still be exported.

Rules:
- fallback is never full satisfaction
- fallback must name or imply a weaker applicability boundary
- fallback must not preserve hook-dependent claims whose evidence is missing
- fallback is profile-defined, not an automatic universal rescue

### `unsatisfied`

The active profile is not satisfied and no accepted fallback applies.

Rules:
- a response may still be syntactically well-formed
- local state may still carry weak or diagnostic value
- but the state must not be exported as satisfying the active profile

## Why three states are enough

The marker needs to answer only one downstream question:

> Can this assessed state be treated as satisfying the active profile, only a defined weaker fallback, or neither?

That is smaller than:
- a failure-code registry
- a per-item manifest
- a policy decision log
- a negotiation transcript
- a global `profile_error` object

Item-level details remain where they already belong:
- requested optional absence: rev0055 negative item accounting
- required/default absence: rev0056 profile-nonconforming downgrade trigger
- local explanation: optional boundary context / reason vocabulary where already earned

## Placement

Best placement:
- local assessed state
- audit/export metadata derived from local assessed state

Poor placements:
- mandatory wire claim field
- discovery/request exposure class
- operator alias layer
- bundle-level result

The marker is downstream-facing.
It summarizes the local validation outcome after profile rules, request results, required/default checks, and local downgrade logic have been applied.

## Interaction with existing archive rules

### With optional request results

A requested optional item can be absent with `unavailable`, `unknown`, or `omitted`.
That does not automatically make `profile_conformance = unsatisfied`.
It matters only if the active profile or exported applicability depends on that item.

### With required/default visibility

Missing required/default visibility normally prevents `satisfied`.
The outcome is:
- `fallback` if the profile explicitly defines a weaker acceptable mode
- otherwise `unsatisfied`

### With unknown

`unknown` should not silently preserve `satisfied` when the unknown item is required for the exported claim.
The profile must either define a fallback or the state becomes `unsatisfied`.

### With relays

A relay may restate its own local assessed state and mark it independently.
It must not upgrade upstream `fallback` or `unsatisfied` into `satisfied` unless it has new local evidence and profile rules that justify the stronger state.

## Non-goals

This test does not add:
- a machine-readable profile manifest
- a universal list of failure reasons
- a profile negotiation mechanism
- named request bundles
- alias-level status
- packet-level invalidity for every missing required/default field

## Archive judgment

Add a compact local assessed-state marker:

`profile_conformance = satisfied | fallback | unsatisfied`

This is the smallest shared outcome that makes rev0056 usable downstream without turning conformance into a new protocol subsystem.

## rev0058 follow-on

rev0058 resolves the fallback vocabulary frontier.

Current answer:
- no shared fallback-applicability vocabulary
- no `fallback_applicability` field
- `profile_conformance = fallback` must pair with an explicit non-stronger `applicability` boundary when exported for action
- fallback remains profile-defined and weaker than satisfaction

## rev0059 follow-on

rev0059 scopes the conformance marker.

Current answer:
- `profile_conformance` must be interpreted under a profile
- exported assessed state should carry `assessed_profile` unless the boundary is already sealed to one profile
- `assessed_profile` names the rules used for this assessment, not merely the operator's intended active mode
- if the profile is not resolvable to the receiver, the conformance marker should not be exported as actionable

Compactly:

```text
assessed_profile + profile_conformance + applicability
```

is the local/export triad.
It is not a profile manifest or wire negotiation surface.
