# Cube audit rev0025

Revision: rev0028

## Audit/factor notes

This revision returned from the rev0022 foundation audit into a concrete runtime slice. During the pass, the cube exposed two useful maintenance facts:

1. `make turn-start` was still allowed to use the smoke tier's auto parallelism. In this cloudtainer, that startup was terminated once. Rev0023 factors the bootstrap toward serial smoke so future sessions spend less process budget on the first command.
2. `src/block-store.mjs` already advertised `PersistedSpillMailbox` exports before the runtime source made the persisted mailbox legible as a current proof surface. Rev0023 resolves that mismatch by wiring the persisted spill mailbox into BrowserRT exports, smoke, types, IPC exports, manifest, docs, and proof artifact.

## Coherence target

Future sessions should understand that persisted spill is now an earned fake/model rung, not a durability claim. The next session should not jump straight to OPFS durability. It should either harden retention/compaction over the fake provider or run a very narrow provider proof.

## Current non-claims to preserve

- No OPFS persisted spill proof.
- No browser Worker persisted spill proof.
- No browser crash/restart durability proof.
- No exactly-once message delivery.
- No throughput or latency measurement.
- No cross-browser conformance.
- No WebGPU proof.

## Next likely slice

A cheap retention/compaction proof for persisted spill, or a node-fs provider skeleton, before OPFS spending.
