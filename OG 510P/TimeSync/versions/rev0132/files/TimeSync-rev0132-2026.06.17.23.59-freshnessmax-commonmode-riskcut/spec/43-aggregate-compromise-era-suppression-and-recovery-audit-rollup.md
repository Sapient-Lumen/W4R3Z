# 43. Aggregate compromise-era suppression and recovery-audit rollup

rev0080 closes FT-0079 by adding privacy-preserving aggregate semantics for reporting periods that overlap lifecycle-authority compromise or recovery windows.

## Placement

The new fields are optional members of `aggregate_verifier_audit_summary.aggregate_summary`:

- `compromise_era_suppression`
- `recovery_audit_rollup`

They are deliberately aggregate-only. Individual replay-transparency receipts already carry recovery-attestation posture. Aggregate summaries may report that a period overlapped a compromise or recovery window, or that counts were suppressed, but they must not identify incidents, authorities, verifiers, challenge results, or recovery attestations.

## Non-upgrade boundary

Aggregate compromise-era suppression and recovery-audit rollups can constrain aggregate replay-review posture. They cannot update TimeState, profile conformance, validity horizon, current actionability, source traceability, source diversity, verifier authorization, policy acceptance, or TimeSync provenance.

`replay_visibility_effect` therefore cannot be `current_replay_visibility` for aggregate rollups. Current replay visibility remains a per-receipt evaluation surface.

## Privacy boundary

The following remain outside TimeSync aggregate rollups:

- incident identifiers;
- exact incident-window timing;
- affected authority identity;
- verifier identity or roster;
- affected challenge-result identifiers;
- recovery-attestation identifiers;
- incident forensics;
- legal-authority details;
- compatibility-statement material;
- external recovery or incident provenance.

Small compromise-era or recovery-audit cohorts must be suppressed independently of the existing aggregate verifier-audit suppression flag. A reporting period can have a large total replay count while the compromise-era subset is too small to report safely.

## Cross-operator rollup

Cross-operator recovery rollups are valid only when digest-bound compatibility has already accepted the relevant profile / transparency-policy / lifecycle-authority boundary. A rollup may name only the compatibility statement digest, not the compatibility statement material, authority roster, verifier roster, or trust-policy language.

## What this does not define

TimeSync does not define an incident-response protocol, recovery audit standard, privacy-budget mechanism, legal disclosure process, transparency-log protocol, monitor registry, verifier registry, policy authority registry, or provenance graph.
