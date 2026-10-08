---
id: P-0519
title: Crate Authority Surface Pack Kit — ambient-authority budgets, determinism modes, capability injection, and sandbox recipes for library authors
status: idea
domains: [crates, sandboxing, capabilities, determinism, security, dx, supportiveness, docs]
last_reviewed: 2026-03-19
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
  - https://doc.rust-lang.org/cargo/reference/environment-variables.html
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://docs.rs/ambient-authority/latest/ambient_authority/struct.AmbientAuthority.html
  - https://docs.rs/cap-std/latest/cap_std/
  - https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
  - https://docs.rs/rustix/latest/rustix/
  - https://docs.rs/wasi-cap-std-sync/latest/wasi_cap_std_sync/
  - https://docs.rs/getrandom/latest/getrandom/
  - https://docs.rs/cap-directories/latest/cap_directories/struct.ProjectDirs.html
  - https://docs.rs/cap-tempfile/latest/cap_tempfile/
  - https://docs.rs/cargo-capsec/latest/cargo_capsec/
---

# Problem

Rust has meaningful capability and sandboxing substrate, but it still has very little **crate-authored authority support**.

A downstream adopter can often discover that a crate uses `std::fs`, `reqwest`, `getrandom`, `SystemTime`, temp directories, or environment variables.
They can sometimes discover that a crate *could* be used with `cap-std`, a custom RNG backend, or a WASI-style host.
What they still usually cannot answer quickly is:

- **What ambient powers might this crate actually exercise or assume?**
- **Which powers are hard requirements versus optional accelerants or probes?**
- **Which dependencies can be injected, mocked, or replaced instead of coming from global host state?**
- **Can the crate run in an offline, deterministic, or sandboxed profile?**
- **Which profiles need filesystem write access, home-dir discovery, environment reads, network egress, or process spawning?**
- **Where does a given authority actually originate: caller input, injected handle, host-supplied capability, ambient discovery, or root-crate backend choice?**
- **What fallback order widens authority when the preferred path is unavailable?**
- **What happens when the host denies that authority — hard error, degraded mode, or silent fallback?**
- **How did that authority surface change across releases?**

That leaves teams reverse-engineering authority posture from source spelunking, CI failures, bug reports, and cargo-culted environment recipes.

The missing crate is **not** another sandbox runtime, **not** another generic static authority linter, and **not** another capability-based replacement for `std`.

The missing crate is the boring receiver-facing layer that lets a crate hand other people a **checked authority surface contract**.

# Why this moved now

Several current Rust and ecosystem signals line up unusually well.

## 1. Rust’s own vision work now explicitly asks for more supportive crate interfaces

The December 2025 vision-doc work argues that Rust should expand extensibility to include **supportive interfaces from crates**.
Authority posture is one of the most important of those interfaces for teams who care about sandboxing, offline behavior, determinism, plugins, embedded deployment, or narrow trust boundaries.

## 2. The 2025 survey still says docs and code are the main learning surfaces

The 2025 State of Rust survey says online documentation remains the preferred canonical reference, followed by studying the code itself.
That means authority assumptions left in issue comments, shell snippets, or “it probably doesn’t touch the network” lore are still effectively under-specified.

## 3. Rust now has clearer official language for ambient side effects and determinism pressure

The Rust project-goals page on sandboxed build scripts says build scripts can be run in a sandbox that limits file-system and network access, and that doing so also improves determinism.
That is compile-time rather than runtime, but it demonstrates that **ambient authority, side effects, and determinism** are now clearly recognized design seams rather than niche paranoia.

## 4. Cargo and popular crates already expose many ambient knobs — just not as a joined crate contract

Cargo documents a large environment-variable surface and build scripts that can perform arbitrary tasks.
`getrandom` documents opt-in and custom backends, including cases where downstream users must provide or select the entropy source explicitly.
This means Rust already has meaningful substrate for authority choices, but the choices still arrive as scattered per-crate folklore rather than one reviewable support artifact.

## 5. Capability-oriented ecosystem pieces already exist

`ambient-authority` explicitly marks when the user has opted into ambient authority.
`cap-std` provides capability-based filesystem, network, and time APIs and de-emphasizes global paths and global network namespaces.
`wasi-cap-std-sync` shows how that capability substrate maps into a host/sandbox boundary.
So the sharper gap is not “Rust has never thought about capabilities”; it is the missing **crate-authored contract layer above that substrate**.

## 6. Lower-level OS libraries openly do not solve this layer by themselves

`rustix` explicitly says it does not restrict ambient authorities or impose sandboxing.
That is the point: low-level substrate and syscalls are different from a receiver-facing artifact that tells other people what a crate may touch, how to narrow it, and how that changed.

## 7. Static-scanning prior art now exists, which sharpens the missing value rather than eliminating it

`cargo_capsec` now provides a real static-scanning lane by producing a capability map of functions that exercise ambient authority.
That is useful substrate.
It also makes the missing value more specific: the archive does **not** need another scanner, it needs the maintainer-authored contract above the scan that says which origins, fallbacks, and denial behaviors are intended.

# What it provides

- `authority-pack.toml` — versioned declaration of named authority kinds, scenario profiles, injection points, and recipe references.
- `authority-surface.receipt.json` — observed inventory of filesystem, network, env, time, randomness, process, tempdir, home-dir, stdio, thread, and host-probe touchpoints imported from code/tests/examples and optional probes.
- `authority-profile.report.json` — machine-readable summary of the crate’s intended authority profiles, such as `pure_core`, `offline_readonly`, `sandbox_ready`, `deterministic_testable`, `host_integrated`, and `manual_review_required`.
- `determinism-surface.report.json` — records whether behavior is `pure`, `seed_injectable`, `clock_injectable`, `env_sensitive`, `filesystem_sensitive`, `network_sensitive`, `host_probe`, or `manual_review_required`.
- `capability-injection.report.json` — records which dependencies can be supplied explicitly via traits/handles/config versus coming from ambient globals.
- `sandbox-recipe.manifest.json` — commands, env policy, FS/network expectations, fixed-clock/fixed-RNG hooks, and capability handles needed to verify named profiles.
- `authority-check.report.json` — verifies whether the advertised profiles match observed imports and recipe outcomes.
- `authority-budget.policy.json` — explicit meaning for whether a power is required, optional, forbidden, test-only, or still manual-review-only in a named profile.
- `injection-boundary.receipt.json` — observed or declared record of whether a dependency is ambient-only, injectable at construction, injectable per operation, host-supplied, or test-only.
- `profile-witness.report.json` — records what happened when a named profile actually ran under restrictions such as no network, empty env, read-only FS, fixed clock, or fixed RNG.
- `authority-origin.receipt.json` — records whether a power originates in caller input, injected handles, host-supplied capabilities, ambient directory discovery, ambient tempdir, OS entropy, or root-crate backend choice.
- `fallback-chain.report.json` — records the preferred and fallback order before the crate widens into more ambient authority.
- `refusal-posture.report.json` — records what happens when the host denies an authority request.
- `authority-diff.report.json` — compares two versions and classifies `authority_added`, `authority_removed`, `budget_changed`, `profile_changed`, `injection_boundary_changed`, `injection_regressed`, `determinism_regressed`, `origin_changed`, `fallback_changed`, `refusal_posture_changed`, `profile_witness_changed`, `recipe_changed`, and `manual_review_boundary_changed`.
- `authority-notes.summary.md` — short human-facing summary rendered from the structured artifacts.
- `cargo authority-surface init` — generate and annotate a starter authority pack.
- `cargo authority-surface capture` — capture one crate’s authority surface.
- `cargo authority-surface check` — verify the declared profiles.
- `cargo authority-surface doctor` — render suspicious profile-budget or injection-boundary drift.
- `cargo authority-surface diff <old> <new>` — compare two crate authority surfaces.
- `cargo authority-surface summary` — render a reviewable Markdown summary.
- `cargo authority-surface pack` — emit one portable bundle for review or CI.

# What the crate should provide other people

1. **A stable map of ambient powers** instead of forcing users to grep for `std::fs`, `Command`, `var`, `home_dir`, `getrandom`, `sleep`, and ad hoc network clients.
2. **Named authority profiles** so people can tell the difference between “pure parser core”, “offline readonly”, “sandbox-ready”, and “host-integrated” use.
3. **Authority-origin truth** so downstream users know whether power comes from caller input, explicit handles, host capabilities, ambient discovery, or a root-crate backend choice.
4. **Fallback-order truth** so “sandbox-ready” does not quietly hide a later fallback to `$HOME`, project dirs, tempdir, or environment probes.
5. **Refusal-posture truth** so denied authority becomes a reviewable behavior instead of trial-and-error folklore.
6. **Injection-point truth** so downstream users know whether clock, RNG, filesystem, network, cache, and process dependencies can be supplied explicitly.
7. **Checked sandbox and determinism recipes** so adopters can verify claims rather than trusting README prose.
8. **Release-to-release authority diffs** so new ambient reads, writes, probes, fallback chains, or nondeterministic dependencies become reviewable like API changes.
9. **Reusable import artifacts** for pathfinder crates, policy gates, plugin hosts, docs portals, and org-specific sandbox governance.

# Persona / who it’s for

- library maintainers whose crates may touch host resources or depend on ambient state
- application teams deciding whether a dependency is suitable for offline, embedded, sandboxed, or regulated use
- platform/security engineers trying to review dependency authority posture without bespoke source audits
- plugin/extension host authors who need to understand what a guest library expects from the host
- docs/tool authors who want stable authority metadata instead of scraped prose

# Users & user stories

- **Embedded engineer**: “Show me whether this crate can run without filesystem, network, and OS entropy, and what I must inject to make that true.”
- **Security reviewer**: “Give me one artifact telling me whether the crate reads env vars, spawns processes, touches `$HOME`, or needs network egress.”
- **Plugin-host author**: “Tell me which host services must be passed in explicitly and which assumptions still leak through ambient globals.”
- **Library author**: “Publish one checked authority profile so users stop guessing whether the crate is safe to run in CI, WASI, or a restricted sandbox.”
- **Release reviewer**: “Diff two versions and tell me whether the crate gained a new ambient dependency.”

# Prior art (and why it’s insufficient)

- `ambient-authority` makes opting into ambient authority explicit.
- `cap-std` and related Bytecode Alliance crates provide capability-based filesystem, network, and time APIs.
- `wasi-cap-std-sync` maps capability-oriented filesystem access into WASI host contexts.
- `getrandom` supports opt-in and custom backends, including downstream-provided implementations.
- Cargo’s environment-variable and build-script docs expose large ambient/config surfaces.
- build-script sandboxing work and tools like `cackle` or `cargo-sandbox` show policy and runtime enforcement directions.

What remains missing is the joined, maintainer-authored artifact that says:

- these are the **authority kinds** this crate intentionally needs or may use,
- these are the **profiles** in which they appear,
- these dependencies are **injectable** rather than ambient,
- these recipes let you verify **offline / deterministic / sandbox-ready** modes,
- and this is how the crate’s **authority surface changed** across releases.

That is a different lane from:

- **P-0509** task-first crate choice,
- **P-0510** producer-side capability contracts,
- **P-0516** configuration scenarios,
- **P-0518** observability surfaces,
- compile-time sandbox policy tooling such as **P-0107**,
- generic capability-based replacement libraries,
- or org-wide sandbox runtimes.

# Design goals

1. **Receiver-facing first** — optimize for downstream users deciding whether they can safely adopt, sandbox, or replay this crate.
2. **Authority-surface over enforcement** — describe and verify ambient dependencies rather than replacing runtime sandboxes.
3. **Determinism honesty** — make clocks, randomness, env reads, filesystem writes, and host probes part of the visible surface.
4. **Injection over magic** — reward crates that expose explicit handles or traits rather than ambient globals.
5. **Join, don’t replace** — import from capability libraries, Cargo recipes, and optional probes rather than competing with them.
6. **Diffability** — make authority drift explicit across releases.

# MVP surface

- Minimal `authority-pack.toml` schema with named authority kinds, profiles, and recipe references.
- Import lane for obvious authority touchpoints from code/tests/examples and declared feature/config hooks.
- Authority vocabulary:
  - `fs_read`
  - `fs_write`
  - `temp_dir`
  - `home_dir`
  - `env_read`
  - `env_write`
  - `network_egress`
  - `network_ingress`
  - `time_now`
  - `sleep_timer`
  - `randomness`
  - `process_spawn`
  - `stdio`
  - `thread_spawn`
  - `host_probe`
  - `manual_review_required`
- Determinism vocabulary:
  - `pure`
  - `seed_injectable`
  - `clock_injectable`
  - `env_sensitive`
  - `filesystem_sensitive`
  - `network_sensitive`
  - `host_probe`
  - `manual_review_required`
- `authority-check.report.json` that records whether advertised profiles are consistent with imports and recipes.
- `authority-diff.report.json` for release-to-release surface drift.
- `cargo authority-pack summary` to render a short reviewable Markdown summary.

# Compatibility story

This crate should interoperate with:

- capability-oriented libraries such as `cap-std` and `ambient-authority`,
- sandbox/policy tools such as `cargo-sandbox`-style workflows,
- downstream-specific injection surfaces for clocks, RNGs, filesystems, HTTP clients, and caches,
- docs portals or crate pathfinder tools that want authority metadata.

It should **not** try to replace:

- `cap-std`,
- `ambient-authority`,
- `rustix`,
- runtime sandboxes or container policy,
- or Cargo’s compile-time sandboxing work.

# Artifact vocabulary

## `authority-pack.toml`

```toml
schema_version = "0.1"
crate = "example-crate"

[[profile]]
name = "offline_readonly"
determinism = "clock_injectable"
authority = ["fs_read", "env_read"]
forbidden = ["network_egress", "process_spawn", "fs_write"]

[[touchpoint]]
name = "config_lookup"
kind = "env_read"
profile_refs = ["offline_readonly", "host_integrated"]
injectable = false

[[touchpoint]]
name = "rng_source"
kind = "randomness"
profile_refs = ["deterministic_testable", "host_integrated"]
injectable = true
recipe_ref = "recipes/fixed_rng.toml"
```

## `determinism-surface.report.json`

```json
{
  "schema_version": "0.1",
  "crate": "example-crate",
  "summary": {
    "determinism_class": "clock_injectable",
    "notes": [
      "core parse path is pure",
      "cache expiry checks require an injected clock for deterministic replay"
    ]
  },
  "hazards": [
    {"kind": "time_now", "status": "injectable"},
    {"kind": "randomness", "status": "injectable"},
    {"kind": "env_read", "status": "ambient_only"}
  ]
}
```

For a more implementation-ready build sketch, see `meta/crate-authority-surface-product-plan-2026-03-19.md` (and keep the 2026-03-17 note as the earlier sketch).

# Distinctive implementation shape

## Crates

- `authpack-core` — schemas, vocabularies, diff logic, summary rendering.
- `authpack-scan` — import touchpoints from source, tests, examples, and declared features/config.
- `authpack-probe` — optional recipe-driven probes using constrained environments or fixed dependencies.
- `authpack-cap` — adapters for capability-oriented libraries and explicit-handle patterns.
- `cargo-authority-pack` — CLI.

## Profile vocabulary

- `pure_core`
- `offline_readonly`
- `sandbox_ready`
- `deterministic_testable`
- `host_integrated`
- `manual_review_required`

## Diff vocabulary

- `authority_added`
- `authority_removed`
- `profile_changed`
- `injection_regressed`
- `determinism_regressed`
- `recipe_changed`
- `manual_review_boundary_changed`

# Conformance & fixtures

The fixture pack should start with five scenario families:

1. **Parser / data-model library** — a mostly pure core with optional env-driven defaults and no ambient IO in the main path.
2. **SDK / client library** — optional network, cache, env, and clock dependencies with one offline or mocked profile.
3. **Plugin / extension runtime helper** — explicit host handles for FS/network/time plus clear “ambient-only” escape hatches.
4. **Env-or-home cache fallback** — an “offline” profile that still widens into env/home/tempdir behavior on cache miss.
5. **Seeded RNG but clock leak** — a superficially deterministic profile that still depends on system time.
6. **Capability-profile path escape** — a crate that uses `cap-std` in some paths while an absolute-path helper still bypasses the profile.
7. **Caller-supplied temp dir beats ambient temp root** — a crate that must show explicit authority origin and preference order.
8. **Project dirs denied silently fall back to tempdir** — a crate that must record refusal posture rather than claiming sandbox readiness.
9. **Library-owned getrandom backend** — a crate that must distinguish root-crate backend choice from library-owned authority.

Each fixture should include one declared profile, one intentionally drifting profile, and one manual-review zone so the crate learns how to stay honest.

# Path to boring stability

Before 1.0, the project should prove:

1. the authority vocabulary is small enough to be portable,
2. obvious false positives and false negatives are documented and versioned,
3. capability-injection reports are useful across at least three crate families,
4. diff reports are stable enough for CI review,
5. and summary output stays conservative rather than pretending perfect static knowledge.

# Non-goals

- Replacing container, VM, or OS sandboxing.
- Guaranteeing that static scans prove the absence of all side effects.
- Becoming a general-purpose secure-coding lint suite.
- Automatically rewriting crates to use capability APIs.
- Owning compile-time sandbox policy for build scripts or proc macros.

# Security / safety model

- Treat imports and probes as **evidence**, not as mathematical proof.
- Default to `manual_review_required` when a touchpoint cannot be classified confidently.
- Keep “ambient-only” and “injectable” explicitly separate.
- Make recipe failures first-class findings rather than hiding them behind green summaries.
- Prefer conservative summaries over under-reporting ambient authority.

# Maintenance & governance plan

- Keep the vocabularies versioned and intentionally small.
- Maintain fixtures as the core value so the crate remains honest about what it can and cannot classify.
- Publish cookbook notes for common patterns: fixed clock, custom RNG, injected HTTP client, explicit cache directory, no-home-dir mode.
- Coordinate with capability and sandbox projects without trying to subsume them.

# Milestones

## 0.1
- Schema crate, summary renderer, manual authoring of `authority-pack.toml`, simple source/import scan, and first-class `authority-budget`, `injection-boundary`, and `profile-witness` artifacts.

## 0.2
- Recipe runner for fixed-clock/fixed-RNG/no-network checks and first diff report.

## 0.3
- Capability-oriented adapters (`cap-std`, injected RNG/client patterns) and docs-portal import story.

## 0.4
- Profile drift CI helpers and richer scenario fixtures.

# Open questions

- What is the smallest authority vocabulary that still captures real downstream review value?
- Which touchpoints are worth static import heuristics, and which must remain recipe/probe territory?
- How should the crate express “ambient authority only in examples/tests” without creating a false sense of purity?
- Which profile names are broad enough to travel across CLIs, services, libraries, WASI, and embedded use cases?
- How should plugin-host crates declare “the host provides this capability” without collapsing back into ambient globals?

# Sources

- Rust vision doc on supportive interfaces from crates: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust project goal on sandboxed build scripts: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo environment variables: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo build scripts: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- `ambient-authority` docs: https://docs.rs/ambient-authority/latest/ambient_authority/struct.AmbientAuthority.html
- `cap-std` docs: https://docs.rs/cap-std/latest/cap_std/
- `cap-std::fs::Dir::open_ambient_dir` docs: https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- `rustix` docs: https://docs.rs/rustix/latest/rustix/
- `wasi-cap-std-sync` docs: https://docs.rs/wasi-cap-std-sync/latest/wasi_cap_std_sync/
- `getrandom` docs: https://docs.rs/getrandom/latest/getrandom/
- `cap_directories::ProjectDirs` docs: https://docs.rs/cap-directories/latest/cap_directories/struct.ProjectDirs.html
- `cap-tempfile` docs: https://docs.rs/cap-tempfile/latest/cap_tempfile/
- `cargo_capsec` docs: https://docs.rs/cargo-capsec/latest/cargo_capsec/
