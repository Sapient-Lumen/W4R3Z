# Revision notes — rev0988

## Summary

Rev0988 removes a severe catalog-scaling defect from rev0987 selective-sync
dematerialization. A metadata-only file effect no longer reloads and owns the
complete folder catalog at planning, pre-unlink, and post-unlink boundaries.
Each boundary now reads one transactionally pinned metadata row and zero or one
canonical-path primary-key row.

## C++ implementation

- Added an internal `FolderCatalogPathCutpoint` carrying exact configured
  identity, limits, catalog generation, selective-sync generation/digest, and
  one optional catalog entry.
- Added a deferred-transaction loader that binds metadata and the exact
  `WHERE canonical_path=?` row to one SQLite snapshot.
- Replaced the three per-candidate complete catalog snapshots in metadata-only
  dematerialization with targeted path cutpoints.
- Centralized current-format catalog-row decoding and validation in
  `load_modern_catalog_entry_row_or_throw`, shared by complete and targeted
  loaders.
- Added `remote_targeted_catalog_path_cutpoint_count` to convergence reports and
  `remote_targeted_catalog_path_cutpoints` to both shipping JSON surfaces.

## Runtime proof

The focused folder-owner suite now includes a batch regression over eight files.
It proves three exact path reads per successful dematerialization while complete
catalog projection reads remain pass-bounded rather than effect-count-bounded.
Catalog and causal evidence remain retained and every rooted name is absent.
The one-file regression independently proves the exact three-cutpoint shape.

## Authority boundary

The targeted cutpoint is path-local authority. It does not replace complete
catalog proof for global planning, deletion inference, aggregate digests, or
terminal settlement. The rooted hash, private predecessor retention, causal
checks, atomic removal, and post-removal proof are unchanged.

The replica database owner is still an O(history) reference implementation and
still performs complete causal-state reproof around each successful
metadata-only effect. That is now the clearest remaining per-effect scaling
seam. Rev0988 does not claim million-path or multi-terabyte workload
qualification, content-defined chunking, placeholders, payload eviction,
garbage collection, Android support, or measured ENOSPC behavior.

## Validation and archive

Exact rev0988 source passed the complete GCC 14.2 Debug graph in its 540-edge configured dependency state, including 261 exact-change rebuild edges and a no-work source re-attestation. The documentation-independent registry passed 266/266 tests; the finalized targeted-cutpoint and structural audits complete 268/268 registered-test accounting. The independent GCC product lane passed 43/43 tests in bounded exact-source invocations. Focused proofs passed 532 folder-owner checks, 52/52 selective-sync audit checks, 24/24 targeted catalog-cutpoint audit checks, and 425/425 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed in bounded invocations with leak detection and halt-on-error. The direct sanitizer folder-owner proof passed 532 checks in 29.67 seconds at 1,668,096 KiB peak RSS. Aggregate inspection found no retained compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0987 parent SHA-256 matched 33680473e933ecf4e588eb24d8d90cf080002c256a2b4ed6408253424ded6d96 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 9/9 changed active files and the complete 592-file active projection byte-for-byte and mode-for-mode. That projection contains 27,537,575 bytes with SHA-256 d9d3383d821bb05d6c41b9610ec3cbe0bfaceec60ec0c968d4ea9fa430c759f9. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

`AnonSync-rev0988-2026.08.04.06.00-targetedcatalog-pathcutpoint-projectionfence-celestite.zip`
