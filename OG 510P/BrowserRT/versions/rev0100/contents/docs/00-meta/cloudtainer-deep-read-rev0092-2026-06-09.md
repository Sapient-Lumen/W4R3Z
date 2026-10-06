# Cloudtainer deep read — rev0092 session note

Generated: 2026-06-08 23:51 EDT  
Source archive: `BrowserRT-rev0092-2026.06.05.22.10-opfs-web-lock-quarantine-restore-expected-fingerprint-proof(3).zip`

## Status after this session

The rev0092 expected-fingerprint work remains green. I ran `check_cube` after the corrective patch and it passed. The patched `npm run test:current` resolved to the rev0092 expected-fingerprint release pair and passed 2/2. The patched `npm run audit:current` wrote the expected-fingerprint contract audit. The patched `npm run test:browser:current` resolved to the expected-fingerprint OPFS/Web Locks proof and passed 1/1.

The full release tier was also run before the patch and passed 130/130. I did not run the full browser tier; the manifest estimates that tier at roughly 0.0s (0.0 minutes) serial across 61 tasks, so broad browser sweeps remain a turn-expensive choice.

## Corrected in this linked archive

1. `package.json` current aliases were stale even though central metadata was current. The worst offenders were `test:current`, `test:browser:current`, `audit:current`, `test:browser-current`, and `package:current`. They pointed at the previous provenance-binding/replay-guard slice or older timestamps instead of the rev0092 expected-fingerprint work.
2. `tools/check_cube.py` now checks those primary current aliases. The cube should now fail fast if a future package advertises one current proof while the convenience entry points run another.
3. This report plus `artifacts/audit/REV0092-CLOUDTAINER-DEEP-READ.json` make the cloudtainer debt discovered in-session part of the revision payload.


## Packaging waste correction discovered during the session

After the first report draft, a package run failed the cube's own artifact budget audit: the earlier exploratory full-release run had left 112 transient per-proof artifacts under `artifacts/validation` and `artifacts/audit`, raising the source tree to roughly 10.47 MB against the 8 MiB soft budget. I removed those transient files rather than weakening the budget. After pruning, the artifact budget audit passed again at 7,560,519 bytes, `check_cube` passed, and `verify_release` passed on the linked archive.

This is a useful cloudtainer lesson: full release sweeps are fine as validation, but their per-task byproducts should either be explicitly retained as evidence or cleaned before packaging. Otherwise the project can fail for storage drag even when all proof claims are green.

## What is still missing

### Current-office coverage is incomplete

`check_cube` had strong checks for central metadata, release docs, manifest rows, and generated artifact revisions, but not for the convenience commands that humans actually reach for during a session. This is how the archive could be internally green while `npm run test:current` still ran the previous slice. The new alias guard closes the primary hole, but a broader current-office schema should also cover Makefile package/verify paths, package release timestamps, and any script name containing `current`.

There are still historical aliases with confusing names, including `current:quarantine-clearance-receipt-provenance-binding`, `quarantine-receipt-restore-integrity-current`, and `quarantine-status-transition-import-current`. Some may be intentionally retained replay shortcuts, but their names make them dangerous. Rename them to `replay:<slice>` or `historical:<slice>`.

### Browser/platform proof debt remains the main claim gap

The cube is honest that it does not yet claim cross-browser behavior, quota behavior, eviction behavior, crash durability, or production readiness. That should stay explicit. The next useful evidence is not another narrow happy-path OPFS proof; it is a small, repeatable platform matrix:

- Chromium OPFS + Web Locks current canary.
- Firefox/Safari smoke probes if CI or local runners are available.
- Storage pressure/estimate/persistence probes that avoid destructive disk filling.
- Abrupt page close / worker kill / process kill recovery probes for the storage lane.
- Clear separation between async OPFS block-store behavior and sync-access-handle worker behavior.

### The next “tamper-proof” name is too strong unless the trust model changes

Rev0092 expected-fingerprint restore is a useful operator guard: it blocks valid-but-wrong ledgers/receipts before import or registration. It should not be sold as adversarial tamper proof. The code path uses project fingerprints as binding evidence, not cryptographic attestation. A real tamper-evident/tamper-resistant slice needs canonical byte serialization, WebCrypto digest/HMAC/signature choices, receipt expiry/revocation, key lifecycle, and an explicit statement about who the attacker is.

Suggested rename if the mechanism stays lightweight: `tamper-evident-expected-digest-binding` rather than `tamper-proof`.

### OPFS/Web Locks edge semantics should move into preflight checks

`src/web-lock-coordinator.mjs` already guards some option conflicts, but it should also locally reject invalid combinations such as `steal + ifAvailable` and `steal + shared`, and it should validate/coerce lock names before calling string methods. That gives stable BrowserRT errors rather than letting browser engines or accidental TypeErrors define the contract.

### The cube is becoming a proof museum

Current measured shape:

- Files in working tree: 1097
- `package.json`: 163,140 bytes, 290 scripts
- Manifest tasks: 237
- Release tier: 130 tasks, estimated 0.0s
- Browser tier: 61 tasks, estimated 0.0 minutes serial
- Normalized duplicate doc groups: 42 groups covering 105 files
- Tool clone-like pairs at Jaccard >= 0.65: 275
- Remaining scripts mentioning `REV0089`: 193
- Remaining scripts mentioning `REV0090`: 2

The exact duplicate-doc budget is green, but normalized duplicates and clone-like tools show that historical drift has been copied forward structurally. The largest generated surfaces are now data products rather than code: manifest, surface inventory, impact map, release manifest, package scripts, and proof artifacts.

## Correct over-time changes

1. Add a `current-office` audit that verifies docs, central JSON, Makefile targets, npm scripts, manifest current IDs, validation artifact paths, and package/verify paths all describe the same current proof.
2. Replace one-off proof-tool copies with a table-driven quarantine proof harness. Keep per-slice docs, but generate the repeated tool bodies from a manifest row.
3. Split `package.json` into stable human scripts and generated historical replay scripts. Human scripts should be fewer than twenty and should never contain stale revision literals.
4. Add a browser-proof summary artifact that points to the last full browser sweep and carries only the current canary proof in the package hot path.
5. Move older generated evidence into a compressed or indexed evidence shelf once it is no longer the current or previous revision.
6. Decide whether BrowserRT is a platform proof kit, a local-first storage runtime, or a demo product. If it is meant to become usable software, add one tiny external-facing wedge: boot worker, OPFS block write/read, Web Lock guard, quarantine timeout, restore receipt, and a trace viewer.

## Speculation

The browser primitives are no longer exotic enough to justify endless primitive proof slices. OPFS and Web Locks are mainstream enough that BrowserRT's value should shift to discipline: cheap evidence, careful non-claims, storage-lane recovery semantics, and a small public API that prevents common browser-storage mistakes.

The most wasteful future path would be to continue adding one bespoke proof file per edge case while the current-office map keeps drifting. The highest-leverage path is to make the cube smaller to reason about: parameterized proofs, stronger current-office checks, and browser canaries that are explicit about what they do not prove.
