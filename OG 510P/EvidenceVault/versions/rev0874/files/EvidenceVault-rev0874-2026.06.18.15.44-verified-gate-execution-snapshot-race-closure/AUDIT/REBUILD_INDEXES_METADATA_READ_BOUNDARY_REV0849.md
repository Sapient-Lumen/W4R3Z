# Rebuild indexes metadata read boundary — rev0849

- Status: `early_metadata_reads_reject_symlink_boundaries`
- Validator: `scripts/validate_rebuild_indexes_metadata_read_boundary_rev0849.py`

## Purpose

Harden rebuild_indexes.py metadata and hash readers that run before the final full-tree symlink collection pass, so early JSON/identity/RO-Crate reads cannot cross archive symlink or outside-root boundaries.

## Changed surfaces

- `scripts/rebuild_indexes.py`
- `scripts/validate_rebuild_indexes_symlink_boundary_rev0845.py`

## Validator cases

- regular archive metadata JSON and hash reads pass
- final symlink metadata JSON/hash reads block
- intermediate symlink metadata JSON/hash reads block
- outside-root JSON read blocks
