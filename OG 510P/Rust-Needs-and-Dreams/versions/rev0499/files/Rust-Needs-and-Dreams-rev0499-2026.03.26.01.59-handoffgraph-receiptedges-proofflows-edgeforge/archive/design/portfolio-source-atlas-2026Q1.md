## Addendum (rev0436)
For questions about **which upstream Rust sources should actually anchor a canon claim, what kind of claim each source is fit for, and what caveats should travel with that source instead of living only in maintainer memory**, read this note right after `design/portfolio-evidence-renewal-2026Q1.md`, `design/portfolio-hypothesis-ledger-2026Q1.md`, `design/portfolio-consumer-routing-2026Q1.md`, and `meta/SOURCE_ATLAS_PROTOCOL.md`.

Interpretation rule:
- this note does **not** promote a new seam;
- it does **not** change the broad ladder or the default portfolio order;
- it exists to answer the missing archive-maintenance question: **once the repo has claims, renewal rules, proving grounds, anchors, and a doctor loop, what shared atlas of authority lanes and source caveats should it keep so future revisions stop re-deriving their citation basis ad hoc?**
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep the strongest multi-project answer as **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- keep **Native Edge Contract** as the active specialist frontier;
- and require every serious broad claim to say not only *what sources support it* but *which source family is carrying which part of the argument*.

# Design: Portfolio source atlas and authority lanes (2026 Q1)

## Goal
The archive can now rank seams, specify what they should ship, stage the portfolio, triage additions, score pilots, route consumers, validate a thin shared envelope, keep proving grounds and anchors, renew stale evidence, and maintain a hypothesis ledger for live canon claims.

What it still lacked was one canonical answer to a narrower but increasingly important question:

> once the archive has many repeated claims and many moving upstream sources, where does it record which source families are actually trustworthy for which kinds of claims, what cadence they move on, and what caveats must travel with them?

This note is the archive's answer to a **portfolio source atlas**, not frontier promotion.

Read with:
- `design/portfolio-evidence-renewal-2026Q1.md`
- `design/portfolio-hypothesis-ledger-2026Q1.md`
- `design/portfolio-consumer-routing-2026Q1.md`
- `meta/SOURCE_ATLAS_PROTOCOL.md`
- `meta/EVIDENCE_RENEWAL_PROTOCOL.md`
- `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`

## Why this note is needed now
The repo has crossed a threshold where the next likely failure is not only “ranking the wrong thing.” It is also **source roulette**: one revision leans on a blog post, another on a goals page, another on service docs, and the archive starts sounding stable even when it is mixing different authority lanes without saying so.

Current Rust signals make a source-atlas layer more necessary, not less:
- Rust's March 2026 challenges writeup is excellent for recurring pain, but it is not the same authority lane as a service-behavior doc or a specific goal page.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey is strong evidence for broad pain and learning behavior, but it is still a survey snapshot rather than a command contract or service guarantee.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The January 2026 program-management update and the 2026 flagships page are important for portfolio and funding posture, but they are not the same thing as stable tool/output docs.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo build analysis explicitly allows schema evolution during prototyping, and Cargo's 1.94 cycle is adding `cargo report` and structured-logging surfaces. Those are exactly the kinds of sources that need caveats carried forward instead of being treated as timeless facts.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- docs.rs rustdoc JSON is one of the best substrate sources in the ecosystem, but it explicitly tells consumers to inspect `format_version` and says historical downloads are incomplete.
  https://docs.rs/about/rustdoc-json
- crates.io's January 2026 update and the Trusted Publishing docs are strong for registry/service posture, but they are still separate from Cargo's reference docs on route semantics and publishing behavior.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://crates.io/docs/trusted-publishing
- The Build Dir Layout v2 testing call is a strong “here is what is changing and how to test it” signal, but it is not a stable promise that downstream tools may depend on unspecified internals forever.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The libtest JSON goal captures real demand for programmatic output, but it is still a goal/contract lane, not a stable release note or fully stabilized interface.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html

Taken together, those signals say the archive needed one explicit answer for **which source families support which claim families, with what caveats**.

## Headline answer
A serious archive should maintain a **small shared source atlas** for the upstream sources it repeatedly leans on.

A source-atlas card is not a bibliography entry.
It is a thin maintained note for a source that the archive expects to cite again and again.
Each card should say:
- what the source is;
- what authority lane it belongs to;
- what claim classes it is fit for;
- what caveats must travel with it;
- how quickly it tends to drift;
- what changes would justify re-checking it;
- and which canon assets materially depend on it.

The atlas should therefore help the repo answer three practical questions:
1. **Can I use this source for the claim I am making?**
2. **What caveat should travel with that use?**
3. **When should I prefer a different lane instead of overloading this one source?**

## What this note is for
Use the source-atlas layer when the archive needs to answer which recurring sources should back broad ranking and staging claims, which sources are better for service behavior versus portfolio direction, which machine-usable surfaces still carry schema or freshness caveats, whether a revision is mixing survey, roadmap, and service-contract claims dishonestly, and which sources should be renewed first when an argument feels stale.

Do **not** use it to claim that the archive now has one canonical bibliography for every note, that the checker can prove a citation is true, that one source card replaces evidence renewal, or that a fresh source automatically outranks older but still authoritative sources.

## The source-atlas model
A source-atlas card should stay thin and high-value.
It should name a source the archive expects to cite repeatedly, classify its authority lane, summarize its scope, name the claim classes it is especially useful for, record known caveats and non-uses, and link to canon assets that materially rely on it.

The atlas itself should stay small enough that maintainers and tools can keep it current. It should prefer **reused, high-leverage sources** over exhaustive bibliographic completeness.

A source-atlas card should therefore help the repo keep these distinct:
- **ecosystem pain evidence**;
- **roadmap / goal / funding posture**;
- **tooling-surface and output-contract evidence**;
- **service-behavior evidence**;
- **security / route / registry evidence**.

## The first source atlas
The archive's first shared source atlas should cover at least five authority lanes:
- **official blog** — broad pain, project-wide status, ecosystem incidents, and high-level operational changes;
- **Inside Rust / project-management** — staffing, sequencing, roadmaps, and implementation-season posture;
- **project goals** — bounded work plans, milestone expectations, and active proto-contracts for future surfaces;
- **Cargo / reference docs** — route semantics, command behavior, and current tool contracts;
- **service docs** — docs.rs or crates.io behavior and service-specific caveats.

That atlas should not pretend those lanes are interchangeable. A survey snapshot is not a command contract. A goals page is not a service guarantee. A service “about” page is not a portfolio strategy note.

## Why a source atlas is better than just “more citations”
The archive already cited sources. What it lacked was a place to remember **how to use those sources honestly next time**.

Without a source atlas, future revisions are more likely to:
- overuse one fresh blog post for claims that need a goal page or reference doc;
- miss important service caveats like `format_version`, testing-call posture, or evolving schemas;
- or keep repeating strong conclusions without remembering which source lane was actually doing the evidentiary work.

The source atlas is a smaller answer than a full bibliography and a more durable answer than ad hoc recollection.

## What should be machine-checkable
A shared checker for the atlas should stay thin. It may enforce top-level schema family and revision, unique source IDs, required authority-lane coverage, required claim-class coverage, allowed drift horizons, non-empty caveat and preferred-use fields, and existence of referenced canon assets.

It should **not** try to prove that a source is current or that a claim inferred from it is correct.

## What should happen after the source atlas changes
When the atlas changes materially, the repo should prefer a visible packet:
- update the atlas card or add the new card;
- update the design/protocol if the model changed;
- update the doctor loop if the atlas became a required maintained asset;
- and update routing files if the atlas should now be consulted before future evidence-renewal or hypothesis-ledger edits.

## Default interpretation for future revisions
Until stronger evidence arrives:
- the source atlas is a **deepening + hygiene** layer, not a promotion;
- it strengthens the archive's ability to cite and renew claims honestly over time;
- it should stay small and focused on high-leverage repeated sources;
- and it should resist a common failure mode: using the right source for the wrong kind of claim and only discovering that mistake after the prose already sounds authoritative.
