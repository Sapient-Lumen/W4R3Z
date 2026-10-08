# Crate authority-surface product plan — 2026-03-19

This note exists to keep **P-0519 Crate Authority Surface Pack Kit** disciplined.
The archive already decided that the missing value is a **receiver-facing ambient-authority / determinism / injection / sandbox-profile contract**.
This pass answers a narrower question:

> If somebody actually started building **P-0519** this week, what should version `0.1` look like once we treat **authority origin**, **fallback order**, and **refusal posture** as first-class review objects rather than vague caveats?

## Main judgment

A buildable `0.1` should still be a **small cargo subcommand plus library**.
But the center of gravity is now sharper:

- not just **what** powers exist,
- but **where they come from**,
- **which path is preferred before widening into more authority**,
- and **what happens when the host says no**.

That means a worthy `0.1` should help crate authors publish one reviewable answer to:

- which ambient powers the crate may exercise in each named profile,
- whether each power comes from injected handles, caller-supplied paths, host-supplied capabilities, project-dir discovery, ambient temp roots, OS entropy, or manual-review-only zones,
- what fallback chain widens authority when the preferred path is unavailable,
- whether denied authority yields a hard error, degraded mode, silent fallback, retry, or manual review,
- which sandboxed / offline / deterministic recipes were actually witnessed,
- and how those facts changed between releases.

It should **not** become a new sandbox runtime, a new capability library, or a new static-scanning proof system.
Those are imports, not the product.

## What the crate should provide other people

For downstream users, release reviewers, and policy teams, the crate should provide:

1. **One compact authority contract** instead of folklore spread across README prose, examples, shell recipes, and source spelunking.
2. **Authority-origin truth** so users can tell whether a power is ambient, caller-supplied, host-supplied, capability-based, or owned by the root crate.
3. **Fallback-order truth** so users can tell whether an injected or explicit path is really preferred before ambient discovery or tempdir fallback.
4. **Refusal-posture truth** so “offline-ready” or “sandbox-ready” means more than “we think it should probably work”.
5. **Injection-boundary truth** so clock, RNG, filesystem, network, cache, and process dependencies stop being guessed at.
6. **Profile witnesses** showing whether a named profile actually survived real restrictions.
7. **A release diff** that makes new ambient reads, widened fallbacks, or denial-behavior regressions loud.
8. **A short human summary** that can be pasted into docs, policy review, or dependency-adoption notes.

For maintainers, the crate should provide:

1. a small policy file that is cheap to review,
2. explicit `manual_review_required` escape hatches instead of fake certainty,
3. adapters for capability-oriented and explicit-handle patterns instead of bespoke reinvention,
4. one place to record “root crate owns this backend choice” versus “library boundary exposes injection”,
5. and a CI gate for “this release changed authority posture”.

## Recommended `0.1` command surface

### `cargo authority-surface init`
Create a starter `authority-pack.toml` by importing obvious candidates from:

- maintainer-declared profiles,
- visible filesystem / env / tempdir / network / time / randomness / process touchpoints,
- declared feature flags and examples,
- obvious explicit-handle patterns,
- project-dir / tempdir helpers,
- and known capability-oriented APIs when they are used directly.

The generated pack should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo authority-surface capture`
Emit one normalized authority bundle from a declared profile or recipe.
This should capture:

- observed touchpoints,
- authority origins,
- authority budgets,
- fallback chains,
- refusal posture,
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
- do authority origins and fallback chains remain compatible with the declared profile,
- do injection-boundary declarations match the touched APIs or adapters,
- do refusal-posture claims match recipe outcomes,
- and which parts remain manual-review-only?

### `cargo authority-surface doctor`
Render human-facing warnings for suspicious situations such as:

- `explicit_dir_loses_priority_to_home_probe`
- `project_dirs_denied_but_tempdir_fallback_is_silent`
- `custom_rng_backend_owned_by_library_not_root_crate`
- `ambient_temp_root_used_even_when_dir_capability_available`
- `profile_claim_without_witness`
- `manual_review_required`

`doctor` should be a human-first renderer over captured artifacts, not a magical verifier.

### `cargo authority-surface summary`
Render a short receiver-facing note for dependency review, docs, or sandbox-policy handoff.
A good summary answers:

- which profiles exist,
- where their powers originate,
- what fallback order widens authority,
- what happens when the host denies access,
- what can be injected,
- what was actually witnessed,
- and where the caveats are.

### `cargo authority-surface diff <old> <new>`
Compare two receipts or packs and classify:

- `authority_added`
- `authority_removed`
- `origin_changed`
- `fallback_changed`
- `refusal_posture_changed`
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
  - import logic for touchpoints, explicit-handle patterns, project-dir/tempdir calls, and authority hints
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
- `authority_surface_cap_directories`
- `authority_surface_cap_tempfile`
- `authority_surface_getrandom`
- `authority_surface_time`
- `authority_surface_http_client`
- `authority_surface_cache_dirs`
- `authority_surface_wasi`
- `authority_surface_capsec_import`

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
- `authority-budget.policy.json`
- `injection-boundary.receipt.json`
- `profile-witness.report.json`

This pass adds three more important artifacts:

- `authority-origin.receipt.json` — where a power actually originates, such as `caller_supplied_path`, `injected_handle`, `host_supplied_capability`, `ambient_project_dirs`, `ambient_temp_dir`, `os_entropy`, `root_crate_backend_choice`, or `manual_review_required`.
- `fallback-chain.report.json` — the preferred and fallback order for acquiring a capability or host service.
- `refusal-posture.report.json` — what the crate does when the host denies a requested authority.

Those files matter because authority support gets vague again if the archive only records “this crate touches env/network/filesystem” without making clear:

- who owns the authority choice,
- what path is preferred before fallback,
- and whether denial fails honestly or silently widens into more power.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Declared public surface**
   - `authority-pack.toml`
   - maintainer-declared profiles and touchpoints
2. **Observed touchpoints**
   - filesystem, env, tempdir, home dir, network, time, randomness, process, stdio, thread, host probes
3. **Authority origins**
   - caller path / explicit config
   - construction-time handle
   - per-operation handle
   - host-supplied capability
   - project-dir discovery
   - ambient temp dir
   - OS entropy / backend selection
4. **Fallback chains**
   - explicit first choice
   - degraded or convenience fallbacks
   - ambient widening steps
5. **Refusal posture**
   - hard error
   - degraded mode
   - silent fallback
   - retry
   - manual review
6. **Profile budgets**
   - required, optional, forbidden, or manual-review authority
7. **Recipe witnesses**
   - restricted runs under no-network / empty-env / no-home / read-only-fs / fixed-time / fixed-rng / no-spawn
8. **Manual review zones**
   - hidden FFI, indirect runtime behavior, backend-specific drift, or unexercised examples

The importer should prefer visible uncertainty over synthesis.

## Authority-origin policy

The first implementation should treat **authority origin as first-class review material**.
A good `0.1` should model:

- `caller_supplied_path`
- `caller_supplied_url`
- `injected_handle`
- `injectable_at_construction`
- `injectable_per_operation`
- `host_supplied_capability`
- `ambient_project_dirs`
- `ambient_temp_dir`
- `ambient_env`
- `os_entropy`
- `root_crate_backend_choice`
- `manual_review_required`

What matters is not only that a dependency is injectable somewhere, but **who owns the authority decision**.
A crate that says “the root binary chooses the entropy backend” is different from one that silently owns the choice inside a library crate.

## Fallback-chain policy

The first implementation should treat **fallback chains as explicit review objects**.
A good `0.1` should record:

- the preferred path,
- each fallback step,
- whether the step widens authority,
- whether the step preserves or breaks profile claims,
- and whether the chain ends in a hard error or an ambient escape hatch.

The crate should stay conservative about “helpful” fallbacks.
An explicit cache root that quietly falls back to home-dir discovery or tempdir should not be summarized the same way as a crate that simply fails and asks the caller for a path.

## Refusal-posture policy

The first implementation should treat **denied authority as witnessed behavior** rather than prose.

### What should count as refusal classes in `0.1`

- `hard_error`
- `degraded_mode`
- `silent_fallback`
- `retry_then_error`
- `manual_review_required`

### What should count as standard restriction sets in `0.1`

- `no_network`
- `empty_env`
- `no_home_dir`
- `readonly_fs`
- `deny_project_dirs`
- `deny_temp_dir`
- `fixed_rng`
- `no_process_spawn`

The refusal report should make it obvious whether a crate:

- failed loudly under denied authority,
- degraded in a documented way,
- silently widened into another authority source,
- or was never actually exercised.

## Preferred proving grounds

Future implementation passes should keep testing these concrete families:

- a crate that advertises an injectable cache root but still probes `$HOME` first,
- a crate that degrades from project dirs into ambient tempdir without telling users,
- a library crate that defines a `getrandom` backend instead of leaving entropy ownership to the root crate,
- a capability-oriented tempdir path that should beat ambient temp discovery when a `Dir` is already available.

## Main boundary to keep sharp

Do not let **P-0519** collapse back into either of these easier stories:

- “we have a static authority scan, therefore we solved authority support”,
- “we use capability crates somewhere, therefore the dependency is sandbox-ready”.

The product is the maintainer-authored contract **above** those pieces.
