# Refactor audit — rev0072

## Severe failure corrected

The directory-level contract introduced in rev0068 verified identity, checksums, and generated-file hygiene, but it stopped at the directory boundary. rev0071 therefore passed its tests and package audit while the actual linked artifact was written without compression and expanded from roughly 44 MiB to 942 MiB.

The correction is architectural: archive construction and archive inspection are now first-class tested code. A future store-only recurrence fails the release command.

## Evidence retention audit

The rev0071 evidence index marked 73 of 78 bulky files as blocked by a “live reference.” Inspection showed that this was too conservative:

- many references are output destinations in historical producer scripts;
- many are documentation or generated-data provenance mentions;
- fifteen raw files were read by `audit_cube.py` only to recount rows already captured in the evidence index;
- two cold files are optional cache inputs to one historical rev0047 rerun;
- six files are still read row-by-row by inherited checks and remain hot.

The refactor replaces filename-presence reasoning with an operational distinction between hot row-level dependencies and cold preserved evidence. The inherited audit now uses catalog row counts for the fifteen count-only cases.

## What was not deleted

No cold evidence was discarded. The sidecar contains 72 original files totaling 835,771,817 bytes before compression. A full member-by-member audit checked all 72 SHA-256 values and byte counts. The sidecar itself is pinned in the core catalog by filename, size, and SHA-256.

## Remaining risk

The six hot artifacts still occupy about 47.3 MiB uncompressed. They are candidates for later derivative-based audit refactors, but removing them in this revision would mix a packaging repair with changes to replay/model verification semantics. Keeping them hot is the conservative boundary.

The cold sidecar is currently one monolithic layer. If it begins changing frequently, split future additions into append-only digest-named layers rather than rebuilding the historical base. The core catalog can then point to multiple layers while old layer hashes remain stable.
