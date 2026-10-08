# Research policy

Every LLMPoetry turn begins with a web research pulse and logs it. This is both a currentness gate and an entropy gate.

## Operating sequence

1. Search or otherwise browse before substantive project action.
2. Classify each source by role using `registries/source_taxonomy.json`.
3. Add used sources to `registries/source_registry.json`.
4. Add the pulse to `registries/research_entropy_ledger.json` when packaging a revision.
5. If the revision is packaged, run `make doctor`; the current-turn pulse is validated.

## Entropy without false authority

A strange source can lend texture, form, object, or register. It cannot support a factual claim unless it is also an appropriate fact source and is registered as such.
