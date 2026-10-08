# rev0079 to rev0080 migration map

- Existing rev0079 replay-transparency receipts remain valid.
- Existing aggregate verifier audit summaries remain valid unless they claim the new compromise-era or recovery-audit rollup fields incorrectly.
- Add `aggregate_summary.compromise_era_suppression` when a reporting period overlaps a lifecycle-authority compromise window and aggregate reporting must either suppress or coarsely report the affected subset.
- Add `aggregate_summary.recovery_audit_rollup` when reporting aggregate recovered-current / historical-only / contested / unknown recovery posture over a period.
- Do not export incident identifiers, exact incident windows, authority identities, verifier identities, affected challenge-result IDs, recovery-attestation IDs, forensics, legal-authority details, or external provenance.
