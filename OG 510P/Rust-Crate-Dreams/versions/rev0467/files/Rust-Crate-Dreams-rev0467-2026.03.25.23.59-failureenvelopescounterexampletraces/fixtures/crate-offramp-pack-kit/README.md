# crate-offramp-pack-kit fixtures

This fixture pack exists to make **P-0515 Crate Off-Ramp Pack Kit** concrete.

The goal is not to prove every migration story.
The goal is to make five truths reviewable:

1. **successor intent truth** — what is being sunset and what class of replacement is actually being claimed,
2. **successor authority truth** — who is actually making that claim,
3. **stopgap horizon truth** — whether a shim or last-safe pin is only temporary and where the boundary is,
4. **recipe witness truth** — what migration path was really checked and what still needs manual review,
5. **portable bundle truth** — whether those claims travel together without collapsing into one verdict.

## Core artifacts

- `successor-map.report.schema.json`
- `deprecation-surface.receipt.schema.json`
- `offramp-recipe.manifest.schema.json`
- `successor-compat.report.schema.json`
- `sunset-check.report.schema.json`
- `offramp-diff.report.schema.json`
- `successor-authority.receipt.schema.json`
- `stopgap-horizon.report.schema.json`
- `recipe-witness.report.schema.json`
- `offramp-support-bundle.manifest.schema.json`

## Scenario families

- `crate_rename_shim/`
- `security_offramp/`
- `successor_split/`
- `no_successor_manual/`
- `rustdoc_note_and_stopgap_authority/`
- `last_safe_pin_horizon/`
- `rename_recipe_witness_scope/`
- `portable_bundle/`
