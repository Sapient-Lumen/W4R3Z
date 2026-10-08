# Crate authority-surface product plan — 2026-03-17

This note exists to keep **P-0519 Crate Authority Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing ambient-authority / determinism / injection / sandbox-profile contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0519** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps crate authors publish one reviewable answer to:

- which ambient powers the crate may exercise in each named profile,
- which of those powers are hard requirements versus optional conveniences or test-only escape hatches,
- which dependencies can be injected or host-supplied rather than pulled from global state,
- which sandboxed / offline / deterministic recipes were actually witnessed,
- where the crate still falls back to `manual_review_required`,
- and what changed between releases.

It should **not** try to become a new sandbox runtime, a new capability library, a new secure-coding linter, or a static proof of side-effect absence.
Those are adjacent imports, not the product.

## What the crate should provide other people

For downstream users, release reviewers, and policy teams, the crate should provide:

1. **One compact authority contract** instead of folklore scattered across README notes, examples, issue threads, and source spelunking.
2. **An authority budget per profile** so users can tell the difference between `required_runtime_authority`, `optional_accelerant`, `host_convenience`, and `forbidden_in_profile`.
3. **Injection-boundary truth** so clock, RNG, filesystem, network, cache, and process dependencies stop being guessed at.
4. **Profile witnesses** showing whether an `offline_readonly`, `sandbox_ready`, or `deterministic_testable` claim actually survived a restricted recipe.
5. **A determinism hazard summary** so time, randomness, env, filesystem, and host-probe pressure become explicit review objects.
6. **A short human summary** that can be pasted into docs, policy review, or dependency-adoption notes.
7. **A release diff** that makes new ambient reads, writes, probes, or injection regressions loud.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. adapters for capability-oriented and explicit-handle patterns instead of bespoke reinvention,
4. one place to record “examples/tests only” or “host convenience only” authority use,
5. and a CI gate for “this release changed authority posture”.

## Recommended `0.1` command surface

### `cargo authority-surface init`
Create a starter `authority-pack.toml` by importing obvious candidates from:

- maintainer-declared profiles,
- visible filesystem / env / tempdir / network / time / randomness / process touchpoints,
- declared feature flags and examples,
- obvious explicit-handle patterns,
- and known capability-oriented APIs when they are used directly.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo authority-surface capture`
Emit one normalized authority bundle from a declared profile or recipe.
This should capture:

- observed touchpoints,
- authority budgets,
- injection boundaries,
- determinism hazards,
- recipe restrictions,
- and imported evidence sources.

`capture` should work on imported artifacts too.
It must not require one blessed sandbox runtime.

### `cargo authority-surface check`
Run the local validation pass:

- do declared authority kinds and determinism classes parse,
- do named profiles have coherent required/forbidden authority budgets,
- do injection-boundary declarations match the touched APIs or adapters,
- do sandbox recipes declare explicit restriction sets,
- are profile-witness claims backed by recipe results,
- and which parts remain manual-review-only?

### `cargo authority-surface doctor`
Render human-facing warnings for suspicious situations such as:

- `ambient_env_read_in_sandbox_ready_profile`
- `home_dir_fallback_not_budgeted`
- `randomness_claimed_seed_injectable_but_backend_ambient`
- `absolute_path_escape_breaks_capability_profile`
- `profile_claim_without_witness`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo authority-surface summary`
Render a short receiver-facing note for dependency review, docs, or sandbox-policy handoff.
A good summary answers:

- which profiles exist,
- what ambient powers they require,
- what can be injected,
- what was actually witnessed,
- and where the caveats are.

### `cargo authority-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `authority_added`
- `authority_removed`
- `budget_changed`
- `profile_changed`
- `injection_boundary_changed`
- `injection_regressed`
- `determinism_regressed`
- `profile_witness_changed`
- `recipe_changed`
- `manual_review_boundary_changed`

### `cargo authority-surface pack`
Emit one compact `.authoritysurface.zip` bundle for CI artifacts, release review, sandbox-policy review, or dependency-adoption handoff.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `authority_surface_model`
  - shared Rust types for packs, receipts, policies, witnesses, reports, and diffs
- `authority_surface_discovery`
  - import logic for touchpoints, explicit-handle patterns, and authority hints
- `authority_surface_check`
  - policy validation, drift checks, and doctor warnings
- `authority_surface_witness`
  - restricted-profile recipe execution and witness recording
- `authority_surface_pack`
  - summary rendering, diff writing, markdown output, and zip bundle emission
- `cargo-authority-surface`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `authority_surface_cap_std`
- `authority_surface_getrandom`
- `authority_surface_time`
- `authority_surface_http_client`
- `authority_surface_cache_dirs`
- `authority_surface_wasi`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should still revolve around:

- `authority-pack.toml`
- `authority-surface.receipt.json`
- `authority-profile.report.json`
- `determinism-surface.report.json`
- `capability-injection.report.json`
- `sandbox-recipe.manifest.json`
- `authority-check.report.json`
- `authority-diff.report.json`
- `authority-notes.summary.md`

This pass adds three more important artifacts:

- `authority-budget.policy.json` — what `required_runtime_authority`, `optional_accelerant`, `host_convenience`, `test_only`, `forbidden_in_profile`, and `manual_review_required` mean for a profile.
- `injection-boundary.receipt.json` — the declared or observed boundary for a dependency or touchpoint, including `ambient_only`, `injectable_at_construction`, `injectable_per_operation`, `host_supplied_capability`, `test_only_injection`, or `manual_review_required`.
- `profile-witness.report.json` — what happened when a named profile was actually exercised under restrictions such as no network, empty env, no home directory, read-only FS, fixed clock, fixed RNG, or no process spawn.

Those files matter because authority support gets vague again if the archive only records “this crate touches env/network/filesystem” without making clear:

- which of those powers are actually budgeted,
- which can be replaced with explicit handles,
- and which profile claims were directly witnessed versus merely intended.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared public surface**
   - `authority-pack.toml`
   - maintainer-declared profiles and touchpoints
2. **Observed touchpoints**
   - filesystem, env, tempdir, home dir, network, time, randomness, process, stdio, thread, host probes
3. **Injection boundaries**
   - construction-time handles
   - per-operation handles
   - host-supplied capabilities
   - test-only seams
4. **Profile budgets**
   - required, optional, forbidden, or manual-review authority
5. **Recipe witnesses**
   - restricted runs under no-network / empty-env / no-home / read-only-fs / fixed-time / fixed-rng / no-spawn
6. **Manual review zones**
   - hidden FFI, indirect runtime behavior, backend-specific drift, or unexercised examples

The importer should prefer visible uncertainty over synthesis.

## Authority-budget policy

The first implementation should treat **authority budgets as first-class review objects** and keep them separate from raw import lists.

### What should count as budget classes in `0.1`

- `required_runtime_authority`
- `optional_accelerant`
- `host_convenience`
- `test_only`
- `forbidden_in_profile`
- `manual_review_required`

### What should *not* be encoded as budget classes in `0.1`

- “this crate probably doesn’t need the network most of the time”
- “the env read is only for convenience so it doesn’t count”
- “examples use `$HOME`, therefore production does too”
- “we saw one filesystem helper so the whole crate is host-integrated”

The budget policy should be versioned and diffable.
If a maintainer cannot explain whether an authority kind is required, optional, or forbidden for a profile, it should fall back to `manual_review_required`.

## Injection-boundary policy

The first implementation should treat **injection boundaries as explicit review material**.
A good `0.1` should model:

- `ambient_only`
- `injectable_at_construction`
- `injectable_per_operation`
- `host_supplied_capability`
- `test_only_injection`
- `manual_review_required`

What matters is not only that a dependency is injectable somewhere, but **where** the boundary lives.
A crate that needs ambient globals in production but supports test-only injection should not be summarized the same way as one that accepts explicit handles at its public boundary.

## Profile-witness policy

The first implementation should treat **profile claims as witnessed when possible** and explicit about missing evidence.

### What should count as witness outcomes in `0.1`

- `passed_under_restriction`
- `failed_under_restriction`
- `not_run`
- `manual_review_required`

### What should count as standard restriction sets in `0.1`

- `no_network`
- `empty_env`
- `no_home_dir`
- `readonly_fs`
- `fixed_clock`
- `fixed_rng`
- `no_process_spawn`

The witness report should make it obvious whether a claim was:

- observed under a real restriction set,
- only partially exercised,
- or never exercised at all.

## Proving-ground archetypes

A worthy first implementation should prove itself against at least five archetypes:

1. **Parser / data-model library**
   - mostly pure core
   - optional env or home-dir defaults
2. **SDK / client crate**
   - offline profile versus host-integrated cache/network profile
3. **Plugin / extension runtime**
   - host-supplied filesystem/network/time handles versus ambient escape hatches
4. **Embedded / deterministic helper**
   - fixed clock / fixed RNG profile claims
5. **WASI / capability-oriented crate**
   - explicit `cap-std` / host-capability path versus absolute-path ambient fallback

If `0.1` cannot survive those five, the vocabulary is still too narrow.

## Adoption staircase

Do not require the ecosystem to jump straight to perfect static knowledge.

### Stage 1 — import and annotate
- generate a starter pack
- let maintainers mark profiles, budgets, and manual-review zones

### Stage 2 — local checks
- verify touchpoints, budgets, injection boundaries, and recipe declarations
- keep the vocabulary explicit and small

### Stage 3 — witness restricted profiles
- run conservative restricted recipes
- record what passed, failed, or stayed manual-review-only

### Stage 4 — summary and diff
- render human-facing authority notes
- compare releases and make drift visible

### Stage 5 — optional adapters
- import from `cap-std`, `ambient-authority`, `getrandom`, explicit-handle HTTP clients, and WASI-capability stacks
- remain adapter-first, not replacement-first

## Guardrails

A worthy `0.1` must stay conservative.

- It should prefer a false `manual_review_required` over a false “sandbox-ready” claim.
- It should never summarize one successful restricted test as proof of total authority absence.
- It should never treat capability-oriented substrate usage as proof that every public path is capability-safe.
- It should never hide example/test-only ambient usage; instead it should classify it explicitly.
- It should never infer “deterministic” merely because the crate compiled without network access once.

## Non-goals for `0.1`

- static proof of no hidden authority via FFI or proc-macro expansion,
- automatic rewriting toward capability APIs,
- owning OS/container sandbox policy,
- replacing `cap-std`, `ambient-authority`, or `rustix`,
- or inventing a universal security score for crates.

## Why this beats adjacent candidates right now

This lane beats “another sandbox crate” because the missing problem is usually not raw isolation machinery; it is the missing **receiver-facing contract** above that machinery.
It beats “another capability library” because the ecosystem already has meaningful substrate there.
It beats “another scanner” because downstream users still need budget, injection, and witness artifacts they can review and diff.
And it beats “just use docs.rs/read the code” because authority posture is too important to stay buried in source archaeology.

## Sources

- Rust vision doc on supportive interfaces from crates: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Safety-critical ecosystem support post: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust project goal on sandboxed build scripts: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- Cargo environment variables: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo build scripts: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- `ambient-authority` docs: https://docs.rs/ambient-authority/latest/ambient_authority/struct.AmbientAuthority.html
- `cap-std` docs: https://docs.rs/cap-std/latest/cap_std/
- `cap-std::fs::Dir` docs: https://docs.rs/cap-std/latest/cap_std/fs/struct.Dir.html
- `rustix` docs: https://docs.rs/rustix/latest/rustix/
- `wasi-cap-std-sync` docs: https://docs.rs/wasi-cap-std-sync/latest/wasi_cap_std_sync/
- `getrandom` docs: https://docs.rs/getrandom/latest/getrandom/
