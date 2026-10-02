# ADR 0364: Retain interrupted long-soak evidence

Status: accepted and implemented
Date: 2026-09-10

## Context

ADR 0361 added duration-bound three-writer writable soaks, including the 24-hour profile needed for
synchronization trust graduation. A 24-hour run can be interrupted for ordinary operational reasons:
operator stop, terminal close, service restart, host maintenance, or time-boxed construction work.

Before this decision, an interrupted soak could leave useful partial behavior in logs and node state
without a structured retained receipt. That is a bad fit for the project evidence model. Rejected or
incomplete science runs should still explain where they stopped, what had already converged, and
whether they retained any content.

## Decision

`tools/run-sync-three-writer.py` now installs explicit `SIGINT`/`SIGTERM` handling around the
three-writer qualification lifecycle. Normal interruption becomes a `rejected` proof instead of an
unstructured process exit, and cleanup suppresses repeat interrupts while stopping agents and the
private bootstrap fixture.

The harness keeps a mutable, content-free partial-soak record while the soak is running. If the run
rejects after soak setup, the rejected proof may include `partial_soak_evidence`:

- whether a soak campaign was active;
- whether it completed;
- requested duration, minimum cycles, cycle delay, restart cadence, and repair cadence;
- converged cycle count and elapsed time;
- daemon restart, repair, and delete-cycle counters;
- last converged cycle duration;
- final digest commitment for the last converged synthetic soak state; and
- optional Agent high-water RSS values when available.

The record always carries `soak_contains_secrets=false`. It does not include file content, paths,
Tox keys, stable principals, private phrases, backup paths, or checkpoint contents.

`tools/verify-sync-three-writer-sandwurm.py` accepts and validates this optional rejected-proof
shape while preserving compatibility with older rejected proofs. Its self-test now includes a
partial-soak rejected fixture and requires the projected cycle count to survive verification.

## Consequences

Normal operator interruption no longer wastes the scientific value of a long soak. A partial receipt
can be retained, compacted, and discussed without disclosing private content.

This does not make an interrupted run a passing 24-hour soak. It also does not cover `SIGKILL`,
power loss, VMM death, kernel panic, killed process groups, or host storage loss. Those remain
separate abrupt-storage and VM-cut gates.

This decision does not change synchronization protocol behavior, authority semantics, backup trust,
or precious-data recommendations.

## Evidence

The verifier self-test includes a rejected receipt with partial soak progress. The full 24-hour
soak remains a future evidence run.
