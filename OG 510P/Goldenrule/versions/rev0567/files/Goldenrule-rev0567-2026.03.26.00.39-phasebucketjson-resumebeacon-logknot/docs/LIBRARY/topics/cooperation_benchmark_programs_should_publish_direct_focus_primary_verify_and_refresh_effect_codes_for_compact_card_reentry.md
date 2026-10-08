# Cooperation benchmark programs should publish direct focus primary verify and refresh effect codes for compact-card reentry

If the fused compact-card reentry surfaces already publish the direct first focus verify command and the direct first focus refresh command, they should also publish one small effect-code witness for each of those commands.

The goal is to make first-pass reentry locally legible: the inheritor should be able to tell whether the first focus command is a read-only check or a state-changing rewrite without reverse-engineering command names.

For the canonical compact-card control plane, witness, and next-action surfaces, that means publishing `focus_primary_verify_effect_code` and `focus_primary_refresh_effect_code` as strict aliases of the lineage-local handoff-pack semantics already retained for the focus lineage.
