# Design: Build Cache pilot program (`cargo cache pilot`, `cache-lane-report/v0`, `cache-pilot-pack/v0`)

## Goal
Give **Build Cache Kit** its own ranked pilot program so the archive proves lane-aware build-cache truth before widening back out into the full **Build-State Evidence Stack**.

The missing contribution is not another cache backend, remote-cache service, or one-number “build acceleration” score.
It is a disciplined rollout that proves Rust projects can publish enough cache-lane evidence that humans and tools can distinguish:
- Cargo-native workspace-local build state,
- editor-private duplication,
- Cargo-native user-wide reuse,
- compiler-wrapper cache reuse,
- container-layer reuse,
- and CI/plugin exchange.

## References (signals)
- Cargo’s build-cache docs now publicly distinguish `build-dir` from `target-dir` and still point users to `sccache` as a separate third-party shared-cache lane.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
- The build-dir-layout goal makes smaller self-contained units, fine-grained locking, reduced rust-analyzer contention, a first-class user-wide cache, and plugin-based remote exchange part of the intended future.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The user-wide-cache goal says today’s cache is per-workspace by default and that ad hoc shared-target-dir use causes cross-project conflicts and `cargo clean` blast radius.
  https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- The Cargo 1.94 cycle says target-dir locking still has tricky fingerprint/upgrade cases and leaves important contention points around proc-macros and build scripts.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The build-dir-layout-v2 call for testing says with Cargo 1.91 users can already separate `build-dir` from `target-dir` and asks the ecosystem to test tools and release processes against the new layout.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- rust-analyzer explicitly offers a private `cargo.targetDir` lane that avoids locking at the expense of duplicate artifacts.
  https://rust-analyzer.github.io/book/configuration.html
- `sccache` and `cargo-chef` remain explicit that they are partial, purpose-shaped lanes with their own caveats and intended environments.
  https://github.com/mozilla/sccache/blob/main/docs/Rust.md
  https://docs.rs/crate/cargo-chef/latest

## Why this needs its own design layer
Without a cache-specific pilot program, the archive is vulnerable to three bad outcomes:
1. **layout theater** — every build-state fact gets flattened into one `target/` story;
2. **hit-rate theater** — wrapper hits, Cargo-native reuse, duplicated editor state, and container-layer reuse all get narrated as one fake cache metric;
3. **CI theater** — coarse tarball restore gets mistaken for entry-aware build-state reuse.

A worthy contribution here should prove a smaller and stronger claim:
> Rust projects can attach enough lane-aware cache evidence that reviewers can tell what kind of reuse, duplication, contention, and exchange actually happened.

## Shared artifact posture
### 1. `cache-lane-profile/v0`
Declares the cache lane under test.

Should record:
- lane identity (`workspace-local`, `editor-private`, `user-wide`, `wrapper`, `container-layer`, `ci-exchange`)
- package/workspace scope
- host/target posture
- build-dir / target-dir posture
- trusted storage or remote-exchange posture
- expected lock/duplication semantics

### 2. `cache-collection-profile/v0`
Declares what evidence was collected.

Should record:
- Cargo-native reports used
- wrapper-native reports used
- container or CI receipts used
- required versus optional evidence
- freshness / currentness rules
- how missing evidence renders (`unknown`, `partial`, `imported`, `inconclusive`)

### 3. `cache-lane-scorecard/v0`
Asks whether the pilot stayed honest.

Should ask:
- did the pilot preserve lane identity explicitly?
- did it separate reuse from duplication-by-policy?
- did it separate local entry existence from remote exchange?
- did it render lock/contention truth explicitly?
- did it mark imports or missing evidence honestly?

### 4. `cache-pilot-pack/v0`
Bundle for review and reuse:
- lane profile
- collection profile
- linked `build-state-pack/v0` or bounded imports
- scorecard
- optional raw attachments or CI receipts

## Ranked first pilots

### 1) Cargo-native split-dir pilot
**Why first**
- Cargo 1.91+ already allows `build-dir` to be separated from `target-dir`.
- This proves the archive can talk about final versus intermediate state without waiting for broader upstream convergence.

**Must prove**
- build-dir and target-dir stay distinct in reports;
- lock scope is rendered explicitly;
- tool breakage from path scraping is treated as lane mismatch, not silent incompatibility;
- final artifacts are not mislabeled as cache entries.

### 2) Editor coexistence pilot
**Why second**
- rust-analyzer contention is one of the most legible inner-loop problems.
- This pilot exercises duplication-by-policy and lock avoidance directly.

**Must prove**
- editor-private target/build dirs stay explicit;
- duplication is not narrated as a miss;
- CLI and editor consumers can compare tradeoffs honestly;
- build scripts/proc-macros are allowed to remain partially contentious when evidence says so.

### 3) Wrapper cache pilot (`sccache` lane)
**Why third**
- `sccache` is the most established shared-cache lane users actually reach for today.
- It is high leverage precisely because it is easy to overclaim.

**Must prove**
- wrapper-owned reuse stays separate from Cargo-native reuse;
- unsupported or caveated inputs remain explicit;
- remote/local backing-store posture is visible;
- wrapper reports are marked as imports, not authoritative Cargo unit truth.

### 4) Container recipe/layer pilot (`cargo-chef` lane)
**Why fourth**
- This is strategically important for production pipelines and easy to misdescribe as ordinary cache reuse.
- It proves the archive can compare recipe/layer reuse honestly against local build-state reuse.

**Must prove**
- recipe identity and stage/toolchain identity remain explicit;
- dependency-layer reuse is not confused with per-unit rustc reuse;
- same-toolchain requirement is captured;
- local interactive builds are not silently treated as the same lane.

### 5) CI / user-wide exchange pilot
**Why fifth**
- This is the biggest long-horizon prize and the easiest place to invent fake wins.
- It should come only after the local lanes are already legible.

**Must prove**
- user-wide Cargo-native reuse stays separate from coarse CI blobs and separate from wrapper remotes;
- upload/download events are not equivalent to actual entry reuse;
- selective exchange or plugin behavior is represented honestly;
- trust/write-back posture remains explicit.

## Immediate archive consequences
Read this file together with:
- `design/build-cache-lane-map.md`
- `design/build-cache-kit.md`
- `proposals/epic-build-cache-kit.md`
- `design/build-state-evidence-stack.md`
- `design/build-state-evidence-pilot-program.md`

## Archive decision
Future build-cache revisions should prefer:
- lane profiles over one universal cache metric,
- lock/duplication reason codes over folklore,
- bounded imports over scraped assumptions,
- and honest `INCONCLUSIVE` states over fake cache-success narratives.
