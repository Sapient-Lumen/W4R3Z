# ADR 0365: Retain witness-checkpoint custody drill receipts

Status: accepted and implemented
Date: 2026-09-10

## Context

ADR 0313 made complete witness-service checkpoint floors executable. ADR 0360 added
`witness-service-checkpoint-custody`, which verifies that a signed checkpoint is authentic, outside
the witness service root, and optionally bound to operator-supplied custody labels while still
reporting `operational-independence=not-assessed`.

The remaining protected-state frontier is operational independence: a witness checkpoint must be
retained outside the Agent disk, witness service root, administrative account, and snapshot failure
domain. The C++ command provides a console report, but repeatable qualification also needs a
durable, content-free receipt that can be saved beside other IoTox evidence.

## Decision

Add `tools/run-witness-checkpoint-custody-drill.py`.

The wrapper runs:

```text
iotox witness-service-checkpoint-custody SERVICE_ROOT CHECKPOINT SERVICE_PUBLIC_KEY_HEX \
  [custody-system=TEXT custody-generation=TEXT custody-failure-domain=TEXT]
```

It requires:

- an existing IoTox binary;
- an existing service root directory;
- an existing regular checkpoint file outside the service root;
- a 64-hex witness service public key; and
- custody labels either all present or all absent.

Custody labels are operator claims, not secrets. The wrapper bounds each label to 1..256 UTF-8 bytes
and rejects control characters before passing it to the C++ command.

On success the wrapper validates the C++ report schema, checkpoint authentication, outside-root
status, public-key match, custody-label binding, checkpoint record count, same/different-device
observation, and the explicit nonclaim `operational-independence=not-assessed`.

It writes a JSON receipt with schema `iotox.witness-checkpoint-custody-drill.v1`. The receipt keeps
only hashes of the report, binary, checkpoint, service public key, path evidence, and custody labels,
plus bounded counters and booleans. It records
`operational_independence=operator-evidence-required` to make the next gate explicit.

On C++ command failure the wrapper writes a rejected receipt with a failure kind, return code,
stdout/stderr byte counts, failure hash, binary hash, checkpoint hash, and `contains_secrets=false`.
It does not retain raw stderr/stdout because those diagnostics can contain local paths.

`tools/iotox-repo.sh witness-custody ...` is the public repository-helper entry point for the same
wrapper.

## Consequences

Witness custody drills now produce retained evidence in the same style as synchronization and
Sandwurm gates. The artifact is suitable for review without revealing private service paths,
checkpoint internals, labels, or device state.

This does not deploy an independent witness. It does not prove that a checkpoint is immutable,
versioned, off-machine, separately administered, or rollback resistant. Those claims require an
operator-retained artifact in a real independent failure domain and a separate acceptance record.

This decision does not change witness wire protocol, checkpoint format, data-key custody, service
startup-floor enforcement, or protected-state authority semantics.

## Evidence

The wrapper contains a self-test that drives a fake IoTox-compatible custody report and verifies a
passing JSON receipt. Real deployment evidence remains open.
