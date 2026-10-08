# Comptime Reflection Bridge Kit — lane boundaries (2026-03-21)

**P-0439** is about a receiver-facing bridge layer for Rust reflection-like metadata.

It answers questions like:

- Which reflection-like source produced this exported schema?
- Does that source cover declared type families, only observed concrete instantiations, or just a projection like serialization format structure?
- Does a downstream consumer need runtime registry state, or only static generated metadata?
- What was lost or synthesized while moving between reflection ecosystems?

## It is not:

### Not `bevy_reflect`
`bevy_reflect` is a runtime reflection system with its own derives, registries, and dynamic behaviors.
**P-0439** sits above it and records what a Bevy export can honestly claim to other tools.

### Not `facet` or `facet-reflect`
Those crates define their own shape model and runtime value views.
**P-0439** does not replace them; it bridges from them into a narrower, portable artifact story.

### Not `serde_reflection`
That lane extracts serialization **format descriptions**.
**P-0439** may import that evidence, but it must keep “format schema” separate from “full type-shape reflection”.

### Not a final Rust reflection standard
The Rust project goal is still experimental and compile-time-only for now.
**P-0439** should stay adapter-shaped and resist pretending the language design is settled.

### Not a runtime mutation framework
Some sources can peek or poke live values; others only emit compile-time metadata.
**P-0439** reports that distinction instead of erasing it.

### Not a universal codegen platform
Downstream code generators, editors, CLIs, config tools, and migration tools can consume bridge artifacts, but **P-0439** is not itself a whole generation framework.
