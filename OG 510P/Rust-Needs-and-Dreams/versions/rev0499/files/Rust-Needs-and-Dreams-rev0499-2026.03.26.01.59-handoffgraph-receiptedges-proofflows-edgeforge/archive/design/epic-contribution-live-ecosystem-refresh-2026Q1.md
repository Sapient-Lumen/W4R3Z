# Design: Epic contribution live ecosystem refresh (2026Q1)

## Goal
The archive already had a strong broad ladder, sharper execution blueprints, live dossiers, live decision packets, first-build kernels, slices, contracts, witness packs, fixture packs, and schema packs.
What it still lacked was one explicit note for a recurring maintainer question:

> if we re-open the latest archive **and** re-check the freshest official Rust signals, what is ideal Rust still really missing **now**, which contributions still look worthy or epic, which ones are currently buildable, and what meta-hygiene should keep that refresh from turning into smooth LLM folklore?

This note is a **live external-signal refresh + priority-sharpening + meta-hygiene deepening** pass.
It does **not** rewrite the broad ladder.
It does **not** promote a new frontier.
It exists so the archive can answer “what is missing right now?” without forgetting the distinction between:
- strategic importance;
- current delivery posture;
- and source-candor / archive-operating discipline.

Read with:
- `design/territory-priority-refresh-2026Q1.md`
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `design/epic-contribution-v0-kernel-briefs-2026Q1.md`
- `design/epic-contribution-kernel-slices-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Why a new live refresh note is merited
The latest official Rust signals keep reinforcing the same broad pain map, but they also sharpen **how** the archive should read it.

The 2025 State of Rust survey says resource usage (slow compile times and storage usage) is still one of the leading non-trivial problems, debugging remains a meaningful pain point, docs remain the preferred canonical reference, and editor/LLM-mediated learning is rising.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The March 2026 challenges post says the recurring universal challenges are compilation performance, borrow checking/ownership for beginners, async difficulty, and ecosystem-crate choice and maturity gaps, while embedded, safety-critical, and GUI work each surface sharper domain-specific missing support.
It is also a useful meta-hygiene signal because the original version was retracted after criticism of the LLM-shaped draft, which makes this source valuable for challenge categories and cautionary process lessons, but a poor excuse for vague “the ecosystem feels like…” paraphrase.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 compiler-performance survey says build performance pain is not one thing; it breaks into incremental rebuilds, type-check/IDE performance, clean/CI builds, link time, and explanation deficits.
It explicitly says respondents want better understanding of why builds are slow, and that `cargo check` / `cargo build` cache separation remains painful.
https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/

Cargo's live roadmap keeps validating the archive's build/debug substrate instincts.
The build-dir-layout goal says the status quo creates whole-cache locking, bad CI cacheability, and user pressure to depend on internal details.
The build-analysis goal is explicitly about recording richer metrics, extending `cargo report`, and enabling external tooling and build replay while keeping data collection opt-in.
The relink-don't-rebuild goal says many obviously-local edits still rebuild reverse dependencies.
The production-ready Cranelift goal says compile-time improvements matter, but that debug info is still a major missing feature.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
https://rust-lang.github.io/rust-project-goals/2025h2/production-ready-cranelift.html

The debugging survey says Rust is still not at first-class debugger support, especially across debugger versions, operating systems, async workflows, visualizers, and Rust-expression evaluation.
That makes debuggability a **cross-tuple acceptance commons**, not a “just fix LLDB” leaf.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The package and registry picture keeps rewarding package-intake and route-review work.
crates.io has new security-tab and trusted-publishing improvements, but the malicious-crate policy update and the March 2026 Cargo advisory both underline that route posture, alternate-registry caveats, and real operational response still matter.
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

The safety-critical picture keeps validating a program-shaped commons.
The January 2026 safety-critical writeup says the ecosystem still lacks maturity around qualification/certification tooling, readiness checklists, dependency lifecycle patterns, safety-case-friendly async/runtime requirements, and interop discipline.
The FLS adoption note matters here because it shows one concrete path where industry-backed qualification work moved into a sustainable Rust-Project home without pretending the whole ecosystem was suddenly “solved”.
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
https://blog.rust-lang.org/2025/03/26/adopting-the-fls/

The canonical-learning and atlas story is also sharper now.
The Vision Doc lessons post says the process gathered a broad survey plus 70+ interviews, but also says broad interviews do not answer every technical question and recommends more open, incremental, structured user research over one giant post-hoc summary.
That supports the archive's insistence on lane defaults, renewal receipts, canon/derivation boundaries, and source-candor.
https://blog.rust-lang.org/2025/12/03/lessons-learned-from-the-rust-vision-doc-process/

## Headline answer
The freshest official picture still says the archive's strongest missing contributions are **shared evidence layers and shared readiness commons**, not one more winner-take-all framework.

The live reading should now be:

1. **Build-State Evidence** remains the strongest overall missing contribution.
2. **Package Intake + Release Boundary Review** is the clearest operator-shaped urgent bridge.
3. **Feedback Loop / Debuggability Acceptance Commons** is the clearest next deepening build.
4. **Safety-Critical + Institutional Readiness Commons** is the clearest program-shaped rising seam.
5. **Compatibility Claims** is the clearest claim-routing layer that many downstream consumers actually need.
6. **Adoption Navigation + Ecosystem Atlas + renewal receipts** remains strategically huge, but still has a real renewal-burden blocker.
7. **Tooling Contract + Semantic Context** remain the most important machine-facing substrates beneath several of the items above.

That is **not** a broad ladder rewrite.
It is the archive's best current answer to two distinct questions:
- what is strategically most missing; and
- what has the clearest present-tense path to an honest first ship.

## The two ladders the archive must keep separate

### A) Strategic importance ladder
For “what is Rust really still missing?” questions, keep this order in mind:
1. **Build-State Evidence**
2. **Feedback / Debug Acceptance Commons**
3. **Package Intake + Release Boundary Review**
4. **Safety-Critical Readiness Commons**
5. **Compatibility Claims**
6. **Adoption Navigation + Ecosystem Atlas**
7. **Tooling Contract / Semantic Context substrate**

Rationale:
- build/resource pain is broad and still under-explained;
- debugging is broad, cross-tool, and still structurally underbuilt;
- package intake is where supply-chain/security/advisory/route reality hits real operators;
- safety-critical is the clearest rising domain where better evidence layers and consortium-shaped ownership really matter;
- compatibility claims are increasingly necessary because target/platform/MSRV/debugger/support truth keeps shifting;
- adoption navigation is strategically huge but still expensive to keep honest;
- tooling-contract and semantic-context work are powerful mostly because they make other layers more honest and less scrape-driven.

### B) Current delivery ladder
For “what should a serious team fund or ship next?” questions, use the live packet posture:
1. **Build-State Evidence** — current `advance`
2. **Package Intake + Release Boundary Review** — current `advance`
3. **Feedback / Debug Acceptance Commons** — current `deepen`
4. **Safety-Critical Readiness Commons** — current `deepen`
5. **Adoption Navigation + Ecosystem Atlas** — current `hold` until renewal burden becomes more honestly solved

Interpretation rule:
- do not let strategic importance impersonate current readiness;
- do not let current `hold` posture erase long-run strategic importance;
- and do not let enabling substrates outrank user-visible evidence layers just because they sound more “infrastructure-ish”.

## What the strongest missing contributions should look like in theory and practice

### 1) Build-State Evidence
This remains the archive's strongest one-project answer because the official signals keep describing the same missing thing from different angles:
- users want to know what rebuilt and why;
- `cargo check` and `cargo build` still create cache/handoff pain;
- build-dir layout is changing because too many tools depend on internal details;
- and future Cargo work keeps pointing toward recorded build facts, report surfaces, and replayable analysis.

In theory, the worthy contribution is an **evidence layer** for the build loop.
In practice, it should look like:
- one portable `build-state-pack/v0` family;
- imports from Cargo-native or Cargo-adjacent structured facts rather than `target/` scraping;
- `capture`, `explain`, `diff`, `doctor`, and `renewal` commands;
- explicit unsupported-state receipts for unstable or lossy imports;
- exports for CI, support, IDE, package-intake, and debug consumers.

What to refuse:
- a cache platform pretending to be the whole answer;
- a build-health score farm;
- a daemon that quietly becomes the real build control plane.

### 2) Package Intake + Release Boundary Review
This seam should now be read as a first-class epic, not just a security side quest.
The ecosystem keeps needing one honest answer to:
- what route is this dependency coming from;
- what package/build-script/malware posture applied;
- what waivers or drills exist;
- and what changed at the registry or release boundary.

In theory, the worthy contribution is an **operator review kit** for package admission and boundary receipts.
In practice, it should look like:
- route profiles;
- intake receipts;
- waiver and quarantine receipts;
- explicit alternate-registry posture and caveats;
- import lanes for RustSec, registry metadata, trusted-publishing posture, build-script risk, and drill evidence.

What to refuse:
- a giant trust dashboard with unclear decision rights;
- a one-number “package safety” score;
- a hosted platform that hides route-specific unknowns.

### 3) Feedback Loop / Debuggability Acceptance Commons
The debugging survey makes clear that the missing thing is not one visualizer or one debugger adapter.
The missing thing is a **cross-tuple acceptance commons** that can say what works, what regressed, and what is still unsupported across debugger/runtime/OS/toolchain combinations.

In theory, the worthy contribution is an acceptance-layer bridge from build evidence to diagnosis and handoff.
In practice, it should look like:
- debugger-tuple profiles;
- session packs and replay results;
- async-debug acceptance lanes;
- visualizer and expression-evaluation acceptance artifacts;
- exports for issue filing, support, docs, and bounded assistant/editor consumers.

What to refuse:
- “bless one debugger and move on”;
- an IDE-only solution with no portable receipts;
- a debugger fork sold as the whole ecosystem answer.

### 4) Safety-Critical + Institutional Readiness Commons
This is the clearest place where ideal Rust must think outside the usual crate/tool reflex.
The missing contribution is not a badge, not a whitepaper, and not one certified runtime proclamation.
It is a **shared readiness commons** with evidence slots, checklists, lifecycle patterns, and explicit ownership/renewal discipline.

In theory, it is a program seam that helps high-assurance users state real readiness without overclaim.
In practice, it should look like:
- target- and domain-oriented readiness cards;
- dependency lifecycle and replacement playbooks;
- async/runtime qualification requirement bundles rather than one premature runtime winner;
- interop/FFI evidence lanes;
- attachable evidence imports from support, toolchain, package-intake, compatibility, and public-boundary layers.

What to refuse:
- “certified Rust” brand language with weak underlying receipts;
- one runtime trying to become the official safety story;
- one vendor-owned evidence portal replacing a commons.

### 5) Compatibility Claims
This keeps mattering because target policies, docs.rs defaults, MSRV drift, public-boundary realities, debugger tuples, and domain-specific requirements all create claims that people repeat faster than they can verify.

In theory, the worthy contribution is a **claim-routing layer**.
In practice, it should look like:
- explicit claim families;
- imported support-envelope, public-API, debugger, and toolchain evidence;
- drift receipts and recheck triggers;
- narrow exports for docs, release, support, and procurement-style consumers.

What to refuse:
- a badge farm;
- one matrix pretending to settle every support question;
- one semver/MSRV result being treated as the whole verdict.

### 6) Adoption Navigation + Ecosystem Atlas
The latest official signals strengthen the need, but they also strengthen the warning.
People do need help choosing crates, stacks, and defaults.
But the Vision Doc lessons and survey signal both argue against one giant recommendation machine.

In theory, the worthy contribution is an **editorial/renewal commons** for bounded defaults and lane maps.
In practice, it should look like:
- scenario/lane cards;
- atlas records with explicit evidence imports;
- renewal receipts and drift notices;
- local-fit overlays rather than global winner declarations;
- explicit `unknown`, `manual-review-required`, and `stale` posture.

Why it is still `hold` for kernelization:
- the burden is not imagination;
- the burden is keeping recommendation truth fresh, scoped, reviewable, and anti-theater.

What to refuse:
- best-crates portals;
- leaderboard theater;
- assistant-memory canon with no freshness surface.

### 7) Tooling Contract + Semantic Context substrate
These remain crucial, but mostly as imported truth families beneath the higher-ranking epics.
The ecosystem still lacks a coherent machine-facing handoff for scope/plan/evidence and a sufficiently portable semantic substrate for richer downstream reasoning.

In theory, these are **multipliers**.
In practice, they should look like:
- versioned import/reference packs;
- bounded discovery/scope/plan/evidence sections;
- semantic context packs with exact subject/version/freshness posture;
- explicit adapter-lossiness accounting.

What to refuse:
- a Cargo daemon;
- a universal knowledge graph pitch;
- a nightly-only substrate pretending it already solves downstream stability.

## Outside-the-box bets that still look worthy

### Safety-case-friendly async requirements, not anointing one runtime
The safety-critical writeup is a clue that the right missing contribution may be a **requirements/evidence layer for async suitability** before it is a runtime product race.
A worthy contribution here would capture scheduling assumptions, executor behavior, qualification needs, blocking rules, and audit hooks in a reviewable form.

### Sandboxed build inputs and permission manifests
The sandboxed build-scripts goal is still not top-band on its own, but it remains one of the clearest bets that could improve determinism, trust, reproducibility, and build explainability at once.
The right framing is not “Wasm everywhere”.
It is **permissioned build authority with receipts**.
https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html

### Interop evidence kits for long-lived C/C++ boundaries
The safety-critical writeup also makes clear that many serious adopters will live on FFI boundaries for years.
A worthy contribution here is not magical zero-cost bindgen romance.
It is a review kit that keeps interface shape, unsafe posture, drift, ownership, and replacement plans visible.

### Canonical learning plus bounded derivation overlays
Because docs remain canonical while LLM mediation rises, the worthy contribution is not “AI for Rust docs”.
It is a canon-plus-derivation boundary where maintainers can publish stable learning truth and downstream assistant/editor consumers can carry visibly lossy overlays.

## What should be folded, merged, or refused faster
- Generic crate-discovery portals should fold under **Adoption Navigation + Ecosystem Atlas** if they survive at all.
- Release-score or provenance-score projects should fold under **Package Intake** or **Compatibility Claims** instead of becoming their own empire.
- IDE-only build/debug improvements should route through **Build-State Evidence** and **Debug Acceptance**, not become standalone strategic answers.
- “Make Cargo the one universal workspace/build control plane” should be refused faster.
- Assistant-memory canonization should be refused faster.
- “Just pick the right runtime/framework” remains the wrong answer to most of these ecosystem gaps.

## Meta-hygiene consequence
The latest official Rust signals now teach two archive-operating lessons:

1. **Freshness without source-candor is not enough.**
   A source can be current and still need careful scope handling, especially when a post itself became part of the controversy.

2. **Broad research must not impersonate specific technical proof.**
   Surveys and interviews are good at pointing to pain categories, weak at settling exact tool/kernel shapes by themselves.

So future “latest archive + online refresh” answers should say, explicitly:
- what current official sources were re-checked;
- what stable canon is unchanged;
- what current packet/dossier posture still governs near-term action;
- what tempting ranking rewrite is still refused;
- and what part of the answer is strategy, current verdict, or meta-hygiene.

## Archive decision
- add `design/epic-contribution-live-ecosystem-refresh-2026Q1.md` as the live latest-signals synthesis note;
- add `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md` as the operating rule for future “latest archive + online refresh” revisions;
- keep the broad ladder unchanged;
- keep **Build-State Evidence** and **Package Intake + Release Boundary Review** as the clearest present-tense `advance` lanes;
- keep **Feedback / Debug Acceptance Commons** and **Safety-Critical Readiness Commons** as the clearest present-tense `deepen` lanes;
- keep **Adoption Navigation + Ecosystem Atlas** as strategically huge but still kernel-`hold` until the renewal burden is more honestly solved;
- keep **Compatibility Claims** and **Tooling Contract / Semantic Context** as imported multipliers rather than standalone winner-take-all answers;
- and tighten source-candor discipline for any future live refresh.