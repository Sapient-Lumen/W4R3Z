# Design: Support Envelope execution blueprint 2026Q1

## Why this note exists now
The archive already had the right ingredients for **Support Envelope**:
- `design/support-envelope-kit.md`
- `design/support-envelope-pilot-program.md`
- `design/compatibility-claims-stack.md`
- `design/compatibility-claims-pilot-program.md`
- `design/compatibility-claims-lane-map.md`

What it still lacked was the same thing Build-State Evidence, Feedback Loop, Async Capability Commons, Safety-Critical Readiness Commons, Cargo Artifact Contract, Distribution Contract, Workspace Environment, Publisher & Source Identity, Reviewable Edit, and Toolchain Productization now have:

> one direct answer to **what the worthy contribution should actually ship in theory and practice**.

That absence matters because the current ecosystem pressure is no longer only “cross compilation is awkward” or “platform matrices get stale”.
It is that serious Rust teams increasingly need to answer **what exactly they support, for which lane, with what runtime floor, with what host-tool or provisioning posture, with what evidence strength, and what downstream consumers may honestly conclude from that**.

The archive should therefore stop treating Support Envelope as only a kit/pilot inside a broader compatibility band.
It should describe a real contribution shape.

## Fresh signals that force the seam into focus
Primary sources now line up around the same missing middle:
- The rustc target-tier policy still makes lane differences explicit: Tier 2 guarantees that a target builds, while Tier 1 guarantees that it builds and passes all tests; host-tools support is a further, separately governed surface with its own requirements.
  https://doc.rust-lang.org/rustc/target-tier-policy.html
- rustc platform-support pages increasingly record concrete runtime floors and toolchain assumptions rather than just triples. For example, the s390x page names Linux kernel and glibc minimums, while the LoongArch page names kernel, libc or musl, CPU-feature, and host-toolchain expectations.
  https://doc.rust-lang.org/rustc/platform-support/s390x-unknown-linux-gnu.html
  https://doc.rust-lang.org/rustc/platform-support/loongarch-linux.html
- docs.rs metadata already lets authors declare `default-target`, `targets`, and `additional-targets`, while the docs.rs builds page still says all non-`x86_64-unknown-linux-gnu` targets are cross-compiled and `#[cfg(docsrs)]` only affects the final rustdoc invocation, not dependencies or workspace members.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
- docs.rs changed its default target list in October 2025, replacing `x86_64-apple-darwin` with `aarch64-apple-darwin` and `i686-unknown-linux-gnu` with `aarch64-unknown-linux-gnu`. That proves docs-target posture is part of the public support story rather than an internal rendering detail.
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Cargo's `supported-targets` RFC remains a live official attempt to let packages declare support more directly, but it still only covers part of the larger support-envelope problem.
  https://github.com/rust-lang/rfcs/pull/3759
- Cargo's own docs still distinguish `cargo check` from `cargo build`: `check` skips final code generation and can miss diagnostics only emitted during codegen. That makes evidence strength a first-class support question rather than a reporting nicety.
  https://doc.rust-lang.org/cargo/commands/cargo-check.html
  https://doc.rust-lang.org/cargo/commands/cargo-build.html
- Recent official Rust changes keep moving support posture over time: `x86_64-apple-darwin` was demoted to Tier 2 with host tools in Rust 1.90, `aarch64-pc-windows-msvc` was promoted to Tier 1 in Rust 1.91, and release notes continue to record baseline/support changes such as minimum Apple OS raises and new target support.
  https://blog.rust-lang.org/2025/08/19/demoting-x86-64-apple-darwin-to-tier-2-with-host-tools/
  https://blog.rust-lang.org/2025/10/30/Rust-1.91.0/
  https://doc.rust-lang.org/beta/releases.html
- The 2025 State of Rust survey still says online docs are canonical while editor/agentic use is rising. That increases the value of attachable, machine-usable support truth rather than hidden CI lore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, those signals say the missing contribution is not another cross-build wrapper and not a hosted compatibility matrix.
It is a **reviewable support-envelope layer**.

## Headline answer
If one serious team wants to build the archive's clearest remaining platform/runtime/docs support contribution, the answer should now be:

> Build a **Support Envelope reference layer** that captures declared lane support, observed support evidence, runtime-floor truth, host-tool and provisioning posture, support drift, and bounded downstream handoffs; emit reusable reports and packs; and prove the shape across release-artifact, source-build, docs-surface, and long-lived support lanes.

That answer is deliberately narrower than “solve compatibility claims for everything”.
It is also deliberately stronger than “add one more target matrix to the README”.

## What this contribution should be in theory

### Core thesis
A support-envelope system becomes real ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact lane is being claimed** — dev-host, source-build, release-artifact, docs-surface, or runtime-floor attachment;
2. **what exact subject the claim applies to** — crate, workspace, release, binary artifact, package family, optional variant;
3. **what environment or provisioning posture is required** — stock rustup, host tools, cross wrapper, custom target, rebuilt std/sysroot, SDK or libc floor, runner/emulator expectations;
4. **what evidence strength exists for that lane** — declared only, compiled, built, packaged, tested, smoked, field-observed, or manually reviewed;
5. **what changed since the last support claim** — new lane added, runtime floor raised, docs target moved, host-tool support dropped, evidence weakened or strengthened;
6. **what downstream consumers may import** — release notes, docs pages, support policy, safety review, adoption guidance, package-intake policy, assistants, and incident consumers should be able to import selected facts without re-deriving the whole story.

If a project cannot answer those questions without combining target-tier docs, CI matrices, docs.rs settings, release notes, and issue-tracker lore by hand, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable support truth and handoff**.

It should include:
- lane identity capture;
- declared support envelopes;
- runtime-floor and host-tool attachments;
- observed support receipts;
- support diffs and waivers;
- bounded consumer exports and redactions.

It should not become:
- the new universal compatibility badge;
- a hosted matrix portal;
- a replacement for rustc target policy;
- a replacement for docs.rs, rustup, Cargo, or debugger tooling;
- or a universal cross-build runner.

### Separation rule
A worthy contribution here must preserve at least six distinct truth classes:
- **subject truth** — which crate/workspace/release/artifact the claim is about;
- **lane truth** — dev-host vs source-build vs release-artifact vs docs-surface vs runtime-floor attachment;
- **provisioning truth** — host tools, cross toolchains, custom targets, rebuilt stdlib, emulators, SDKs, libc/CRT assumptions;
- **evidence truth** — declared vs compiled vs built vs tested vs packaged vs observed;
- **drift truth** — what changed and why;
- **consumer-handoff truth** — what a specific docs/release/policy/safety/assistant consumer may import.

Without that separation, a green CI build, a docs.rs page, or one release artifact silently becomes “supported”, and the whole layer stops being honest.

### Shape rule
The primary contribution shape should now be:
- **reference layer + report/pack command + observation/diff corpus**.

Why this shape fits:
- **reference layer** because the seam is really about lane identity, evidence vocabulary, and non-collapse rules;
- **report/pack command** because the missing piece is a portable output that teams can diff, publish, and import;
- **observation/diff corpus** because real support stories change over time and must be proven across several lanes, not declared once.

Wrong shapes to refuse first:
- compatibility badge program;
- screenshot matrix generator;
- cross-build wrapper pretending to own support truth;
- docs.rs configuration helper pretending to prove local support;
- release page badge that hides runtime floors and evidence strength.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo supporttruth inspect`
- `cargo supporttruth declare`
- `cargo supporttruth observe`
- `cargo supporttruth diff`
- `cargo supporttruth handoff --to <docs|release|policy|safety|assistant>`
- `cargo supporttruth pack`
- `cargo supporttruth doctor`

The tool should **import** rustc/rustup/Cargo/docs.rs/CI facts where possible rather than replacing those systems.

### Public artifact spine
A credible public artifact family would keep the current kit ideas but make the review spine explicit:
- `support-envelope/v0`
- `runtime-floor-report/v0`
- `support-observation-report/v0`
- `support-diff-report/v0`
- `support-waiver/v0`
- `support-handoff/v0`
- `support-pack/v0`

### First proving lanes
A credible rollout should rank proving lanes instead of pretending every support story lands at once.

#### Lane 1 — released binary / shipped artifact lane
Start where the support question is clearest to downstream users.
This lane proves the archive can describe what is actually shipped for Linux/macOS/Windows and with what evidence strength.

What to prove:
- separate `release-artifact` from `source-build` and `docs-surface`;
- attach runtime floors or mark them explicitly unknown;
- record whether the lane was packaged, smoke-run, or merely built;
- make floor/support diffs visible between releases.

#### Lane 2 — source-build / custom-target lane
This lane proves that “supports target X” can remain honest when the lane depends on cross wrappers, custom targets, or rebuilt stdlib.

What to prove:
- separate stock target support from `build-std` or custom-target posture;
- preserve provisioning backend and host-tool requirements;
- keep `cargo check` and `cargo build` strength visibly different;
- keep declared support distinct from observed support.

#### Lane 3 — docs-surface lane
This lane proves that docs are part of the support story without silently impersonating the whole story.

What to prove:
- capture docs.rs default-target/targets/additional-targets posture;
- record when docs-only targets are representative, convenience-only, or compatibility probes;
- preserve the fact that docs.rs cross-compiles and that `#[cfg(docsrs)]` is local to the final rustdoc invocation;
- export a bounded docs-facing summary rather than a fake support verdict.

#### Lane 4 — runtime-floor derivation lane
This lane proves that runtime floors can be attached honestly and incrementally.

What to prove:
- import explicit upstream floors where they exist;
- record when floors are declared, derived, observed, or unknown;
- preserve CPU-feature and SDK/CRT/libc/kernel assumptions separately;
- keep target triple identity separate from runtime-floor truth.

#### Lane 5 — long-lived support / downstream handoff lane
Only after the earlier lanes work should the pack become a shared import layer for adoption, policy, safety, support, and assistant consumers.

What to prove:
- policy or safety lanes can import support facts without over-claiming verification;
- release and docs lanes can render bounded summaries without erasing uncertainty;
- adoption guidance can distinguish supported, partial, watch, and experimental lanes honestly;
- long-lived support diffs can remain understandable across releases.

## What to refuse
A worthy contribution here must refuse the most tempting wrong shapes:
- another platform badge farm;
- another cross-build convenience layer sold as support truth;
- flattening docs.rs success into local/CI/release support;
- flattening `cargo check` into build/package/run evidence;
- flattening target-tier status into runtime-floor truth;
- flattening custom-target or rebuilt-stdlib success into mainstream support;
- or making the pack depend on one CI vendor, one release host, or one docs surface.

## Ranking and repo consequence
This revision does **not** rewrite the broad ladder.
It does **not** outrank **Build-State Evidence** overall.
It does **not** displace **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked day-to-day missing middle.

What it does do is make one repeatedly promoted seam explicit:
- **Compatibility Claims** remains the broader support/claim-shaping band in the archive;
- **Support Envelope** is now the clearest **platform/runtime/docs support execution blueprint** beneath that broader band;
- its primary shape is now **reference layer + report/pack command + observation/diff corpus**;
- **Acceptance Surface** and imported debugger tuple truth remain adjacent owners rather than the same thing;
- and future release/support/adoption/safety/package-intake/policy work should import this layer rather than rediscovering support truth privately.

That gives the archive a better answer to a pressure cluster that keeps surfacing in official Rust reality:
How should Rust let teams declare, observe, diff, and hand off **support claims** without smearing target tier, host-tool posture, docs targets, runtime floors, cross-build lanes, and evidence strength into one vague word like “supported”?
