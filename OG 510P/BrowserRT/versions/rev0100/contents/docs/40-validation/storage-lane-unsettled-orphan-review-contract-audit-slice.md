# Storage-lane unsettled orphan review contract audit slice

Task:

```text
facility:storage-lane-unsettled-orphan-review-contract-audit
```

This audit checks wiring for the `rev0078` unsettled timeout orphan-review boundary. It does not launch Chromium. It verifies that the runtime exposes reviewed/fingerprint-bound orphan finalization, that release and browser proofs exist, that first-read/currentness surfaces point at the current rev0078 task, and that the manifest, impact map, and surface inventory carry the new proof IDs.

Non-claims: the audit itself does not prove browser behavior, OPFS durability, provider cancellation, rollback, quota/eviction survival, or production readiness.

Executable proof IDs guarded by this audit include `scheduler:storage-lane-unsettled-orphan-review-proof` and `browser:opfs-web-lock-unsettled-orphan-review-proof`.
