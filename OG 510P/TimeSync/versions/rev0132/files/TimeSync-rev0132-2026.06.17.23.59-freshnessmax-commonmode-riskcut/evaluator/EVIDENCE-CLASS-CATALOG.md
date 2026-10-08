# Evidence class catalog — rev0132

This rendered catalog mirrors `evaluator/evidence-class-catalog.json`. Evidence classes with `may_satisfy_profile_obligation: false` can appear in summaries but cannot satisfy profile obligations.

## `local_measurement_summary`

A compact statement derived from local clock/discipline observation, without exporting raw samples or the clock algorithm.

- may_satisfy_profile_obligation: `true`
- may_appear_in_exported_summary: `true`

## `authenticated_source_claim`

A source claim whose source identity or channel was authenticated before local assessment.

- may_satisfy_profile_obligation: `true`
- may_appear_in_exported_summary: `true`

## `unauthenticated_source_claim`

A source claim observed without identity/channel authentication strong enough for the consuming profile.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`

## `source_diversity_summary`

A compact evaluator summary of timing-source dependency diversity and common-mode risk, without exporting source identifiers, paths, raw observations, or clock-selection algorithms.

- may_satisfy_profile_obligation: `true`
- may_appear_in_exported_summary: `true`
- notes:
  - May support source_diversity_posture obligations but is still summary-only and not a provenance graph.

## `operator_configuration`

A local configuration fact, such as selected profile, applicability map, validity scope, or policy reference.

- may_satisfy_profile_obligation: `true`
- may_appear_in_exported_summary: `true`

## `profile_catalog_rule`

A normative rule from the assessed profile catalog, including required/default items and fallback maps.

- may_satisfy_profile_obligation: `true`
- may_appear_in_exported_summary: `true`

## `validity_horizon_summary`

A compact evaluator summary of the profile-assessment validity window and current-actionability decision, without treating export time as fresh timing evidence.

- may_satisfy_profile_obligation: `true`
- may_appear_in_exported_summary: `true`
- notes:
  - May support validity_horizon obligations and replay review.
  - Does not by itself prove freshness, source correctness, or continued real-world validity after evaluated_at.

## `local_policy_rule`

A local policy rule used after historical profile assessment to decide present acceptability or actionability.

- may_satisfy_profile_obligation: `true`
- may_appear_in_exported_summary: `true`

## `external_evidence_reference`

An opaque pointer or salted commitment binding a redacted evidence item to an external retained record, without interpreting the external record as TimeSync provenance.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May bind a redacted summary item to material held outside TimeSync.
  - Cannot by itself satisfy a profile obligation or upgrade traceability, freshness, source diversity, or actionability.

## `authorized_verifier_disclosure`

A detached authorized-verifier challenge result or receipt confirming that redacted salted-commitment material was reviewed outside ordinary TimeSync exchange, without carrying the salt/preimage in an ordinary evidence summary.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May document that an authorized disclosure review occurred for a redacted commitment.
  - Cannot by itself satisfy or upgrade traceability, freshness, source diversity, profile conformance, or current actionability.

## `replay_transparency_receipt`

A detached replay-transparency receipt or aggregate verifier audit summary showing that challenge-result replay was logged or summarized, without exposing verifier rosters, salts, preimages, legal-authority detail, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May support review of replay visibility and aggregate verifier activity.
  - Cannot satisfy or upgrade traceability, freshness, source diversity, profile conformance, current actionability, or TimeSync provenance.

## `witness_cohort_summary`

A compact detached summary of witness-checkpoint or monitor-cohort posture for replay-transparency review, without exporting witness/monitor rosters, identities, proof material, gossip transcripts, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May support review of replay visibility and split-view posture only.
  - Cannot satisfy or upgrade traceability, freshness, source diversity, profile conformance, current actionability, or TimeSync provenance.

## `transparency_trust_policy_reference`

A digest-bound reference to external transparency trust-policy rules for anchor freshness, checkpoint consistency, witness thresholds, monitor-cohort minimums, or cross-operator replay-visibility threshold equivalence, without exporting the trust-policy language, trust anchors, witness rosters, monitor identities, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May bind replay-transparency or aggregate verifier audit posture to external local policy rules.
  - Cannot satisfy or upgrade profile evidence, source traceability, current actionability, profile conformance, transparency provenance, or verifier authorization.

## `lifecycle_authority_rotation_summary`

A compact summary of transparency trust-policy lifecycle-authority rotation, delegated status-publication posture, or compromise-response state, without exporting authority rosters, key material, delegation chains, forensics, repository topology, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May constrain replay-visibility evaluation for a transparency trust-policy reference.
  - Cannot satisfy or upgrade TimeState, profile evidence, source traceability, validity horizon, actionability, verifier authorization, or TimeSync provenance.

## `lifecycle_authority_recovery_attestation`

A compact digest-bound reference to a lifecycle-authority compromise recovery attestation or historical/contested replay-visibility disposition, without exporting authority rosters, key material, incident forensics, legal authority details, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May distinguish recovered-current, historical-only, contested, or unknown replay visibility after lifecycle-authority compromise.
  - Cannot satisfy or upgrade TimeState, profile evidence, source traceability, validity horizon, actionability, verifier authorization, or TimeSync provenance.

## `recovery_audit_rollup_summary`

A compact aggregate summary of compromise-era suppression and lifecycle-authority recovery-audit rollup posture, without exporting incident identifiers, affected challenge-result identifiers, authority identities, verifier identities, forensics, legal-authority details, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May constrain aggregate replay-review posture for a reporting period that overlaps a lifecycle-authority compromise or recovery window.
  - Cannot satisfy or upgrade TimeState, profile evidence, source traceability, validity horizon, actionability, verifier authorization, or TimeSync provenance.

## `aggregate_privacy_control_summary`

A compact aggregate-only summary of publication cadence, suppression-threshold equivalence, and statistical-noise posture for replay-transparency aggregate audit summaries, without exporting verifier identities, challenge-result identifiers, privacy-budget internals, noise parameters, cross-publication reconstruction material, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May constrain whether aggregate replay-review rollups are safe to publish or compare across operators and reporting periods.
  - Cannot satisfy or upgrade TimeState, profile evidence, source traceability, validity horizon, actionability, verifier authorization, individual replay visibility, or TimeSync provenance.

## `aggregate_revision_lineage_summary`

A compact aggregate-only summary of correction, withdrawal, supersession, and longitudinal reconciliation lineage for replay-transparency aggregate publications, without exporting suppressed deltas, individual challenge-result identifiers, verifier identities, exact reconstruction material, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May constrain whether an aggregate publication supersedes, corrects, withdraws, or reconciles a prior aggregate publication.
  - Cannot satisfy or upgrade TimeState, profile evidence, source traceability, validity horizon, actionability, verifier authorization, individual replay visibility, aggregate current visibility, or TimeSync provenance.

## `aggregate_correction_authority_summary`

A compact summary of aggregate correction-authority authorization, correction-notification freshness, and correction-chain portability posture, without exporting authority rosters, key material, recipient identities, repository topology, or notification payloads.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May constrain how aggregate correction, withdrawal, supersession, or reconciliation lineage is interpreted.
  - Cannot satisfy profile obligations or upgrade TimeState, profile conformance, actionability, individual replay visibility, or TimeSync provenance.

## `aggregate_correction_authority_lifecycle_summary`

A compact summary of aggregate correction-authority lifecycle, revocation, emergency-withdrawal, and contestation posture, without exporting authority rosters, key material, revocation endpoints, repository topology, incident forensics, legal-process details, emergency-response plans, contestation-party identities, or external provenance semantics.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May constrain whether aggregate correction-authority posture remains current, historical, emergency-withdrawn, contested, or unknown for aggregate interpretation.
  - Cannot satisfy or upgrade TimeState, profile evidence, source traceability, validity horizon, actionability, verifier authorization, individual replay visibility, or TimeSync provenance.

## `portable_digest_binding_policy_summary`

A compact summary or digest-bound reference describing canonical JSON, byte-envelope, and semantic-version binding policy for returned or retained TimeSync objects, without treating that policy as timing evidence or external provenance.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May constrain how digest-bound returned objects are interpreted for portability and replay review.
  - Cannot satisfy or upgrade TimeState, profile evidence, source traceability, validity horizon, actionability, verifier authorization, or TimeSync provenance.

## `retained_prior_assessment`

A prior retained TimeSync assessment reused as a record, not as fresh timing evidence.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`

## `transport_metadata_only`

Envelope/carrier metadata such as sent_at, sequence, delivery status, or channel authentication, considered only as carriage context.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`
- notes:
  - May explain carriage integrity but must not be promoted to TimeState freshness, traceability, or conformance.

## `not_observed`

The evaluator records that an item was absent, unknown, or deliberately unavailable.

- may_satisfy_profile_obligation: `false`
- may_appear_in_exported_summary: `true`


rev0088 audit note: rendered profile files are checked against the normative catalog so non-satisfying evidence classes remain visible to reviewers.

## `scope_composition_guard_summary`

Compact mixed-layer scope-composition guard summary. It may constrain compatibility/discovery/lifecycle interpretation, but cannot satisfy profile obligations or update TimeState, profile assessment, actionability, replay visibility, lifecycle suppression, or TimeSync provenance.
