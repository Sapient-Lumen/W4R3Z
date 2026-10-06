# Kernel Kit demo current office — rev0054

Current revision: rev0055

Rev0051 keeps the Kernel Kit demo as the narrow usefulness proof and adds a human-facing handoff Markdown layer.

Current useful flow:

1. run the browser Kernel Kit demo by explicit id;
2. read the OPFS reload handoff;
3. export the receipt;
4. trigger controlled bounded failure;
5. compare success/failure traces;
6. create the diagnostic runbook;
7. build a support bundle;
8. import/diff the support bundle;
9. build handoff Markdown for the next session.

The current runtime slice remains `browser:kernel-kit-demo-proof`. The current release-tier slice is `demo:kernel-kit-handoff-markdown-proof`; the current audit is `facility:kernel-kit-handoff-markdown-audit`.

## Exact commands

```bash
node tools/run_tests.mjs --tier release --id demo:kernel-kit-handoff-markdown-proof,facility:kernel-kit-handoff-markdown-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1
python3 tools/check_cube.py
```

## Non-claims

No production runtime claim. No production handoff-markdown claim. No automated next-session correctness claim. No production support-bundle claim. No production support-bundle import claim. No production support-bundle diff claim. No production guided-tour claim. No support-bundle authenticity or signature claim. No automated regression detection claim. No automated failure triage claim. No automated failure recovery claim. No root-cause analysis claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.

Carry-forward demo contract markers: Interactive Kernel Kit Demo; facility:kernel-kit-demo-audit; facility:kernel-kit-page-contract-audit. No product-market-fit claim.
