# Constitutional ID namespace audit (generated)

Generated from `docs/20-constitution/claim-registry.md` and `docs/20-constitution/open-question-registry.md`. Do not edit directly; run `make index` after changing constitutional registries.

## `CL` namespace

- Source: `docs/20-constitution/claim-registry.md`
- Entry count: `397`
- Unique IDs: `397`
- Duplicate IDs: `0`
- Missing IDs inside observed range: `0`
- Nonmonotone adjacent transitions: `0`
- Current max: `CL-0397`

## `OQ` namespace

- Source: `docs/20-constitution/open-question-registry.md`
- Entry count: `96`
- Unique IDs: `96`
- Duplicate IDs: `0`
- Missing IDs inside observed range: `0`
- Nonmonotone adjacent transitions: `0`
- Current max: `OQ-0096`

## Audit result

- Duplicate namespace IDs: `0`
- Missing namespace IDs: `0`
- Nonmonotone adjacent transitions: `0`

## Audit rule

Constitutional IDs are not evidence, but they are authority handles. Duplicate or skipped `CL-####` / `OQ-####` entries make later route bindings ambiguous. This audit keeps registry growth visible and does not promote any scientific route.
