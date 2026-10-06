# BrowserRT: start here

Current packaged head: `rev0005` / `BrowserRT-rev0005-2026.05.24.02.50-test-observatory-scaffold.zip`.
Summary highlight: **testing observatory: affected selection, surface inventory, timing history, process policy**.
Codename: **Test Observatory Scaffold**.

BrowserRT is a browser userspace kernel for heavyweight local browser software.
Rev0005 focuses on the testing facility because future browser, OPFS, SAB,
WebGPU, mesh, chaos, replay, and benchmark checks will be too expensive to treat
as one monolithic command.

## Read order for a careful pass

1. `README.md`
2. `CONTEXT-PACK.md`
3. `REVISION-RECEIPT.json`
4. `SURFACE-STATUS.json`
5. `docs/40-validation/cloudtainer-test-economics.md`
6. `docs/40-validation/test-facility-architecture.md`
7. `docs/40-validation/process-start-policy.md`
8. `docs/40-validation/affected-selection-and-timing.md`
9. `docs/40-validation/browser-harness-plan.md`
10. `test/manifest.json`
11. `test/impact-map.json`
12. `test/surface-inventory.json`
13. `tools/run_tests.mjs`
14. `tools/plan_tests.mjs`
15. `tools/turn_bootstrap.mjs`
16. `artifacts/validation/REV0005-TEST-HARNESS-RUN.json`
17. `artifacts/validation/REV0005-TEST-ANALYSIS.json`
18. `docs/60-proof/phase-zero-executable-proof.md`
19. `artifacts/proof/REV0005-PROOF-RUN.json`
20. `src/browserrt.mjs`

## First command

```bash
make turn-start
```

This runs the cheap smoke slice, writes timing evidence, and records the process
policy. It does not start a daemon, watcher, or browser that later turns must
rely on.

## Useful slices

```bash
node tools/run_tests.mjs --list --tier release
node tools/plan_tests.mjs --tier release
node tools/plan_tests.mjs --tier release --changed src/browserrt.mjs --only-affected
node tools/run_tests.mjs --tier release --changed src/browserrt.mjs --only-affected
node tools/run_tests.mjs --tier release --shard 1/2
```

## What a good next revision does

Add one tiny managed browser/CDP boot harness slice. Do not yet combine browser,
OPFS, SAB, and WebGPU. First prove that the browser process can be leased,
observed, and cleaned up inside a single command.
