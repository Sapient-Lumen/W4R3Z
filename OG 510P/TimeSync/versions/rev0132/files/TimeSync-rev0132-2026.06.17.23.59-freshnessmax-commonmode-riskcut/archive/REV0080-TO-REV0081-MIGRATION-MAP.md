# rev0080 to rev0081 migration map

- Existing aggregate verifier audit summaries must add `aggregate_summary.aggregate_privacy_controls`.
- For first publications, set `publication_cadence.window_relation_to_previous` to `none_first_publication`.
- For later publications, include `previous_publication_digest` binding `aggregate_verifier_audit_summary`.
- Do not publish exact adjacent reporting windows when suppressed subsets may be differenced.
- Compatible-operator aggregate cohorts require digest-bound equivalent-or-stricter suppression-threshold equivalence.
- Noisy aggregate counts require `noise_status: applied_policy_bound` and a digest binding `aggregate_privacy_policy_rules`.
- Do not use noisy counts to report below the declared minimum group size.
- Do not export privacy-budget material, noise parameters, verifier identities, challenge-result identifiers, policy language, or cross-publication reconstruction material.
