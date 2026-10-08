# 41 — Lifecycle-authority rotation, delegation, and compromise-response boundary

## Status

Normative in rev0078.

This section closes FT-0077. It defines a compact rotation/delegation/compromise-response posture for a transparency trust-policy lifecycle authority without importing a key-management system, delegation protocol, authority registry, status repository, incident-response record, forensic package, or provenance graph.

## Motivation

rev0077 can say that a policy lifecycle authority was discovered, renewal-hinted, fresh, monotonic, and not rolled back. That is not sufficient when the lifecycle authority itself rotates, delegates status publication, or becomes compromised. A stale but monotonic authority may still be the wrong authority after a rotation; a delegated status publisher may be valid only for a narrow scope; and a compromise response may make replay visibility historical or contested without changing the underlying TimeState or profile assessment.

TimeSync still does not define the external authority system. It records only enough summary posture for a receiver to decide whether replay visibility remains current under local policy.

## `rotation_delegation_status`

`policy_lifecycle_authority_reference` now contains `rotation_delegation_status`.

The object summarizes:

- lifecycle-authority rotation state,
- optional successor authority digest,
- delegated status/revocation publication posture,
- compact compromise-response state,
- non-interpretation guardrails.

It intentionally does not export authority key material, key identifiers, delegation chains, authority rosters, rotation protocol messages, repository topology, status endpoints, incident forensics, credential material, legal-authority detail, or external provenance.

## Rotation boundary

`rotation_state` can be:

- `current_authority_active`
- `planned_rotation_to_successor`
- `successor_authority_active`
- `rotation_not_applicable`
- `unknown_or_redacted`

Current replay visibility cannot rely on `unknown_or_redacted`. A planned rotation must carry a `successor_authority_digest`, and that digest must not equal the current `authority_digest`. A planned or successor-active rotation also requires a `rotation_statement_digest`.

A rotation statement digest is an anchor for local review. It is not a public key, authority roster, protocol transcript, or trust-anchor export.

## Delegation boundary

`delegation_state` can be:

- `not_delegated`
- `delegated_status_publication`
- `delegated_revocation_publication`
- `delegated_lifecycle_and_revocation`
- `unknown_or_redacted`

Current replay visibility cannot rely on `unknown_or_redacted` delegation posture. Any delegated posture must carry a concrete `delegation_scope` and a `delegation_digest`. `not_delegated` must use `delegation_scope: none`.

A delegation digest is a compact review handle. TimeSync does not export the delegation chain, delegated authority roster, key material, trust-anchor material, status endpoint, or delegation protocol.

## Compromise-response boundary

`compromise_response.state` can be:

- `none_known`
- `suspected_under_review`
- `confirmed_contained`
- `confirmed_unresolved`
- `unknown`

Current replay visibility requires no unresolved compromise. `suspected_under_review`, `confirmed_unresolved`, and `unknown` cannot support current replay visibility. `confirmed_contained` can remain current only if the record says the compromise has `replay_visibility_effect: no_current_effect` and binds a successor or recovery authority digest plus response digest.

Compromise-response metadata may make replay visibility historical, contested, or unknown. It never reopens the profile assessment, updates TimeState, exports incident forensics, or becomes TimeSync provenance.

## Cross-operator authority-rotation equivalence

Replay-transparency policy-equivalence compatibility statements now contain `policy_lifecycle_equivalence.authority_rotation_equivalence`.

Current cross-operator replay-visibility equivalence requires:

- known subject and related rotation states,
- known subject and related delegation states,
- authority-rotation relation not `weaker_or_unknown`,
- delegation relation not `weaker_or_unknown`,
- compromise-response relation not contested, unknown, or weaker,
- replay-visibility-only non-upgrade guardrails.

This equivalence does not equate authority registries, trust anchors, key material, delegation chains, rotation protocols, compromise forensics, policy language, profile evidence, or provenance.

## Validation requirements

The rev0078 validator rejects:

- unknown rotation posture used for current replay visibility,
- delegated lifecycle authority posture without delegation digest/scope,
- unresolved or unknown authority compromise used for current replay visibility,
- contained compromise without recovery/successor digest and response digest,
- authority key material, delegation chains, authority rosters, rotation protocols, or compromise forensics exported through TimeSync,
- weaker or unknown cross-operator authority-rotation/delegation/compromise-response equivalence,
- lifecycle-authority rotation summaries used as profile-obligation evidence,
- malformed discovery-returned trust-policy references with invalid authority-rotation posture.

## Non-goal

TimeSync does not define a policy authority registry, key lifecycle, delegation protocol, revocation protocol, status endpoint, transparency log, incident-response workflow, forensics format, credential system, or trust-anchor distribution mechanism. Rotation/delegation/compromise posture is only a bounded replay-visibility review surface for a policy digest already referenced elsewhere.
