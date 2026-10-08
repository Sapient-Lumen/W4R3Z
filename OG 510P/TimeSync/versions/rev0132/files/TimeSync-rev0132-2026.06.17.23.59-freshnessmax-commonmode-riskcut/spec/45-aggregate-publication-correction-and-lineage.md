# 45. Aggregate Publication Correction and Lineage

## Status

Normative for rev0082.

## Problem

rev0081 defined publication cadence and aggregate privacy controls for replay-transparency aggregate verifier audit summaries. That was enough to say whether repeated aggregate releases were safe to compare, but not enough to say what a later publication means relative to an earlier one.

A later aggregate publication may correct counts, withdraw an unsafe publication, supersede a prior aggregate, or reconcile several aggregate windows into a longer-period view. Without explicit lineage, consumers may mistakenly treat a corrected publication as a fresh independent measurement, treat withdrawal as deletion, or compute suppressed deltas from adjacent releases.

## New field

Aggregate verifier audit summaries now carry:

```text
aggregate_summary.aggregate_revision_lineage
```

This field is required for `record_kind: aggregate_verifier_audit_summary`.

## Lineage states

`aggregate_revision_lineage.status` is one of:

- `original`
- `corrected`
- `withdrawn`
- `superseded`
- `reconciled`
- `unknown`

`original` means the aggregate publication does not assert correction, withdrawal, supersession, or reconciliation lineage. It may still have ordinary publication-cadence sequence metadata.

`corrected`, `withdrawn`, `superseded`, and `reconciled` require a `prior_aggregate_digest` that binds to `aggregate_verifier_audit_summary` and a monotonic `publication_sequence` / `previous_publication_sequence` relationship.

`superseded` additionally requires `supersedes_aggregate_digest`.

`reconciled` additionally requires a `reconciliation` object and digest-bound revision-chain metadata.

## Non-rewrite rule

A correction does not rewrite history. Prior aggregate publications remain addressable as prior publications. A corrected, withdrawn, superseded, or reconciled publication constrains interpretation of later aggregate review; it does not erase, mutate, or re-sign the prior record.

The boundary flags therefore require:

```text
prior_publication_rewritten = false
suppressed_delta_exported = false
individual_result_identifiers_exported = false
verifier_identity_exported = false
correction_updates_profile_assessment = false
correction_updates_replay_visibility_only = true
external_correction_record_interpreted_as_timesync_provenance = false
```

## Current-visibility boundary

Aggregate correction lineage is not individual replay visibility. It must not upgrade a corrected publication to current individual replay visibility and must not update a profile assessment.

The following are invalid for concrete correction states:

```text
correction_effect = current_replay_visibility
correction_effect = profile_assessment_update
```

Acceptable effects are aggregate-only or historical-context effects.

## Withdrawal semantics

A withdrawn aggregate publication requires a `withdrawal_disposition` of `historical_only`, `contested`, or `unknown`.

Withdrawal does not delete the prior aggregate. It says that the prior aggregate should no longer be used as an ordinary aggregate review signal without the withdrawal context.

## Longitudinal reconciliation

Longitudinal reconciliation exists to support coarser or compatible rebucketing across aggregate publications while preserving suppression and privacy boundaries.

The reconciliation boundary requires:

```text
suppressed_deltas_exported = false
individual_result_identifiers_exported = false
adjacent_exact_windows_exported = false
reconciliation_updates_profile_assessment = false
reconciliation_updates_replay_visibility_only = true
external_reconciliation_record_interpreted_as_timesync_provenance = false
```

`window_relation = adjacent_exact_windows` is invalid because it can enable differencing. `window_relation = unknown` is also invalid for a concrete reconciled publication.

If reconciliation is suppression-aware, cumulative counts must be thresholded, suppressed, or policy-bound noisy counts rather than raw aggregate counts.

## Digest and chain binding

A corrected, withdrawn, superseded, or reconciled aggregate must bind to the prior aggregate with:

```text
prior_aggregate_digest.binds = aggregate_verifier_audit_summary
```

A reconciled aggregate must also bind the prior and current revision chain:

```text
previous_chain_digest.binds = aggregate_publication_revision_chain
chain_head_digest.binds = aggregate_publication_revision_chain
```

These digests are interpretation anchors, not proof material, publication-repository state, or provenance graphs.

## Evidence class

rev0082 adds:

```text
aggregate_revision_lineage_summary
```

This class may appear in exported summaries but cannot satisfy profile obligations.

## Non-goals

TimeSync does not define:

- a correction workflow engine,
- publication notification cadence,
- legal withdrawal process,
- repository topology,
- transparency-log protocol,
- suppressed-delta release policy,
- verifier registry,
- correction authority registry,
- individual challenge-result reconciliation,
- provenance graph.

## Validator-backed invariants

The rev0082 validator rejects:

- corrected / withdrawn / superseded / reconciled aggregate publications without a prior aggregate digest,
- non-monotonic correction sequence numbers,
- suppressed-delta leakage,
- individual result identifier leakage,
- correction lineage promoted to current replay visibility,
- correction lineage used to update profile assessment,
- adjacent exact-window reconciliation,
- unbounded or unknown reconciliation posture,
- malformed discovery-returned aggregate revision lineage,
- aggregate revision-lineage summaries used as profile-obligation evidence.
