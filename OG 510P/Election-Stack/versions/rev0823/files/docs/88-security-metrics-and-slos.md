# 88 — Security Metrics & Service Level Objectives (SLOs)

**Track:** A (Deployable core)


## Why metrics
For a public election system, you need measurable targets that support:
- early detection,
- public transparency,
- and operational decision thresholds (e.g., “freeze intake now”).

## Core SLOs (examples)
> These are starting points; tune per jurisdiction and threat model.

### Integrity & verifiability
- **Receipt truthfulness:** 0 cases where UI indicates RECORDED without a valid inclusion proof.
- **Checkpoint cadence:** witness-quorum checkpoint at least every *T* minutes during voting hours.
- **Verifier availability:** at least 2 independent verifier implementations available and validating.

### Availability
- **Ballot intake:** p95 acceptance latency < *X* seconds under normal load.
- **Receipt confirmation:** p95 inclusion proof availability < *Y* minutes.
- **Degraded mode:** intake remains available with quorum loss of up to *k* witnesses.

### Detection
- **Split-view detection:** fork proof emitted within *N* minutes of first divergent STH.
- **ENR drift detection:** alert within *M* minutes of first mismatch.

## Metrics catalog
- `receipt_recorded_without_proof_count`
- `checkpoint_interval_seconds`
- `witness_quorum_size`
- `fork_proof_events`
- `enr_drift_alerts`
- `token_mint_error_rate`
- `revocation_epoch_changes_per_hour`
- `vrdb_snapshot_diff_size`

## Reporting
Publish a signed **MetricsReport** at a regular cadence (e.g., daily during voting, hourly on election day) containing:
- checkpoint IDs/hashes covered
- metric values + thresholds
- any triggered incident policies

Schema: `schemas/MetricsReport.json`