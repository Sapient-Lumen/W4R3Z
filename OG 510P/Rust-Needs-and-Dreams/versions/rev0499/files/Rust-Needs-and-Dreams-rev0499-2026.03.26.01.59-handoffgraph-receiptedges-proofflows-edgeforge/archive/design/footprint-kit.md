# Design: Footprint Kit (`cargo footprint`, `footprint-pack/v0`)

## Goal
Define a portable contract for planning, measuring, diffing, and reviewing Rust artifact resource footprints: native binary size, section layout, Wasm retained size, stack usage, and allocation/heap behavior.

This should **not** replace `cargo-bloat`, `twiggy`, `cargo-call-stack`, `cargo-llvm-lines`, linker maps, `cargo-binutils`, `dhat`, jemalloc profilers, or Cargo profile tuning.
It should make them compose better and make footprint claims reviewable.

Current posture in the archive: **companion kit / evidence substrate**. Footprint Kit is now the footprint half of a broader **Resource Evidence Stack** with Perf Labs. That shared frontier should make release, compile/storage, and deployment-resource reviews easier without flattening size, stack, allocation, and performance into one metric.

## References (signals)
- Cargo profiles already expose the tuning knobs that teams use for footprint work: `opt-level`, `strip`, `lto`, `panic`, `incremental`, and `codegen-units`. That is strong evidence the optimization surface is real, but Cargo does not define a shared footprint-report artifact above those knobs.
  https://doc.rust-lang.org/cargo/reference/profiles.html
- The embedded book explicitly teaches the speed-vs-size tradeoff, which is a useful reminder that footprint is a first-class engineering concern rather than a post-hoc metric.
  https://docs.rust-embedded.org/book/unsorted/speed-vs-size.html
- The Embedonomicon and embedded runtime docs make memory layout, RAM/FLASH section placement, and stack placement explicit parts of executable correctness on constrained targets.
  https://docs.rust-embedded.org/embedonomicon/memory-layout.html
  https://docs.rs/cortex-m-rt/latest/src/cortex_m_rt/lib.rs.html
- `cargo-bloat` exists because developers need to know what takes space in native executables, but its scope is still a point tool.
  https://docs.rs/crate/cargo-bloat/latest/source/
- The Rust/Wasm book says size profiling should guide shrinking efforts and recommends `twiggy`, which shows the Wasm lane already has strong tooling but not a shared cross-target contract.
  https://rustwasm.github.io/book/reference/code-size.html
  https://rustwasm.github.io/book/reference/tools.html
- `cargo-call-stack` plus `-Z emit-stack-sizes` show that stack usage analysis is possible, but the compiler metadata path is unstable and LLVM only emits it for ELF object formats. That is exactly the kind of capability/coverage nuance a shared contract should record explicitly.
  https://docs.rs/crate/cargo-call-stack/0.1.0
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/emit-stack-sizes.html
- `cargo-llvm-lines` demonstrates that monomorphization growth is often a root cause for executable size and compile-time pain, but it currently does not attach naturally to release or regression review artifacts.
  https://docs.rs/crate/cargo-llvm-lines/latest
- `cargo-binutils` exposes lower-level object/section inspection without defining one normalized policy/report layer above it.
  https://docs.rs/crate/cargo-binutils/latest
- `dhat` and jemalloc profiling crates demonstrate that runtime allocation evidence exists, but via tool- and allocator-specific pathways rather than one portable reporting surface.
  https://docs.rs/dhat/latest/dhat/
  https://docs.rs/tikv-jemalloc-ctl/latest/tikv_jemalloc_ctl/profiling/index.html
  https://docs.rs/jemalloc_pprof/latest/jemalloc_pprof/
- Rust's 2024 annual survey explicitly called out large binary size of compiled artifacts. That is a strong ecosystem-wide signal that footprint review matters beyond embedded specialists.
  https://raw.githubusercontent.com/rust-lang/surveys/main/surveys/2024-annual-survey/report/annual-survey-2024-report.pdf

## Core components

### 1) `footprint-budget/v0`
Describes what resource promises matter.

Required ideas:
- subject identity (crate/workspace/revision/artifact)
- artifact kind (`bin`, `cdylib`, `staticlib`, `wasm`, `firmware`, `example`, `bench`)
- target / profile / feature / cfg / allocator / linker assumptions
- resource dimensions in scope:
  - total artifact bytes
  - section budgets (`.text`, `.rodata`, `.data`, `.bss`, debug-info policy)
  - Wasm retained-size or export-surface budgets
  - stack budgets (`task`, `interrupt`, `call-root`, `global-max`)
  - heap/allocation posture (`no-alloc`, bounded-init-only, sampled-runtime, profile-attached)
  - optional startup/runtime memory notes
- threshold classes (`hard-fail`, `warn`, `track-only`)
- comparison baseline (`main`, `last-release`, `board-profile`, `named-budget-id`)
- measurement coverage requirements (`static-required`, `runtime-required`, `best-effort`, `unsupported-allowed`)

Design rule: **make the dimensions explicit instead of collapsing them into one “size score.”**
A 15 kB `.text` regression is not the same thing as a higher stack bound or a noisier allocator profile.

### 2) `footprint-measurement-report/v0`
Records what was actually measured and how.

Should support:
- linked `footprint-budget/v0`
- tool identities / versions / toolchains
- measured target/profile/feature/config set
- coverage matrix by dimension (`measured`, `unsupported`, `not-run`, `partial`)
- normalized summaries for:
  - native executable / library bytes
  - section breakdowns
  - symbol or retained-size hot spots
  - stack bounds and call roots where available
  - codegen expansion indicators (`llvm-lines`, monomorphization counts, instantiation hot spots)
  - heap/allocation summaries when runtime profilers are used
- raw attachment pointers (map file, `twiggy` output, `cargo-bloat` table, `cargo-call-stack` graph, `dhat` file, allocator dumps)
- limitations and caveats (`ELF-only`, `Wasm-only`, `allocator-specific`, `sampling`, `unstable-flag-required`)

This is the missing “what exactly did we measure, under what assumptions?” artifact.

### 3) `footprint-diff-report/v0`
Summarizes changes against a chosen baseline.

Should record:
- baseline identity and comparison method
- per-dimension deltas (`+13.2% .text`, `-8.4% Wasm retained bytes`, `stack bound unchanged`, `heap peak unknown`)
- policy verdicts (`pass`, `warn`, `fail`, `inconclusive`)
- candidate reason codes:
  - `profile-change`
  - `dependency-growth`
  - `monomorphization-growth`
  - `debug-info-policy-change`
  - `allocator-change`
  - `linker-layout-change`
  - `new-export-surface`
  - `measurement-coverage-change`
- optional correlated evidence from Config Set / Public API / Migration / Release Pipeline kits

A good diff report is about **review**, not just collection.

### 4) `footprint-pack/v0`
Bundle containing:
- `footprint-budget/v0`
- one or more `footprint-measurement-report/v0`
- optional `footprint-diff-report/v0`
- optional raw attachments and rendered summaries

This is the unit that should travel through CI, PR review, release prep, board qualification notes, and downstream archaeology.

### 5) `cargo footprint`
Reference UX:
- `cargo footprint doctor`
- `cargo footprint budget`
- `cargo footprint measure`
- `cargo footprint diff`
- `cargo footprint pack`

`cargo footprint` should begin as an explainer / adapter / packer.
It should not pretend to be a universal profiler or linker replacement.

## What the kit should provide to others
- **Perf Labs:** correlate runtime regressions with explicit artifact/section/stack growth instead of treating performance and footprint as one metric.
- **Config Set Kit:** reuse explicit target/profile/feature selections so footprint claims say what was actually measured.
- **Cross Toolchain Kit / Sysroot Pack Kit:** record when resource numbers depend on custom toolchains, sysroots, linkers, or target-specific standard-library builds.
- **Device Lab Kit:** attach real-device memory/allocator observations to the same footprint story instead of leaving them in board-specific logs.
- **Release Pipeline Kit:** attach footprint packs to release candidates so size/stack regressions are reviewable alongside signatures, SBOMs, and provenance.
- **Migration Kit:** compare before/after resource posture when dependency upgrades, edition changes, or MSRV/toolchain ratchets alter artifact shape.
- **Public API Kit / DocProof Kit:** preserve the distinction between API/docs support claims and deployment/resource support claims, while still allowing a release to attach both.

## Non-goals
- Do **not** define one fake universal score for all resource concerns.
- Do **not** replace profilers, linkers, or allocator-specific tooling.
- Do **not** guarantee stack or heap truth on every target/toolchain.
- Do **not** hide platform limitations such as ELF-only or Wasm-only support.
- Do **not** collapse compile-time size causes and runtime memory observations into one undifferentiated number.

## Overlap boundaries
- **Not Perf Labs:** Perf Labs owns runtime performance/regression evidence; Footprint Kit owns binary/section/stack/allocation budget evidence.
- **Not Config Set Kit:** Config Set chooses measured slices; Footprint Kit records per-slice resource outcomes.
- **Not Release Pipeline Kit:** Release Pipeline packages releases; Footprint Kit supplies one attachable evidence lane.
- **Not Device Lab Kit:** Device Lab owns board/lab execution plans; Footprint Kit may consume board-specific memory evidence from those runs.
- **Not Cross Toolchain / Sysroot Pack Kits:** those kits provision toolchains/stdlib variants; Footprint Kit records how those choices affect measured resources.
- **Not Safety Evidence Kit:** safety/verification claims remain separate; resource budgets are useful constraints but not proof of correctness.

## Why this could matter
A good Footprint Kit would make Rust feel more honest and more usable in constrained deployments.
It would give the ecosystem:
- explicit resource budgets instead of implicit “keep it small” folklore,
- one way to compare section growth, Wasm retained size, stack bounds, and allocator evidence without pretending they are identical,
- better reuse of existing native/Wasm/embedded/runtime tools,
- clearer review lanes for release and migration regressions,
- and a portable way to say what parts of resource posture were actually measured versus merely assumed.


## Next credible move
The archive should now treat a **ranked shared pilot program** as the next real step for Footprint Kit:
- compile-workflow + build-storage evidence first,
- native release-artifact lanes second,
- constrained embedded/Wasm lanes third,
- runtime allocation lanes fourth,
- federated resource-review consumers fifth.

See [`design/resource-evidence-pilot-program.md`](./resource-evidence-pilot-program.md). The point is to prove that footprint evidence composes cleanly with Perf Labs and Cargo build-state evidence before trying to standardize every size/profiling workflow at once.
