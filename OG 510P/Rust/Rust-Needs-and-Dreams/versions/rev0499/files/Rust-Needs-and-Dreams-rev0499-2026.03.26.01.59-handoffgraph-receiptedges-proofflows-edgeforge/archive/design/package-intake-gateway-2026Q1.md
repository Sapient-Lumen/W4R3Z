## Execution addendum (rev0420)
For execution-oriented questions about what this seam should **actually ship**, read `design/package-intake-gateway-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- this contract note still defines **what the seam is**;
- the execution blueprint now defines **what artifact family, commands, lanes, and anti-goals a serious v0 should have**;
- and neither note should be allowed to impersonate package admission, dependency review, compile-time execution authority, or consumer install.

# Design: Rust package intake gateway 2026Q1 (`cargo intake`, `package-intake-pack/v0`)

## Goal
Define a first-class **package intake boundary** between:
- durable package publication / registry truth,
- local dependency or install selection,
- filesystem extraction / staging,
- and later build / review / install consumers.

The worthy contribution here is **not** another registry, another malware scanner, another sandbox wrapper, or another installer frontend.
It is the missing reviewable layer that says:

**what package payload came from which route, how it was staged locally, what extraction and lock/resolution posture applied, and what later consumers may honestly assume.**

Read this together with:
- [`design/package-admission-stack.md`](./package-admission-stack.md)
- [`design/dependency-review-stack.md`](./dependency-review-stack.md)
- [`design/consumer-install-kit.md`](./consumer-install-kit.md)
- [`design/distribution-route-mobility-stack.md`](./distribution-route-mobility-stack.md)
- [`design/compile-time-capabilities-kit.md`](./compile-time-capabilities-kit.md)
- [`proposals/epic-package-intake-gateway.md`](../proposals/epic-package-intake-gateway.md)

## Why this seam matters now
Fresh official signals made this boundary much sharper than it looked even one revision ago.

- Cargo’s March 21, 2026 security advisory says a vulnerability in the `tar` crate used by Cargo to extract packages during a build can let a malicious crate change permissions on arbitrary directories, and it explicitly tells users of alternate registries to verify impact with their vendor.  
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- Cargo source replacement treats vendoring and mirroring as first-class routes, but says the core assumption is that replacement sources are **exactly the same** as the original source and may not add extra crates.  
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo registries make alternate registries a first-class route with their own index and auth semantics, while crates.io still refuses packages that depend on crates from other registries.  
  https://doc.rust-lang.org/cargo/reference/registries.html
- `cargo package` already exposes a surprisingly rich local packaging/staging boundary: rewritten normalized manifests, always-included `Cargo.lock` by default, flattened symlinks, extraction-and-build verification from a pristine state, and an explicit note that `.cargo_vcs_info.json` is only best-effort and **not verified provenance**.  
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo install` still has distinct semantics that many users blur together: source builds from crates.io or git use a temporary target directory, packaged lockfiles are ignored unless `--locked` is passed, and config discovery starts at `$CARGO_HOME` instead of the local project unless `--path` is used.  
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- crates.io’s January 2026 update added Trusted Publishing-only mode and `pubtime`, which means route trust and freshness inputs are getting better, but they still do not say what happened when a package crossed from registry truth into local machine state.  
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io’s February 2026 policy update says routine malware removals will generally be communicated through RustSec advisories rather than a blog post per case. That makes durable intake artifacts and policy-aware local review more important than ambient announcement watching.  
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- The sandboxed-build-scripts project goal is strategically important, but it governs **compile-time execution authority after intake**, not the route/extraction/staging boundary itself.  
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

Taken together, those signals say the ecosystem is getting stronger at **publish review**, **trust signals**, and **build execution control**, but it still lacks one honest boundary for **package ingress into local machine state**.

## The missing distinction
The archive already had strong adjacent seams, but they are not the same thing:

### Package Admission Stack
Asks:
> what package set and publish evidence were admitted for publication?

That is upstream and registry-facing.
It should stay distinct.

### Dependency Review Stack
Asks:
> what trust, effect, capability, and artifact-link facts apply to a dependency subject or upgrade?

That is review-facing and often lockfile-facing.
It should stay distinct.

### Consumer Install Kit
Asks:
> what candidate was chosen for acquisition, what plan was selected, and what actually mutated the install root?

That is consumer-facing and product-facing.
It should stay distinct.

### Package intake gateway
Asks:
> by what route did this package arrive, what payload and extraction semantics applied, how was it staged, what resolution/lock posture mattered, and what can later build/install/review layers safely import?

That middle boundary is the missing one.

## Shared thesis
A worthy contribution should make six truths explicit without flattening them:

1. **subject truth**
   - crate/package identity
   - requested version / selected version
   - dependency-intake versus install-intake versus packaging-verify context
   - direct source kind (`crates-io`, alternate registry, exact-copy mirror, vendored directory, local registry, git, path, packaged tarball)

2. **route truth**
   - registry / mirror / vendor / local source identity
   - auth and protocol posture (`sparse`, `git`, local directory, direct tarball import, offline cache)
   - route constraints and assumptions (exact-copy, alternate-registry, crates.io-only, private-only)

3. **payload truth**
   - normalized manifest / lockfile presence
   - included files / flattened symlinks / generated metadata
   - payload hash / archive identity / index metadata / `pubtime` if available
   - best-effort versus verified provenance

4. **staging and extraction truth**
   - where the package was staged or unpacked
   - what guard posture applied during extraction
   - what filesystem mutations were intended, observed, refused, or unknown
   - whether verification rebuilt from a pristine extracted state, was skipped, or was lossy

5. **resolution truth**
   - packaged-lockfile used, ignored, regenerated, unavailable, or offline-constrained
   - alternate-registry assumptions used during packaging or installation
   - exact dependency-resolution continuity versus latest-compatible recomputation

6. **handoff truth**
   - what later belongs to dependency review, compile-time authority, build-state evidence, consumer install, package admission, or incident response
   - what this intake artifact may honestly claim on its own

## Core artifact family
### 1) `intake-subject/v0`
Describes the exact intake subject:
- crate/package id
- selected version and requested selector
- route class
- initiating operation (`dependency-fetch`, `package-verify`, `install-source-build`, `offline-vendor-import`, `local-registry-import`, `unknown`)
- caller / workspace / install-root context

### 2) `intake-route-report/v0`
Captures how the package was reached:
- registry / mirror / vendor / local-path / tarball identity
- protocol (`sparse`, `git`, `directory`, `file`, `unknown`)
- source-replacement / alternate-registry / private-registry posture
- relevant auth and policy notes
- freshness inputs such as `pubtime` when available
- route assumptions and ambiguity notes

### 3) `intake-payload-report/v0`
Captures what payload was actually under intake:
- archive identity and hashes
- normalized manifest summary
- packaged lockfile posture
- file listing or pointer
- symlink-flattening notes
- `.cargo_vcs_info.json` presence and “best-effort only” warning when relevant
- payload-level warnings / omissions

### 4) `intake-staging-receipt/v0`
Captures local staging / extraction / verification:
- staging root / temp root / cache root / extracted root
- extraction mode and guard posture
- observed mutation classes (`created`, `chmod`, `symlink-flattened`, `skipped`, `blocked`, `unknown`)
- verification mode (`pristine-build`, `no-verify`, `lossy-import`, `unknown`)
- timestamps, runner identity, partial-failure notes

### 5) `intake-decision-brief/v0`
A concise human/assistant summary:
- what route and payload were used
- what extraction / staging posture applied
- what lock/resolution posture applied
- key warnings
- explicit `OK`, `WARN`, `HOLD`, `INCONCLUSIVE` outcome for the intake event itself

### 6) `intake-handoff/v0`
Bounded exports for:
- dependency review
- compile-time authority / build execution
- package admission comparison
- consumer install
- incident response
- assistants / support

### 7) `package-intake-pack/v0`
Attachable bundle linking the above artifacts plus optional imported raw attachments.

## Reference CLI shape
A reference companion could look like:
- `cargo intake resolve`
  - emit `intake-subject/v0` + `intake-route-report/v0`
- `cargo intake inspect`
  - emit `intake-payload-report/v0`
- `cargo intake stage`
  - emit `intake-staging-receipt/v0`
- `cargo intake brief`
  - emit `intake-decision-brief/v0`
- `cargo intake handoff --to <dep-review|build|install|incident|assistant>`
  - emit `intake-handoff/v0`
- `cargo intake pack`
  - build `package-intake-pack/v0`
- `cargo intake verify-pack <path>`
  - verify schema versions, checksums, route markers, and handoff boundaries

The important part is not the command spelling.
The important part is the **portable artifact family**.

## Ranked execution lanes
### 1) Ordinary crates.io dependency fetch / package verify lane
Prove:
- route truth for crates.io,
- payload truth from `.crate`,
- staging/extraction receipt,
- bounded handoff into dependency review and build.

### 2) Alternate-registry / source-replacement lane
Prove:
- alternate-registry identity,
- exact-copy mirror assumptions,
- route distinction between replacement, private registry, and vendored directory,
- explicit ambiguity and vendor-verification notes.

### 3) `cargo install` source-build lane
Prove:
- packaged-lockfile used versus ignored,
- temporary target-dir behavior,
- config-discovery posture,
- handoff into consumer install receipts.

### 4) Offline vendor / local-registry lane
Prove:
- route truth when the network is absent,
- preserved exact-copy assumptions,
- local mirror / vendor provenance notes,
- bounded handoff into airgapped workflows.

### 5) Incident-response lane
Prove:
- a prior intake event can be re-opened when a later advisory or extraction bug appears,
- route and staging semantics remain inspectable,
- consumers can tell whether the issue belonged to publication, intake, build execution, or installation.

## Relationship to older lessons
This design tries to learn the right lesson from older Rust supply-chain and build debates:
- **not** every problem is “malware scanning”; sometimes the seam is route and staging truth;
- **not** every problem is “sandbox build scripts”; package ingress itself is already a boundary;
- **not** every problem is “just use `--locked`”; lock posture is one field inside a larger intake event;
- **not** every problem is “trust the registry”; alternate registries, source replacement, and local mirrors already complicate that story;
- **not** every problem is “make a better installer”; intake also matters for dependency fetch and packaging verification.

## What not to build
Do **not** turn this into:
- a new registry product,
- a universal malware verdict engine,
- a replacement for `cargo package`, `cargo fetch`, `cargo install`, or registry implementations,
- a generic archive-extraction library marketed as ecosystem strategy,
- or a giant package-manager abstraction that erases Cargo’s actual route semantics.

## Success bar
This becomes worthy when a maintainer, security reviewer, downstream packager, registry operator, or assistant can answer:
- where the package came from,
- what exact payload was staged,
- what extraction/staging semantics applied,
- what lock/resolution posture mattered,
- which later review or install layers still need to run,
- and whether a later incident belongs to publication, intake, build execution, or install,

without reconstructing the story from registry tabs, shell transcripts, temp directories, and folklore.
