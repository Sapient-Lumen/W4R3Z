# Frontier salience snapshot — 2026-03-18 (58)

This pass did **not** promote a new lane.
It sharpened an already-strong cross-cutting proposal:

- **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — because the archive still needed a more reviewable answer to the question “which starter stack should we trust for this task, and why should we trust *this* recommendation now?”

## Main judgment

The next worthy move here was **not** another global crate ranker, another “awesome Rust” list, another trust score in isolation, or another attempt to settle official blessing politics.
Those already exist in partial form or fail for governance reasons.

The sharper missing layer is the **task-oriented decision contract** above them, especially once three more facts are separated cleanly:

- explicit **evidence-origin reports**,
- explicit **freshness-window policies**,
- explicit **starter-set-scope reports**,
- plus the already-added task profiles, role-coverage reports, interop reports, decision axes, starter-set locks, and manual-review boundaries.

That move is better grounded now because:

- the Rust vision-doc work still treats crate discoverability and supportive ecosystem surfaces as part of Rust’s actual product experience;
- the 2025 State of Rust survey still says docs and code are the main learning surfaces;
- the 2026 debugging survey makes it explicit that debugging quality remains a major challenge, so choosing crates without support-surface awareness is still too shallow;
- crates.io now has a Security tab, Trusted Publishing enhancements, SLOC metrics, `pubtime` in the index, and filtered Cargo-only download counts;
- docs.rs changed default build targets in October 2025, which changes visible support posture for many crates;
- Cargo is actively working on build analysis and build-dir-layout changes, which means tool-facing support signals are still moving;
- and rustup / Cargo / docs.rs continue to evolve quickly enough that stale recommendation folklore gets less trustworthy over time, not more.

So the gap is no longer “Rust has no search, metadata, or trust signals”.
The gap is that teams still rarely get a **reviewable provenance-aware / freshness-aware / scope-aware starter-stack decision artifact** above those moving pieces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0451 Cfg Availability Ledger Kit** — still the sharpest item-level conditional-support truth lane.
7. **P-0519 Crate Authority Surface Pack Kit** — still one of the strongest ambient-power review lanes.
8. **P-0510 Crate Capability Contract & Interop Profile Kit** — still the strongest producer-side fact surface for a single crate.
9. **P-0521 Crate Resource Surface Pack Kit** — still one of the best capacity/support contracts in the frontier.
10. **P-0513 Crate Runtime Handoff Pack Kit** — still the strongest post-failure support-bundle lane.

## Why this won over adjacent candidates right now

- It beat **more niche protocol or format workbenches** because this lane multiplies value across nearly every ecosystem domain.
- It beat **more trust-only or health-only follow-ons** because new trust signals still do not answer task fit or scope by themselves.
- It beat **more docs or examples follow-ons** because even good support surfaces are downstream of choosing a plausible stack.
- It beat **more global ranking ideas** because new signals from crates.io/docs.rs/toolchain policy make unscoped rankings look even more fake.

## What changed in the archive

Added:
- `meta/frontier-salience-2026-03-18-58.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `fixtures/crate-ecosystem-pathfinder-kit/evidence-origin.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/freshness-window.policy.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/starter-set-scope.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/pubtime_cooldown_prevents_fresh_release_overpromotion/`
- `fixtures/crate-ecosystem-pathfinder-kit/docsrs_default_target_shift_changes_visible_support_story/`
- `fixtures/crate-ecosystem-pathfinder-kit/trusted_publishing_and_security_tab_do_not_equal_task_fit/`
- `entries/2026-03-18-238.md`

Updated:
- `proposals/crate-ecosystem-pathfinder-kit.md`
- `meta/crate-ecosystem-pathfinder-product-plan-2026-03-17.md`
- `fixtures/crate-ecosystem-pathfinder-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- registry metadata,
- crate-authored docs,
- official Rust policy,
- imported trust/health receipts,
- fresh-publish novelty,
- and a frozen starter-set answer for one specific scope

into one fake “best crate” story.

## Sources

- https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2026/03/12/Rustup-1.29.0/
