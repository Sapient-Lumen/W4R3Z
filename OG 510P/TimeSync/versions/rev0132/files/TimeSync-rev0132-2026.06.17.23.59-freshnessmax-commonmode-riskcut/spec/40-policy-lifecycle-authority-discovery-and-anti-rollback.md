# 40 — Policy lifecycle authority discovery, renewal hints, and anti-rollback sequencing

## Status

Normative in rev0077.

This section closes FT-0076. It defines a compact lifecycle-authority reference for transparency trust-policy status without importing a policy repository, trust-anchor system, revocation protocol, endpoint registry, transparency log, or provenance graph.

## Motivation

rev0076 could say whether a transparency trust-policy digest was active, expired, revoked, superseded, or drifted at a replay-visibility evaluation. It deliberately did not say how a receiver knew which lifecycle authority stated that status, whether the status was stale or rolled back, or whether a successor policy digest was discoverable.

That missing seam matters because a stale lifecycle status can make an old policy look current, and a replayed status record can make a revoked or superseded policy appear active. TimeSync still does not define the external lifecycle authority. It only records a digest-bound summary of authority discovery, renewal hint, and anti-rollback sequence posture.

## `lifecycle_authority_reference`

A `transparency_trust_policy_reference` now contains `lifecycle_authority_reference`.

The object binds:

- the lifecycle authority identity by opaque `authority_id` plus digest,
- the trust-policy digest whose lifecycle status is being evaluated,
- how the lifecycle authority was discovered or configured,
- whether a successor/renewal hint exists,
- a monotonic status sequence check,
- a freeze/staleness check,
- non-interpretation guardrails.

The object is intentionally a summary. It does not export repository topology, status endpoints, APIs, trust-anchor material, status protocol messages, policy language, legal authority detail, witness/monitor rosters, verifier identities, or external provenance.

## Authority discovery boundary

`discovery.discovery_state` can be:

- `configured_authority`
- `authority_statement_digest_bound`
- `compatibility_statement_bound`
- `unknown_or_redacted`

Current replay visibility requires a known, digest-bound, or locally configured discovery posture. `unknown_or_redacted` cannot support current replay visibility.

A compatibility-bound discovery must carry a `compatibility_statement_digest`. That digest binds the compatibility statement; it does not import that statement's trust framework, signatures, trust anchors, or authority registry into TimeSync.

## Renewal hint boundary

`renewal_hint` may say that a successor digest or renewal path exists. It is advisory and lifecycle-scoped only.

A hint with `successor_digest_available` or `renewal_available` must carry:

- `successor_policy_digest`, and
- `expected_next_sequence`.

The hint cannot update profile assessment, current actionability, traceability, source diversity, verifier authorization, or TimeSync provenance.

## Anti-rollback and freeze boundary

`anti_rollback_sequence` records a compact monotonic lifecycle-status posture.

Current replay visibility requires:

- `monotonicity: monotonic_checked`,
- `rollback_status: no_rollback_detected`,
- `freeze_check.status: fresh`,
- `observed_status_age_seconds <= max_status_age_seconds`,
- sequence state not updating the profile assessment.

A stale, unchecked, rolled-back, sequence-gap, or non-monotonic lifecycle status cannot support current replay visibility. It may still be retained as a historical status artifact, but TimeSync does not make it current replay evidence.

## Cross-operator sequence equivalence

`transparency_policy_equivalence.policy_lifecycle_equivalence.sequence_equivalence` summarizes whether subject and related lifecycle-policy authorities have compatible anti-rollback/freeze posture.

Current cross-operator replay-visibility equivalence requires:

- both subject and related sequence status to be `monotonic_checked`,
- no rollback detected,
- fresh sequence status,
- a sequence relation other than `weaker_or_unknown`,
- replay-visibility-only non-upgrade semantics.

This does not make lifecycle authorities equivalent for policy language, trust anchors, proof formats, monitor/witness requirements, or profile evidence. It only constrains replay-visibility threshold interpretation.

## Validation requirements

The rev0077 validator rejects:

- current replay visibility under unknown lifecycle-authority discovery,
- current replay visibility under rollback, sequence-gap, stale, or unchecked status sequence,
- renewal hints that name a successor/renewal without successor digest and next sequence,
- sequence numbers that move backward or fail monotonic comparison,
- authority discovery that exports repository topology, status endpoints, APIs, or trust anchors,
- cross-operator sequence equivalence that is weaker or unknown,
- discovery-returned policy references with malformed lifecycle-authority posture.

## Non-goal

TimeSync still does not define a policy repository, publication protocol, status API, key-discovery mechanism, trust-anchor lifecycle, witness protocol, transparency log, or credential system. A lifecycle-authority reference is only a bounded review surface for a policy digest already referenced elsewhere.
