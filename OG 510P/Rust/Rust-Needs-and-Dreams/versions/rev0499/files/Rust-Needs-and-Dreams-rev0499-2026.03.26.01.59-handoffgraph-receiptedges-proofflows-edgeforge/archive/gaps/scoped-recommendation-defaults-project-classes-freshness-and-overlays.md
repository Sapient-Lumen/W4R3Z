# Gap: scoped recommendation defaults for recurring Rust project classes

## What is missing
Rust still lacks a **portable layer for reusable scoped defaults**.

The ecosystem now has many pieces of guidance, but they live at different levels:
- crates.io and docs.rs expose candidate crates and canonical docs;
- curators and internal teams produce lane maps or shortlists;
- project-specific adoption briefs answer one concrete question;
- starter repos and platform overlays turn some of those answers into working trees;
- assistants increasingly summarize all of the above from memory.

What is missing is the thin layer in the middle:
> for this recurring project class, with this runtime family, risk posture, team maturity, and environment posture, what reusable default Rust lane are we prepared to recommend right now — with alternatives, freshness, and escalation rules still visible?

## Why this matters now
Fresh official signals all point at the same seam:
- Rust’s March 20, 2026 challenges post says ecosystem choice still depends too much on **tacit knowledge** and **choice paralysis**, and that the problem is often not library absence but difficulty choosing the right lane.
- Rust’s December 2025 vision work says users still need help getting oriented in crates.io and finding a good “starter set” of crates, but also makes clear that broad blessing is politically risky.
- The 2025 State of Rust survey says online docs remain canonical while learning and editor behavior are increasingly machine-mediated.
- crates.io’s January 2026 update added `pubtime`, SLOC, and a docs.rs source link, which makes refresh and review inputs more machine-usable.
- Cargo’s February 2026 development-cycle note says Cargo cannot be everything to everyone and explicitly celebrates plugins.
- The Rust Foundation’s 2026–2028 strategy couples stable infrastructure, sustainable maintenance, and adoption growth, which means recommendation infrastructure now belongs inside core ecosystem thinking.

Together those signals say the next missing contribution is not a universal “best crates” page.
It is a **reviewable scoped-defaults layer**.

## The current seam is awkward
Today Rust guidance often jumps directly between three unstable states:
1. **candidate-space only** — respectable lanes are listed, but nobody says which reusable default applies here;
2. **project-specific brief** — one good answer exists, but it is too narrow to reuse;
3. **accidental blessing** — one answer gets repeated until it starts pretending to be universal.

That leads to familiar failures:
- teams recompute the same recommendation for the same project class over and over;
- starter templates or example repos silently become de facto defaults without a freshness budget;
- assistants repeat yesterday’s advice as if it were today’s public default;
- public guidance and local policy overlays blur together;
- one high-status recommendation starts laundering itself into ecosystem truth.

## What truths need to stay distinct
A worthy contribution here should keep these truths separate:

1. **candidate space**
   - what serious lanes exist for this domain and slot map;
   - what the archive or curator sees as viable candidates.

2. **reusable scoped default**
   - the default lane for a recurring project class;
   - the assumptions about runtime, risk, support horizon, team maturity, and environment posture;
   - the freshness budget and override threshold.

3. **project-specific override**
   - what changed for one concrete project;
   - why the reusable default still fits or no longer fits.

4. **first-route handoff**
   - what a learner/team should read or build first if the reusable default applies.

5. **local institutional overlay**
   - what an organization, product family, or regulated context adds or narrows locally.

6. **neutral common ground**
   - what is a shared seam across lanes rather than a recommendation default.

If those truths do not stay distinct, the ecosystem keeps oscillating between paralysis and stealth blessing.

## What “good” looks like
A serious contribution here is **not** another ranking engine or “top crates” catalog.
It is a shared artifact family such as:
- `lane-default-scope/v0`
- `lane-default-card/v0`
- `lane-slot-defaults/v0`
- `lane-default-evidence/v0`
- `lane-default-freshness/v0`
- `lane-default-handoff/v0`
- `lane-default-pack/v0`
- optional `lane-default-diff/v0`
- optional `lane-default-override-report/v0`

That would let Rust answer questions like:
- what is the reusable default for a conservative internal CLI lane right now?
- what does that default assume about runtime, team maturity, and support horizon?
- what serious alternatives remain first-class?
- when should a team escalate to a project-specific adoption brief?
- what may Profiled Onramp, Project Bootstrap, or an assistant safely import from this default?
- what changed since the previous default revision?

## Why this belongs in the archive now
The archive already has much of the substrate:
- Ecosystem Atlas for candidate space;
- Adoption Navigation and Adoption Decision for project-scoped recommendations;
- Recommendation Posture Ladder for authority boundaries;
- Canonical Learning for canon;
- Institutional Overlay for local policy;
- Profiled Onramp and Project Bootstrap for downstream starter paths.

What it still lacks is the explicit statement that **reusable scoped defaults** are their own worthy control-plane contribution.
That is the missing move between “many possible lanes” and “one team-specific answer.”

## References (signals)
- Rust challenges, March 20 2026:
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- What do people love about Rust?, December 19 2025:
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- 2025 State of Rust survey, March 2 2026:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io development update, January 21 2026:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo 1.94 development-cycle note, February 18 2026:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Rust Foundation strategic plan 2026–2028:
  https://rustfoundation.org/strategic-plan/
