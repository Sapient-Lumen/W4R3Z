# Design: Filesystem Surface lane map (path-kind lanes, rooted/capability resolution, canonical-display bridges, traversal, watch, staged mutation, durability, and trust checks)

## Goal
Sharpen **Filesystem Surface Kit** so the archive stops treating “filesystem support” as one bucket.
Rust filesystem work already spans materially different lanes, and they differ in **how paths are represented**, **how resolution authority is established**, **how machine-resolved paths relate to human-facing paths**, **how trees are traversed or watched**, **how mutation is staged or committed**, and **what later security or productization consumers may honestly conclude**.

The archive should therefore keep filesystem review grounded in a lane map instead of one flattened “path + watch + save” story.

## Signals from the current ecosystem
- std `fs` now explicitly documents **TOCTOU** hazards, recommends atomic operations such as `File::create_new`, and says keeping files open for the duration of operations helps avoid race windows.
  https://doc.rust-lang.org/std/fs/
- std `fs::canonicalize` still returns canonical absolute paths with symlinks resolved, and on Windows it uses **extended-length path syntax** that may be incompatible with other applications.
  https://doc.rust-lang.org/std/fs/fn.canonicalize.html
- std `fs::rename` still says cross-mount-point renames do not work, which keeps “replace” and “move anywhere” from collapsing into one guarantee.
  https://doc.rust-lang.org/std/fs/fn.rename.html
- nightly `std::fs::Dir` still exists as an experimental open-directory lane aimed at descendant operations with fewer race opportunities.
  https://doc.rust-lang.org/nightly/std/fs/struct.Dir.html
- `cap-std` keeps capability-rooted semantics explicit: `Dir` is an open-directory handle, methods operate relative to it, and `canonicalize` returns a **relative path** because absolute paths do not interoperate well with the capability model.
  https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- `camino` still keeps UTF-8 path posture explicit through `Utf8Path` and `Utf8PathBuf` rather than pretending `std::path::Path` is always string-like.
  https://docs.rs/camino/latest/camino/
- `tempfile` still makes temp persistence caveats explicit: `persist` cannot cross filesystems and is not durable by itself, while `persist_noclobber` is not guaranteed to be atomic on all platforms.
  https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- `atomic-write-file` keeps a different lane explicit: write to a temp file in the same directory, `fsync`, and then replace the destination, while also documenting symlink and metadata-preservation caveats.
  https://docs.rs/atomic-write-file/latest/atomic_write_file/
- `walkdir` and `ignore` keep traversal policy plural through symlink-following, deterministic sorting, same-filesystem boundaries, `.ignore` / `.gitignore` / global ignore support, and precedence rules.
  https://docs.rs/walkdir/latest/walkdir/struct.WalkDir.html
  https://docs.rs/ignore/latest/ignore/struct.WalkBuilder.html
- `notify` keeps native-vs-polling watch posture, backend-specific caveats, editor-save differences, and platform failure modes explicit.
  https://docs.rs/notify/latest/notify/
  https://docs.rs/notify/latest/src/notify/lib.rs.html
- `fs-err`, `dunce`, and `fs-mistrust` prove adjacent filesystem lanes matter too: operation/path-rich errors, Windows path simplification, and trust/privacy checking are all real ecosystem needs rather than implementation trivia.
  https://docs.rs/fs-err/latest/fs_err/
  https://docs.rs/dunce/latest/dunce/
  https://docs.rs/fs-mistrust/latest/fs_mistrust/

## The lanes

### 1) Bare-path std lane (`Path` / `OsStr` / global namespace)
This is the baseline lane for ordinary `std::fs` code working with global filesystem paths.

What defines it:
- opaque OS-native paths
- global namespace resolution from cwd / absolute inputs
- standard metadata/open/rename/remove operations
- TOCTOU exposure unless callers use atomic/open-handle patterns deliberately

Why it deserves its own lane:
- it is still the default ecosystem posture
- it is the lane most wrappers and helpers either build on or try to fence
- it is not equivalent to capability-rooted access, UTF-8 path-only APIs, or trust-checked directories

Design rule:
- keep bare-path std semantics separate from every “safer than std” or “more ergonomic than std” adapter layered above it

### 2) UTF-8 path lane (`camino` and adjacent string-safe APIs)
This is the lane where path values are intentionally restricted to UTF-8 for ergonomics and integration.

What defines it:
- `Utf8Path` / `Utf8PathBuf`
- string-like path access and display
- explicit rejection or conversion of non-UTF-8 paths
- easier interop with Cargo-like tools and config formats that already assume UTF-8

Why it deserves its own lane:
- it solves a different problem than capability scoping or durable mutation
- it is an ecosystem commitment, not merely a display helper
- flattening it into generic `Path` support hides migration and compatibility tradeoffs

Design rule:
- keep UTF-8 path posture separate from canonicalization policy and separate from capability-rooted resolution

### 3) Rooted/capability lane (`cap-std`, checked-dir, open-directory handles)
This is the lane where operations are scoped through an already-open directory or checked root.

What defines it:
- directory handles instead of ambient global path lookup
- relative descendant operations rooted in an authority object
- reduced race surface for descendant operations
- explicit scoping of what the caller is allowed to touch

Why it deserves its own lane:
- rooted capability semantics are not the same as ordinary relative paths from cwd
- this lane is strategically important for security-sensitive tools and sandboxes
- it changes what canonicalization and path publication even mean

Design rule:
- keep rooted/capability semantics separate from bare-path std code and separate from later trust/privacy policy conclusions

### 4) Canonical machine-path vs display-path lane (`canonicalize`, `dunce`, user-facing rendering)
This is the lane where machine-resolved paths and human-facing paths diverge.

What defines it:
- symlink-resolved canonical paths
- Windows extended-length path forms
- simplified/human-compatible rendering for logs, CLIs, or interop
- explicit choice about whether lexical paths are preserved, replaced, or carried alongside canonical ones

Why it deserves its own lane:
- canonical correctness and display compatibility are often different goals
- `dunce` exists precisely because canonical machine paths are not always the right public path form
- flattening this lane into generic “normalize path” logic causes avoidable UX and interop mistakes

Design rule:
- keep machine-resolution truth separate from display/rendering truth and separate from rooted/capability semantics

### 5) Traversal lane (`walkdir`, `ignore`, recursive scans)
This is the lane for recursive tree inspection.

What defines it:
- recursion depth and descriptor usage
- symlink-following policy
- deterministic ordering or deliberate non-ordering
- ignore/hidden/glob policy
- same-filesystem or boundary-crossing posture

Why it deserves its own lane:
- recursive traversal semantics are a public contract for tooling, editors, search, and build systems
- `walkdir` and `ignore` expose materially different defaults and policies
- flattening traversal into generic path access hides major performance and correctness choices

Design rule:
- keep traversal policy separate from single-path mutation semantics and separate from watch semantics

### 6) Watch lane (`notify`, native backends, polling fallback)
This is the lane for change detection over time.

What defines it:
- native watcher or polling backend
- recursive or non-recursive coverage
- event coalescing and ordering posture
- rename/remove/editor-save caveats
- platform-specific fallbacks and failure modes

Why it deserves its own lane:
- watch behavior is not just “traversal plus time”
- native backends and polling are materially different products
- platform and editor caveats are first-class semantics, not footnotes

Design rule:
- keep watch-backend and event-shape truth separate from traversal policy and separate from downstream debounce/UI policy

### 7) Staged mutation lane (temp paths, replace flows, cleanup posture)
This is the lane for “write elsewhere, then publish” workflows.

What defines it:
- temp file naming and location policy
- cleanup-on-drop or explicit keep behavior
- persist / replace / no-clobber semantics
- child-process handoff when only a path is needed

Why it deserves its own lane:
- the temp/staging story is broader than one `persist` call
- cleanup, leftovers, and publish posture matter to real tools
- `tempfile` and adjacent crates already expose this as its own design space

Design rule:
- keep staged mutation separate from durability claims and separate from watch/traversal consumers observing the results

### 8) Durable replace lane (`atomic-write-file` and adjacent crash-aware writers)
This is the lane for “do not leave intermediate garbage behind, and say what durability you actually provided”.

What defines it:
- same-directory temp creation
- sync posture before publication
- replace semantics bounded by mount/device behavior
- explicit metadata-preservation and symlink caveats

Why it deserves its own lane:
- atomic publication and durable persistence are not identical
- `atomic-write-file` documents commit sequencing, cross-device constraints, symlink replacement behavior, and metadata loss explicitly
- flattening this into “safe save” hides what actually survives interruption, crash, or platform quirks

Design rule:
- keep durable-replace semantics separate from temp staging ergonomics and separate from generic file writes

### 9) Trust/privacy check lane (`fs-mistrust` and adjacent policy checkers)
This is the lane where the question is not “can I access it?” but “can I trust the path and its ancestors enough to use it for secrets or private state?”

What defines it:
- path-component-by-component trust checks
- symlink and ancestor ownership scrutiny
- explicit trusted-user/group heuristics
- checked directories that continue enforcing relative access patterns

Why it deserves its own lane:
- privacy/trust review is not solved by canonicalization alone
- `fs-mistrust` explicitly says canonicalizing a final path is not enough when modifiable symlinks or ancestors can redirect meaning
- this lane is strategically different from capability scoping and from durable save semantics

Design rule:
- keep trust/privacy claims separate from plain rooted access and separate from later product-level security claims

## Review rules that follow from the lane map
1. Keep **bare-path std semantics** separate from **rooted/capability semantics**.
2. Keep **UTF-8 path posture** separate from **machine canonicalization**.
3. Keep **machine-resolved canonical paths** separate from **human/display paths**.
4. Keep **traversal policy** separate from **watch/event policy**.
5. Keep **temp staging** separate from **durability guarantees**.
6. Keep **durable replace claims** separate from **plain save ergonomics**.
7. Keep **trust/privacy checking** separate from **mere rooted access**.
8. Keep **portable review artifacts** separate from **tool-native raw logs, watch streams, and fixture traces**.
9. Keep **filesystem-native truth** separate from **downstream product/security/support conclusions**.

## What a worthy contribution should look like
The worthy contribution here is **not**:
- another path helper crate,
- another virtual filesystem abstraction,
- another watcher wrapper,
- or another “atomic write” helper that hides lane differences behind one trait.

It is a thin `cargo fscheck` / `fs-pack/v0` layer that can preserve:
- lane identity,
- path-kind posture,
- rooted/capability authority,
- canonical-vs-display path policy,
- traversal and watch semantics,
- staging and durability posture,
- trust/privacy checks,
- raw fixtures and vector results,
- and bounded downstream handoffs.

That means downstream reviewers can answer:
- *was this plain std path handling, UTF-8 path handling, rooted capability handling, or checked/trusted-dir handling?*
- *did canonicalization change the public path shape, and was a display-safe path carried separately?*
- *did recursive behavior come from `walkdir`, `ignore`, a watcher backend, or a polling fallback?*
- *was mutation direct, staged, atomic-replace style, durable, or merely best-effort?*
- *what changed because watch backends, trust checks, or rooted capability handles got involved?*

## Immediate archive consequences
Read this together with:
- `design/filesystem-surface-kit.md`
- `design/filesystem-surface-pilot-program.md`
- `gaps/filesystem-surfaces-paths-traversal-and-durable-mutation-contracts.md`
- `proposals/epic-filesystem-surface-kit.md`
- `design/runtime-capability-kit.md`
- `design/runtime-settings-kit.md`
- `design/command-surface-kit.md`

The archive should now prefer **lane-aware filesystem packs before one fake filesystem verdict**, and it should keep path-kind, resolution, watch, staging, durability, and trust semantics reviewable instead of narrating them as interchangeable “fs support”.
