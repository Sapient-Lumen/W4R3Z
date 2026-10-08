# Cooperation benchmark programs should publish direct primary verify and refresh target sha256s in handoff packs

A compact handoff pack should publish one direct `primary_verify_target_sha256` and one direct `primary_refresh_target_sha256` witness alongside the first machine targets.

This keeps lineage-local machine reentry auditable without forcing inheritors to scan the retained file manifest just to confirm the exact identity of the first verify and refresh targets.

## Implications

- `primary_verify_target_sha256` and `primary_refresh_target_sha256` should be strict aliases of the retained file-manifest `sha256` values already bound by the pack.
- These fields are not a second retention or hashing semantics. They are compact local witnesses over the exact first machine targets already retained.
- When a canonical first machine target is unavailable, the corresponding direct sha256 witness should be `null`.
