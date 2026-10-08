# Rust-blocked cloudtainer sessions should shift to static surface mapping and Python shadow work

When a session inherits a cloudtainer with Python/Node but no working `cargo`, `rustc`, or JuNest fallback, the productive move is not to stall and not to drag a bulky toolchain into the archive by default. The cheaper durable move is to preserve one static Rust navigation artifact, advance the Python-shadow lanes that can still be checked locally, and leave runtime-semantic claims explicitly blocked until the Rust lane can rerun.

A good blocked-toolchain workflow stays small:
- regenerate `docs/RUST_SURFACE_INVENTORY.md` so future inheritors can recover module boundaries, hotspots, and likely reading order without compiling the crate,
- keep contract, schema, report, and small-state math work in Python where local execution still exists,
- use the Rust Playground or Compiler Explorer only for tiny self-contained snippets when a remote compile is actually needed, and
- prefer syntax-only parsing routes such as Tree-sitter when source-shape insight is enough (`RS-OPS-006`..`RS-OPS-010`).

Why this matters:
- the official Rust site and docs explicitly point to the Rust Playground as a no-install path for trying Rust and small code snippets,
- Compiler Explorer already exposes compile/execute/output inspection for small examples,
- Tree-sitter and the upstream Rust grammar make syntax-only source analysis possible without invoking Cargo,
- and the archive already has a strict size discipline that favors compact citations and small retained handles over large downloaded toolchains or copied external bodies.

The resulting handoff is better for the next implementor: one small map of the blocked Rust surface, one explicit note about what local claims remain provisional, and no unnecessary archive bloat. When the Rust lane comes back, that later session can replace the provisional shadow work with actual runtime evidence instead of first rediscovering where the engine lives.
