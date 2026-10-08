## Addendum (rev0495)
For questions about **which present-tense strategic claims this archive is currently leaning on**, **what would narrow or break them**, **which broad claims are still alive after another live online refresh**, or **what evidence should force a visible downgrade instead of another smooth restatement**, read this note immediately after:
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- `design/epic-contribution-hot-substrate-watchcards-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`
- `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`

Interpretation rule:
- this note does **not** rerank the broad ladder;
- it does **not** promote a new frontier;
- it exists to answer the now-missing execution question: **once the repo has rankings, packets, stewardship maps, watchcards, and operating rails, where does it keep the strongest present-tense claims as explicit claims with downgrade triggers and falsifiers instead of house style?**
- keep **Build-State Evidence** as the strongest one-project answer overall unless the ledger says otherwise;
- keep **Package Intake + Release Boundary Review** as the strongest urgent operator-facing pair;
- keep **Feedback / Debug Acceptance Commons** and **Safety-Critical + Institutional Readiness Commons** as deepen lanes rather than fresh empire-building excuses;
- and require every repeated strategic claim to say what still supports it, what would narrow it, what would falsify it, and what repo layers should move if it changes.

# Design: Portfolio hypothesis ledger and falsifier gates (2026 Q1)

## Goal
The archive can already rank strong seams, specify execution blueprints, stage gates, packets, kernel briefs, operating surfaces, stewardship homes, control loops, and hot-substrate watchcards.

What it still lacked as a *current canon layer* was one explicit answer to this narrower question:

> once a broad strategic conclusion has been repeated across the repo, where does the archive name that conclusion as a falsifiable present-tense claim instead of letting it float forever as tone?

This note is the archive's answer to **portfolio hypothesis ledger and falsifier gates**, not a new seam.

Read with:
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-portfolio-control-loop-2026Q1.md`
- `design/epic-contribution-hot-substrate-watchcards-2026Q1.md`
- `design/epic-contribution-operating-surface-2026Q1.md`
- `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md`
- `meta/HYPOTHESIS_LEDGER_PROTOCOL.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/PORTFOLIO_CONTROL_LOOP_PROTOCOL.md`
- `ledgers/portfolio-hypothesis-ledger-v0/hypotheses.json`

## Why this note is needed now
The repo is now good enough at synthesis that a different failure mode matters more: a claim can become “canon” by repetition after the conditions that made it reasonable have already shifted.

Current official Rust signals make a hypothesis-ledger layer more necessary, not less:
- The March 2026 challenges post says compilation performance remains a broad tax, ecosystem navigation is still too tacit-knowledge-heavy, and some pains are highly domain-shaped rather than one universal missing framework.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says documentation remains the dominant canonical learning source even as editor- and LLM-mediated learning rises, and it still surfaces resource usage and debugging among the ecosystem's practical pain points.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo build analysis is still explicitly a prototype around recorded metadata, unstable `cargo report` surfaces, and evolvable stored structure rather than a finished stable review layer.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The Build Dir Layout v2 testing call says many tools still rely on unspecified internals and that even wide testing will not cover everything.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- crates.io development and Project Director updates keep turning security, trusted publishing, vulnerability surfacing, and capability analysis into more concrete service/operator truth without making a full package-intake review product appear by magic.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/
- docs.rs rustdoc JSON and libtest JSON both show why machine-readable surfaces matter while also warning that versioning, toolchain, and compatibility caveats must travel with them.
  https://docs.rs/about/rustdoc-json
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- The safety-critical writeup, FLS adoption, and Foundation strategy keep reinforcing that some of Rust's highest-value missing contributions are commons/program work whose real bottleneck is durable stewardship, qualification discipline, and evidence renewal.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  https://blog.rust-lang.org/2025/03/26/adopting-the-fls/
  https://rustfoundation.org/strategic-plan/
- The Vision Doc lessons post is still a strong warning that broad research is useful but not a license to collapse interviews, surveys, and current implementation details into one timeless answer.
  https://blog.rust-lang.org/2025/12/03/lessons-learned-from-the-rust-vision-doc-process/

Taken together, those signals say the archive needed a **thin explicit ledger of strong present-tense claims** beneath its rankings, control loops, and watchcards.

## Headline answer
A serious worthy-contributions repo should maintain a **small named hypothesis ledger** for the strategic claims it actually keeps leaning on.
It is not a prediction market and not a KPI dashboard.
It exists for a narrower question:

> which present-tense claims are strong enough that the archive keeps reusing them, what still supports them, what would narrow them, and what evidence would make the archive stop saying them in their current form?

The ledger should therefore:
1. name a small set of high-leverage claims;
2. classify each claim so readers know what kind of statement it is;
3. say what still supports it;
4. state downgrade triggers and stronger falsifiers explicitly;
5. say which control-loop layers should move if the claim changes; and
6. keep claim truth separate from watchcards, packets, charters, and seam-local artifact semantics.

## What this note is for
Use the hypothesis-ledger layer when the archive needs to answer:
- which repeated strategic conclusions are currently *live*;
- which fresh upstream or service movement should merely narrow a claim versus actually break it;
- whether a revision should say **confirmed**, **narrowed**, **degraded**, **superseded**, or **retired**;
- and which broad portfolio statements are now important enough that future revisions must stop paraphrasing them loosely.

Do **not** use it to claim that:
- every seam-local statement belongs in the shared ledger;
- one ledger card replaces evidence renewal, packet review, or watchcards;
- the checker can settle a strategic argument automatically; or
- the archive should become a prediction-market repo.

## The hypothesis-ledger model
A hypothesis card is a named present-tense claim the archive relies on.
It should say:
- what class of claim it is;
- what the claim currently states;
- what sources and neighboring assets support it;
- what leading indicators keep it plausible;
- what downgrade triggers should narrow it;
- what stronger falsifiers should break it;
- what review horizon it belongs on; and
- what control-loop layers should move when it changes.

The ledger is the maintained set of those cards.
It should stay small enough that reviewers can remember it and tools can validate it.
The first ledger should prefer **high-leverage canon claims** over a giant theory dump.

A card should use explicit state such as `active`, `narrowed`, `degraded`, `superseded`, or `retired`.
A downgrade trigger is weaker than a falsifier: a downgrade trigger says the claim is still directionally plausible but should now be stated more narrowly; a falsifier says the archive should stop saying the claim in its current form.

## The first current ledger
The current archive should keep at least these recurring claim classes explicit:
- **one-project ranking** — what still deserves to lead if the repo must recommend one serious build;
- **multi-project ranking** — what family answer still beats a one-platform fantasy;
- **frontier posture** — what should and should not count as frontier-shifting movement;
- **anti-tacit-knowledge** — what the archive really means by navigation/defaults without slipping into portalism;
- **staging claim** — what must come before broader atlas or policy surfaces;
- **portfolio hygiene** — what level of artifact the next fresh signal honestly belongs to;
- **proof discipline** — what caveats must travel with machine-readable or service-side truth; and
- optionally, **commons-program priority** claims when the repo keeps leaning on stewardship-heavy seams like safety readiness.

## Why a hypothesis ledger is better than another prose memo
The archive already had ranking notes, renewal rules, watchcards, packets, scorecards, and doctor loops.
None of those alone says:
**which broad claims are still alive, what would narrow them, and what evidence would make the archive stop repeating them?**
That is the gap this layer fills.

## What should be machine-checkable
The checker for the ledger should stay thin.
It may enforce:
- top-level schema family and revision;
- required claim-class coverage;
- unique hypothesis IDs;
- required fields and allowed status values;
- allowed control-loop references;
- non-empty support / downgrade / falsifier fields; and
- existence of related canon assets.

It should **not** attempt to prove the strategic claim true.

## What should happen after a hypothesis changes
When a live hypothesis changes materially, the repo should prefer a visible packet:
1. update the hypothesis card;
2. update the design/ranking/control-loop notes that depend on it;
3. refresh the nearest watchcard, packet, stewardship note, or canon file named by the card's affected loops;
4. record the change in `RESEARCH_LOG.md` and `meta/LATEST_REVISION_FILESET.md`; and
5. say whether the claim was confirmed, narrowed, degraded, superseded, or retired.

## Default interpretation for future revisions
Until stronger evidence arrives:
- the hypothesis ledger is a **current-canon + hygiene** layer, not a promotion;
- it strengthens the archive's ability to compare itself against reality over time;
- it should stay small and focused on claims that repeatedly shape funding, staffing, ranking, sequencing, or maintenance answers; and
- it should resist a common failure mode: repeating a good conclusion after the conditions that made it good have already shifted.
