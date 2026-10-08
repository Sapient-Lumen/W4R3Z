## Rev0338 sharpened frontier: filesystem surfaces need an explicit lane map
The archive already had the right filesystem substrate, but it still needed a clearer map of the **different filesystem lanes** Rust is actually using.

That is now important because today’s ecosystem is visibly plural:
- std `fs` explicitly documents TOCTOU hazards and open-handle/atomic-operation guidance;
- `canonicalize` still produces machine-correct paths that can be awkward display or interop paths on Windows;
- `cap-std` keeps rooted capability-relative operations explicit;
- `camino` keeps UTF-8 path posture explicit;
- `tempfile` and `atomic-write-file` make staging and durability a real lane split rather than one fake “atomic save” promise;
- `walkdir` / `ignore` keep traversal policy plural; and
- `notify` / `fs-mistrust` prove that watching and trust/privacy checks are real filesystem-adjacent lanes too.

So the missing contribution is not another helper crate. It is a reviewable lane-aware boundary above today’s filesystem crates and below downstream CLI/editor/security/product stacks.


# Gap: filesystem surfaces, path semantics, traversal policy, durable mutation, and reviewable filesystem contracts

## What is missing
Rust has strong filesystem primitives, but the ecosystem still lacks a **portable way to publish what a filesystem surface actually means**.

Today there is no standard way to say:
- whether paths are treated as opaque `Path` / `OsStr` values, UTF-8-only paths, capability-relative paths, or canonicalized absolute paths,
- whether path resolution follows symlinks, rejects `..`, preserves lexical form, canonicalizes eagerly, or keeps human-facing display paths distinct from machine-resolved paths,
- whether recursive traversal respects `.gitignore` / hidden-file rules / filesystem-boundary limits / symlink-following / deterministic ordering,
- whether watching is edge-triggered, event-stream based, polling based, recursive, parent-directory based, or best-effort under rename/remove races,
- whether writes are direct/truncating, staged in a temp file, atomic-replace style, no-clobber style, or durable only after extra sync steps,
- what temp-file cleanup, persistence, cross-filesystem limits, and security assumptions apply,
- how path display, UNC / extended-length Windows paths, case sensitivity, and UTF-8 assumptions are handled,
- and what evidence actually ran: symlink escape vectors, rename/cross-filesystem vectors, atomic replace vectors, watch/walk vectors, or platform-matrix probes.

That gap matters because Rust’s filesystem ecosystem is not one thing.
Std `fs` exposes broad cross-platform operations but also explicitly documents TOCTOU risks, unstable open-directory APIs, mount-point rename limits, and canonicalization behavior that can produce Windows extended-length paths. Capability-first crates such as `cap-std` and `cap-std-ext` deliberately de-emphasize bare global paths. `camino` makes UTF-8 path assumptions explicit. `tempfile`, `atomic-write-file`, walk/watch crates, and error wrappers each solve sharp slices of the problem, but there is no shared artifact family that records which slice a public surface actually chose.

So the missing contribution is not another filesystem helper crate.
It is a **reviewable filesystem-surface layer** for publishing path posture, traversal and watch behavior, staging/durability semantics, and evidence honestly.

Sources:
- https://doc.rust-lang.org/std/fs/
- https://doc.rust-lang.org/std/fs/fn.canonicalize.html
- https://doc.rust-lang.org/std/fs/fn.rename.html
- https://doc.rust-lang.org/nightly/std/fs/struct.Dir.html
- https://docs.rs/cap-std
- https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- https://docs.rs/cap-std-ext
- https://docs.rs/camino
- https://docs.rs/tempfile
- https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- https://docs.rs/atomic-write-file
- https://docs.rs/notify
- https://docs.rs/walkdir
- https://docs.rs/ignore/latest/ignore/struct.WalkBuilder.html
- https://crates.io/crates/fs-err
- https://docs.rs/dunce

## The current seam is awkward
Rust already has several real filesystem subcultures, but their semantics do not line up cleanly:
- std `fs` now explicitly warns about TOCTOU, recommends atomic operations like `File::create_new`, and has an unstable `std::fs::Dir` intended to keep a directory open so descendant operations can avoid some races;
- `canonicalize` resolves symlinks and returns Windows extended-length paths, which is often correct for machine resolution but awkward for CLI/UI/display and for interop with other tools;
- `rename` is not a generic “atomic move everywhere” primitive, because std documents that it will not work across mount points and that overwrite behavior differs by platform and object kind;
- `cap-std` and `cap-std-ext` deliberately shift resolution to open directories / rooted resolution and explicitly avoid absolute-path-first assumptions;
- `camino` makes UTF-8 path assumptions explicit and ergonomic, while std preserves full generality through `Path` / `OsStr`;
- `tempfile` exposes cleanup-on-drop, persist, and no-clobber persistence lanes, but its docs also say persistence cannot cross filesystems and that some persistence operations are not fully atomic or synchronized to disk on all platforms;
- `atomic-write-file` exists because direct truncating writes leave broken intermediate states under interruption;
- `notify`, `walkdir`, and `ignore` already model materially different watch/traversal semantics: platform-native vs polling, symlink-following or not, deterministic sort or not, `.gitignore` / hidden-file behavior or not.

So the ecosystem is not missing *filesystem primitives*.
It is missing the **artifact family that records which path, traversal, watch, staging, and durability semantics a public surface actually chose, and what evidence checked those claims**.

Sources:
- https://doc.rust-lang.org/std/fs/
- https://doc.rust-lang.org/std/fs/fn.canonicalize.html
- https://doc.rust-lang.org/std/fs/fn.rename.html
- https://doc.rust-lang.org/nightly/std/fs/struct.Dir.html
- https://docs.rs/cap-std
- https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- https://docs.rs/cap-std-ext
- https://docs.rs/camino
- https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- https://docs.rs/atomic-write-file
- https://docs.rs/notify
- https://docs.rs/walkdir
- https://docs.rs/ignore/latest/ignore/struct.WalkBuilder.html
- https://crates.io/crates/fs-err
- https://docs.rs/dunce

## Why this matters
This gap matters because filesystem semantics cut across many high-value Rust systems at once:
1. **configuration and local state** — direct truncation, temp staging, and sync posture decide whether crashes corrupt state;
2. **package/build/tooling workflows** — watch, walk, ignore, and canonicalization semantics decide whether tools are fast, deterministic, or race-prone;
3. **security and sandboxing** — authority boundaries are only half the story; symlink traversal and rooted resolution still decide whether code escapes intent;
4. **cross-platform UX** — display paths, UNC handling, UTF-8 assumptions, and rename behavior leak into CLIs, logs, and desktop tools;
5. **editors and developer tools** — filesystem watching and recursive walking are public support boundaries, not just internal implementation details;
6. **durability and recovery** — users care whether “save succeeded” means bytes reached a temp file, reached the final name, or actually survived to disk.

A worthy contribution here is therefore not another path utility or one more virtual filesystem facade.
It is a way to treat **filesystem surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://doc.rust-lang.org/std/fs/
- https://doc.rust-lang.org/std/fs/fn.canonicalize.html
- https://doc.rust-lang.org/std/fs/fn.rename.html
- https://docs.rs/cap-std
- https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- https://docs.rs/atomic-write-file
- https://docs.rs/notify
- https://docs.rs/walkdir
- https://docs.rs/ignore/latest/ignore/struct.WalkBuilder.html

## What “good” looks like
A worthy contribution here is **not** one fake universal filesystem badge.
It is a shared filesystem-surface boundary:
- one `fs-surface/v0` describing the top-level filesystem family and intended use,
- one `path-kind-profile/v0` describing opaque-path vs UTF-8-path vs rooted/capability-relative posture, canonicalization/display policy, and platform/path-format assumptions,
- one `resolution-traversal-profile/v0` describing symlink policy, `..` handling, rooted resolution, case/path-equality assumptions, recursive walk limits, ignore rules, and deterministic ordering posture,
- one `mutation-durability-profile/v0` describing create/truncate/create-new/replace semantics, cross-filesystem limits, sync posture, overwrite/no-clobber semantics, and crash-power-loss expectations,
- one `temp-staging-profile/v0` describing temp naming, cleanup, persistence, rollback, and child-process handoff posture,
- one `walk-watch-profile/v0` describing recursive watch/walk semantics, polling/native lanes, coalescing/race caveats, hidden/ignore handling, and event ordering expectations,
- one `fs-adapter-profile/v0` describing bridges between std `fs`, capability-rooted crates, UTF-8 path wrappers, atomic-write helpers, walk/watch stacks, and error/reporting layers,
- one `fs-vector-set/v0` describing symlink-escape, rename/mount-point, watch-rename/remove, temp-persist, canonicalize/display, and deterministic-traversal vectors,
- one `fs-check-report/v0` recording which vectors actually ran,
- and one `fs-pack/v0` bundle for docs, CI, migration notes, fixtures, and archaeology.

That would let Rust teams reason about filesystem choices with **explicit artifacts** instead of a brittle mix of README advice, path helper functions, and platform bug folklore.

## Non-goals
This gap should not be used to:
- replace std `fs`, `cap-std`, temp-file crates, or watcher crates,
- define one canonical path type or one canonical watch engine,
- collapse authority, path identity, traversal policy, durability semantics, and watch behavior into one fake manifest,
- or pretend that “filesystem support” can be solved by a single abstraction layer.

The job is smaller and sharper:
**make filesystem surfaces legible, honest, and checkable across paths, traversal, staging, mutation, durability, and evidence.**
