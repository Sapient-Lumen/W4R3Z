# Cooperation benchmark programs should publish direct focus primary verify and refresh target byte counts for compact-card reentry

If the fused compact-card reentry surfaces already publish the direct first focus verify and first focus refresh targets, they should also publish one small retained byte-count witness for each of those targets.

The goal is to make first-pass reentry locally auditable: the inheritor should be able to tell the approximate size of the first machine target without diving into the focus lineage handoff manifest.

For the canonical compact-card control plane, witness, and next-action surfaces, that means publishing `focus_primary_verify_target_bytes` and `focus_primary_refresh_target_bytes` as strict aliases of the lineage-local handoff-pack file-manifest bytes already retained for the focus lineage.
