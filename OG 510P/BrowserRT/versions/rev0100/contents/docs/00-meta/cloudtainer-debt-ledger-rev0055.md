# Cloudtainer debt ledger — rev0055

Current office: **Cloudtainer Currentness Debt Ledger**.

This is a deliberately skeptical read of the rev0054 cube. The executable readiness-contrast surface passed, but several non-executable surfaces were still telling future sessions to resume the older readiness-gate or handoff work. That is the kind of failure that wastes cloudtainer time: the tests are green, but the next turn starts from the wrong map.

## Findings

### 1. Severe currentness drift

Central fields in `CUBE-META.json`, `REENTRY-CONTRACT.json`, `SURFACE-STATUS.json`, and `VALIDATION-INDEX.json` still named `demo:kernel-kit-readiness-gate-proof` / `facility:kernel-kit-readiness-gate-audit` as current after rev0054 added the degraded-readiness contrast. `REVISION-RECEIPT.json` was partly updated, but `current_task`, `current_audit`, `package_slug`, and `package_stamp` still carried readiness-gate values.

Correction in rev0055: set current task/slice/audit to the readiness-contrast proof and audit, and add audit checks so this does not silently pass again.

### 2. Stale plan commands

The package `plan` script still selected handoff-import files, and the Makefile plan selected an older OPFS storage-lane slice. That does not break release, but it makes the next edited turn waste time running unrelated affected tests.

Correction in rev0055: point plan commands at `src/kernel-kit-readiness-contrast.mjs`, the contrast proof/audit tools, the demo page/runner, manifest, impact map, and inventory.

### 3. Historical-doc accretion

The cube now carries hundreds of Markdown files, including many byte-identical rev-specific roadmap and audit copies. This is useful as archaeological evidence, but the archive policy says each added surface should have a deletion or consolidation condition. The current shape favors accumulation over retrieval.

Correction over time: keep only current plus previous generated contract/roadmap copies in the package, and move older duplicates into a compact `docs/00-meta/history-index.md` plus changelog references.

### 4. Artifact budget growth

Generated artifacts are the largest part of the cube. The browser Kernel Kit proof is intentionally explicit, but its JSON is large enough that repeated snapshots will dominate the package if retained without a current/previous policy.

Correction over time: package current artifacts by default; keep previous artifacts only when a differential audit explicitly needs them; compress bulky browser observations into a compact receipt unless a debugging turn asks for full observations.

### 5. Browser-only evidence remains easy to overread

The explicit browser proof is valuable because it drives the same page API a person uses. It is still a cloudtainer Chromium proof, not cross-browser, mobile, long-session, storage-eviction, quota-pressure, or production evidence.

Correction over time: preserve the explicit browser tier and add narrow browser capability matrix receipts before claiming any broad web-platform behavior.


### 6. Silent package validation wastes interactive turns

The package wrapper used a silent release sweep and then ran smoke bootstrap late. In this cloudtainer that created long no-output windows during the most expensive step, which makes a healthy validation look stalled and can invite external termination.

Correction in rev0055: package-time bootstrap now runs first, and the release sweep is visible rather than quiet. A later refinement should replace full verbosity with an explicit heartbeat mode.

## Next corrections worth doing before more feature growth

1. Add a package-time duplicate-doc budget check and make it warning-first for one revision, then fail once the archive has a compaction path.
2. Split `test/manifest.json` into source fragments plus a generated manifest, or add a manifest writer, because hand-editing large JSON is becoming a drift risk.
3. Add a compact browser proof summary artifact beside the full browser proof; make root docs link to the summary.
4. Add a `current-office` schema check for central JSONs rather than ad hoc key checks.
5. Promote cloudtainer shelf status from prose into machine-readable capability rows.

## Non-claims

No production runtime claim. No production readiness-contrast claim. No automated regression detection claim. No automated demo-go/no-go claim. No automated next-session correctness claim. No product-market-fit claim. No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim. No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim. No throughput, latency, SLO, or real performance claim. No exactly-once delivery claim.
