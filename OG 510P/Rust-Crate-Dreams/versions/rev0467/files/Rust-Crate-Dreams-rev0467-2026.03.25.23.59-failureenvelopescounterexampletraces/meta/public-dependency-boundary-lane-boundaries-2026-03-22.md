# Public dependency boundary lane boundaries — 2026-03-22

Keep **P-0431** separate from these adjacent lanes.

## 1. Not generic public-API diffing

If the primary question is “what public items changed?”, that belongs primarily to public-API / SemVer lanes.

P-0431 owns **dependency-boundary truth**, not the full public API change surface.

## 2. Not the compiler lint itself

rustc and Cargo own `exported_private_dependencies` and `public = true`.
P-0431 owns the **review bundle above them**: intent, verdict, route, provenance, gaps, and migration.

## 3. Not external-type allowlisting alone

`cargo-check-external-types` is useful substrate for exposed external types.
P-0431 must stay broader:

- manifest intent,
- Cargo/rustc provenance,
- workspace limitations,
- migration posture.

## 4. Not dependency lifecycle / criticality planning

If the primary question is where a third-party dependency is allowed to live in a system and how it exits over time, that belongs primarily to **P-0535 Dependency Lifecycle Transition Kit**.

P-0431 owns whether the dependency is part of the public API boundary today.

## 5. Not documentation rendering or cargo-doc filtering by itself

RFC 3516 notes documentation implications, but if the main job is docs generation, docs support classes, or doctest execution, that belongs elsewhere.

P-0431 may later export boundary facts to docs tooling, but it is not the docs tool.
