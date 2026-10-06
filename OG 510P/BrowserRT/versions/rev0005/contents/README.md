# BrowserRT

BrowserRT is an ambitious browser userspace kernel: a coordinated runtime for
serious local browser software. The intended future runtime manages workers,
explicit memory ownership, bounded queues, OPFS storage lanes, WebGPU lanes,
telemetry, cancellation, replay, and cross-tab coordination.

Current packaged head: `rev0005` / `BrowserRT-rev0005-2026.05.24.02.50-test-observatory-scaffold.zip`.

## Current status

This is still a **baby cube**. Rev0005 does not add browser/GPU/storage features.
It builds the validation observatory needed before those features arrive:
manifest schema, affected selection, timing history, surface inventory,
quarantine ledger, dry-run planning, and process-start policy.

The worker-agent proof remains green: BrowserRT can boot, emit trace evidence,
bound a channel, create transfer object refs, call a supervised worker, transfer
an `ArrayBuffer`, observe a forced crash, and restart the supervised agent.

## One command

```bash
make lint
```

## Test commands

```bash
make turn-start
node tools/run_tests.mjs --list --tier release
node tools/plan_tests.mjs --tier release
node tools/run_tests.mjs --tier release --jobs auto
make test-affected CHANGED=src/browserrt.mjs
```

## Core non-negotiables

- BrowserRT is not a worker-pool wrapper; it is a resource runtime.
- Control plane and data plane stay separate.
- No unbounded queues.
- Cancellation and deadlines are first-class.
- Memory ownership must be explicit.
- Capability tiers degrade cleanly; no SAB-only or GPU-only design.
- Every expensive proof must be decomposed into manifest-addressable slices.
- Timing evidence is part of validation, but not a public performance claim.
- No long-lived process may be required to survive across cloudtainer turns.
- The cloudtainer is the build boundary: no external services, CDNs, network
  dependencies, or non-vendored toolchains are required.

## Repository map

- `docs/00-meta/`: archive discipline, example-cube lessons, cloudtainer rules.
- `docs/05-research/`: related-work and testing-facility research passes.
- `docs/10-contract/`: frozen runtime-level contracts.
- `docs/20-architecture/`: architecture lanes, primitives, mesh, tradeoffs.
- `docs/30-demos/`: demo pressure that should guide implementation.
- `docs/40-validation/`: cloudtainer testing economics and validation design.
- `docs/50-roadmap/`: phased build and test-facility plans.
- `docs/60-proof/`: executable proof surfaces.
- `src/`: dependency-free runtime scaffold, proof workers, and test-facility helpers.
- `test/`: manifest, impact map, surface inventory, quarantine ledger, selftests.
- `tools/`: cube validation, proof runner, test runner, planning, analysis, packaging.
- `artifacts/research/`: URL-free source registries.
- `artifacts/proof/`: machine-readable executable proof witness.
- `artifacts/validation/`: test timing, surface, analysis, and turn-bootstrap witnesses.
