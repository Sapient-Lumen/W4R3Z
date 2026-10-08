# Crate ecosystem pathfinder product plan — 2026-03-17

This note exists to keep **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** disciplined.
The archive already decided that the missing value is a **task-oriented decision layer** above crates.io/Cargo/docs browsing.
This pass answers a narrower question:

> If somebody actually started building **P-0509** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps people publish one reviewable answer to:

- what task is being solved,
- which roles and hard constraints matter,
- which candidates were imported,
- where runtime / target / `no_std` / proc-macro / build-script lock-in lives,
- how popularity, maintenance, and trust signals were weighed,
- and whether a starter set is justified or manual review is still required.

It should **not** try to become a replacement registry, a hosted recommendation engine, a universal “best crate” score, or an official Rust blessing process.
Those are adjacent governance or infrastructure concerns, not the product.

## What the crate should provide other people

For downstream users, team leads, educators, and release reviewers, the crate should provide:

1. **One compact decision artifact** instead of folklore scattered across README prose, issue threads, Discord advice, and stale internal wiki pages.
2. **A task profile** that states the real job: async service, CLI baseline, `no_std` embedded, Wasm browser client, desktop GUI baseline, or another named lane.
3. **A role-coverage report** so users can see whether a crate family actually covers the needed roles or only wins on one narrow dimension.
4. **An interop / lock-in report** so runtime coupling, trait ecosystem expectations, proc-macro/build-script posture, and target boundaries stop being hidden costs.
5. **An evidence-origin report** so registry metadata, crate-authored docs, official Rust policy, imported receipts, and direct observation do not get flattened into one authority class.
6. **A decision-axis report** so task fit, teaching fit, adoption signal, maintenance imports, trust imports, and migration friction stay visibly separate.
7. **A freshness-window policy** so newly published crates or freshly changed support signals do not silently become frozen defaults without review.
8. **A starter-set lock plus scope report** that a team can commit to source control when confidence is high enough and the intended scope is explicit.
9. **A manual-review summary** when the evidence is mixed, stale, or role-dependent.
10. **A short human summary** that can be pasted into onboarding docs, ADRs, or contributor guides.

For maintainers of the decision artifact, the crate should provide:

1. a small policy file for ranking/veto logic,
2. explicit hard-constraint failures instead of soft hand-waving,
3. visible freshness and uncertainty markers,
4. diffable output for release-to-release reconsideration,
5. and fixture-first task lanes that keep the product from drifting into generic recommendation theater.

## Recommended `0.1` command surface

### `cargo pathfinder init --task <lane>`
Create a starter `task-profile.toml` for a named lane such as:

- `cli_baseline`
- `async_http_service`
- `embedded_no_std_baseline`
- `wasm_browser_client`
- `desktop_gui_baseline`

The generated task should be incomplete on purpose.
Anything uncertain should be marked `manual_review_required` rather than guessed.

### `cargo pathfinder import --task task-profile.toml`
Collect a compact `candidate-import.report.json` from declared sources such as:

- registry search/import surfaces,
- package metadata (`keywords`, `categories`, version, features),
- docs/README imports,
- and optional imported health/trust receipts.

The importer should record where evidence came from and how fresh it is.
It must not pretend imported metadata is the same thing as task fit.

### `cargo pathfinder explain --task task-profile.toml`
Emit:

- `role-coverage.report.json`
- `interop-surface.report.json`
- `decision-axis.report.json`
- `decision-pack.report.json`
- `decision.summary.md`

`explain` is the heart of the product.
It should keep distinct:

- hard vetoes,
- role coverage,
- interop coupling,
- adoption signal,
- health/trust imports,
- migration friction,
- and unresolved ambiguity.

### `cargo pathfinder freeze --decision decision-pack.report.json`
When confidence is high enough, emit `starter-set.lock.json`.
If confidence is not high enough, the command should refuse to pretend that a frozen starter set exists.

### `cargo pathfinder diff <old> <new>`
Compare two decision bundles and classify:

- `task_profile_changed`
- `candidate_added`
- `candidate_removed`
- `role_coverage_changed`
- `interop_lockin_changed`
- `health_or_trust_import_changed`
- `starter_set_changed`
- `manual_review_boundary_changed`

### `cargo pathfinder bundle`
Emit one compact `.pathfinder.zip` bundle for ADRs, onboarding, security review, or internal starter-stack governance.

## Recommended crate/workspace split

Keep the first implementation modular but not over-factored.
A good starting shape would be:

- `pathfinder_model`
  - shared Rust types for task profiles, role coverage, decision axes, packs, locks, and diffs
- `pathfinder_import`
  - metadata/docs import logic and freshness receipts
- `pathfinder_rules`
  - hard-constraint rules, evidence-weight policy parsing, and lane-specific heuristics
- `pathfinder_render`
  - summary rendering, markdown output, and zip bundle emission
- `cargo-pathfinder`
  - user-facing CLI / cargo subcommand

Optional adapters should stay optional until the core vocabulary is trusted:

- `pathfinder_health_import`
- `pathfinder_trust_import`
- `pathfinder_docs_import`

## `0.1` artifact set

The archive already had the right center of gravity.
`0.1` should revolve around:

- `task-profile.json`
- `candidate-import.report.json`
- `interop-surface.report.json`
- `decision-pack.report.json`
- `starter-set.lock.json`
- `decision.summary.md`

This pass adds six more important artifacts around the original core:

- `evidence-weight.policy.json` — how hard constraints, task fit, interop fit, teaching fit, adoption signal, imported health/trust, and migration friction are weighed.
- `role-coverage.report.json` — which candidate covers which role, where one crate family needs companions, and where gaps remain.
- `decision-axis.report.json` — explicit per-candidate axis values so the product does **not** collapse everything into a fake objective score.
- `evidence-origin.report.json` — which important recommendation facts came from registry metadata, crate-authored docs, official Rust policy, imported receipts, local observation, or inference.
- `freshness-window.policy.json` — which signal classes may influence a frozen recommendation immediately, which should stay in cooldown, and which are import-only until review.
- `starter-set-scope.report.json` — whether the frozen answer is for teaching, production, org policy, target-specific use, or still requires scope review.

Those files matter because pathfinder gets vague again if the archive only records “crate X ranked first” without making clear:

- what task was optimized for,
- which roles mattered,
- which vetoes were applied,
- which evidence classes carried real authority,
- whether a very new signal was still in a review window,
- and whether the frozen answer was actually scoped for the audience using it.

## Discovery order

A disciplined import order helps prevent fake certainty.

1. **Task profile**
   - lane name
   - roles
   - hard constraints
   - environment assumptions
2. **Candidate import**
   - registry/docs metadata
   - freshness class
   - candidate families
   - evidence-origin labeling
3. **Freshness gate**
   - new publish cooldowns
   - docs-surface or support-signal review windows
   - import-only versus freeze-eligible signals
4. **Hard-veto pass**
   - `no_std` mismatch
   - runtime-policy mismatch
   - target mismatch
   - forbidden proc-macro/build-script posture
   - license or policy mismatch
5. **Role coverage**
   - which candidate covers which named role
   - where companion crates are required
   - where gaps remain
6. **Interop / lock-in analysis**
   - runtime coupling
   - ecosystem-trait alignment
   - target/platform posture
   - migration friction
7. **Imports from adjacent lanes**
   - health posture
   - trust/risk posture
8. **Manual review zones**
   - unresolved ties
   - stale evidence
   - domain-specific caveats
   - tasks where role-dependent winners differ

The importer should prefer visible uncertainty over synthesis.

## Ranking discipline

The first implementation should treat **popularity and adoption as advisory inputs**, not as the product’s hidden truth.
A good `0.1` should keep separate:

- `hard_veto`
- `task_fit`
- `role_coverage`
- `interop_fit`
- `teaching_fit`
- `adoption_signal`
- `health_import`
- `trust_import`
- `migration_friction`
- `uncertainty`
- `evidence_origin_confidence`
- `freshness_gate`
- `starter_set_scope`

### What should count as a `starter_set_ready` verdict in `0.1`

Only when all of the following are true:

- all required roles are covered,
- no hard veto is active,
- the winning stack does not rely on hidden companion crates or undocumented setup steps,
- the decisive evidence classes are explicit and not mostly inference,
- no critical signal is still inside a freshness cooldown,
- the intended starter-set scope is explicit,
- uncertainty is not dominant,
- and the tool can explain the choice in ordinary language.

### What should force `manual_review_required` in `0.1`

- equally plausible winners with materially different lock-in costs,
- conflicting evidence between docs and observed ecosystem posture,
- a critical recommendation fact whose origin is mostly inference,
- a key candidate that is still inside a freshness cooldown,
- stale metadata or absent docs for a critical role,
- domain lanes where a “teaching default” and a “production default” diverge too sharply,
- or constraint sets so specific that generic ranking would mostly be theater.

## Scenario families that should pressure `0.1`

### `async_http_service_tokio_lockin_tradeoff`
At least two plausible service stacks should exist, but the report must make runtime coupling, middleware alignment, and migration cost explicit instead of faking a universal winner.

### `cli_baseline_newcomer_vs_power_stack`
The report should show that beginner success and long-term extensibility can disagree without treating either side as objectively wrong.

### `embedded_no_std_alloc_split`
The report should surface `no_std` / `alloc` / proc-macro / host-tool boundaries as first-order facts, not footnotes.

### `manual_review_required_conflicting_signals`
A lane where adoption/popularity and task/interop fit disagree strongly should force the tool to stop at reviewable ambiguity.

### `pubtime_cooldown_prevents_fresh_release_overpromotion`
A newly published candidate may be imported and discussed, but freshness policy should stop it from silently becoming the frozen default stack before a review window clears.

### `docsrs_default_target_shift_changes_visible_support_story`
A change in docs.rs default targets should not be mistaken for the same thing as a real shift in task fit or a universal support recommendation.

### `trusted_publishing_and_security_tab_do_not_equal_task_fit`
Security-tab or Trusted-Publishing posture may raise confidence in one axis, but it should not erase role coverage, interop lock-in, or scope mismatches.

## Adoption plan

A believable `0.1` should target three low-drama adoption surfaces first:

1. **internal ADRs** for teams choosing a starter stack,
2. **teaching / onboarding repos** that want a checked-in explanation,
3. **platform/security teams** that need a transparent decision artifact rather than an oral tradition.

Do **not** start with “replace crates.io search” or “become the ecosystem’s official recommender.”
The crate should win first as a **small review artifact**.

## What to leave for later

Keep these out of `0.1` unless they fall out naturally:

- hosted recommendation services,
- automatic `Cargo.toml` editing,
- registry-wide rankings,
- machine-learned recommendation models,
- official Rust-project blessing workflows,
- and giant domain corpora that cannot be reviewed locally.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
- https://doc.rust-lang.org/cargo/commands/cargo-search.html
- https://doc.rust-lang.org/cargo/commands/cargo-add.html
- https://doc.rust-lang.org/cargo/reference/manifest.html
- https://github.com/rust-lang/crates.io/discussions/9325
- https://internals.rust-lang.org/t/follow-up-the-rust-platform/3782
