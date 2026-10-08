# Design: Package Intake Gateway execution blueprint (2026 Q1)

## Goal
Turn the archive's strongest **operationally urgent seam** into a sharper **buildable program**.

The missing contribution is not another generic supply-chain dashboard, another malware feed, another registry clone, another installer monopoly, or another sandbox wrapper.
It is a disciplined companion layer that lets Rust teams carry **reviewable package-ingress truth** from registry or source route into local machine state and onward into dependency review, build execution, install, SBOM, and incident consumers.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team decides to build the archive's most underappreciated urgent seam, what should that contribution actually ship in theory and practice?

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/package-intake-gateway-2026Q1.md`
- `design/package-admission-stack.md`
- `design/dependency-review-stack.md`
- `design/consumer-install-kit.md`
- `design/distribution-route-mobility-stack.md`
- `proposals/epic-package-intake-gateway.md`

## Why this note is needed now
The archive already knew that **Package Intake Gateway** was strategically real.
What it still lacked was a crisper answer to **what the operational seam should look like**.

Fresh official signals sharpen that answer:
- Cargo's March 21, 2026 advisory says a vulnerability in the `tar` crate used by Cargo to extract packages during a build could let a malicious crate change permissions on arbitrary directories, and it explicitly tells users of alternate registries to verify impact with their vendor.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- `cargo package` already describes a real packaging/staging boundary: it rewrites and normalizes the manifest, always includes `Cargo.lock` by default, includes `.cargo_vcs_info.json`, flattens symlinks, extracts the `.crate`, rebuilds from a pristine state to verify it builds, and warns that `.cargo_vcs_info.json` is only a best-effort snapshot rather than verified provenance.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo install` has materially different local-intake semantics: crates.io and git installs build in a temporary target directory by default, packaged lockfiles are ignored unless `--locked` is passed, and configuration discovery begins at `$CARGO_HOME` rather than the local project unless `--path` is used.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo source replacement says replacement sources must be **exactly the same** as the original source and may not add crates that are not present in the original source.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
- Cargo registries make alternate registries first-class, distinguish `git` and `sparse` index protocols, and note that crates.io does not accept packages that depend on crates from other registries.
  https://doc.rust-lang.org/cargo/reference/registries.html
- crates.io's January 2026 update added Trusted Publishing-only mode, which improves publish-side trust posture without by itself recording what happened when a package crossed into local machine state.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io's February 2026 malware-policy update says removed malicious crates will always get a RustSec advisory, which makes durable intake receipts more important than ambient blog watching.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Rust's 2026 flagships explicitly put secure-supply-chain work on public/private dependencies and SBOM support, and Cargo's unstable SBOM precursor emits JSON for compiled artifacts, which means package-ingress truth now has clearer downstream consumers than before.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The sandboxed-build-scripts work is important, but it starts after package ingress and compile-time execution begin; it is not itself the route/extraction/staging boundary.
  https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

Taken together, those signals say the archive should stop describing package intake only as a sharp concept.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's strongest operational seam, the answer should now be:

> Build a **Package Intake Gateway reference layer** that records route, payload, staging, extraction, resolution, and handoff truth as portable review artifacts instead of leaving that story smeared across temp directories, lockfile behavior, registry config, and memory.

That answer is deliberately narrower than “secure the Rust supply chain”.
It is also deliberately stronger than “add more package metadata”.

## What this contribution should be in theory

### Core thesis
A package-intake system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact subject entered local machine state;**
2. **what route and protocol delivered it;**
3. **what payload was actually under intake;**
4. **what staging / extraction / verification posture applied;**
5. **what resolution / lock posture bounded later use;**
6. **what later consumers may honestly import from that intake event.**

If a project cannot answer those questions without raw logs and folklore, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable package-ingress review**.

It should include:
- route and registry/source identity;
- payload and archive truth;
- staging and extraction receipts;
- lock/resolution posture;
- explicit downstream handoff.

It should not become:
- a replacement registry;
- a universal malware oracle;
- a generic archive-extraction sandbox sold as ecosystem strategy;
- or the new official interface for every install, admission, and review workflow.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **subject truth** — what crate/package/version and initiating operation is under review;
- **route truth** — what registry, mirror, vendor directory, local registry, git, path, or tarball route applied;
- **payload truth** — what archive, normalized manifest, lockfile posture, file listing, and provenance hints existed;
- **staging / extraction truth** — where and how the package was unpacked, verified, refused, or left ambiguous;
- **resolution truth** — whether a packaged lockfile, regenerated resolution, offline constraint, or later recomputation applied;
- **consumer-handoff truth** — what dependency review, build execution, install, SBOM, or incident consumers may claim next.

This is the biggest theory/practice guardrail in the whole design.
Without it, every intake event turns into a vague “supply-chain status” blob.

### Adjacency rule
A worthy v0 should stay explicitly adjacent to, but distinct from:
1. **package admission** — publication-side checks and registry policy;
2. **dependency review** — trust, effect, capability, and upgrade reasoning;
3. **compile-time execution authority** — what build scripts or proc macros may do once code starts running;
4. **consumer install** — install-root mutation and lifecycle continuity;
5. **SBOM / incident response** — later artifact-side or response-side consumers.

That is the strategic point of the project.
It gives those layers a cleaner handoff without impersonating them.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo intake resolve`
- `cargo intake inspect`
- `cargo intake stage`
- `cargo intake brief`
- `cargo intake handoff --to <dep-review|build|install|sbom|incident|assistant>`
- `cargo intake pack`
- `cargo intake verify-pack`
- `cargo intake replay`

The tool should **import** Cargo-native behavior when available rather than replacing it.

### Public artifact spine
Keep the current family, but make the review shape more explicit:
- `intake-subject/v0`
- `intake-route-report/v0`
- `intake-payload-report/v0`
- `intake-staging-receipt/v0`
- `intake-resolution-report/v0`
- `intake-decision-brief/v0`
- `intake-handoff/v0`
- `package-intake-pack/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — crate/package/version/selector, initiating operation, workspace/install-root context;
- **authority posture** — observed locally, imported from Cargo/package metadata, imported from registry metadata, or inferred;
- **coverage / completeness** — exact, partial, mixed, policy-limited, stale, unknown;
- **route markers** — registry name, index URL or directory route, protocol, replacement/mirror/vendor posture;
- **payload anchors** — archive digest, normalized manifest digest, lockfile posture, optional file listing digest;
- **staging anchors** — staging root, temp root, verification mode, mutation classes, refusal/blocked notes;
- **consumer limits** — what the next layer may and may not claim;
- **raw attachments** — tarball path or digest, package-file listing, extracted-tree snapshot, Cargo metadata, advisory references, RustSec references when relevant;
- **reason-coded ambiguity** — explicit why for every partial or unsupported answer.

### Commands and what they should emit

#### `cargo intake resolve`
Purpose:
- capture one intake subject;
- record route class, registry/source identity, and initiating operation;
- emit `intake-subject/v0` plus `intake-route-report/v0`.

Important rule:
- if the route name is only partially known, emit a **weaker route report** instead of pretending full certainty.

#### `cargo intake inspect`
Purpose:
- inspect the payload under intake;
- record normalized manifest posture, lockfile posture, file-list posture, symlink flattening notes, and provenance-hint warnings;
- emit `intake-payload-report/v0`.

#### `cargo intake stage`
Purpose:
- capture where and how extraction or pristine verification happened;
- record mutation classes, guard posture, blocked/refused actions, and verify/no-verify posture;
- emit `intake-staging-receipt/v0` plus `intake-resolution-report/v0` when lock/resolution behavior is known.

#### `cargo intake brief`
Purpose:
- tell a human what entered, by what route, under what lock/resolution posture, with what key warnings;
- render the same pack at different depths without inventing new facts.

#### `cargo intake handoff`
Purpose:
- emit narrower downstream exports for dependency review, build execution, install, SBOM, incident response, or assistants without making those slices canonical by themselves.

#### `cargo intake pack`
Purpose:
- assemble the above artifacts plus optional raw attachments into one reviewable `package-intake-pack/v0`.

#### `cargo intake verify-pack`
Purpose:
- validate schema versions, digests, route markers, redaction markers, and handoff boundaries.

#### `cargo intake replay`
Purpose:
- support later incident or support analysis using the recorded route/payload/staging facts without claiming to reproduce the entire original environment automatically.

## Ranked feature set

### P0 — required for a worthy v0
- exact subject capture for crates.io, alternate registry, mirror/vendor, git, path, and local tarball cases;
- explicit route/protocol posture, including source-replacement and alternate-registry distinctions;
- payload inspection with normalized-manifest, lockfile, and provenance-hint posture;
- staging/extraction receipt with mutation classes and verify/no-verify posture;
- explicit distinction between packaged-lock continuity and recomputed resolution;
- one portable pack plus one portable human-readable brief;
- honest `partial`, `policy-limited`, `unknown`, and `inconclusive` states.

### P1 — strong near-term extensions
- install-lane specifics for temp target dirs, config-discovery posture, and root mutations;
- vendor/local-registry replay lanes;
- RustSec/advisory-linked incident handoffs;
- SBOM handoff markers linking ingress truth to later artifact-side precursors;
- policy overlays for internal/private registries.

### P2 — do later or fold elsewhere
- registry mirroring services;
- hosted malware scoring;
- generic quarantine VMs as the primary product;
- full dependency governance or approval workflows;
- turning replay into a false promise of perfectly deterministic reproduction.

## Pilot lanes that best prove the idea

### 1) Ordinary crates.io dependency / package-verify lane
Prove:
- subject, route, payload, staging, and resolution truth for the common case;
- handoff into dependency review and build without extra policy empires;
- honest handling of `cargo package` verify and pristine rebuild posture.

This lane matters because it proves the seam on the path most Rust users already walk.

### 2) Alternate-registry / source-replacement lane
Prove:
- route truth survives mirrors, replacement sources, private registries, and protocol differences;
- exact-copy assumptions are visible rather than implicit;
- advisory and vendor-contact posture can be attached without becoming the whole product.

This lane matters because the March 2026 advisory made route semantics impossible to ignore.

### 3) `cargo install` source-build lane
Prove:
- temp target-dir behavior, lockfile ignore/`--locked` behavior, and config-discovery posture are all explicit;
- the install-facing lane stays separate from package admission and dependency review;
- consumer-install handoffs stay bounded.

This lane matters because many users blur install acquisition into ordinary dependency fetch.

### 4) Vendor / local-registry / offline lane
Prove:
- offline-constrained resolution and local directory routes remain visible;
- vendored and local-registry cases do not disappear into “file path” folklore;
- later SBOM or incident consumers can see how the package actually entered the machine.

### 5) Incident / replay lane
Prove:
- later investigators can answer what route and payload were involved without reconstructing the story from scratch;
- advisory-linked updates and local receipts can meet in one pack;
- the system supports investigation without overstating reproducibility.

This lane should come after ordinary crates.io and install lanes, not before.
That is the whole point.

## Failure modes to avoid

### 1) The generic-supply-chain trap
If the tool starts promising to solve all Rust package security and provenance questions, it will become either vague or imperial.

### 2) The registry-replacement trap
If intake packs silently become alternate registry infrastructure, the project will inherit operating burdens it does not need.

### 3) The sandbox-substitute trap
If the tool pretends that intake receipts replace build-script or proc-macro execution controls, users will misunderstand the threat boundary.

### 4) The install-manager trap
If install-lane exports silently turn into a full package manager story, the project will blur consumer lifecycle and ingress truth.

### 5) The one-advisory trap
If the project is justified only by one scary incident, it will decay when the incident is no longer front-page. The real seam is durable even when the headlines move on.

## What success would look like
A worthy Package Intake Gateway contribution is successful when a later reviewer can answer:
- what package actually entered local machine state,
- by what route and protocol,
- with what payload and provenance-hint posture,
- under what staging / extraction / verification posture,
- with what lock/resolution continuity,
- and which later consumers may honestly import those facts,

without reconstructing the story from temp directories, Cargo folklore, or tribal memory.

## Current recommendation
Keep the broad ladder intact.
Keep **Build-State Evidence** as the strongest one-project answer overall.
Keep **Native Edge Contract** as the active specialist frontier.
Keep **Semantic Context Contract** as the key hidden multiplier.

But when the question is no longer “is Package Intake Gateway strategically real?” and is instead “what should that operational seam actually ship?”, use this blueprint as the canonical answer.
