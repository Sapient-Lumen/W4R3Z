# ADR 0366: Enforce retained drill local requirements

Status: accepted and implemented
Date: 2026-09-10

## Context

ADR 0361 added retained synchronization recovery drill receipts. ADR 0365 added retained witness
checkpoint custody drill receipts. Both wrappers convert command output into durable, content-free
JSON evidence while preserving the core nonclaims:

- `backup-independence=not-assessed`; and
- `operational-independence=not-assessed`.

That receipt layer still needed two hardening changes.

First, rejected sync recovery drill receipts retained a bounded raw failure string. Bounded text is
still not content-free enough for a backup or restore path because diagnostics can contain private
local paths.

Second, the wrappers recorded useful observations such as same/different device and label presence,
but could not require them. An operator running an independence-oriented drill should be able to say
“reject this receipt unless provenance/custody labels are present” or “reject this receipt unless the
restored/checkpoint root is on a different filesystem device.” Different-device evidence is not
independence, but it is a useful enforceable local minimum.

## Decision

`tools/run-sync-retained-recovery-drill.py` now:

- validates the exact text-hex format emitted by the production CLI;
- writes rejected command receipts without raw stdout/stderr text;
- records failure kind, return code, stdout/stderr byte counts, and a complete failure hash;
- preserves structured `decision=mismatch` reports even though the production command exits nonzero;
- accepts `--require-operator-provenance`; and
- accepts `--require-different-device`.

If `--require-operator-provenance` is set, the receipt is rejected unless all backup provenance
labels were supplied and bound into the verifier report. If `--require-different-device` is set, the
receipt is rejected unless the verifier reports `root-devices-differ=1`.

`tools/run-witness-checkpoint-custody-drill.py` now:

- accepts `--require-custody-labels`; and
- accepts `--require-different-device`.

If `--require-custody-labels` is set, the receipt is rejected unless all custody labels were supplied
and bound into the custody report. If `--require-different-device` is set, the receipt is rejected
unless the report says the checkpoint and service roots are on different filesystem devices.

Both wrappers retain explicit booleans for which local requirements were requested and whether each
one was satisfied. A failed local requirement produces a structured `status=rejected` receipt while
still retaining the command/report hash and non-secret counters.

`tools/iotox-repo.sh sync-recovery-drill ...` is now the public repository-helper entry point for
the retained recovery wrapper, matching `tools/iotox-repo.sh witness-custody ...`.

## Consequences

The operator can now make same-machine convenience drills visibly fail when they are intended to
stand in for an independence gate. This reduces accidental overclaiming while keeping the wrappers
usable for local smoke tests.

This still does not prove backup independence, restore provenance, operational witness independence,
immutability, versioning, or off-machine custody. It only enforces locally observable prerequisites
and label binding.

This decision does not change synchronization protocol behavior, witness protocol behavior, storage
formats, authority semantics, or the C++ CLI reports.

## Evidence

Both wrapper self-tests now cover a passing labeled receipt and a rejected missing-label receipt.
The sync recovery self-test also covers a nonzero structured mismatch report. The validation note
for this pass records real-binary positive, mismatch, and requirement-rejected recovery drills under
`nix develop`, plus the real-binary negative witness checkpoint drill.
