# Session review — rev0849

- Created: `2026-06-13T14:21:00Z`
- Role: overlay/patch refactor bundle, not a canonical signed release
- Derived from: `EvidenceVault-rev0848-2026.06.13.12.52-builder-boundary-public-path-integrity-hardening.zip`

## Risk focus

- Prevent a future public release snapshot from digesting public entry payloads not explicitly authorized by the queue decision.
- Ensure HTML/XML docs materials are in scope for the fresh local rights-reference scan.
- Stop early rebuild metadata/hash reads from crossing symlink or outside-root boundaries before the final full-tree scan.

## Substantive changes

- `scripts/publish_queue_item.py`: `validate_public_paths_against_snapshot()` now blocks snapshot `entry_points` absent from `decision.public_paths`, in addition to blocking decision paths absent from the snapshot/source manifest.
- `scripts/publication_rights_gate.py`: scan roots now include `docs/` and `documentation/`, and text suffix coverage now includes `.html`, `.htm`, `.xhtml`, and `.xml`.
- `scripts/rebuild_indexes.py`: early JSON/text/hash readers now require archive-local regular files with no final or intermediate symlink components, and the release-manifest/RO-Crate/source-index/metadata validation paths use those readers.

## New evidence

- `AUDIT/PUBLISH_QUEUE_ITEM_AUTHORIZED_SNAPSHOT_ENTRIES_REV0849.*`
- `AUDIT/PUBLICATION_RIGHTS_GATE_HTML_DOCS_SCAN_REV0849.*`
- `AUDIT/REBUILD_INDEXES_METADATA_READ_BOUNDARY_REV0849.*`
- `scripts/validate_publish_queue_item_authorized_snapshot_entries_rev0849.py`
- `scripts/validate_publication_rights_gate_html_docs_scan_rev0849.py`
- `scripts/validate_rebuild_indexes_metadata_read_boundary_rev0849.py`
- `VALIDATION/rev0849_targeted_validation.txt`

## Deliberately unchanged

Publication remains blocked. This revision does not invent root `LICENSE`, `COPYING`, `NOTICE`, component license conclusions, SPDX rights assertions, or RO-Crate rights metadata.

The rev0840 canonical patch streams remain unchanged.
