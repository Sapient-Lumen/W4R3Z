# Cargo lock-contention lanes — 2026-03-16

## Main judgment

**P-0490 Cargo Lock Contention Witness Kit** should now be treated as a nearly-buildable support-bundle crate, but only if future passes keep three boundaries explicit:

1. **shared-root topology**,
2. **live wait evidence**,
3. **optional imported-session context**.

The worthy crate is not another generic Cargo performance dashboard.
It is the boring artifact layer that can tell another person:

- which roots were in play,
- which roots were actually shared,
- what wait was observed,
- what evidence lane supplied that fact,
- and how sure the bundle is.

## The root classes that must stay separate

Current Cargo and rust-analyzer docs make at least four materially different coordination surfaces visible:

1. **target-dir** — final artifacts and user-facing outputs.
2. **build-dir** — intermediate compiler/build-script artifacts.
3. **Cargo home package/index/git cache roots** — registry and source caches.
4. **wrapper/cache-mode overlays** — `RUSTC_WRAPPER`, `RUSTC_WORKSPACE_WRAPPER`, rust-analyzer wrapper behavior, and any resulting cache separation.

A good lock-contention bundle should be able to say:

- “rust-analyzer split target-dir, but build-dir remained shared,”
- “target-dir and build-dir were isolated, but package-cache work still serialized fetch/update activity,”
- or “the roots were shared, but wrapper-induced cache separation made duplicate work and contention harder to interpret.”

## Session imports are allowed support context, not blocker proof

Cargo’s build-analysis work creates a useful new seam for this proposal:

- `cargo report sessions`
- `cargo report timings`
- `cargo report rebuilds`

Those surfaces make it reasonable for **P-0490** to import one session as supporting context.
They do **not** mean the crate can suddenly identify the blocking process with certainty.

Future passes should preserve an explicit distinction between:

- **observed wait facts**,
- **root-sharing facts**,
- **imported session context**,
- and **manual annotations**.

If the bundle only knows that a build-analysis session overlapped the witness window, that should live in `build-analysis-session.link.json`, not inside the blocker verdict itself.

## What this crate is not

### Not P-0494
**P-0494 Cargo Compile-Time-Deps Workflow Kit** is still about **tool-facing workflow parity and root-lane truth**.
P-0490 may reuse root-lane facts, but it should stay on **blocking / waiting / shared-root topology**.

### Not P-0469
**P-0469 Cargo Rebuild Explanation Kit** is still about **why work rebuilt**.
P-0490 is about **why progress stalled**.
The same support bundle may import context from both, but the lane boundaries should stay visible.

### Not P-0035
**P-0035 cargo-build-insights** is still the **historical warehouse / trend lane**.
P-0490 may attach one imported session, but it should not become a long-term build-history store.

### Not P-0436
**P-0436 Target-Dir Lease & Shared Cache Coordination Kit** is still the **policy / lease / cleanup / coordination** lane.
P-0490 is the **incident witness** lane.

### Not P-0489
**P-0489 Cargo Build-Dir Consumer Transition Kit** is still about **tool migration off build-dir internals**.
P-0490 may mention `build-dir`, but should not drift into consumer migration planning.

## Best next repo moves

Future revisions on this lane should prefer:

1. schema-first exactness and evidence-source artifacts,
2. scenarios where target-dir, build-dir, and package-cache sharing diverge,
3. optional build-analysis session linkage with explicit caveats,
4. compact redaction-safe support bundles.

They should not drift into:

- active process scheduling,
- kill/retry orchestration,
- another general build profiler,
- or another build-history warehouse.

## Sources

- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://doc.rust-lang.org/cargo/reference/build-cache.html
- https://doc.rust-lang.org/cargo/reference/environment-variables.html
- https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- https://rust-analyzer.github.io/book/faq.html
- https://rust-analyzer.github.io/book/configuration
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
