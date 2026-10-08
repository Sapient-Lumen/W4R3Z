---
id: P-0509
title: Crate Ecosystem Pathfinder & Decision-Pack Kit — task-oriented crate selection, interop-aware starter sets, and reviewable decision receipts
status: idea
domains: [ecosystem, crates-io, cargo, onboarding, dx, interop]
last_reviewed: 2026-03-23
evidence:
  - https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
  - https://blog.rust-lang.org/2026/03/20/rust-challenges/
  - https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
  - https://doc.rust-lang.org/cargo/reference/manifest.html
  - https://doc.rust-lang.org/cargo/commands/cargo-search.html
  - https://doc.rust-lang.org/cargo/commands/cargo-add.html
  - https://docs.rs/about/metadata
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://doc.rust-lang.org/cargo/commands/cargo-info.html
  - https://github.com/rust-lang/crates.io/discussions/9325
  - https://rust-lang.github.io/rust-project-goals/2024h2/notes.html
  - https://internals.rust-lang.org/t/follow-up-the-rust-platform/3782
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
  - https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
  - https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
---

# Problem

Rust’s crate ecosystem is one of its superpowers, but it still asks users to accumulate too much **tacit knowledge** before they can make boring choices well.

The latest official vision-doc work says users still experience crate choice as “undiscoverable”, lack a clear starter set, and have trouble judging which crates are actually the ecosystem defaults for a task.
At the same time, official Cargo/crates.io surfaces still mostly give users:

- textual search,
- a few keywords/categories,
- descriptions/readmes,
- and a dependency add command that defaults to an existing dep, a workspace member, or the latest registry release.

Those are useful ingredients, but they do **not** produce a portable answer to questions like:

- “Which HTTP stack fits a small async service with Tokio, tracing, and serde?”
- “Which date/time crate is least likely to trap a newcomer later?”
- “Which crates are reasonable for a `no_std` embedded baseline?”
- “What is the least-locking-in starter set for a CLI app?”

The missing crate is therefore **not** another registry, another façade crate, or another trust score in isolation.
It is a **task-oriented decision layer** that can turn ecosystem tacit knowledge into a small, reviewable, check-in-able artifact.

The lane now also needs a candidate-specific memory layer: not just “what won”, but “why a plausible alternative lost” and “what would let it back in later.”

# What it provides

The crate should provide other people with a compact, explainable decision bundle for choosing crates in a given task lane.

## Core artifacts

- `task-profile.json` — the problem being solved, plus hard constraints (for example: `no_std`, async runtime policy, MSRV floor, license allowlist, target platforms, proc-macro tolerance, FFI tolerance, preferred interoperability crates).
- `candidate-import.report.json` — normalized candidate facts imported from crates.io/Cargo metadata/docs and optional adjacent tools.
- `candidate-basis.receipt.json` — per-candidate record of which source surfaces actually supplied facts, what freshness/authority class those facts have, and what still needs human review.
- `interop-surface.report.json` — runtime coupling, core trait expectations, serde/tracing/http integration, proc-macro/build-script exposure, `no_std`/Wasm posture, and “adoption friction” notes.
- `role-coverage.report.json` — which candidates cover which named roles, where companion crates are required, and where coverage is partial.
- `decision-axis.report.json` — separated axes for task fit, interop fit, adoption signal, teaching fit, maintenance/trust imports, migration friction, and uncertainty.
- `decision-pack.report.json` — ranked candidates, trade-offs, explicit eliminations, confidence level, and `manual_review_required` when evidence is thin or conflicting.
- `candidate-elimination.receipt.json` — per-candidate explanation of whether a crate was a runner-up, hard-blocked, policy-vetoed, out of scope, or still manual-review-only.
- `candidate-reentry.policy.json` — what exact change would let an excluded candidate re-enter consideration, and which public-surface changes are explicitly insufficient.
- `starter-set.lock.json` — the chosen starter set for a team/task, with versions, roles, accepted trade-offs, and review timestamp.
- `revisit-trigger.policy.json` — the event classes that force review of a frozen answer, such as advisories, malicious-crate notices, health/support posture changes, docs-surface shifts, or task-constraint changes.
- `freeze-horizon.policy.json` — the maximum age and review cadence allowed for a frozen starter set when no trigger has fired yet.
- `decision-watch.report.json` — the current watch state for a frozen decision: `steady`, `review_due`, `invalidated`, `superseded`, or `manual_review_required`, plus the trigger receipts that caused it.
- `decision-timebox.receipt.json` — exactly when the decision was frozen, which evidence windows were in-bounds, which cooldown policy applied, and which facts were still out of scope.
- `as-of-replay.report.json` — compares freeze-time basis with current-view replay, keeping visibility drift, fresh-release drift, and true task-fit drift separate.
- `evidence-weight.policy.json` — weighting/veto rules for a named task lane so “popularity” does not silently become the whole decision.
- `support-visibility.report.json` — what public registry/docs/tooling surfaces make the candidate look supported or legible, and what those visible surfaces still do **not** prove.
- `evidence-origin.report.json` — where the important facts came from: registry metadata, crate-authored docs, official Rust policy, imported receipts, local observation, or inference.
- `freshness-window.policy.json` — how recent publish/support/docs signal changes are allowed to influence automatic freezing versus manual review.
- `starter-set-scope.report.json` — whether a frozen answer is for teaching, production, org policy, or a narrower target/runtime lane.
- `starter-set-readiness.report.json` — whether the candidate stack is actually ready to freeze or still blocked by freshness, hidden companions, or scope ambiguity.
- `lockin-cost.report.json` — where runtime choice, proc-macros, trait gravity, or companion crates make future migration expensive.
- `scope-split.receipt.json` — whether teaching and production defaults intentionally diverge and why.
- optional `migration-notes.md` — “if you later move from crate A to crate B, here is where lock-in will hurt.”
- `pathfinder-bundle.manifest.json` — portable handoff that joins the task profile, decision pack, starter-set lock, basis receipts, visibility reports, watch policies, freeze-time receipts, replay reports, exclusion receipts, and re-entry policies for later review.
- optional `decision.summary.md` — short human-facing summary for ADRs, onboarding, or contributor docs.

## Commands

- `cargo pathfinder init --lane async_http_service`
- `cargo pathfinder import --task task-profile.json`
- `cargo pathfinder explain --task task-profile.json`
- `cargo pathfinder gate --task task-profile.json`
- `cargo pathfinder freeze --decision decision-pack.report.json`
- `cargo pathfinder watch --lock starter-set.lock.json`
- `cargo pathfinder replay --lock starter-set.lock.json --as-of 2026-01-15T00:00:00Z`
- `cargo pathfinder reconsider --candidate candidate_alpha`
- `cargo pathfinder capture --task task-profile.json`
- `cargo pathfinder doctor --decision decision-pack.report.json`
- `cargo pathfinder diff old-decision.json new-decision.json`
- `cargo pathfinder bundle --decision decision-pack.report.json`

## Adjacency rule

This crate should **import** adjacent evidence when available instead of reinventing it:

- **P-0011 Crate Health** for maintenance/MSRV/governance posture
- **P-0017 Trust Lens** for confusables / trust-cost / security posture
- **P-0006 stdx-curated** when a façade/battery pack is the actual intended output

# Users & user stories

- **New Rust user**: “Give me a sane starter set for CLI + config + logging + error handling, and tell me why.”
- **Team lead**: “Freeze one reviewable starter pack for services on Tokio without turning it into a forever-forked internal wiki page.”
- **Library author**: “Show me the crates that minimize runtime lock-in and have the cleanest interop surface.”
- **Educator**: “Pick a teaching stack that matches official docs expectations and avoids surprising later rewrites.”
- **Platform/security team**: “Allow only candidates that fit our license/MSRV/trust policy, but still tell developers what the next-best choice is.”

# Prior art (and why it’s insufficient)

- **crates.io/Cargo search surfaces** are real and useful, but they are intentionally generic: textual search plus small metadata fields.
- **`cargo add`** is ergonomic for adding a known crate, but it is not a task recommender.
- **docs.rs** and README browsing help users inspect a candidate once they already suspect it is relevant.
- **P-0011 Crate Health** can describe whether a crate looks sustained; it does not answer whether it is the right crate for a specific task.
- **P-0017 Trust Lens** can score trust/risk posture; it does not answer ergonomic fit or interop fit.
- **P-0006 stdx-curated** could become a dependency-minimal “golden path”; it does not solve the broader decision problem for task-specific lanes across the ecosystem.
- Third-party catalogs and blog posts can help, but they do not emit a stable artifact a team can review, diff, and check into source control.

# Design goals

1. **Task-first, not crate-first.** Start from “what are you trying to do?” rather than “which famous crate should win?”
2. **Explainability over magic.** Every ranking should say why a candidate rose or fell.
3. **Interop-aware.** Async runtime coupling, trait ecosystem alignment, proc-macro/build-script posture, and target support must be first-class facts.
4. **Import, don’t absorb.** Health/trust/curation/publish-receipt crates should remain separate lanes.
5. **Portable decisions.** Teams should be able to commit the resulting decision pack to a repo and revisit it later.
6. **Historical honesty.** The crate should record what was actually knowable at freeze time instead of letting the current ecosystem silently rewrite history.
7. **Popularity is advisory, not destiny.** Adoption signal can break ties or warn about ecosystem reality, but it must not erase fit, lock-in, or teaching cost.
8. **Provenance matters.** Registry metadata, crate-authored docs, official Rust policy, and imported receipts must not be silently flattened into one evidence class.
9. **Freshness matters.** Newly published crates and newly surfaced signals should be visible, but not automatically frozen into starter sets.
10. **Scope must stay explicit.** A teaching starter set, a production starter set, and an org-policy starter set are different artifacts even when they overlap.
11. **Honest uncertainty.** When evidence is incomplete, the output should say `manual_review_required`, not fabricate consensus.
12. **Broad applicability.** The same substrate should work for CLI, services, embedded, Wasm, GUI, data, and niche domain lanes.

# Non-goals

- Replacing crates.io search or ranking globally.
- Officially blessing one crate per category on behalf of the Rust project.
- Becoming a façade crate that reexports ecosystem defaults.
- Inventing a new security/trust model instead of importing adjacent evidence.
- Pretending to compute a universal objective quality score for crates.
- Running arbitrary downstream benchmarks or test suites in 0.1.

# Architecture & API sketch

## Crate split

- `pathfinder-core` — task model, candidate model, role coverage, ranking engine, decision-pack schema
- `pathfinder-import` — crates.io/Cargo/docs adapters, freshness receipts, and cache
- `pathfinder-interop` — task-lane rules (runtime coupling, `no_std`, Wasm, proc-macro/build-script, trait ecosystem)
- `pathfinder-policy` — evidence-weight policy, hard vetoes, and manual-review boundaries
- `cargo-pathfinder` — CLI and repo-facing workflow

## Task profile sketch

```json
{
  "schema_version": "0.1",
  "task": "async_http_service",
  "constraints": {
    "runtime": "tokio",
    "msrv_floor": "1.82",
    "targets": ["x86_64-unknown-linux-gnu", "aarch64-apple-darwin"],
    "no_std": false,
    "license_allowlist": ["MIT", "Apache-2.0", "MIT OR Apache-2.0"]
  },
  "roles": ["http_server", "routing", "serialization", "logging", "error_handling"],
  "preferences": {
    "prefer_low_runtime_lockin": true,
    "prefer_widely_adopted": true,
    "prefer_small_dependency_surface": false
  }
}
```

## Ranking model sketch

A first version can score along visibly separate axes:

- hard vetoes,
- task fit,
- role coverage,
- interop fit,
- teaching fit,
- maintenance posture import,
- trust/risk import,
- ecosystem adoption signal,
- migration friction,
- uncertainty.

The output should keep those axes separate instead of collapsing them into one fake objective number or popularity rank.

## 0.1 task families

- `cli_baseline`
- `async_http_service`
- `sync_http_client`
- `embedded_no_std_baseline`
- `wasm_browser_client`
- `desktop_gui_baseline`
- `dataframe_pipeline_baseline`

# Security / safety model

- Default to **read-only metadata collection** and cached imports.
- Avoid hidden network fetches in “offline review” mode.
- Treat popularity/adoption signals as **advisory**, not proof of fitness or safety.
- Never auto-edit `Cargo.toml` unless the user explicitly asks for manifest changes.
- Record source freshness so downstream reviewers can see when a decision may need to be revisited.
- Never auto-replace a frozen starter set merely because a trigger fired; distinguish `review_due` from `replacement_required`.

# Maintenance & governance plan

- Keep artifact schemas versioned and stable.
- Publish fixture families for common task lanes and edge cases.
- Maintain transparent scoring rules plus an allowlist for manual overrides/exceptions.
- Require every 1.0-worthy task profile to have at least one cross-platform and one “surprising loser” fixture.
- Encourage teams to commit decision packs locally instead of relying on a central service.

# Milestones

## 0.1
- task profile schema
- metadata import pipeline
- ranked decision pack for 3–5 task families
- frozen starter-set lock artifact
- offline review mode

## 0.2
- interop-surface analyzer
- imports from P-0011 and P-0017 when available
- decision diff / review tooling
- frozen-decision watch state and revisit-trigger policies
- GitHub Action for “starter set drift” PRs

## 0.3
- lane-specific heuristics for embedded/Wasm/GUI/data
- manual override policy file
- migration-notes generator

## 1.0
- stable schemas
- curated fixture corpus across at least six task families
- evidence-driven docs explaining why the tool did **not** produce a universal winner

# Open questions

- Which signals are too political or too gameable to treat as ranking inputs?
- How aggressive should freshness windows be for newly published crates or newly surfaced support signals?
- Which recommendation facts must always carry explicit provenance labels?
- Should the default output rank multiple candidates by lane, or only emit a “starter pack” when confidence is high enough?
- Which facts belong in imported health/trust artifacts versus pathfinder-native interop artifacts?
- How should the crate represent “ecosystem default for teaching” versus “ecosystem default for production” when they differ?


## 2026-03-19 productization refresh

This pass keeps the original thesis but sharpens the product around three review objects that were previously too implicit:

- **starter-set readiness** — whether a ranked answer is actually mature enough to freeze,
- **lock-in cost** — what exit cost the selected stack buys through runtime choice, macros, traits, and companion crates,
- **scope split** — whether teaching and production defaults intentionally diverge.

That means **P-0509** should now be read less as “task-oriented crate ranking” and more as **freezeable decision support for scoped starter sets**.
A convincing `0.1` should expose commands such as `init`, `import`, `explain`, `gate`, `freeze`, `doctor`, `diff`, and `bundle`, and it should emit first-class artifacts like:

- `starter-set-readiness.report.json`
- `lockin-cost.report.json`
- `scope-split.receipt.json`

Those additions matter because the archive had already made role coverage, evidence weighting, evidence origin, freshness windows, and starter-set scope explicit, but it still did not cleanly separate:

- “this crate ranks highly for the task”,
- “this starter answer is boring enough to freeze”,
- “this stack is easy to teach but expensive to leave later”,
- and “we are deliberately publishing different defaults for different scopes”.

## 2026-03-20 decision-aging refresh

This pass keeps the same thesis but sharpens the product around three more review objects that frozen decisions were still missing:

- **revisit-trigger truth** — which event classes reopen a frozen decision,
- **freeze-horizon truth** — how long a frozen answer may age quietly before review is due,
- **decision-watch truth** — whether the starter set is still steady, due for review, invalidated, or already superseded.

That matters because the archive had already made freshness windows explicit, but freshness windows answer a different question: whether a *new* candidate or signal is too fresh to freeze right now. They do **not** answer what should happen when a team already froze a decision and then:

- a RustSec advisory or malicious-crate notice lands,
- docs.rs target visibility changes,
- a health/support posture import changes without a new code release,
- or the lock simply grows old enough that the decision should no longer pretend to be freshly reviewed.

So **P-0509** should now be read less as “freezeable decision support” and more as **freezeable-and-reviewable decision support**.
A convincing `0.2` should expose first-class artifacts like:

- `revisit-trigger.policy.json`
- `freeze-horizon.policy.json`
- `decision-watch.report.json`

Those additions matter because the archive had already learned how to say:

- “this stack may be frozen”,
- “this stack buys lock-in”,
- and “this scope split is intentional”,

but it still did not cleanly separate:

- “this frozen decision remains steady”,
- “this frozen decision is due for review”,
- “this trigger invalidates the recommendation until humans re-check it”,
- and “this trigger is merely new information, not automatic crate replacement”.

## 2026-03-22 import-basis refresh

This pass keeps the same thesis but sharpens the product around three more review objects that task-first ranking still left too implicit:

- **candidate basis** — which source surfaces actually supplied the facts,
- **support visibility** — what public registry/docs/tooling surfaces make a candidate legible without settling task fit,
- **portable bundle shape** — what another team must receive to review the decision later without reconstructing it from memory.

That matters because the archive already had candidate import, role coverage, evidence origin, starter-set readiness, lock-in cost, scope split, and decision watch.
But it still did not cleanly separate:

- “Cargo could find/add this package”,
- “crates.io and docs.rs make this candidate look polished and visible”,
- “these exact facts came from these exact surfaces”,
- and “this is therefore the right starter-set choice for the task”.

So **P-0509** should now be read less as “freezeable-and-reviewable decision support” and more as **freezeable, reviewable, and import-honest decision support**.
A convincing next pass should expose first-class artifacts like:

- `candidate-basis.receipt.json`
- `support-visibility.report.json`
- `pathfinder-bundle.manifest.json`

Those additions matter because the ecosystem now has richer registry/docs/tooling signals, but a worthwhile crate contribution still needs to help other people answer the harder question: **what should we choose, why, and what exactly backed that answer?**


# Sources

- Rust vision-doc analysis of supportiveness, async difficulty, and crate discoverability: https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2024 State of Rust survey results: https://blog.rust-lang.org/2025/02/13/2024-State-Of-Rust-Survey-results/
- Cargo manifest metadata (`keywords`, `categories`): https://doc.rust-lang.org/cargo/reference/manifest.html
- `cargo search` docs: https://doc.rust-lang.org/cargo/commands/cargo-search.html
- `cargo add` docs: https://doc.rust-lang.org/cargo/commands/cargo-add.html
- crates.io development update (Security tab, Trusted Publishing, `pubtime`, filtered Cargo-only downloads): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious-crate policy update: https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- docs.rs default-target change announcement: https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Rust debugging survey 2026: https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io search discussion on ranking/order limits: https://github.com/rust-lang/crates.io/discussions/9325
