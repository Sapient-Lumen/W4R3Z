# rev0102 browser block-store lane provider-options slice

Current managed-browser task: `browser:block-store-lane-provider-options-proof`.

The Managed Chromium proof exercises the same scheduled provider-option and storeOptions boundary with real OPFS. It verifies that a scheduled OPFS `put()` receives `providerOptions.writeBudgetGuard` and rejects before creating the proof prefix, that `putOptions.writeBudgetGuard = false` overrides the inherited budget for an intentional write, and that a pre-aborted `providerOptions.signal` reaches a scheduled OPFS read without corrupting the existing block.

The proof also runs a separate Web-Lock-guarded OPFS smoke operation and confirms the browser ends with no held or pending locks. The browser budget rejection uses an impossible projected-usage ratio rather than a fixed byte reserve because browser-reported quotas can be extremely large in the cloudtainer profile.

Non-claims: Managed Chromium only; no cross-browser proof; no Firefox, Safari, mobile, multi-tab fairness, quota-reservation, eviction-survival, fsync, crash/power-loss, or production-readiness claim is made. This slice proves scheduled option pass-through in the browser harness and keeps the Web Locks smoke path live.
