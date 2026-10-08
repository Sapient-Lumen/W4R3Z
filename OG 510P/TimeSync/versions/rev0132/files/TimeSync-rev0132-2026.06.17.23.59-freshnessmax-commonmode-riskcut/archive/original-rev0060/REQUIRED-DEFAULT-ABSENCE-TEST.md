# REQUIRED-DEFAULT-ABSENCE-TEST

This note closes the frontier left by rev0055.

rev0055 settled absence for explicitly requested optional items.
This note asks about a stronger case:
what if the item was not merely requested, but required or default-visible under the active profile boundary?

## Question

If a profile says an item must be visible by default and the response does not carry it,
should that be treated as:
- ordinary silence
- an optional request failure
- response invalidity
- local downgrade
- or both validity failure and local downgrade depending on consequence

## Source pattern

The source base points away from a one-word answer.

- NTPv5 separates a compact mandatory wire contract from optional extension fields. Missing expected extension fields can have item-level meaning, but that does not automatically make the entire packet syntactically invalid.
- NTPv5 also defines values that a server must maintain and expose in ordinary operation, such as leap indicator, stratum, root delay, root dispersion, and reference-ID behavior. Those are not optional request results.
- Roughtime treats mandatory tags and signed response contents as part of the response's validity shape. A response can be parseable while still failing the contract the client expected.
- PTP profile material is even more direct: a profile is a set of constraints on required, allowed, and forbidden options and values. If a clock violates those constraints, it has not satisfied that profile, even if some underlying messages remain intelligible.
- Synchrophasor-style timing quality reinforces the same pressure: where traceability, accuracy, leap status, or dimension semantics are measurement-bearing, absence is not neutral runtime silence.

The common pattern is:
**profile-required/default visibility is a contract-satisfaction question first, then a local consequence question.**

## Three validity layers

The archive now distinguishes three layers that were previously easy to blur.

### 1. Packet / exchange validity

A message can be well-formed, authenticated, and useful for some weaker purpose even when it does not satisfy a demanding profile.

This layer asks:
- can the response be parsed
- is the integrity boundary acceptable
- are the minimal timing fields usable at all

### 2. Profile satisfaction

A response either satisfies the active profile contract or it does not.

If the active profile says `traceability_posture`, `sync_dimension`, or `boundary_context` must be default-visible at this boundary,
then unexplained absence means the response does **not** satisfy that profile by default.

### 3. Local assessed consequence

A receiver still has to decide what to do locally.
It may:
- reject the response for the profile
- downgrade to a weaker local `applicability`
- enter a degraded regime
- retain only generic timing usefulness
- or use a profile-defined fallback

This is not a universal downgrade table.
It is a rule against silent preservation of stronger claims.

## Current archive rule

A missing profile-required/default item is:

> **profile-nonconforming by default, and locally downgrade-triggering.**

That does not mean every such response is a malformed packet.
It means the response cannot be counted as satisfying the profile whose default-visible item is missing.

## Rules

1. **Tier membership alone is not enough.**
   A hook being in the archive's `profile_default` tier does not make it required in every exchange.
   It becomes required only when a concrete profile boundary declares it default-visible or mandatory.

2. **Required/default absence fails profile satisfaction.**
   If the active profile requires the item in the response and it is absent, the full profile contract is unsatisfied unless the profile itself defines a fallback.

3. **Local downgrade follows.**
   Any stronger `applicability`, `regime`, or operator display that depends on the missing item must be withdrawn or weakened.
   Missing evidence cannot preserve a stronger hook-dependent claim.

4. **Fallback must be explicit and weaker.**
   A profile may define that `unknown`, `unavailable`, or a legacy absence maps to a degraded operating mode.
   That mode is not the full satisfied profile.
   It is a named or documented fallback consequence.

5. **Optional request accounting does not rescue required absence.**
   The rev0055 `unavailable | unknown | omitted` result shape is for absent explicitly requested optional items.
   A required/default item missing from the default response is a profile-conformance failure, not just an optional request result.

6. **`omitted` is especially weak for required/default items.**
   If a required/default item may be silently omitted without consequence, the profile did not truly require it.
   A profile can define a rare authenticated omission rule, but that is a fallback rule, not the base meaning of required visibility.

7. **No universal protocol error is added.**
   The archive does not create a generic `invalid`, `denied`, or `profile_error` wire taxonomy here.
   The validity judgment belongs first to profile satisfaction and local assessment.

## Compact decision table

| Situation | Profile satisfaction | Local consequence |
|---|---|---|
| Generic exchange, item not required | no failure | ordinary optional absence |
| Item requestable, requested, absent | profile may still be satisfied | rev0055 negative optional result if result-capable |
| Profile requires item, item absent, no fallback | unsatisfied | reject full-profile state or downgrade to weaker local use |
| Profile requires item, protected `unknown` with fallback | degraded/fallback only | withdraw stronger hook-dependent applicability |
| Profile requires item, `unavailable` | unsatisfied unless profile defines degraded mode | treat responder/boundary as not full-profile capable |
| Profile requires item, legacy/non-result-capable response | unsatisfied by default | use only if profile explicitly allows legacy fallback |

## Consequences by current item

### `traceability_posture`

At a P5-like measurement boundary or a P4-like live control boundary where traceability posture is default-visible,
absence means the full traceability-bearing profile is not satisfied.

The local system may still keep a weaker time estimate,
but it must not keep displaying or exporting a traceability-dependent applicability label.

### `sync_dimension`

This hook remains profile-declared first.
If the profile declaration itself is the trusted surface, then the response has not omitted the required evidence.

But if the profile says the response must carry or echo the synchronization dimension,
then absence makes the dimension-bearing profile unsatisfied.
A system cannot keep treating a response as frequency-safe, phase-safe, or time-safe merely because the dimension was expected.

### `boundary_context`

`boundary_context` is usually requestable, not globally default-visible.
When a profile makes transition explanation default-visible, absence means the transition explanation contract was not met.

That should not become a generic error taxonomy.
It is a local/profile failure to provide a required explanation surface.

## Placement

This rule lives in **profile validation and local assessed state**.
It is not a new mandatory field in minimal `TimeState`.

rev0057 exposes the compact local marker as:

```text
profile_conformance: satisfied | fallback | unsatisfied
```

The marker is local assessed metadata, not a mandatory wire field.
The important rule remains semantic:
profile-required/default absence cannot silently pass as full profile satisfaction.

## Reduction result

The archive does **not** add:
- a full profile manifest
- alias-level or bundle-level validity
- a universal protocol error object
- mandatory reason strings for every omission
- or a global rule that the whole packet must be discarded

It adds only this distinction:

```text
well-formed response != satisfied profile
missing required/default item => profile unsatisfied by default + local downgrade
```

## What this settles

This note settles the rev0055 frontier:
required/default absence is both a profile-contract problem and a local consequence trigger.

The response may remain usable for weaker purposes,
but it must not be accepted as satisfying the full profile whose required/default item is missing.

## What this still does not settle

This note does not decide:
- how much of profile validation should be exposed to downstream clients
- how authenticated or versioned profile declarations should be bound to individual exchanges

## rev0057 follow-on

rev0057 names the local consequence of this test:

- full profile obligations met: `profile_conformance = satisfied`
- explicit weaker profile mode applies: `profile_conformance = fallback`
- required/default absence with no accepted fallback: `profile_conformance = unsatisfied`

This keeps the rev0056 distinction intact: a response can remain well-formed while local assessed state refuses to count it as profile-satisfied.

## rev0059 follow-on

rev0059 resolves the profile-identity frontier left open here.

Required/default absence is now evaluated under a resolvable profile scope:

```text
assessed_profile: <profile-ref>
profile_conformance: satisfied | fallback | unsatisfied
```

The same missing item may have different consequences under different profiles.
Therefore a downstream receiver must know which profile made the item required/default-visible before it can interpret the conformance result.
