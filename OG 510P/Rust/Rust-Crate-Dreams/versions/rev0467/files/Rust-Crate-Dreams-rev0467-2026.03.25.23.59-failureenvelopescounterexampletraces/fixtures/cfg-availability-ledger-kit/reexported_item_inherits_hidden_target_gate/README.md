# Scenario family — re-exported public path inherits a hidden target gate

This fixture family exists for crates that expose a friendly top-level path for an item whose real gate lives deeper in the module graph.

It is meant to catch support drift such as:

- a public `pub use` path looks unconditional,
- the underlying definition is guarded by a target-specific or feature-specific gate,
- docs summarize the exported path without preserving the lineage of that gate,
- and a naive ledger treats the top-level path as locally unconditional.

A good availability ledger should make four things explicit:

1. the **defining path** and the **exported path**,
2. each **lineage step** that carried or changed the gate,
3. the effective availability class on the exported path,
4. and whether manual review is required because the lineage or summaries lost information.
