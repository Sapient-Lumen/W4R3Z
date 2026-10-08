# Design: Epic contribution review packets 2026Q1

## Goal
The archive already has a broad ladder, practical build briefs, macro-programs, reference architectures, launch charters, and stage gates.
What it still lacked was one compact answer to a practical editorial question:

> when a top Rust ecosystem program comes up for comparison, deepening, advancement, merge, or pruning, what packet should reviewers actually read so the decision is about the same things every time?

This note exists to make the repo better at **comparison, advancement, and elimination without drift**.
It is the archive's answer to:
- what a serious proposal must include before it can be compared honestly,
- what should be visible when a program is advanced, folded, delayed, or killed,
- how theory and practice should stay in the same review frame,
- and how the strongest Rust ecosystem contributions can be judged without re-litigating their shape every revision.

Read with:
- `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/epic-contribution-program-stack-2026Q1.md`
- `design/practical-epic-contribution-briefs-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `meta/PROGRAM_STAGE_GATE_PROTOCOL.md`
- `meta/PROGRAM_CHARTER_PROTOCOL.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Why this note is needed now
The current Rust picture still points to a handful of serious ecosystem programs rather than one missing universal framework.
But the repo is now large enough that a different problem dominates: future revisions can compare, reorder, or widen the top programs using different implicit criteria every time.
That makes the archive feel rich while still being hard to operate.

Recent official signals sharpen that problem:
- The March 2026 challenges writeup clusters pain around compilation/resource friction, crate choice and tacit knowledge, async complexity, embedded constraints, and safety-critical maturity. That is a portfolio picture, not a one-tool picture.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey still reports resource usage and debugging as meaningful productivity limits, while documentation remains canonical even as editor/LLM-mediated learning rises. That makes reviewable packets more important than prose-only synthesis.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The debugging survey explicitly frames debugger quality as a tuple problem across debuggers, operating systems, async support, visualizers, and Rust-expression evaluation. That means a review packet has to show accepted, partial, and unsupported states rather than a single anecdotal success.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo's build-analysis goal, build-dir-layout work, and external-tools posture reinforce that machine-readable packs, JSON surfaces, and companion tools are the realistic review substrate for many worthy contributions.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- The Cargo 1.94 development-cycle post again emphasizes plugins, structured logging, and build-dir work while explicitly saying Cargo cannot be everything to everyone. That argues for portable review packets and narrow upstream asks rather than platform fantasies.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The March 2026 build-dir-layout-v2 testing call shows how many tools still depend on unspecified internals. That is exactly the kind of environment where broad claims need packetized negative states and migration receipts.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The 2026 flagships keep SBOM support, public/private dependencies, and safety-critical tooling in the center. The safety-critical writeup keeps stressing shared ownership, evidence, and maintenance. Those are packet-heavy program seams.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The March 2026 Cargo advisory and the crates.io malicious-crate notification update both reinforce that supply-chain and intake work is review-heavy, route-heavy, and local-first. That is another reason to require comparable review packets before widening package-intake claims.
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/

Taken together, those signals say the next missing repo layer is not another top-ten note.
It is a **standard review packet**.

## Headline answer
Every top-band Rust ecosystem program should be comparable through one bounded packet before the archive does any of the following:
- advances it,
- widens it,
- merges it into a stronger parent,
- gives it a new steward story,
- or kills it.

That packet should carry one honest slice of both **theory** and **practice**:
- what problem shape the program claims to solve,
- what artifact family it actually ships,
- what proof it has earned,
- what owner and maintenance burden it assumes,
- what exact decision gets better,
- what adjacent options it beats, loses to, or should fold into,
- and what larger launch form is still premature.

The missing discipline is this:

> do not compare worthy programs by summaries when their evidence, stage, owner shape, and refusal clauses live in different places.

## What a review packet is
A review packet is not a product brochure and not a giant dossier.
It is the smallest bounded bundle that lets a reviewer decide one of the verbs that matter:
**advance, deepen, merge, hold, fold, or kill**.

The default packet should have two layers:
1. **one review brief** — a tight human-readable summary of the current candidate and the decision requested;
2. **one annex bundle** — links or attachments for proof assets, proving-ground results, scorecards, receipts, and adjacent comparisons.

The brief should be readable in one sitting.
The annex exists so the brief does not become vibes-only.

## The standard packet spine
Every serious packet should answer the same ten questions.

### 1) Identity and scope
- What is the candidate called in this packet?
- Which macro-program or seam does it belong to?
- Is this packet about a program, a kernel, a pilot, a packet family, a charter, or a fold/kill decision?
- What is explicitly out of scope?

### 2) Why now
- What current Rust signals make this worth reviewing now?
- Which pain is recurring and broad, and which pain is narrow but urgent?
- What freshness anchors justify this review?

### 3) Kernel and artifact family
- What is the minimum real thing being proposed?
- What artifact family or file family would actually ship first?
- What imports does it rely on?

### 4) Stage and proof status
- What stage is the candidate in now?
- What proof budget has it earned?
- What proof is missing?
- What next gate would justify widening?

### 5) Practical decision improved
- Which concrete developer/operator/steward decision gets better if this exists?
- What before/after difference is expected?
- What residue stays manual?

### 6) Proving grounds and negative states
- Which tuple, lane, or proving grounds were used?
- What is accepted, partial, unsupported, or regressed?
- What known contradictions remain?

### 7) Owner shape and maintenance envelope
- Who owns this first?
- What cadence of upkeep does it assume?
- What human review remains irreducible?

### 8) Comparison and adjacency
- What neighboring candidate did this beat, narrow, merge with, or lose to?
- Why is this not better folded into a stronger parent?
- What tempting larger build is still refused?

### 9) Bounded v0 and requested verdict
- What is the actual v0?
- What exact verdict is requested now: advance, deepen, merge, hold, fold, or kill?
- What narrower next step follows if approved?

### 10) Refresh and expiry
- What evidence expires?
- What renewal cadence applies?
- Under what condition should the packet be reissued rather than reused?

## The six review verdicts
The packet exists so the archive can use a shared verdict vocabulary.

### Advance
Use when the candidate has earned its next gate and the next widening is still bounded.

### Deepen
Use when the broad idea is right but the kernel, proof assets, or proving-ground story are still thin.

### Merge
Use when the candidate is real but is better treated as a component, lane, or packet inside a stronger parent program.

### Hold
Use when the idea remains plausible but the current evidence or maintenance posture is not yet sufficient for movement.

### Fold
Use when the candidate has no independent first life and should be routed under a stronger sibling or parent.

### Kill
Use when the candidate's current shape is misleading, over-claiming, or maintenance-incoherent enough that the repo should stop carrying it as an active answer.

## What a good packet should look like for the top macro-programs

### 1) Evidence Spine / Build-State Evidence
The packet should center on:
- imported machine-readable build facts;
- one or two real decision improvements such as rebuild explanation, cache contention explanation, or CI/local comparison;
- adapter-lossiness and unstable-surface warnings;
- a refused launch form such as dashboard empire, build daemon, or hosted control plane.

A bad packet here sounds broad but cannot show the pack format, the diff/doctor path, or the proving grounds.

### 2) Feedback / Debug Acceptance Commons
The packet should center on:
- the debugger tuple matrix;
- async-debug posture;
- visualizer or expression-evaluation acceptance state;
- exportable session/support pack shape;
- unsupported and regressed states that remain visible.

A bad packet here says “debugging is painful” and maybe names tools, but does not carry a tuple table or show what practical support/export decision improved.

### 3) Navigation / Defaults / Claims Commons
The packet should center on:
- the bounded audience and lane;
- source freshness and renewal burden;
- the exact claim grammar being made;
- what evidence lane cards import;
- anti-winner-table refusal.

A bad packet here offers recommendations without renewal receipts or without saying what recommendation authority it is explicitly *not* claiming.

### 4) Package Intake + Release Boundary Review
The packet should center on:
- local-first intake or release-boundary operation;
- route truth, extraction/replay, quarantine, waiver, and escalation receipts;
- concrete incident or drill context;
- explicit operator/manual ownership;
- the difference between helpful local review and broader policy posture.

A bad packet here turns current supply-chain anxiety into a generic ecosystem policy pitch without proving a local review boundary first.

### 5) Safety-Critical + Institutional Readiness Commons
The packet should center on:
- qualified scope and target/runtime profile;
- evidence recipe or checklist family;
- required shared ownership;
- long-horizon maintenance and standards boundaries;
- narrow upstream asks rather than certification theater.

A bad packet here mistakes institutional importance for shipped evidence assets.

## Packet-level ranking discipline
The broad ranking still stands:
1. Evidence Spine / Build-State Evidence
2. Feedback / Debug Acceptance Commons
3. Navigation / Defaults / Claims Commons
4. Tooling Contract / Shared Spine / Semantic Context as thin multipliers
5. Package Intake + Release Boundary Review
6. Compatibility Claims
7. Safety-Critical + Institutional Readiness Commons

But packet discipline changes how the repo should act on that ranking:
- a lower-ranked candidate with a stronger packet may deserve deepening before a higher-ranked candidate with fuzzy comparison state;
- a high-ranked candidate without a real packet is still not ready for a widening story;
- and a merged or folded verdict can be a success if the packet proves the value survives under a stronger parent.

## What to refuse
A review packet should refuse the following archive failure modes:
- ranking by rhetorical force;
- widening by adjacency rather than proof;
- calling a proposal practical without owner and maintenance posture;
- comparing pilots, kernels, and macro-programs as if they are the same unit;
- reusing stale survey/blog/goal signals without visible freshness anchors;
- and treating one polished demo or portal mockup as stronger than a dull packet with real receipts.

## Repo implications
From this revision onward, the repo should prefer:
- one good packet over three overlapping summaries;
- explicit verdict requests over vague “further exploration” language;
- fold/kill clarity over archive accretion;
- and packet reissue after material drift rather than quiet carry-forward of an old comparison.

That is the practical upgrade:
not another answer to **what matters**,
but a shared answer to **what reviewers must see before the repo changes its mind**.
