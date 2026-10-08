# Design: Epic contribution review-packet specimens 2026Q1

## Goal
The archive now has a review-packet note, but it still lacked a smaller practical answer to a new question:

> once the repo knows what a good packet should contain, what tiny set of **filled-out specimen packets** should it keep so future revisions stop re-inventing packet shape, verdict posture, and evidence candor from scratch?

This note exists to make the repo better at **theory-to-practice translation**.
It is the archive's answer to:
- what a *real* top-program packet should look like once the fields are actually populated;
- how verdict language should behave when the candidate is strong but not equally mature;
- how current Rust signals change packet posture in practice;
- and what archive hygiene is needed so future LLM-assisted revisions do not drift into summary theater.

Read with:
- `design/epic-contribution-review-packets-2026Q1.md`
- `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/practical-epic-contribution-briefs-2026Q1.md`
- `meta/PROGRAM_REVIEW_PACKET_PROTOCOL.md`
- `meta/REVIEW_PACKET_SPECIMEN_PROTOCOL.md`
- `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- `specimens/review-packets-v0/README.md`

## Why this note is needed now
The repo is now good enough at packet theory that the next failure mode is obvious: a future revision can say it followed the packet protocol while still quietly changing packet shape, verdict burden, or evidence candor from one revision to the next.
A tiny specimen corpus solves that better than another broad synthesis note.

Current Rust signals make specimen packets timely:
- The March 2026 challenges writeup still clusters pain around compilation/resource friction, async complexity, crate choice/trust, embedded constraints, safety-critical maturity, and GUI compile-loop pain. That means the strongest candidates are still portfolio-shaped and should be compared through concrete packets rather than new ranking prose.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The same post now also carries an author's note explaining that its original draft was retracted because of discomfort with LLM-speak and lack of felt substance. That is a direct archive lesson: broad synthesis must keep provenance, caveats, and evidentiary modesty visible rather than hiding them behind polished language.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey still reports resource usage and debugging as meaningful productivity limits, while online documentation remains the canonical reference even as editor and LLM-mediated learning rise. That is another reason to keep packet specimens tight, source-aware, and import-explicit.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo build-analysis work is still explicitly prototyping `cargo report`-style subcommands, rebuild-reason recording, timing history, and schema evolution without promising a stable data format yet. A specimen packet can show how to carry that instability honestly.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo's build-dir-layout work still frames fine-grained locking, reduced contention with Rust Analyzer, and user-wide/shared cache goals as active substrate work, not finished guarantees.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The Cargo 1.94 cycle says Cargo cannot be everything to everyone, celebrates plugins, and still lists public/private dependencies, plumbing commands, and libtest JSON among focus areas without progress. That argues for companion-first packets and conservative requested verdicts.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The debugging survey still frames debugging as a cross-debugger, cross-OS, async, visualizer, and expression-evaluation problem. That means the honest packet verdict there is not the same as the honest packet verdict for build evidence.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io's January 2026 update and the March 2026 Cargo advisory show that package-intake/security work is increasingly concrete — security tabs, trusted publishing enhancements, publication timestamps, mitigation rollout on crates.io, and alternate-registry caveats — but still boundary- and operator-shaped rather than solved by one crate.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The 2026 flagships keep supply-chain, building-blocks, and safety-critical work in the strategic core, while the safety-critical writeup stresses that higher-criticality teams often internalize or abstract over third-party dependencies and need shared-ownership evidence programs rather than one-off tools.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The maintenance writeup reinforces that real upkeep is invisible, multiplicative work; packet owner shape therefore has to be realistic, not decorative.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

Taken together, those signals say the repo now needs a **packet-specimen layer with provenance guards**.

## Headline answer
The archive should maintain a **small review-packet specimen corpus** for the strongest and most distinct verdict postures.
That corpus should not try to cover every seam.
It should instead teach four things clearly:
1. what an `advance` packet looks like when the candidate has a strong kernel and current upstream tailwinds;
2. what a `deepen` packet looks like when the candidate is strategically important but the proof surface is still incomplete;
3. what a `hold` packet looks like when the candidate matters but should widen slower than people want;
4. what a second `advance`, but boundary/operator-shaped, packet looks like when security and route reality are doing most of the justificatory work.

The first specimen set should therefore cover:
- **Build-State Evidence** — `advance`
- **Feedback / Debug Acceptance Commons** — `deepen`
- **Navigation / Defaults / Claims Commons** — `hold`
- **Package Intake + Release Boundary Review** — `advance`

Those four specimens are enough to keep future revisions honest without turning the corpus into a registry of every top-band seam.

## What packet specimens are for
Packet specimens are not live verdicts.
They are **reference examples of packet shape, evidence candor, and requested-verdict posture**.
Use them when the archive needs help answering:
- how much evidence is enough for `advance` versus only `deepen`;
- how to keep unstable upstream work visible without collapsing into vagueness;
- how to separate imported evidence from archive inference;
- how to keep negative states visible in a packet that is otherwise optimistic;
- and how to stop future LLM-assisted revisions from smoothing over caveats.

Do **not** use packet specimens as a substitute for the current revision's own packet, verdict, or fresh research.

## The first specimen set

### 1) Build-State Evidence — `advance`
This specimen should teach the strongest current posture in the repo.
Why `advance` is justified here:
- Cargo build analysis is explicitly trying to record rebuild reasons, timing data, CLI arguments, and an evolvable data store.
- Build-dir-layout work is explicitly motivated by reduced lock contention, GC, and shared-cache futures.
- Cargo's external-tools surface already offers `cargo metadata`, JSON messages, and custom subcommands as the narrow companion seam.
- The requested widening is still bounded: a local-first report/pack family, not a service or daemon empire.

The specimen should therefore model a packet that:
- asks for stage movement only into a bounded companion-first v0;
- keeps unstable-format caveats visible;
- names real proving grounds such as shared workspaces, CI/local comparisons, and Cargo/Rust-Analyzer contention;
- and refuses hosted-control-plane fantasies.

### 2) Feedback / Debug Acceptance Commons — `deepen`
This specimen should teach restraint.
Why `deepen` is the honest verdict here:
- debugging is clearly painful enough to remain strategically important;
- the capability bar is explicit (multi-debugger, multi-OS, visualizers, async, Rust expression evaluation);
- but as of March 23, 2026 the public survey-launch post promises that results will be evaluated and published later, and there is not yet a public survey-results packet to import.

The specimen should therefore model a packet that:
- treats the kernel as tuple records, acceptance fixtures, and exportable session packs rather than one debugger fork;
- names the missing proof directly;
- asks for more matrix truth before broader advancement;
- and refuses any packet that claims the area is already coherent just because one debugger or operating system improved.

### 3) Navigation / Defaults / Claims Commons — `hold`
This specimen should teach anti-portal discipline.
Why `hold` is the honest verdict here:
- the crate-choice and tacit-knowledge problem remains real and current;
- docs remain canonical even as LLM/editor mediation rises;
- but recommendation layers are high-renewal, easy to overstate, and easy to turn into winner-table theater.

The specimen should therefore model a packet that:
- treats the candidate as lane cards + evidence imports + renewal receipts;
- says explicitly that packet quality is bounded by source freshness and review capacity;
- keeps claim authority narrow;
- and refuses broad ecosystem portal, score, or best-crate league-table forms.

### 4) Package Intake + Release Boundary Review — `advance`
This specimen should teach operator realism.
Why `advance` is justified here:
- crates.io has shipped concrete security-facing surface changes: security tab, trusted-publishing-only mode, blocked triggers, and publication-time data;
- Cargo is still directly exposed to package extraction risk, as the March 2026 advisory shows;
- alternate registries remain a separate exposure lane.

The specimen should therefore model a packet that:
- centers on local-first route review, quarantine, waiver, replay, and release-boundary receipts;
- treats crates.io posture as informative but not universal;
- keeps alternate-registry caveats visible;
- and refuses vague “secure the ecosystem” platform stories.

## Specimen rules the repo should preserve
Each specimen packet should visibly separate:
- imported evidence,
- archive inference,
- current proof,
- missing proof,
- requested verdict,
- and larger launch forms still refused.

Each specimen packet should also carry a short **source-candor note** saying whether a cited source is:
- operational/contractual,
- roadmap/prototype-directional,
- survey or synthesis framing,
- or governance/support-lane realism.

That matters because some of the strongest current sources are intentionally not equal in epistemic weight.
A Cargo Book page, a project-goal page, a survey launch, a safety-critical interview synthesis, and a retracted-then-reposted challenges writeup should not be used as if they are all the same kind of evidence.

## What packet specimens should refuse
The specimen layer should explicitly refuse:
- treating a specimen as a live verdict;
- copying specimen rhetoric without re-checking freshness;
- converting a source-candor note into a hidden internal assumption;
- using the challenges writeup as quote-grade proof for exact prevalence claims after its retraction note about scope and evidence presentation;
- letting LLM polish erase caveats, retractions, unstable-format warnings, or unsupported tuple states;
- and widening the specimen corpus whenever the real need is just to deepen one existing packet.

## Default interpretation for future revisions
Until the portfolio posture changes materially:
- the packet-specimen layer is **deepening + hygiene**, not a frontier promotion;
- it makes the current top-band portfolio easier to operate and compare;
- it strengthens the repo's ability to keep packet verdicts stable across future LLM-assisted revisions;
- and it gives future contributors a concrete way to deepen strong programs without inventing fresh packet grammar every time.
