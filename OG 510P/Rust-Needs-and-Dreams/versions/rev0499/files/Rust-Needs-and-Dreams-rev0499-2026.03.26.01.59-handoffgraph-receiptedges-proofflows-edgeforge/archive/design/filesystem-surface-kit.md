## Rev0338 filesystem-lane-map refresh
Read this kit together with `design/filesystem-surface-lane-map.md` and `design/filesystem-surface-pilot-program.md`.

This kit should now be interpreted through an explicit lane map:
- **bare-path std lane** for ordinary `Path` / `OsStr` ambient-resolution code,
- **UTF-8 path lane** for `camino`-style string-safe path surfaces,
- **rooted/capability lane** for `cap-std` / checked-dir style descendant operations,
- **canonical-machine vs display-path lane** for `canonicalize` / `dunce` style path-shape bridges,
- **traversal lane** for `walkdir` / `ignore` recursive-scan behavior,
- **watch lane** for `notify` native-vs-polling change detection,
- **staged mutation lane** for `tempfile` / `TempPath` / publish flows,
- **durable replace lane** for `atomic-write-file` style crash-aware publication,
- and **trust/privacy lane** for `fs-mistrust` style path/ancestor scrutiny.

The kit should now resist a common flattening failure: treating path kind, rooted authority, canonical/display path form, traversal policy, watch backend, temp staging, durability guarantees, and trust checks as if they were one interchangeable filesystem abstraction. They are not.


# Design: Filesystem Surface Kit (`cargo fscheck`, `fs-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **filesystem surfaces** in Rust: path posture, resolution and traversal policy, mutation and durability semantics, temp/staging behavior, walk/watch semantics, and the evidence that those claims were actually checked.

This should help answer questions like:
- does this API accept opaque OS paths, UTF-8-only paths, or capability-relative paths,
- does it canonicalize eagerly, preserve user-facing lexical paths, or keep both,
- what symlink, `..`, rooted-resolution, and case/path-equality assumptions apply,
- what save/replace semantics are promised and what crash-durability caveats remain,
- whether recursive walking is deterministic and what ignore rules it respects,
- whether watching is native or polling and what rename/remove caveats apply,
- and what vectors actually ran across platforms.

It should **not** replace filesystem crates, path types, or watchers.
It should make filesystem semantics reviewable and comparable.

## References (signals)
- std `fs` now explicitly documents TOCTOU hazards and recommends atomic operations such as `File::create_new` instead of check-then-create patterns.
  https://doc.rust-lang.org/std/fs/
- Nightly `std::fs::Dir` exists precisely to keep a directory open and avoid some descendant TOCTOU races, but it is still unstable.
  https://doc.rust-lang.org/nightly/std/fs/struct.Dir.html
- `canonicalize` resolves symlinks and returns Windows extended-length paths, which are sometimes correct for machine resolution but awkward for human/display interop.
  https://doc.rust-lang.org/std/fs/fn.canonicalize.html
- `rename` does not work across mount points and has platform-dependent overwrite behavior.
  https://doc.rust-lang.org/std/fs/fn.rename.html
- `read_dir` yields platform/filesystem-dependent ordering and can encounter new errors after iterator construction.
  https://doc.rust-lang.org/std/fs/fn.read_dir.html
- `cap-std` centers `Dir`-relative access and de-emphasizes current-working-directory/global-namespace assumptions.
  https://docs.rs/cap-std
- `cap-std`’s `Dir` docs explicitly say its `canonicalize` returns a relative path because absolute paths do not interoperate well with the capability model.
  https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- `cap-std-ext` adds rooted-resolution helpers such as `RootDir` with `RESOLVE_IN_ROOT` semantics.
  https://docs.rs/cap-std-ext
- `camino` makes UTF-8 path assumptions explicit and ergonomic rather than implicit.
  https://docs.rs/camino
- `tempfile` documents cleanup-on-drop and explicit persistence APIs; `NamedTempFile::persist` and `persist_noclobber` also document cross-filesystem limits and non-uniform atomicity/durability caveats.
  https://docs.rs/tempfile
  https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- `atomic-write-file` exists because direct writes/truncation leave files in broken intermediate states under interruption.
  https://docs.rs/atomic-write-file
- `notify` explicitly supports both platform-native and polling watchers and documents rename/remove caveats.
  https://docs.rs/notify
- `walkdir` and `ignore` expose rich traversal policies around symlinks, ordering, file-descriptor limits, `.gitignore`, hidden files, and filesystem boundaries.
  https://docs.rs/walkdir
  https://docs.rs/ignore/latest/ignore/struct.WalkBuilder.html
- `fs-err` shows that even “just std::fs” usually needs better operation/path reporting in practice.
  https://crates.io/crates/fs-err
- `dunce` exists because std canonical paths on Windows are often not the human-/tool-facing form people actually want.
  https://docs.rs/dunce

## Proposed artifact family

### 1) `fs-surface/v0`
Top-level declaration of a filesystem support boundary.

Fields:
- surface id
- surface family (`config-store`, `workspace-scan`, `editor-watch`, `sandboxed-fs`, `user-content-save`, `cache-store`, `artifact-staging`, `general`)
- primary crates / adapters used
- supported platforms / targets
- intended guarantees (`best-effort`, `reviewable`, `durability-aware`, `sandbox-rooted`, `deterministic-traversal`, `watch-capable`)
- notes / non-goals

### 2) `path-kind-profile/v0`
Describe path-value posture.

Fields:
- path lane (`opaque-os`, `utf8-only`, `capability-relative`, `canonical-absolute`, `display-preserving`, `mixed`)
- path input types (`Path`, `PathBuf`, `Utf8Path`, `Dir` + relative path, etc.)
- canonicalization policy (`never`, `on-open`, `on-compare`, `on-store`, `user-selectable`)
- display/rendering policy (`raw`, `simplified`, `humanized`, `lossy`, `separate-display-path`)
- Windows path posture (UNC/extended-length allowed or hidden)
- case/path equality assumptions
- non-UTF-8 handling posture

### 3) `resolution-traversal-profile/v0`
Describe path resolution and tree-walk semantics.

Fields:
- rooted resolution posture (`cwd-relative`, `absolute-allowed`, `dir-relative`, `resolve-in-root`, `other`)
- `..` / absolute-path handling
- symlink policy (`follow-none`, `follow-root-only`, `follow-all`, `follow-explicit`, `reject`, `mixed`)
- canonicalization-before-open policy
- recursion depth posture
- deterministic ordering posture
- hidden/ignore policy (`none`, `.gitignore`, `.ignore`, global gitignore, custom globs)
- same-filesystem boundary policy
- file-descriptor / resource posture for walking

### 4) `mutation-durability-profile/v0`
Describe mutation, replacement, and durability semantics.

Fields:
- creation posture (`create`, `create_new`, `truncate`, `append`, `open-existing`, `mixed`)
- overwrite/replace policy (`direct-overwrite`, `rename-replace`, `no-clobber`, `temp-stage-then-replace`, `other`)
- cross-filesystem posture
- sync posture (`none`, `file-only`, `file+dir`, `platform-dependent`, `caller-managed`)
- crash/power-loss claims
- overwrite guarantees vs caveats
- lock/coordination assumptions if any

### 5) `temp-staging-profile/v0`
Describe temp-file and staging behavior.

Fields:
- temp naming style (`anonymous`, `named`, `o_tmpfile`, `randomized`, `user-specified`, `mixed`)
- cleanup posture (`drop-cleanup`, `explicit-close`, `disable-cleanup-supported`, `keep-on-failure`, `manual`)
- persistence policy (`replace`, `noclobber`, `keep-in-place`, `publish-link`, `other`)
- cross-filesystem constraints
- child-process handoff posture
- security caveats
- rollback / leftover-artifact behavior

### 6) `walk-watch-profile/v0`
Describe recursive scanning and watch semantics.

Fields:
- scan engine(s)
- watch engine(s)
- native vs polling posture
- recursive behavior
- rename/remove caveats
- event coalescing / ordering posture
- hidden/ignore behavior
- symlink traversal during watch/scan
- filesystem-boundary posture
- unsupported / degraded platforms

### 7) `fs-adapter-profile/v0`
Describe bridge lanes.

Fields:
- from/to crates or artifact lanes
- lossy vs lossless adaptation
- path-encoding changes
- display-path changes
- capability/sandbox assumptions
- durability / temp / watch behavior changes
- manual migration notes

### 8) `fs-vector-set/v0`
Executable or review vectors.

Typical vectors:
- symlink escape / `..` traversal probes
- canonicalize/display parity probes
- cross-filesystem rename/persist probes
- crash-safe replace / temp staging probes
- cleanup / leftover artifact probes
- deterministic walk ordering probes
- ignore-rule / hidden-file precedence probes
- watch rename/remove / polling/native parity probes
- Windows path-format / UTF-8 edge probes

### 9) `fs-check-report/v0`
Results of running declared vectors.

Fields:
- vector ids executed
- environment (OS, filesystem type if known, Rust toolchain, target, watcher backend)
- outcomes (`pass`, `fail`, `unsupported`, `inconclusive`, `skipped`)
- failure classes (`escape`, `path-format`, `cross-fs`, `durability`, `cleanup`, `ordering`, `watch-race`, `other`)
- fixture/log attachments

### 10) `fs-pack/v0`
Bundle format:
- `fs-surface/v0`
- one or more `path-kind-profile/v0`
- one or more `resolution-traversal-profile/v0`
- one or more `mutation-durability-profile/v0`
- zero or more `temp-staging-profile/v0`
- zero or more `walk-watch-profile/v0`
- zero or more `fs-adapter-profile/v0`
- one `fs-vector-set/v0`
- one or more `fs-check-report/v0`
- raw fixtures / watch logs / temp directories / migration notes

## Reference UX: `cargo fscheck`
- `cargo fscheck inspect`
  - discover likely path types, canonicalization, temp/staging helpers, walk/watch crates, and risky patterns
- `cargo fscheck check`
  - run declared vectors and emit `fs-check-report/v0`
- `cargo fscheck diff <A> <B>`
  - compare two packs or versions and explain semantic drift
- `cargo fscheck doctor`
  - explain likely ambiguity points: symlink-following, canonicalize/display mismatch, cross-filesystem writes, watch rename caveats, non-durable saves
- `cargo fscheck pack`
  - bundle an `fs-pack/v0`

`cargo fscheck` should begin as an orchestrator / validator / packer. It should avoid becoming a new VFS, watcher engine, or path crate.

## Default policy
- **Path posture must be explicit.**
- **Human-facing display paths stay distinct from machine-resolved canonical paths when needed.**
- **Traversal policy must say what happens with symlinks, `..`, ignore rules, and filesystem boundaries.**
- **“Atomic save” and “durable save” stay distinct.**
- **Watch support must record backend and rename/remove caveats.**
- **Unsupported and platform-dependent outcomes are valid outcomes.**

## What the kit should provide to others
- **Application authors:** a way to state what kind of paths/config saves/watch behavior they actually support.
- **Library authors:** a way to publish symlink, rooted-resolution, durability, and temp-file assumptions honestly.
- **Tooling authors:** a way to compare walk/watch/canonicalize behavior across editor, build, and CLI stacks.
- **Security reviewers:** a way to tell capability-rooted resolution apart from bare-path best-effort code.
- **Migration work:** a way to compare std-path, UTF-8-path, capability-rooted, and watch/staging lanes without pretending they are interchangeable.

## Overlap boundaries
- **Not Runtime Capability Kit:** that kit owns whether filesystem authority exists and how it is delegated; Filesystem Surface Kit owns the semantics once filesystem APIs are used.
- **Not Command Surface Kit:** that kit owns CLI flags/help/transcripts; this kit owns path/traversal/save/watch semantics behind commands.
- **Not Build Interop / Airgap Kit:** those kits own build/distribution workflows; this kit owns filesystem meaning beneath them.
- **Not Allocation / Initialization / Override Kits:** those kits own memory-resource, construction, or provider-slot behavior, not filesystem semantics.
- **Not Runtime Settings Kit:** that kit owns config-source precedence and schema/documentation; this kit owns how config/state touches the filesystem.

## Hard problems (explicitly scoped)
1. **Durability is deeper than atomic rename**
   - v0 should allow honest `caller-managed` / `platform-dependent` durability claims instead of fake certainty.
2. **Path identity is not one thing**
   - lexical, canonical, rooted-relative, UTF-8, and human-display paths all serve different roles.
3. **Watch behavior is fundamentally backend-shaped**
   - native and polling lanes should be recorded, not flattened.
4. **Traversal policy is security-relevant**
   - symlink, `..`, ignore, and same-filesystem rules need first-class treatment, not README footnotes.
5. **Cross-platform behavior stays messy**
   - Windows extended-length paths, rename differences, and filesystem-specific limits should remain explicit.

## Evaluation plan
Pilot on:
1. one CLI/config crate using temp save + replace,
2. one capability-rooted filesystem lane using `cap-std`,
3. one editor / watcher lane using `notify`,
4. one recursive scan lane using `walkdir` / `ignore`,
5. one UTF-8-path-heavy application using `camino`.

Success bar:
- projects can publish filesystem assumptions without inventing their own schema,
- reviewers can tell path posture, traversal policy, save/durability posture, and watch behavior apart,
- symlink / mount-point / watch-race surprises become visible before production,
- and the ecosystem gets a reusable boundary above today’s fragmented filesystem stack without flattening meaningful differences.
