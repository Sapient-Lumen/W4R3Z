## Execution addendum (rev0426)
For questions about **whether a newly attractive idea deserves top-band treatment at all**, read `design/portfolio-selection-rubric-2026Q1.md` immediately after this note.

Interpretation rule:
- the broad territory map is unchanged;
- the new note owns proposal selection, foldability, and kill criteria;
- this note still owns the broad ranking split among one-project winner, specialist frontier, hidden multiplier, and folding/elimination decisions;
- and a fresh source, advisory, or assistant use case is no longer enough by itself to create a new top-band answer.

## Sequencing addendum (rev0425)
For questions about **program order, staffing order, or funding order** rather than broad ranking, read `design/portfolio-execution-sequencing-2026Q1.md` right after this note.

Interpretation rule:
- this revision does **not** change the broad ladder;
- it makes the archive's default build order explicit;
- and the preferred generic sequence is now **shared spine -> Build-State Evidence -> Semantic Context -> boundary bridges -> recommendation/specialist widenings**.

## Execution addendum (rev0423)
For questions about what the archive's **active specialist frontier** should actually ship, read `design/native-edge-execution-blueprint-2026Q1.md` immediately after `design/worthy-contribution-shortlist-2026Q1.md`.

Interpretation rule:
- the broad ladder is unchanged;
- **Native Edge Contract** remains the active specialist frontier;
- this revision does **not** promote a new frontier;
- it makes that frontier concrete as a **portable native-edge reference layer** above imported boundary, provider/link, context, and foreign-build handoff evidence.

## Execution addendum (rev0422)
For questions about what the archive's strongest **anti-tacit-knowledge / ecosystem-navigation answer** should actually ship, read `design/adoption-navigation-execution-blueprint-2026Q1.md` immediately after `design/worthy-contribution-shortlist-2026Q1.md`.

Interpretation rule:
- the broad ladder is unchanged;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer;
- this revision does **not** promote a new frontier;
- it makes that answer concrete as a **portable project-scoped recommendation-review layer** above defaults, canon, evidence, and local-fit imports.

## Execution addendum (rev0421)
For questions about what the archive's **release / upgrade portfolio seam** should actually ship, read `design/migration-public-api-execution-blueprint-2026Q1.md` immediately after `design/worthy-contribution-shortlist-2026Q1.md`.

Interpretation rule:
- the broad ladder is unchanged;
- the clearest multi-project portfolio answer is still **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- this revision does **not** promote a new frontier;
- it makes the remaining release / upgrade quadrant concrete as a **portable version bridge** above imported Public API and Migration Truth evidence.

## Execution addendum (rev0420)
For questions about what the archive's current **operationally urgent seam** should actually ship, read `design/package-intake-gateway-execution-blueprint-2026Q1.md` immediately after `design/worthy-contribution-shortlist-2026Q1.md`.

Interpretation rule:
- **Package Intake Gateway** remains the most underappreciated operational seam;
- this revision is **deepening**, not promotion;
- the sharper answer is now “portable package-ingress review layer” rather than merely “something about supply-chain security”;
- **Package Admission**, **Dependency Review**, **compile-time execution authority**, and **Consumer Install** remain separate even when current advisories make intake feel newly urgent.

## Execution addendum (rev0418)
For questions about what the archive's current **one-project winner** should actually ship, read `design/build-state-evidence-execution-blueprint-2026Q1.md` immediately after `design/worthy-contribution-shortlist-2026Q1.md`.

Interpretation rule:
- **Build-State Evidence** remains the strongest one-project answer;
- this revision is **deepening**, not promotion;
- the sharper answer is now “portable build-review layer above Cargo-native evidence” rather than merely “something about builds”;
- **Package Intake Gateway** remains separate even though current security signals make it feel more urgent.

## Execution addendum (rev0417)
For execution-oriented / funder / one-project-vs-portfolio questions, read `design/worthy-contribution-shortlist-2026Q1.md` immediately after this note.

Interpretation rule:
- **Build-State Evidence** = strongest one-project answer;
- **Native Edge Contract** = active specialist frontier;
- **Package Intake Gateway** = most underappreciated operationally urgent seam;
- **Semantic Context Contract** = key hidden multiplier;
- **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake** = clearest multi-project portfolio answer.

# Design: Strategic Territory Map 2026Q1

## Goal
This is a **portfolio synthesis note**, not a new frontier promotion.
Its job is to answer one broader question the archive kept circling:

> After reading the latest archive and fresh official Rust signals, what would actually count as a worthy or even epic contribution to the ecosystem now?

The answer is **not** “whatever sounds ambitious.”
The answer is: contributions that turn recurring Rust pain into **reviewable, machine-usable, non-imperial contracts**.

Ideal Rust is still missing many things, but the deepest gaps are no longer best described as “one more framework”, “one more score”, or “one more assistant”.
They are better described as missing **truth-carrying seams** between code, builds, APIs, migration, native interop, docs, support, and future machine consumers.

## Fresh signals that matter most
Several recent official signals keep converging on that same interpretation.

- The March 20, 2026 Rust challenges post says the ecosystem problem is often **choice paralysis** and **tacit knowledge**, not simple absence of crates.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the canonical reference, while debugging and resource usage remain real pain points and editor / LLM-mediated learning is rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 goals/roadmaps make the strategic pressure unusually explicit: **Building blocks**, **Secure your supply chain**, **Safety-Critical Rust**, **Higher-level Rust**, and cross-language application areas are all active at once.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Cargo and docs.rs are increasingly exposing machine-usable substrate rather than only human-facing output: Cargo build-analysis and build-dir-layout work, docs.rs-hosted rustdoc JSON, and crates.io’s newer security / publishing / metadata surfaces all push in that direction.
- The archive now also needs a thinner **portfolio grammar** above those substrates, so the strongest multi-project answer does not fragment into six incompatible trust models.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://docs.rs/about/rustdoc-json
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The Rust project keeps saying Cargo cannot be everything to everyone, which is a strategic hint that many worthy contributions should be **companion tools with disciplined artifact families**, not demands that Cargo itself become a universal platform.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Headline conclusion
The archive’s broad ladder should stay intact.
What changed is that the repo now has a clearer single-sentence answer to “what Rust is really missing”:

> Rust is most strategically missing **portable evidence and contract layers** that let humans, tools, CI, docs, and assistants share the same bounded truth without flattening distinct layers into folklore.

That conclusion favors some candidates and eliminates others.

## Portfolio answer by question

### 1) If you want the strongest broad/buildable epic contribution overall
Keep **Build-State Evidence** in first place.

Why it still wins:
- the survey still says slow compile times and storage usage are among the biggest productivity problems;
- the compiler-performance survey and Cargo build-analysis work both say users need better explanations of what rebuilt and why;
- build-dir-layout and related work make editor/Cargo coexistence, locking, GC, and shared-cache design first-class engineering problems;
- and the contribution composes with many other frontiers instead of competing with them.

Read with:
- `design/build-state-evidence-stack.md`
- `design/build-state-evidence-pilot-program.md`
- `design/build-cache-kit.md`
- `design/change-impact-kit.md`
- `design/build-doctor-kit.md`

### 2) If you want the strongest anti-tacit-knowledge / ecosystem-navigation answer
Keep **Adoption Navigation Contract** plus **Reviewable Lane Defaults + renewal receipts** in first place.

Why it still wins:
- the challenge signal is about **choosing well**, not merely discovering that crates exist;
- docs remain canonical, but the recommendation layer still lacks project-scoped, freshness-visible decision records;
- and the worthy move is still not a global “best crates” list but a portable decision bundle.

Read with:
- `design/adoption-navigation-contract-2026Q1.md`
- `design/reviewable-lane-defaults.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/ecosystem-atlas-kit.md`

### 3) If you want the clearest daily developer-experience composition move
Keep **Rust inner-loop contract / Feedback Loop Stack** as the best bundle-shaping move under the build/debug band.

Why it matters:
- build-state evidence and debuggability now visibly overlap;
- Cargo is finally producing session-grade machine-usable evidence;
- and debugger/runtime/editor tradeoffs need a review boundary instead of remaining local lore.

Read with:
- `design/rust-inner-loop-contract-2026Q1.md`
- `design/feedback-loop-stack.md`
- `design/debuggability-stack.md`
- `design/build-state-evidence-stack.md`

### 4) If you want the most strategically real specialist frontier for industry adoption
Keep **Native Edge Contract** as the clearest current specialist frontier.

Why it matters:
- cross-language interop is now an explicit Rust application area;
- C++/Rust and broader native-edge adoption are not niche edge cases;
- and the missing contribution is a reviewable handoff for boundary/provider/toolchain/build-system truth, not another one-tool bridge empire.

Read with:
- `design/native-edge-execution-blueprint-2026Q1.md`
- `design/native-edge-contract-2026Q1.md`
- `design/native-edge-stack.md`
- `design/ffi-boundary-kit.md`
- `design/native-dependency-kit.md`

### 5) If you want the hidden multiplier for future semver, docs, IDE, CI, and assistant tooling
Treat **Semantic Context Contract** as the most important enabling substrate that should remain explicit even when it is not the active top-band promotion.

Why it matters:
- docs.rs now hosts rustdoc JSON;
- `cargo-semver-checks` and cross-crate linting still need honest cross-crate semantic context;
- Cargo is still evolving its machine-facing surfaces;
- and more consumers now want derived machine answers without becoming the new source of truth.

Read with:
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/semantic-context-contract-2026Q1.md`
- `design/semantic-context-kit.md`
- `design/semantic-context-lane-map.md`

### 6) If you want release/change correctness rather than broad DX
Keep **Public API Contract** and **Migration Truth Contract** as the strongest paired release/change-program frontiers.

Why they matter:
- public/private dependencies, semver enforcement, and SBOM work keep making release boundaries more explicit;
- migration continues to be staged, configuration-sensitive, and harder than one fixer pass;
- and both areas benefit from semantic context without collapsing into it.

Read with:
- `design/public-api-contract-2026Q1.md`
- `design/migration-truth-contract-2026Q1.md`

## Explicit ranking discipline
This note does **not** rewrite the broad ladder.
For portfolio purposes, keep the current broad order intact:

1. **Build-State Evidence**
2. **Adoption Navigation Contract**
3. **Reviewable Lane Defaults + renewal receipts**
4. **Debuggability / Rust inner-loop contract**
5. **Workspace Environment Contract**
6. **Toolchain Productization Contract**
7. **Migration Truth Contract**
8. **Public API Contract**
9. **Native Edge Contract**
10. **Publisher & Source Identity / Distribution / Maintenance Reality** as adjacent operational seams
11. **Semantic Context Contract** as the key hidden multiplier beneath several of the above, not a reason to flatten them
12. the remaining testing / assurance / observability / runtime / public-lane bands in their current relative order

Interpretation rule:
- **broad build priority** is not the same thing as **current specialist frontier**;
- **active promotion** is not the same thing as **hidden multiplier**;
- and **important substrate** is not automatic justification for moving a candidate to the top of the broad ladder.

## What to explicitly fold or eliminate
A portfolio synthesis is only useful if it says what **not** to build as standalone empires.

### Fold these into Adoption Navigation instead of treating them as separate top-band answers
- another global crate-score site
- another “best Rust stack” essay engine
- another assistant-only recommendation layer

Why: those ideas only become honest when they import **question truth, candidate-lane truth, canonical references, maintenance reality, and freshness-visible evidence**.

### Fold these into Build-State Evidence / Rust inner-loop instead of treating them as separate top-band answers
- another generic build-health score
- another cache-wrapper-first empire
- another “why is my build slow?” dashboard with weak provenance

Why: the missing seam is **portable evidence and diagnosis**, not yet another surface that competes with Cargo-native reporting.

### Fold these into Native Edge instead of treating them as separate top-band answers
- another “universal Rust FFI framework” pitch
- another “one build.rs trick for all native deps” pitch
- another CMake/Bazel adapter that silently claims the whole adoption story

Why: boundary truth, provider/link truth, host/target truth, and foreign-build handoff are separate facts.

### Fold these into Public API + Migration Truth + Semantic Context instead of treating them as separate top-band answers
- another semver-only checker with no explicit subject/authority story
- another migration bot that hides what changed, what was inferred, and what remained manual

### Fold these into Canonical Learning rather than treating them as standalone strategic answers
- another docs portal that rephrases maintainer docs without stronger validation or structured imports
- another assistant-first “smart docs” layer that becomes the only visible surface

## What a worthy contribution should look like
Across the portfolio, the archive should keep rewarding the same shape.

### Theoretical shape
A worthy contribution should usually be:
1. **thin** rather than imperial;
2. **artifact-first** rather than dashboard-first;
3. **compositional** rather than one-true-platform;
4. **machine-usable but human-reviewable**;
5. **explicit about partiality, freshness, and unsupported areas**;
6. **adjacent to official Cargo/rustc/docs.rs/crates.io surfaces** instead of pretending those surfaces do not exist.

### Practical shape
A worthy v0 should usually have:
- a small artifact family with named schemas;
- capture / explain / diff / verify / doctor style commands or equivalent workflows;
- imports from current Rust substrate instead of bespoke scraping;
- derived assistant/summary outputs kept downstream from captured truth;
- and a pilot program that starts with one lane where the evidence is already real.

## Lessons of the past and present
The repo should keep remembering these lessons.

1. Rust does **not** mainly need more opinionated surface area; it needs better **truth transfer** across existing surface area.
2. The strongest ecosystem contributions often sit **between** official components rather than inside one of them.
3. Better machine-usable surfaces do **not** reduce the need for canonical docs; they increase the value of keeping canonical docs authoritative.
4. LLM/editor-mediated workflows are becoming more common, which means the archive should invest more in **bounded consumer layers**, not less.
5. A specialist frontier can be strategically urgent without outranking the broadest buildable epic overall.

## Repo consequence
This revision should therefore be treated as **synthesis + hygiene**, not promotion.

- The broad ladder stays intact.
- The active specialist frontier remains **Native Edge Contract**.
- `design/strategic-territory-map-2026Q1.md` becomes the first read when the question is archive-wide prioritization, elimination, or “what worthy Rust contribution should win next?”
- Future revisions should say explicitly whether they are:
  - **promotion**,
  - **deepening**,
  - **synthesis with no new promotion**,
  - or **hygiene**.

## References (signals)
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
