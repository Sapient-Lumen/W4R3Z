# Rematch worlds need topology-stable delta anchors

## Claim

Budget-admissible delta bands are not yet the final inheritor-facing object. If an admissible band contains multiple distinct panel-label topologies, rematch benchmarks should publish **topology-stable subbands** or a **stability-first anchor** inside one such subband.

## Why

A single admissible parent band can still hide multiple scientifically different summaries of the same benchmark. Staying inside the same budget cap does not guarantee that the benchmark still reports the same mix of `material leader`, `practical tie`, and `undecided` panels.

That creates two new failure modes:

1. **Anchor laundering**: a report can keep the same declared budget cap and parent band while quietly moving its chosen delta across an internal state-change boundary.
2. **Boundary fragility**: a min-cost anchor can sit one grid step from a topology change, making later reinterpretation or minor rounding changes look more meaningful than they are.

## Current proxy consequence

In the current 9-panel proxy, the cap-10 low-delta admissible band splits into four topology-stable subbands, including a single-point knife edge. The inherited min-cost anchor sits extremely close to one of those internal boundaries, while a wider interior core exists that stays admissible and offers a much larger topology buffer.

## Implementor rule

Every rematch benchmark that publishes budget-admissible delta bands should also publish either:

- the **topology-stable subbands** inside each admissible parent band, or
- a **stability-first anchor** chosen from an interior topology-stable core, plus its buffer to the nearest topology boundary.

This keeps the archive compact while making the action rule much harder to game through seemingly harmless anchor motion inside a broad admissible interval.
