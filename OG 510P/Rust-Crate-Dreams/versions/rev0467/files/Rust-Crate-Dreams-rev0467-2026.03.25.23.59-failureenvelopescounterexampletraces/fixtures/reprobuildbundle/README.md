# reprobuildbundle fixtures

These fixtures sketch the receiver-facing artifacts for **P-0242 Reproducible Build Evidence Kit**.

The goal is to make the proposal answer a concrete handoff question:

> what files should another maintainer, rebuilder, or reviewer actually receive?

## Artifact lanes

- `build-recipe.schema.json` — what source/toolchain/config/environment was claimed.
- `rebuild-verdict.schema.json` — whether the compared outputs reproduced exactly, semantically, or not at all.
- `diff-summary.schema.json` — smallest useful explanation of the observed drift.

## Scenario shape

Each scenario should ideally include:

- short notes,
- one or more recipe examples,
- a verdict example,
- and a diff summary example.

The fixtures intentionally keep the schema surface small. Raw `diffoscope` HTML/JSON outputs, signatures, and deterministic bundle packing belong in lower or adjacent layers.
