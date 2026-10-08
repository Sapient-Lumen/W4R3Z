# P0005-D001 Bloom false-presence and release-scaffold audit — rev0070

## Priority decision

The cube's highest-risk unfinished work remains external disclosed-reader evidence, but no real reader is present in this turn and no response is fabricated. The best substantive move available inside the cube is therefore a genuinely different machine-native wager, not another revision of deletion/absence and not another candidate wrapper.

`P0005-D001` commits an exact false positive. The ledger contains `CASE-0017`, `CASE-0021`, and `CASE-0028`, never `CASE-1001`. The absent query maps to bits 17, 28, and 26. Every bit is set, and each is owned by a different inserted record. The four-byte filter answers `POSSIBLY PRESENT`; the exact set answers `NOT PRESENT`. The builder and independent checker reproduce all bytes.

This is deliberately synthetic. It claims no current/live status, rate, person, case, screening system, or adverse action. Its literary risk is acute: the distributed error may feel like a record assembled from other people's truths, or it may remain a neat Bloom-filter diagram. The draft stays same-turn unjudged.

## Source pressure

The design is bounded by Bloom's 1970 paper metadata and NIST's later explanation of bit arrays, possible membership, false positives, and small-filter rate-estimation caution. The artifact itself proves the exact collision and makes no approximate rate claim.

## Waste and refactor findings

### Parent-dependent constructors were being shipped

The rev0069 archive carried 22 root-level `do_rev*.py` constructors totaling 1,382,114 bytes. They cannot build the current release alone: they depend on prior trees, contain one-turn migration literals, and contradict the pruning policy's statement that the working cube is not a preservation archive. Rev0070 records their exact names, sizes, and hashes in the JSON audit and removes them from the distributable tree. Historical release archives remain the preservation layer.

### Release safety logic was duplicated

Manifest building, archive packaging, and post-package inspection each carried overlapping path and member logic. `tools/release_tree.py` now owns canonical relative-path validation, symlink rejection, case-fold collision detection, release-member collection, fixed ZIP metadata, and archive verification. The three release entrypoints import it rather than drifting separately. Parent-dependent `do_rev*.py` constructors are now an explicit release exclusion and a packaged-constructor failure condition.

### A current-state invariant surface had escaped validation

`ARCHIVE_INVARIANTS.json` still advertised `rev0024` and `P0002-D010` while the actual incoming head was P0004-D002. The previous checker verified seed/specimen conditions but never checked the invariant surface's own revision or head. Rev0070 currentizes that file and gates revision, head, unsafe release paths, and absence of root revision constructors.

## What did not happen

No real-reader response was added. No candidate was promoted. No P0005-D002, P0004-D003, P0003-D005, or P0002-D029 was created. P0003-D004 and P0004-D002 remain byte-frozen; P0002-D010's response log remains empty.

## Next stop

A later turn should cold-review the exact P0005-D001 bytes. The central question is whether “All three bits said yes. / No record did.” creates a pressure not exhausted by mechanism disclosure. The external reader pilot remains operationally first whenever a real reader is available.
