# Cloudtainer forward momentum — rev0199

Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. Linked rev0199 is a substance-first correction of the riskiest active seam: the supposedly tiny `browserrt/runtime-core` entry had drifted over its closure budget by pulling in the product-wedge proof helper.

## What changed

- `src/runtime-core-public.mjs` and `src/runtime-core-public.d.ts` no longer import or export the product-wedge proof helper.
- `examples/runtime-core-consumer.mjs` now creates a compact runtime-core receipt locally instead of borrowing the product-wedge receipt format.
- `tools/runtime_core_entry_contract_audit.mjs` now forbids `src/product-wedge.mjs` in the runtime-core closure and fails if the helper export returns.
- `docs/00-meta/inactive-evidence-compaction-index-rev0151.md` was compacted from a duplicated table to a pointer to its JSON receipt, freeing active-cloudtainer budget without deleting attribution.

## Observed result

- Before: rev0198 runtime-core closure was 7 files / 133,739 bytes and failed the 130,000-byte budget.
- After: runtime-core closure is 6 files / 128,439 bytes; `src/product-wedge.mjs` is absent from the closure.
- Package boundary remains tight: examples 224,836 / 225,000 bytes, package src 1,448,605 / 1,450,000 bytes, 73 packed files.

## Research posture applied

Online source check reinforced the non-claims: OPFS is quota-bound and cleared with site data; persistence is observable/requested rather than assumed; Web Locks do not replace provider lifecycle cancellation after grant; Storage Buckets are a capability branch, not a baseline; and high-volume OPFS IO should be treated as a privacy/byte-time surface after FROST-style SSD timing work.

## Next correction

Do not add another registry. The next high-value refactor is structural package relief: split/suppress heavy examples and support evidence from the publish boundary, then add an OPFS byte-time/privacy posture guard before more high-IO local-first demos.

Non-claims: no runtime promotion, publication, root facade split, OPFS durability, quota reservation, eviction survival, fsync/power-loss durability, Storage Buckets support, Web Lock fairness, Service Worker lifetime, crash recovery, privacy guarantee, or cross-browser proof.
