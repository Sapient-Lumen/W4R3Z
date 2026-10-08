# Cooperation benchmark programs should publish direct focus primary verify and refresh target sha256s for compact card reentry

A compact-card reentry surface should publish one direct `focus_primary_verify_target_sha256` and one direct `focus_primary_refresh_target_sha256` witness alongside the first focus-machine targets.

This keeps first-pass inheritance locally auditable without forcing inheritors to hop into the focus-lineage handoff pack or scan its file manifest just to confirm the exact identity of those first machine targets.

## Implications

- `focus_primary_verify_target_sha256` and `focus_primary_refresh_target_sha256` should agree with the chosen focus-lineage handoff pack when one exists.
- These fields should stay strict aliases of the retained pack-manifest hashes, not a second hashing semantics.
- When no focus-lineage handoff pack exists, both direct sha256 witnesses should be `null`.
