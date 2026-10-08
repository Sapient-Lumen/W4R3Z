# FALLBACK APPLICABILITY VOCABULARY TEST

## Question

After rev0057 adds:

```text
profile_conformance = satisfied | fallback | unsatisfied
```

does `fallback` need its own shared weakened-applicability vocabulary?

Candidate pressure:
- `fallback` is safer than silence
- but a receiver still needs to know what the downgraded state is good for
- a bare fallback marker could become a polite way to keep exporting an unsafe consequence

## Source pattern

The source pattern does not support a second shared consequence vocabulary.

- NTPv5 keeps the ordinary wire protocol narrow and explicitly leaves filtering, source selection, clock control, and other algorithms out of the core protocol.
- NTPv5 extension behavior remains item-specific: optional fields can be included, omitted, or interpreted at item level, not by a broad semantic downgrade lattice.
- Roughtime separates a compact signed response from local/ecosystem policy and deliberately avoids a general error-reporting mechanism.
- RFC 9760 treats PTP profiles as constraints over required, allowed, and forbidden options and profile-specific defaults.
- NIST smart-grid and TMAS material show why downstream applications need uncertainty / traceability / timing-status meaning, but those needs are application-shaped rather than globally tier-shaped.
- Finance clock-sync rules show the same pattern from another side: a timing state can be adequate for one regulated use and inadequate for another because the tolerance and evidence requirements differ.

The common lesson is:
profile fallback must be explicit enough for downstream use, but its meaning is defined by the profile and exported applicability, not by a universal fallback label set.

## Failure mode if we add shared fallback labels

A shared fallback vocabulary would likely duplicate `applicability`.

For example:
- `fallback_local_only`
- `fallback_monitoring_only`
- `fallback_not_control`
- `fallback_not_traceable`
- `fallback_coarse_time_only`

Those are not wrong ideas.
But they are applicability consequences.
Putting them in a second fallback-specific lane would create two competing answers to the same downstream question:

> What uses should trust this assessed state now?

The archive already gave that job to `applicability`.

## Failure mode if fallback remains bare

A bare `profile_conformance = fallback` is also not enough.

It tells a receiver that full profile satisfaction failed and an accepted weaker mode exists.
It does not by itself say whether the state is still acceptable for:
- coarse logging
- routine authentication
- frequency transfer
- phase-sensitive protection
- financial timestamping
- audit-only reconstruction
- local continuity

Therefore fallback may not travel alone when the state is exported for action.

## Test result

Do **not** add a shared fallback-applicability vocabulary.

Do add one tight invariant:

```text
profile_conformance = fallback
requires an explicit non-stronger applicability boundary.
```

That boundary lives in the existing `applicability` field or in the profile's already-defined consequence mapping.
It is not a new field family.

## Proposed rule

When local assessed state exports `profile_conformance = fallback`:

1. The exported `applicability` must be no stronger than the applicability that full profile satisfaction would have supported.
2. Any hook-dependent applicability claim whose evidence is missing must be withdrawn or weakened.
3. The weakened applicability must be defined by the active profile, local deployment profile, or audited boundary context.
4. If no adequate weakened applicability label exists, the state should export as `unsatisfied` for that profile, or as diagnostic/local-only state outside the profile claim.

Compactly:

```text
fallback is a conformance outcome;
applicability carries the remaining use boundary.
```

## Minimal examples

### Finance / traceable timestamping

If the active profile requires NIST/UTC-traceable evidence and that evidence is missing,
`fallback` cannot preserve a regulated timestamping applicability claim.
A weaker local recordkeeping or diagnostic label might survive if the profile defines it,
but the original compliance-shaped applicability is gone.

### Smart-grid / synchrophasor use

If required timing-quality or traceability status is missing,
`fallback` may preserve a monitoring-only or non-protection use only if the profile defines that consequence.
It must not silently preserve phase-sensitive control applicability.

### Telecom frequency versus phase/time

A degraded state may still be useful for a frequency-oriented lane while failing a time/phase lane.
That is profile-local applicability, not a universal fallback label.

### General computing

A local system may continue coarse logging or user-interface time display after losing a stronger profile condition.
That does not mean it still satisfies a high-integrity ordering, audit, or traceability profile.

## Interaction with `profile_conformance`

`profile_conformance` answers:

> Did the assessed state satisfy the active profile, only a defined weaker mode, or neither?

`applicability` answers:

> What downstream uses should trust this state now?

These fields are adjacent but not redundant.
The first summarizes validation outcome.
The second carries use consequence.

## Interaction with request results

Absent requested optional items still use rev0055 item-level accounting when result-capable.
That accounting may be one input to fallback assessment.
It does not create fallback labels.

## Interaction with required/default absence

Missing required/default evidence usually blocks `satisfied`.
If the profile defines a weaker mode, the local outcome may be `fallback`.
But the lowered use boundary must be expressed through existing applicability semantics.

## Interaction with aliases and bundles

Operator aliases do not get fallback statuses.
Named bundles do not get fallback statuses.
Fallback belongs to local profile validation and assessed consequence,
after aliases have expanded and item-level accounting has been applied.

## Non-goals

This test does not add:
- a global fallback taxonomy
- a second `fallback_applicability` field
- a compliance verdict vocabulary
- a per-sector use registry
- a universal downgrade table
- a manifest of all surviving uses

## Archive judgment

Fallback does **not** need a shared weakened-applicability vocabulary.

It needs a stronger invariant:

```text
fallback must not be bare;
existing applicability must carry the explicit lowered use boundary.
```

If the system cannot express a safe lower applicability boundary,
it should not export `fallback` as an actionable profile state.
It should export `unsatisfied` for that profile or keep the state diagnostic/local.

## rev0059 follow-on

rev0059 adds the missing scope for fallback.

A fallback claim is not safe unless the receiver can resolve which profile allowed the fallback.
Therefore actionable exported fallback now needs:

```text
assessed_profile: <profile-ref>
profile_conformance: fallback
applicability: <non-stronger downstream boundary>
```

A sealed single-profile boundary may provide `assessed_profile` by context.
Across mixed, relayed, audited, or detached boundaries, explicit profile scope is preferred.
