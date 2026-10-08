# FT-0079 closure — aggregate compromise-era suppression and recovery-audit rollup

Closed in rev0080.

Decision: aggregate verifier audit summaries may carry compact `compromise_era_suppression` and `recovery_audit_rollup` objects. These are aggregate-only, privacy-preserving review surfaces. They can constrain aggregate replay-review posture but cannot update individual replay receipt current visibility, TimeState, profile conformance, actionability, verifier authorization, traceability, source diversity, or TimeSync provenance.

Validator-backed guardrails reject small compromise-era/recovery cohorts without suppression, exact incident-window export, incident/authority/verifier/result/attestation leakage, current-visibility promotion, and cross-operator rollup portability without compatibility digest.
