## Addendum (rev0494)
For questions about **what changed in current substrate truth before any packet, stewardship, or territory reading is rewritten**, read `design/epic-contribution-hot-substrate-watchcards-2026Q1.md` and `meta/HOT_SUBSTRATE_WATCH_PROTOCOL.md` after this note.

## Addendum (rev0493)
For questions about **whether a fresh official signal should change current packet posture, stewardship posture, or the broad territory reading itself**, read `design/epic-contribution-portfolio-control-loop-2026Q1.md` and `meta/PORTFOLIO_CONTROL_LOOP_PROTOCOL.md` after this note.

Interpretation rule:
- territory refresh still owns the broad strategic picture;
- the new control-loop note owns which loop a new change belongs to before the map is touched.


## Stewardship / graduation addendum (rev0492)
For questions about **what should happen after the broad territory and buildout order are already known**, especially when they ask for **where a worthy contribution should mature, what should stay companion-first, what should remain service-side, or what needs consortium-grade stewardship**, read `design/epic-contribution-stewardship-and-graduation-map-2026Q1.md` immediately after this note.

Interpretation rule:
- this note still owns the broad territory refresh;
- the new note owns the sharper **honest-home / graduation-path** read, not a fresh broad priority rewrite.

## Operating-surface addendum (rev0491)
For questions about **what should happen after the broad territory and buildout order are already known**, especially when they ask for **a coherent implementation family, shared operator verbs, repeated receipt roles, or what framework shapes should be refused**, read `design/epic-contribution-operating-surface-2026Q1.md` immediately after this note.

Interpretation rule:
- this note still owns the broad territory refresh;
- the new note owns the sharper **shared operating-surface** read, not a fresh broad priority rewrite.

## Buildout addendum (rev0490)
For questions about **what should happen after the latest-territory refresh**, especially when they ask not just for ranking but for **continuing repo construction, theory/practice details, side-bet folding, or archive meta-engineering**, read `design/epic-contribution-worthy-repo-buildout-2026Q1.md` immediately after this note.

Interpretation rule:
- this note still owns the broad territory refresh;
- the new note owns the sharper **worthy repo buildout** read, not a fresh broad priority rewrite.

## Live refresh addendum (rev0489)
For questions about **what the latest archive plus latest official Rust signals imply right now**, especially when they ask not just for a broad band refresh but also for **current `advance` / `deepen` / `hold` reading** or **source-candor / LLM-hygiene lessons**, read `design/epic-contribution-live-ecosystem-refresh-2026Q1.md` immediately after this note.

Interpretation rule:
- this note still owns the broad 2026Q1 territory refresh;
- the new note owns the sharper **latest-signals + current-packets + meta-hygiene** read, not a fresh broad ladder rewrite.


## Addendum (rev0459)
For questions about how the strongest current candidates compare **side-by-side** once the broad bands are already known, read `design/epic-contribution-scorecards-2026Q1.md` immediately after this note.

Interpretation rule:
- the broad priority bands remain intact;
- the new note does **not** rewrite them;
- it exists to keep **broad first build**, **second build**, **multiplier**, **urgent bridge**, and **program seam** distinct during comparison.

# Design: Territory priority refresh (2026 Q1)

## Goal
Re-read the latest archive against the freshest public Rust signals and answer the harder portfolio question more directly:

> after all the blueprints, kits, and frontier work, what is still missing enough that a serious team, lab, or funder should actually build it now — and what should be folded, merged, or refused instead of widened?

This note is a **ranking refresh + synthesis pass + elimination pass**.
It does **not** promote a new frontier.
It exists so the archive can say, more crisply than before, which worthy contributions are merely interesting, which are fundable, which are epic, and which are seductive but strategically wrong.

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`

## Why a refresh is merited
The archive's broad answers were already strong.
What changed is that the latest public signals make the **ordering** and **shape discipline** harder to dodge.

Signals that sharpen the ranking:
- Rust's March 2026 challenges writeup says the recurring pain is not just ownership syntax or beginner friction. It explicitly names **compile/resource pain**, **async difficulty**, **choice paralysis / tacit knowledge**, and domain-specific maturity gaps such as embedded and safety-critical work.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says resource usage remains one of the biggest non-trivial productivity concerns, debugging remains a major challenge, docs remain the canonical reference, and editor/LLM-mediated learning is rising instead of fading. That is a strong argument for **portable truth layers** rather than more folklore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The compiler-performance survey says incremental rebuilds, link time, IDE/Cargo contention, and cache/layout pain remain serious, and that users want tools that explain what rebuilt and why. That keeps **Build-State Evidence** and the broader feedback-loop story in the top band.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo's accepted build-analysis, build-dir-layout, and relink-don't-rebuild work all point in the same direction: the ecosystem needs **machine-usable evidence and explicit handoff boundaries**, not one giant wrapper or daemon.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- The 2026 debugging survey says “truly stellar” support would require multi-debugger and multi-OS coverage, visualizers, first-class async debugging, and Rust expression evaluation — and says Rust is not there yet. That means debuggability is still not a leaf feature request; it is an ecosystem gap with acceptance-surface shape.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The safety-critical writeup says the friction is operational: readiness checklists, dependency lifecycle playbooks, MSRV discipline, async-runtime qualification, and audited interop boundaries are still missing. That is evidence for a **commons/program seam**, not a one-crate fix.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The StableMIR effort becoming `rustc_public` is a reminder that some of the most important contributions are **substrates that make whole classes of tools easier to build honestly**.
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/

## Headline conclusion
The broad ladder is still right, but the sharper order for serious near-term ecosystem bets is now:

1. **Build-State Evidence**
2. **Feedback Loop / Debuggability Acceptance**
3. **Adoption Navigation + Ecosystem Atlas + renewal receipts**
4. **Tooling Contract**
5. **Compatibility Claims**
6. **Safety-Critical Readiness Commons**

That list is not “the only things worth doing”.
It is the archive's best answer to **what most reduces recurring Rust pain without collapsing into a platform empire, score farm, or one-project fantasy**.

## Ranking refresh

### 1) Build-State Evidence remains the strongest one-project answer
This stays in first place.
The evidence has only gotten stronger:
- the compiler-performance survey keeps pointing to rebuild churn, linker latency, and poor bottleneck explanation;
- Cargo build-analysis is explicitly trying to capture the facts that a real build-review layer would need;
- build-dir-layout work makes contention, GC, and editor/CLI coexistence first-class;
- and this seam still composes with many others instead of competing with them.

What a worthy contribution should look like in practice:
- one portable `build-state-pack/v0` family;
- capture / explain / diff / doctor / renewal commands;
- imported facts from Cargo-native reports and structured outputs rather than target-dir scraping;
- separate fields for subject, rebuild reason, timing/resource evidence, cache/contention posture, and human-readable diagnosis.

What to refuse:
- a cache-wrapper empire;
- a build-health score dashboard;
- a daemon that becomes the real build control plane.

### 2) Feedback Loop / Debuggability Acceptance should now be treated as the clearest second-band build priority
The archive used to call this the clearest under-ranked missing middle.
That is still true, but the ranking should now be understood more forcefully:
**this is not just a nice adjacent seam; it is one of the best places to invest after build-state evidence.**

Why it rises:
- debugging is still named as major friction in both broad survey language and debugger-specific material;
- the debugging gap is not one debugger or one visualizer problem — it is a missing **acceptance layer** for build → diagnose → inspect → explain → handoff;
- and the same Cargo changes that help build evidence also make richer session and handoff packs more plausible.

What a worthy contribution should look like:
- a session-oriented `feedback-loop-pack/v0` family;
- imports from Build-State Evidence rather than fresh local lore;
- debugger-tuple profiles, visualizer acceptance, async-debug acceptance, and native/split-debug lanes;
- exports for issue, support, CI, docs, and bounded assistant/editor consumers.

What to refuse:
- another debugger fork sold as the whole answer;
- an IDE-only integration that loses portable truth;
- a hosted “developer experience” portal.

### 3) Adoption Navigation stays the strongest anti-tacit-knowledge answer and should be treated as a real top-band investment, not a soft community extra
The March 2026 challenges work makes this impossible to ignore.
The question is not “could we search crates better?”
The question is “how do teams make bounded, reviewable, renewable choices without inheriting silent private canon?”

The answer remains:
**Adoption Navigation Contract + Reviewable Lane Defaults + Ecosystem Atlas + renewal receipts.**

Why it deserves explicit top-band placement:
- choice paralysis and tacit knowledge are now named pain, not archive inference;
- docs remain canonical, which means recommendation layers must become more grounded and freshness-visible rather than more improvised;
- and editor/LLM mediation rising means the ecosystem needs stronger canonical recommendation artifacts, not weaker ones.

What a worthy contribution should look like:
- domain records, lane definitions, slot maps, local-fit overlays, and drift/renewal receipts;
- imported evidence from support, trust, learning, build, and compatibility layers without flattening them;
- project-scoped recommendation review rather than global winner declaration.

What to refuse:
- one “best crates for Rust” portal;
- a leaderboard disguised as guidance;
- an assistant memory blob masquerading as canon.

### 4) Tooling Contract remains the key machine-facing substrate and should be ranked above many newer specialist leaves
This seam matters because Cargo is still not a coherent machine-facing contract from discovery through evidence handoff.
The archive now has the right shape for it, and the current upstream direction keeps validating that shape.

Why it stays high:
- Cargo itself keeps emphasizing report surfaces, plugins, and layout honesty rather than one universal external API;
- many downstream tools still depend on partial surfaces or internal details because no better truth family exists;
- and later CI/IDE/outer-build/docs/release/assistant layers still need a shared import boundary.

What a worthy contribution should look like:
- `tooling-contract-pack/v0` or equivalent family;
- separate subject, discovery/scope, graph/plan, execution/evidence, stability/adapter-lossiness, and consumer-handoff truth;
- adapters/imports for Cargo-native surfaces instead of pretending one surface already owns the whole story.

What to refuse:
- a Cargo daemon;
- a BSP-only bridge;
- a monorepo control plane;
- a target-dir or build-dir scraper presented as stable canon.

### 5) Compatibility Claims is the right claim-routing seam, but it should now be understood as more strategic than glamorous
This is not the most exciting contribution.
It is one of the most necessary ones once teams need to answer: what is supported, on which terms, with what drift posture, and what do docs/release/support/safety consumers actually get to conclude?

Why it matters more now:
- safety-critical and platform-readiness work both need stronger claim shaping;
- MSRV and acceptance drift keep mattering even when target matrices look static;
- and more generated docs, reports, and assistants means unsupported claims spread faster unless the ecosystem has attachable truth.

What a worthy contribution should look like:
- `compatibility-claims-pack/v0` built from imported support-envelope, public-API, release, debugger-acceptance, and toolchain facts;
- explicit claim families, evidence posture, drift status, and unknowns;
- consumer-specific exports that stay lossy on purpose.

What to refuse:
- a badge farm;
- a single compatibility matrix pretending to own the verdict;
- one semver or MSRV result being treated as total support truth.

### 6) Safety-Critical Readiness Commons is the clearest rising program-shaped contribution that still should not be mistaken for one crate
This is the strongest place where the archive should think outside the usual “Cargo + dev tooling” reflex.
The safety-critical writeup makes clear that the missing work is partly technical, partly documentary, and partly institutional.

Why it merits elevation:
- readiness checklists, dependency lifecycle playbooks, async-runtime qualification requirements, and FFI/interop auditing all remain underbuilt;
- the underlying users are real, high-stakes, and increasingly public;
- and the payoff is larger than one niche: it pressures the ecosystem toward better evidence, better support claims, better toolchain productization, and better compatibility posture.

What a worthy contribution should look like:
- readiness checklists per target family;
- dependency lifecycle and replacement playbooks;
- attachable evidence slots for toolchain, support, public API, runtime, and interop posture;
- consortium-friendly ownership rather than one vendor-owned product.

What to refuse:
- a “certified Rust” brand with weak underlying evidence;
- one async runtime trying to win by proclamation;
- one compliance badge replacing actual traceability.

## Hidden multipliers and outside-the-box bets

### StableMIR-backed tool substrate
This remains one of the most interesting “small-looking but ecosystem-wide” bets.
A stable compiler-facing analysis substrate can make many other tools less fragile and less forced to depend on compiler internals.
The archive should keep treating it as an enabling substrate, not a user-facing epic by itself.

### Sandboxed build inputs (`build.rs` and proc macros)
This is still not mature enough to outrank the top band, but it is one of the clearest long-horizon supply-chain and determinism seams worth watching.
If it becomes practical, it could improve reproducibility, security posture, and build explainability all at once.
It should be framed as **build-authority and determinism substrate**, not as a novelty runtime story.

### Canonical learning with bounded assistant derivation
The survey signal that docs remain canonical while editor/LLM mediation rises means the archive should keep pushing for maintainer-authored canonical artifacts with explicit derived overlays.
The worthy contribution is not the assistant.
The worthy contribution is the **canon + derivation + lossiness boundary**.

## What should be folded, merged, or eliminated

### Fold under stronger parent seams
- Many release / provenance / publish ideas should now route through **Release Truth** or **Compatibility Claims** instead of spawning fresh leaf epics.
- Many crate-discovery or recommendation ideas should route through **Adoption Navigation + Ecosystem Atlas** rather than becoming new portals.
- Many IDE/CI/outer-build integration ideas should route through **Tooling Contract** and **Build-State Evidence** rather than pretending they are standalone strategic fronts.
- Many assistant-context ideas should route through **Canonical Learning** and the continuity protocol rather than becoming archive-local memory systems.

### Eliminate as top-band answers
The archive should now say “no” faster to these instincts:
- Cargo daemon / universal workspace manager dreams
- target-dir or build-dir scraping as tool substrate
- “best crates” portals and generic ecosystem score sites
- release-bot empires or provenance-badge theaters
- framework winner-hunting as a top-band portfolio answer
- assistant-owned repo memory that silently rewrites canon

These are not always worthless.
They are just usually the wrong **portfolio answer**.

## How to evaluate a fresh proposed contribution after this refresh
A candidate should now clear all of these bars before it is allowed to rearrange the top band:
1. it addresses a recurring pain named by official Rust signals, not just archive taste;
2. it emits reviewable artifacts instead of screenshots or private state;
3. it can begin as a thin companion layer rather than a platform empire;
4. it preserves multiple truth classes instead of flattening them;
5. it has a steward story that does not depend on constant heroic curation;
6. it either composes with the current top band or clearly beats one of its members.

If it cannot clear those bars, it should usually be folded, watched, or refused.

## Portfolio answer in one paragraph
If a serious team asked the archive, right now, what worth building in Rust would count as genuinely strategic, the answer should be:
**build one reviewable evidence layer first (Build-State Evidence), then one reviewable daily-loop acceptance layer (Feedback Loop / Debuggability Acceptance), then one renewable recommendation layer (Adoption Navigation + Ecosystem Atlas), while keeping Tooling Contract and Compatibility Claims as the machine-facing and claim-facing spines beneath them — and treat safety-critical readiness as the strongest program-shaped proving ground for whether the whole ecosystem can carry stronger evidence, support, and interoperability discipline.**
