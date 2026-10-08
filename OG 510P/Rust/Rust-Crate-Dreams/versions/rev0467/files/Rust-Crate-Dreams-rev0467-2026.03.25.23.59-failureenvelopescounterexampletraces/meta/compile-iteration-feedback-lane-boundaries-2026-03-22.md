# Compile iteration feedback lane boundaries — 2026-03-22

When future revisions touch **P-0537 Compile Iteration Feedback Kit**, keep these lanes separate.

## The six truths that must not be collapsed

1. **watch/trigger route** — what noticed the edit and what command lane fired.
2. **compile/link acceleration** — what only made rebuild or relink faster.
3. **reload surface** — whether the updated surface was markup, assets, functions, symbols, or none.
4. **patch eligibility** — whether this edit class is safe for live update, relink-only, restart-only, or manual review.
5. **state continuity** — what state survives, resets, migrates, or becomes invalid.
6. **restart fallback** — what deterministic path remains when live update is not safe.

## Do not let these stand in for an honest answer

- “the watcher reran instantly,”
- “we switched to LLD or Wild,”
- “the framework supports hot reload,”
- “the process stayed up,”
- or “the edit felt faster.”

A workflow can have all of those truths and still leave patch safety, state continuity, or restart truth unresolved.

## Adjacent proposals that must remain distinct

- **P-0469 Cargo Rebuild Explanation Kit** — why this build rebuilt.
- **P-0035 cargo-build-insights** — historical session import and trend adjudication.
- **P-0486 Debuggability Support Contract Kit** — what debugging support exists for a build.
- **P-0509 Crate Ecosystem Pathfinder Kit** — which crates to pick for a task.

P-0537 should own the edit-to-feedback contract, not all build performance or all DX.
