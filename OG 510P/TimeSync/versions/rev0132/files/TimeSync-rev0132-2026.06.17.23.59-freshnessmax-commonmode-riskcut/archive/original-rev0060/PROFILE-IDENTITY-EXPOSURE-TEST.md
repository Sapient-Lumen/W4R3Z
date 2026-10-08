# PROFILE IDENTITY EXPOSURE TEST

## Question

Now that local assessed state may carry:

```text
profile_conformance = satisfied | fallback | unsatisfied
```

and rev0058 says `fallback` is profile-local while `applicability` carries the lowered use boundary,
must the assessed state also name the profile being evaluated?

Candidate terms:
- `active_profile`
- `assessed_profile`
- `profile_ref`

## Pressure

A conformance marker without profile identity is under-scoped.

`profile_conformance = satisfied` only means:

> satisfied under some profile's required/default obligations.

`profile_conformance = fallback` only means:

> full satisfaction failed, but that same profile defines a weaker acceptable mode.

If the receiving boundary does not know which profile supplied those rules,
the marker can become false reassurance.
The same timing state may satisfy a coarse logging profile, fall back under a traceable-audit profile, and be unsatisfied for phase-sensitive control.

But adding too much profile machinery would bloat the archive.
A universal profile registry, profile manifest, negotiation exchange, or profile hash grammar would turn a small local marker into a management subsystem.

## Source pattern

Current protocol and profile patterns support **resolvable identity at the boundary**, not a universal profile manifest in every timing exchange.

- NTPv5 keeps the wire protocol narrow, makes protocol-version support explicit where needed, and leaves local algorithms and source-selection judgments outside the core protocol.
- NTS separates key-establishment / parameter negotiation from later time packets; context can be established explicitly outside the ordinary packet path and then relied on by a bounded association.
- Roughtime uses compact tag and key identities for message interpretation and evidence, but does not attach a broad profile manifest to every signed time response.
- RFC 9760 treats PTP profiles as real selections of attribute values, defaults, required options, permitted options, and prohibited options. The profile is a configuration/management fact with semantic force.

The common lesson:
profile identity must be knowable where conformance is consumed,
but it does not need to become a new wire-negotiation layer.

## Test result

Add a compact assessed-state companion:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
```

`assessed_profile` names the profile under which the conformance marker was computed.
It is preferred over `active_profile` because the important exported fact is not merely which profile a local node is trying to run,
but which profile's rules were actually used for this assessment.

## Export rule

When local assessed state crosses a boundary and carries `profile_conformance`, the evaluated profile must be **resolvable** by the receiver.

That can happen in either of two ways:

1. The state explicitly carries `assessed_profile`.
2. The enclosing boundary is already sealed to exactly one profile by configuration, contract, or authenticated session context.

If neither is true, do not export actionable `profile_conformance`.
Export weaker diagnostic state, or omit the marker.

Compactly:

```text
profile_conformance is scoped by assessed_profile.
```

## What counts as resolvable

A profile reference is resolvable if the consuming boundary can map it to the validation rules that produced the conformance marker.

It may be:
- a standards/profile identifier
- a deployment profile name plus authority
- a versioned local policy reference
- an audit-contract reference
- a digest-backed profile reference, where the boundary already uses digests

The archive does **not** yet require one global grammar.
The minimum is boundary resolvability, not global publication.

## Why not rely only on surrounding configuration

Surrounding configuration is enough only inside a sealed single-profile boundary.

It is not enough when:
- an assessed state is exported to a different operator, service, relay, appliance, or audit boundary
- multiple profiles may be active on the same host or interface
- the same state is assessed for multiple downstream uses
- fallback behavior is profile-specific
- a receiver stores the state for later audit, detached from the original configuration

In those cases, hidden configuration makes `satisfied`, `fallback`, and `unsatisfied` ambiguous.

## Why not require the field everywhere

Some contexts really are single-profile and sealed.

For example:
- a tightly managed appliance fleet with one audited timing profile
- a local diagnostic view inside one configured service
- an authenticated session whose setup already selected the profile and binds all later exports to it

For these cases, requiring `assessed_profile` in every local view would be redundant.
The rule is export-boundary resolvability, not mandatory repetition.

## Multi-profile assessment

Do not make one top-level `profile_conformance` silently cover multiple profiles.

If one timing state is assessed under several profiles, use separate scoped assessment records, or separate exports, such as:

```text
assessment[logging].assessed_profile = logging-basic@2026
assessment[logging].profile_conformance = satisfied
assessment[logging].applicability = coarse_logging

assessment[audit].assessed_profile = traceable-audit@2026
assessment[audit].profile_conformance = fallback
assessment[audit].applicability = local_recordkeeping_only
```

This is not a manifest of all possible profiles.
It is only a way to avoid pretending that one conformance value has universal meaning.

## Interaction with `applicability`

`assessed_profile` answers:

> Under which profile were the rules evaluated?

`profile_conformance` answers:

> Did this assessed state satisfy that profile, only a defined fallback, or neither?

`applicability` answers:

> What use boundary remains safe now?

These three are not interchangeable.
A receiver needs all three when an assessed state is exported for action across a mixed or auditable boundary.

## Interaction with wire claims

This decision does not add `assessed_profile` to the minimal wire claim.

A source packet may remain small.
A local assessed object may add profile identity after it validates the packet, applies item-level request results, checks required/default visibility, and computes downstream consequence.

If a future protocol profile wants to carry profile identity on the wire, it may do so as a profile feature.
That does not force the minimal TimeState or all timing packets to grow.

## Interaction with aliases and bundles

Operator aliases do not become profile identifiers.
Named request bundles do not become profile identifiers.

A profile reference names validation rules and defaults.
An alias names a local convenience expansion.
A bundle, if ever used, would name a request preset.

Those must not collapse into one label.

## Non-goals

This test does not add:
- a global profile registry
- a profile negotiation protocol
- a profile manifest
- a universal profile hash field
- a compliance certificate
- alias-to-profile promotion
- bundle-level conformance
- mandatory profile identity in every source packet

## Archive judgment

Add the rule:

```text
Exported profile_conformance must be scoped by a resolvable assessed_profile,
unless the enclosing boundary is already sealed to exactly one profile.
```

The selected companion is `assessed_profile`, not `active_profile`.

This keeps the profile marker usable without widening the ordinary timing exchange.
It also keeps fallback honest: a receiver can know which profile allowed the fallback and which applicability boundary remains.

## rev0060 follow-up

rev0060 answers the reference-granularity question with a boundary-tiered rule:
`id + version/revision` when unambiguous, plus authority, digest, or signed
profile-binding only when the consuming boundary needs that stronger binding.
