---
id: P-0107
title: Cargo Sandbox & Capability Policy Kit — policy authority, actor capabilities, ambient-input receipts, sanitization modes, launcher routes, and drift bundles
status: idea
domains: [cargo, sandboxing, build-scripts, proc-macros, supply-chain, supportiveness]
last_reviewed: 2026-03-23
evidence:
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
  - https://github.com/rust-lang/compiler-team/issues/475
  - https://github.com/rust-lang/cargo/issues/5720
  - https://github.com/rust-lang/cargo/issues/16591
  - https://doc.rust-lang.org/cargo/reference/environment-variables.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/unstable.html
  - https://doc.rust-lang.org/beta/releases.html
  - https://github.com/cackle-rs/cackle
  - https://github.com/madsmtm/cargo-sandbox
---

# Problem

Compile-time execution in Rust has become too important to leave as folklore.
The upstream story is now concrete enough to plan a worthy crate above it rather than merely wish for “safer build scripts someday”.

Current signals line up around the same shape:

- the Rust project goal for sandboxed build scripts explicitly treats filesystem and network access as a first-class design surface and ties sandboxing to determinism and future caching work;
- the accepted compiler-team MCP makes the end-state even clearer: build scripts and proc macros should eventually have a minimal declared API, configuration knobs in Cargo/rustc, and compilation errors when undeclared powers are used;
- Cargo still documents a very large build-time environment surface, including `OUT_DIR`, `TARGET`, `HOST`, `DEP_*`, wrappers, and encoded compiler flags;
- Cargo config still documents that `RUSTFLAGS`/`build.rustflags` hit build scripts and proc macros unless an explicit `--target` is used, which means policy scope and execution topology are easy to misread;
- Cargo’s unstable `--compile-time-deps` mode proves that “compile-time actors only” is already a real workflow surface for tools like rust-analyzer;
- recent Cargo issue work is now accepted around wrapping **host build target executions**, and that same issue cluster explicitly links sandboxing, environment sanitization, allowlist mode, and upcoming unstable `-Zsandbox` experiments;
- and the current practical tools are informative but incomplete: `cackle` can sandbox build scripts separately but still has shared granularity for proc macros, while `cargo-sandbox` explicitly aims to sandbox build scripts and proc macros yet remains platform-limited.

That means the missing value is not another OS sandbox runtime and not another static scanner that merely spots `std::fs`.
The missing value is a crate that lets another engineer, reviewer, or policy owner answer these questions without reverse-engineering one-off logs:

1. **Which compile-time actor asked for which capability?**
2. **Which policy source was authoritative for that grant or denial?**
3. **Was the run observe-only, audit, or enforce?**
4. **How granular was the backend really — per build script, per proc macro, shared `rustc` lane, or whole-command?**
5. **Which exceptions were break-glass and who owns them?**
6. **What materially changed across releases, toolchains, or CI policies?**

That worthy crate is **Cargo Sandbox & Capability Policy Kit**.

# Sharper reading after the 2025–2026 Cargo changes

## 1. Sandbox policy now has a real upstream target

The project goal and MCP no longer leave this lane at pure aspiration.
They point toward declared powers, one interface for build-time sandboxing, and a runtime that can be swapped or integrated with Cargo.
That makes a userland support contract more rather than less valuable.

## 2. Build-time environment truth is still messy

Cargo exposes many environment variables to build scripts and still makes host-vs-target flag scope easy to misread.
A capability kit has to say which actor actually had those powers and under what route.

## 3. Practical runners still have uneven granularity

Today’s tools already demonstrate useful policies, but they also expose where the support contract is missing.
If one backend can isolate build scripts per crate but only sandbox proc macros at a coarse shared level, the crate must preserve that truth instead of flattening it into “sandbox enabled”.

## 4. IDE / preflight workflows depend on compile-time actors alone

`--compile-time-deps` proves that build scripts and proc macros form a meaningful lane of their own.
A reviewable policy artifact for that lane helps both security-sensitive CI and editor/tooling workflows.

## 5. Recent Cargo changes make policy drift easier to hide

When build-time env behavior, wrappers, and host execution hooks move, a green build can quietly stop meaning the same thing.
A worthy crate therefore needs receipts and diffs, not just a one-shot runner.

# Main judgment

A worthy crate here should provide a receiver-facing answer to eight questions:

1. **Policy authority** — which manifest, workspace overlay, organization rule, or manual override actually defined the policy?
2. **Actor capability scope** — which build script, proc macro lane, rustc lane, or compile-time-only workflow got which filesystem/network/env/process powers?
3. **Ambient input** — which parent env keys, Cargo-set env keys, path roots, toolchain selectors, wrapper variables, or build-script-emitted env channels still reached that actor or lane?
4. **Sanitization mode** — were those channels inherited, allowlisted, rewritten, or denied by default?
5. **Launcher route** — did the actor run directly, through rustc, through a preload/interceptor route, or via a dedicated runner?
6. **Enforcement mode** — was the run observe-only, warn/audit, or hard-enforce, and what denial semantics followed?
7. **Exception ownership** — which break-glass grants exist, who owns them, and when do they expire?
8. **Policy drift** — what changed across versions, toolchains, backends, or CI overlays that materially changes the review story?

That is much more valuable than another thin wrapper around `sandbox-exec`, Landlock, or `bwrap`.

# 2026-03-23 refinement — ambient ingress, sanitization, and launcher routes should now be first-class

The current substrate now makes three more receiver-facing review objects worth promoting.

## 1. `ambient-input.receipt.json`

A compile-time actor can stay meaningfully privileged even when explicit network/filesystem powers look narrow.
This receipt should record:

- Cargo-set env vars and compiler-side env channels,
- inherited parent env vars,
- config-driven env injection,
- path-search roots and executable discovery lanes,
- toolchain selectors / toolchain files,
- wrapper or preload env routes,
- and build-script-emitted env that can later reach rustc or proc macros.

## 2. `sanitization-mode.receipt.json`

A worthy crate should make sanitization explicit, not implied.
This receipt should say whether ambient ingress was:

- inherited wholesale,
- allowlisted,
- rewritten,
- deny-by-default,
- or still manual-review-only.

It should also capture whether project-local opt-out was rejected and whether toolchain auto-install remained enabled.

## 3. `launcher-route.receipt.json`

Receiver-facing trust depends on how a compile-time actor was actually wrapped.
This receipt should preserve:

- direct execution versus rustc-wrapper versus preload/interceptor versus dedicated-runner routes,
- per-actor versus shared-lane granularity,
- and whether earlier build-time actors can still perturb later host compilation lanes.

Without that artifact, “sandboxed” is still too easy to over-read.

# What it provides

- `Cargo.sandbox.toml` — declared workspace policy with package/actor selectors and named profiles.
- `policy-authority.receipt.json` — authoritative source for the effective policy.
- `actor-capability.matrix.json` — per-actor view of granted and denied powers.
- `enforcement-mode.receipt.json` — whether a run was observe/audit/enforce plus backend granularity and denial behavior.
- `exception-ack.record.json` — owned break-glass grants and expiry/review metadata.
- `observed-access.report.json` — optional normalized observation import from a backend.
- `ambient-input.receipt.json` — env/path/toolchain/wrapper ingress visible to an actor or lane, including build-script-emitted env channels.
- `sanitization-mode.receipt.json` — whether ingress was inherited, allowlisted, rewritten, deny-by-default, or still manual-review-only.
- `launcher-route.receipt.json` — how an actor was actually wrapped or intercepted, at what granularity, and with what route-mutation risk.
- `sandbox-policy-drift.diff.json` — what changed across crate versions, toolchains, or CI overlays.
- `sandbox-support-bundle.manifest.json` — portable review bundle joining contract, ingress, routes, observations, exceptions, and diff.
- `cargo sandbox-policy snapshot`
- `cargo sandbox-policy doctor`
- `cargo sandbox-policy diff <old> <new>`
- `cargo sandbox-policy pack`
- `*.sandboxpolicybundle.zip`

# First-class review objects for 0.1

## `policy-authority.receipt.json`

Should record at least:

- policy subject,
- authority route (`crate_manifest`, `workspace_overlay`, `organization_policy`, `ci_override`, `manual_review`),
- actor selectors covered,
- backend family,
- and why this source outranked the alternatives.

## `actor-capability.matrix.json`

Should record at least:

- actor identity,
- actor class (`build_script`, `proc_macro_lane`, `rustc_host_lane`, `compile_time_deps_workflow`, `manual_review`),
- filesystem read/write roots,
- network posture,
- env read/write posture,
- process-spawn posture,
- and granularity notes when an actor is only partially isolated.

## `ambient-input.receipt.json`

Should record at least:

- which Cargo-set env vars reached the actor,
- which parent env vars remained visible,
- which config-driven env or path channels mattered,
- whether toolchain selection or wrappers were in play,
- whether build-script-emitted env could influence later host compilation,
- and which of those channels still require manual review.

## `sanitization-mode.receipt.json`

Should record at least:

- whether ingress was inherited, allowlisted, rewritten, or deny-by-default,
- default deny/warn/allow posture,
- explicitly allowed / stripped / rewritten keys,
- allowed path roots,
- project-local override posture,
- toolchain auto-install posture,
- and why the chosen mode is sufficient or still incomplete.

## `launcher-route.receipt.json`

Should record at least:

- direct-exec versus rustc-wrapper versus preload-interceptor versus dedicated-runner routes,
- actor or lane subject,
- actual granularity,
- backend family,
- route-mutation risk,
- and whether a shared host lane prevents per-actor claims.

## `enforcement-mode.receipt.json`

Should record at least:

- mode (`observe`, `audit`, `enforce`),
- denial behavior (`record_only`, `warn`, `block`),
- backend family,
- granularity class,
- known blind spots,
- and whether the result is safe for release review or only local diagnosis.

## `exception-ack.record.json`

Should record at least:

- actor and capability,
- justification,
- owner,
- expiry/review date,
- source,
- and whether the exception broadens or only preserves existing support posture.

## `sandbox-policy-drift.diff.json`

Should classify at least:

- `actor_added`,
- `actor_removed`,
- `capability_broadened`,
- `capability_narrowed`,
- `authority_route_changed`,
- `backend_changed`,
- `mode_changed`,
- `exception_added`,
- `exception_removed`,
- `manual_review_required`.

# What the crate should provide other people

1. **A boring policy contract** instead of bespoke CI shell wrappers and tribal allowlists.
2. **A precise actor matrix** so build scripts and proc macros stop inheriting one another’s support story by accident.
3. **An ambient-input receipt** so env/path/toolchain channels are inspectable instead of hidden behind “no network” or “no filesystem” shorthand.
4. **A sanitization-mode receipt** so another reviewer can tell whether the run was inherited, allowlisted, rewritten, or deny-by-default.
5. **A launcher-route receipt** so “sandboxed” never hides shared rustc lanes, preload tricks, or build-script-induced route mutation risk.
6. **An honest enforcement receipt** so “sandboxed” never hides observe-only mode or coarse backend granularity.
7. **Owned break-glass records** instead of invisible exceptions sprinkled through runner configs.
8. **A release-review diff** so new network access, broader filesystem scope, or wider ambient ingress triggers review before trust quietly drifts.
9. **A backend-agnostic bundle** that stays useful whether the actual runner is `cackle`, `cargo-sandbox`, a future Cargo flag, or an internal wrapper.

# Persona / who it’s for

- security-conscious maintainers,
- CI/buildfarm operators,
- enterprise platform teams,
- distro/packaging engineers running no-network or limited-host builds,
- editor/tooling authors using compile-time-only workflows,
- and reviewers who need to decide whether a build-time policy story is truly supportable.

# Users & user stories

- **CI owner**: “Tell me whether this green run was observe-only or actual enforcement.”
- **Security reviewer**: “Show me the one proc macro that forced a broader grant and whether that grant is scoped or shared.”
- **Maintainer**: “Keep build-script path grants narrow without accidentally authorizing proc macros.”
- **Tooling engineer**: “Document the compile-time-only lane we use for editor support and whether its policy differs from full builds.”
- **Release reviewer**: “Diff old and new capability posture before approving the upgrade.”

# Prior art (and why it’s insufficient)

- The project goal and MCP describe the upstream direction, but not a portable day-to-day bundle for policy authority, enforcement mode, and drift.
- `cackle` is valuable and practical, but its own docs already expose limits in proc-macro granularity; that proves the need for a higher-level support contract rather than removing it.
- `cargo-sandbox` demonstrates a real end-user workflow, but its platform matrix is intentionally incomplete and it is not yet a shared artifact standard.
- Cargo docs explain env/config behavior, but they do not package those facts into a reviewable capability contract.
- The archive already has adjacent lanes: runtime crate authority (**P-0519**), delegated build units (**P-0508**), proc-macro migration readiness (**P-0040**), and host/target scope contracts. None of those is the same as compile-time sandbox policy truth.

# Design goals

1. **Authority-first** — always say where policy came from.
2. **Actor-first** — never flatten build scripts and proc macros into one “sandboxed build” answer.
3. **Enforcement-honest** — preserve observe/audit/enforce differences.
4. **Backend-agnostic** — receipts should survive backend changes.
5. **Exception-explicit** — break-glass paths must be owned and reviewable.
6. **Stable-first, upstream-aware** — useful now, compatible with future Cargo-native substrate.
7. **Adjacent-lane honest** — do not collapse this lane into runtime sandboxing, delegated build topology, or general trust scoring.

# MVP surface

- Minimal types: `PolicyAuthorityReceipt`, `ActorCapabilityMatrix`, `EnforcementModeReceipt`, `ExceptionAckRecord`, `ObservedAccessReport`, `SandboxPolicyDriftDiff`, `SandboxSupportBundle`
- Minimal functions:
  - `resolve_policy_authority()`
  - `capture_actor_matrix()`
  - `capture_enforcement_mode()`
  - `diff_policy_bundles()`
  - `pack_sandbox_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `markdown`
  - `cackle-import`
  - `cargo-sandbox-import`

# Compatibility story

- Must remain useful on stable by ingesting existing runner behavior and Cargo-observable facts rather than waiting for upstream stabilization.
- Must preserve whether a fact came from declared policy, workspace overlay, imported backend report, or manual review.
- Must remain valuable if Cargo later ships native sandboxing because teams will still need authority receipts, actor matrices, enforcement receipts, and diffs.
- Must integrate with adjacent archive lanes instead of replacing them.

# Conformance & fixtures

- a package where a build script needs path-limited `pkg-config`/headers but a proc macro must stay deny-by-default,
- a run where observe mode passes but enforce mode would have blocked the release,
- a backend with coarse proc-macro granularity that must not over-claim per-macro isolation,
- a workspace overlay that authorizes one temporary network exception and becomes the true authority route,
- and a release that broadens capability scope and therefore requires review even though the build still succeeds.

# Path to boring stability

1. Freeze the vocabulary for authority, actor scope, enforcement, exceptions, and drift.
2. Start with snapshot/doctor/diff/pack instead of owning the actual sandbox runner.
3. Import current practical backends rather than forcing one backend to win.
4. Keep stable-vs-nightly and per-platform posture explicit.
5. Let upstream Cargo/native sandboxing reuse the artifact layer later if it wants.

# Why this could be epic

This crate would sit above one of Rust’s most politically and operationally sensitive seams: arbitrary code execution during builds.
It would help other people make policy decisions, audit upgrades, compare backends, and publish honest support stories now, while still lining up with where Cargo and rustc appear to be heading.
That is the right kind of epic contribution: one crate that turns a messy, high-stakes frontier into durable review objects other teams can actually use.
