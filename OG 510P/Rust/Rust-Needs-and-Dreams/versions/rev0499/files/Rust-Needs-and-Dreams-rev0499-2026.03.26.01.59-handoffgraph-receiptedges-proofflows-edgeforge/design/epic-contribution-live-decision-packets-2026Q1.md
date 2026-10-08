# Epic-contribution live decision packets (2026 Q1)

## Why this note exists
The archive now has:
- ranking and shortlist notes,
- macro-program grouping,
- reference architectures,
- launch charters,
- stage gates,
- review-packet rules,
- specimen packets,
- and live candidate dossiers.

What it still lacked was a **current decision-packet corpus** for the actual top band.
Without that layer, the repo can say what the leading candidates are and what their current working posture is, but it still has to reconstruct the actual **decision artifact** a maintainer would read to say “advance”, “deepen”, or “hold” right now.
That creates three avoidable failures:
- a dossier says the candidate is important, but not what the current verdict packet should look like end-to-end;
- a specimen shows packet shape, but not the present-day verdict burden for the real candidate; and
- future revisions can quietly change a leader's posture without leaving behind the packet that justified the change.

A live decision packet is the missing bridge.
It is narrower than a broad note, more decision-ready than a dossier, and more current than a specimen.

## What a live decision packet is
A live decision packet should answer, in one place:
- what the candidate is;
- what verdict the archive is asking for right now;
- what exact current evidence supports that verdict;
- what bounded v0 or next move follows if accepted;
- what proof is still missing;
- what negative states and caveats remain visible;
- who could actually carry the next step;
- what larger form is still refused;
- and what reissue trigger should force the packet to be rewritten.

A live decision packet is therefore:
- more formal than a dossier,
- more current than a specimen,
- and still much smaller than a broad portfolio memo.

Think of it as the archive's **now-decision artifact**.

## Why live decision packets are the right next layer now
Fresh 2026 Rust signals still cluster around a few serious seams rather than around one magical missing framework:
- Cargo build analysis is still prototyping recorded build metadata and `cargo report` subcommands for rebuild reasons and timing history.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo 1.94 is still actively evolving build-dir layout, structured logging, and report commands while also saying Cargo cannot be everything to everyone and explicitly valuing plugins.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The build-dir-layout-v2 testing call still says many tools and processes rely on unspecified build-dir details because Cargo features are missing, and asks people to test real workflows on nightly.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The Cargo Book still centers `cargo metadata`, `--message-format`, and custom subcommands as the narrow integration seams for third-party tools.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- The 2025 State of Rust survey still reports resource usage and debugging as meaningful productivity limits, while documentation remains the canonical learning reference even as LLM-mediated learning rises.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 debugging survey still frames debugger quality as a multi-debugger, multi-OS, visualizer, async, and expression-evaluation problem, and survey results were not yet published when this revision was prepared.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- crates.io has continued adding concrete security and provenance-facing features, including a Security tab, trusted-publishing expansion, and trusted-publishing-only mode.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The March 2026 Cargo advisory still shows that registry and extraction boundaries remain operator-real and route-specific.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The safety-critical writeup still says the ecosystem support thins out quickly beyond prototyping and that tools, evidence recipes, and shared ownership are the bottleneck.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The 2026 goals process still frames goals as front doors for would-be contributors and agreements between proposers, champions, and accepting teams.
  https://rust-lang.github.io/rust-project-goals/2026/

Taken together, those signals say the repo now needs **current packets for current decisions**, not another broad reranking note.

## The packet relation now
The default order is now:
1. **broad note** for territory and ranking;
2. **reference architecture / charter / stage-gate** for theory and shape;
3. **specimen packet** for packet grammar;
4. **dossier** for current working posture;
5. **live decision packet** for the verdict the archive would stand behind now.

Default writing rule:
- start from the nearest dossier;
- borrow grammar from the nearest specimen;
- produce one live decision packet only when the repo wants a current explicit verdict artifact.

## Required fields for live decision packets
Every live decision packet should keep these sections visible:
1. **identity** — candidate, macro-program, packet role;
2. **requested verdict now** — `advance`, `deepen`, `hold`, `merge`, `fold`, or `kill`;
3. **why now** — fresh evidence that still makes this worth deciding now;
4. **practical decision improved** — the user/operator/steward decision that gets better;
5. **bounded next move** — what exactly happens if the verdict is accepted;
6. **earned proof** — what the candidate has already earned;
7. **missing proof / blockers** — what still stops a stronger move;
8. **negative states and caveats** — unsupported tuples, unstable surfaces, freshness burdens, or route gaps;
9. **owner shape / upkeep** — who could actually carry the next move;
10. **refused larger forms** — what premature empire the candidate must not become;
11. **reissue triggers** — what upstream change should force a packet rewrite;
12. **source candor** — what each source lane is and is not proving.

## The first live decision-packet corpus
The initial corpus should cover the same top band already represented by dossiers:
1. **Build-State Evidence** — current `advance`
2. **Feedback / Debug Acceptance Commons** — current `deepen`
3. **Navigation / Defaults / Claims Commons** — current `hold`
4. **Package Intake + Release Boundary Review** — current `advance`
5. **Safety-Critical + Institutional Readiness Commons** — current `deepen`

Why all five belong:
- they carry distinct verdict postures;
- they model distinct owner shapes;
- they expose different proof and upkeep burdens;
- and together they give the repo a stable current-verdict corpus instead of one-shot packet writing.

## What these first packets should teach
### 1) Build-State Evidence
Teach what a live `advance` packet looks like when the seam is narrow, companion-first, and aligned with active upstream substrate work.
The packet should ask for one bounded build/report/diff/doctor family, not a dashboard or daemon empire.

### 2) Feedback / Debug Acceptance Commons
Teach what a live `deepen` packet looks like when the core problem is real but the tuple matrix and results corpus are still incomplete.
The packet should be explicit that survey results are still pending and unsupported tuples remain first-class facts.

### 3) Navigation / Defaults / Claims Commons
Teach what a live `hold` packet looks like when the need is real but the main blocker is renewal burden and review capacity.
The packet should refuse winner-table or portal drift.

### 4) Package Intake + Release Boundary Review
Teach what a live `advance` packet looks like when supply-chain concern is route-real and the first useful answer is a local-first review boundary.
The packet should keep alternate-registry, waiver, quarantine, and operator judgment central.

### 5) Safety-Critical + Institutional Readiness Commons
Teach what a live `deepen` packet looks like when the need is serious but the right next move is still an evidence commons, not certification theater.
The packet should foreground shared ownership, qualification recipes, and bounded target profiles.

## Anti-goals
This layer should refuse:
- becoming another shortlist;
- silently replacing dossiers;
- using specimens as if they were current truth;
- generating live packets for every plausible candidate;
- or treating one live packet as evergreen after upstream evidence changed.

## Default interpretation for future revisions
Until the portfolio changes materially:
- this is a **decision-artifact deepening** move, not a frontier promotion;
- the broad ladder is unchanged;
- dossiers remain the default current-working cards;
- live decision packets are now the default current-verdict artifacts for the top band; and
- future packet-heavy revisions should refresh the nearest live packet before writing another broad memo.
