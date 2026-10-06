# Branch continuity audit slice — rev0062

`facility:branch-continuity-audit` is a browser-light static audit added after the rev0062 branch split. The risk is not a browser API behavior by itself: it is packaging a later revision that contains the Web Lock timeout work while silently dropping the corrupt-block repair work or the tab-termination lifecycle proof.

The audit checks that three runtime branches are present together:

- OPFS corrupt final-hash detection and repair: `BRT_OPFS_BLOCK_CHECKSUM_MISMATCH`, `repairedCorrupt`, post-write verification, and the fake/browser corrupt repair probes.
- Web Lock acquisition timeout/backstop: `BRT_WEB_LOCK_TIMEOUT`, abort-backed pending request timeout, and release/browser timeout probes.
- Multi-page tab lifecycle coordination: normalized `queryLocks`, `waitForSettled`, and the browser tab-termination proof that closes a holder target while a guarded OPFS mutation waits.

It also checks that the manifest, impact map, and surface inventory wire all three branches. This is intentionally a release-tier audit because it should catch branch divergence cheaply before browser-heavy proof runs.

Non-claims: static/source audit only; no cross-browser Web Locks or OPFS claim, no quota or eviction claim, no crash or power-loss durability claim, no fairness or production readiness claim.
