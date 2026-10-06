# Kernel Kit storage posture slice — rev0107 linked pass

## Purpose

The Kernel Kit product path now records a small, real browser storage posture before the proof closes. This is intentionally narrower than a quota-pressure or eviction-survival experiment: it asks what the current managed Chromium page can observe through `navigator.storage.estimate()` and `navigator.storage.persisted()`, carries that posture into the page report, local handoff, and support bundle, and keeps persistent-storage requests off by default.

## What changed

- `boot().kernelKitStoragePosture()` captures StorageManager estimate/persistence posture and emits `kernel-kit-demo:storage-posture`.
- The browser runner and human page runner call it in both the work path and reload path.
- The browser Kernel Kit proof now requires storage posture evidence in work, reload, and support bundle output.
- The browser proof artifact is compacted after assertions so the package keeps the behavior receipt without carrying the entire page object graph.
- `facility:kernel-kit-storage-posture-audit` statically checks runtime, type, page, browser-runner, browser-proof, support-bundle, package-retention, manifest, impact-map, and surface-inventory wiring.

## Evidence commands

```sh
node tools/kernel_kit_storage_posture_contract_audit.mjs --json artifacts/audit/REV0107-KERNEL-KIT-STORAGE-POSTURE-CONTRACT-AUDIT.json
node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1 --json artifacts/validation/REV0107-BROWSER-KERNEL-KIT-DEMO-PROBE.json
```

## Non-claims

Storage posture is advisory capability/estimate evidence, not a quota reservation or eviction-survival proof. This does not claim persistent-storage grant, browser-restart durability, fsync, crash recovery, multi-tab coordination, cross-browser conformance, production readiness, or product-market fit.
