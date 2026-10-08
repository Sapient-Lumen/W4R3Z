# Scenario — std-contract authority plus one Kani profile does not settle other consumers

This scenario exists to prove that one imported contract surface and one consumer lane do not justify a cross-tool completeness claim.

The example receipt should show:

- compiler-native or std-like contract authority for each clause,
- the extraction route used to capture it,
- and any normalization or manual-review gaps that still fence the snapshot.

Use this when a team wants to say “the contracts are there” but has only demonstrated one Kani-shaped consumption route.
