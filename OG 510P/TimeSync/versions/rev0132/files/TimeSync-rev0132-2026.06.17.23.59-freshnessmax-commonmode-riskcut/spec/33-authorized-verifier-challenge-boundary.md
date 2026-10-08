# 33 — Authorized verifier challenge boundary

rev0070 closes FT-0069 by defining a minimal, detached authorized-verifier challenge result for redacted salted commitments.

## Decision

TimeSync may record that an authorized verifier challenged a redacted commitment and received a match result, but ordinary TimeSync exchange and retained evidence summaries must not carry the salt or preimage.

The actual disclosure of salt, preimage, or selective-disclosure proof material occurs outside TimeSync through an authorized channel. The TimeSync artifact carries only:

```text
challenge identity
verifier authorization summary
target summary / assessment / profile binding
target commitment value(s)
requested disclosure class
result status
opaque receipt reference and digest
non-provenance / non-reassessment boundary flags
```

## Placement

The challenge result is represented by:

```text
schema/authorized-verifier-challenge.schema.json
examples/evaluator/authorized-verifier-challenge-result-p3-redacted.json
```

It is not embedded in the six-field TimeState core. It is not an extension hook. It is not a profile assessment conclusion. It is not an evaluator evidence summary input item. It may be retained as a detached challenge record or returned as a requestable result item when policy allows.

## Boundary rules

A challenge result must say:

```text
salt_preimage_material_location: external_authorized_channel_only
ordinary_exchange_allowed: false
ordinary_retained_summary_allowed: false
challenge_result_is_profile_evidence: false
challenge_result_reopens_assessment: false
external_provenance_interpreted_by_timesync: false
```

If a result is present, it must also say:

```text
disclosure_does_not_update_timestate: true
disclosure_does_not_reassess_profile: true
disclosure_cannot_satisfy_profile_obligation: true
disclosure_not_timesync_provenance: true
ordinary_retained_summary_must_not_include_preimage: true
```

The challenge result can prove only that an authorized external disclosure review matched or failed to match a commitment. It cannot upgrade traceability, freshness, source diversity, profile conformance, validity horizon, or current actionability.

## Evidence class rule

rev0070 adds the evidence class:

```text
authorized_verifier_disclosure
```

It has `may_satisfy_profile_obligation: false`. This lets a summary or retained review surface mention a challenge/disclosure receipt without making that receipt profile evidence.

## Target binding

A challenge result targets one evidence summary and one assessment:

```text
summary_id
assessment_id
assessed_profile
target commitment item name(s)
target commitment value(s)
```

If a referenced evidence summary is carried alongside the challenge result, the validator checks that the target commitment appears in the summary.

## What remains external

TimeSync does not define:

```text
verifier identity proofing
legal authority
credential issuance
selective-disclosure proof verification
external audit chain of custody
salt or preimage transport
operator-specific disclosure workflow
```

Those systems may be referenced through opaque receipt handles and digests. TimeSync does not parse their provenance or credential semantics.

## Negative fixture pressure

rev0070 adds negative fixtures for:

```text
expired challenge result
challenge target commitment not present in the referenced evidence summary
preimage or salt material exported inside a TimeSync challenge record
authorized_verifier_disclosure used as profile-obligation evidence
malformed discovery-returned challenge result
```

## rev0071 portability/replay/revocation tightening

rev0071 keeps the rev0070 disclosure boundary and adds a second boundary: a challenge result may be portable only as a commitment-verification receipt for the same summary, assessment, assessed-profile digest, and target commitment.

The new fields are:

```text
portability_boundary
challenge_result.portable_result_state
replay_context
```

They do not make the challenge result profile evidence. They only let a receiver distinguish a still-usable commitment-verification receipt from a stale, revoked, cross-profile, or cross-operator replay attempt.

Cross-operator replay requires a digest-bound profile compatibility statement and remains subject to local policy.
