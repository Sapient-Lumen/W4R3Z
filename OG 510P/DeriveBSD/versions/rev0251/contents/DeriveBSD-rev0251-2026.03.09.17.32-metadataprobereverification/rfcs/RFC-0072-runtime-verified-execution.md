# RFC-0072: Runtime verified execution (MAC/veriexec integration)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-25

## Summary

Optional integration with a verified-execution mechanism so runtime can enforce that only closure-approved code runs.

## Motivation

Supply-chain controls are stronger when they are enforceable at runtime:
- prevents “drop a binary into /usr/local and run it” failure modes
- reduces blast radius after a compromise

FreeBSD has an implementation direction via MAC/veriexec, and NetBSD Veriexec provides a proven kernel-integrity model.

## Goals / Non-goals

Goals:
- derive fingerprint database from closure manifest/proof
- load fingerprints during activation
- enforce for host and optionally for service jails/microVM roots

Non-goals:
- making this mandatory for v1

## Proposal

### Evidence objects

When enabled, verified execution is expressed as evidence:
- `exec-verify-policy` (desired mode + fingerprint DB digest)
- `exec-verify-receipt` (load/apply outcome)
- `exec-verify-snapshot` (current enforcement state)
- `exec-verify-event` (violations/state transitions as typed events)

Schemas + examples are provided under `spec/` (see `docs/233-verified-execution-as-evidence.md`).

### Flow

- Add a build step that can emit a fingerprint DB artifact from a closure manifest/proof.
- Activation loads the fingerprint DB and emits an apply receipt.
- Runtime emits violations as typed events.
- `derive verify` checks enforcement state matches deployment evidence.

## Alternatives considered

- rely purely on signatures + policy without runtime enforcement

## Backwards compatibility

Optional; does not change artifact identity unless enabled by policy.

## Security considerations

- ensure escape hatches are explicit and logged
- treat verifier config as part of the deployment object

## Open questions

- minimal surface needed for enforcement in service jails
- how to bind enforcement state to ZFS BEs across rollback
