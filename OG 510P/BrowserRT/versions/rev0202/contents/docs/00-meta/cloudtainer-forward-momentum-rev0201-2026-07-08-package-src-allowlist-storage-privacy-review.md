# Cloudtainer forward momentum — rev0201

Current packaged head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. Linked rev0201 is a substance-first package-boundary and storage-posture correction, not a runtime promotion.

## Risk selected

The sharpest risk was the package `src` budget, not a missing registry. Rev0200 still packed broad `src/*.mjs` / `src/*.d.ts` globs and observed only 1,395 bytes of package-src headroom. That invited the wasteful correction of widening limits or compacting human-readable source further. Rev0201 instead makes the publish surface explicit and auditable.

## What changed

- `package.json` now ships an explicit source/type allowlist for the public API, runtime-core subpath, browser storage posture subpath, and dynamic worker entrypoints. Broad `src/*.mjs` and `src/*.d.ts` are no longer accepted.
- `tools/package_tarball_boundary_contract_audit.mjs` now derives the public/runtime package source closure, includes the dynamic worker URL entrypoints, and fails on any unused packed source or missing closure file.
- `tools/public_api_contract_audit.mjs` was updated to enforce the new explicit package allowlist instead of the old broad source glob expectation.
- `src/browser-storage-posture.mjs` now adds an advisory storage privacy policy: large planned OPFS writes can emit `storage-timing-side-channel-review` and require product review before background IO.
- `tools/browser_storage_posture_probe.mjs` proves both the normal no-large-write path and the large planned-write review path; managed Chromium storage posture still passes.
- The storage posture code was compacted enough to keep runtime-core under its existing 130,000-byte closure budget instead of widening the budget.

## Observed result

- Package source bytes dropped from 1,448,605 to 1,395,339; source margin rose from 1,395 to 54,661 bytes.
- Package file count dropped from 73 to 63; packed bytes dropped from 309,772 to 298,050.
- Runtime-core closure is 129,576 / 130,000 bytes across 6 files, with product-wedge still absent from the closure.
- Browser current resumed from checkpoints and reports 12/12 passed.

## Research posture applied

artifacts/research/REV0125-BROWSER-RUNTIME-SOURCE-CHECK-REV0201.json records current OPFS/Storage/Web Locks/Storage Buckets/FROST source checks. The important product change is intentionally modest: FROST-class OPFS SSD-timing research becomes an advisory large planned-write review trigger, not a mitigation claim.

## Audit trail

artifacts/datacube-audit/REV0125-PACKAGE-SRC-ALLOWLIST-STORAGE-PRIVACY-REVIEW-REV0201.json records the before/after package boundary metrics, allowlist proof, runtime-core closure margin, storage privacy posture proof, and validation commands.

## Next correction

The root facade and demo/proof helper package surface are still the next structural risks. Avoid adding another registry: either split the full facade out of the installed adoption path or move proof-heavy helpers behind a non-published support surface while preserving package consumer smoke.

Non-claims: no runtime promotion, publication, production readiness, root facade split, quota reservation, eviction survival, fsync or power-loss durability, Storage Buckets support, Web Lock fairness, Service Worker lifetime proof, browser-kill/crash recovery guarantee, privacy/fingerprinting mitigation, or cross-browser proof.
