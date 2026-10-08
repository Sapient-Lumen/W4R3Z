# Epic-contribution candidate dossiers (2026 Q1)

## Why this note exists
The archive now has:
- ranking and shortlist notes,
- macro-program grouping,
- reference architectures,
- launch charters,
- stage gates,
- review-packet rules,
- and a specimen packet corpus.

What it still lacked was a **live working dossier layer** for the actual top-band candidates.
Without that layer, every new revision still has to reconstruct the current posture of the leaders from scattered notes.
That creates three avoidable failures:
- fresh revisions restate the same portfolio posture in slightly different language;
- “current verdict” silently drifts away from the nearest packet specimen; and
- future assistants can describe a worthy contribution in theory but still fail to say what the candidate’s **current operating posture** actually is.

A dossier is the missing bridge.
It is not as broad as a macro-program note and not as formal as a fresh live review packet.
It is a **current working card** for one top candidate.

## What a dossier is
A candidate dossier should answer, in one place:
- what the candidate is;
- why it still belongs in the top band;
- what current verdict posture the archive is carrying (`advance`, `deepen`, `hold`, or stricter);
- what concrete v0 or next packet would make progress real;
- what source families are doing the heavy lifting;
- what proof is still missing;
- what bigger launch shape remains refused;
- and what event would force reissue.

A dossier is therefore narrower than a new synthesis note and more current than a specimen.
Think of it as the archive’s **live packet staging area**.

## Why dossiers are the right next layer now
Fresh 2026 Rust signals still cluster around a few serious seams rather than around one magical missing framework:
- the 2026 goals process explicitly treats a goal as an agreement between owner(s) doing the work and team(s) accepting it, with champions supporting owners over time;
- the 2026 goal slate moved to annual goals so there is more time to discuss and organize real work;
- Cargo build analysis is still prototyping recorded build metadata and `cargo report` surfaces;
- the build-dir-layout-v2 testing call still says downstream tools and processes rely on unspecified details and asks people to test nightly with real workflows;
- Cargo continues to emphasize narrow external-tool seams and still lists plumbing commands, public/private dependencies, and libtest JSON as focus areas without progress in the 1.94 cycle;
- crates.io continues to ship concrete trust and security features while leaving route-specific/operator-specific work unresolved;
- debugging remains a cross-debugger, cross-OS, async, visualizer, and expression-evaluation acceptance problem; and
- the Foundation strategy plus maintenance and safety-critical writeups keep reinforcing maintenance realism, infrastructure investment, and institution-shaped ownership for long-horizon seams.

Sources:
- https://blog.rust-lang.org/inside-rust/2026/02/03/first-look-at-2026-project-goals/
- https://rust-lang.github.io/rust-project-goals/2026/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rustfoundation.org/strategic-plan/
- https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

Taken together, those signals say the repo now needs a **live top-band dossier corpus**, not another broad ladder rewrite.

## What dossiers should contain
Every dossier should keep the following fields visible:
- identity and macro-program;
- current archive posture;
- why the candidate is still load-bearing now;
- what exact v0 / packet / proving-ground move is next;
- current proof already earned;
- missing proof that still blocks a stronger verdict;
- owner shape and maintenance reality;
- refused larger forms;
- reissue triggers;
- source-candor notes.

The emphasis should be on **current operability**, not on rhetorical completeness.

## The first dossier corpus
The initial dossier set should cover the same top band the archive already keeps returning to:
1. **Build-State Evidence**
2. **Feedback / Debug Acceptance Commons**
3. **Navigation / Defaults / Claims Commons**
4. **Package Intake + Release Boundary Review**
5. **Safety-Critical + Institutional Readiness Commons**

Why these five:
- they span the strongest current macro-programs;
- they represent distinct verdict postures and owner shapes;
- they cover the seams where current public Rust signals are most actionable;
- and they are enough to keep future revisions from reconstructing the top band from scratch.

## What each dossier should teach
### 1) Build-State Evidence
Teach what an `advance` candidate looks like when the kernel is narrow, the external seam is real, and upstream substrate motion is clearly aligned.
The dossier should point toward one bounded local-first build/report/diff/doctor family and keep unstable-surface caveats explicit.

### 2) Feedback / Debug Acceptance Commons
Teach what a `deepen` candidate looks like when the kernel is right but the tuple matrix and results corpus are still incomplete.
The dossier should stay strict about unsupported tuples and missing survey-results synthesis.

### 3) Navigation / Defaults / Claims Commons
Teach what a `hold` candidate looks like when the problem is real but the archive’s renewal budget is the main blocker.
The dossier should keep freshness, review capacity, and anti-portal rules explicit.

### 4) Package Intake + Release Boundary Review
Teach what an operator-shaped `advance` candidate looks like when incident reality and service behavior justify a narrow build now.
The dossier should keep alternate-registry caveats, local judgment, and waiver/quarantine receipts central.

### 5) Safety-Critical + Institutional Readiness Commons
Teach what a strict stewarded seam looks like when the path is real, but higher-assurance adoption still needs evidence recipes, shared ownership, and long-horizon maintenance.
The dossier should bias toward `deepen`, not because the seam is weak, but because the maintenance and qualification burden is real.

## Dossiers versus specimens versus packets
- **Specimens** teach packet shape.
- **Dossiers** teach current posture for real top candidates.
- **Live packets** are revision-time decision artifacts.

Default relation:
- start from the nearest dossier;
- borrow shape and candor rules from the nearest specimen;
- only then write or refresh a live packet.

## Anti-goals
The dossier layer should refuse:
- becoming a second broad shortlist;
- silently reranking the portfolio without touching the routing layer;
- copying specimen verdicts without fresh evidence;
- or turning into a registry of every plausible candidate.

## Default interpretation for future revisions
Until the portfolio changes materially:
- this is a **deepening + operating-canon** move, not a frontier promotion;
- dossiers are now the default place to look for the top band’s current posture;
- future revisions should update an existing dossier before inventing another broad synthesis note;
- and any serious packet-writing pass should say which dossier it used as the live starting point.
