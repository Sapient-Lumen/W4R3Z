# Design: Filesystem Surface Pilot Program (`cargo fscheck pilot`, `fs-pilot-pack/v0`)

## Goal
Turn the archive’s filesystem-surface idea into a ranked rollout instead of a permanently plausible layer sitting between runtime capability, settings, CLI tools, editors, and security review.

A worthy contribution here is not a rewrite of `std::fs`, `cap-std`, `camino`, `tempfile`, `atomic-write-file`, `walkdir`, `ignore`, `notify`, or `fs-mistrust`.
It is a staged proof that Rust can publish **filesystem-native evidence** across unlike path, resolution, traversal, watch, staging, durability, and trust lanes before broader product or security stacks try to absorb them.

## Why this needs a pilot layer
The current ecosystem already has all the ingredients needed to drift into confusion:
- std now explicitly documents TOCTOU hazards and atomic/open-handle guidance;
- `camino` makes UTF-8 path posture explicit;
- `cap-std` makes rooted capability-relative access explicit;
- `tempfile` and `atomic-write-file` distinguish staging, replace, and durability caveats;
- `walkdir`, `ignore`, and `notify` expose different scan/watch semantics; and
- `fs-mistrust` shows that path trust/privacy checking is its own ecosystem need.

That means the boundary only becomes real if it survives actual cross-lane adoption.

Sources:
https://doc.rust-lang.org/std/fs/
https://doc.rust-lang.org/std/fs/fn.canonicalize.html
https://doc.rust-lang.org/std/fs/fn.rename.html
https://doc.rust-lang.org/nightly/std/fs/struct.Dir.html
https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
https://docs.rs/camino/latest/camino/
https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
https://docs.rs/atomic-write-file/latest/atomic_write_file/
https://docs.rs/walkdir/latest/walkdir/struct.WalkDir.html
https://docs.rs/ignore/latest/ignore/struct.WalkBuilder.html
https://docs.rs/notify/latest/notify/
https://docs.rs/fs-mistrust/latest/fs_mistrust/

## Ranked pilot order

### Pilot 1 — Save semantics pair
Use one ordinary direct-write lane and one staged-publish lane.

Must prove:
- direct truncate/create/write posture can be described honestly;
- staged temp-file publish can be described without overclaiming durability;
- `persist`, replace, no-clobber, cleanup, and leftover behavior survive portable packaging;
- vector results can show where “atomic enough for UI” and “durable after crash/power loss” diverge.

Why first:
- it reaches ordinary applications immediately;
- it prevents the pack from becoming “watch metadata with extra steps”;
- save semantics are where user-visible corruption risk appears fastest.

### Pilot 2 — Path-kind and display bridge pair
Use plain `Path` / `OsStr` plus a UTF-8-path or display-simplification lane.

Must prove:
- `Path` vs `Utf8Path` posture can be published without pretending one subsumes the other;
- canonical machine paths and display-safe paths can coexist in one pack;
- Windows path-shape caveats remain visible instead of disappearing in normalization prose.

Why second:
- it proves the archive can keep path-kind and display concerns distinct before capability and watch lanes complicate matters;
- it makes migration and CLI/reporting fallout concrete.

### Pilot 3 — Rooted/capability lane
Use `cap-std` or another open-directory-rooted implementation.

Must prove:
- rooted descendant operations can be described as a different authority lane, not a different spelling of relative paths;
- relative canonicalization/output semantics can be preserved;
- adapters between rooted/capability and bare-path lanes can declare their lossiness honestly.

Why third:
- it is the strongest security- and sandbox-relevant lane in the current ecosystem;
- it stress-tests whether the pack can preserve authority posture cleanly.

### Pilot 4 — Traversal lane
Use `walkdir` and `ignore` together.

Must prove:
- symlink-following, deterministic ordering, same-filesystem boundaries, and ignore precedence can be represented explicitly;
- traversal vectors can capture real differences between `walkdir` and `ignore` defaults and options;
- traversal semantics can remain separate from later watch or indexing consumers.

Why fourth:
- recursive scans are widely used and easy to over-flatten;
- this is the first point where filesystem semantics become large-scale tool behavior rather than single-path behavior.

### Pilot 5 — Watch lane
Use `notify` with both native and polling backends where possible.

Must prove:
- native backend identity and polling fallback remain explicit;
- editor-save, rename/remove, network-filesystem, and platform-specific caveats survive the pack boundary;
- watch semantics can import traversal/root info without collapsing into it.

Why fifth:
- watching is strategically important for editors, tools, and local-first systems;
- it tests the hardest real-time filesystem lane without making it define the whole schema too early.

### Pilot 6 — Trust/privacy lane
Use `fs-mistrust` or an adjacent trust-checking integration.

Must prove:
- trust/privacy checking remains distinct from capability-rooted access;
- ancestor and symlink-sensitive checks can be represented without pretending canonicalization solved them;
- downstream security review can import trust-check packs without treating them as general filesystem correctness proof.

Why sixth:
- it is strategically valuable, but easier to model honestly once path-kind, rooted access, staging, traversal, and watch lanes already exist.

## Shared schema discipline
Every pilot must keep these pairs distinct:
1. **bare-path std semantics** vs **rooted/capability semantics**
2. **UTF-8 path posture** vs **display/canonical bridge policy**
3. **traversal semantics** vs **watch/event semantics**
4. **temp staging** vs **durability guarantees**
5. **rooted access** vs **trust/privacy checking**
6. **portable summary** vs **tool-native raw fixtures/logs/events**

## Immediate archive consequences
Read this together with:
- [`design/filesystem-surface-lane-map.md`](./filesystem-surface-lane-map.md)
- [`design/filesystem-surface-kit.md`](./filesystem-surface-kit.md)
- [`design/runtime-capability-kit.md`](./runtime-capability-kit.md)
- [`design/runtime-settings-kit.md`](./runtime-settings-kit.md)
- [`design/command-surface-kit.md`](./command-surface-kit.md)
- [`proposals/epic-filesystem-surface-kit.md`](../proposals/epic-filesystem-surface-kit.md)

The archive should now prefer:
- **filesystem evidence importers before new helper facades**,
- **path/resolution/watch/staging honesty before universal “safe fs” claims**,
- and **lane-aware filesystem packs before downstream product/security abstractions**.

## What should wait
Do **not** start with:
- another universal path crate,
- another watcher wrapper pretending native and polling are the same,
- another “atomic write solves durability” API,
- or a single mega-abstraction trying to replace std paths, capability handles, traversal, watch, and trust checks at once.

Those may become consumers or adapters later. They are not the missing substrate.
