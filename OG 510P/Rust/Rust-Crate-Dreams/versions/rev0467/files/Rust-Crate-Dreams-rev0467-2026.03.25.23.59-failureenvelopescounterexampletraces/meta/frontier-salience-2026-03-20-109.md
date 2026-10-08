# Frontier salience snapshot — 2026-03-20 (109)

This pass did **not** add another ranking engine, another always-online recommendation bot, or another blessed-crates list.
It deepened **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** by making one more receiver-facing truth explicit:

- **decision-aging truth** — a frozen starter-set lock now needs explicit **revisit triggers**, **freeze horizons**, and **decision-watch state** so later security/support/docs shifts do not hide behind an old but tidy decision bundle.

## Main judgment

The archive already knew how to say:

- which crates fit a task,
- whether a starter answer is mature enough to freeze,
- where lock-in lives,
- and whether teaching and production defaults diverge.

What it still lacked was one compact way to say:

- which later events force a re-check,
- how long a frozen answer may age quietly,
- whether a fired trigger means `review_due` or `invalidated`,
- and whether a frozen answer has actually been superseded by a newer reviewed decision.

That is now more urgent because Rust’s ecosystem surfaces move faster than a team’s internal decision docs:

- the vision-doc work still frames crate discovery and starter-set orientation as a real obstacle,
- the 2025 survey still says docs/code remain the canonical learning surfaces and maintainers support remains a concern,
- crates.io now exposes security/publishing/`pubtime` substrate that can change the interpretation of a frozen choice,
- routine malicious-crate removals now flow through RustSec advisories/RSS,
- and docs.rs target-default shifts proved that visible support posture can move without the chooser touching their local lock.

So the sharper gap is no longer just “freezeable crate choice”.
The sharper gap is **freezeable-and-reviewable crate choice**.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — stronger again because it can now age honestly instead of pretending a frozen decision is timeless.
2. **P-0514 Crate Upgrade Pack Kit** — still unusually strong because upgrade pain remains where dependency cost becomes concrete.
3. **P-0515 Crate Off-Ramp Pack Kit** — still strong because leaving a crate cleanly remains a real downstream need.
4. **P-0011 Crate Health Contract Kit** — stronger than before because support posture increasingly changes faster than folk heuristics.
5. **P-0520 Crate Lifecycle Surface Pack Kit** — still unusually strong because shutdown/drain truth remains widely under-served.
6. **P-0522 Crate Persistence Surface Pack Kit** — still strong because durable-state promises remain under-specified.
7. **P-0521 Crate Resource Surface Pack Kit** — still strong because admission and backlog truth stay receiver-facing and testable.

## Why this beat nearby work right now

- It beat another **upgrade-pack** pass because the archive had just invested heavily there and the choice layer was still carrying stale-decision risk.
- It beat another **health** pass because health is a major imported trigger, but the pathfinder still lacked the vocabulary for what to do *after* imported signals change.
- It beat a broader **trust/security** pass because Rust already has stronger trust/security substrate, while teams still lack a compact reviewed answer to “is our frozen starter set still OK?”
- It beat a pure **always-fresh ranking** idea because the right product is not perpetual automatic re-ranking; it is a reviewed decision contract with explicit watch state.

## What changed in the archive

Added:
- `entries/2026-03-20-289.md`
- `meta/frontier-salience-2026-03-20-109.md`
- `meta/crate-ecosystem-pathfinder-product-plan-2026-03-20.md`
- `meta/crate-ecosystem-pathfinder-watch-boundaries-2026-03-20.md`
- `fixtures/crate-ecosystem-pathfinder-kit/revisit-trigger.policy.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/freeze-horizon.policy.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/decision-watch.report.schema.json`
- `fixtures/crate-ecosystem-pathfinder-kit/rustsec_or_malicious_crate_signal_invalidates_frozen_decision/`
- `fixtures/crate-ecosystem-pathfinder-kit/docs_surface_shift_triggers_review_without_forcing_auto_replacement/`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-ecosystem-pathfinder-kit.md`
- `meta/crate-ecosystem-pathfinder-lane-boundaries-2026-03-19.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `fixtures/crate-ecosystem-pathfinder-kit/README.md`
