# Web-Lock-guarded block-store release guard — rev0062 (carried forward from rev0060)

Current revision: rev0062

`coord:web-lock-guarded-block-store-proof` is the browser-light guard for the new coordination wrapper. It uses a deterministic fake Web Locks implementation, not Chromium, so the release harness can check the wrapper contract without launching a browser.

The proof checks that an already-held exclusive lock blocks a second mutating call, shared read-like calls can co-hold, trace evidence is emitted, and wrapped block-store reads/verifies still reach the provider.

Non-claims: fake-lock proof only; no cross-browser behavior, OPFS durability, quota, eviction, crash, background lifecycle, fairness, or production exactly-once claim. The real browser primitive and OPFS contention behavior are checked by `browser:opfs-web-lock-guarded-contention-proof`.
