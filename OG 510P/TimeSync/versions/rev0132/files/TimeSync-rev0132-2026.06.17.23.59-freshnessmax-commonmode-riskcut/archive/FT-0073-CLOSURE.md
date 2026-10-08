# FT-0073 closure — witnessed checkpoint and monitor-cohort trust boundaries

FT-0073 asked whether TimeSync should add a compact summary for independently witnessed checkpoints or monitor-cohort observations, or leave all witness/gossip/monitor semantics external.

## Decision

TimeSync now supports optional summary-only witness/monitor posture:

```text
challenge_replay_transparency_receipt.witness_cohort_evaluation
aggregate_verifier_audit_summary.aggregate_summary.monitor_cohort_coverage
```

This posture is detached replay-transparency metadata. It is not TimeState, not profile evidence, not current-actionability evidence, not verifier authorization, not a witness protocol, not a monitor registry, and not provenance.

## Guardrails added

The validator rejects:

```text
consistent witness or monitor status without a checked-consistent checkpoint
consistent witness or monitor status below threshold
same-root or unknown independence used as independent-threshold met
witness or monitor disagreement treated as current replay visibility
witness or monitor rosters, identities, dependency details, proof material, logs, or gossip transcripts exported through the summary
aggregate monitor-cohort coverage below minimum group size without suppression
witness_cohort_summary used as profile-obligation evidence
malformed discovery-returned witness/monitor posture
```

## Preserved boundary

External transparency systems may have witnesses, monitors, gossip, logs, receipts, signatures, and policy. TimeSync does not import those protocols. It only records whether the replay-transparency posture was summarized as independently witnessed, monitor-observed, insufficient, disputed, unchecked, or unknown.
