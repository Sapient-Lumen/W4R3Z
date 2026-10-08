## Rev0338 lane-map + pilot-program refresh
This epic should now be read together with:
- `design/filesystem-surface-lane-map.md`
- `design/filesystem-surface-pilot-program.md`

The practical shift is small but important: the epic no longer describes one fuzzy filesystem contract. It now assumes a ranked rollout that keeps **bare-path std**, **UTF-8 path**, **rooted/capability**, **canonical-display bridge**, **traversal**, **watch**, **staged mutation**, **durable replace**, and **trust/privacy** lanes distinct.

That means success is not “one crate to unify Rust filesystem work”. Success is a thin `cargo fscheck` / `fs-pack/v0` layer whose lane profiles and imports let downstream tools compare filesystem claims honestly without erasing the differences between path kinds, traversal engines, watch backends, save semantics, or trust checks.


# Epic proposal: Filesystem Surface Kit

## Thesis
One of the more worthy ecosystem contributions in Rust now would be a **portable review layer for filesystem surfaces**.

Rust programs constantly cross boundaries between opaque OS paths, UTF-8 paths, rooted capability-relative paths, canonicalized machine paths, user-facing display paths, staged temp-file saves, recursive traversal, and file watching. But today those semantics are usually published only through function names, crate choice, and scattered bug lore.

Rust does not need one more path helper crate nearly as much as it needs a boring, explicit `fs-pack/v0`.

## Why now
The timing is good:
- std `fs` now explicitly documents TOCTOU hazards and recommends atomic open/create patterns;
- nightly `std::fs::Dir` exists to reduce some race conditions by keeping directories open;
- capability-oriented filesystem APIs such as `cap-std` and `cap-std-ext` already prove that rooted resolution is a real lane, not theory;
- `camino` shows the ecosystem wants UTF-8 path posture to be explicit when that assumption is acceptable;
- `tempfile` and atomic-write crates prove that save/replace semantics are already a first-class problem;
- `notify`, `walkdir`, and `ignore` show that scan/watch semantics are their own public surface, with meaningful differences in symlink, ordering, ignore, and backend behavior;
- `fs-err` and `dunce` exist because even error messages and human-facing path forms are not trivial afterthoughts.

That means the next major filesystem seam is visible before it has converged.
This is exactly when a reviewable contract is more valuable than another helper facade.

Sources:
- https://doc.rust-lang.org/std/fs/
- https://doc.rust-lang.org/std/fs/fn.canonicalize.html
- https://doc.rust-lang.org/std/fs/fn.rename.html
- https://doc.rust-lang.org/nightly/std/fs/struct.Dir.html
- https://docs.rs/cap-std
- https://docs.rs/cap-std-ext
- https://docs.rs/camino
- https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- https://docs.rs/atomic-write-file
- https://docs.rs/notify
- https://docs.rs/walkdir
- https://docs.rs/ignore/latest/ignore/struct.WalkBuilder.html
- https://crates.io/crates/fs-err
- https://docs.rs/dunce

## What should be built
A first credible version should ship:
1. `fs-surface/v0`, `path-kind-profile/v0`, `resolution-traversal-profile/v0`, `mutation-durability-profile/v0`, `temp-staging-profile/v0`, `walk-watch-profile/v0`, `fs-adapter-profile/v0`, `fs-vector-set/v0`, `fs-check-report/v0`, and `fs-pack/v0`
2. one std + temp/staging pilot distinguishing direct overwrite, create-new, and staged replace claims
3. one capability-rooted pilot using `cap-std` / `cap-std-ext`
4. one watch pilot covering native vs polling and rename/remove caveats
5. one traversal pilot covering symlink, ignore, filesystem-boundary, and deterministic-order options
6. one UTF-8-path/display-path pilot covering `camino`, canonicalization, and Windows-path caveats
7. docs and CI that make cross-filesystem, watch-race, cleanup, and durability loss visible

The winning version is compact, semantic, and boundary-aware.
It should make filesystem behavior legible together rather than canonizing one crate family.

## Initial pilots
- **Save lane** — distinguish direct truncation, temp-stage-replace, no-clobber, and durability claims explicitly
- **Rooted-resolution lane** — publish capability-relative / resolve-in-root semantics honestly
- **Traversal lane** — show symlink, ignore, ordering, and boundary policies concretely
- **Watch lane** — show backend, rename/remove caveats, and polling fallback posture
- **Display/migration lane** — record differences between canonical machine paths and human-facing paths

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document path, traversal, mutation, temp, watch, and evidence vocabulary
2. **v0.2 save + traversal pilots**
   - ship one staged-save pilot and one recursive-traversal pilot
   - show where “atomic” and “durable” diverge
3. **v0.3 rooted + watch depth**
   - add capability-rooted and watch-backend evidence
   - capture rename/remove and symlink caveats explicitly
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical filesystem stack

## Success metrics
- Library authors can review path posture, traversal policy, save behavior, and watch semantics without reconstructing them from helper functions and bug reports.
- Applications can distinguish display paths from canonical paths and staged replace from durable save.
- Security reviews can tell rooted capability-relative resolution apart from bare-path best-effort code.
- Tooling stacks can publish whether they sort, ignore, watch, or poll in reproducible ways.
- Migrations between std-path, UTF-8-path, capability-rooted, and watcher/traversal lanes become diffable instead of surprising.

## Archive fit
This proposal fills a real gap in the archive:
- **Runtime Capability Kit** handles filesystem authority as a capability,
- **Command Surface Kit** handles CLI surface semantics,
- **Airgap Kit** and **Build Interop Kit** handle workflow/distribution seams,
- **Runtime Settings Kit** handles config schema/source precedence,
- **Compile Guidance Kit** handles compiler-facing supportiveness.

But none of those is the portable contract for **path posture, rooted resolution, traversal/watch policy, save/replace/durability truth, and attachable filesystem evidence**.
Filesystem Surface Kit is the missing substrate above Rust’s already powerful and already fragmented filesystem ecosystem.
