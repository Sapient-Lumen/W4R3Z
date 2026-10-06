# Kernel Kit OPFS abort-boundary slice — rev0107 linked repair

## Why this slice exists

The risky gap after the raw OPFS composite AbortSignal proof was product-path isolation: the freshest storage safety boundary could pass as a narrow provider proof while the human/CDP Kernel Kit workflow still demonstrated only boot, worker, storage-lane write, reload readback, and trace/export surfaces.

This linked repair carries the current raw OPFS `signal`/`abortSignal` boundary into the Kernel Kit browser/page path without pretending Kernel Kit owns the global current office.

## Runtime change

`boot().kernelKitOpfsAbortBoundary()` now performs a real raw `OpfsAsyncBlockStore.put()` with both `signal` and `abortSignal` supplied. The sibling `abortSignal` is pre-aborted, so the put must reject with `BRT_OPFS_OPERATION_ABORTED` before a block is present. A second invalid sibling check must reject with `BRT_OPFS_ABORT_SIGNAL_INVALID`.

The report proves:

- composed abort rejection happened;
- invalid sibling rejection happened;
- `has()` and `verify()` do not observe the target block after the abort;
- option-pair/composite signal counters moved;
- cleanup was attempted;
- the boundary is a non-mutation boundary for this pre-write path.

## Product-path change

Both Kernel Kit browser runners now call `kernelKitOpfsAbortBoundary()` after the storage-lane write snapshot and before closing the runtime trace. The human page renders a compact “OPFS abort boundary” section, and the CDP proof now asserts the report, trace kinds, and support-bundle preservation.

This is intentionally one useful end-to-end path, not a new registry-heavy doctrine pass.

## Audit/refactor change

`tools/kernel_kit_demo_contract_audit.mjs` no longer requires `REVISION-RECEIPT.json` to name Kernel Kit as the active current slice. That old check was stale and would fail any healthy future where another proof owns the current office. It now verifies that current-office fields are present while treating Kernel Kit as carried-forward evidence.

`tools/kernel_kit_opfs_abort_boundary_contract_audit.mjs` is the new release-tier static audit for the product-path abort-boundary wiring.

## Validation commands

```bash
node tools/kernel_kit_opfs_abort_boundary_contract_audit.mjs --json artifacts/audit/REV0107-KERNEL-KIT-OPFS-ABORT-BOUNDARY-CONTRACT-AUDIT.json
node tools/kernel_kit_demo_contract_audit.mjs --json artifacts/audit/REV0107-KERNEL-KIT-DEMO-CONTRACT-AUDIT.json
node tools/browser_kernel_kit_demo_probe.mjs --json artifacts/validation/REV0107-BROWSER-KERNEL-KIT-DEMO-PROBE.json --timeout-ms 40000
python3 tools/check_cube.py
```

## Non-claims

No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, multi-tab coordination, or cross-browser conformance claim.

Abort remains cooperative and BrowserRT-checkpointed. This proves a pre-write non-mutation boundary for composed raw OPFS options, not arbitrary cancellation of native filesystem work after side effects begin.
