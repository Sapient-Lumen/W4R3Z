# Migration map — rev0082 to rev0083

## Required aggregate lineage addition

Aggregate verifier audit summaries now require:

```text
aggregate_summary.aggregate_revision_lineage.correction_authority_reference
```

For an existing rev0082 original aggregate publication, use a local authority reference with `authority_role: original_publication_authority`, `notification_state: not_applicable`, and `chain_portability_state: local_chain_only`.

For a corrected, withdrawn, superseded, or reconciled aggregate publication, provide:

- a digest-bound correction authority,
- `authorization_status: authorized`,
- a role matching the lineage status,
- notification cadence within policy,
- notification digest if the publication change requires notification,
- local-only or compatible-operator portability posture.

## Compatible-operator correction chains

If the aggregate publication is interpreted by a compatible operator, the correction-authority portability boundary must include:

- `operator_scope: compatible_operator_digest_bound`,
- `authority_equivalence: digest_bound_equivalent_or_stricter`,
- `chain_portability_state: portable_to_compatible_operator`,
- `compatibility_statement_digest`,
- `portable_correction_chain_digest`.

## Evidence class catalog

Add `aggregate_correction_authority_summary` to the set of evidence classes that cannot satisfy profile obligations.

## Profile digests

The profile normative digests changed because the forbidden evidence-class set is part of profile evidence policy.
