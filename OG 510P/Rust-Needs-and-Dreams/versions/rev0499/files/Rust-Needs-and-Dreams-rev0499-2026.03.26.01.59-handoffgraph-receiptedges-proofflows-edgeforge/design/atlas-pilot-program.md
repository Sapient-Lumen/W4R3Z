# Design: Atlas Pilot Program (`cargo atlas pilot`, `atlas-pilot-pack/v0`)

## Goal
Make the **Ecosystem Atlas** real by starting with a ranked, reviewable pilot program instead of attempting to model all of Rust at once.

The problem is no longer persuading ourselves that better stack guidance would be useful. The problem is choosing **which domains to pilot first**, what evidence and interop truth each pilot must carry, and how to tell whether a pilot is ready to graduate from “interesting curation” to “trusted ecosystem substrate.”

A worthy contribution here is not just `cargo atlas query`. It is a disciplined rollout program that can prove the atlas model on a few high-pressure domains without silently becoming a global blessed-crates list.

## References (signals)
- Rust’s vision work says users need help navigating crates.io, that people do not have a place to get advice on a good “starter set” of crates, and that smoother interop plus shared building blocks are part of the answer.  
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online documentation is still the preferred canonical reference, hints that people are moving some questions to LLM tooling, and calls out maintainer support as an explicit concern.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io now exposes better decision inputs such as Trusted Publishing posture, Security-tab advisory information, SLOC, and `pubtime`.  
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s 1.90 cycle notes explicitly say Cargo cannot be everything to everyone and that plugins matter, which argues for atlas as companion infrastructure rather than a demand that Cargo absorb all ecosystem curation.  
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The C++/Rust interop problem-map goal argues for building a broad skeleton first, then prioritizing pain points, competing solution areas, and long-lead work. That is also the right strategy for atlas pilots.  
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html
- docs.rs now hosts rustdoc JSON, and the Rust project is pushing StableMIR / `rustc_public` as a more reliable tool-facing interface. That makes it more realistic to derive machine-usable outputs from curated atlas truth.  
  https://docs.rs/about/rustdoc-json  
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html

## Why this needs its own design layer
The atlas design already explains the canonical artifact family (`atlas-domain`, `stack-lane`, `stack-slot-map`, `selection-evidence`, `freshness-budget`, and so on). What it does **not** fully answer by itself is:
- which domains should go first,
- how many lanes are enough for a credible pilot,
- which interop seams must be explicit before a pilot is trustworthy,
- how freshness is budgeted,
- what “pilot success” means,
- and when a pilot should be frozen, widened, split, or retired.

Without that layer, atlas risks two bad outcomes:
1. **ontology inflation** — lots of beautiful schemas and no trusted recommendations;
2. **politics by accident** — a small number of early pilots become de facto blessed answers without explicit governance and evidence standards.

## Design principles
1. **Pilot domains, not total coverage.** We should prefer a few well-run domain pilots over a giant half-curated universe.
2. **Multiple respectable lanes per pilot.** If a domain only has one serious answer, atlas is not being tested very hard.
3. **Interop posture must be visible.** Every pilot needs named shared seams and named incompatibilities.
4. **Freshness must be budgeted up front.** “We’ll revisit this later” is not a contract.
5. **Governance must be explicit.** Early pilots should say who curates, who reviews, and how disputes or stale defaults are handled.
6. **Graduation criteria must be concrete.** A pilot graduates when it proves stable artifacts, credible freshness, explicit alternatives, and bounded derived outputs.
7. **Machine outputs stay subordinate.** Guides, starter templates, and assistant contexts are derived artifacts, never the recommendation source of truth.

## Artifact family
### 1. `pilot-domain-brief/v0`
Defines why a domain is worth piloting:
- domain id and summary
- target audience and expected users
- why this domain is high-pressure enough to matter
- why it is tractable enough to pilot now
- key interop seams and likely lane splits

### 2. `pilot-slot-template/v0`
The minimum slot skeleton a pilot must make explicit:
- required versus optional slots
- slots that are still too immature to standardize
- expected shared seams between slots
- anti-slots (things that must not be smuggled in as hidden defaults)

### 3. `pilot-lane-candidate-set/v0`
The lane hypotheses before curation hardens:
- candidate lane ids
- what each lane optimizes for
- why each lane deserves to exist
- what evidence is still missing before a lane can be recommended

### 4. `pilot-evidence-budget/v0`
Defines minimum evidence for a credible pilot:
- required registry / docs / trust / lifecycle / support inputs
- required interop-seam truth
- freshness windows per signal type
- manual-review requirements
- explicit “cannot yet claim” areas

### 5. `pilot-governance-profile/v0`
Makes pilot stewardship reviewable:
- curators and reviewer roles
- conflict-of-interest expectations
- dispute/escalation path
- publish cadence and stale-lane policy
- conditions for splitting one pilot into subdomains

### 6. `pilot-success-scorecard/v0`
Decides whether the pilot is working:
- are lanes materially different and justified?
- are interop seams explicit enough to avoid cargo-culting?
- do freshness checks catch real drift?
- do derived outputs stay bounded and faithful?
- are alternatives still visible?
- do consumers use the artifacts rather than bypassing them?

### 7. `atlas-pilot-pack/v0`
Bundle for review and reuse:
- canonical pilot artifacts
- rendered pilot summary
- current recommendation state
- freshness status
- derived guide / template / assistant outputs with provenance

## Ranked first pilots

### 1) CLI / command applications
**Why first**
- Very common entry point for Rust adoption.
- Enough diversity for real lane choices, but still tractable.
- Strong documentation, testing, and packaging expectations.
- Good place to test how atlas handles ergonomics, footprint, and terminal-rich alternatives.

**Likely lanes**
- conservative / low-surprise
- rich terminal / interactive TUI
- low-footprint / minimal-dependency
- internal-platform / ops-tooling

**Core slots**
- argument parsing
- config/settings
- paths/filesystem posture
- error / diagnostic rendering
- logging/tracing
- testing / transcript verification
- packaging / install story

**Why this is a good pilot**
The CLI domain is broad enough to matter but bounded enough that slot maps, alternatives, and freshness can be made concrete quickly.

### 2) HTTP / service backends
**Why second**
- High practical value.
- Strong need for explicit runtime, middleware, and protocol seams.
- Already has real common vocabulary (`http`, Tower-style service/layer seams) to test atlas+commons integration.

**Likely lanes**
- axum/tower-oriented
- lower-level hyper-first
- conservative enterprise / support-weighted
- minimal-surface internal service

**Core slots**
- runtime
- HTTP types
- router / middleware stack
- auth/session posture
- config and secrets
- tracing / observability
- persistence / migration story
- service contract / API description

**Why this is a good pilot**
This is the clearest place to prove that atlas recommendations can point to real shared seams instead of vague “these crates work together” folklore.

### 3) Client apps and shell-heavy desktop/mobile lanes
**Why third**
- Rust interest in client apps is real, but the space is fragmented.
- Strong need to expose native bridges, permission/capability assumptions, packaging, and update channels explicitly.
- Good test of how atlas handles high interop cost and multiple shells.

**Likely lanes**
- Tauri/web-shell oriented
- native Rust UI oriented
- bridge-heavy / mixed-language mobile-app lane

**Core slots**
- shell / UI toolkit
- platform bridge
- app lifecycle
- permissions/capabilities
- packaging/update story
- logging/crash reporting
- storage and settings

**Why this is a good pilot**
A client-app pilot would force atlas to represent real-world compromise instead of pretending there is one clean universal GUI stack.

### 4) Safety-oriented internal tools
**Why fourth**
- Important because it tests whether atlas can weight maintenance, trust, support, and reviewability more heavily than popularity.
- Lower glamour, high real-world value.
- Good proving ground for integration with Trust Signals, Lifecycle Ledger, Support Envelope, and Safety Evidence.

**Likely lanes**
- conservative internal CLI
- review-heavy service utility
- offline / airgapped-adjacent lane

**Core slots**
- dependency posture
- native dependency posture
- settings/config provenance
- logging/audit evidence
- packaging / support claims
- assurance evidence imports

**Why this is a good pilot**
It tests whether atlas can resist popularity-driven defaults and instead produce evidence-backed conservative guidance.

### 5) Wasm component / plugin host surfaces
**Why fifth**
- Strategic, but still moving fast.
- Valuable as a pilot because it forces explicit host requirements, package identity, and compatibility claims.
- Better after atlas has already proved itself on more stable domains.

**Likely lanes**
- component-first service/plugin lane
- host-embedder lane
- experimental composition lane

**Core slots**
- WIT/world identity
- host capability profile
- publication/registry path
- composition and import satisfaction
- compatibility and testing story

**Why this is not first**
The underlying workflows are still evolving quickly enough that it is a better second-wave pilot than the opening demonstration.

## Pilot domains to defer
These are important, but not ideal first pilots:
- **general async** — too much live language/runtime churn for first-wave curation
- **ML/data science** — high value, but stack boundaries and interop seams are still too messy for a clean opening atlas demonstration
- **embedded as a single pilot** — should likely split by subdomain (MCU app, RTOS-ish, Linux edge, safety-critical embedded) rather than pretend one embedded lane exists
- **game development** — strategically interesting, but ecosystem identity is too framework-centered for first-wave neutral curation

## Suggested CLI shape
- `cargo atlas pilot plan`
- `cargo atlas pilot check`
- `cargo atlas pilot diff`
- `cargo atlas pilot score`
- `cargo atlas pilot render`
- `cargo atlas pilot promote`
- `cargo atlas pilot retire`

## Phased execution
### Phase 0: pilot-program scaffolding
- lock down pilot artifacts
- define scorecards and evidence budgets
- write one worked example without pretending the ecosystem is already solved

### Phase 1: first two pilots
- ship CLI and HTTP/service pilots
- require explicit lane differences, alternatives, seam references, and freshness budgets
- produce derived guide + assistant-context outputs only after canonical artifacts are stable

### Phase 2: governance and federation
- add at least one non-core curator or org overlay
- test stale-lane handling and dispute resolution
- prove that atlas can remain plural instead of converging on one global answer

### Phase 3: second-wave pilots
- add client-app and safety-oriented pilots
- use them to test heavy interop and high-trust weighting

### Phase 4: fast-moving domains
- approach Wasm component/plugin pilots once the first-wave mechanics are credible
- explicitly mark volatile or watch/wait lanes instead of overclaiming stability

## Non-goals
This program should **not**:
- pretend every Rust domain is ready for curation now;
- turn early pilots into silent global defaults;
- hide disagreement between curator groups;
- emit unbounded assistant prompts divorced from freshness and provenance;
- or treat domain popularity as enough evidence for recommendation quality.

## Why this could be an epic contribution
The atlas idea becomes much more credible when paired with a concrete pilot program.

That is the move from “interesting vision” to “ecosystem infrastructure.” A successful pilot program would give Rust:
- an explicit way to experiment with reference stacks without pretending to bless the whole ecosystem,
- a way to test federation and curator pluralism before politics hardens,
- a path to machine-usable starter guidance that still respects canonical docs and review,
- and a discipline for turning ecosystem lore into durable, freshness-aware artifacts.

The real achievement is not one more list of recommended crates.
It is a **repeatable method for publishing and maintaining known-good Rust lanes**.
