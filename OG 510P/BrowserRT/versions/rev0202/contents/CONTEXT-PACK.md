# BrowserRT context pack — rev0125 / linked rev0202

Packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. Linked rev0202 corrects the immediate runtime-core budget risk: recovery guidance was useful but branch-heavy, and the runtime-core closure had only 424 bytes of slack.

The substantive change table-drives storage recovery classifications/steps in `src/browser-storage-recovery-guidance.mjs`, keeps `createBrowserStorageRecoveryGuidance(...)` behavior covered by existing posture probes, and ratchets `tools/runtime_core_entry_contract_audit.mjs` to 128,500 bytes. Observed runtime-core closure is 128,028 bytes across 6 files.

Research posture remains conservative: OPFS is quota-bound and cleared with site data; Web Locks do not substitute for provider lifecycle cancellation after grant; Storage Buckets are a capability branch, not a baseline; and high-volume OPFS IO is a privacy byte-time surface after recent SSD-timing work.

Next useful work: reduce packed example/proof-helper weight or split proof-heavy helpers away from the installed adoption path while preserving package consumer smoke. Avoid another doctrine registry.

Current proof anchor: `browser:opfs-block-store-raw-composite-abort-signal-proof`. Runtime spelling anchors: opfsasyncblockstore, abortSignal, signal, OPFS, fake web locks. Non-claim reminders: cross-browser, quota, eviction, crash, browser-light.

current office remains rev0125.
