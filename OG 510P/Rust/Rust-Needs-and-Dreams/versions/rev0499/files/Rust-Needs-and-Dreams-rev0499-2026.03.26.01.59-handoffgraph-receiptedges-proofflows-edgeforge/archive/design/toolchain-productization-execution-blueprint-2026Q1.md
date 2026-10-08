# Design: Toolchain Productization execution blueprint 2026Q1

## Why this note exists now
The archive already had the right ingredients for **Toolchain Productization**:
- `design/toolchain-productization-contract-2026Q1.md`
- `design/toolchain-productization-stack.md`
- `design/toolchain-productization-lane-map.md`
- `design/toolchain-productization-pilot-program.md`
- `proposals/epic-toolchain-productization-stack.md`

What it still lacked was the same thing Build-State Evidence, Feedback Loop, Async Capability Commons, Safety-Critical Readiness Commons, Cargo Artifact Contract, Distribution Contract, Workspace Environment, Publisher & Source Identity, and Reviewable Edit now have:

> one direct answer to **what the worthy contribution should actually ship in theory and practice**.

That absence matters because the current ecosystem pressure is no longer “sometimes people cross-compile.”
It is that serious Rust users increasingly need to answer **which exact compiler/toolchain family was provisioned, which stdlib/sysroot family was actually built or imported, which activation lane selected it, which hardening or sanitizer lane actually ran, and what later consumers may honestly conclude from that fact pattern**.

The archive should therefore stop treating Toolchain Productization as only a stack/contract/pilot cluster.
It should describe a real contribution shape.

## Fresh signals that force the seam into focus
Primary sources now line up around the same missing middle:
- The accepted `build-std` goal says the next job is an MVP with the potential to be stabilized, and names rebuilding `core`/`std` for non-shipped targets, size or feature tuning, ABI-modifying flags, exploit mitigations, and configuration-sensitive std rebuilds as central use cases.
  https://rust-lang.github.io/rust-project-goals/2025h1/build-std.html
- Cargo's unstable docs still say unstable features are nightly-only, and `build-std` remains in the unstable feature set rather than ordinary stable Cargo surface.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- rustup still models **toolchains**, **profiles/components/targets**, **directory-sensitive overrides**, and **path-linked local toolchains** as distinct control surfaces; a path toolchain also bypasses component/target/profile settings entirely.
  https://rust-lang.github.io/rustup/concepts/toolchains.html
  https://rust-lang.github.io/rustup/overrides.html
- rustup's cross-compilation docs still say that installing a target stdlib is not enough: other tools such as linkers and SDKs are often also required.
  https://rust-lang.github.io/rustup/cross-compilation.html
- rustc's custom-target docs still say target JSON properties are unstable and compiler versions should be pinned when custom targets are used.
  https://doc.rust-lang.org/rustc/targets/custom.html
- The sanitizer docs still recommend rebuilding the standard library with `-Zbuild-std` when enabling CFI, which is strong evidence that runtime-analysis posture and stdlib identity are coupled in practice.
  https://doc.rust-lang.org/beta/unstable-book/compiler-flags/sanitizer.html
- The exploit-mitigations docs make the same pressure broader than sanitizers: Rust now documents a growing matrix of mitigation lanes, several of which are nightly-only or lane-specific rather than one default posture.
  https://doc.rust-lang.org/rustc/exploit-mitigations.html
- The sanitizer-stabilization goal explicitly says stabilization needs infrastructure for **precompiled and instrumented standard libraries**.
  https://rust-lang.github.io/rust-project-goals/2025h2/stabilization-of-sanitizer-support.html
- Rust-for-Linux keeps saying low-level Rust needs stable compiler flags/tooling for optimizations, code hardening, sanitizer integration, and custom std/core builds; the 2025H1 goals RFC also ties this to stable ways to rebuild core with specific compiler options.
  https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
  https://rust-lang.github.io/rfcs//3764-Project-Goals-2025h1.html
- The end-of-2025 program-management update says CPython is surfacing a very similar cluster of needs: `build-std`, platform support, sanitizer support, and other low-level compiler/toolchain requirements.
  https://blog.rust-lang.org/inside-rust/2025/12/19/program-management-update--end-of-2025/

Taken together, those signals say the missing contribution is not “another wrapper around rustup” and not “one more org-local cross-build cache.”
It is a **reviewable toolchain-variant/product layer**.

## Headline answer
If one serious team wants to build the archive's clearest remaining toolchain/sysroot/hardening contribution, the answer should now be:

> Build a **Toolchain Productization reference layer** that captures provisioned toolchain identity, stdlib/sysroot profile identity, activation/reuse posture, runtime-analysis or hardening lane truth, and bounded consumer handoffs; emit reusable reports and packs; and prove the shape across stock, rebuilt, custom-target, and instrumented lanes.

That answer is deliberately narrower than “solve environments for all Rust users”.
It is also deliberately stronger than “make `build-std` easier”.

## What this contribution should be in theory

### Core thesis
A toolchain-productization system becomes real ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact toolchain family was provisioned** — channel/version/date/host, path-linked or archive origin, component/profile/target posture, plus any external linker/SDK/C-toolchain attachments;
2. **what exact stdlib/sysroot family existed** — built vs imported, source provenance, compiler identity, target/custom-target identity, profile family, and reuse bounds;
3. **how that variant was activated** — rustup override/toolchain-file/direct `+toolchain` posture, Cargo target/config posture, workspace-vs-CI-vs-external-build-system mode, and mismatch/fallback/rejection reasons;
4. **what runtime-analysis or hardening lane actually ran** — instrumented stdlib posture, mitigation or sanitizer family, runtime library assumptions, host/target scope, and mixed-language caveats;
5. **what support envelope or compatibility posture may be claimed** — stable vs nightly, experimental vs organization-local, exact-identity vs compatible-range reuse, and what remains intentionally unsupported;
6. **what downstream consumers may import** — firmware/release/support/safety/incident/assistant consumers should be able to import selected facts without re-deriving the whole toolchain story.

If a project cannot answer those questions without opening rustup state, CI YAML, Cargo config, target JSON, and shell history side by side, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable toolchain/sysroot truth and handoff**.

It should include:
- toolchain identity capture;
- stdlib/sysroot profile identity capture;
- activation/reuse receipts;
- runtime-analysis / hardening lane receipts;
- support-envelope summaries;
- bounded consumer exports and redactions.

It should not become:
- the new universal environment manager;
- rustup replacement;
- Cargo replacement;
- one true cross-compilation wrapper;
- one vendor's distro or qualification manual;
- or a cache product that silently turns reuse into support claims.

### Separation rule
A worthy contribution here must preserve at least six distinct truth classes:
- **provisioning truth** — what compiler/toolchain/linker/SDK/C-runtime inputs existed;
- **sysroot truth** — what std/core/alloc/test/proc_macro family actually existed and with what profile identity;
- **activation truth** — how the consumer selected or rejected that toolchain/sysroot family;
- **runtime-lane truth** — which mitigation/sanitizer/instrumented-runtime lane actually ran;
- **support-envelope truth** — what may honestly be claimed afterward;
- **consumer-handoff truth** — what a specific release/support/safety/assistant consumer may import.

This is the most important guardrail in the design.
Without it, every downstream consumer becomes a hidden fork of toolchain truth.

### Shape rule
The primary contribution shape should now be:
- **reference layer + report/pack command + profile/acceptance corpus**.

Why this shape fits:
- **reference layer** because the seam is really about shared identity and non-collapse rules, not just collection;
- **report/pack command** because the real missing piece is a portable output that teams can diff, ship, and hand off;
- **profile/acceptance corpus** because stock rustup, rebuilt std, custom-target, and instrumented-runtime lanes are materially different and must be proven separately.

Wrong shapes to refuse first:
- environment-manager empire;
- “universal build-std wrapper” product;
- target-matrix badge catalog;
- cache-first product that hides stdlib identity;
- sanitizer convenience wrapper that hides whether std itself was instrumented.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo toolchaintruth inspect`
- `cargo toolchaintruth capture`
- `cargo toolchaintruth activate`
- `cargo toolchaintruth verify-lane`
- `cargo toolchaintruth explain`
- `cargo toolchaintruth diff`
- `cargo toolchaintruth handoff --to <release|firmware|support|safety|assistant>`
- `cargo toolchaintruth pack`
- `cargo toolchaintruth doctor`

The tool should **import** rustup/Cargo/SDK/CI facts where possible rather than replacing those systems.

### Public artifact spine
A credible public artifact family would keep the current contract ideas but make the review spine explicit:
- `toolchain-provision-report/v0`
- `sysroot-profile-report/v0`
- `toolchain-activation-report/v0`
- `toolchain-runtime-lane-report/v0`
- `toolchain-support-summary/v0`
- `toolchain-handoff/v0`
- `toolchain-product-pack/v0`

### First proving lanes
A credible rollout should rank proving lanes instead of pretending every specialized toolchain story lands at once.

#### Lane 1 — stock rustup / override truth lane
Start where the identity problem is most common and the authority surfaces are clearest.
This lane proves the archive can capture stock toolchain identity, directory-sensitive override posture, components/targets/profiles, and activation rules **without** falsely claiming rebuilt stdlib or runtime instrumentation.

What to prove:
- capture `channel` / version / host / components / targets / profile posture;
- distinguish ordinary rustup toolchain selection from path-linked custom toolchains;
- keep activation/reuse separate from provisioning;
- emit a support summary that says what is stock, what is local, and what is merely available.

#### Lane 2 — rebuilt stdlib / sysroot profile lane
This is the current official pressure seam.
The archive should prove that a rebuilt `core`/`std` family can leave one build machine as a reviewable identity record rather than only as hidden cache state.

What to prove:
- capture compiler/source identity for the stdlib family;
- capture profile family (`baseline`, `hardened`, `instrumented`, `core-only`, `custom-target`);
- capture reuse bounds and mismatch reasons;
- keep stdlib identity separate from the workspace/environment that consumed it.

#### Lane 3 — custom-target lane
Custom targets are strategically real, but unstable enough that they require extra honesty rather than extra hype.
This lane proves the system can handle compiler-pinned target specs and explicit instability.

What to prove:
- preserve target-spec identity or hash in every relevant report;
- carry compiler pinning explicitly;
- keep target identity separate from support claims;
- make unstable/reserved fields a first-class warning posture.

#### Lane 4 — instrumented/hardened runtime lane
This lane proves the system can represent what actually ran when sanitizer or mitigation posture matters.
It should begin with one or two realistic lanes, not every sanitizer/mitigation family at once.

What to prove:
- whether std itself was instrumented;
- which runtime/mitigation lane was enabled;
- host/target or mixed-language caveats;
- what observations are comparable across runs and what remain lane-specific.

#### Lane 5 — consumer handoff lane
Only after the earlier lanes work should the pack become a shared import layer for release/support/safety/firmware work.

What to prove:
- release lanes can import provisioning + sysroot facts without swallowing runtime-analysis claims;
- safety lanes can import runtime-lane/support-envelope facts without pretending qualification is solved;
- support and assistant lanes can summarize the pack without claiming stronger authority than the pack carries.

## What to refuse
A worthy contribution here must refuse the most tempting wrong shapes:
- another rustup replacement story;
- another environment-manager story;
- “installed target means supported” theater;
- flattening rebuilt stdlib identity into target triples or cache keys;
- flattening sanitizer/hardening results into build success;
- flattening exact identity, compatible reuse, and local experimentation into one support story;
- or making the review pack depend on one CI vendor, one SDK host, or one low-level adopter.

## Ranking and repo consequence
This revision does **not** rewrite the broad ladder.
It does **not** outrank **Build-State Evidence** overall.
It does **not** displace **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked day-to-day missing middle.

What it does do is make one repeatedly promoted seam explicit:
- **Toolchain Productization** is now the clearest remaining **toolchain-variant / sysroot / hardening / activation execution blueprint** in the archive;
- its primary shape is now **reference layer + report/pack command + profile/acceptance corpus**;
- **Workspace Environment** remains the adjacent discovery/realization consumer and **Safety-Critical Readiness Commons** remains an important imported program layer, but neither is the same thing as the portable toolchain-product boundary itself;
- and future build-std, sanitizer, custom-target, firmware, low-level-platform, and large-adopter work should import this layer rather than rediscovering it privately.

That gives the archive a better answer to a pressure cluster that is only getting more important:
How should Rust let teams provision, rebuild, instrument, activate, compare, and hand off **toolchain variants** without smearing compiler identity, stdlib identity, runtime posture, and support claims into one vague phrase like “custom toolchain”?
