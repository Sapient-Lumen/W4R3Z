# FT-0078 closure — lifecycle-authority recovery attestations

FT-0078 is closed in rev0079.

Decision: TimeSync adds a compact `policy_lifecycle_authority_recovery_attestation` reference object and allows it to appear under contained lifecycle-authority compromise responses. The object is digest-bound, summary-only, and replay-visibility scoped.

The reference can distinguish recovered-current, historical-only, contested, and unknown replay visibility. It does not carry incident-response records, authority rosters, key material, delegation chains, legal-authority details, policy repositories, or external provenance.

Remaining frontier: aggregate compromise-era suppression and recovery-audit rollup semantics are deferred to FT-0079.
