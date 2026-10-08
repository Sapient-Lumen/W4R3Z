# Rematch world benchmark fill work should flow through one tiny patch, then compile back to one artifact

The archive already knows that the first endogenous rematch benchmark should land as one retained JSON artifact.

That does **not** mean the inheritor should do scratch work by repeatedly editing or copying the full retained seed. The seed intentionally embeds the frozen compact decision bundle so the final published artifact can stay self-contained, but that same property makes the seed a poor scratch surface.

## Compact execution rule

During fill work, the inheritor should operate on one compact fill patch that carries only the mutable benchmark surface:

- `benchmark_id`
- `world_semantics_contract`
- `matching_state_contract`
- `occupancy_accounting_contract`
- `turnover_tempo_contract`
- `paired_ranking_views_contract`

The patch should **not** copy:

- `compact_decision_bundle`
- publication / decision contract pointers that are already frozen in the seed
- static shape metadata such as `required_sections`

Once the world-dependent fields are filled, the patch should be compiled back onto the standing seed to produce the one retained benchmark artifact.

## Why this helps

This keeps scratch state small while preserving the standing one-artifact publication story.

The inheritor gains three things at once:

1. a smaller editable surface during fill work,
2. no temptation to hand-edit the copied compact decision bundle,
3. and one deterministic path back to the publishable retained artifact.

## Operational sequence

1. Regenerate `examples/snapshots/rematch_world_benchmark_fill_patch.json` if the standing seed changes.
2. Fill the patch instead of the full seed.
3. Compile the patch back onto the seed with `scripts/tools/apply_rematch_world_benchmark_fill_patch.py`.
4. Run the mutation guard and completion gate on the compiled benchmark artifact.
5. Retain the compiled benchmark artifact, not a long chain of patch sidecars.

That keeps the archive aligned with its size discipline: compact scratch is allowed, but long-term retained state should converge back to one benchmark artifact rather than spreading into another benchmark-sidecar family.
