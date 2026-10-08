## Added 2026-03-19 (267): upgrade substrate exists, but it still does not yield a reviewable downstream lane contract

The upgrade-pack lane should now assume the ecosystem already has meaningful **release and migration substrate**:

- Cargo still documents SemVer compatibility and feature handling, but as one conventional slice of compatibility rather than a whole migration story.
- `cargo-semver-checks` is now mature enough to be part of real release workflows, but its docs still note rustdoc-JSON instability and support-window limits.
- `release-plz update` now integrates `cargo-semver-checks` when installed, while also explicitly warning that it does not catch every SemVer violation.
- `cargo release` clearly automates validation, versioning, tagging, and publishing, but stays producer-side.
- `cargo fix` and `rustfix` provide real source-suggestion substrate, but they do not by themselves prove manifest/config/docs follow-through.
- Cargo external-tools / `cargo metadata --format-version` now make workspace-aware import feasible.
- Cargo workspaces remain common enough that package-scope ambiguity is a practical issue.
- The `hint-mostly-unused` write-up makes feature flags as stable interface unusually explicit, which means feature/default-policy drift belongs inside upgrade hazard modeling.

Those surfaces are enough to justify an upgrade-pack crate above them.
They are **not** enough to say where an upgrade hazard came from, which package/example/binary lanes were actually checked, whether imported release/changelog/docs surfaces are canonical enough to back hazard authority, how disagreements between authorities should be handled, or whether a machine fix covered the whole migration surface on the current lane.

Future passes should therefore treat “more release substrate exists” as evidence that **P-0514 is buildable**, not as evidence that the lane is already solved.
They should also keep source-lineage discipline, conflict-transparent abstention, and current-lane follow-through state explicit instead of treating nearby notes, partial evidence, and prior-lane completions as interchangeable.

## Added 2026-03-19 (266): freeze-boundary substrate exists, but it still does not yield a reviewable starter-set decision

The pathfinder lane should now assume the ecosystem already has meaningful **selection substrate**:

- Cargo gives importable surfaces such as `search`, `add`, `info`, `metadata`, and stable custom-subcommand/external-tool support.
- Cargo manifests already expose lightweight category/keyword/MSRV and related facts.
- crates.io now exposes more review signals such as Security, Trusted Publishing visibility, SLOC, and `pubtime`.
- docs.rs still exposes target/default-target posture and configurable metadata.

Those surfaces are enough to justify a decision-pack crate above them.
They are **not** enough to say whether a starter set may be frozen, what hidden companion crates still block freezing, what lock-in cost the stack buys, or whether teaching and production defaults should intentionally split.

Future passes should therefore treat “more metadata exists” as evidence that **P-0509 is buildable**, not as evidence that the lane is already solved.

## Added 2026-03-19 (264)

### Authority-surface / ambient-authority substrate
- Rust vision doc (crates need more supportive interfaces): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (online docs remain the preferred canonical reference, followed by studying the code): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `ambient-authority` docs (ambient power is an explicit opt-in token): https://docs.rs/ambient-authority/latest/ambient_authority/struct.AmbientAuthority.html
- `cap-std::fs::Dir::open_ambient_dir` docs (not sandboxed; may access any path visible to the host process): https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- `cap_directories::ProjectDirs::from` docs (project-directory discovery itself uses ambient authority): https://docs.rs/cap-directories/latest/cap_directories/struct.ProjectDirs.html
- `cap-tempfile` docs (ambient `tempdir` and capability-oriented `tempdir_in(&Dir)` both exist): https://docs.rs/cap-tempfile/latest/cap_tempfile/
- `getrandom` docs (custom backends belong in the root crate, must be defined only once, and upstream libraries should not define them outside tests/benchmarks): https://docs.rs/getrandom/latest/getrandom/
- Cargo environment variables: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo build scripts (compiled and executed before the package build; inputs arrive via environment variables): https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Rust project goal on sandboxed build scripts: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- `cargo_capsec` docs (static capability map / ambient-authority scanner): https://docs.rs/cargo-capsec/latest/cargo_capsec/

**Conclusion:** the gap is **not** “Rust lacks capability APIs”, **not** “Rust lacks static authority scanning”, and **not** “Rust lacks tempdir/project-dir/entropy substrate”. The missing layer is a **crate-authored contract** for authority origin, fallback order, refusal posture, injection boundaries, and witnessed restricted profiles.

## Added 2026-03-19 (257)

### Example-surface / first-success substrate
- Rust vision doc (crates need more supportive interfaces): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (online docs remain the preferred canonical reference, followed by studying the code): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust API Guidelines documentation chapter (example code is often copied verbatim by users): https://rust-lang.github.io/api-guidelines/documentation.html
- Cargo targets docs (`examples/` are first-class and compiled by `cargo test` by default): https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- rustdoc documentation tests: https://doc.rust-lang.org/rustdoc/documentation-tests.html
- rustdoc scraped examples: https://doc.rust-lang.org/rustdoc/scraped-examples.html
- Cargo unstable docs (`doc-scrape-examples`): https://doc.rust-lang.org/cargo/reference/unstable.html
- docs.rs metadata docs: https://docs.rs/about/metadata
- docs.rs builds docs (sandbox, blocked network, mostly read-only sources): https://docs.rs/about/builds
- `trycmd` docs: https://docs.rs/trycmd/latest/trycmd/
- `term_transcript` docs: https://docs.rs/term-transcript/latest/term_transcript/
- `mdBook` docs: https://docs.rs/crate/mdbook/latest
- `cargo-generate` docs: https://docs.rs/crate/cargo-generate/latest

**Conclusion:** the gap is **not** “Rust lacks examples”, **not** “tutorial/book tools already solve crate onboarding”, and **not** “docs.rs metadata or scraped examples automatically produce a trustworthy quickstart”. The sharper gap is a **joined first-success support artifact** above example, docs, and tutorial substrate.

## Added 2026-03-19 (255)

### Public API readiness / release-review substrate
- 2026 Rust flagship goals (control over public API dependencies and breaking change detection are both explicit supply-chain work): https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- 2025H2 `cargo-semver-checks` goal (Cargo integration path remains real but unfinished): https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- `cargo-public-api` latest docs (list and diff public API; depends on rustdoc JSON): https://docs.rs/crate/cargo-public-api/latest
- `cargo-semver-checks` latest docs (stable/beta support and nightly/rustdoc-JSON instability caveats): https://docs.rs/crate/cargo-semver-checks/latest
- Cargo unstable `public-dependency` docs: https://doc.rust-lang.org/cargo/reference/unstable.html#public-dependency
- `cargo add` docs (`--public` / `--no-public`): https://doc.rust-lang.org/cargo/commands/cargo-add.html
- rustc lint docs (`exported_private_dependencies`): https://doc.rust-lang.org/beta/rustc/lints/listing/warn-by-default.html#exported-private-dependencies
- rustdoc unstable-features docs (JSON output and coverage JSON): https://doc.rust-lang.org/rustdoc/unstable-features.html
- Cargo SemVer chapter: https://doc.rust-lang.org/cargo/reference/semver.html
- RFC 3516 public/private dependencies: https://rust-lang.github.io/rfcs/3516-public-private-dependencies.html
- Cargo changelog (`cargo tree --edges public`, metadata inclusion, `cargo add --public` progress): https://doc.rust-lang.org/cargo/CHANGELOG.html

**Conclusion:** the gap is **not** “Rust lacks semver analyzers”, **not** “public/private dependency work already solves release review”, and **not** “docs coverage alone tells you whether a public release is ready.” The sharper gap is a **joined public-release review artifact** above semver evidence, public-boundary facts, docs readiness, and waiver posture.

## Memory observation substrate (2026-03-17 refresh)

- `leaktracer`: allocator-interception crate with easy setup and per-function allocation accounting.
  - Evidence: https://docs.rs/leaktracer/latest/leaktracer/
  - Implication: low-friction allocation attribution already exists, but it is not a full review artifact or regression workflow.

- `dhat`: heap and ad hoc profiling via a global allocator wrapper and explicit `Profiler` lifetime.
  - Evidence: https://docs.rs/dhat/latest/dhat/
  - Evidence: https://docs.rs/dhat/latest/dhat/struct.Profiler.html
  - Implication: scoped profile capture already exists, but the archive should keep scope-boundary truth explicit because “profile captured” is not the same as “the right phase was captured”.

- `tikv-jemalloc-ctl`: typed API over jemalloc control/introspection, including statistics and heap-dump-adjacent controls.
  - Evidence: https://docs.rs/tikv-jemalloc-ctl/latest/tikv_jemalloc_ctl/
  - Implication: allocator statistics are real substrate, but stats do not automatically imply callsite-level attribution.

- `jemalloc_pprof`: heap profiling data from jemalloc converted to pprof-compatible output.
  - Evidence: https://docs.rs/jemalloc_pprof/latest/jemalloc_pprof/
  - Implication: profile export substrate exists, but the missing product layer is still the bundle that records capture scope, symbolization fidelity, redaction posture, and release-gating policy.

## Added 2026-03-17 (224)

### Crate discovery / selection substrate
- Rust vision doc (crate discoverability and supportive ecosystem surfaces remain part of the product experience): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2024 project-goals notes (spotty ecosystem support and the need to assemble learning workflows): https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
- `cargo search` (textual registry search): https://doc.rust-lang.org/cargo/commands/cargo-search.html
- `cargo add` (dependency insertion for an already chosen crate): https://doc.rust-lang.org/cargo/commands/cargo-add.html
- Cargo manifest `keywords` / `categories`: https://doc.rust-lang.org/cargo/reference/manifest.html
- crates.io search-order discussion: https://github.com/rust-lang/crates.io/discussions/9325
- Rust Platform follow-up discussion: https://internals.rust-lang.org/t/follow-up-the-rust-platform/3782

**Conclusion:** the gap is **not** “Rust lacks registry search”, **not** “keywords/categories do nothing”, and **not** “the only answer is official blessing.” The sharper remaining gap is a **task-first decision artifact** above those surfaces that keeps task fit, role coverage, lock-in, teaching fit, adoption signal, and manual-review boundaries explicit.

## Added 2026-03-18 (238)

### Crate discovery / selection freshness-and-provenance substrate
- Rust vision doc (crate discoverability and supportive ecosystem surfaces remain part of the product experience): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 (debugging remains a major pain point): https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io development update (Security tab, Trusted Publishing, SLOC metrics, `pubtime`, filtered Cargo-only downloads): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious-crate notification update (RustSec remains the canonical alert surface): https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- docs.rs default-target change announcement: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- docs.rs metadata docs: https://docs.rs/about/metadata
- docs.rs builds docs (`docsrs` only on the final crate, local preflight caveat): https://docs.rs/about/builds
- Cargo build-analysis goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Build-dir-layout v2 call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- rustup 1.29.0 announcement: https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/

**Conclusion:** the gap is **not** “Rust has no recommendation signals”, **not** “new security or publishing metadata settles crate choice”, and **not** “a docs.rs surface change is the same as task-fit truth”. The sharper gap is a **provenance-aware, freshness-aware, scope-aware decision artifact** above registry/docs/toolchain/platform signals.

## Added 2026-03-17 (236)

### Crate persistence-surface deepening substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `std::fs::File` docs (`sync_data`, `sync_all`, dropping ignores close errors): https://doc.rust-lang.org/std/fs/struct.File.html
- `std::fs::rename` docs (replace existing destination on same mount point): https://doc.rust-lang.org/std/fs/fn.rename.html
- `tempfile::NamedTempFile::persist` docs (replace path, but neither file contents nor containing directory are synchronized on return): https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- `atomic-write-file` docs (no intermediate state during overwrite): https://docs.rs/atomic-write-file/latest/atomic_write_file/
- Tokio `fs` docs (ordinary blocking file operations behind `spawn_blocking`): https://docs.rs/tokio/latest/tokio/fs/index.html
- `serde-reflection` docs (store format descriptions under version control): https://docs.rs/serde-reflection/latest/serde_reflection/
- Postcard docs (stable wire format): https://docs.rs/postcard/latest/postcard/
- `revision` docs (revision-tolerant serialization / deserialization): https://docs.rs/revision/latest/revision/
- redb database docs (automatic recovery plus integrity-check/repair boundary): https://docs.rs/redb/latest/redb/struct.Database.html

**Conclusion:** the gap is **not** “Rust lacks atomic overwrite helpers”, **not** “async file APIs create a new durability contract”, and **not** “one stable wire surface proves every persisted surface is stable”. The sharper gap is a **crate-authored persistence contract layer** with explicit compatibility authority, atomicity scope, and recovery-witness artifacts above the existing substrate.

## Added 2026-03-17 (217)

### Crate persistence-surface productization substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `std::fs::File` docs (`sync_all`, `sync_data`, dropping ignores close errors): https://doc.rust-lang.org/std/fs/struct.File.html
- `std::fs::rename` docs (replace existing destination on same mount point): https://doc.rust-lang.org/std/fs/fn.rename.html
- `tempfile::NamedTempFile::persist` docs (atomic replace, but neither file contents nor containing directory are synchronized on return): https://docs.rs/tempfile/latest/tempfile/struct.NamedTempFile.html
- `atomic-write-file` docs (atomic overwrite without intermediate state): https://docs.rs/atomic-write-file/latest/atomic_write_file/
- `atomic-write-file` docs (symlink paths are replaced; target left untouched): https://docs.rs/atomic-write-file/latest/atomic_write_file/
- `atomic-write-file` docs (timestamps / ACLs / xattrs / SELinux contexts are not preserved): https://docs.rs/atomic-write-file/latest/atomic_write_file/
- Serde container attributes (`deny_unknown_fields`, enum tagging): https://serde.rs/container-attrs.html
- Serde field attributes (`rename`, `default`, `alias`): https://serde.rs/field-attrs.html
- `serde-reflection` docs (store format descriptions under version control): https://docs.rs/serde-reflection/latest/serde_reflection/
- Postcard docs (stable wire format): https://docs.rs/postcard/latest/postcard/
- redb database docs (automatic recovery plus integrity-check/repair boundary): https://docs.rs/redb/latest/redb/struct.Database.html

**Conclusion:** the gap is **not** “Rust has no atomic replace helpers”, **not** “we just need another serializer or embedded store”, and **not** “migration notes alone explain persisted-state risk”. The sharper gap is a **crate-authored persistence-surface contract layer** with explicit public-vs-cache policy, write-path truth, failure-model coverage, and release-to-release diffs.

## Added 2026-03-17 (216)

### Docs.rs parity / evidence substrate
- docs.rs builds docs (nightly toolchain, `docsrs`/`DOCS_RS`, cross-compilation behavior, sandbox limits, `cargo docs-rs` caveat): https://docs.rs/about/builds
- docs.rs metadata docs (`default-target`, `targets`, `additional-targets`, feature flags, cargo/rustdoc args): https://docs.rs/about/metadata
- docs.rs about page (`/releases/` build summaries and current service version): https://docs.rs/about
- docs.rs rustdoc JSON docs (hosted JSON output, format-version caveat, compression URLs): https://docs.rs/about/rustdoc-json
- docs.rs default-target change announcement (Apple ARM64 and Linux ARM64 default-target drift): https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- docs.rs repository README (local builder reproduction path): https://github.com/rust-lang/docs.rs
- `cargo docs-rs` README (CI-friendly local preflight, but still only an imitation): https://github.com/dtolnay/cargo-docs-rs

**Conclusion:** the gap is **not** “docs.rs lacks metadata knobs”, **not** “`cargo docs-rs` already gives perfect parity”, and **not** “one local green doc build explains hosted failures.” The sharper remaining gap is a **docs.rs-facing receipt / fidelity / hosted-import / drift-cause / issue-bundle layer** above today’s docs.rs, builder, and local-preflight substrate.

## Added 2026-03-17 (214)

### Toolchain/target support-contract substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces; stable use dominates): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rustup 1.29 announcement (new official Solaris hosts, PATH fallback behavior, and environment plurality): https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
- rustup toolchain-file / override docs (`path` toolchains ignore `components`, `targets`, and `profile`): https://rust-lang.github.io/rustup/overrides.html
- rustup profiles docs: https://rust-lang.github.io/rustup/concepts/profiles.html
- rustup components docs: https://rust-lang.github.io/rustup/concepts/components.html
- rustup cross-compilation docs (`rustup target add` installs stdlib, but external linkers/tools are still usually needed): https://rust-lang.github.io/rustup/cross-compilation.html
- Cargo `rust-version` docs (support expectations, workspace-policy complexity, resolver interactions): https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo config docs (config hierarchy, `build.target`, target `linker`/`runner`, and flag scoping): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo resolver docs (`resolver = "3"` / Rust-version-aware fallback): https://doc.rust-lang.org/cargo/reference/resolver.html
- docs.rs metadata docs (`default-target`, `targets`, `additional-targets`): https://docs.rs/about/metadata
- docs.rs builds docs (nightly, cross-compilation behavior, `DOCS_RS`/`docsrs`, sandbox limits): https://docs.rs/about/builds
- docs.rs default-target change announcement: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- RFC 2803 target-tier policy: https://rust-lang.github.io/rfcs/2803-target-tier-policy.html

**Conclusion:** the gap is **not** “Rust lacks toolchain metadata”, **not** “docs.rs parity already tells the whole support story”, and **not** “a Rust target tier or one green build proves project support”. The sharper remaining gap is a **project-authored toolchain/target support contract with support classes, evidence provenance, external-prerequisite honesty, bootstrap hints, and release-to-release drift reports** above today’s rustup / Cargo / docs.rs substrate.

## Added 2026-03-17 (212)

### Crate example-surface productization / adjacent prior art
- `cargo-generate` already helps people get up and running quickly with a new Rust project from templates: https://docs.rs/crate/cargo-generate/latest
- `mdBook` already gives Rust projects a strong tutorial/book publishing path: https://docs.rs/crate/mdbook/latest
- `term-transcript` already offers a static, testable terminal-transcript path that avoids some dynamic-recording churn: https://docs.rs/term-transcript/latest/term_transcript/
- real crates such as `s2-sdk` already show `rustdoc-scrape-examples` in live docs: https://docs.rs/s2-sdk/latest/s2_sdk/

**Conclusion:** the gap is **not** “Rust lacks project templates,” **not** “Rust lacks tutorial publishing,” **not** “nobody uses scraped examples,” and **not** “terminal transcript tooling is missing.” The sharper remaining gap is a **crate-authored official-quickstart / docs-linkage / environment-honesty / normalization / release-diff contract** above those pieces.

## Added 2026-03-17 (211)

### Crate diagnosis-surface / troubleshooting-support substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (debugging remains a visible productivity issue; docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 (debuggers, OSes, visualizers, async debugging, and expression evaluation are still active needs): https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Tokio tracing docs: https://tokio.rs/tokio/topics/tracing
- Tokio Console announcement (runtime warnings and async-state views): https://tokio.rs/blog/2021-12-announcing-tokio-console
- `console-subscriber` docs: https://docs.rs/console-subscriber/latest/console_subscriber/
- `tokio-metrics` docs: https://docs.rs/tokio-metrics/latest/tokio_metrics/
- `miette` docs: https://docs.rs/miette/latest/miette/
- `miette::Diagnostic` docs (codes/help/URLs): https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- `miette::JSONReportHandler` docs: https://docs.rs/miette/latest/miette/struct.JSONReportHandler.html
- `tracing-error` docs: https://docs.rs/tracing-error/latest/tracing_error/
- `tracing-error::TracedError` docs: https://docs.rs/tracing-error/latest/tracing_error/struct.TracedError.html
- `tracing-error::SpanTrace` docs: https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
- `console-subscriber::Builder` docs: https://docs.rs/console-subscriber/latest/console_subscriber/struct.Builder.html
- `tokio-metrics::RuntimeMonitor::intervals` docs: https://docs.rs/tokio-metrics/latest/tokio_metrics/struct.RuntimeMonitor.html

**Conclusion:** the gap is not “Rust has no diagnostics”, not “Tokio Console already solves crate troubleshooting support”, not “rich error renderers already publish a symptom contract”, and not “runtime metrics automatically explain the right first step”. The sharper remaining gap is a **crate-authored symptom / first-inspection / instrumentation-honesty / support-capture contract** above today’s diagnostics substrate.

## Added 2026-03-17 (210)

### Crate example-surface / adoption-quickstart-support substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust API Guidelines documentation chapter (examples are often copied verbatim by users): https://rust-lang.github.io/api-guidelines/documentation.html
- Cargo targets docs (`examples/` targets, default compilation under `cargo test`): https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- RFC 3123 scraped examples: https://rust-lang.github.io/rfcs/3123-rustdoc-scrape-examples.html
- rustdoc scraped examples book page: https://doc.rust-lang.org/rustdoc/scraped-examples.html
- docs.rs metadata docs: https://docs.rs/about/metadata
- docs.rs builds docs: https://docs.rs/about/builds
- `trycmd` docs: https://docs.rs/trycmd/latest/trycmd/
- `trybuild` docs: https://docs.rs/trybuild/latest/trybuild/
- `skeptic` docs: https://docs.rs/skeptic/latest/skeptic/

**Conclusion:** the gap is **not** “Rust has no examples”, **not** “we just need another docs portal”, and **not** “scraped examples already solve it”. The sharper gap is a **crate-authored example-surface / official-quickstart / prerequisite-origin / success-witness / scenario-coverage / docs-linkage layer** above today’s docs, example, and test substrate.

## Added 2026-03-17 (208)

### Crate persistence-surface / durable-bytes-support substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `std::fs::File` docs (`sync_all`, `sync_data`, dropping ignores close errors): https://doc.rust-lang.org/std/fs/struct.File.html
- Serde overview: https://serde.rs/
- Serde container attributes (`deny_unknown_fields`, enum tagging, defaults): https://serde.rs/container-attrs.html
- Serde field attributes (`alias`, `default`, `flatten`, custom adapters): https://serde.rs/field-attrs.html
- `serde-reflection` docs (extract format descriptions; store under version control to catch unintended changes): https://docs.rs/serde-reflection/latest/serde_reflection/
- Postcard docs (documented stable wire format): https://docs.rs/postcard/latest/postcard/
- redb database docs (automatic recovery from crashes / unclean shutdowns): https://docs.rs/redb/latest/redb/struct.Database.html
- `revision` docs (`revisioned`, field history metadata): https://docs.rs/revision/latest/revision/attr.revisioned.html
- Tokio `fs` docs (ordinary file operations use `spawn_blocking`): https://docs.rs/tokio/latest/tokio/fs/

**Conclusion:** the gap is **not** “Rust has no serializers or persistence substrate”, **not** “we just need another embedded store”, and **not** “upgrade notes already explain persisted-state risk”. The sharper gap is a **crate-authored persistence-surface / compatibility-window / durability-boundary / recovery-posture / migration-diff layer** above today’s serializer, format, file, and storage-engine substrate.

## Added 2026-03-17 (206)

### Crate lifecycle-surface substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tokio graceful shutdown guide: https://tokio.rs/tokio/topics/shutdown
- `TaskTracker` docs: https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- `CancellationToken` docs: https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- `JoinHandle` docs: https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
- `AbortHandle` docs: https://docs.rs/tokio/latest/tokio/task/struct.AbortHandle.html
- `spawn_blocking` docs (running blocking tasks cannot be aborted): https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- Tokio `AsyncWrite` docs (`shutdown` is the hook for graceful protocol shutdown): https://docs.rs/tokio/latest/tokio/io/trait.AsyncWrite.html
- `AbortOnDropHandle` docs: https://docs.rs/tokio-util/latest/tokio_util/task/index.html
- Tokio `select!` cancellation-safety docs: https://docs.rs/tokio/latest/tokio/macro.select.html
- Tokio `AsyncWriteExt` docs (`write`, `write_all`, `flush`, `shutdown`): https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html
- `async_shutdown` docs: https://docs.rs/async-shutdown/latest/async_shutdown/
- `tokio-graceful-shutdown` docs: https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/
- `task_scope` docs: https://docs.rs/task_scope/latest/task_scope/
- `moro` docs: https://docs.rs/crate/moro/0.4.0

**Conclusion:** the gap is **not** “Rust has no cancellation/shutdown substrate”, **not** “we just need another runtime helper”, and **not** “structured concurrency alone solves downstream lifecycle clarity”. The sharper gap is a **crate-authored lifecycle-surface / background-work / shutdown-obligation / drain-recipe / diff layer** above today's async primitives, shutdown helpers, and structured-concurrency experiments.

## Added 2026-03-17 (204)

### Crate observability-surface substrate
- Tokio’s tracing topic docs say `tracing` is structured, event-based diagnostics and explicitly name routes into OpenTelemetry export, Tokio Console, logging, and profiling. https://tokio.rs/tokio/topics/tracing
- `tracing` docs list a wide ecosystem of integrations, including subscribers, OpenTelemetry export, framework middleware, and multiple formatter/output layers. https://docs.rs/tracing/latest/tracing/
- `tracing-subscriber` docs show composable `Layer` and `Filter` abstractions, JSON/fmt/env-filter support, and `no_std`-aware layering surface. https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
- `EnvFilter` docs make route activation more explicit: filters may be global or per-layer, and regex field matching should be disabled for potentially untrusted input. https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
- `console-subscriber` docs make Tokio-console activation explicit: Tokio `tracing` support and `tokio_unstable` are required on the Tokio path. https://docs.rs/console-subscriber/latest/console_subscriber/
- `tracing-opentelemetry` docs make the bridge boundary explicit: traces and metrics are supported, but logs are not. https://docs.rs/tracing-opentelemetry/latest/tracing_opentelemetry/
- OpenTelemetry Rust docs still say traces, metrics, and logs are beta in Rust. https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry semantic-conventions and schema docs tie signal meaning to common names and versioned schema URLs. https://opentelemetry.io/docs/concepts/semantic-conventions/ ; https://opentelemetry.io/docs/specs/otel/schemas/
- OpenTelemetry Rust instrumentation-libraries docs say many libraries/frameworks are supported through instrumentation crates, and the docs team still does not know of any Rust library with OpenTelemetry natively integrated by default. https://opentelemetry.io/docs/languages/rust/libraries/
- OpenTelemetry sensitive-data docs say implementers remain responsible for reviewing the telemetry emitted by their instrumentation and libraries. https://opentelemetry.io/docs/security/handling-sensitive-data/

**Conclusion:** the gap is **not** “Rust cannot do telemetry,” **not** “we only need another subscriber/exporter,” and **not** “semantic conventions already tell one crate’s whole support story.” The sharper gap is a **crate-authored observability-surface / activation-recipe / bridge-route / schema-posture / sensitivity-boundary contract** above today’s tracing/OTel substrate.

## Added 2026-03-08 (154)

### Cargo resolver workspace-inheritance substrate
- Cargo workspace docs say `[workspace.dependencies]` features are additive with member dependency features. https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo dependency-spec docs still say inherited dependencies cannot use keys other than `optional` and `features`, giving `default-features` as an example. https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- Cargo issue #14841 says that wording is currently easy to misread because real inherited `default-features` behavior is murkier than the docs suggest. https://github.com/rust-lang/cargo/issues/14841
- Cargo issue #11329 shows member-level `default-features = false` can be neutralized unless the workspace dependency also disables defaults. https://github.com/rust-lang/cargo/issues/11329
- Cargo issue #12162 shows this scales badly in larger workspaces because one member’s wish to disable defaults can force many other members to spell out the opposite. https://github.com/rust-lang/cargo/issues/12162
- Rust release notes document the converse case too: when a workspace dependency disables defaults, a member inherited dependency with `default-features = true` re-enables them. https://doc.rust-lang.org/beta/releases.html
- Cargo issue #11779 shows target-specific inherited dependencies can still be where effective feature/default-feature behavior becomes conservative or manual-review territory. https://github.com/rust-lang/cargo/issues/11779

**Conclusion:** the gap is **not** “Cargo lacks workspace dependency inheritance.” The sharper gap is a **dependency-origin / inherited-policy explanation layer** above today’s docs, manifests, and issue-style investigative surfaces.

## Added 2026-03-08 (153)

### Cargo resolver feature-intent substrate
- Cargo features docs warn that `default-features = false` may still fail to keep defaults off if another dependency path enables them. https://doc.rust-lang.org/cargo/reference/features.html
- The same docs say `--no-default-features` disables defaults for the **selected packages**. https://doc.rust-lang.org/cargo/reference/features.html
- Cargo resolver docs still say dependency features are unified across multiple selected workspace packages. https://doc.rust-lang.org/cargo/reference/resolver.html
- The workspace feature-unification tracking issue is still open and still has unresolved investigative-surface questions. https://github.com/rust-lang/cargo/issues/14774
- Cargo issue #8157 shows `--bin` versus `-p` can still produce different feature outcomes in a workspace. https://github.com/rust-lang/cargo/issues/8157
- Cargo issue #8366 shows `default-features = false` inside a workspace can still surprise users. https://github.com/rust-lang/cargo/issues/8366
- Cargo issue #14021 shows too-few requested features can still be masked by feature unification. https://github.com/rust-lang/cargo/issues/14021
- Cargo issue #16583 shows even current `cargo tree` presentation can blur the requested subject under workspace feature-unification. https://github.com/rust-lang/cargo/issues/16583

**Conclusion:** the gap is **not** “Cargo has no feature controls” and not “raw graph/tree views already tell you who requested what.” The sharper gap is a **feature-intent / negative-intent / subject-scope explanation layer** above today’s resolver and investigative surfaces.

## Added 2026-03-08 (152)

### Cargo resolver unification substrate
- Cargo unstable docs define `resolver.feature-unification` with explicit `selected`, `workspace`, and `package` modes. https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo resolver docs still say dependency features are unified across multiple selected workspace packages. https://doc.rust-lang.org/cargo/reference/resolver.html
- The workspace feature-unification tracking issue is still open and still has unresolved investigative-surface questions. https://github.com/rust-lang/cargo/issues/14774
- Cargo issue #4463 shows feature selection can still depend on the compiled package set. https://github.com/rust-lang/cargo/issues/4463

**Conclusion:** the gap is **not** “Cargo has no resolver policy surface.” The sharper gap is a **unification-policy / participant-scope explanation layer** above today’s resolver and investigative surfaces.

## Added 2026-03-08 (151)

### Cargo resolver lane / platform substrate
- Cargo resolver docs: resolver v2 avoids unifying target-specific dependency features that are not currently being built, and also keeps build-dependencies / proc-macros and dev-dependencies separate in key cases. https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo features docs restate the same lane split rules, which makes them user-facing contract and not just internal trivia. https://doc.rust-lang.org/cargo/reference/features.html
- `cargo tree` docs explicitly say its feature view is only “pretty close” and may merge features for display convenience. https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- `cargo metadata` docs say the resolve includes all targets unless `--filter-platform` is used. https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo unstable docs say `--unit-graph` provides a more complete internal-graph view, including feature relationships between dependency kinds, but remains unstable. https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo issue #11261 shows `cargo tree` can still display unified normal+dev features under resolver v2. https://github.com/rust-lang/cargo/issues/11261
- Cargo issue #14415 shows proc-macro/build-vs-normal feature stories can still require manual review. https://github.com/rust-lang/cargo/issues/14415

**Conclusion:** the gap is **not** “Cargo has no feature or graph surfaces.” The sharper gap is a **lane-partition / platform-coverage / exactness bundle** above those surfaces.


# Known existing tools (to avoid reinventing)

This list is intentionally incomplete; add to it as you discover overlap.

## Offline / mirroring
- Panamax (mirrors rustup + crates.io): https://github.com/panamax-rs/panamax
- offline_crates (crates.io mirror helper): https://github.com/martynp/offline_crates
- crates-mirror (older crates.io caching mirror): https://crates.io/crates/crates-mirror

## Supply chain / auditing
- cargo-vet (audit tracking): https://mozilla.github.io/cargo-vet/
- Google rust-crate-audits (public audits using cargo-vet): https://github.com/google/rust-crate-audits
- cargo-auditable (embed deps into binaries): https://github.com/rust-secure-code/cargo-auditable
- cargo-audit (RustSec vulnerability checks): https://github.com/rustsec/rustsec/tree/main/cargo-audit

## Licenses / compliance
- cargo-deny (license and security policies): https://github.com/EmbarkStudios/cargo-deny
- cargo-about (license listing generation): https://github.com/EmbarkStudios/cargo-about
- cargo-bundle-licenses (bundle third-party licenses): https://github.com/sstadick/cargo-bundle-licenses

## Concurrency testing
- loom (permutation testing for concurrency): https://github.com/tokio-rs/loom
- shuttle (randomized concurrency testing): https://docs.rs/shuttle/latest/shuttle/
- frankenlab (deterministic record/replay harness): https://lib.rs/crates/frankenlab

Last updated: 2026-03-01
## Supply-chain / SBOM / provenance
- cargo-sbom (SPDX + CycloneDX): https://docs.rs/crate/cargo-sbom/latest
- cargo-cyclonedx (CycloneDX plugin): https://crates.io/crates/cargo-cyclonedx
- cyclonedx-rust-cargo (repo): https://github.com/CycloneDX/cyclonedx-rust-cargo
- Pre-RFC Cargo SBOM: https://internals.rust-lang.org/t/pre-rfc-cargo-sbom/19842
- cargo-auditable (embed dep graph into binaries): https://github.com/rust-secure-code/cargo-auditable
- crates.io Trusted Publishing docs: https://crates.io/docs/trusted-publishing
- RFC 3691 Trusted Publishing: https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
- sigstore crates: https://docs.rs/sigstore/latest/sigstore/

## Release engineering / shipping
- cargo-dist (release engineering toolkit): https://axodotdev.github.io/cargo-dist/

## Embedded testing
- embedded-hal-mock (driver mocks): https://github.com/dbrgn/embedded-hal-mock
- defmt-test (on-target test harness): https://crates.io/crates/defmt-test
- awesome-embedded-rust catalog (includes embedded-test): https://github.com/rust-embedded/awesome-embedded-rust

## Auditing / vetting
- cargo-vet (audited dependency policy): https://mozilla.github.io/cargo-vet/
## Privacy-preserving metrics / telemetry
- Internals discussion: metrics without betraying privacy (rustc) — https://internals.rust-lang.org/t/no-telemetry-in-the-rust-compiler-metrics-without-betraying-user-privacy/19275
- OpenDP (differential privacy library, implemented in Rust) — https://github.com/opendp/opendp
- sigstore note: privacy-metrics-kit should avoid “phoning home” by default; use file export or explicit endpoints.

## Data contracts / schema registries
- Rust schema registry client (Confluent) examples — https://yokota.blog/2025/04/16/using-data-contracts-with-the-rust-schema-registry-client/
- schema-registry-validation (JSON Schema/Avro/Protobuf validation engine) — https://lib.rs/crates/schema-registry-validation
- schema-registry-compatibility — https://crates.io/crates/schema-registry-compatibility

## Chaos testing / fault injection
- tower-resilience-chaos — https://docs.rs/tower-resilience-chaos
- fracture (deterministic chaos testing for async Rust) — https://www.reddit.com/r/rust/comments/1p3e8or/fracture_deterministic_chaos_testing_for_async/
- faine (fault injection / failpoints) — https://crates.io/crates/faine

## TUF / signing / trust roots
- `tuf` crate (TUF client library): https://docs.rs/tuf
- `tough` crate (TUF client): https://crates.io/crates/tough
- rust-tuf repo: https://github.com/theupdateframework/rust-tuf
- TUF adoption draft for Rust crates/releases: https://hackmd.io/%40cWcJa4-JQNOtacfKywdqxA/ByrMv8JH0

## GUI text input / accessibility
- winit (window/events foundation): https://github.com/rust-windowing/winit
- winit IME APIs (`set_ime_allowed`, IME positioning, platform notes): https://docs.rs/winit/latest/winit/window/struct.Window.html
- winit `WindowEvent::Ime` docs (Web explicitly unsupported): https://docs.rs/winit/latest/winit/event/enum.WindowEvent.html
- current Windows overlap bug while IME is allowed: https://github.com/rust-windowing/winit/issues/4508
- current Web/WASM IME issue (hidden-input fallback / canvas limitation): https://github.com/rust-windowing/winit/issues/4424
- Parley (rich text layout substrate): https://docs.rs/parley/latest/parley/
- cosmic-text (layout/editing substrate): https://docs.rs/cosmic-text/latest/cosmic_text/
- AccessKit (cross-platform accessibility infra): https://crates.io/crates/accesskit
- AccessKit text position / text selection vocabulary: https://docs.rs/accesskit/latest/accesskit/
- accesskit_winit (winit adapter): https://docs.rs/crate/accesskit_winit/latest
- accesskit_unix (AT-SPI adapter): https://docs.rs/crate/accesskit_unix/latest
- accesskit_windows (UIA adapter): https://docs.rs/crate/accesskit_windows/0.29.0
- accesskit_macos (NSAccessibility adapter): https://docs.rs/accesskit_macos/latest/accesskit_macos/
- kittest (AccessKit-powered framework-agnostic GUI testing): https://docs.rs/kittest/latest/kittest/
- 2025 survey of Rust GUI libraries (field signal on uneven text-input/accessibility polish): https://www.boringcactus.com/2025/04/13/2025-survey-of-rust-gui-libraries.html
- Slint issue: text-input accessibility exposure remains a major design challenge: https://github.com/slint-ui/slint/issues/2895
- egui IME discussion (illustrative upstream dependency): https://github.com/emilk/egui/issues/248

**Conclusion:** the gap is **not** “Rust lacks text or layout substrate” and **not** “IME APIs existing means text input is solved.” The sharper gap is a **shared transaction/selection engine plus backend-capability and replay bundle layer** above current layout/editing/accessibility substrate.

## Lakehouse / open table formats
- Iceberg (official Rust implementation): https://crates.io/crates/iceberg
- delta-rs / deltalake (Delta Lake in Rust): https://delta-io.github.io/delta-rs/
- Hudi-rs / hudi crate: https://hudi.apache.org/docs/0.15.0/python-rust-quick-start-guide/
- delta-kernel-rs (interoperability-focused Delta implementation): https://github.com/delta-io/delta-kernel-rs

## Audio ecosystem
- RustAudio ecosystem overview: https://github.com/RustAudio/audio-ecosystem
- vst-rs (deprecated VST2 bindings; maintenance lesson): https://github.com/RustAudio/vst-rs

## Local-first / CRDT
- Loro (CRDT library; Rust + JS via WASM + Swift): https://loro.dev/blog/v1.0
- crdt-kit (newer CRDT crate; check scope before proposing overlap): https://crates.io/crates/crdt-kit


## Sandboxing / isolation
- landlock (Linux Landlock bindings): https://docs.rs/landlock
- extrasafe (seccomp + Landlock ergonomics): https://crates.io/crates/extrasafe
- nanosandbox (cross-platform sandbox primitive): https://crates.io/crates/nanosandbox

## Build-time sandboxing
- cargo-sandbox (sandbox Cargo builds; incomplete): https://github.com/madsmtm/cargo-sandbox
- cargo-task-wasm (sandboxed xtask-style tasks via Wasm Components): https://github.com/yoshuawuyts/cargo-task-wasm

## WASI / Component Model
- WASI 0.2 launch announcement (Preview 2): https://bytecodealliance.org/articles/WASI-0.2
- WASI interface catalog (0.2 + Component Model): https://wasi.dev/interfaces
- Component Model docs: https://component-model.bytecodealliance.org/
- wit-bindgen (bindings generator): https://github.com/bytecodealliance/wit-bindgen
- sample-wasi-http-rust (spec-compliant example): https://github.com/bytecodealliance/sample-wasi-http-rust
- wit-component (component tooling crate): https://crates.io/crates/wit-component

## Formal verification / model checking
- Kani (model checker): https://github.com/model-checking/kani
- Creusot (deductive verification): https://github.com/creusot-rs/creusot

## ML inference
- tract (pure Rust inference, ONNX/NNEF): https://github.com/sonos/tract
- ort (ONNX Runtime wrapper + alternative backends): https://crates.io/crates/ort
## Cargo update / version policies / minimal versions
- cargo-edit (cargo upgrade, set-version): https://crates.io/crates/cargo-edit
- cargo-minimal-versions (wraps -Z minimal-versions / direct-minimal-versions): https://crates.io/crates/cargo-minimal-versions
- Internals discussion on minimal-versions + upgrade: https://internals.rust-lang.org/t/zminimal-versions-cargo-update-and-cargo-upgrade/21335
- Registry index publish time proposal (“pubtime” enabler): https://github.com/rust-lang/cargo/issues/15491
- cargo-override (patch table helper; highlighted by Cargo team): https://github.com/eopb/cargo-override

## Secrets / secure storage / secret managers
- keyring (OS credential stores): https://docs.rs/keyring
- secrecy (redacted secret types): https://docs.rs/secrecy/latest/secrecy/
- SecureStore format + crate: https://github.com/neosmart/securestore-rs
- vaultrs (async Vault client): https://crates.io/crates/vaultrs
- vault-client-rs (dual async + blocking Vault client): https://github.com/michaelklishin/vault-client-rs

## Reproducible builds / packaging
- Cargo issue: reproducible `.crate` archives: https://github.com/rust-lang/cargo/issues/8612
- repro-env (build environment helper): https://github.com/kpcyrd/repro-env
- Reproducible builds discussion for rustc: https://internals.rust-lang.org/t/reproducible-builds-for-rustc-gsoc-25-idea/22532

## Internationalization / localization
- cargo-i18n: https://crates.io/crates/cargo-i18n
- rust-i18n: https://crates.io/crates/rust-i18n
- fluent-rs: https://github.com/projectfluent/fluent-rs
- ICU4X: https://github.com/unicode-org/icu4x

## Cross-compilation / linker lanes
- cargo-zigbuild (Zig-backed linker lane): https://github.com/rust-cross/cargo-zigbuild
- cargo-xwin (Windows MSVC cross lane): https://github.com/rust-cross/cargo-xwin
- xwin (Windows CRT/SDK packaging): https://docs.rs/xwin/latest/xwin/
- cross (containerized cross-compilation/testing lanes): https://github.com/cross-rs/cross

## Host / target config scope substrate
- Cargo configuration docs: `build.rustflags`, `build.rustdocflags`, target-specific flags, and host-vs-target behavior. https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable docs: `target-applies-to-host` and `[host]`. https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog: recent updates for `-Ztarget-applies-to-host`. https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo internal target-info docs: host artifact rules are counterintuitive and also apply to rustdoc. https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/build_context/target_info/fn.extra_args.html
- Cargo issue: `RUSTFLAGS` changes build-script behavior when `--target` is added. https://github.com/rust-lang/cargo/issues/14046
- docs.rs issue: rustdoc cfgs and build-script cfgs can diverge. https://github.com/rust-lang/docs.rs/issues/1580

**Conclusion:** the gap is **not** “Cargo has no config knobs” and not “host/target scope is unknowable.” The sharper gap is a **contract / receipt / diagnosis layer** for what config applied to host artifacts, target artifacts, and rustdoc, and why that changed.

## Proc-macro sandboxing / Wasm
- Compiler-team issue: WebAssembly for procedural macros: https://github.com/rust-lang/compiler-team/issues/876
- Pre-RFC: Wasm compilation of proc macros: https://internals.rust-lang.org/t/pre-rfc-sandboxed-deterministic-reproducible-efficient-wasm-compilation-of-proc-macros/19359
## Reproducibility
- cargo-reproduce (reproducible Rust builds verifier/normalizer): https://lib.rs/crates/cargo-reproduce
- Reproducible crate builds tracking (Cargo): https://github.com/rust-lang/cargo/issues/8612
- Reproducible builds project (background): https://reproducible-builds.org/


## eBPF
- Aya (pure Rust eBPF library): https://github.com/aya-rs/aya
- awesome-aya (curated ecosystem list): https://github.com/aya-rs/awesome-aya
- libbpf-rs (Rust wrapper over libbpf + cargo plugin): https://github.com/libbpf/libbpf-rs
- eBPF Foundation projects list (landscape): https://ebpf.foundation/projects/


## Cargo / IDE integration
- Cargo issue: Provide Cargo messages as JSON messages: https://github.com/rust-lang/cargo/issues/8283
- Cargo issue: proc macros can break message-format=json: https://github.com/rust-lang/cargo/issues/8179
- rustc JSON output docs: https://doc.rust-lang.org/beta/rustc/json.html

## Binary installs / distribution
- cargo-binstall (install Rust binaries from release artifacts): https://github.com/cargo-bins/cargo-binstall
- cargo-dist (CI-powered release/distribution for Rust projects): https://axodotdev.github.io/cargo-dist/

## Sandboxing prototypes
- cargo-sandbox (sandbox build scripts/proc macros; macOS-first prototype): https://github.com/madsmtm/cargo-sandbox

## Reproducibility tooling
- cargo-reproduce (rebuild & compare crates/binaries for reproducibility): https://crates.io/crates/cargo-reproduce

## Added 2026-03-01 (tooling substrates)
- cargo-run-bin — workspace-scoped tool runner with caching: https://crates.io/crates/cargo-run-bin
- cargo doc portal / open dependency docs issue: https://github.com/rust-lang/cargo/issues/3805
- rustdoc JSON RFC: https://rust-lang.github.io/rfcs/2963-rustdoc-json.html
- nextest run recordings (design): https://nexte.st/docs/design/architecture/recording-runs/
- CEL (Common Expression Language) crate: https://crates.io/crates/cel
- OPA Rego -> Wasm docs: https://openpolicyagent.org/docs/wasm
- ipc-channel: https://github.com/servo/ipc-channel


## Native deps / sys crates / build tooling
- system-deps (declarative pkg-config deps): https://crates.io/crates/system-deps
- system-deps discussion on becoming a standard: https://github.com/gdesmott/system-deps/issues/97
- vcpkg crate (vcpkg integration): https://docs.rs/vcpkg
- pkg-config crate (build helper): https://crates.io/crates/pkg-config
- cargo vcpkg (tooling referenced by vcpkg docs): https://docs.rs/vcpkg

## OpenAPI / API codegen
- progenitor (OpenAPI 3 client generator): https://github.com/oxidecomputer/progenitor
- paperclip (OpenAPI codegen): https://paperclip-rs.github.io/paperclip/
- utoipa (OpenAPI docs generation): https://docs.rs/utoipa

## Robotics (ROS 2)
- ros2_rust / rclrs (ROS 2 bindings): https://github.com/ros2-rust/ros2_rust
## Durable execution / workflows
- durable (durable execution engine): https://github.com/iopsystems/durable
- duroxide (durable execution framework): https://docs.rs/duroxide
- Flawless (durable execution engine): https://flawless.dev/

## Passkeys / WebAuthn
- webauthn-rs (server WebAuthn): https://crates.io/crates/webauthn-rs
- passkey (passkey-rs by 1Password): https://crates.io/crates/passkey
- passkey-server (storage-agnostic server pieces): https://lib.rs/crates/passkey-server
- soft-fido2 (software CTAP stack; authenticator+client): https://github.com/pando85/soft-fido2

## Bluetooth LE (host)
- btleplug (cross-platform BLE): https://github.com/deviceplug/btleplug
- bluest (cross-platform BLE): https://github.com/alexmoon/bluest

## HTTP record/replay (VCR)
- rvcr (reqwest middleware): https://crates.io/crates/rvcr
- surf-vcr (Surf client): https://docs.rs/surf-vcr
- http-client-vcr (http-client): https://crates.io/crates/http-client-vcr
## Game networking / rollback / determinism
- bevy_ggrs (Bevy plugin for GGRS): https://crates.io/crates/bevy_ggrs
- GGRS (rollback netcode in safe Rust): https://crates.io/crates/ggrs
- fortress-rollback (fork of GGRS): https://crates.io/crates/fortress-rollback
- backroll (GGPO-style rollback): https://github.com/HouraiTeahouse/backroll-rs
- lightyear (deterministic replication + prediction/rollback patterns): https://github.com/cBournhonesque/lightyear

## Kubernetes controllers / testing
- kube-rs controller docs (testing patterns): https://kube.rs/controllers/testing/
- controller-rs (reference controller): https://github.com/kube-rs/controller-rs

## Markdown rendering / sanitization
- pulldown-cmark (CommonMark parser): https://crates.io/crates/pulldown-cmark
- ammonia (HTML sanitizer): https://crates.io/crates/ammonia
- syntect (syntax highlighting): https://crates.io/crates/syntect

## Email transport security & auth
- mail-auth (DKIM/ARC/SPF/DMARC): https://github.com/stalwartlabs/mail-auth
- email-auth (SPF/DKIM/DMARC/ARC/BIMI): https://docs.rs/email-auth

## OpenPGP / S/MIME building blocks
- sequoia-openpgp (OpenPGP implementation): https://crates.io/crates/sequoia-openpgp
- cms (Cryptographic Message Syntax primitives): https://crates.io/crates/cms
- tlsrpt-rs (parse SMTP TLS reports / RFC8460): https://github.com/kravietz/tlsrpt-rs
- mhost (probe many email DNS records incl. DMARC/MTA-STS/TLS-RPT): https://crates.io/crates/mhost

## Identity (SAML)
- samael (SAML2 crate): https://crates.io/crates/samael
- saml-rs (strict policy SAML crate): https://github.com/terminaloutcomes/saml-rs

## MCP (Model Context Protocol)
- Official Rust MCP SDK (rmcp): https://github.com/modelcontextprotocol/rust-sdk
- Official MCP SDK listing / tiers: https://modelcontextprotocol.io/docs/sdk
- MCP docs (build server): https://modelcontextprotocol.io/docs/develop/build-server
- MCP authorization spec: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- MCP security best practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- MCP transport security guidance: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
- MCP reference servers (explicitly educational / not production-ready): https://github.com/modelcontextprotocol/servers
- MCP interceptor extension repo (experimental, not normative): https://github.com/modelcontextprotocol/experimental-ext-interceptors

## PDF / document parsing
- lopdf (PDF manipulation): https://crates.io/crates/lopdf
- pdf-rs (PDF parsing): https://crates.io/crates/pdf-rs
- pdfium (bindings to PDFium): https://crates.io/crates/pdfium
- rust-fuzz trophy-case (fuzzing bug showcase): https://github.com/rust-fuzz/trophy-case

## 2026-03-05 additions (spot-check)

### Accessibility
- `atspi` (Pure Rust AT-SPI2 protocol impl) — https://crates.io/crates/atspi
- `uiautomation` (Windows UI Automation wrapper) — https://crates.io/crates/uiautomation

### Audio plugins
- CLAP spec repo — https://github.com/free-audio/clap
- `clack` (Rust wrappers for CLAP plugin/host) — https://github.com/prokopyl/clack
- `clap-clap` (CLAP plugin scaffolding) — https://crates.io/crates/clap-clap
- `vst3` (Rust bindings for VST3) — https://crates.io/crates/vst3

## Supply chain / OCI / Wasm components (notes)
- `sigstore` (sigstore-rs) — Sigstore client capabilities for Rust; heavily focused on verification in some modules (experimental). https://docs.rs/sigstore/latest/sigstore/ and https://github.com/sigstore/sigstore-rs
- `sigstore-verification` — ecosystem crate focused on verifying signatures/attestations (watch overlap when proposing verification-first designs). https://crates.io/crates/sigstore-verification
- `in_toto_attestation` — protobuf-generated bindings for in-toto attestations (good substrate; missing ergonomic builders/policy). https://crates.io/crates/in_toto_attestation and https://github.com/in-toto/attestation
- `oci-spec` — OCI spec types in Rust (useful; missing deterministic IO + diffs + evidence workflows). https://docs.rs/oci-spec
- `ocipkg` — OCI image layout utilities/docs (overlap with layout read logic). https://termoshtt.github.io/ocipkg/ocipkg/index.html
- `cargo-component` — Bytecode Alliance tooling for building components in Rust (experimental; ecosystem still missing a stable bundle/harness layer). https://github.com/bytecodealliance/cargo-component
- Rust component-model docs — current Rust guidance now says `cargo-component` is being deprecated as native tooling can be used directly. https://component-model.bytecodealliance.org/language-support/rust.html
- WAC / component composition docs — composition tooling is still early and interface-version inference/injection can be inconsistent. https://component-model.bytecodealliance.org/composing-and-distributing/composing.html
- Wasmtime component run docs — `wasmtime run --invoke` makes exported-function exercise a real review surface. https://component-model.bytecodealliance.org/running-components/wasmtime.html and https://bytecodealliance.org/articles/invoking-component-functions-in-wasmtime-cli
- `wasm32-wasip3` target docs — component-producing future-facing target, but still explicitly transitional. https://doc.rust-lang.org/rustc/platform-support/wasm32-wasip3.html
- **Conclusion:** the gap is **not** “Rust cannot build Wasm components” and **not** “we only need another builder wrapper”. The sharper gap is a **component contract / bundle layer** that keeps tooling lineage, world-version locks, composition closure, and exercise posture separately reviewable.

## Routing security / RPKI
- Routinator (RPKI validator / RTR server; Rust): https://github.com/NLnetLabs/routinator
- NLnet Labs Routinator project page: https://nlnetlabs.nl/projects/routing/routinator/

## Smart home / Matter
- rs-matter (pure-Rust Matter stack): https://github.com/project-chip/rs-matter
- connectedhomeip (Matter reference implementation): https://github.com/project-chip/connectedhomeip

## Observability / OpenTelemetry
- opentelemetry-rust (SDK + ecosystem): https://github.com/open-telemetry/opentelemetry-rust
- opentelemetry-semantic-conventions (constants crate): https://crates.io/crates/opentelemetry-semantic-conventions

## Observability / Metrics exposition
- OpenMetrics spec (Prometheus): https://prometheus.io/docs/specs/om/open_metrics_spec/ and https://github.com/prometheus/OpenMetrics
- `openmetrics-parser` (Rust parser for OpenMetrics + Prometheus text exposition): https://crates.io/crates/openmetrics-parser

## USB video/audio classes
- USB-IF UVC v1.5 document set (normative ref for many devices): https://www.usb.org/document-library/video-class-v15-document-set

## Industrial protocols: OPC UA (spot-check)
- `opcua` (pure Rust OPC UA stack): https://docs.rs/crate/opcua/latest
- `async-opcua` (Rust OPC UA server/client): https://github.com/FreeOpcUa/async-opcua
- `open62541` (safe bindings to the open62541 C implementation): https://crates.io/crates/open62541 and https://docs.rs/open62541
- Discussion of Rust OPC UA options (2025): https://www.basyskom.de/en/opc-ua-and-rust-in-2025/

## Healthcare imaging: DICOM/DICOMweb (spot-check)
- `dicom` umbrella crate (DICOM-rs ecosystem): https://crates.io/crates/dicom
- dicom-rs project: https://github.com/Enet4/dicom-rs
- `dicom-test-files` (download-on-demand fixture corpus): https://crates.io/crates/dicom-test-files
- DICOMweb overview + links to PS3.18: https://www.dicomstandard.org/using/dicomweb and https://dicom.nema.org/medical/dicom/current/output/html/part18.html

## Robotics/realtime middleware: DDS/RTPS (spot-check)
- cyclonedds-rs (safe-ish bindings for CycloneDDS): https://github.com/sjames/cyclonedds-rs
- CycloneDDS issue re: official Rust support/maintenance: https://github.com/eclipse-cyclonedds/cyclonedds/issues/2183
- OMG DDSI-RTPS spec landing pages/PDF: https://www.omg.org/spec/DDSI-RTPS/2.2/About-DDSI-RTPS and https://www.omg.org/spec/DDSI-RTPS/2.1/PDF

## QUIC / HTTP/3 stacks (spot-check)
- `quinn` (pure-Rust QUIC transport): https://crates.io/crates/quinn
- `quiche` (QUIC + HTTP/3, widely used): https://crates.io/crates/quiche
- `s2n-quic` (Amazon QUIC stack): https://crates.io/crates/s2n-quic
- `h3` + `h3-quinn` (HTTP/3 crates and Quinn integration): https://crates.io/crates/h3 and https://crates.io/crates/h3-quinn
- qlog specs (structured QUIC/HTTP3 logging): https://datatracker.ietf.org/doc/draft-ietf-quic-qlog-main-schema/ and https://quicwg.org/qlog/draft-ietf-quic-qlog-h3-events.html

## eBPF frameworks / tooling (spot-check)
- `aya` (pure-Rust eBPF framework): https://crates.io/crates/aya
- Aya ecosystem list: https://github.com/aya-rs/awesome-aya
- libbpf overview/docs (CO-RE support): https://libbpf.readthedocs.io/en/latest/libbpf_overview.html
- Kernel verifier docs (normative behavior reference): https://docs.kernel.org/bpf/verifier.html
- bpftool (reference inspection/management utility): https://bpftool.dev/

## MLS (Messaging Layer Security) implementations (spot-check)
- RFC 9420 (MLS protocol): https://datatracker.ietf.org/doc/rfc9420/
- `openmls` (Rust MLS implementation): https://crates.io/crates/openmls
- `mls-spec` (MLS wire-format data structures): https://lib.rs/crates/mls-spec

## Notes added 2026-03-05

- SPDX-related Rust crates exist (e.g., license expression parsing, SPDX doc models), but SPDX 3.x introduces a broader data model and multiple serializations; the “interop + canonical diff + evidence bundle” layer remains thin.
  Source: https://www.omg.org/spec/SPDX/3.0/About-SPDX
  Source: https://spdx.dev/wp-content/uploads/sites/31/2024/12/SPDX-3.0.1-1.pdf

- CycloneDX Rust parsing exists and is referenced in ecosystem discussions, but canonicalization/diff/evidence workflows are not standardized.
  Source: https://ferrous-systems.com/blog/stackable-client/
  Source: https://github.com/CycloneDX/specification

- VC/SSI libraries exist in Rust (types, DID/claim signing), but profile-first validation + conformance corpora + privacy-safe repro artifacts are usually missing.
  Source: https://docs.rs/identity_credential
  Source: https://github.com/spruceid/ssi

- RISC-V architectural testing tooling exists (arch-test + RISCOF), but a Rust-native adapter/diff/bundle layer could make regressions CI-friendly and results shareable.
  Source: https://github.com/riscv/riscv-arch-test
  Source: https://riscof.readthedocs.io/en/latest/intro.html


## Added 2026-03-05
- PKCS#11 wrappers: `cryptoki`, `pkcs11` (bindings/idiomatic APIs; not a conformance/evidence harness).
- WebRTC stack: `webrtc` / webrtc-rs (protocol implementation; not an interop evidence harness).

## Added 2026-03-05 (OpenAPI/JSON Schema, FMI, GeoPackage spot-check)
- OpenAPI models: `openapiv3` (3.0.x), `openapiv3_1` / `oas3` (3.1.x bindings). Still missing: a canonical end-to-end pipeline (normalize→refs→bundle→lint→diff→evidence).
  Source: https://crates.io/crates/openapiv3
  Source: https://crates.io/crates/openapiv3_1
  Source: https://docs.rs/oas3
- JSON Schema validation: `jsonschema` (validator + meta-schema validation). Still missing: OpenAPI-centric dialect/ref policies + semantic diffing and repro bundles.
  Source: https://crates.io/crates/jsonschema
- FMI/FMUs: `fmi` (consume FMUs) + `fmi-xtask` (build FMUs). Still missing: a cross-tool interop harness with canonical traces + evidence bundles.
  Source: https://crates.io/crates/fmi
  Source: https://docs.rs/fmi-xtask
- GeoPackage: `gpkg` exists but appears stale relative to newer GeoPackage versions; Rust has broader geospatial libs (e.g., GeoRust) but not a modern gpkg conformance/canonicalization layer.
  Source: https://crates.io/crates/gpkg
  Source: https://github.com/georust/geozero

## Added 2026-03-05 (Zarr, IEC 61850, FHIR/SMART spot-check)

- Zarr ecosystems exist in other languages, and OGC has endorsed a Zarr community standard (v2). Rust has scattered efforts, but there is no widely adopted, spec-led Zarr v3 core + canonicalization + evidence-bundle toolchain.
  Source: https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html
  Source: https://www.ogc.org/standards/zarr-storage-specification/

- IEC 61850 testing/diagnostics is dominated by vendor tools (GOOSE/Sampled Values monitoring/testing). Rust has general pcap/network crates but lacks an interop-first “pcap → canonical IR → diff → bundle” kit for reproducible troubleshooting.
  Source: https://www.megger.com/en-us/type/relay/iec61850-solutions
  Source: https://www.omicronenergy.com/en/products/svscout/

- FHIR/SMART: multiple server products implement FHIR REST and SMART OAuth patterns, but Rust tooling is typically low-level (HTTP/OAuth) or partial (FHIR models) without a reusable conformance pack + transcript canonicalization + PHI-safe evidence bundle layer.
  Source: https://www.hl7.org/fhir/http.html
  Source: https://build.fhir.org/ig/HL7/smart-app-launch/

- OCPP (EV charging): OCA publishes OCPP specs/downloads and certification test procedures; Rust has protocol/model crates (e.g., rust-ocpp, ocpp_rs) but lacks a default *evidence bundle* kit for capture/replay/diff and safe sharing of failures.
  Source: https://openchargealliance.org/my-oca/ocpp/
  Source: https://openchargealliance.org/wp-content/uploads/2025/09/02.-Test-Procedure-Test-Plans_OCPP2.0.1_v31_final.pdf
  Source: https://crates.io/crates/rust-ocpp
  Source: https://crates.io/crates/ocpp_rs

- OpenXR CTS: Khronos maintains an open-source CTS and publishes usage docs/releases; Rust has bindings (openxr/openxrs) and examples, but lacks a “CTS triage” layer that canonicalizes results + environment provenance into portable artifacts.
  Source: https://registry.khronos.org/OpenXR/conformance/cts_usage.html
  Source: https://github.com/KhronosGroup/OpenXR-CTS
  Source: https://github.com/KhronosGroup/OpenXR-CTS/releases
  Source: https://github.com/Ralith/openxrs

- Nostr: protocol is specified through NIPs (NIP-01 base flow); Rust implementations exist for clients/relays, but interop/compliance harnesses and pinned-NIP evidence bundles are fragmented.
  Source: https://nips.nostr.com/1
  Source: https://github.com/nostr-protocol/nips
  Source: https://crates.io/crates/nostr
  Source: https://crates.io/crates/nostr-relay

## Added 2026-03-05 (pointers)
- SIP/RTP building blocks exist in various crates, but the gap targeted by **P-0233** is the *canonical transcript + diff + redactable evidence bundle* layer.
- LoRaWAN stacks exist (embedded and server-side), but **P-0234** targets *cross-stack trace normalization + scenario harness*.
- Matrix has mature SDKs and some test tooling; **P-0235** focuses on *federation-layer repro bundles and DAG semantic diffs*.

## Added 2026-03-05 (evidence refresh)

### Deterministic testing / record-replay
- FrankenLab (deterministic async harness): https://docs.rs/crate/frankenlab/
- Sturgeon (record/replay async streams w/ timing): https://github.com/synoet/sturgeon

### Sandboxing
- `sandbox-rs` (library + CLI for lightweight Linux sandboxes): https://crates.io/crates/sandbox-rs
- `syd` (Linux sandbox kernel / Firejail-like): https://crates.io/crates/syd
- `seccomp` / `seccompiler` (building blocks): https://crates.io/crates/seccomp , https://crates.io/crates/seccompiler

### Formal methods connectors
- `tla-checker` (Rust TLA+ model checker): https://crates.io/crates/tla-checker
- `tla-connect` (integrate TLA+/Apalache into Rust tests): https://lib.rs/crates/tla-connect
- tree-sitter TLA+ grammar (Rust crate): https://github.com/tlaplus-community/tree-sitter-tlaplus

## Reproducible builds and diff tooling (inputs for P-0242)
- Reproducible Builds “Tools” index (diff engines, nondeterminism detectors): https://reproducible-builds.org/tools/
- diffoscope (deep diff for archives/binaries/directories): https://diffoscope.org/
- `.buildinfo` concept notes (minimal recipe framing): https://reproducible-builds.org/events/berlin2016/buildinfofiles/

## Evidence bundle substrate and attestation lanes (inputs for P-0256)
- in-toto specs index: https://in-toto.io/docs/specs/
- in-toto envelope spec: https://github.com/in-toto/attestation/blob/main/spec/v1/envelope.md
- Sigstore bundle format: https://docs.sigstore.dev/about/bundle/
- SCITT architecture draft: https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/
- Rust `sigstore` crate docs: https://docs.rs/sigstore/latest/sigstore/
- Rust `coset` crate docs: https://docs.rs/coset/latest/coset/
- Rust `serde_jcs` crate docs: https://docs.rs/serde_jcs/latest/serde_jcs/
- Rust `zip` crate docs: https://docs.rs/zip/latest/zip/

## Rust fuzzing primitives (inputs for P-0243)
- Rust Fuzz Book (cargo-fuzz overview/tutorial/coverage): https://rust-fuzz.github.io/book/cargo-fuzz.html
- cargo-fuzz crate registry entry (documents `cmin` and related workflows): https://crates.io/crates/cargo-fuzz

## SemVer/API diff tooling (inputs for P-0244)
- cargo-semver-checks (current de-facto tool; notes rustdoc JSON instability): https://github.com/obi1kenobi/cargo-semver-checks
- Rust project goal for merging cargo-semver-checks into Cargo: https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html
- Cargo’s SemVer compatibility reference: https://doc.rust-lang.org/cargo/reference/semver.html


## Notes added 2026-03-05 (52)
- Attestation building blocks: `tss-esapi` (TPM ESAPI wrapper), COSE libraries (`cose-rust`, `cose`).
- ACVP-related: NIST ACVP specs/repo, existing clients like Cisco `libacvp`, and Rust parsing helpers like `acvp-parser`.
- SCITT ecosystem: IETF SCITT architecture + SCRAPI drafts; this proposal focuses on client/verification + evidence artifacts (not running a log).

## Identity / directory / calendaring
- libdav (CalDAV/CardDAV client lib): https://crates.io/crates/libdav
- kaldav (CalDAV client): https://crates.io/crates/kaldav
- fast-dav-rs (async CalDAV client): https://crates.io/crates/fast-dav-rs
- xandikos (CalDAV/CardDAV server): https://crates.io/crates/xandikos
- samael (SAML2 library): https://crates.io/crates/samael
- saml-rs (IdP-focused SAML work): https://terminaloutcomes.github.io/saml-rs/saml_rs/
- ldap3 (LDAP client): https://crates.io/crates/ldap3

## Added 2026-03-05 (supporting context for P-0251..P-0253)

- DNS: Hickory DNS (formerly Trust-DNS) — https://crates.io/crates/hickory-dns
- DNS: announcement/rename context — https://bluejekyll.github.io/blog/posts/announcing-hickory-dns/
- JOSE/JWT: jsonwebtoken — https://crates.io/crates/jsonwebtoken
- JOSE/JWT: josekit — https://crates.io/crates/josekit
- Git: gix (gitoxide) — https://crates.io/crates/gix
- Git: git2 (libgit2 bindings) — https://crates.io/crates/git2


## Notes added 2026-03-05 (rev0064)
- BGP/BMP parsing exists (e.g., bgpkit-parser) but proposal P-0254 focuses on portable evidence bundles + canonical diffs: https://crates.io/crates/bgpkit-parser
- Rust GraphQL servers exist (async-graphql, juniper) but proposal P-0255 targets GraphQL-over-HTTP interop evidence + conformance harness: https://crates.io/crates/async-graphql ; https://crates.io/crates/juniper


## Added 2026-03-05 (supporting context for P-0259..P-0261)

- SPDM: intel/rust-spdm (implementation moved from jyao1/rust-spdm): https://github.com/intel/rust-spdm
- SPDM (kernel work): rspdm RFC threads: https://lkml.org/lkml/2025/2/27/191
- Redfish SDK: redfish (async-first): https://crates.io/crates/redfish
- Redfish codegen: redfish-codegen: https://crates.io/crates/redfish-codegen
- Redfish (vendor/client): nv-redfish: https://crates.io/crates/nv-redfish
- AMQP 1.0: ntex-amqp framework: https://crates.io/crates/ntex-amqp
- AMQP 1.0: dove library: https://lib.rs/crates/dove

## Pointers added (2026-03-05)
- Kafka protocol reference: official guide (wire schema) — https://kafka.apache.org/protocol/
- Envoy xDS protocol docs + data-plane-api protos — https://www.envoyproxy.io/docs/envoy/latest/api-docs/xds_protocol ; https://github.com/envoyproxy/data-plane-api
- Rust: `xds-api` bindings and `xds-client` early client crate — https://crates.io/crates/xds-api ; https://crates.io/crates/xds-client/0.1.0-alpha.1
## Notes added (2026-03-05)
- WebTransport building blocks exist (e.g., `web-transport-quinn`, `webtransport-rs`), but are not a conformance/evidence lab. https://crates.io/crates/web-transport-quinn
- RDP implementations/bindings exist (`IronRDP`, `rdp-rs`, `freerdp2`), but lack standardized redactable trace bundles.
  - https://github.com/Devolutions/IronRDP
  - https://crates.io/crates/rdp-rs
  - https://crates.io/crates/freerdp2
- Container runtime APIs exist in Rust (`containerd-client`, containerd rust-extensions), but no CRI capture/replay kit.
  - https://crates.io/crates/containerd-client
  - https://github.com/containerd/rust-extensions

## Notes added 2026-03-05 (P-0268..P-0270)

- PostgreSQL protocol and driver ecosystem is strong (`tokio-postgres`, `postgres`, `sqlx`, `postgres-protocol`, `pgwire`), but there is no common *evidence bundle* / interop harness.
  - https://crates.io/crates/tokio-postgres
  - https://crates.io/crates/sqlx
  - https://crates.io/crates/postgres-protocol
  - https://crates.io/crates/pgwire
- S3 clients and servers exist (AWS SDK for Rust, `s3`, `s3s`, MinIO), but compatibility testing is ad hoc and non-portable.
  - https://crates.io/crates/aws-sdk-s3
  - https://crates.io/crates/s3
  - https://crates.io/crates/s3s
  - https://github.com/minio/minio
- OpenTelemetry Rust crates cover SDK/export, but troubleshooting OTLP ingest/partial success remains ecosystem-specific without a standardized capture/replay artifact.
  - https://crates.io/crates/opentelemetry
  - https://crates.io/crates/opentelemetry-otlp
  - https://crates.io/crates/opentelemetry-proto

## New overlap pointers (2026-03-05)

- WebGPU ecosystem: `wgpu`, `wgpu-native`, and the upstream WebGPU CTS repository/runner.
- Arrow Flight ecosystem: `arrow-flight` (arrow-rs) and Flight.proto in Apache Arrow.
- gNMI ecosystem: OpenConfig gNMI spec + reference implementations (`openconfig/gnmi`).


## Notes added 2026-03-05
- Wi‑Fi Easy Connect (DPP) references: Android platform docs; vendor SDK docs (ESP-IDF).
- Modbus Rust stacks: `tokio-modbus`, `modbus-rs`, `modbus-core`.

## SSH
- russh (client/server SSH library): https://crates.io/crates/russh
- thrussh (SSH2 implementation): https://crates.io/crates/thrussh

## ActivityPub / federation
- activitypub-federation (framework extracted from Lemmy): https://crates.io/crates/activitypub-federation

## NATS
- async-nats (actively developed NATS client): https://crates.io/crates/async-nats
- nats (legacy client): https://crates.io/crates/nats
## Identity / OAuth / OIDC building blocks
- `openidconnect` (OIDC client/library) — useful substrate for profile-as-code harnesses.
  - https://crates.io/crates/openidconnect
- `oauth2` (OAuth 2.0 client primitives) — substrate for high-security profile checks.
  - https://crates.io/crates/oauth2

## SQLite ecosystem signals
- SQLite on-disk format reference (anchor for artifact-level tooling).
  - https://sqlite.org/fileformat.html
- `rusqlite` (SQLite bindings) — not an on-disk artifact inspector.
  - https://crates.io/crates/rusqlite
- `sqlite-parser-nom` / `sqlite_wasm_reader` — partial file-format readers; useful overlap checks.
  - https://crates.io/crates/sqlite-parser-nom
  - https://crates.io/crates/sqlite_wasm_reader

## BACnet Rust crates
- `bacnet-rs`, `bacnet-emb`, `mabi-bacnet` — implementations/simulators to adapter-wrap.
  - https://crates.io/crates/bacnet-rs
  - https://crates.io/crates/bacnet-emb
  - https://crates.io/crates/mabi-bacnet

## Notes added 2026-03-05 — related ecosystem pieces

- TLS/X.509 stacks and helpers:
  - `rustls` (TLS library): https://crates.io/crates/rustls
  - `webpki` (X.509 validation helper): https://crates.io/crates/webpki
  - `x509-parser` (DER parsing): https://crates.io/crates/x509-parser

- IEC 60870-5-104:
  - OpenMUC j60870 (Java reference implementation / field context): https://www.openmuc.org/j60870/user-guide/
  - Rust crates vary in completeness; interop tooling should adapter-wrap, not replace.

- HL7 v2 / MLLP:
  - Existing HL7 parsing crates exist, but the gap is **transport evidence + PHI-safe bundles**:
    https://crates.io/crates/hl7

## Networking protocol stacks relevant to new evidence kits (2026-03-05)

- SNMP: crates like `snmp`, `snmp-parser` (plus vendor tooling); proposals focus on **interop evidence** rather than stack replacement.
- RADIUS: Rust has partial client/server crates; proposals focus on **registry-pinned decoding + evidence bundles** for AAA debugging.
- CAN/UDS: ecosystem includes SocketCAN bindings and various automotive crates; proposals focus on **canonical trace IR + UDS session evidence**.


## Additions (2026-03-05)

- DNP3 implementations: `dnp3` crate (Step Function I/O) (IEEE 1815).
- OpenID Federation: `openid-federation` crate.
- JPEG XL: `jxl-encoder` (pure Rust encoder), `jpegxl-rs` wrapper around libjxl.


## Added 2026-03-06 (68)

### OpenRTB / AdCOM
- `iab` — strongly typed structures for OpenRTB/AdCOM and related IAB specs: https://crates.io/crates/iab
- `iab-specs` — feature-gated spec support including AdCOM/OpenRTB: https://crates.io/crates/iab-specs
- `openrtb`, `openrtb2` — older type-oriented crates: https://crates.io/crates/openrtb ; https://crates.io/crates/openrtb2
- Gap note: proposals should target **interop evidence + profile validation**, not duplicate base schemas.

### MAVLink
- `mavlink` — protocol implementation with message sets: https://crates.io/crates/mavlink
- `mavio` — minimal transport-agnostic MAVLink communication: https://crates.io/crates/mavio
- `maviola` — stateful MAVLink abstractions: https://crates.io/crates/maviola
- `mavspec` — codegen/spec toolchain direction: https://crates.io/crates/mavspec
- Gap note: proposals should target **microservice replay/conformance**, not another frame parser.

### ORC
- `orc-rust` — active native Rust ORC implementation: https://crates.io/crates/orc-rust
- `orc-format` — safe Rust ORC toolkit: https://crates.io/crates/orc-format
- `orcrs` — ORC reader: https://crates.io/crates/orcrs
- Gap note: avoid pitching a greenfield ORC engine unless there is evidence that `orc-rust` cannot grow into the role.

### BPMN / DMN
- `dsntk` — DMN/FEEL toolkit: https://crates.io/crates/dsntk
- `bpmn-engine`, `bpm-engine-bpmn`, `snurr`, `bpxe` — BPMN parsers/engines in varying maturity levels.
  - https://crates.io/crates/bpmn-engine
  - https://crates.io/crates/bpm-engine-bpmn
  - https://crates.io/crates/snurr
  - https://crates.io/crates/bpxe
- Gap note: target **conformance, portability, and replayable evidence**, not yet another isolated engine.

### AS2
- Rust does not appear to have an obvious, mature, widely adopted AS2 crate family on crates.io at the moment of this pass. Re-check before draft promotion.
- Non-Rust reference point: `phase2` (Java): https://github.com/phax/phase2


## Added 2026-03-06 (69)

- **FIX is not a “no crates exist” gap**. There are Rust bindings and native engines (`quickfix`, `fefix`, `fixer`, HotFIX family). The missing layer is cross-engine **Orchestra-aware interop, replay, and evidence**.
- **XBRL is not just a parser gap**. Arelle and official conformance suites already define a strong reference world; the Rust opportunity is **canonical facts, conformance harnesses, and reproducible filing bundles**.
- **IPP is not merely “need an IPP client.”** A real gap remains in **IPP Everywhere profile/certification workflows**, especially capability diffs and replayable issue artifacts.
- **SECS/GEM is not “no Rust at all.”** Emerging crates cover parts of SECS-II/HSMS; the missing value is **GEM/state-machine semantics, scenario packs, and fab-safe evidence artifacts**.
- **EBICS should be treated as a profile/evidence problem first**, not as a reason to invent a giant end-to-end payments platform.


## Added 2026-03-06 (70)

### OCPP
- `rust-ocpp` — OCPP 1.6 / 2.0.1 / 2.1 data types and protocol support direction: https://crates.io/crates/rust-ocpp
- `ocpp-client` — client-side implementation substrate: https://crates.io/crates/ocpp-client
- Gap note: proposals should target **interop/certification/evidence**, not merely duplicate message types.

### FHIR / SMART
- `helios-fhir`, `helios-fhirpath`, `fhir-rs`, `fhir` — meaningful Rust substrate for models and FHIRPath.
  - https://crates.io/crates/helios-fhir
  - https://crates.io/crates/helios-fhirpath
  - https://crates.io/crates/fhir-rs
  - https://crates.io/crates/fhir
- Gap note: the opportunity is **IG pinning + launch replay + PHI-safe evidence**, not just another model generator.

### RDAP / EPP
- ICANN-sponsored RDAP crates: `icann-rdap-common`, `icann-rdap-client`, `icann-rdap-srv`.
  - https://crates.io/crates/icann-rdap-common
  - https://crates.io/crates/icann-rdap-client
  - https://crates.io/crates/icann-rdap-srv
- `epp-client` provides registrar-side substrate: https://crates.io/crates/epp-client
- Gap note: proposals should join **provisioning and publication evidence** rather than only parsing RDAP JSON.

### IFC / BIM
- `ifc_rs`, `bimifc-parser`, `ifc-lite-core`, `ifc` show active parser/model movement.
- buildingSMART validation infrastructure is a strong non-Rust reference point for conformance-first design.
- Gap note: target **validation, semantic diffs, and bundle workflows**, not a giant monolithic BIM platform.

### OpenADR
- OpenLEADR / Rust crates: `openleadr-wire`, `openleadr-client`, `openleadr-vtn`.
- Gap note: the missing layer is **scenario replay + profile pinning + evidence bundles**, not a greenfield protocol rewrite.



## Added 2026-03-06 (71)

### AS4 / Peppol eDelivery
- Strong official profile surface exists in EU eDelivery and Peppol documentation; proposals should target **onboarding, discovery, trust, and evidence**, not generic XML reinvention.
- `faktura` shows invoice-generation momentum in Rust, but does not close the network-interoperability gap.

### GS1 EPCIS / CBV
- GS1 publishes mature EPCIS references; proposals should target **canonical events, vocabulary lockfiles, lineage diffs, and evidence bundles** rather than another thin codec.
- `gs1` provides identifier-oriented substrate, which should be treated as a building block rather than proof the problem is solved.

### ONVIF / RTSP
- Rust substrate exists: `retina`, `onvif-cam-rs`, `onvif-rs`, and ONVIF-adjacent GStreamer work.
- Gap note: the proposal should stay focused on **profile-aware interop evidence**, not a monolithic VMS or analytics stack.

### DLMS / COSEM
- `dlms_cosem` and related smart-meter crates show Rust can parse pieces of the stack.
- Gap note: target **profile pinning + replay + object-model diagnostics**, not a giant head-end system.

### SIP / SDP / RTP
- `rsip`, `rsip-dns`, and `rsipstack` are real and recently active substrate.
- Gap note: the missing layer is **canonical call evidence + replay + profile pinning**, not another header parser.


## Added 2026-03-06 (72)

### OPC UA PubSub / UAFX
- Rust OPC UA substrate is real: `async-opcua`, `async-opcua-types`, and related crates.
- Gap note: the missing value is **PubSub/UAFX replay, profile pinning, timing/metadata diagnostics, and portable evidence**, not another generic OPC UA client/server pitch.

### GTFS / GTFS Realtime
- `gtfs-realtime` and `gtfs-rt` provide Rust parsing/manipulation substrate for realtime feeds.
- Gap note: the real missing layer is **schedule-aware semantic validation and replay**, not protobuf decoding alone.

### OGC API / CQL2
- GeoRust now has notable OGC API substrate: `ogcapi`, `ogcapi-types`, and related crates.
- Gap note: proposals should target **conformance/query lockfiles + semantic result diffs + bug bundles**, not just another API scaffold.

### DCSA eBL / PINT
- Official standards and interoperability machinery are maturing quickly, but there does not appear to be a clear boring-default Rust crate family for eBL/PINT interop workflows yet. Re-check before draft promotion.
- Gap note: target **portable handoff/dispute evidence and profile pinning**, not a giant end-to-end trade SaaS.

### STIX / TAXII
- Rust substrate exists in crates like `stix`, `stix2`, and OASIS-hosted Rust STIX work.
- Gap note: the missing opportunity is **semantic diffing + TAXII replay + profile-aware evidence**, not merely serializing STIX JSON.


## Added 2026-03-06 (73)

### Asset Administration Shell (AAS)
- IDTA publishes current multi-part AAS releases, including API and package-format surfaces.
- Rust substrate exists in `aas` and the Eclipse BaSyx Rust SDK.
- Gap note: the missing value is **semantic/package conformance + profile pinning + evidence bundles**, not a giant digital-twin platform.

### OGC SensorThings API
- Official OGC SensorThings standards are mature and explicitly span REST/OData + MQTT-style usage.
- Rust substrate exists in `sensorthings-validator`, which is a good sign that the ecosystem can support a broader conformance/replay layer.
- Gap note: proposals should target **observation semantics, query/paging drift, MQTT replay, and portable evidence**, not generic IoT platform ambition.

### IIIF
- IIIF already has explicit API surfaces, compliance levels, and validator services for Image and Presentation APIs.
- Rust substrate exists in crates like `iiif` and `i3f`.
- Gap note: the opportunity is **compliance/profile lockfiles + cross-image/presentation diagnostics + replayable evidence**, not a monolithic viewer or DAMS.

### HLS / LL-HLS
- Rust substrate exists in `m3u8-rs`, `quick-m3u8`, and `hls_client`.
- Gap note: the real missing layer is **playlist/timeline semantics + low-latency replay + profile pinning + portable bug bundles**, not another standalone parser.

### RO-Crate
- RO-Crate 1.2 is stable and Rust now has `ro-crate-rs` plus fresh research momentum.
- Gap note: proposals should target **profile-aware verification + deterministic packaging + semantic archival diffs**, not a giant repository platform.



## Added 2026-03-06 (74)

### AMWA NMOS
- AMWA already provides a broad spec family and the NMOS Testing Tool.
- Rust substrate exists in `nmos-rs`, even if it is not yet a boring-default stack.
- Gap note: proposals should target **topology/activation replay + evidence bundles**, not merely another API wrapper.

### UBL / EN16931 / Peppol / PINT
- Rust substrate exists in crates like `faktura` and `einvoice`.
- Gap note: the real missing value is **profile pinning + explainable rule failures + semantic diffs**, not just XML generation.

### SDMX 3.0
- `sdmx_json` and the `neoncitylights/sdmx` monorepo are real substrate.
- Official specs and TCK activity are public and active.
- Gap note: target **query lockfiles + structure-aware diffs + replay**, not merely data deserialization.

### 3MF
- Rust substrate exists in `lib3mf`, `threemf`, and newer native efforts like `lib3mf-rs`.
- Official conformance suites now exist.
- Gap note: the opportunity is **package/extension conformance and portable evidence**, not another thin reader/writer alone.

### LTI 1.3 / LTI Advantage
- Rust substrate exists in Atomic Forge, `atomic-lti-tool`, and `atomic-lti-tool-axum`.
- Gap note: the missing layer is **launch/service replay + redaction + profile packs**, not generic JWT/OAuth primitives.



## Added 2026-03-06 (75)

### Crossref / JATS
- JATS 1.4 and Crossref 5.4.0 are both current, public, machine-readable surfaces.
- Rust substrate is becoming real in `crossref-xml` and related scholarly-metadata crates.
- Gap note: the missing value is **profile-pinned transforms + explainable validation + replayable deposit bundles**, not just XML generation.

### OCFL / BagIt
- Rust substrate exists in `rocfl`, `async_bagit`, and `bagr`.
- Gap note: the missing layer is **BagIt-profile pinning + OCFL ingest planning + semantic preservation diffs + portable evidence**, not another giant repository platform.

### DDEX ERN / MEAD
- Rust substrate exists in `ddex-core`, `ddex-parser`, and `ddex-builder`.
- Gap note: the real missing value is **partner-profile lockfiles + semantic delivery diffs + onboarding evidence bundles**, not merely parsing DDEX XML faster.

### OpenDRIVE / OpenSCENARIO
- Rust substrate exists in `opendrive` and early `openscenario-rs` work.
- Official ASAM checker infrastructure now exists for OpenDRIVE and OpenSCENARIO XML.
- Gap note: the opportunity is **road/scenario lockfiles + checker normalization + replayable evidence**, not a fresh monolithic simulator.

### CCSDS CFDP
- Rust substrate exists in `cfdp-rs`, `cfdp-simplified`, and `spacepackets`.
- Gap note: the missing value is **mission-profile pinning + transaction replay + semantic fault diffs + portable anomaly bundles**, not another bare PDU crate.



## Added 2026-03-06 (76)

### EPUB / OPDS
- Rust substrate exists in crates like `epub`, `lib-epub`, and `opds`.
- EPUBCheck already exists and should be wrapped, not ignored.
- Gap note: the missing value is **profile pinning + validator normalization + package/catalog diffs + portable evidence**, not another bare ZIP/XML reader.

### BIDS / NIfTI
- The official BIDS Validator is active and Rust already has the `nifti` crate.
- Gap note: the opportunity is **dataset/profile semantics + header-aware diagnostics + redactable evidence bundles**, not merely parsing headers or directory trees.

### STAC
- Rust substrate exists in `stac`, `stac-api`, and `stac-server`.
- Community validation tools already exist.
- Gap note: the missing layer is **validation normalization + query replay + semantic diffs**, not another catalog/server implementation by itself.

### LAS / LAZ / COPC
- Rust substrate exists in `las`, `las-crs`, and `copc-rs`.
- Gap note: the opportunity is **profile-aware header/CRS/COPC replay evidence**, not just another point-cloud parser.

### MARC / BIBFRAME
- Rust substrate exists in `marc`, `marc-record`, and `mrrc`, while official conversion tooling/specs already exist from the Library of Congress.
- Gap note: the missing value is **round-trip semantic diffs + profile-pinned conversion workbench bundles**, not merely ISO 2709 or XML parsing.


## Added 2026-03-06 (77)

### GA4GH htsget / refget / Crypt4GH
- Rust substrate exists in `noodles-htsget`, `htsget-search`, and `crypt4gh`.
- GA4GH already publishes htsget/refget/Crypt4GH specs and a public htsget compliance suite.
- Gap note: the real missing value is **profile pinning + reference-aware replay + privacy-aware evidence bundles**, not a fresh file parser.

### xAPI / cmi5
- Rust substrate exists in `xapi-rs`, and official xAPI/cmi5/profile documentation is public.
- Gap note: proposals should target **profile-aware validation + session replay + semantic diffs**, not another analytics dashboard or LMS.

### NETCONF / YANG / RESTCONF
- Rust substrate exists in `netgauze-netconf-proto`, `netconf-rs`, `netconf-rust`, and `serde_yang`/YANG parsers.
- Gap note: the opportunity is **capability lockfiles + cross-surface diffs + replayable evidence**, not one more thin protocol client.

### AsyncAPI / CloudEvents
- Rust substrate exists in `asyncapi-rust`, `asyncapiv3`, and `cloudevents-sdk`.
- Gap note: the missing layer is **binding-aware contract verification + transport-neutral semantic diffs + replayable evidence**, not just spec generation.

### DataCite / CodeMeta / CITATION.cff
- Rust fragments exist in `crate2bib`, `aeruginous`, and `code-metadata`.
- Gap note: the opportunity is **deterministic crosswalks + loss reporting + release/deposit bundles**, not merely formatting one citation string.

## Added 2026-03-06 (78)

### OpenUSD / USDZ
- `openusd` (native Rust OpenUSD library): https://crates.io/crates/openusd
- `openusd-rs` (pure Rust OpenUSD implementation): https://crates.io/crates/openusd-rs
- `pxr_rs` (Rust interface for OpenUSD): https://github.com/AndrejOrsula/pxr_rs
- `usdchecker` / OpenUSD toolset: https://openusd.org/release/toolset.html

### CityGML / CityJSON
- `cjval` (official Rust validator for CityJSON/CityJSONSeq): https://github.com/cityjson/cjval
- `ecitygml` (Rust CityGML 3.0 processing): https://docs.rs/ecitygml
- 3D City DB validation tooling: https://3dcitydb-docs.readthedocs.io/en/version-2024.0/impexp/cli/validate.html

### netCDF / CF / OPeNDAP
- `netcdf` (Rust bindings): https://crates.io/crates/netcdf
- `readap` (Rust OpenDAP client/parser): https://crates.io/crates/readap
- CF checker / conventions tooling: https://cfconventions.org/conventions.html

### CAP / IPAWS
- `rasn-cap`: https://crates.io/crates/rasn-cap
- `oasiscap`: https://github.com/willglynn/oasiscap
- FEMA CAP/IPAWS developer guidance: https://www.fema.gov/emergency-managers/practitioners/integrated-public-alert-warning-system/technology-developers/common-alerting-protocol

### MusicXML / MEI
- `musicxml`: https://crates.io/crates/musicxml
- `verovioxide`: https://crates.io/crates/verovioxide
- `muxml-rust`: https://github.com/rbermani/muxml-rust


## Added 2026-03-06 (79)

### glTF / KTX2
- Rust substrate exists in `gltf`, `gltf-validator`, and `ktx2` / `libktx_rs`.
- Khronos already publishes the core spec, validator, and KTX2 spec.
- Gap note: the missing value is **profile pinning + validator normalization + package/texture evidence**, not another basic loader.

### WARC / CDXJ / WACZ
- Rust substrate exists in `warc`, `warcat`, `rust_warc`, and `wacksy`.
- Gap note: the real opportunity is **cross-layer audit + replay probes + portable evidence bundles**, not only raw WARC parsing.

### miniSEED / StationXML / SeedLink
- Rust substrate exists in `stationxml-rs`, `seedlink`, `mseedio`, and related miniSEED crates.
- Gap note: the missing layer is **waveform/inventory/transport alignment + replayable evidence**, not isolated file or socket handling.

### MCAP / rosbag2
- Rust substrate exists in `mcap`, `rosbags-rs`, `rustbag`, and the Rust Foxglove SDK.
- Gap note: the sharper contribution is **schema/topic/clock lockfiles + conversion audits + replay bundles**, not yet another logger.

### MPEG-DASH
- Rust substrate exists in `dash-mpd` and `dash-mpd-cli`.
- DASH-IF already provides a conformance surface.
- Gap note: the missing value is **validator wrapping + segment-aware semantic diffs + portable evidence**, not just MPD parsing or downloading.


## Added 2026-03-06 (80)

### ISO 20022 / CBPR+ / HVPS+ / SEPA
- Rust substrate exists in `open-payments-iso20022`, `iso20022`, `iso-20022-sdk`, and focused crates like `pain`.
- Official message-definition catalogues and market-practice overlays already exist.
- Gap note: the missing value is **profile locks + overlay-aware validation + semantic diffs + privacy-aware evidence**, not merely another XML model.

### OME-Zarr / NGFF
- Rust substrate exists in `ome_zarr_metadata`, `zarrs`, and `zarrs_tools`.
- OME already publishes a validator surface and conformance-test framing.
- Gap note: the opportunity is **validator normalization + structural/linkage checks + dataset evidence bundles**, not a fresh generic Zarr reader.

### GRIB2 / BUFR
- Rust substrate exists in `grib` and `eccodes`.
- WMO registries and ECMWF ecCodes already define the practical standards surface.
- Gap note: the missing layer is **table/version locks + ecCodes normalization + semantic diffs + evidence**, not raw binary decoding alone.

### FITS / WCS / VOTable
- Rust substrate exists in `fitsio`, `fitsrs`, `wcs`, and `votable`.
- FITS 4.0, WCS, and VOTable standards are already stable/public.
- Gap note: the real opportunity is **coordinate-aware validation + export-loss reporting + portable evidence bundles**, not another isolated parser.

### LSP / DAP / LSIF
- Rust substrate exists in `tower-lsp`, `lsp-types`, `ls-types`, and `dap`.
- Microsoft already publishes the protocol specs and LSIF model.
- Gap note: the missing layer is **capability lockfiles + transcript replay + semantic diffs + evidence bundles**, not more transport or type crates.

## Added 2026-03-06 (81): current substrate that means these are no longer “pure parser” gaps

### RDF / SPARQL / SHACL
- Rust substrate exists in `oxigraph`, `oxrdfio`, `oxrdf`, and Rio-family crates such as `rio_turtle`.
- W3C now has active RDF 1.2, SPARQL 1.2, and SHACL 1.2 surfaces.
- Gap note: the missing value is **canonicalization + validator/query replay + semantic diffs + portable evidence**, not just more RDF parsing.

### OData
- Rust substrate exists in `odata-params`, `odata_client_codegen`, `odata_client`, and domain-specific OData clients such as `reso-client`.
- OData protocol, CSDL, and JSON format specs are public and current.
- Gap note: the missing layer is **metadata locks + query replay + runtime drift evidence**, not merely another generated client.

### Iceberg / Delta
- Rust substrate exists in `iceberg`, `iceberg-catalog-rest`, and `deltalake`.
- Apache Iceberg and Delta both publish active/open metadata and connector surfaces.
- Gap note: the sharp opportunity is **catalog/table surface comparability + metadata drift evidence + replay**, not more file readers.

### VCF / BCF / CSI
- Rust substrate exists in `noodles`, `noodles-vcf`, `noodles-bcf`, and `noodles-csi`.
- HTS specs clearly publish current VCF/BCF/index surfaces.
- Gap note: the missing contribution is **header/index locks + region-query replay + semantic conversion diffs**, not raw parsing.

### Ion / PartiQL
- Rust substrate exists in `ion-rs`, `partiql`, and `partiql-extension-ion`.
- Ion and PartiQL have public specifications and real Rust implementation momentum.
- Gap note: the missing layer is **encoding-aware semantic replay and host-subset lockfiles**, not another serializer or query parser.


## Added 2026-03-06 (82): current substrate that means these are no longer “pure parser” gaps

### ONNX / ONNX Runtime
- Rust substrate exists in `onnx-ir`, `ort`, and `tract-onnx`.
- ONNX already publishes an IR specification and backend-test suite.
- Gap note: the missing value is **model/opset locks + backend diffs + replayable evidence**, not another runtime.

### LwM2M
- Rust substrate exists in `lwm2m-registry` and related registry/object tooling.
- OMA already publishes the OMNA object registry and interoperability test materials.
- Gap note: the opportunity is **object-version pinning + bootstrap/registration replay + redacted evidence**, not just another registry reader.

### SARIF
- Rust substrate exists in `sarif_rust` and `serde-sarif`.
- OASIS already publishes the SARIF standard and errata, and downstream platforms publish supported-subset guidance.
- Gap note: the missing layer is **subset locks + suppression/baseline diffs + replayable evidence**, not another scanner or raw JSON formatter.

### UN/EDIFACT
- Rust substrate exists in `edifact-types`, `edi-format`, and adjacent EDI parsing work.
- UNECE already publishes syntax rules and directory material.
- Gap note: the sharp opportunity is **release/profile lockfiles + code-list diffs + portable evidence**, not just syntax tokenization.

### OSCAL
- Rust substrate exists in `roscal_lib` and related OSCAL toolbox work.
- NIST already publishes validation guidance, metaschema-derived references, and model families.
- Gap note: the missing layer is **cross-document locks + linkage diffs + audit-ready evidence bundles**, not another compliance dashboard.

## Added 2026-03-06 (83): what exists already in the newly promoted domains

### SARIF
- `sarif_rust` — Rust SARIF schema/types: https://crates.io/crates/sarif_rust
- `serde-sarif` — SARIF serde support: https://docs.rs/serde-sarif
- OASIS SARIF 2.1.0 spec: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
- GitHub’s SARIF subset docs: https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support-for-code-scanning

**Conclusion:** the gap is **not** “Rust cannot represent SARIF.” The sharper gap is subset locks, baseline/fingerprint stability, and replayable ingestion evidence.

### Process mining
- `process_mining` — serious Rust support for XES, OCEL 2.0, and PNML: https://docs.rs/process_mining
- OCEL 2.0 spec/resources: https://www.ocel-standard.org/specification/overview/
- XES standard: https://www.xes-standard.org/
- PNML reference site: https://www.pnml.org/

**Conclusion:** the gap is **not** “Rust has no process-mining substrate.” The sharper gap is semantic-boundary tooling, loss accounting, and portable replay/evidence bundles.

### CSAF / OpenVEX / OSV
- `csaf-walker`: https://docs.rs/csaf-walker
- `openvex`: https://docs.rs/openvex
- `osv`: https://docs.rs/osv
- CSAF tools ecosystem: https://www.csaf.io/tools/
- Ubuntu OpenVEX feed: https://documentation.ubuntu.com/security/security-updates/vex/

**Conclusion:** the gap is **not** “Rust lacks advisory data types.” The sharper gap is cross-format product matching, status crosswalks, and explainable advisory evidence.

### Uptane / TUF / SUIT
- `tuf`: https://crates.io/crates/tuf
- `tough`: https://crates.io/crates/tough
- `tuftool`: https://crates.io/crates/tuftool
- `suit_validator`: https://crates.io/crates/suit_validator
- Uptane 2.1.0 standard: https://uptane.org/docs/2.1.0/standard/uptane-standard

**Conclusion:** the gap is **not** “Rust lacks secure-update primitives.” The sharper gap is deployment-policy locks, campaign replay, and explainable OTA evidence.

### OOXML / OPC
- `ooxmlsdk`: https://crates.io/crates/ooxmlsdk
- `ooxml-opc`: https://docs.rs/ooxml-opc/latest/ooxml_opc/
- `ooxml`: https://crates.io/crates/ooxml
- OOXML Validator: https://github.com/mikeebowen/OOXML-Validator

**Conclusion:** the gap is **not** “Rust cannot touch OOXML.” The sharper gap is validator normalization, package/profile locks, safe redaction, and semantic package diffs.

## Feature flags / OpenFeature
- OpenFeature Rust SDK: https://openfeature.dev/docs/reference/sdks/server/rust/
- open_feature_ofrep: https://docs.rs/open-feature-ofrep
- flagd Rust provider docs: https://flagd.dev/providers/rust/
- flagd: https://flagd.dev/

## Protobuf / descriptors / JSON mapping
- prost: https://github.com/tokio-rs/prost
- prost-reflect: https://github.com/andrewhickman/prost-reflect
- protobuf editions overview: https://protobuf.dev/editions/overview/

## Jupyter / notebooks / kernels
- jupyter-protocol: https://crates.io/crates/jupyter-protocol
- nbformat: https://crates.io/crates/nbformat
- runtimelib: https://docs.rs/crate/runtimelib/latest
- evcxr_jupyter: https://github.com/evcxr/evcxr/blob/main/evcxr_jupyter/README.md

## Remote execution / CAS
- bazel-remote-apis: https://crates.io/crates/bazel-remote-apis
- reapi: https://crates.io/crates/reapi
- Buildbarn remote execution: https://github.com/buildbarn/bb-remote-execution
- Remote APIs repo: https://github.com/bazelbuild/remote-apis

## 3D Tiles / geospatial 3D
- tyler: https://github.com/3DGI/tyler
- tyler crate: https://crates.io/crates/tyler
- geo-tileset: https://crates.io/crates/geo-tileset
- etiles: https://crates.io/crates/etiles


## Geospatial interchange / GeoArrow family
- GeoArrow Rust crates: https://geoarrow.org/geoarrow-rs/rust/
- GeoParquet spec: https://geoparquet.org/releases/v1.1.0/
- FlatGeobuf project/spec: https://flatgeobuf.org/
- geozero: https://docs.rs/crate/geozero/latest

## Device onboarding / FDO
- fdo-rs implementation: https://github.com/fdo-rs/fido-device-onboard-rs
- fdo-rs organization: https://github.com/fdo-rs
- FDO certification overview: https://fidoalliance.org/get-certified-fdo/

## GNSS / geodesy
- rinex Rust project: https://github.com/nav-solutions/rinex
- ntrip-client: https://docs.rs/ntrip-client
- gnss-qc: https://docs.rs/crate/gnss-qc/0.4.0/source/README.md

## Model-file substrate
- SafeTensors docs: https://huggingface.co/docs/safetensors/index
- safetensors repo: https://github.com/huggingface/safetensors
- Candle: https://github.com/huggingface/candle
- Candle SafeTensors module: https://docs.rs/candle-core/latest/candle_core/safetensors/index.html
- GGUF spec doc: https://github.com/ggml-org/ggml/blob/master/docs/gguf.md
- gguf crate: https://docs.rs/gguf

## USB HID
- USB HID specs/tools: https://www.usb.org/hid
- HID Usage Tables 1.7: https://usb.org/document-library/hid-usage-tables-17
- usbd-hid: https://docs.rs/usbd-hid
- hidparser: https://docs.rs/hidparser
- hid-report: https://docs.rs/hid-report
- rust-osdev usb utilities: https://github.com/rust-osdev/usb


## Added 2026-03-06 (86)

- **AT Protocol / Bluesky ecosystem**
  - Official AT specs now cover repository, sync, and Lexicon surfaces, and official docs now also describe backfilling and the newer Tap simplification layer.
  - Rust substrate exists via `atrium-api`, `atproto_lexicon`, and adjacent OAuth/identity/crypto crates.
  - Gap remains: no boring Rust default for **Lexicon-pinned sync evidence, backfill receipts, or migration-safe replay bundles**.

- **OCPI / EV roaming**
  - EVRoaming Foundation lists **OCPI 2.3.0** as current, documents booking extensions, and publishes a test tool roadmap.
  - Rust substrate exists via `ocpi` and `ocpi-tariffs`.
  - Gap remains: no boring Rust default for **partner onboarding evidence, extension-policy locks, or explainable tariff/session/CDR receipts**.

- **Substrait / Flight SQL / ADBC / DataFusion**
  - Substrait continues to position itself as cross-engine query interchange; ADBC and Flight SQL define complementary Arrow-native client/wire surfaces.
  - Rust substrate exists via DataFusion, `datafusion-substrait`, and `datafusion-flight-sql-server`.
  - Gap remains: no boring Rust default for **capability diffs, extension-pack locks, or query/result evidence bundles**.

- **PDF/A / PAdES**
  - veraPDF remains the open validator surface for PDF/A/PDF/UA; ETSI and DSS remain the obvious adjacent standards/tooling surfaces for PAdES validation.
  - Rust substrate exists via `lopdf` and early signing crates like `pdf_signing`.
  - Gap remains: no boring Rust default for **validator normalization, signature-scope diffs, or compact compliance-grade evidence bundles**.

- **MCTP / PLDM**
  - DMTF’s PMCI family continues to grow, including MCTP host-interface work and PLDM file-transfer / firmware-update surfaces.
  - Rust substrate now exists via `mctp-rs`, `pldm`, and `pldm-fw`.
  - Gap remains: no boring Rust default for **topology locks, package summaries, or replayable firmware/file-transfer incident bundles**.


## Added 2026-03-06 (87)

### OpenLineage / Marquez
- OpenLineage docs: https://openlineage.io/docs/
- OpenLineage object model: https://openlineage.io/docs/spec/object-model
- OpenLineage custom facets: https://openlineage.io/docs/spec/facets/custom-facets/
- Marquez reference implementation: https://github.com/MarquezProject/marquez

**Conclusion:** the gap is **not** “there is no lineage standard or backend.” The sharper gap is facet governance, naming-strategy discipline, semantic graph diffs, and portable incident evidence.

### DIDComm / mediation
- DIDComm Messaging v2.0: https://identity.foundation/didcomm-messaging/spec/v2.0/
- Out Of Band 2.0: https://didcomm.org/out-of-band/2.0/
- Coordinate Mediation 2.0: https://didcomm.org/coordinate-mediation/2.0/
- `didcomm`: https://crates.io/crates/didcomm
- `affinidi-messaging-didcomm`: https://docs.rs/affinidi-messaging-didcomm

**Conclusion:** the gap is **not** “Rust cannot pack DIDComm messages.” The sharper gap is explicit profile locks, routing receipts, safe redaction, and replayable interop bundles.

### FDC3
- FDC3 standard: https://fdc3.finos.org/docs/fdc3-standard
- API overview: https://fdc3.finos.org/docs/api/spec
- Desktop Agent Bridging: https://fdc3.finos.org/docs/agent-bridging/spec
- App Directory overview: https://fdc3.finos.org/docs/app-directory/overview

**Conclusion:** the gap is **not** “there is no FDC3 standard surface.” The sharper gap is vendor-neutral receipts, app-directory diffs, and cross-agent workflow evidence — especially in a Rust ecosystem that still has thin native substrate here.

### WebDriver BiDi / CDP
- WebDriver BiDi W3C TR: https://www.w3.org/TR/webdriver-bidi/
- WebDriver BiDi repository: https://github.com/w3c/webdriver-bidi
- `webdriverbidi`: https://crates.io/crates/webdriverbidi
- `fantoccini`: https://crates.io/crates/fantoccini
- `chromiumoxide`: https://crates.io/crates/chromiumoxide

**Conclusion:** the gap is **not** “Rust has no browser automation crates.” The sharper gap is capability locks, BiDi↔CDP fallback explanation, minimized replay slices, and portable flake evidence.

### OpenDAL / object_store
- Apache OpenDAL repository: https://github.com/apache/opendal
- OpenDAL capability docs: https://opendal.apache.org/docs/rust/opendal/struct.Capability.html
- `object_store` docs: https://docs.rs/object_store
- `arrow-rs-object-store` repository: https://github.com/apache/arrow-rs-object-store

**Conclusion:** the gap is **not** “Rust lacks storage abstraction crates.” The sharper gap is semantics probes, capability normalization, backend overlay packs, and portability-grade incident bundles.

## Added 2026-03-06 (frontier pass 88)

### MCP / protocol substrate
- Official MCP Rust SDK (`rmcp`): https://github.com/modelcontextprotocol/rust-sdk
- Official MCP SDK listing and tiering: https://modelcontextprotocol.io/docs/sdk
- Official authorization spec: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
- Official security best practices: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- Reference-server repo warns its servers are educational rather than production-ready: https://github.com/modelcontextprotocol/servers
- Interceptor extension repo exists, but is explicitly experimental: https://github.com/modelcontextprotocol/experimental-ext-interceptors
- Implication: future MCP proposals should avoid pretending “Rust has no MCP substrate”; the gap is often conformance, policy, evidence, or deployment guardrails above the SDK.

### Sigma / OCSF
- `rsigma` (parser/evaluator/linter/LSP toolkit): https://github.com/timescale/rsigma
- `sigma-rust` (parser/evaluator): https://github.com/jopohl/sigma-rust
- `ocsf-rs` / OCSF Rust schema efforts: https://github.com/yaleman/ocsf-rs
- `ocsf-types-rs`: https://github.com/dmitrikaramazov/ocsf-types-rs
- Implication: the missing Rust value is likely mapping receipts, corpora, and evidence bundles, not just “yet another parser”.

### Web of Things
- `wot` / `wot-td`: https://github.com/wot-rust/wot
- `webthing-rust`: https://github.com/WebThingsIO/webthing-rust
- Implication: Rust already has TD/server substrate, so future proposals should justify any new crate above parsing/serving basics.

### GA4GH cloud APIs
- GA4GH SDK issue tracker includes Rust-tagged work for DRS/TRS and extensions: https://github.com/ga4gh/ga4gh-sdk/issues
- Implication: Rust substrate is thin but not nonexistent; evidence/handoff tooling may be the better first move than a giant from-scratch stack.

### Frictionless / Data Package overlap
- `wacksy::datapackage` models Frictionless-style `datapackage.json` for WACZ packaging: https://docs.rs/wacksy/latest/wacksy/datapackage/
- Implication: there is partial overlap already, but not a general Rust workbench for package locks, validation receipts, and semantic diffs.


## Added 2026-03-06 (89)

### LoRaWAN / embedded radio substrate
- LoRaWAN L2 1.0.4 spec: https://resources.lora-alliance.org/technical-specifications/ts001-1-0-4-lorawan-l2-1-0-4-specification
- LoRaWAN 1.1 spec: https://resources.lora-alliance.org/technical-specifications/lorawan-specification-v1-1
- Regional Parameters RP002-1.0.5: https://resources.lora-alliance.org/technical-specifications/rp002-1-0-5-lorawan-regional-parameters
- `lorawan`: https://docs.rs/lorawan
- `lorawan-device`: https://docs.rs/lorawan-device
- `lora-phy`: https://docs.rs/crate/lora-phy/latest

**Conclusion:** the gap is **not** “Rust lacks a LoRaWAN stack.” The sharper gap is version/region overlays, certification-case mapping, MAC-trace normalization, and portable field-debug evidence.

### MIDI 2.0 / MIDI-CI
- MIDI 2.0 Specification Overview v1.1: https://amei.or.jp/midistandardcommittee/MIDI2.0/MIDI2.0-DOCS/M2-100-U_v1-1_MIDI_2-0_Specification_Overview.pdf
- Property Exchange overview: https://midi.org/midi-2-0-property-exchange
- Profiles / Property Exchange details: https://midi.org/details-about-midi-2-0-midi-ci-profiles-and-property-exchange-updated-june-2023
- `midi2`: https://docs.rs/midi2
- `midi20`: https://docs.rs/midi20

**Conclusion:** the gap is **not** “Rust cannot represent UMP packets.” The sharper gap is capability negotiation, profile/property receipts, and replayable interop fixtures.

### WebExtensions / browser-extension substrate
- WECG spec draft: https://w3c.github.io/webextensions/specification/
- WECG community group: https://www.w3.org/community/webextensions/
- MDN cross-browser guide: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Build_a_cross_browser_extension
- `web-extensions-sys`: https://docs.rs/web-extensions-sys/latest/i686-pc-windows-msvc/web_extensions_sys/
- `web-extensions`: https://docs.rs/web-extensions

**Conclusion:** the gap is **not** “there is no WebExtensions portability effort.” The sharper Rust gap is semantic manifest diffs, browser capability matrices, and evidence bundles above today’s mostly Chrome-oriented bindings.

### VDA 5050
- Official VDA 5050 repository/spec: https://github.com/VDA5050/VDA5050
- `vda5050-types`: https://docs.rs/vda5050-types
- `libVDA5050pp`: https://git.openlogisticsfoundation.org/silicon-economy/libraries/vda5050/libvda5050pp/-/tree/main/docs

**Conclusion:** the gap is **not** “there are no protocol types or reference libraries.” The sharper gap is topic-capture normalization, factsheet compatibility, order/state diffs, and portable onboarding receipts.

### FIX SBE / codegen substrate
- FIX SBE online materials: https://www.fixtrading.org/standards/sbe-online/
- Aeron SBE reference implementation: https://github.com/aeron-io/simple-binary-encoding
- `rustysbe`: https://docs.rs/rustysbe
- `sbe_gen`: https://docs.rs/sbe_gen
- `sbe-codegen`: https://crates.io/crates/sbe-codegen

**Conclusion:** the gap is **not** “Rust lacks SBE generators/codecs.” The sharper gap is generator-neutral schema IR, acting-version receipts, and evidence-grade schema-evolution diffs.


## Added 2026-03-06 (90)

### OpenAPI Overlay / Arazzo / Rust substrate
- Overlay Specification latest: https://spec.openapis.org/overlay/latest.html
- Arazzo Specification latest: https://spec.openapis.org/arazzo/latest.html
- Arazzo 1.0.1 release note: https://www.openapis.org/blog/2025/01/24/announcing-arazzo-specification-version-1-0-1
- `arazzo-models`: https://docs.rs/arazzo-models
- `openapiv3`: https://docs.rs/openapiv3

**Conclusion:** the gap is **not** “Rust cannot model OpenAPI-family documents.” The sharper gap is deterministic overlay receipts, workflow/source pinning, and post-transform semantic diffs.

### CMSIS-SVD / IP-XACT / register tooling
- CMSIS-SVD overview: https://arm-software.github.io/CMSIS_5/SVD/html/index.html
- CMSIS-SVD format docs: https://arm-software.github.io/CMSIS_5/SVD/html/svd_Format_pg.html
- Accellera IP-XACT downloads/user guide: https://www.accellera.org/downloads/standards/ip-xact
- `svd-rs`: https://docs.rs/svd-rs
- `svd2rust`: https://docs.rs/svd2rust
- `yarig`: https://crates.io/crates/yarig

**Conclusion:** the gap is **not** “Rust lacks SVD/PAC tooling.” The sharper gap is neutral register IR, conversion-loss accounting, patch overlays, and evidence that can span firmware and IP flows.

### OpenPGP / discovery / trust policy
- RFC 9580 OpenPGP: https://www.rfc-editor.org/rfc/rfc9580.html
- `sequoia-openpgp`: https://docs.rs/sequoia-openpgp/latest/sequoia_openpgp/
- `sequoia-net`: https://docs.rs/sequoia-net/latest/sequoia_net/
- `sequoia-cert-store`: https://docs.rs/sequoia-cert-store/latest/sequoia_cert_store/
- `sequoia-autocrypt`: https://docs.rs/sequoia-autocrypt/latest/sequoia_autocrypt/
- Autocrypt spec PDF: https://docs.autocrypt.org/_/downloads/en/main/pdf/

**Conclusion:** the gap is **not** “Rust has no serious OpenPGP implementation.” The sharper gap is discovery precedence, trust-policy explanation, safe redaction, and portable evidence bundles.

### ASAM MDF / A2L / DBC substrate
- ASAM MDF wiki: https://www.asam.net/standards/detail/mdf/wiki/
- ASAM MCD-2 MC (A2L): https://www.asam.net/standards/detail/mcd-2-mc/
- `a2lfile`: https://docs.rs/a2lfile
- `asammdf`: https://docs.rs/asammdf
- `can_decode`: https://docs.rs/can_decode
- `dbc-rs`: https://crates.io/crates/dbc-rs

**Conclusion:** the gap is **not** “Rust cannot parse these files.” The sharper gap is pinned interpretation metadata, signal-map diffs, and explicit loss accounting across standard and de facto sidecars.

### Web Push / VAPID / ECE substrate
- RFC 8030 Web Push: https://www.rfc-editor.org/rfc/rfc8030.html
- RFC 8291 Web Push encryption: https://www.rfc-editor.org/rfc/rfc8291.html
- RFC 8292 VAPID: https://www.rfc-editor.org/rfc/rfc8292.html
- `web-push`: https://docs.rs/web-push/
- `web-push-native`: https://docs.rs/web-push-native
- `ece`: https://crates.io/crates/ece

**Conclusion:** the gap is **not** “Rust has no Web Push senders.” The sharper gap is subscription/delivery receipts, redaction-safe debugging artifacts, and explicit browser/service overlays.

## Added 2026-03-06 (91)

### ISO 15118 / Plug & Charge / V2G substrate
- CharIN ISO 15118 overview: https://www.charin.global/technology/iso15118
- CharIN Plug & Charge overview: https://www.charin.global/technology/plug-charge
- CharIN knowledge base / implementation guidance: https://www.charin.global/technology/knowledge-base
- EcoG open implementation: https://github.com/EcoG-io/iso15118
- Rust encoder bindings: https://github.com/tux-evse/iso15118-encoders-rs

**Conclusion:** the gap is **not** “nobody is implementing ISO 15118.” The sharper Rust gap is session locks, certificate-chain receipts, profile overlays, and shareable field-debug evidence.

### Desktop shipping / release substrate
- `dist` / `cargo-dist`: release engineering, installer generation, and machine-readable manifests. Source: https://axodotdev.github.io/cargo-dist/book/
- `cargo-packager`: cross-platform desktop packaging as a CLI and Rust library, with signing helpers. Source: https://docs.rs/cargo-packager/latest/cargo_packager/
- CrabNebula Packager docs: macOS/Windows/Linux package families plus compatible updater flow. Source: https://docs.crabnebula.dev/packager/
- Tauri distribution docs: direct-download vs store routes, per-platform signing, macOS notarization, and updater artifact/signature concerns are all explicit substrate. Source: https://v2.tauri.app/distribute/ and https://v2.tauri.app/plugin/updater/
- Patchify: self-updating Rust application substrate exists, which means future desktop-shipping proposals should avoid pretending updater capability is absent. Source: https://github.com/danwilliams/patchify
- Implication: future desktop-shipping proposals should avoid pretending “Rust cannot package or update desktop apps.” The sharper gap is often a **release/update/support contract above existing tooling**.

### XDG Desktop Portal / Rust desktop substrate
- XDG Desktop Portal docs: https://flatpak.github.io/xdg-desktop-portal/docs/
- Portal API reference: https://flatpak.github.io/xdg-desktop-portal/docs/api-reference.html
- Request interface: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Request.html
- Documents interface: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Documents.html
- `ashpd`: https://docs.rs/ashpd/latest/ashpd/
- `zbus`: https://docs.rs/zbus

**Conclusion:** the gap is **not** “Rust lacks portal bindings.” The sharper gap is backend capability matrices, request/session receipts, and sandbox-safe portability evidence.

### OpenFGA / ReBAC substrate
- OpenFGA overview: https://openfga.dev/docs/fga
- Configuration language: https://openfga.dev/docs/configuration-language
- Immutable models: https://openfga.dev/docs/getting-started/immutable-models
- Contextual tuples: https://openfga.dev/docs/interacting/contextual-tuples
- Testing models: https://openfga.dev/docs/modeling/testing
- Store file format: https://openfga.dev/docs/modeling/store-file-format
- `openfga-client`: https://docs.rs/openfga-client
- `openfga-rs`: https://docs.rs/crate/openfga-rs/latest

**Conclusion:** the gap is **not** “Rust has no OpenFGA clients.” The sharper gap is immutable-model pinning, tuple-change receipts, replayable decisions, and explainable authz diffs.

### E57 / LAS / COPC point-cloud substrate
- libE57 overview: https://libe57.org/
- OGC LAS overview: https://www.ogc.org/standards/las/
- COPC spec site: https://copc.io/
- `e57`: https://docs.rs/e57
- `las`: https://docs.rs/las
- `copc-rs`: https://docs.rs/copc-rs
- `e57-to-las`: https://docs.rs/e57-to-las

**Conclusion:** the gap is **not** “Rust cannot read point-cloud formats.” The sharper gap is scan-model receipts, conversion-loss accounting, and explicit normalization evidence across file families.

### OpenDocument / ODF substrate
- ODF 1.4 approval note: https://www.oasis-open.org/2025/12/03/oasis-approves-open-document-format-odf-v1-4-standard-marking-20-years-of-interoperable-document-innovation/
- ODF 1.4 family index: https://docs.oasis-open.org/office/OpenDocument/v1.4/os/v1.4-os.html
- ODF 1.4 package part: https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part2-packages/OpenDocument-v1.4-os-part2-packages.html
- ODF 1.4 formula part: https://docs.oasis-open.org/office/OpenDocument/v1.4/os/part4-formula/OpenDocument-v1.4-os-part4-formula.html
- `spreadsheet_ods`: https://docs.rs/spreadsheet_ods
- `calamine`: https://docs.rs/calamine
- `open-document`: https://crates.io/crates/open-document

**Conclusion:** the gap is **not** “Rust cannot touch OpenDocument.” The sharper gap is package/schema/formula receipts, modality-aware conformance reporting, and honest partial-support evidence.


## Added 2026-03-06 (92)

### CWL / Workflow Run RO-Crate / Rust substrate
- CWL standards v1.2.1: https://www.commonwl.org/v1.2/
- CWL user guide (latest describes v1.2): https://www.commonwl.org/user_guide/
- Workflow Run RO-Crate working group: https://www.researchobject.org/workflow-run-crate/
- Provenance Run Crate profile: https://www.researchobject.org/workflow-run-crate/profiles/provenance_run_crate/
- `commonwl`: https://docs.rs/commonwl/latest/commonwl/
- `cwl_engine`: https://docs.rs/cwl_engine/latest/cwl_engine/

**Conclusion:** the gap is **not** “Rust has no CWL substrate.” The sharper gap is pinned workflow/input/output receipts and profile-aware provenance export that survive runner handoff.

### VSS / VISS v2 / Rust substrate
- COVESA Vehicle Signal Specification: https://covesa.global/project/vehicle-signal-specification/
- VISS v2 Core: https://www.w3.org/TR/viss2-core/
- VISS v2 Transport: https://www.w3.org/TR/viss2-transport/
- COVESA VISS project page: https://covesa.global/project/vehicle-information-service-specification/
- `vehicle-signals`: https://docs.rs/vehicle-signals

**Conclusion:** the gap is **not** “there is no common vehicle model/API work.” The sharper gap is tree locks, capability matrices, and replayable request/subscription evidence.

### Exif / XMP / IPTC / Rust substrate
- Exif 3.0 overview: https://cipa.jp/std/documents/e/Exif3.0-Overview_E.pdf
- CIPA standards history: https://www.cipa.jp/e/std/history_sec.html
- ISO 16684-1:2019 (XMP): https://www.iso.org/standard/75163.html
- IPTC Photo Metadata Standard: https://iptc.org/standards/photo-metadata/iptc-standard/
- IPTC mapping guidelines: https://iptc.org/std/photometadata/documentation/mappingguidelines/
- IPTC Photo Metadata 2025.1: https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata-2025.1.html
- `kamadak-exif`: https://docs.rs/kamadak-exif
- `xmp_toolkit`: https://docs.rs/xmp_toolkit
- `rexiv2`: https://docs.rs/rexiv2
- `image` changelog: https://docs.rs/crate/image/latest/source/CHANGES.md

**Conclusion:** the gap is **not** “Rust cannot read image metadata.” The sharper gap is mapping-pack pinning, conflict/loss receipts, and redaction-safe interop evidence across metadata families.

### CNAB / OCI / Rust substrate
- CNAB spec repository: https://github.com/cnabio/cnab-spec
- Compatible registries: https://cnab.io/registries/
- `cnab-to-oci`: https://github.com/cnabio/cnab-to-oci
- `oci-spec`: https://docs.rs/oci-spec
- `oci-client`: https://docs.rs/oci-client

**Conclusion:** the gap is **not** “there is no bundle format or OCI substrate.” The sharper gap is bundle locks, relocation receipts, registry-quirk evidence, and air-gap handoff artifacts.

### CloudEvents / CESQL / CDEvents / Rust substrate
- CloudEvents spec repository: https://github.com/cloudevents/spec
- CESQL v1.0 announcement: https://cloudevents.io/blog/2024-07-15/
- `cloudevents-sdk`: https://docs.rs/cloudevents-sdk
- `cloudevents-sdk-reqwest`: https://docs.rs/cloudevents-sdk-reqwest
- `cdevents-sdk`: https://docs.rs/cdevents-sdk

**Conclusion:** the gap is **not** “Rust lacks event envelopes or transport bindings.” The sharper gap is filter locks, family-mapping receipts, and replayable routing evidence.

## Added 2026-03-06 (93)

### FinOps / cost normalization
- FOCUS home/spec hub: https://focus.finops.org/
- OpenCost docs/spec: https://opencost.io/docs/
- OpenCost specification: https://opencost.io/docs/specification/

### Context brokers / NGSI-LD / model packs
- NGSI-LD official site: https://ngsi-ld.org/
- ETSI NGSI-LD API: https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.09.01_60/gs_CIM009v010901p.pdf
- Orion-LD broker: https://github.com/FIWARE/context.Orion-LD
- Smart Data Models catalogue: https://smart-data-models.github.io/data-models/
- `json-ld` crate docs: https://docs.rs/json-ld

### SDR / RF capture substrate
- SigMF home: https://sigmf.org/
- SigMF repository: https://github.com/sigmf/SigMF
- SoapySDR: https://github.com/pothosware/SoapySDR
- `soapysdr` crate: https://crates.io/crates/soapysdr
- `futuresdr` crate docs: https://docs.rs/futuresdr
- `vita49` crate: https://crates.io/crates/vita49

### GS1 identifier transforms
- GS1 Digital Link: https://www.gs1.org/standards/gs1-digital-link
- GS1 Digital Link URI Syntax: https://ref.gs1.org/standards/digital-link/uri-syntax/
- GS1-Conformant Resolver Standard: https://ref.gs1.org/standards/resolver/
- GS1 EPC Tag Data Standard overview: https://www.gs1.org/standards/tds
- `gs1` crate: https://crates.io/crates/gs1

### Profiling / pprof / Parca / OTel
- `pprof` repository: https://github.com/google/pprof
- `profile.proto`: https://github.com/google/pprof/blob/main/proto/profile.proto
- Parca: https://github.com/parca-dev/parca
- OpenTelemetry profiling announcement: https://opentelemetry.io/blog/2024/profiling/
- OTel `pprof` semantic attributes: https://opentelemetry.io/docs/specs/semconv/registry/attributes/pprof/
- `pprof` crate docs: https://docs.rs/pprof
- `pprof_util` crate docs: https://docs.rs/pprof_util


## Added 2026-03-06 (94)

### Expression / policy substrate
- CEL already has an official language site and spec/conformance repository, and Rust has an active `cel` / `cel-rust` implementation. The gap is **portable environment locking and evaluation receipts**, not “does Rust have CEL at all?”
  - https://cel.dev/overview/cel-overview
  - https://github.com/google/cel-spec
  - https://github.com/cel-rust/cel-rust

### Robotics model-description substrate
- Rust already has `urdf-rs` and `sdformat`, while SDFormat and xacro are real external contracts. The gap is **loss-aware expansion/conversion evidence** across xacro, URDF, SDF, and simulator profiles.
  - https://sdformat.org/
  - https://docs.ros.org/en/rolling/p/xacro/
  - https://docs.rs/urdf-rs
  - https://docs.rs/sdformat

### IMF package-validation substrate
- Rust now has serious IMF parsing/validation substrate in `imferno-core`, and SMPTE’s IMF/OPL standards family is mature. The gap is **normalized finding sets, package locks, and deliverable receipts**.
  - https://www.smpte.org/standards/st2067
  - https://docs.rs/imferno-core/latest/imferno_core/
  - https://lib.rs/crates/imferno-core

### A2A substrate
- Official A2A docs, validator/TCK work, and multiple Rust crates now exist. The gap is **SDK-neutral capability locks and protocol transcripts**, not another “minimal types” crate.
  - https://a2aprotocol.ai/
  - https://github.com/a2aproject/a2a-tck
  - https://docs.rs/a2a
  - https://docs.rs/a2a-rs-core/latest/a2a_rs_core/

### Quantum language / IR substrate
- OpenQASM 3 and QIR both have official homes, while Rust has parser pieces and at least early QIR-facing crates. The gap is **profile-aware lowering evidence** between source programs and IR targets.
  - https://openqasm.com/versions/3.0/intro.html
  - https://www.qir-alliance.org/projects/
  - https://github.com/Qiskit/openqasm3_parser
  - https://crates.io/crates/qir-qis


## Added 2026-03-07 (95)

### Rust specification / witness substrate
- FLS adoption post: https://blog.rust-lang.org/2025/03/26/adopting-the-fls/
- FLS maintenance goal: https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- Rust Reference: https://doc.rust-lang.org/stable/reference/
- `ui_test`: https://docs.rs/ui_test
- `compiletest_rs`: https://crates.io/crates/compiletest_rs

**Conclusion:** the gap is **not** “Rust has no spec text” and not “Rust has no compile-fail harness.” The sharper gap is a **clause-linked witness and drift-receipt layer** that makes spec claims portable, replayable, and reviewable.

### Cargo workspace impact substrate
- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- `guppy`: https://docs.rs/guppy
- `guppy-summaries`: https://docs.rs/guppy-summaries
- `determinator`: https://crates.io/crates/determinator

**Conclusion:** the gap is **not** “Rust lacks workspace graph tooling.” The sharper gap is an **explainable affected-work planner** that turns diffs, graph structure, and policy into shareable CI/review receipts.

### Public compiler IR / analysis substrate
- StableMIR goal: https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- `rustc_public` / project-stable-mir: https://github.com/rust-lang/project-stable-mir
- Rust tooling/extensibility/discoverability commentary: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/

**Conclusion:** the gap is **not** “Rust has no public analysis substrate.” The sharper gap is a **lockfile + fixture + capability-matrix + evidence-bundle layer** that helps tool authors build above `rustc_public` without inventing incompatible private formats.


## Added 2026-03-07 (96)

### Sysroot / build-std substrate
- Cargo unstable `build-std` docs: https://doc.rust-lang.org/cargo/reference/unstable.html#build-std
- Build-std project goal: https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- `cargo-xbuild`: https://crates.io/crates/cargo-xbuild
- `cargo-sysroot`: https://crates.io/crates/cargo-sysroot
- Rust-for-Linux goal notes: https://rust-for-linux.com/rust-project-goals

**Conclusion:** the gap is **not** “nobody can rebuild the sysroot.” The sharper gap is a **portable recipe/lock/receipt layer** for custom sysroot workflows.

### Public/private dependency substrate
- Public/private dependencies project goal: https://rust-lang.github.io/rust-project-goals/2025h1/public-private-dependencies.html
- RFC 3516: https://rust-lang.github.io/rfcs/3516-public-private-dependencies.html
- `cargo-public-api`: https://github.com/cargo-public-api/cargo-public-api
- Cargo issue on suggested fix limitations: https://github.com/rust-lang/cargo/issues/13095

**Conclusion:** the gap is **not** “Rust has no concept of public dependencies” and not “there are no public-API tools.” The sharper gap is a **boundary inspection/migration/explanation layer** that turns the concept into a boring workflow.

### Cargo plumbing substrate
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Rust project goals index / important goals: https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- `cargo_metadata`: https://docs.rs/cargo_metadata
- `cargo-manifest`: https://docs.rs/cargo-manifest

**Conclusion:** the gap is **not** “Cargo has zero machine-readable outputs.” The sharper gap is a **phase-shaped schema and receipt layer** that helps tools survive evolving Cargo plumbing surfaces.

### MC/DC / safety-critical coverage substrate
- Safety-critical Rust flagship: https://rust-lang.github.io/rust-project-goals/2026h1/safety-critical-rust.html
- Coverage options in the unstable book: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/coverage-options.html
- `cargo-llvm-cov`: https://github.com/taiki-e/cargo-llvm-cov
- Rust issue tracking MC/DC: https://github.com/rust-lang/rust/issues/124118

**Conclusion:** the gap is **not** “Rust has no coverage tooling.” The sharper gap is a **decision-map, caveat-index, and evidence-bundle layer** for higher-assurance MC/DC-style workflows.


## Added 2026-03-07 (97)

### Sanitizer workflow substrate
- Sanitizer stabilization goal: https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- Rust sanitizer docs: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- Build-std goal (re instrumented std and whole-program flags): https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- `cargo-llvm-cov`: https://github.com/taiki-e/cargo-llvm-cov

**Conclusion:** the gap is **not** “Rust has no sanitizer support” and not “there are no cargo workflow wrappers in the ecosystem.” The sharper gap is a **profile/suppression/receipt/report-bundle layer** for sanitizer runs.

### Cargo-script / single-file package substrate
- Cargo-script project goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html
- Cargo-script RFC: https://rust-lang.github.io/rfcs/3502-cargo-script.html
- `rust-script`: https://github.com/fornwall/rust-script
- cargo/rust-analyzer design notes: https://hackmd.io/%40rust-cargo-team/HJZ7cw5uxl

**Conclusion:** the gap is **not** “Rust cannot run scripts” and not “no one has tried one-file package tooling.” The sharper gap is a **lock/bundle/doctor/export layer** that makes official single-file packages reproducible and reviewable.

### Target-dir / shared-cache coordination substrate
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo build cache docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo environment variables (`CARGO_TARGET_DIR`, `CARGO_BUILD_BUILD_DIR`, wrappers): https://doc.rust-lang.org/cargo/reference/environment-variables.html
- `sccache`: https://github.com/mozilla/sccache

**Conclusion:** the gap is **not** “Cargo has no cache knobs” and not “there is no shared compilation cache.” The sharper gap is a **lease/receipt/cleanup coordination layer** above those knobs and wrappers.

### Multi-backend workflow substrate
- Cranelift backend goal: https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html
- `rustc_codegen_cranelift`: https://github.com/rust-lang/rustc_codegen_cranelift
- `rustc_codegen_gcc`: https://github.com/rust-lang/rustc_codegen_gcc
- Rust project goals overview (backend diversity / compilation initiative context): https://rust-lang.github.io/rust-project-goals/

**Conclusion:** the gap is **not** “Rust lacks alternative backends.” The sharper gap is a **matrix/diff/fallback artifact layer** that helps projects use backend diversity intentionally.


## Added 2026-03-07 (98)

### Relink / interface-diff substrate
- Relink don't rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- `cargo-public-api`: https://github.com/cargo-public-api/cargo-public-api
- `cargo-semver-checks`: https://github.com/obi1kenobi/cargo-semver-checks
- cargo semver-checks goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html

**Conclusion:** the gap is **not** “Rust has no public-surface diff tooling.” The sharper gap is a **private-change / interface-change witness layer** that ordinary teams can review during day-to-day development.

### Reflection / comptime substrate
- Reflection and comptime goal: https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- `bevy_reflect`: https://docs.rs/bevy_reflect/latest/bevy_reflect/
- Facet project: https://facet.rs/
- `facet-reflect`: https://crates.io/crates/facet-reflect

**Conclusion:** the gap is **not** “Rust lacks any reflection-like libraries.” The sharper gap is a **schema-IR / bridge / migration-receipt layer** between today's derive/runtime reflection and tomorrow's compile-time substrate.

### Projection / reborrow / pinning substrate
- Field projections goal: https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
- Reborrow traits goal: https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- `pin-project`: https://crates.io/crates/pin-project
- `miri`: https://github.com/rust-lang/miri
- `pin-init`: https://github.com/Rust-for-Linux/pin-init

**Conclusion:** the gap is **not** “Rust has no projection or pinning helpers.” The sharper gap is a **shared contract/fixture/receipt kit** for testing advanced pointer invariants and projection semantics.

### Rust/C++ boundary substrate
- C++/Rust interop problem space mapping: https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- `cxx`: https://cxx.rs/
- `autocxx`: https://google.github.io/autocxx/
- `bindgen`: https://github.com/rust-lang/rust-bindgen
- `cbindgen`: https://github.com/mozilla/cbindgen
- In-place initialization goal: https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html

**Conclusion:** the gap is **not** “Rust has no C++ interop tools.” The sharper gap is a **boundary receipt / ownership matrix / replay bundle layer** for mixed-language edges.


## Added 2026-03-07 (99)

### Trait-solver / compile-fail substrate
- Next-generation trait solver goal: https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
- Rust project goals overview (stabilization context): https://rust-lang.github.io/rust-project-goals/
- `ui_test`: https://docs.rs/ui_test
- `trybuild`: https://crates.io/crates/trybuild
- `compiletest_rs`: https://crates.io/crates/compiletest_rs

**Conclusion:** the gap is **not** “Rust has no compile-fail harnesses” and not “the trait solver transition is only an upstream compiler problem.” The sharper gap is a **solver-drift witness layer** above existing harnesses.

### Optional namespace substrate
- RFC 3243: https://rust-lang.github.io/rfcs/3243-packages-as-optional-namespaces.html
- Open namespaces goal: https://rust-lang.github.io/rust-project-goals/2025h2/open-namespaces.html
- Cargo tracking issue: https://github.com/rust-lang/cargo/issues/13576
- crates.io tracking issue: https://github.com/rust-lang/crates.io/issues/8292
- Cargo development-cycle note: https://blog.rust-lang.org/inside-rust/2024/03/26/this-development-cycle-in-cargo-1.78/

**Conclusion:** the gap is **not** “Rust has no namespace design” and not “there is no implementation work.” The sharper gap is a **migration-plan / alias-receipt / import-diff layer** for crate families.

### Rust-for-Linux stable-readiness substrate
- Rust-for-Linux tooling goal (2025H1): https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Rust-for-Linux stable language goal: https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-language.html
- Rust-for-Linux stable compiler goal: https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-compiler.html
- Kernel quick start: https://docs.kernel.org/rust/quick-start.html
- Rust-for-Linux version policy: https://rust-for-linux.com/rust-version-policy
- Rust-for-Linux unstable features: https://rust-for-linux.com/unstable-features

**Conclusion:** the gap is **not** “Rust-for-Linux lacks documentation, policy, or goal work.” The sharper gap is a **stable-readiness profile + rustavailable receipt + waiver bundle** for maintainers.

### Const capability substrate
- Const traits goal: https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `rustdoc-types`: https://docs.rs/crate/rustdoc-types/latest
- `rustdoc-json`: https://crates.io/crates/rustdoc-json
- `cargo-public-api`: https://docs.rs/crate/cargo-public-api/latest
- Rustdoc unstable features: https://doc.rust-lang.org/rustdoc/unstable-features.html

**Conclusion:** the gap is **not** “Rust has no public-API extraction” and not “const capability is purely a language-team concern.” The sharper gap is a **const-surface ledger / diff / receipt layer**.


## Added 2026-03-07 (100)

### Borrow-check transition substrate
- Polonius goal: https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `ui_test`: https://docs.rs/ui_test
- `trybuild`: https://crates.io/crates/trybuild
- `compiletest_rs`: https://crates.io/crates/compiletest_rs

**Conclusion:** the gap is **not** “Rust lacks compile-fail harnesses” and not “Polonius is only an upstream compiler concern.” The sharper gap is a **borrow-check transition witness layer** above existing harnesses.

### In-place initialization substrate
- In-place initialization goal: https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- Pin ergonomics goal: https://rust-lang.github.io/rust-project-goals/2026/pin-ergonomics.html
- `pin-init`: https://docs.rs/pin-init
- Crubit `Ctor` support: https://github.com/google/crubit/blob/main/support/ctor.rs

**Conclusion:** the gap is **not** “Rust has no pinned-init crates” and not “future in-place init must wait for the language.” The sharper gap is an **address-stability / fallible-init receipt and adoption layer**.

### Ergonomic ref-counting substrate
- Ergonomic ref-counting in 2026: https://rust-lang.github.io/rust-project-goals/2026/ergonomic-rc.html
- Ergonomic ref-counting RFC decision and preview: https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
- Initial ergonomic ref-counting goal: https://rust-lang.github.io/rust-project-goals/2024h2/ergonomic-rc.html

**Conclusion:** the gap is **not** “Rust has no `Rc` or `Arc`” and not “the language-team roadmap already gives applications a migration workflow.” The sharper gap is a **capture audit / aliasing ledger / migration receipt** layer.

### Trait hierarchy evolution substrate
- Evolving trait hierarchies goal: https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- `Receiver` docs: https://doc.rust-lang.org/std/ops/trait.Receiver.html
- `tower::Service`: https://docs.rs/tower/latest/tower/trait.Service.html
- Implementable trait aliases design meeting: https://hackmd.io/%40rust-lang-team/Syx0GQUMT

**Conclusion:** the gap is **not** “trait evolution is purely upstream design work” and not “library authors can just rewrite the trait.” The sharper gap is a **semver-aware hierarchy planner with impl-closure and receiver-capability ledgers**.


## Added 2026-03-07 (101)

### Parallel front-end substrate
- Parallel front-end goal: https://rust-lang.github.io/rust-project-goals/2025h2/parallel-front-end.html
- Tracking issue: https://github.com/rust-lang/rust/issues/113349
- `rustc-perf`: https://github.com/rust-lang/rustc-perf
- rustc-perf parallel-front-end issue: https://github.com/rust-lang/rustc-perf/issues/2068

**Conclusion:** the gap is **not** “Rust has no parallel-front-end work” and not “there is no performance tooling.” The sharper gap is a **maintainer-facing parity and repro receipt layer** above compiler-team tooling.

### Conditional-availability substrate
- `doc_cfg` stabilization goal: https://rust-lang.github.io/rust-project-goals/2025h2/rustdoc-doc-cfg.html
- RFC 3631: https://rust-lang.github.io/rfcs/3631-rustdoc-cfgs-handling.html
- rustdoc advanced features (`cfg(doc)` visibility, not passed to doctests): https://doc.rust-lang.org/rustdoc/advanced-features.html
- rustdoc unstable features (`doc(auto_cfg)` default and hide/show): https://doc.rust-lang.org/rustdoc/unstable-features.html
- docs.rs builds (`cfg(docsrs)` scope, sandbox, hosted-vs-local notes): https://docs.rs/about/builds
- docs.rs metadata (features, targets, custom `rustc` / `rustdoc` args): https://docs.rs/about/metadata
- docs.rs rustdoc JSON: https://docs.rs/about/rustdoc-json
- Cargo build scripts (`cargo::rustc-cfg`, `cargo::rustc-check-cfg`): https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo features: https://doc.rust-lang.org/cargo/reference/features.html
- `rustdoc-json`: https://crates.io/crates/rustdoc-json
- `doc-cfg`: https://docs.rs/doc-cfg

**Conclusion:** the gap is **not** “Rust cannot show conditional availability” and not “there is no machine-readable substrate.” The sharper gap is a **feature/target availability ledger and diff layer** for release review, especially one that keeps slice witnesses, gate normalization, and re-export lineage separate.

### Externally-implementable-item substrate
- EII goal: https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- Runtime attributes reference: https://doc.rust-lang.org/reference/runtime.html
- Attributes reference: https://doc.rust-lang.org/reference/attributes.html
- `log::set_logger`: https://docs.rs/log/latest/log/fn.set_logger.html

**Conclusion:** the gap is **not** “Rust lacks customization points” and not “there is no precedent for global override behavior.” The sharper gap is a **semver-aware adoption/documentation/receipt kit** for future EII-style customization surfaces.

### Safety-contract substrate
- std contracts goal: https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- `verify-rust-std`: https://github.com/model-checking/verify-rust-std
- Kani contracts: https://model-checking.github.io/kani/reference/experimental/contracts.html
- Creusot: https://github.com/creusot-rs/creusot
- Flux: https://flux-rs.github.io/

**Conclusion:** the gap is **not** “Rust has no contract work” and not “there are no downstream verification tools.” The sharper gap is a **contract extraction/consumption/diff/runtime-receipt layer** that multiple tools and teams can share.



## Added 2026-03-07 (102)

### ABI-coherence substrate
- RFC 3716 target modifiers: https://rust-lang.github.io/rfcs/3716-target-modifiers.html
- Rust-for-Linux tooling goal: https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- build-std goal: https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Tracking issue for ABI-altering `-C` flags: https://github.com/rust-lang/rust/issues/131837
- Sanitizer docs: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html

**Conclusion:** the gap is **not** “Rust has no ABI-flag work” and not “there are no unstable flags or sysroot rebuild workflows.” The sharper gap is a **whole-program coherence profile + exemption ledger + sysroot receipt layer**.

### Doctest-extraction substrate
- Rust-for-Linux tooling goal: https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Tracking issue for `--output-format=doctest`: https://github.com/rust-lang/rust/issues/134529
- rustdoc unstable doctest extraction docs: https://doc.rust-lang.org/rustdoc/unstable-features.html#doctest
- Tracking issue for doctests in one binary: https://github.com/rust-lang/rust/issues/124853
- rustdoc documentation tests book chapter: https://doc.rust-lang.org/rustdoc/documentation-tests.html

**Conclusion:** the gap is **not** “Rust cannot run documentation tests” and not “rustdoc exposes no machine-readable doctest surface.” The sharper gap is a **manifest / rewrite / runner-receipt layer** for extracted doctest workflows.

### Formality-bridge substrate
- a-mir-formality goal: https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- `rust-lang/a-mir-formality`: https://github.com/rust-lang/a-mir-formality
- `minirust/minirust`: https://github.com/minirust/minirust
- const-trait goal: https://rust-lang.github.io/rust-project-goals/2025h1/const-trait.html

**Conclusion:** the gap is **not** “Rust lacks any formal-model work” and not “there is nowhere to put model examples.” The sharper gap is a **portable counterexample / assumptions / reduction bundle** for rustc-versus-model validation.

### External-toolchain-handshake substrate
- Rust-for-Linux tooling goal: https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Cargo build-cache dep-info docs: https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo unstable `binary-dep-depinfo`: https://doc.rust-lang.org/cargo/reference/unstable.html#binary-dep-depinfo
- Unstable `crate-attr`: https://doc.rust-lang.org/beta/unstable-book/compiler-flags/crate-attr.html
- Cargo unstable `rustdoc-depinfo`: https://doc.rust-lang.org/cargo/reference/unstable.html#rustdoc-depinfo

**Conclusion:** the gap is **not** “Rust has no dep-info or source-pure orchestration knobs.” The sharper gap is a **single handshake manifest and injected-attribute receipt layer** for non-Cargo orchestrators.


## Added 2026-03-07 (103)

### Async-dyn substrate
- Async 2025H1 goal: https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Async fn in dyn trait explainer: https://rust-lang.github.io/async-fundamentals-initiative/explainer/async_fn_in_dyn_trait.html
- `async-trait`: https://crates.io/crates/async-trait
- `trait-variant`: https://docs.rs/trait-variant
- `dynosaur`: https://docs.rs/dynosaur

**Conclusion:** the gap is **not** “Rust has no async trait-object story” and not “there are no proc-macro bridges.” The sharper gap is a **dispatch-recipe / migration-receipt layer** for teams moving between `async-trait`, `trait-variant`, `dynosaur`, and future native async dyn support.

### Clippy safety-profile substrate
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Rust-for-Linux tooling goal (`.clippy.toml` / `CLIPPY_CONF_DIR`): https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- Clippy configuration docs: https://doc.rust-lang.org/clippy/configuration.html
- Clippy lint groups docs: https://doc.rust-lang.org/stable/clippy/lints.html
- `cargo-hack`: https://docs.rs/cargo-hack/latest/cargo_hack/

**Conclusion:** the gap is **not** “Clippy lacks configuration” and not “organizations cannot script lint matrices.” The sharper gap is a **versioned lint profile + waiver ledger + feature-matrix receipt layer** that teams can review and exchange.

### Unsafe-field substrate
- Unsafe fields goal: https://rust-lang.github.io/rust-project-goals/2025h1/unsafe-fields.html
- std contracts goal: https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
- The Scope of Unsafe: https://www.ralfj.de/blog/2016/01/09/the-scope-of-unsafe.html
- Miri: https://github.com/rust-lang/miri

**Conclusion:** the gap is **not** “Rust lacks awareness of field invariants” and not “unsafe review is solved by Miri or contracts.” The sharper gap is a **field-level invariant ledger and mutation witness layer** for maintainers.

### Edition-migration substrate
- Transitioning an existing project to a new edition: https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
- Advanced migrations: https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Rust 1.85.0 / Rust 2024 release: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Allowed-by-default lints: https://doc.rust-lang.org/rustc/lints/listing/allowed-by-default.html
- Rust 2024 Edition project goal: https://rust-lang.github.io/rust-project-goals/2024h2/Rust-2024-Edition.html

**Conclusion:** the gap is **not** “Rust has no edition migration tooling” and not “`cargo fix --edition` makes rehearsals unnecessary.” The sharper gap is a **lint-ledger / fix-preview / macro-risk witness layer** for staged workspace migration.


## Added 2026-03-07 (104)

### Crate-slicing substrate
- Crate slicing goal: https://rust-lang.github.io/rust-project-goals/2026/crate-slicing.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `cargo-slicer`: https://github.com/yijunyu/cargo-slicer
- crates.io entry for `cargo-slicer`: https://crates.io/crates/cargo-slicer
- Parallel rustc blog: https://blog.rust-lang.org/2023/11/09/parallel-rustc.html

**Conclusion:** the gap is **not** “there is no slicing prototype” and not “the research prototype is already a boring production workflow.” The sharper gap is a **slice-eligibility / fallback / predicted-benefit receipt layer** above prototype tools and future rustc-native work.

### Libtest-JSON substrate
- Libtest JSON goal: https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- RFC 3558 libtest JSON: https://rust-lang.github.io/rfcs/3558-libtest-json.html
- `cargo-nextest`: https://crates.io/crates/cargo-nextest
- nextest libtest JSON docs: https://nexte.st/docs/machine-readable/libtest-json/
- `libtest-mimic`: https://crates.io/crates/libtest-mimic

**Conclusion:** the gap is **not** “Rust has no machine-readable test output discussion” and not “nextest already makes the interop layer unnecessary.” The sharper gap is a **schema-lock / suite-aware receipt / projection bundle layer** that Cargo, nextest, and custom harnesses can all exchange.

### Sized-hierarchy / extern-type substrate
- Rust in 2026 flagships / sized hierarchy milestone: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Unstable book: `sized_hierarchy`: https://doc.rust-lang.org/beta/unstable-book/language-features/sized-hierarchy.html
- Tracking issue #144404: https://github.com/rust-lang/rust/issues/144404
- RFC 1861 extern types: https://rust-lang.github.io/rfcs/1861-extern-types.html
- 2025H2 project goals blog: https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/

**Conclusion:** the gap is **not** “Rust has no extern-type story” and not “binding generators already solve refined sizedness adoption.” The sharper gap is a **sizedness-surface audit / opaque-type readiness receipt layer** for maintainers.

### BorrowSanitizer substrate
- BorrowSanitizer goal: https://rust-lang.github.io/rust-project-goals/2026/borrowsanitizer.html
- BorrowSanitizer site: https://borrowsanitizer.com/
- BorrowSanitizer GitHub: https://github.com/borrowSanitizer/bsan
- RFC 3559 Rust has provenance: https://rust-lang.github.io/rfcs/3559-rust-has-provenance.html
- Miri: https://github.com/rust-lang/miri

**Conclusion:** the gap is **not** “Rust lacks aliasing-model tooling” and not “BorrowSanitizer or Miri already provide a maintainer-grade workflow.” The sharper gap is a **profile / FFI-boundary / minimized finding bundle layer** for ordinary unsafe-code review.

## Added 2026-03-07 (105)

### Python wheel / ABI / free-threading substrate
- PyO3 building and distribution: https://pyo3.rs/main/building-and-distribution
- PyO3 multiple Python versions / `abi3`: https://pyo3.rs/main/building-and-distribution/multiple-python-versions
- maturin distribution / cross-compilation: https://www.maturin.rs/distribution.html
- Python Stable ABI docs: https://docs.python.org/3/c-api/stable.html
- Python free-threaded extension docs: https://docs.python.org/3/howto/free-threading-extensions.html
- PyO3 migration guide (free-threaded support): https://pyo3.rs/v0.28.2/migration

**Conclusion:** the gap is **not** “Rust lacks Python bindings” and not “maturin already makes release policy boring.” The sharper gap is a **wheel-matrix / ABI-policy / free-threading readiness receipt layer** above PyO3 and maturin.

### Apple XCFramework / SwiftPM substrate
- UniFFI Swift Xcode integration: https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- UniFFI Swift bindings overview: https://mozilla.github.io/uniffi-rs/latest/swift/overview.html
- UniFFI docs.rs (`cargo swift` adjacency): https://docs.rs/crate/uniffi/latest
- `xcframework` crate docs: https://docs.rs/xcframework/latest/xcframework/
- Apple XCFramework bundle docs: https://developer.apple.com/documentation/xcode/creating-a-multi-platform-binary-framework-bundle
- Apple Swift-package binary distribution docs: https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
- Apple XCFramework origin verification docs: https://developer.apple.com/documentation/xcode/verifying-the-origin-of-your-xcframeworks
- Apple privacy manifest docs for third-party SDKs: https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk?language=objc

**Conclusion:** the gap is **not** “Rust has no Swift bindings” and not “an XCFramework helper crate already solves Apple distribution.” The sharper gap is a **slice-manifest / SwiftPM checksum / privacy-manifest / origin-verification receipt layer** for shipping Rust-built Apple SDKs.


## Added 2026-03-07 (106)

### Cargo resolver-explanation substrate
- Cargo dependency resolution docs: https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo features docs: https://doc.rust-lang.org/cargo/reference/features.html
- `cargo tree` docs: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- `cargo metadata` docs: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo unstable feature-unification / `--unit-graph` docs: https://doc.rust-lang.org/cargo/reference/unstable.html
- `guppy`: https://docs.rs/guppy/latest/guppy/
- `cargo hakari`: https://docs.rs/cargo-hakari/latest/cargo_hakari/
- dependency-spec docs for renamed dependencies: feature names take after the local dependency name, not the original package name, and transitive dependency-feature forwarding does too. https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- registry-index docs: renamed dependencies are represented differently across publish API / index / `cargo metadata` fields (`name`, `package`, `rename`, `explicit_name_in_toml`). https://doc.rust-lang.org/cargo/reference/registry-index.html
- Cargo issue #12546: inherited workspace dependencies still cannot simply be renamed from the member side. https://github.com/rust-lang/cargo/issues/12546
- Cargo issue #14365: renamed + feature-gated dependencies can still go missing in private-registry workflows. https://github.com/rust-lang/cargo/issues/14365
- Cargo issue #14399: renamed crates.io dependencies can still fail verification when published through another registry. https://github.com/rust-lang/cargo/issues/14399

**Conclusion:** the gap is **not** “Cargo exposes no resolver information,” not “`cargo tree` already makes feature-resolution surprises boring,” and not “graph-query crates already hand maintainers a support-grade why-bundle.” The sharper gap is a **cause-chain / version-choice / duplicate-build / diffable explanation layer** above today's resolver, tree, metadata, and graph-simulation substrate, with explicit **dependency-identity / rename-surface truth** when names differ by context.

### Cargo rebuild-explanation substrate
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust compiler performance survey 2025 results: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Relink don't Rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo build docs (`--timings`): https://doc.rust-lang.org/cargo/commands/cargo-build.html
- This development-cycle in Cargo 1.84: https://blog.rust-lang.org/inside-rust/2024/12/13/this-development-cycle-in-cargo-1.84/
- Cargo issue #2904 (“Provide better diagnostics for why crates are rebuilt”): https://github.com/rust-lang/cargo/issues/2904
- Cargo issue #15529 (`cargo check` via rust-analyzer forcing full rebuilds): https://github.com/rust-lang/cargo/issues/15529

**Conclusion:** the gap is **not** “Cargo has no timing or fingerprint surfaces” and not “historical build analysis already solves ordinary rebuild mysteries.” The sharper gap is a **per-run rebuild-cause / fingerprint-delta / cache-conflict receipt layer** that teams can exchange during normal debugging and CI review.


## 2026-03-07 additions (packaging / build-output handoff)
- Cargo package docs: `cargo package` rewrites and normalizes `Cargo.toml`, includes `Cargo.lock`, includes `.cargo_vcs_info.json`, flattens symlinks, and uses include/exclude rules — but the same docs also say `.cargo_vcs_info.json` is only a best-effort snapshot and not verified provenance. Source: https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Publishing docs: crates.io recommends `cargo publish --dry-run` / `cargo package`, manual inspection of `target/package`, checking `cargo package --list`, and watching the 10MB `.crate` size limit. Source: https://doc.rust-lang.org/cargo/reference/publishing.html
- Release note: `cargo publish` should not be relied on as the place `.crate` tarballs persist as final artifacts; use `cargo package` for that surface. Source: https://doc.rust-lang.org/beta/releases.html
- External-tools JSON: Cargo can emit produced artifacts and build-script results as JSON for tooling, but consumers still need to parse line-oriented output and defend against dirty stdout. Source: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Unstable `artifact-dir`: Cargo explicitly says exact filenames can be tricky and that `--artifact-dir` exists to make artifacts easier to access, but the feature remains unstable. Source: https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-dist`: already generates machine-readable manifests, but it is release/distribution tooling rather than a small general-purpose build handoff layer. Source: https://axodotdev.github.io/cargo-dist/
- Cargo unstable SBOM sidecars: generated SBOM precursor files show that sidecar artifact conventions are emerging around executable/linkable outputs. Source: https://doc.rust-lang.org/beta/cargo/reference/unstable.html

**Conclusion:** the gaps are **not** “Cargo cannot package crates” and **not** “Cargo cannot emit build outputs for tools.” The sharper opportunities are a **package-review bundle** and an **artifact-handoff manifest** that make those surfaces reviewable, diffable, and exchangeable.


## Added 2026-03-07 (108)
- `cargo-docs-rs` — runs `cargo rustdoc` with the options docs.rs would use, taking `[package.metadata.docs.rs]` into account; useful preflight substrate, but not a review/diff/issue-bundle workflow. https://crates.io/crates/cargo-docs-rs
- docs.rs build docs — current nightly compiler version, sandbox/resource limits, `docsrs`/`DOCS_RS` behavior, cross-compilation notes, and the explicit note that `cargo docs-rs` can catch many issues without perfectly replicating the hosted environment. https://docs.rs/about/builds
- docs.rs metadata docs — stable user-facing surface for `[package.metadata.docs.rs]` target/feature/rustdoc/cargo customization. https://docs.rs/about/metadata
- Cargo manifest `[lints]` — real per-package lint-policy substrate, including levels and priorities. https://doc.rust-lang.org/cargo/reference/manifest.html
- Cargo `workspace.lints` — real stable workspace lint inheritance, respected as of Rust 1.74. https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo unstable `[lints.cargo]` — emerging substrate for Cargo-emitted lint policy under `-Zcargo-lints`. https://doc.rust-lang.org/cargo/reference/unstable.html


## Added 2026-03-07 (109)

### Cargo config-layer substrate
- Cargo configuration reference: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features (`cargo config`, unstable table): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 development-cycle notes (`config-include` stabilization): https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

**Conclusion:** the gap is **not** “Cargo has no configuration model” and not “an unstable `cargo config get` command already makes configuration debugging boring.” The sharper gap is an **effective-config / origin-trace / redacted support bundle layer** above Cargo’s real configuration substrate.

### Rustdoc mergeable cross-crate docs substrate
- RFC 3662 mergeable cross-crate info: https://rust-lang.github.io/rfcs/3662-mergeable-rustdoc-cross-crate-info.html
- rustdoc unstable merge flags: https://doc.rust-lang.org/rustdoc/unstable-features.html
- Cargo unstable `-Z rustdoc-mergeable-info`: https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo doc` docs: https://doc.rust-lang.org/cargo/commands/cargo-doc.html

**Conclusion:** the gap is **not** “Rust has no cross-crate docs strategy” and not “mergeable-info substrate already gives maintainers a boring workflow.” The sharper gap is a **`doc.parts` manifest / compatibility / finalize-receipt layer** for CI, large workspaces, and non-Cargo build systems.


## Added 2026-03-07 (110)

### Rustdoc coverage / docs-analysis substrate
- rustdoc unstable features: `--show-coverage` can emit JSON, can write to stdout, and can be combined with `--output-format json` coverage output. https://doc.rust-lang.org/rustdoc/unstable-features.html
- `cargo rustdoc` docs: nightly `--output-format json` exists and Cargo still treats it as experimental. https://doc.rust-lang.org/cargo/commands/cargo-rustdoc.html
- `rustdoc_json_types`: public API for rustdoc JSON output. https://doc.rust-lang.org/nightly/nightly-rustc/rustdoc_json_types/
- RFC 2963: rustdoc JSON exists so other tools can build different front-ends and analysis workflows above rustdoc’s semantic data. https://rust-lang.github.io/rfcs/2963-rustdoc-json.html

**Conclusion:** the gap is **not** “Rust lacks docs tooling primitives” and not “coverage JSON already makes docs maintenance boring.” The sharper gap is an **API-aware docs debt / regression / review bundle** above coverage and rustdoc JSON substrate.

### Publish-surface join substrate
- Publishing docs: `cargo publish` packages, extracts, verifies compile, uploads, and recommends `cargo publish --dry-run` / `cargo package` beforehand. https://doc.rust-lang.org/cargo/reference/publishing.html
- Registry index docs: per-version entries include the `.crate` SHA256 checksum (`cksum`), and registries can expose download/API configuration. https://doc.rust-lang.org/cargo/reference/registry-index.html
- RFC 3691 trusted publishing: OIDC-based short-lived tokens, restricted workflow claims, one-time trusted publisher configuration, and explicit CI identity semantics. https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
- crates.io development update (2026-01-21): GitLab support for trusted publishing, trusted-publishing-only mode, and `pubtime` added to index entries. https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

**Conclusion:** the gap is **not** “Rust has no secure publish substrate” and not “registry checksum/trusted-publishing data already forms a maintainer-grade receipt.” The sharper gap is a **local-package / registry-confirmation / publish-identity join layer** for post-publish audits and release history.



## Added 2026-03-07 (111)

### Future-incompat reporting substrate
- Cargo future incompatibility report reference: Cargo checks future-incompatible warnings in all dependencies and records enough data that a full report can be revisited later. https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- `cargo report` docs: Cargo has a dedicated `cargo report future-incompatibilities` command family, so the raw reporting surface is now explicit rather than purely ephemeral. https://doc.rust-lang.org/cargo/commands/cargo-report.html
- Cargo configuration reference: `[future-incompat-report]` is a real config surface, but it is still about notification frequency rather than maintainer-grade ownership, waiver, or remediation workflow. https://doc.rust-lang.org/cargo/reference/config.html

**Conclusion:** the gap is **not** “Cargo cannot detect or re-display future incompatibilities.” The sharper gap is an **owner / waiver / remediation ledger layer** above Cargo’s built-in report substrate.

### Artifact-sidecar substrate
- Cargo external tools JSON: primary artifacts can already be identified for external tooling, which gives the base object that sidecars need to attach to. https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo unstable features: `--artifact-dir` exists because exact artifact access is awkward, and `-Z sbom` emits artifact-adjacent sidecars. https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo unstable SBOM precursor docs: `<artifact>.cargo-sbom.json` sidecars and `CARGO_SBOM_PATH` show that Cargo is already growing sidecar-oriented output conventions. https://doc.rust-lang.org/beta/cargo/reference/unstable.html

**Conclusion:** the gap is **not** “Cargo has no machine-readable artifact surface” and not “SBOM precursor files already provide a boring attachment contract.” The sharper gap is an **artifact-to-sidecar attachment / schema / diff layer** above that substrate.



## Added 2026-03-07 (112)

### Cargo global-cache GC substrate
- 2025 State of Rust survey results: resource usage (including storage usage) remains a major productivity pain signal. https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo changelog: automatic global-cache garbage collection was stabilized in Rust 1.88. https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo configuration reference: `cache.auto-clean-frequency` is a real stable config surface. https://doc.rust-lang.org/cargo/reference/config.html
- Cargo unstable features: nightly manual `gc` controls expose explicit age/size cleanup parameters. https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-cache`: existing Cargo-home size/cleanup tool showing real demand. https://crates.io/crates/cargo-cache
- `cargo-sweep`: useful `target/` cleanup tool, but aimed at build artifacts rather than Cargo-home policy. https://crates.io/crates/cargo-sweep

**Conclusion:** the gap is **not** “Cargo cannot clean global caches” and not “existing cleanup tools already make Cargo-home storage governance boring.” The sharper gap is a **cache inventory / dry-run cleanup / exemption / receipt layer** above Cargo’s GC substrate.

### Cross-target doctest runner substrate
- rustdoc command-line arguments: `--test-runtool` and `--test-runtool-arg` are stable runner hooks for doctests. https://doc.rust-lang.org/rustdoc/command-line-arguments.html
- Rust release notes: target-specific `ignore-*` attributes for doctests and stable runner flags are real stable surface now. https://doc.rust-lang.org/beta/releases.html
- Cargo unstable docs: doctest cross-compiling now honors `--target` starting in Rust 1.89. https://doc.rust-lang.org/cargo/reference/unstable.html
- February 2025 project goals update: rustdoc extraction support for special-environment doctests was important enough for Rust-for-Linux integration work. https://blog.rust-lang.org/2025/03/03/Project-Goals-Feb-Update/

**Conclusion:** the gap is **not** “Rust cannot run doctests under special environments” and not “stable runner flags already make cross-target docs maintenance boring.” The sharper gap is a **runner-profile / target-matrix / ignore-audit / execution-receipt layer** above that substrate.


## Added 2026-03-07 (113)

### Foreign-SDK release substrate
- PyO3 building and distribution guide: https://pyo3.rs/main/building-and-distribution
- PyO3 multiple Python versions / `abi3` / runtime-version caveats: https://pyo3.rs/main/building-and-distribution/multiple-python-versions
- maturin distribution guide (manylinux, bundling, debug info): https://www.maturin.rs/distribution.html
- UniFFI Swift/Xcode integration: https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- Apple binary frameworks as Swift packages: https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
- SwiftPM binary-target checksum docs: https://developer.apple.com/documentation/PackageDescription/Target/checksum
- Apple privacy manifest files: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files

**Conclusion:** the gap is **not** “Rust cannot build Python wheels or Apple SDK bundles.” The sharper gap is a **consumer-promise snapshot / drift / impact receipt layer** above those artifact builders.

### Public-API release-review substrate
- cargo-semver-checks integration goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- cargo-public-api: https://github.com/cargo-public-api/cargo-public-api
- Cargo SemVer guidance: https://doc.rust-lang.org/cargo/reference/semver.html
- 2026 flagship goal for public/private dependencies: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- RFC 3516 public/private dependencies: https://rust-lang.github.io/rfcs/3516-public-private-dependencies.html
- rustdoc coverage JSON / unstable features: https://doc.rust-lang.org/rustdoc/unstable-features.html
- Cargo changelog (`cargo doc --message-format=json`): https://doc.rust-lang.org/cargo/CHANGELOG.html

**Conclusion:** the gap is **not** “Rust lacks API diffing” and not “public-surface release review is already boring.” The sharper gap is a **joined readiness bundle** above semver checks, public-API diffs, public-dependency reasoning, and docs-surface metrics.


## Added 2026-03-07 (114)

### Toolchain/target support substrate
- rustup override/toolchain-file docs: override precedence, `rust-toolchain.toml`, requested components/targets/profile, and proximity rules are already documented. https://rust-lang.github.io/rustup/overrides.html
- rustup profiles/components/targets docs: profiles (`minimal`/`default`/`complete`), optional components, and extra targets are already real install substrate. https://rust-lang.github.io/rustup/concepts/profiles.html ; https://rust-lang.github.io/rustup/concepts/components.html ; https://rust-lang.github.io/rustup/cross-compilation.html
- docs.rs metadata/build docs: crates can already declare docs.rs targets/features/rustdoc args, and docs.rs explicitly says local `cargo docs-rs` testing is only approximate. https://docs.rs/about/metadata ; https://docs.rs/about/builds
- target-tier policy and MSRV resolver RFCs show that support/toolchain policy is already an explicit concern in Rust’s official documents. https://rust-lang.github.io/rfcs/2803-target-tier-policy.html ; https://rust-lang.github.io/rfcs/3537-msrv-resolver.html

**Conclusion:** the gap is **not** “Rust cannot describe toolchains, targets, or docs.rs support.” The sharper gap is a **joined support contract / environment receipt / drift bundle** above those surfaces.

### Multi-verifier campaign substrate
- Miri already runs binaries and test suites to detect UB in executed code. https://github.com/rust-lang/miri
- Kani already provides model checking, proof harnesses, contracts, and explicit feature-support docs. https://model-checking.github.io/kani/ ; https://model-checking.github.io/kani/reference/experimental/contracts.html
- Creusot and Prusti already expose deductive/contract verification workflows. https://creusot-rs.github.io/creusot/guide/ ; https://viperproject.github.io/prusti-dev/user-guide/verify/summary.html
- Flux already exposes a refinement-type checking surface for Rust. https://flux-rs.github.io/
- BorrowSanitizer-related codegen work shows Rust is also investing in practical runtime aliasing instrumentation. https://rust-lang.github.io/rust-project-goals/2025h2/codegen_retags.html

**Conclusion:** the gap is **not** “Rust lacks verification engines.” The sharper gap is a **campaign-level obligation / trust / evidence / drift workbench** above heterogeneous verifiers.


## Added 2026-03-07 (115)

### Debuggability substrate
- 2025 State of Rust survey results: debugging remains among the top productivity problems, even after slipping from 2nd to 4th place. https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo profiles: debug info levels, `split-debuginfo`, and `strip` are already real profile surfaces. https://doc.rust-lang.org/cargo/reference/profiles.html
- `rustc` codegen options: `split-debuginfo` behavior is platform-specific and `strip=debuginfo` can leave backtraces mostly intact while making gdb/lldb ineffective. https://doc.rust-lang.org/rustc/codegen-options/index.html
- Rust reference: `#[debugger_visualizer]` can embed NatVis or GDB visualizer files into debug info. https://doc.rust-lang.org/reference/attributes/debugger.html
- Cargo unstable docs: `trim-paths` is turning path sanitization in objects/diagnostics/macros into a more explicit support/release surface. https://doc.rust-lang.org/cargo/reference/unstable.html

**Conclusion:** the gap is **not** “Rust has no debuginfo or debugger hooks.” The sharper gap is a **support-posture / symbol-sidecar / visualizer / drift bundle** above those surfaces.

### Foreign-SDK consumer-diagnosis substrate
- Python packaging compatibility tags define how installers reason about interpreter/ABI/platform compatibility. https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
- Python wheel format is already a formal archive/install surface. https://packaging.python.org/en/latest/specifications/binary-distribution-format/
- PyO3 `abi3` docs explain the limited API path for multi-version wheels. https://pyo3.rs/v0.28.2/features
- PyO3 free-threaded docs explain that the free-threaded build uses a new ABI and currently has no equivalent limited API, so version-specific free-threaded wheels are needed. https://pyo3.rs/v0.28.2/free-threading
- Apple documents binary frameworks as Swift packages, and third-party SDK requirements now explicitly include privacy manifests and signatures in important binary-dependency cases. https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages ; https://developer.apple.com/support/third-party-SDK-requirements/ ; https://developer.apple.com/documentation/bundleresources/privacy-manifest-files

**Conclusion:** the gap is **not** “Python/Apple SDK consumers lack package specs or official rules.” The sharper gap is a **consumer environment / artifact intake / mismatch diagnosis bundle** above those rules.


### Lower-bound dependency substrate
- Cargo unstable features: `-Z minimal-versions` and `-Z direct-minimal-versions` are intended for CI checks that validate whether `Cargo.toml` requirements really reflect the minimum versions actually used. https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo dependency requirements docs: default requirements express a minimum version plus compatible updates. https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
- Cargo FAQ: `direct-minimal-versions` can still conflict because of multiple versions or missing features. https://doc.rust-lang.org/cargo/faq.html
- Cargo lints docs: `implicit_minimum_version_req` helps make minimum version requirements explicit, but does not guarantee correctness. https://doc.rust-lang.org/cargo/reference/lints.html
- `cargo-minimal-versions`: existing wrapper proving user demand for lower-bound checks. https://crates.io/crates/cargo-minimal-versions

**Conclusion:** the gap is **not** “Cargo lacks a way to attempt lower-bound validation.” The sharper gap is a **policy / blame / waiver / diff witness** for dependency-floor truthfulness.

### Build-dir transition substrate
- Cargo build-cache docs: intermediate build-dir layout is internal to Cargo and subject to change. https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo changelog: `build.build-dir` is now stable, while `-Zbuild-dir-new-layout` exists to unblock caching and locking improvements. https://doc.rust-lang.org/cargo/CHANGELOG.html
- Build-dir-layout goal: Cargo wants finer-grained locking/caching and acknowledges current shared-cache pain. https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- User-wide-cache goal: explicitly calls for a transition path for tooling that accesses intermediate artifacts. https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html

**Conclusion:** the gap is **not** “Cargo has no build cache knobs” and not “new layout work automatically gives tool authors a migration story.” The sharper gap is a **consumer audit / path-contract / transition receipt** layer above internal-layout churn.


### Live lock-contention substrate
- Rust compiler performance survey 2025 results: Cargo and IDE blocking one another is a notable pain point, and separate target directories are a documented workaround with disk-usage trade-offs. https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- rust-analyzer FAQ: rust-analyzer and manual Cargo commands can block one another; a separate target directory can avoid that at the cost of duplicate artifacts. https://rust-analyzer.github.io/book/faq.html
- rust-analyzer configuration: `rust-analyzer.cargo.targetDir` exists specifically to avoid locking the shared Cargo target/Cargo.lock path during background work. https://rust-analyzer.github.io/book/configuration
- Cargo cache-lock internals docs: Cargo explicitly locks package/index caches to coordinate multiple Cargo processes. https://doc.rust-lang.org/beta/nightly-rustc/cargo/util/cache_lock/index.html
- Cargo unstable docs: `build-dir-new-layout` exists to unblock caching and locking improvements. https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout
- Cargo build-dir-layout goal: locking and shared-cache pain are explicit official problems. https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html

**Conclusion:** the gap is **not** “Cargo locking is folklore” and not “a workaround already makes contention boring.” The sharper gap is a **lock-wait / collision-diagnosis / mitigation witness** above that substrate.

### Debugger visualizer compatibility substrate
- Rust reference: `#[debugger_visualizer]` can embed NatVis and GDB visualizer assets into debug info. https://doc.rust-lang.org/reference/attributes/debugger.html
- Rust reference: NatVis embedding is only supported on `-windows-msvc` targets, and embedded GDB pretty printers are not auto-loaded by default. https://doc.rust-lang.org/reference/attributes/debugger.html
- GDB manual: auto-load safe-path rules can decline otherwise-valid scripts until trust is configured. https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html
- Rust release notes: debugger-visualizer support is stabilized and part of the mainstream language/tooling surface now. https://doc.rust-lang.org/beta/releases.html
- Rust debugging survey 2026: debugger support quality and visualizers remain active official concerns. https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- LLDB variable-formatting docs: summaries, filters, synthetic children, and Python-backed formatters are real external formatter substrate. https://lldb.llvm.org/use/variable.html

**Conclusion:** the gap is **not** “Rust lacks embedded visualizer syntax” and not “broad debugger pain automatically implies a new debugger pack.” The sharper gap is a **backend matrix / render-golden / safe-path diagnosis / embed-vs-external routing / drift receipt** for visualizer assets already being shipped.


## Added 2026-03-07 (118)

### Registry-authentication substrate
- Cargo registry-auth docs: Cargo authenticates to registries with built-in or external credential providers. https://doc.rust-lang.org/cargo/reference/registry-authentication.html
- Credential provider protocol docs: external providers use a JSON stdin/stdout protocol. https://doc.rust-lang.org/cargo/reference/credential-provider-protocol.html
- Registry index docs: registries requiring auth set `auth-required = true` in `config.json`. https://doc.rust-lang.org/cargo/reference/registry-index.html
- Registry docs: Cargo supports both `git` and `sparse` registry protocols. https://doc.rust-lang.org/cargo/reference/registries.html
- Cargo config/changelog docs: alternative registries with auth should use credential providers rather than silently storing unencrypted credentials; provider/config layering is real substrate. https://doc.rust-lang.org/cargo/reference/config.html ; https://doc.rust-lang.org/cargo/CHANGELOG.html
- Trusted-publishing RFC: publish identity can now come from OIDC-backed short-lived credentials rather than only stored tokens. https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html

**Conclusion:** the gap is **not** “Cargo lacks registry authentication” and not “trusted publishing already makes auth failures boring.” The sharper gap is a **provider-chain / operation-stage / redacted diagnosis bundle** above Cargo’s registry-auth substrate.

### Source-path hygiene and debugger-source substrate
- rustc remap-source-paths docs: `--remap-path-prefix` rewrites source paths across compiler output, diagnostics, macro expansions, and debug info. https://doc.rust-lang.org/rustc/remap-source-paths.html
- rustc command-line docs: remap rules are explicit CLI surface and last-match wins. https://doc.rust-lang.org/rustc/command-line-arguments.html
- Trim-paths RFC: path sanitization now has an explicit Cargo-facing model, including `/rustc/<commit-hash>/...` virtualization and interaction with sysroot paths. https://rust-lang.github.io/rfcs/3127-trim-paths.html
- rustup components docs: `rust-src` provides std sources and `rustc-dev` provides compiler-as-library sources that affect source lookup and tooling. https://rust-lang.github.io/rustup/concepts/components.html
- Rust release notes: correct un-remapping of compiler-source paths with `rustc-dev` remains subtle enough to need fixes. https://doc.rust-lang.org/beta/releases.html

**Conclusion:** the gap is **not** “Rust lacks remap/trim-path machinery” and not “installable source components already make debugger source lookup boring.” The sharper gap is a **path-hygiene / virtual-source / component-hint receipt** above that substrate.



## Added 2026-03-07 (119)

### Tool-only compile-surface substrate
- Cargo unstable docs: `--compile-time-deps` is a permanently unstable flag that only builds proc-macros, build scripts, and their required dependencies, and is intended for tools like rust-analyzer. https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
- Cargo changelog: `--compile-time-deps` was added as a perma-unstable option, making the tool-only surface more explicit and visible. https://doc.rust-lang.org/cargo/CHANGELOG.html
- RFC 3477: Rust’s ordinary stability guarantee is tied to `cargo build`, while `cargo check` is a weaker policy surface. https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- rust-analyzer configuration: target directory, sysroot source, override command, target, feature, and workspace-scope knobs are already real config surface for these workflows. https://rust-analyzer.github.io/book/configuration

**Conclusion:** the gap is **not** “Cargo lacks a tool-only compile mechanism” and not “editor workflows are already boring because `cargo check` exists.” The sharper gap is a **tool-build / parity / fallback receipt** above that substrate.

### Artifact-dependency substrate
- Cargo unstable docs: artifact dependencies are documented unstable substrate for including build artifacts into other build artifacts and building them for different targets. https://doc.rust-lang.org/cargo/reference/unstable.html#artifact-dependencies
- Cargo changelog: `-Z bindeps` was added to support binary artifact dependencies from RFC 3028. https://doc.rust-lang.org/cargo/CHANGELOG.html
- RFC 3028: Cargo artifact dependencies let a package depend on another package’s binary or C ABI artifact and receive it through environment variables. https://rust-lang.github.io/rfcs/3028-cargo-binary-dependencies.html
- RFC 3176: renamed multi-dependencies on the same crate/version extend artifact dependencies to multi-target scenarios. https://rust-lang.github.io/rfcs/3176-cargo-multi-dep-artifacts.html
- Cargo 1.94 development-cycle notes: artifact-dependency design and adjacent output concerns are still active design territory. https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

**Conclusion:** the gap is **not** “Cargo cannot express artifact dependencies” and not “RFCs plus unstable syntax already make adoption boring.” The sharper gap is an **artifact contract / target matrix / env-var / stable fallback** layer above that substrate.



## Added 2026-03-07 (120)

### Vendored/source-replaced dependency substrate
- Cargo source replacement docs already describe registry replacement, local registries, and directory sources. https://doc.rust-lang.org/cargo/reference/source-replacement.html
- `cargo vendor` already emits vendored source trees and corresponding config snippets for directory-source workflows. https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- `cargo fetch` already documents dependency prefetching and is part of the ordinary offline-preparation story. https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
- Cargo dependency-spec docs already make path, git, and registry dependencies part of the mainstream dependency model. https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html

**Conclusion:** the gap is **not** “Cargo lacks vendoring or source replacement.” The sharper gap is a **source-origin / registry-equivalence / offline-readiness** artifact above those surfaces.

### CPU baseline and runtime-dispatch substrate
- `rustc` already documents `target-cpu` and `target-feature` as codegen surfaces that materially affect generated artifacts. https://doc.rust-lang.org/rustc/codegen-options/index.html#target-cpu ; https://doc.rust-lang.org/rustc/codegen-options/index.html#target-feature
- The Rust reference already exposes `cfg(target_feature)` as a language-visible conditional-compilation surface. https://doc.rust-lang.org/reference/conditional-compilation.html#target_feature
- The standard library already exposes runtime CPU feature detection on supported architectures. https://doc.rust-lang.org/std/macro.is_x86_feature_detected.html

**Conclusion:** the gap is **not** “Rust lacks CPU-feature knobs or runtime detection.” The sharper gap is a **hardware-support promise / dispatch manifest / illegal-instruction risk** artifact above those pieces.

## Added 2026-03-07 (121)

### Node-API / npm native-addon substrate
- Node.js officially documents Node-API as the ABI-stable way to build native addons. https://nodejs.org/api/addons.html ; https://nodejs.org/api/n-api.html ; https://nodejs.org/en/learn/modules/abi-stability
- napi-rs already provides mature Rust-side authoring/build substrate, including generated bindings, CLI scaffolding, and a broad support matrix. https://napi.rs/ ; https://napi.rs/docs/introduction/getting-started ; https://napi.rs/docs/cli/build
- napi-rs v3 explicitly frames broader Bun/Deno compatibility as improving, which makes runtime claims more powerful but also easier to overstate. https://napi.rs/blog/announce-v3

**Conclusion:** the gap is **not** “Rust has no Node addon framework.” The sharper gap is a **prebuild-coverage / loader-route / publish-identity / support-risk bundle** above Node-API, npm package-routing rules, and napi-rs.- Node package docs now make the `"node-addons"` export condition and `--no-addons` behavior explicit, which sharpens the loader/fallback boundary for native packages. https://nodejs.org/api/packages.html ; https://nodejs.org/api/cli.html
- Node addon docs and runtime errors still keep context-aware / Worker-safe loading explicit, so “native addon exists” is not the same as “every runtime path is equally safe.” https://nodejs.org/api/addons.html ; https://nodejs.org/api/errors.html
- npm now documents trusted publishing and automatic provenance generation for supported public-package flows, which sharpens publish identity as part of the package contract. https://docs.npmjs.com/trusted-publishers/ ; https://docs.npmjs.com/creating-and-publishing-unscoped-public-packages/


### NuGet / .NET native-interop substrate
- Microsoft documents native files in NuGet packages via `runtimes/<rid>/native`. https://learn.microsoft.com/en-us/nuget/create-packages/native-files-in-net-packages
- Microsoft documents Runtime Identifiers (RIDs) as the platform-asset vocabulary for NuGet packages. https://learn.microsoft.com/en-us/dotnet/core/rid-catalog
- Microsoft documents native library loading, default probing, and Native AOT interop caveats. https://learn.microsoft.com/en-us/dotnet/standard/native-interop/native-library-loading ; https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/default-probing ; https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/interop
- `csbindgen` already generates Rust→C# `DllImport`-style bindings and proves there is real demand for a Rust-side interop substrate. https://github.com/Cysharp/csbindgen

**Conclusion:** the gap is **not** “Rust has no C# interop tooling.” The sharper gap is a **RID contract / binding receipt / native-load report / support-risk bundle** above NuGet packaging and .NET probing rules.



## Added 2026-03-08 (122)

### JVM / JAR / JNI shipping substrate
- Oracle JNI design overview documents `System.loadLibrary` name mapping and JNI loading/linking semantics. https://docs.oracle.com/en/java/javase/24/docs/specs/jni/design.html
- Oracle `System` API docs now make `load` / `loadLibrary` an explicit restricted/native-access surface in modern JDKs. https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html
- Oracle restricted-method list makes native loading part of an explicit reviewable capability boundary. https://docs.oracle.com/en/java/javase/24/docs/api/restricted-list.html
- Apache Maven docs already make classifiers and attached artifacts ordinary substrate for alternate package shapes. https://maven.apache.org/repositories/dependencies.html ; https://maven.apache.org/plugins/maven-deploy-plugin/examples/deploying-with-classifiers.html
- `jni` / `jni-rs` already provide serious Rust-side JNI authoring substrate. https://docs.rs/jni ; https://github.com/jni-rs/jni-rs

**Conclusion:** the gap is **not** “Rust has no JNI bindings” and not “Maven cannot ship alternate native artifacts.” The sharper gap is a **classifier matrix / loader receipt / native-access report / support-risk bundle** above that substrate.



## Added 2026-03-08 (123)

### Ruby / RubyGems native-extension substrate
- RubyGems already documents gems with extensions as ordinary ecosystem substrate. https://guides.rubygems.org/gems-with-extensions/
- RubyGems specification docs already expose extension hooks and platform metadata in gem specifications. https://guides.rubygems.org/specification-reference/
- `rb-sys` and the broader oxidize-rb project already provide real Rust-side authoring and shipping substrate. https://github.com/oxidize-rb/rb-sys ; https://oxidize-rb.org/ ; https://oxidize-rb.org/docs/building-and-shipping/
- Bundler already documents platform-oriented lockfile workflows such as adding platforms and normalizing platform entries. https://bundler.io/man/bundle-lock.1.html ; https://bundler.io/man/bundle-platform.1.html
- RubyGems already documents trusted publishing, so release-identity posture is now explicit enough to join packaging receipts. https://rubygems.org/pages/trusted-publishing

**Conclusion:** the gap is **not** “Rust has no Ruby extension tooling” and not “RubyGems platform support is just a Bundler detail.” The sharper gap is a **fat-gem matrix / gemspec receipt / Bundler support / publish-identity contract** above that substrate.


## BEAM / Hex / NIF substrate
- Rustler (safe Rust bridge for Erlang NIFs): https://docs.rs/crate/rustler/latest
- rustler_precompiled (precompiled NIF download + checksum tooling): https://hexdocs.pm/rustler_precompiled/
- Hex package publishing docs: https://hex.pm/docs/publish
- Hex package build docs: https://hexdocs.pm/hex/Mix.Tasks.Hex.Build.html
- Hex Core tarball checksum vocabulary: https://hexdocs.pm/hex_core/hex_tarball.html
- Real package examples with precompiled-NIF practices: https://hexdocs.pm/html5ever/changelog.html and https://hexdocs.pm/mjml/changelog.html

Note: future passes should not treat these as proof that a **producer-side Hex/NIF support contract** already exists. They are substrate, not the missing coordination artifact.


## Added 2026-03-08 (126)

### Debug support substrate refresh
- Rust debugging survey 2026: official evidence that debugger support quality, visualizers, async debugging, and evaluator ergonomics are still active project concerns. https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo profiles already expose `debug`, `split-debuginfo`, and `strip`; broad debuggability substrate is real even if support receipts are still missing. https://doc.rust-lang.org/cargo/reference/profiles.html
- Stable `#[debugger_visualizer]` means embedded NatVis/GDB visualizer assets are now a real language surface, not a purely speculative ecosystem wish. https://doc.rust-lang.org/reference/attributes/debugger.html
- `rustc` remap-source-paths and rustup component docs (`rust-src`, `rustc-dev`) make source-lookup posture and debugger-source diagnosis a real seam rather than folklore. https://doc.rust-lang.org/rustc/remap-source-paths.html ; https://rust-lang.github.io/rustup/concepts/components.html
- Release notes continue to mention source un-remapping and debug-related correctness changes, which reinforces that the support story above the substrate is still subtle in practice. https://doc.rust-lang.org/beta/releases.html


## Added 2026-03-08 (127)

### Native build / build-script substrate refresh
- Cargo build scripts reference: build scripts can emit directives, use `links`/metadata, and are conservatively re-run unless authors narrow change detection with `rerun-if-*`. https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo build scripts reference: `OUT_DIR` persists across rebuilds and scripts should not assume it is empty. https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo build scripts reference: `cargo::warning` is often hidden for non-path dependencies unless the build fails or users opt into `-vv`. https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ: Cargo still says after-the-fact rebuild diagnosis is not easy and mostly requires reading verbose fingerprint logs. https://doc.rust-lang.org/cargo/faq.html
- Cargo changelog / docs: `cargo::error=MESSAGE` is now a real surface (1.84+), and Cargo also has active unstable work around warnings handling and build analysis. https://doc.rust-lang.org/cargo/CHANGELOG.html ; https://doc.rust-lang.org/cargo/reference/unstable.html#warnings ; https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- `system-deps` docs: declarative native dependencies in `Cargo.toml` metadata are real substrate, including optional/feature-specific deps. https://docs.rs/system-deps/latest/system_deps/
- `system-deps` docs also already expose real mode controls like `SYSTEM_DEPS_$NAME_BUILD_INTERNAL`, `SYSTEM_DEPS_$NAME_NO_PKG_CONFIG`, and `SYSTEM_DEPS_$NAME_LINK`, which means the missing value is no longer “a control surface exists at all.” https://docs.rs/system-deps/latest/system_deps/ ; https://docs.rs/system-deps/latest/system_deps/struct.Config.html
- `vcpkg` docs: Windows/MSVC-oriented probing that emits Cargo metadata is also real substrate. https://docs.rs/vcpkg/latest/vcpkg/
- `system-deps` issue #97: imperative build scripts are often copied, share defects, and usually are not tested. https://github.com/gdesmott/system-deps/issues/97
- Cargo issues #10159 and #15792: build-script failure presentation remains noisy even after new surfaces like `cargo::error`. https://github.com/rust-lang/cargo/issues/10159 ; https://github.com/rust-lang/cargo/issues/15792
- Rust project goal on sandboxed build scripts: the Rust project explicitly treats `-sys` / native probing as a first-class build-script use case and wants declarative permissions/configuration. https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

- Cargo config already has `target.<triple>.<links>` overrides that skip running a build script entirely, which means any serious native-build contract crate should model override/handoff flows as first-class cases. https://doc.rust-lang.org/cargo/reference/config.html
- Cargo also has active unstable work on “any build script metadata”, which sharpens the case for a typed receipt layer above raw `DEP_*` / `CARGO_DEP_*` env propagation rather than more ad-hoc metadata parsing. https://doc.rust-lang.org/cargo/reference/unstable.html#any-build-script-metadata

**Conclusion:** the gap is **not** “Rust has no build-script protocol,” not “`cargo::error` already solved build-script UX,” and not “`system-deps` means native dependency management is already boring.” The sharper gap is a **report/test/contract stack** above current substrate, increasingly including **mode/policy truth** for system vs vendored vs override outcomes.


## Added 2026-03-08 (129)

### Native-build upstream-fit substrate
- Cargo external tools docs explicitly say `--message-format=json` includes **results of build scripts**, which means a serious buildscript UX crate can layer on current machine-readable output instead of pretending Cargo exposes nothing structured. https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo external-tools docs also say the `build-script-executed` message can be emitted even when the script did not run, surfacing previously cached values; report-oriented crates need capture-origin honesty instead of claiming every observation is fresh. https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build-script docs explicitly say `cargo::warning` is shown by default only for `path` dependencies and that registry-dependency warnings are otherwise hidden unless the build fails or the user opts into `-vv`. https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo issue #15038 shows that `cargo::error` still has noisy non-zero-exit edge cases, so the existence of the directive is not proof that human-scale build-script UX is solved. https://github.com/rust-lang/cargo/issues/15038
- Cargo unstable features already include `metabuild` and `multiple-build-scripts`, so future buildscript-oriented crates should avoid baking in a worldview where one handwritten `build.rs` file is the permanent unit of truth. https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo issue #14948 explicitly frames “reduce the need for users to write build scripts” as an upstream direction, which means a good crate in this frontier should ease migration and review rather than entrench imperative scripts forever. https://github.com/rust-lang/cargo/issues/14948

**Conclusion:** the gap is still real, but it is a **layering / receipt / workflow** gap above upstream Cargo substrate, not a license to fork Cargo's model.


## Added 2026-03-08 (130)

### Cargo build-analysis / `cargo report` substrate
- Cargo unstable docs: `-Zbuild-analysis` records and persists detailed build metrics across runs, stores JSONL logs under `$CARGO_HOME/log/`, and exposes `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`. https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- Cargo changelog: `cargo report timings` HTML replay is now a real unstable command surface, and `--compile-time-deps` remains explicit tool-only substrate. https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo tracking issue #15844: open questions still include programmable format for `cargo report sessions`, schema evolution, session IDs for nested Cargo calls, and how actionable/friendly rebuild reasons should be. https://github.com/rust-lang/cargo/issues/15844
- Cargo issue #16472: session selection for `cargo report timings` / `cargo report rebuilds` is still active accepted design territory. https://github.com/rust-lang/cargo/issues/16472
- Cargo issue #16488: the new `cargo report sessions` / `rebuilds` / `timings` commands still lacked dedicated man pages as of January 2026. https://github.com/rust-lang/cargo/issues/16488
- Cargo external tools JSON: Cargo already has a stable machine-readable JSON message channel for builds/artifacts/build-script results, which remains relevant alongside build-analysis. https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo metadata docs: `cargo metadata --format-version` remains Cargo's stable graph/context substrate, which is relevant when build-analysis imports need durable package/target context. https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo unstable docs/changelog: the machine-readable `--timings=json` output has been removed on 1.94-nightly even as `cargo report timings` grows, which reinforces the need for a downstream stable import/warehouse contract instead of treating timing HTML as the machine schema. https://doc.rust-lang.org/cargo/reference/unstable.html ; https://doc.rust-lang.org/cargo/CHANGELOG.html

**Conclusion:** the gap is **not** “Cargo has no build-analysis substrate anymore.” The sharper gaps are now two adjacent layers: a **stable session-import / rebuild-bundle / redaction / diff contract** for per-run support, and a **stable imported-session warehouse / regression-adjudication contract** for longitudinal analysis.


## Added 2026-03-08 (132)

### Cargo tool-workflow parity substrate
- Cargo unstable docs: `--compile-time-deps` is a permanently unstable tool-oriented mode that only builds proc-macros, build scripts, and their required dependencies. https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
- RFC 3477: `cargo build` carries Rust’s standard stability guarantee while `cargo check` is intentionally a faster and less complete surface. https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- rust-analyzer configuration: the documented command/config surface already includes build-script override commands, check override commands, target dirs, targets, and sysroot source. https://rust-analyzer.github.io/book/configuration
- Cargo build-dir layout goal: rust-analyzer/Cargo contention and shared-cache pain are explicit upstream motivation for layout work. https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo metadata docs: the output is stable and versioned when callers pass `--format-version`, making it a useful graph/context substrate but not a sufficient workflow receipt by itself. https://doc.rust-lang.org/cargo/commands/cargo-metadata.html

**Conclusion:** the gap is not “Cargo has no tool-facing build substrate.” The sharper gap is a **receiver-facing parity / fallback / workflow receipt** above existing Cargo and rust-analyzer surfaces.


## Cargo build-dir transition substrate
- Cargo build-cache docs (final vs intermediate, internal layout warning): https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo config docs (`build.build-dir`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo external-tools JSON (`build-script-executed`, produced artifacts): https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build-script docs (`OUT_DIR` contract): https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo env vars docs (`OUT_DIR`, `CARGO_BIN_EXE_<name>`): https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Rust release notes warning for tools relying on build-dir internals: https://doc.rust-lang.org/beta/releases.html
- Cargo build-dir layout goal / tooling transition motivation: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- rust-analyzer `build-dir` support issue: https://github.com/rust-lang/rust-analyzer/issues/20150


## Added 2026-03-08 (137)

### Debuggability posture substrate refresh
- Cargo profiles explicitly document `debug`, `split-debuginfo`, and `strip`; the broad posture knobs already exist. https://doc.rust-lang.org/cargo/reference/profiles.html
- Cargo profiles also warn that Cargo and `rustc` can have different defaults for `split-debuginfo`, which is exactly the sort of drift a receipt crate should surface. https://doc.rust-lang.org/cargo/reference/profiles.html
- `rustc` codegen docs already document the main sidecar realities: `pdb` on Windows MSVC, `dSYM` on macOS, and `dwo` / `dwp` on other Unix platforms. https://doc.rust-lang.org/rustc/codegen-options/index.html
- `rustc` also documents that `strip=debuginfo` may leave backtraces mostly intact while making interactive debugger use ineffective. https://doc.rust-lang.org/rustc/codegen-options/index.html
- Stable `#[debugger_visualizer]` means NatVis/GDB visualizer assets are real substrate, not a speculative future dependency. https://doc.rust-lang.org/reference/attributes/debugger.html
- Cargo’s unstable `trim-paths` docs make path hygiene a real adjacent seam, but that still does not provide a receiver-facing support contract. https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
- Cargo’s changelog note that disabling debuginfo now implies `strip = "debuginfo"` when `strip` is not set is a concrete example of subtle support-posture drift that maintainers can miss. https://doc.rust-lang.org/cargo/CHANGELOG.html

## Added 2026-03-17 (215)

### Debuggability productization substrate refresh
- Rust’s vision-doc work explicitly calls for more **supportive interfaces** from crates, which strengthens the case for a reviewable debug-support contract above raw debugger substrate. https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey still reports debugging as one of the most common productivity-limiting problems, even if it slipped from 2nd to 4th place. https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s Build Dir Layout v2 work explicitly separates intermediate `build-dir` concerns from final `target-dir` artifacts, which sharpens the need for a location-agnostic handoff artifact. https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- `rustc` command-line docs already document `--remap-path-prefix`, which means source-path rewriting is real substrate rather than a hypothetical edge case. https://doc.rust-lang.org/rustc/command-line-arguments.html
- Cargo’s changelog note that disabling debuginfo can imply `strip = "debuginfo"` is exactly the kind of subtle posture drift that a support-contract crate should make reviewable. https://doc.rust-lang.org/cargo/CHANGELOG.html

**Conclusion:** the gap is **not** “Rust still lacks raw debug knobs,” not “Build Dir Layout v2 already solves symbol handoff,” and not “source remapping automatically belongs in the same crate as every debugger problem.” The sharper gap is a **support-class / artifact-handoff / source-lookup-impact contract** above today’s substrate.

## Assurance cases / safety cases
- SACM standard (structured assurance-case metamodel): https://www.omg.org/spec/SACM/2.3/About-SACM
- GSN Community Standard v1 (FAA mirror): https://www.faa.gov/about/office_org/headquarters_offices/ang/redac/redac-sas-201503-gsn-community-standard-v1.pdf
- WebGSN (assurance-argument editor/viewer): https://github.com/safeautonomy/WebGSN
- D-Case Editor (typed assurance-case editor): https://github.com/d-case/d-case_editor
- CertWare (open-source assurance/safety case tools): https://nasa.github.io/CertWare/gsn.html

## Added 2026-03-08 (147)

### Cargo vendoring/source-replacement exactness and coverage substrate
- Cargo source replacement docs now state the core assumption explicitly: replacement sources are expected to contain the **exact same source code** and may not add crates not present in the original source. https://doc.rust-lang.org/cargo/reference/source-replacement.html
- The same docs also say source replacement is **not** the right tool for patching or private-registry semantics. https://doc.rust-lang.org/cargo/reference/source-replacement.html
- `cargo vendor` already exposes `--sync`, `--respect-source-config`, and `--versioned-dirs`, which means the basic vendoring workflow is real substrate rather than missing functionality. https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- Cargo’s offline docs explicitly warn that `--offline` may yield different dependency resolution than online mode. https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
- Cargo path overrides are already documented as exact-graph-only overrides, not arbitrary graph rewrites. https://doc.rust-lang.org/cargo/reference/overriding-dependencies.html
- Open Cargo issues still show edge cases that matter for review: logical source alias splits when multiple sources are replaced into one vendor dir, replaced git workspace sources that still require git-style history, and path dependencies not included by vendoring. https://github.com/rust-lang/cargo/issues/14821 ; https://github.com/rust-lang/cargo/issues/16141 ; https://github.com/rust-lang/cargo/issues/10134

**Conclusion:** the gap is **not** “Cargo lacks vendoring, source replacement, or offline commands.” The sharper gap is a **source-identity / coverage-truth / offline-honesty** artifact above those surfaces.



## Added 2026-03-08 (148)

### Cargo lock-contention / root-sharing substrate refresh
- Rust compiler performance survey 2025: more than 35% of respondents said IDE and Cargo blocking one another is a big problem; the post explicitly points to the rust-analyzer separate-target-dir workaround. https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- rust-analyzer FAQ: rust-analyzer and manual Cargo commands can block one another over the build lock, and separate target directories are the documented mitigation. https://rust-analyzer.github.io/book/faq.html
- rust-analyzer configuration: `cargo.targetDir` is a first-class knob, and rust-analyzer also documents override-command and `useRustcWrapper` surfaces that materially affect contention topology. https://rust-analyzer.github.io/book/configuration
- Cargo build-cache docs: Cargo now documents **target-dir** versus **build-dir** explicitly, with final artifacts living in target-dir and intermediate artifacts in build-dir. https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo environment/config docs: `RUSTC_WRAPPER` and `RUSTC_WORKSPACE_WRAPPER` are first-class surfaces, and the workspace wrapper affects the filename hash so wrapper-produced artifacts are cached separately. https://doc.rust-lang.org/cargo/reference/environment-variables.html ; https://doc.rust-lang.org/cargo/reference/config.html
- Cargo cache-lock internals: package/index cache coordination still uses explicit locking rules, which keeps package-cache contention a real separate lane from target/build-root waits. https://doc.rust-lang.org/beta/nightly-rustc/cargo/util/cache_lock/index.html
- Cargo unstable docs and the build-dir-layout goal still treat the new layout as groundwork for finer-grained locking and shared-cache improvements rather than proof that contention is already solved. https://doc.rust-lang.org/cargo/reference/unstable.html#build-dir-new-layout ; https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html

**Conclusion:** the gap is **not** “Cargo has no lock-contention story at all,” and it is not “set a different target dir and the whole problem disappears.” The sharper missing layer is a **receiver-facing root-sharing / wait / wrapper-context bundle** that can tell another person which lane was shared, which lane was isolated, and where the answer remains conservative.


## Added 2026-03-08 (149)

### rust-analyzer override-command substrate
- rust-analyzer configuration docs: `check.overrideCommand` is a first-class override surface and must emit JSON output. https://rust-analyzer.github.io/book/configuration
- rust-analyzer configuration docs: `cargo.buildScripts.overrideCommand` is also first-class and rust-analyzer explicitly suggests pairing it when wrapping Cargo differently. https://rust-analyzer.github.io/book/configuration
- rust-analyzer configuration docs: `{label}` in `check.overrideCommand` behaves much like `check.workspace = false`, making selection scope part of the support truth. https://rust-analyzer.github.io/book/configuration
- rust-analyzer configuration docs: `cargo.targetDir` prevents Cargo-lock blocking at the expense of duplicate build artifacts. https://rust-analyzer.github.io/book/configuration
- rust-analyzer configuration docs: `cargo.buildScripts.useRustcWrapper` defaults to true. https://rust-analyzer.github.io/book/configuration
- rust-analyzer issue #10793: relative override commands can be hard to debug in practice. https://github.com/rust-lang/rust-analyzer/issues/10793
- rust-analyzer issue #5962: custom override-command workflows can produce path/VFS mismatches even when JSON is emitted. https://github.com/rust-lang/rust-analyzer/issues/5962
- esp-idf-sys issue #113: pairing build-script overrides with a toolchain-specific Cargo invocation can resolve real workflows. https://github.com/esp-rs/esp-idf-sys/issues/113

**Conclusion:** the gap is **not** “rust-analyzer lacks override commands” and not “custom wrapper workflows are already supportable because they can emit JSON.” The sharper gap is a **comparison-baseline + override-command provenance bundle** above that substrate.


## Added 2026-03-08 (150)

### rust-analyzer coverage and invocation substrate
- rust-analyzer configuration docs: `cargo.allTargets` defaults to true and passes `--all-targets` to Cargo. https://rust-analyzer.github.io/book/configuration
- rust-analyzer configuration docs: `check.allTargets` defaults to `cargo.allTargets`. https://rust-analyzer.github.io/book/configuration
- Cargo build docs: `--all-targets` is equivalent to `--lib --bins --tests --benches --examples`. https://doc.rust-lang.org/cargo/commands/cargo-build.html
- rust-analyzer configuration docs: `check.workspace` defaults to true, and if false rust-analyzer passes `-p <package>` if applicable. https://rust-analyzer.github.io/book/configuration
- rust-analyzer configuration docs: build-script and check override commands both support `per_workspace` vs `once`, and linked-project override commands normally run with the workspace root as working directory. https://rust-analyzer.github.io/book/configuration
- rust-analyzer issue #18528: `allTargets = false` can leave a proc-macro dylib path missing because a dev-dependency-bearing lane was not built. https://github.com/rust-lang/rust-analyzer/issues/18528
- rust-analyzer issue #17126: `check.workspace = false` can still leak diagnostics from all members on first startup. https://github.com/rust-lang/rust-analyzer/issues/17126

**Conclusion:** the gap is **not** “rust-analyzer lacks package/target settings.” The sharper gap is a **selection-coverage + workspace-invocation bundle** above that substrate.


## Added 2026-03-08 (155)

### Cargo feature-origin / namespaced-feature substrate
- Cargo features docs: optional dependencies create implicit feature aliases; `dep:` suppresses that alias; `pkg/feat` activates optional dependencies; `pkg?/feat` forwards only if another path already activated the dependency. https://doc.rust-lang.org/cargo/reference/features.html
- Registry index docs: namespaced features (`dep:`) and weak dependencies (`pkg?/feat`) are preserved in the `features2` field for extended syntax. https://doc.rust-lang.org/beta/cargo/reference/registry-index.html
- Rust 1.60 release notes: namespaced and weak dependency features were stabilized. https://doc.rust-lang.org/beta/releases.html
- Cargo metadata issue #10543: `cargo metadata` lost the ability to distinguish implicit optional-dependency features from explicit user-authored features. https://github.com/rust-lang/cargo/issues/10543
- Cargo issue #10788 / changelog fix #12130: `dep:` plus dependency-feature forwarding had real edge cases that needed a fix. https://github.com/rust-lang/cargo/issues/10788 and https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo issue #12111: `dep:` plus `pkg/feat` still produced confusing receiver-facing errors. https://github.com/rust-lang/cargo/issues/12111
- Cargo issue #14015: weak dependency feature forwarding can still produce confusing “not a dependency” style errors when no path activates the optional dependency. https://github.com/rust-lang/cargo/issues/14015
- Cargo issue #12336: downstream tooling can still be misled by feature-like cfg names that do not correspond to real public manifest features. https://github.com/rust-lang/cargo/issues/12336

**Conclusion:** the gap is **not** “Cargo has no feature syntax” and not “optional dependency behavior is already obvious to tools.” The sharper gap is a **feature-origin / activation-precondition receipt layer** that preserves whether a feature-like name was implicit, explicit, hidden, or weakly forwarded.

## Added 2026-03-16 (196)

### Crate capability-contract substrate
- Cargo manifest metadata (`keywords`, `categories`, `build`, `links`, `package.metadata`): https://doc.rust-lang.org/cargo/reference/manifest.html
- Cargo `rust-version` support expectations and `cargo-msrv` note: https://doc.rust-lang.org/cargo/reference/rust-version.html
- docs.rs custom-build metadata: https://docs.rs/about/metadata
- docs.rs rustdoc JSON: https://docs.rs/about/rustdoc-json
- crates.io development update (security tab, SLOC, `pubtime`): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- RFC 1824 crates.io default ranking: https://rust-lang.github.io/rfcs/1824-crates.io-default-ranking.html
- `cargo-deny`: https://embarkstudios.github.io/cargo-deny/
- `cargo-public-api`: https://github.com/cargo-public-api/cargo-public-api
- cargo-semver-checks goal: https://rust-lang.github.io/rust-project-goals/2024h2/cargo-semver-checks.html

**Conclusion:** the gap is **not** “Rust has no machine-readable crate metadata” and not “there are no slice tools for MSRV, API, semver, or dependency policy.” The sharper gap is a **joined producer-side capability / interop / support contract** with observed receipts and conformance reports that other tools can import without scraping README prose.


## General-purpose ecosystem interop substrate
- `http` crate (common HTTP types): https://docs.rs/http
- `tower-service` crate (core `Service` abstraction): https://docs.rs/tower-service
- `tower` crate overview (protocol-agnostic clients/servers around `Service`): https://docs.rs/tower/latest/tower/
- `futures-core::Stream` docs: https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- Serde docs: https://docs.rs/serde
- `axum` docs explicitly emphasize sharing middleware with `hyper` and `tonic` through `tower::Service`: https://docs.rs/axum/latest/axum/
- Evolving trait hierarchies goal: https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- Externally Implementable Items goal: https://rust-lang.github.io/rust-project-goals/2025h1/eii.html
- cargo-semver-checks goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

**Conclusion:** the gap is **not** that Rust lacks shared building blocks. The sharper gap is a **profile-pack + conformance + pair-compatibility** layer above them.

## Diagnostics / crate guidance substrate
- Rust Reference diagnostics attributes (`#[diagnostic]`, `#[diagnostic::on_unimplemented]`): https://doc.rust-lang.org/reference/attributes/diagnostics.html
- Rust Reference built-in attribute index including `diagnostic::do_not_recommend`: https://doc.rust-lang.org/reference/attributes.html
- Rust 1.78.0 release notes (stabilized `#[diagnostic]` namespace and `#[diagnostic::on_unimplemented]`): https://doc.rust-lang.org/beta/releases.html
- RFC 3368 diagnostic attribute namespace: https://rust-lang.github.io/rfcs/3368-diagnostic-attribute-namespace.html
- rustdoc documentation tests (`compile_fail` examples are testable but may become valid in future releases): https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html
- rustdoc unstable features (nightly doctest error-code checks are unlikely to stabilize as exact-message contracts): https://doc.rust-lang.org/rustdoc/unstable-features.html
- trybuild compile-fail harness: https://docs.rs/trybuild/latest/trybuild/
- `trybuild` troubleshooting note on `rust-src`-dependent rendering drift: https://docs.rs/trybuild/latest/trybuild/
- ui_test diagnostics harness: https://docs.rs/ui_test/latest/ui_test/
- miette Diagnostic metadata (`code`, `help`, `url`): https://docs.rs/miette/latest/miette/trait.Diagnostic.html
- proc-macro-error2 (structured proc-macro errors instead of plain panics): https://docs.rs/proc-macro-error2/latest/proc_macro_error2/
- `miette` changelog note on `Diagnostic::url()` / automatic docs.rs link generation: https://docs.rs/crate/miette/latest/source/CHANGELOG.md
- ariadne (diagnostic rendering): https://docs.rs/ariadne/latest/ariadne/
- codespan-reporting (diagnostic reporting): https://docs.rs/codespan-reporting/latest/codespan_reporting/

**Conclusion:** the gap is **not** “Rust has no diagnostic surface”, **not** “compile_fail examples already prove the whole recovery path”, and **not** “we only need prettier rendering.” The sharper gap is a **crate-authored guidance-pack / message-stability / guidance-channel / recovery-origin / recipe-fidelity / diff layer** above today’s compiler hooks, compile-fail harnesses, docs examples, proc-macro helpers, and renderer crates.

## Runtime error / panic handoff substrate
- `std::error` module docs (anticipated runtime failure modes): https://doc.rust-lang.org/std/error/index.html
- `std::error::Error` docs (`source()` across abstraction boundaries): https://doc.rust-lang.org/std/error/trait.Error.html
- `std::backtrace` docs (capture controlled by `RUST_LIB_BACKTRACE` / `RUST_BACKTRACE` due to runtime cost): https://doc.rust-lang.org/std/backtrace/index.html
- `std::panic::set_hook` docs (custom panic reporting with payload and location): https://doc.rust-lang.org/std/panic/fn.set_hook.html
- `std::error::Request` docs (generic typed runtime context currently restricted to `std`-owned use cases): https://doc.rust-lang.org/std/error/struct.Request.html
- nightly `std::error::Report` docs: https://doc.rust-lang.org/beta/std/error/struct.Report.html
- RFC 3192 / dyno background: https://rust-lang.github.io/rfcs/3192-dyno.html
- `error-stack` docs (contexts + attachments): https://docs.rs/error-stack/latest/error_stack/
- `miette` JSON report handler: https://docs.rs/miette/latest/miette/struct.JSONReportHandler.html
- `tracing-error` `SpanTrace`: https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTrace.html
- `human-panic` docs (user-submittable crash reports with privacy note): https://docs.rs/human-panic/latest/human_panic/
- `color-eyre` install docs (panic + error hooks): https://docs.rs/color-eyre/latest/color_eyre/fn.install.html
- `color-eyre` hook builder docs (custom panic sections / issue URLs): https://docs.rs/color-eyre/latest/color_eyre/config/struct.HookBuilder.html
- `tracing-error` `SpanTraceStatus` docs (`UNSUPPORTED` vs `EMPTY`): https://docs.rs/tracing-error/latest/tracing_error/struct.SpanTraceStatus.html

**Conclusion:** the gap is **not** “Rust has no runtime error tooling” and not “just add more logs.” The sharper gap is a **crate-authored runtime handoff / exactness / share-safety / receipt / diff layer** above today’s error, panic, tracing, and renderer substrate.


## Crate upgrade / migration substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code are the main learning surfaces; debugging still matters): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- cargo-semver-checks goal (Cargo wants stronger publish-path semver checking): https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- Cargo SemVer guidance: https://doc.rust-lang.org/cargo/reference/semver.html
- Inside Rust `hint-mostly-unused` post (feature flags are part of a crate's stable interface): https://blog.rust-lang.org/inside-rust/2025/07/15/call-for-testing-hint-mostly-unused/
- rustc JSON diagnostics (structured suggestions / applicability): https://doc.rust-lang.org/beta/rustc/json.html
- Edition guide advanced migrations (`cargo fix --edition` runs iterative fix/check loops and may need multiple configurations): https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- cargo fix docs (automatic application of rustc suggestions): https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- rustfix crate (low-level suggestion applier for rustc JSON output): https://docs.rs/rustfix/latest/rustfix/
- rustfix `Filter` docs (machine-applicable vs everything is explicit): https://docs.rs/rustfix/latest/rustfix/enum.Filter.html
- release-plz update docs (version/changelog automation with optional semver-check consult): https://release-plz.dev/docs/usage/update
- release-plz usage docs (update / release-pr / release remain release-automation commands): https://release-plz.dev/docs/usage
- cargo-release crate page: https://crates.io/crates/cargo-release
- Cargo publish docs: https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- Cargo yank docs: https://doc.rust-lang.org/cargo/commands/cargo-yank.html

**Conclusion:** the gap is **not** “Rust has no release tools”, **not** “there is no SemVer evidence”, and **not** “cargo fix already solves ordinary crate upgrades.” The sharper gap is a **crate-authored release-to-release upgrade pack / hazard / recipe / fixup / diff layer** above semver slices, suggestion substrate, and release automation.


## Crate off-ramp / successor-planning substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code are the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- warn-by-default `deprecated` lint docs (deprecations should usually include what to use instead): https://doc.rust-lang.org/rustc/lints/listing/warn-by-default.html#deprecated
- Cargo SemVer guidance (added deprecations are part of update experience and can be feature-gated before removal): https://doc.rust-lang.org/cargo/reference/semver.html
- Cargo yank docs (yank removes versions from new resolution but does not delete data): https://doc.rust-lang.org/cargo/commands/cargo-yank.html
- Cargo update docs (prefer non-yanked versions or seek maintainer help): https://doc.rust-lang.org/cargo/commands/cargo-update.html
- crates.io development update (Security tab with affected version ranges): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious-crate policy update (RustSec advisories remain the always-on notification path): https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- cargo-audit docs: https://docs.rs/crate/cargo-audit/latest
- cargo-deny docs: https://docs.rs/crate/cargo-deny/latest
- cargo-outdated docs: https://docs.rs/crate/cargo-outdated/latest
- RFC 3416 feature metadata / feature deprecation motivation: https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- docs.rs renamed-crate example (`sello-crypto` → `txgate-crypto`) with a redirect crate and explicit migration steps: https://docs.rs/crate/sello-crypto/latest
- `cargo-maintained` shows the adjacent pressure to detect stale dependency lines, but still does not define a maintainer-authored exit contract: https://docs.rs/crate/cargo-maintained/latest

**Conclusion:** the gap is **not** “Rust has no deprecation/advisory tooling”, **not** “yanks or advisories already tell users what to do”, and **not** “maintenance metadata already covers succession.” The sharper gap is a **crate-authored off-ramp / successor-map / checked exit-recipe / sunset-diff layer** above today’s deprecation, yank, advisory, and outdated-version substrate.


## Crate configuration-scenario substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code are the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo features docs (features are additive by default; mutually exclusive choices need care): https://doc.rust-lang.org/cargo/reference/features.html
- Cargo targets docs (`required-features` controls whether bins/examples/tests/benches are built at all): https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- Cargo external tools docs (`cargo metadata` format is stable and versioned): https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo metadata docs (`--format-version` should be explicit): https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- docs.rs metadata docs (`features`, `all-features`, `no-default-features`, targets, rustdoc args): https://docs.rs/about/metadata
- docs.rs build docs (`cfg(docsrs)` only applies to the final crate; local preflight is only approximate): https://docs.rs/about/builds
- RFC 3416 feature metadata (docs/deprecation/visibility structure remains a live need): https://rust-lang.github.io/rfcs/3416-feature-metadata.html
- Cargo 1.93 development-cycle post (feature metadata still active in Cargo work): https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- document-features docs (keeps feature comments next to `Cargo.toml`): https://docs.rs/crate/document-features/latest
- cargo-feature-combinations docs (runs cargo commands across feature combinations): https://docs.rs/cargo-feature-combinations
- cargo-hack crate page (widely used Cargo wrapper for extra feature-combination and workspace checks): https://crates.io/crates/cargo-hack

**Conclusion:** the gap is **not** “Cargo has no feature/config substrate”, **not** “feature-powerset testing already solves setup”, and **not** “feature docs alone are enough.” The sharper gap is a **crate-authored configuration-scenario / recipe / provenance / matrix-fidelity / diff layer** above today’s features, docs.rs metadata, environment knobs, and raw Cargo inspection tools.


## Crate performance-envelope substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code are the main learning surfaces; resource usage remains a recurring productivity problem): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo bench docs (benchmark target model, custom harness support, nightly-only `#[bench]` note, bench-profile default): https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- Cargo profiles docs (built-in `bench` profile plus custom profiles): https://doc.rust-lang.org/cargo/reference/profiles.html
- Criterion docs (stable-compatible wall-time measurement): https://docs.rs/criterion/latest/criterion/
- Iai-Callgrind docs (CI-friendly instruction/count and cache-oriented measurement): https://docs.rs/iai-callgrind/latest/iai_callgrind/
- Divan docs (throughput counters and benchmark runner): https://docs.rs/divan/latest/divan/
- Divan `AllocProfiler` docs (allocation measurement affects timing and therefore metric-authority needs explicit handling): https://docs.rs/divan/latest/divan/struct.AllocProfiler.html
- codspeed-criterion-compat docs: https://docs.rs/crate/codspeed-criterion-compat/latest
- CodSpeed Rust benchmark docs (runs may execute without real performance measurement in unknown environments): https://codspeed.io/docs/benchmarks/rust
- cargo-nextest Criterion integration docs (Criterion test mode uses `test` profile and one iteration; useful for compile/panic sanity but not the same as authoritative measurement): https://nexte.st/docs/integrations/criterion/
- cargo-nextest benchmark docs (experimental `cargo nextest bench`, custom harness protocol support): https://nexte.st/docs/features/benchmarks/

**Conclusion:** the gap is **not** “Rust has no benchmarking tools”, **not** “profiling bundles already solve product-facing perf posture”, and **not** “hosted CI measurement already tells downstream users what a crate promises.” The sharper gap is a **crate-authored performance-envelope / metric-authority / execution-intent / workload-lineage / environment-fidelity / confidence / diff layer** above today's benchmark, profile, and perf-service substrate.


## Crate authority-surface / ambient-dependency substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces; resource/debugging pain persists): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Safety-critical vision-doc post (teams often accelerate with crates and later harden, constrain, rewrite, or replace dependencies): https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust project goal on sandboxed build scripts (file/network/process restrictions and determinism pressure): https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo environment variables docs: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo build scripts docs: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- `ambient-authority` docs (explicit opt-in marker for ambient authority): https://docs.rs/ambient-authority/latest/ambient_authority/struct.AmbientAuthority.html
- `cap-std` docs (capability-based APIs with `Dir`, `Pool`, and capability-based time): https://docs.rs/cap-std/latest/cap_std/
- `cap-std::fs::Dir` docs (path operations relative to an opened directory, de-emphasizing global filesystem assumptions): https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- `rustix` docs (does not itself restrict ambient authorities or impose sandboxing): https://docs.rs/rustix/latest/rustix/
- `wasi-cap-std-sync` docs (sandboxed filesystem access and host-boundary integration via capability types): https://docs.rs/wasi-cap-std-sync/latest/wasi_cap_std_sync/
- `getrandom` docs (opt-in and custom backends exist, but library-local configuration does not automatically control downstream behavior): https://docs.rs/getrandom/latest/getrandom/

**Conclusion:** the gap is **not** “Rust has no capability substrate”, **not** “we just need another sandbox”, and **not** “static scans alone would settle authority posture”. The sharper gap is a **crate-authored authority-surface / authority-budget / injection-boundary / profile-witness / diff layer** above today’s capability, sandbox, and host-integration substrate.


## Crate resource-surface / capacity-support substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces; resource usage remains a recurring problem): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tokio `mpsc` docs (bounded vs unbounded, backpressure, allocation behavior, clean shutdown): https://docs.rs/tokio/latest/tokio/sync/mpsc/index.html
- Tokio bounded channel docs: https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.channel.html
- Tokio unbounded channel docs: https://docs.rs/tokio/latest/tokio/sync/mpsc/fn.unbounded_channel.html
- Tokio runtime builder docs: https://docs.rs/tokio/latest/tokio/runtime/struct.Builder.html
- Tokio `spawn_blocking` docs: https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- Tokio `Semaphore` docs: https://docs.rs/tokio/latest/tokio/sync/struct.Semaphore.html
- Tokio `SemaphorePermit` docs: https://docs.rs/tokio/latest/tokio/sync/struct.SemaphorePermit.html
- Reqwest client builder and connection pool docs (`pool_idle_timeout`, `pool_max_idle_per_host`, default `usize::MAX`): https://docs.rs/reqwest/latest/reqwest/struct.ClientBuilder.html
- Reqwest client connection pooling docs: https://docs.rs/reqwest/latest/reqwest/struct.Client.html
- Tower limit docs (concurrency/rate primitives, but not a whole backlog contract by themselves): https://docs.rs/tower/latest/tower/limit/index.html
- Tower buffer docs (crate-owned channel-backed buffering is real substrate, but still not a whole resource support contract): https://docs.rs/tower/latest/tower/buffer/index.html
- Tower `ServiceBuilder` docs (layer order changes effective in-flight budgets and belongs in the contract): https://docs.rs/tower/latest/tower/struct.ServiceBuilder.html
- Moka cache builder and capacity docs: https://docs.rs/moka/latest/moka/future/struct.CacheBuilder.html
- Moka cache weighted-size / max-capacity docs: https://docs.rs/moka/latest/moka/future/struct.Cache.html
- Governor quota and rate-limiter docs: https://docs.rs/governor/latest/governor/struct.Quota.html
- Tokio runtime metrics docs: https://docs.rs/tokio/latest/tokio/runtime/struct.RuntimeMetrics.html
- tokio-metrics docs: https://docs.rs/tokio-metrics/latest/tokio_metrics/
- SQLx pool docs (fair waiting, close semantics, and pool acquisition behavior): https://docs.rs/sqlx/latest/sqlx/struct.Pool.html
- SQLx `PoolOptions` docs (max connections, acquire timeout, and other pool posture knobs): https://docs.rs/sqlx/latest/sqlx/pool/struct.PoolOptions.html
- Deadpool managed-pool docs (waiting, resize, close, and status semantics): https://docs.rs/deadpool/latest/deadpool/managed/struct.Pool.html

**Conclusion:** the gap is **not** “Rust has no queues, caches, pools, or limits”, **not** “metrics already tell downstream users what a crate promises”, **not** “a pool size knob already explains acquire fate”, and **not** “layer order is just an implementation detail”. The sharper gap is a **crate-authored resource-surface / admission-path / backlog-ownership / capacity-shrink / acquire-fate / diff layer** above today’s queue/cache/limit/runtime and observation substrate.


## Crate test-surface / downstream-testing-support substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces; debugging still matters): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust test organization docs: https://doc.rust-lang.org/book/ch11-03-test-organization.html
- Tokio testing guide (paused time, mock I/O advice): https://tokio.rs/tokio/topics/testing
- Tokio paused-time docs (`current_thread` requirement): https://docs.rs/tokio/latest/tokio/time/fn.pause.html
- Tokio `#[tokio::test]` docs (`start_paused` requires `test-util`): https://docs.rs/tokio/latest/tokio/attr.test.html
- `tokio-test` docs: https://docs.rs/tokio-test/latest/tokio_test/
- `rstest` fixture docs: https://docs.rs/rstest/latest/rstest/attr.fixture.html
- `proptest` arbitrary/strategy docs: https://docs.rs/proptest/latest/proptest/arbitrary/index.html
- `trybuild` docs: https://docs.rs/trybuild/latest/trybuild/
- `wiremock` docs: https://docs.rs/wiremock/latest/wiremock/
- `wiremock::MockServer` docs (per-test isolation guidance): https://docs.rs/wiremock/latest/wiremock/struct.MockServer.html
- `testcontainers` docs: https://docs.rs/testcontainers/latest/testcontainers/
- Testcontainers system requirements (Docker-API-compatible runtime, weaker guarantees for alternatives): https://rust.testcontainers.org/system_requirements/docker/
- `assert_cmd` docs: https://docs.rs/assert_cmd/latest/assert_cmd/
- `assert_cmd::cargo` limitations docs: https://docs.rs/assert_cmd/latest/assert_cmd/cargo/
- `tempfile` docs: https://docs.rs/tempfile/latest/tempfile/
- `insta` docs: https://docs.rs/insta/latest/insta/
- Insta redactions docs: https://insta.rs/docs/redactions/
- `cargo-nextest` record/replay docs: https://nexte.st/docs/features/record-replay/
- `cargo-nextest` portable recordings docs: https://nexte.st/docs/features/record-replay-rerun/portable-recordings/
- `cargo-nextest` recording-architecture docs: https://nexte.st/docs/design/architecture/recording-runs/

**Conclusion:** the gap is **not** “Rust has no testing tools”, **not** “every crate needs its own bespoke mock stack”, **not** “portable test recordings already equal a supported local recipe”, and **not** “snapshot normalization already defines semantic truth”. The sharper gap is a **crate-authored test-surface / fixture-catalog / topology-honesty / witness-lineage / normalization-boundary / diff layer** above today’s runners, mock helpers, property-testing tools, compile-fail harnesses, replay substrate, and snapshot tools.


## Crate observability-surface / signal-contract substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (docs + code remain the main learning surfaces; debugging/resource usage remain visible pains): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tokio tracing topic docs: https://tokio.rs/tokio/topics/tracing
- `tracing` docs: https://docs.rs/tracing/latest/tracing/
- `tracing-subscriber` docs: https://docs.rs/tracing-subscriber/latest/tracing_subscriber/
- `EnvFilter` docs: filters may be global or per-layer, and regex field matching should be disabled for potentially untrusted input. https://docs.rs/tracing-subscriber/latest/tracing_subscriber/filter/struct.EnvFilter.html
- `console-subscriber` docs: tokio-console route still requires Tokio `tracing` support and `tokio_unstable` on the Tokio path. https://docs.rs/console-subscriber/latest/console_subscriber/
- `tracing-opentelemetry` docs: traces and metrics are supported, but logs are not. https://docs.rs/tracing-opentelemetry/latest/tracing_opentelemetry/
- OpenTelemetry Rust docs: traces, metrics, and logs are beta in Rust. https://opentelemetry.io/docs/languages/rust/
- OpenTelemetry instrumentation-libraries docs: docs team still does not know of any Rust library with native OTel integrated by default. https://opentelemetry.io/docs/languages/rust/libraries/
- OpenTelemetry semantic conventions docs: https://opentelemetry.io/docs/concepts/semantic-conventions/
- OpenTelemetry schemas docs: semantic drift is carried through schema URLs. https://opentelemetry.io/docs/specs/otel/schemas/
- OpenTelemetry logs docs: structured logs and stable schema matter operationally. https://opentelemetry.io/docs/concepts/signals/logs/
- OpenTelemetry handling-sensitive-data docs: implementers remain responsible for reviewing emitted telemetry fields. https://opentelemetry.io/docs/security/handling-sensitive-data/

**Conclusion:** the gap is **not** “Rust has no tracing stack”, **not** “we just need another exporter or dashboard”, and **not** “semantic conventions already publish one crate’s support story.” The sharper gap is a **crate-authored observability-surface / signal-stability / activation-recipe / bridge-route / schema-posture / sensitivity-boundary / diff layer** above today’s tracing, filtering, console, exporter, and semconv substrate.

- `console-subscriber` `init()` docs: the easiest start path also requires a runtime that emits compatible tracing events. https://docs.rs/console-subscriber/latest/console_subscriber/fn.init.html
- `console-subscriber::Builder::init` docs: configures the default tracing subscriber and console layer. https://docs.rs/console-subscriber/latest/console_subscriber/struct.Builder.html
- `tokio-metrics::RuntimeMonitor::intervals` docs: runtime metrics are sampled as interval bundles rather than timeless facts. https://docs.rs/tokio-metrics/latest/tokio_metrics/struct.RuntimeMonitor.html


## Toolchain & target support-contract substrate
- Rust vision doc (supportive interfaces from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (stable compiler use remains dominant; docs and code are main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- rustup overrides: https://rust-lang.github.io/rustup/overrides.html
- rustup profiles: https://rust-lang.github.io/rustup/concepts/profiles.html
- rustup channels / nightly availability: https://rust-lang.github.io/rustup/concepts/channels.html
- Cargo config (`build.target`, target-specific linker/runner, target-vs-host `rustflags` behavior): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo targets: https://doc.rust-lang.org/cargo/reference/cargo-targets.html
- docs.rs metadata: https://docs.rs/about/metadata
- docs.rs builds/sandbox: https://docs.rs/about/builds
- docs.rs default-target change: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- target tier policy: https://rust-lang.github.io/rfcs/2803-target-tier-policy.html
- rustup 1.29.0 release notes: https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/

**Conclusion:** the gap is **not** “Rust has no installer”, **not** “we only need a linker doctor”, and **not** “docs.rs metadata already tells the whole support story”. The sharper gap is a **whole-project support contract** that keeps override lineage, component availability, exercise scope, evidence provenance, and external prerequisites separately reviewable.

## Added 2026-03-18 (239)

### Android native-library shipping substrate refresh
- `cargo-ndk` already provides Android target env setup, target installation helpers, and `jniLibs`-oriented output handling. https://github.com/bbqsrc/cargo-ndk
- UniFFI already documents Kotlin bindings for supported interface shapes, which proves real Android/JVM-facing binding substrate exists without solving packaging/distribution by itself. https://mozilla.github.io/uniffi-rs/latest/kotlin/overview.html
- `cargo-apk` already packages APKs from Rust crates and exposes Android/mobile workflow substrate such as build, run, and debugger hooks. https://github.com/rust-mobile/cargo-apk
- `cargo-mobile2` already provides active Rust/mobile project generation and run workflows, though it is explicitly scoped by its maintainers and not a generic Android library shipping contract. https://github.com/tauri-apps/cargo-mobile2
- Android NDK docs already define native libraries in AARs, package structure, and collision hazards such as `libc++_shared.so`. https://developer.android.com/ndk/guides/libs
- Android JNI guidance already documents thread/env and marshalling constraints, which means some “it loads” problems are already concrete policy/interop seams rather than folklore. https://developer.android.com/training/articles/perf-jni
- Android page-size guidance already makes 16 KB support an explicit release-policy concern for modern 64-bit Android targets. https://developer.android.com/guide/practices/page-sizes
- Rust release notes already show Android NDK floor expectations shifting over time. https://doc.rust-lang.org/beta/releases.html

**Conclusion:** the gap is **not** “Rust cannot target Android”, **not** “there is no binding substrate”, and **not** “mobile tool wrappers are absent.” The sharper gap is a **cargo-native Android library shipping contract / ABI-coverage report / load-doctor / page-size-readiness bundle** above those surfaces.


## Added 2026-03-18 (240)

### Python extension shipping / free-threading / packaging-variant substrate
- PyO3 building and distribution docs (`abi3`, extension-module build surface): https://pyo3.rs/v0.28.2/building-and-distribution
- PyO3 multiple-version support docs (`abi3` and version-floor features): https://pyo3.rs/v0.28.2/building-and-distribution/multiple-python-versions
- PyO3 free-threading guide (`gil_used`, thread-safety posture, `Py_GIL_DISABLED`): https://pyo3.rs/v0.28.2/free-threading
- Python free-threaded extension HOWTO (stable ABI currently unsupported for free-threaded builds; separate wheels needed): https://docs.python.org/3/howto/free-threading-extensions.html
- What’s new in Python 3.14 (free-threaded Python officially supported): https://docs.python.org/3/whatsnew/3.14.html
- maturin changelog (free-threaded support, `3.13t`/`3.14` behavior, recent fixes): https://www.maturin.rs/changelog.html
- maturin issue #3064 (`abi3.abi3t` support still in flight): https://github.com/PyO3/maturin/issues/3064
- cibuildwheel options docs (`3.13` opt-in vs `3.14+` ordinary free-threaded support): https://cibuildwheel.pypa.io/en/stable/options/
- PEP 803 (`abi3t`): https://peps.python.org/pep-0803/
- PEP 825 (wheel variants package format): https://peps.python.org/pep-0825/

**Conclusion:** the gap is **not** “Rust lacks Python extension tooling”, **not** “free-threaded support makes `abi3` automatically cover everything”, and **not** “accepted future PEPs mean today’s release tooling already supports them.” The sharper gap is a **Python-extension compatibility contract layer** with explicit ABI target class, thread-support declaration, and variant-horizon honesty above the existing PyO3/maturin/cibuildwheel substrate.

## Added 2026-03-18 (63)

### Apple XCFramework / SwiftPM substrate refresh
- UniFFI Swift Xcode integration: https://mozilla.github.io/uniffi-rs/latest/swift/xcode.html
- UniFFI docs.rs (`cargo swift` adjacency): https://docs.rs/crate/uniffi/latest
- `cargo swift` README: https://github.com/antoniusnaumann/cargo-swift/blob/main/README.md
- `xcframework` crate docs (`0.2.1`): https://docs.rs/xcframework/latest/xcframework/
- SwiftPM binary-target docs (`url` + `checksum`, or `path`): https://docs.swift.org/package-manager/PackageDescription/PackageDescription.html
- Apple binary-framework distribution docs for Swift packages: https://developer.apple.com/documentation/xcode/distributing-binary-frameworks-as-swift-packages
- Apple XCFramework origin verification docs: https://developer.apple.com/documentation/xcode/verifying-the-origin-of-your-xcframeworks
- Apple privacy manifest docs for apps and third-party SDKs: https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk
- Apple third-party SDK requirements: https://developer.apple.com/support/third-party-SDK-requirements/

**Conclusion:** the gap is **not** “Rust has no Swift/Apple shipping substrate” and not “an XCFramework helper already makes Apple distribution boring.” The sharper gap is a **slice-coverage / wrapper-alignment / trust-posture receipt layer** for shipping Rust-built Apple SDKs.


## Added 2026-03-18 (64)

### NuGet / .NET native substrate refresh
- NuGet native files in .NET packages: https://learn.microsoft.com/en-us/nuget/create-packages/native-files-in-net-packages
- RID catalog: https://learn.microsoft.com/en-us/dotnet/core/rid-catalog
- unmanaged library loading algorithm: https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/loading-unmanaged
- plugin-host tutorial (`AssemblyDependencyResolver`): https://learn.microsoft.com/en-us/dotnet/core/tutorials/creating-app-with-plugin-support
- Native AOT interop: https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/interop
- host determines RID-specific assets (.NET 8): https://learn.microsoft.com/en-us/dotnet/core/compatibility/deployment/8.0/rid-asset-list
- single-file native-library search breaking change (.NET 10): https://learn.microsoft.com/en-us/dotnet/core/compatibility/interop/10.0/native-library-search
- native interop best practices (`LibraryImport`): https://learn.microsoft.com/en-us/dotnet/standard/native-interop/best-practices
- csbindgen: https://github.com/Cysharp/csbindgen

**Conclusion:** the gap is **not** “Rust lacks C# binding generators”, **not** “NuGet has no native-package story”, and **not** “one local app load proves deployment support.” The sharper gap is a **NuGet native interop shipping-contract layer** with explicit RID coverage, loader-route truth, and deployment-posture honesty above existing package, runtime, and binding substrate.

## Added 2026-03-18 (Hex deepening)
- `rustler_precompiled` now explicitly documents that precompilation happens in CI, that the Hex package should always include a checksum file, and that the checksum file is mandatory for the package to work. https://hexdocs.pm/rustler_precompiled/precompilation_guide.html
- The same guide now keeps the target × NIF-version matrix explicit and states that NIF versions are more stable than OTP versions; it also maps `2.15` to OTP 22+, `2.16` to OTP 24+, and `2.17` to OTP 26+. https://hexdocs.pm/rustler_precompiled/precompilation_guide.html
- Erlang system docs still make `erlang:load_nif/2` and fallback stub implementations explicit, which means load-path and fallback behavior are real contract surfaces rather than folklore. https://www.erlang.org/doc/system/nif.html
- Erlang common caveats still warn that doing too much work in each NIF call can degrade VM responsiveness, so “the NIF loads” is not the whole story. https://www.erlang.org/doc/system/commoncaveats.html
- `hex_core` continues to make package tarball creation/unpack plus outer checksum vocabulary explicit, which gives the archive a stable package-receipt substrate. https://hexdocs.pm/hex_core/hex_tarball.html
- Real package changelogs now show the exact maintenance seams this proposal cares about: `mjml` changing target coverage and local-build behavior, and `pcap_file_ex` fixing missing checksum files in the Hex package plus artifact naming drift. https://hexdocs.pm/mjml/changelog.html ; https://hexdocs.pm/pcap_file_ex/0.1.5/changelog.html

## Added 2026-03-18 (246)

### JAR/JNI shipkit / current JVM-native packaging substrate
- Oracle `System.loadLibrary` docs now explicitly say it is a restricted method and that programs can only use it when access to restricted methods is enabled: https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html
- JNI spec intro now explicitly says loading native libraries or declaring native methods in modules without native access will result in exceptions and/or warnings: https://docs.oracle.com/en/java/javase/25/docs/specs/jni/intro.html
- Current JDK migration guidance explains `--enable-native-access=M1,M2,...` for named modules and `--enable-native-access=ALL-UNNAMED` for class-path code: https://docs.oracle.com/en/java/javase/26/migrate/migrating-from-jdk-8-later-jdk-releases.html
- Maven deploy-plugin docs keep attached classifiers an ordinary publication mechanism: https://maven.apache.org/plugins/maven-deploy-plugin/examples/deploying-with-classifiers.html
- Sonatype Central now documents Maven-plugin publication via the Central Publisher Portal: https://central.sonatype.org/publish/publish-portal-maven/
- `os-maven-plugin` documents normalized OS/arch properties and `${os.detected.classifier}` as a de-facto classifier dialect: https://github.com/trustin/os-maven-plugin
- `jni` docs still describe a mostly safe Rust JNI surface and show both exported native methods and explicit registration paths: https://docs.rs/jni

**Conclusion:** the gap is **not** “Rust lacks JVM interop substrate”, **not** “Maven cannot publish the artifacts”, and **not** “native access is just invisible runtime plumbing”. The sharper remaining gap is a **producer-side JAR/JNI release contract** above classifier dialect, loader residency, and native-access posture.


## Added 2026-03-18 (247)

### R / CRAN compiled-package substrate refresh
- `rextendr` already scaffolds Rust-backed R packages with `src/entrypoint.c`, `src/Makevars`, `src/Makevars.win`, a Rust crate, and generated wrappers: https://extendr.rs/rextendr/articles/package.html
- `extendr_module!` already gives Rust-backed packages a real exported-module surface for R bindings: https://extendr.github.io/extendr/extendr_api/macro.extendr_module.html
- R’s extension manual still makes native routine registration and `useDynLib(..., .registration = TRUE)` explicit package-namespace substrate: https://cran.r-project.org/doc/manuals/r-devel/R-exts.html
- R Internals still makes it explicit that compiled code is ordinarily loaded via `useDynLib` or `.onLoad`/`library.dynam` and installed under `libs/`: https://cran.r-project.org/doc/manuals/r-devel/R-ints.html
- Current `R CMD INSTALL` docs still make sub-architecture behavior and staged installation explicit for compiled-code packages: https://cran.r-project.org/doc/manuals/r-patched/packages/utils/refman/utils.html
- Current R administration docs still distinguish Windows/macOS binary-package intake from source installs that require compiled-code toolchains, and note that compiled-code binaries are tied to OS/R-series realities: https://cran.r-project.org/doc/manuals/r-devel/R-admin.html
- There are now many Rust-backed packages on CRAN, which proves the lane is no longer hypothetical: https://github.com/nanxstats/r-rust-pkgs

**Conclusion:** the gap is **not** “Rust cannot target R”, **not** “there is no package scaffolding”, and **not** “R lacks compiled-package loading rules.” The sharper gap is a **producer-side R-package shipping contract** above registration posture, DLL-load truth, and binary-versus-source install honesty.


## Added 2026-03-18 (248)

### RubyGems / Bundler / Rust native-gem substrate refresh
- Bundler now officially scaffolds Rust extensions with `bundle gem --ext=rust`, currently magnus-based: https://bundler.io/man/bundle-gem.1.html
- RubyGems still documents `spec.extensions`, `spec.platform`, and `require_paths`, including that extension build output is copied into `lib/`: https://guides.rubygems.org/specification-reference/
- RubyGems still documents install-time extension builds and the standard native-extension gem layout: https://guides.rubygems.org/gems-with-extensions/
- Bundler’s current Gemfile docs explicitly distinguish Ruby-engine/implementation-style `platforms:` from the OS/arch values understood by `bundle lock --add-platform`: https://bundler.io/man/gemfile.5.html
- Bundler’s cache docs make multi-platform caching and remote fetch behavior for platform gems explicit, including `--all-platforms`: https://bundler.io/man/bundle-cache.1.html
- RubyGems trusted publishing now uses OIDC and short-lived tokens instead of long-lived credentials: https://guides.rubygems.org/trusted-publishing/
- RubyGems now has a first-party `gem rebuild` command and notes that reproducing a build depends on matching the RubyGems version used in gem metadata: https://guides.rubygems.org/command-reference/
- The official `rubygems/release-gem` action now supports trusted publishing and still assumes a Bundler-based release flow: https://github.com/rubygems/release-gem
- `rb-sys` still positions itself as the Rust-native-extension substrate for Ruby and explicitly points to cross-platform development/testing docs: https://github.com/oxidize-rb/rb-sys
- `magnus` remains the higher-level Rust-side authoring layer for Ruby extensions: https://docs.rs/magnus
- oxidize.rb deployment docs now explicitly frame precompiled “fat gems” as the ordinary way to avoid requiring the Rust toolchain on end-user machines: https://oxidize-rb.org/docs/deployment/

**Conclusion:** the gap is **not** “Rust cannot target Ruby”, **not** “Bundler lacks Rust scaffolding”, and **not** “RubyGems cannot express binary gems.” The sharper gap is a **producer-side Ruby native-gem shipping contract** above platform coverage, resolver routes, and extension residency.


## Added 2026-03-19 (251)

### LittleFS / embedded flash filesystem substrate
- Upstream `littlefs` still defines the core value proposition around power-loss resilience, dynamic wear leveling, and bounded RAM/ROM: https://github.com/littlefs-project/littlefs
- `littlefs2` remains the main idiomatic Rust wrapper path and still documents a C backend via `littlefs2-sys`: https://docs.rs/crate/littlefs2/latest
- `littlefs2-sys` still exposes C build/link reality and explicitly says the `string.c` file is GPL-2.0 and that a permissively licensed replacement is welcome: https://github.com/trussed-dev/littlefs2-sys
- The upstream littlefs issue tracker had a 2025 request explicitly asking whether a pure-Rust implementation was wanted, which shows the demand was real before the current month’s release activity: https://github.com/littlefs-project/littlefs/issues/1112
- As of 2026-03-10, `littlefs-rust` publicly documents a safe Rust API built on a function-by-function Rust port of the C implementation, which means raw feasibility is no longer the main missing story: https://docs.rs/littlefs-rust/latest/src/littlefs_rust/lib.rs.html
- The wider embedded stack now has `embedded-storage-async` for async storage traits and Embassy utilities for flash partitioning / in-memory simulation: https://docs.rs/embedded-storage-async/latest/embedded_storage_async/ and https://docs.rs/embassy-embedded-hal/latest/embassy_embedded_hal/
- Long-running issue history around async SPI with littlefs shows that async/blocking honesty is still a real seam: https://github.com/littlefs-project/littlefs/issues/143

**Conclusion:** the gap is no longer simply “prove LittleFS can exist in Rust.” The sharper gap is a **LittleFS adoption layer** above engines and wrappers: storage-adapter receipts, compatibility witnesses, power-cut evidence, host-side image tooling, and compact support bundles.


## Added 2026-03-19 (258)

### Crate lifecycle-surface / shutdown-truth substrate refresh
- Rust vision doc (`supportive interfaces` from crates): https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey (online docs and code remain the main learning surfaces): https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Tokio graceful shutdown guide (signal + propagate + wait): https://tokio.rs/tokio/topics/shutdown
- `CancellationToken` docs: https://docs.rs/tokio-util/latest/tokio_util/sync/struct.CancellationToken.html
- `TaskTracker` docs (`wait` until closed and empty): https://docs.rs/tokio-util/latest/tokio_util/task/task_tracker/struct.TaskTracker.html
- Tokio task utilities module (`AbortOnDropHandle`, `JoinMap`, `TaskTracker`): https://docs.rs/tokio-util/latest/tokio_util/task/index.html
- `JoinHandle` docs (drop detaches; `spawn_blocking` abort caveat): https://docs.rs/tokio/latest/tokio/task/struct.JoinHandle.html
- `JoinSet` docs (drop aborts tracked tasks; `detach_all`; `shutdown` aborts then waits): https://docs.rs/tokio/latest/tokio/task/struct.JoinSet.html
- Tokio `select!` docs (definition of cancellation safety): https://docs.rs/tokio/latest/tokio/macro.select.html
- Tokio `AsyncWriteExt` docs (`write`/`flush` vs `write_all` vs `shutdown`): https://docs.rs/tokio/latest/tokio/io/trait.AsyncWriteExt.html
- `async_shutdown` docs (stop running futures + wait for cleanup + shutdown reason): https://docs.rs/async-shutdown/latest/async_shutdown/
- `tokio-graceful-shutdown` docs (signals, subsystem failure/panic, timeout/error propagation): https://docs.rs/tokio-graceful-shutdown/latest/tokio_graceful_shutdown/
- `task_scope` docs (structured concurrency as executor extension; out-of-task concurrency breaks structure): https://docs.rs/task_scope/latest/task_scope/
- `moro` docs (async scope like `std::scope`): https://docs.rs/moro/latest/moro/

**Conclusion:** the gap is **not** “Rust has no shutdown substrate”, **not** “another graceful-shutdown framework would settle lifecycle support”, and **not** “Tokio docs already publish one crate’s lifecycle contract.” The sharper gap is a **crate-authored lifecycle-surface / activation-boundary / stop-semantics / teardown-evidence / drain-recipe layer** above today’s runtime, task, and async-I/O substrate.
