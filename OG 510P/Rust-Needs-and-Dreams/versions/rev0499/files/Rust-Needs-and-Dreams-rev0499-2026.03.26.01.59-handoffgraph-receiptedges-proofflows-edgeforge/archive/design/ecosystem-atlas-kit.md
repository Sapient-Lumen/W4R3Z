# Design: Ecosystem Atlas Kit (`cargo atlas`, `atlas-pack/v0`)

## Goal
Define a portable contract for publishing, checking, diffing, and consuming **evidence-backed reference stacks** for common Rust domains.

This should help answer questions like:
- what is a good starting lane for this kind of project,
- which slots and interop seams matter,
- which crates are selected and why,
- who is making the recommendation,
- how long the recommendation should be trusted,
- how overlays or org-specific deltas should be expressed,
- and what human docs or assistant contexts were derived from it.

This kit should not replace crates.io, docs.rs, blessed/unofficial directories, framework docs, or internal team standards. It should make those inputs composable, reviewable, and freshness-aware.

## References (signals)
- Rust’s vision work now explicitly recommends helping users get oriented in the crates.io ecosystem, says users lack a place to get advice on a good “starter set” of crates, and points to smoother interop plus shared building blocks as part of the answer.  
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online documentation is still the preferred canonical reference, notes increasing use of LLM tooling for learning, and shows ongoing concern about complexity and maintainer support.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io now surfaces Security-tab advisory info, Trusted Publishing controls, SLOC, and `pubtime`, which means the registry now exposes materially better recommendation inputs than it used to.  
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo’s own development updates keep emphasizing that Cargo cannot be everything to everyone and that plugins matter. That is a strong signal that “ecosystem navigation” should probably be a companion tool and artifact layer, not a demand that Cargo itself become a giant recommendation engine.  
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- Rust Foundation fellowships explicitly funded rustdoc search discoverability and crates.io search/UX work, which is a signal that discoverability/orientation is strategic project infrastructure, not incidental polish.  
  https://rustfoundation.org/media/announcing-the-rust-foundations-2024-fellows/
- Rust maintainer-fund work frames maintenance as invisible, multiplicative labor; recommendation systems that ignore maintenance reality will drift into bad guidance.  
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/
- The C++/Rust interop problem-map goal argues for creating a broad skeleton first and then prioritizing current pain, competing-solution areas, and long-lead work. That logic also fits atlas rollout: pilot a few domains well instead of pretending to solve the entire ecosystem at once.  
  https://rust-lang.github.io/rust-project-goals/2025h2/interop-problem-map.html

## Design principles
1. **Curator pluralism, not one winner.** The atlas must support multiple curator groups and multiple respectable lanes per domain.
2. **Slots, not just lists.** Good guidance names the major slots and seams, not only a bag of crate names.
3. **Evidence over vibe.** Popularity can be one signal, but the atlas must record reasons, tradeoffs, and supporting evidence.
4. **Stale until checked.** Freshness is part of the contract; old recommendations should become explicitly stale.
5. **Alternatives stay first-class.** A non-default option should remain visible with reasons.
6. **Interop is explicit.** Shared types, runtimes, adapters, and migration costs should be recorded, not implied.
7. **Commons are referenced, not reinvented.** When a neutral shared seam exists or should exist, the atlas should point to Interop Commons artifacts instead of smuggling its own hidden pseudo-standard.
8. **Derived outputs are not canonical.** Guides, templates, and assistant contexts are generated from atlas artifacts and must be traceable back.
9. **No fake universal score.** The system must not collapse into one crate-quality number.

## Artifact family
### 1. `atlas-domain/v0`
Defines the user problem space:
- domain id and summary
- success criteria / non-goals
- expected operating contexts (library, app, regulated, educational, internal-platform, etc.)
- important constraints (runtime, footprint, portability, auditability, team maturity)

### 2. `stack-lane/v0`
Defines one lane philosophy within a domain:
- lane id (`conservative`, `batteries-included`, `low-footprint`, `regulated`, `experimental`, etc.)
- optimization priorities and anti-goals
- expected operator / maintainer skill level
- explicit “why this lane exists” rationale

### 3. `stack-slot-map/v0`
Declares the main slots and selections for a lane:
- slot ids (CLI parser, error story, runtime, HTTP surface, config, logging, testing, etc.)
- selected crate(s) or crate families per slot
- required versus optional slots
- allowed alternates
- coupling notes between slots

### 4. `interop-seam-map/v0`
Records how the stack composes:
- shared types / traits / middleware seams / runtime assumptions
- expected adapter crates
- known incompatibilities or migration burdens
- `commons-pack` or `interop-seam` references when a neutral shared building block exists
- “blessed common ground” notes where a shared building block matters more than a full framework choice

### 5. `selection-evidence/v0`
Explains why a choice is present:
- supporting signals used (maintenance, security, support envelope, docs, MSRV, interop fit, footprint, maturity)
- explicit tradeoffs accepted
- non-claims
- date/version scope for the evidence

### 6. `alternative-set/v0`
Keeps alternatives visible:
- alternatives for a slot or whole lane
- where they outperform the default
- why they are not the default here
- migration burden from the default
- whether they should be modeled as a different lane instead

### 7. `curator-record/v0`
Makes curation provenance reviewable:
- curator identity (person, team, org, working group)
- stewardship model
- disclosure / conflict notes where relevant
- escalation or review path

### 8. `freshness-budget/v0`
Defines recommendation freshness:
- normal re-check interval
- early invalidation triggers (new advisory, archive/unmaintained signal, major runtime break, docs rot, MSRV shift, ownership change)
- required checks to renew freshness

### 9. `atlas-overlay/v0`
Describes local variation without forking the base atlas:
- base lane reference
- allowed substitutions / forbidden selections
- org or product-specific constraints
- local evidence additions
- expiration / review owner

### 10. `atlas-check-report/v0`
Records what was re-checked:
- registry / advisory / maintenance / docs / support / interop checks run
- drift detected
- skipped or unavailable checks
- stale status if budget expired

### 11. `atlas-pack/v0`
Bundle for durable consumption:
- canonical artifact set
- rendered summaries
- optional template scaffolds
- optional bounded `assistant-context/v0` outputs derived from the canonical artifacts
- optional pointers to semantic-context or commons artifacts used during derivation

## Execution note: atlas should launch as a ranked pilot program
The atlas should not try to curate all of Rust in its first serious incarnation. The highest-confidence path is a **pilot program** that chooses a few domains where choice pressure is high, multiple respectable lanes exist, shared seams can be named, and freshness can be tested honestly.

Recommended opening order:
1. CLI / command applications
2. HTTP / service backends
3. client apps / shell-heavy desktop-mobile lanes
4. safety-oriented internal tools
5. Wasm component / plugin host surfaces

That sequencing lets atlas prove three hard things early: it can support multiple lanes, point to real Interop Commons seams where they exist, and keep conservative/high-trust guidance distinct from popularity-driven defaults. See [`design/atlas-pilot-program.md`](./atlas-pilot-program.md) for the concrete pilot-artifact and scorecard layer.

## Candidate CLI shape
- `cargo atlas query`
- `cargo atlas explain`
- `cargo atlas check`
- `cargo atlas diff`
- `cargo atlas overlay`
- `cargo atlas render-guide`
- `cargo atlas render-assistant-context`
- `cargo atlas pack`

## How it would work in practice
### CLI domain
A CLI atlas could expose:
- a conservative lane around `clap`, `thiserror`, `tracing`, `camino`-style path posture, and low-surprise testing/reporting choices;
- a richer terminal lane with Ratatui/crossterm-oriented slots;
- explicit compile-time, cross-platform, and Unicode/rendering caveats;
- and pointers to shared terminal/command seams where they exist rather than burying them inside prose.

### Web service domain
A service atlas could expose:
- an `axum`/`tower` lane,
- a lower-level hyper-centric lane,
- explicit slots for runtime, HTTP types, tracing, auth, config, migrations, and schema/reporting,
- interop notes that say what really composes versus what merely coexists,
- and direct references to neutral commons such as `http`/Tower-style seams when those are the real leverage points.

### Safety-oriented internal tool lane
A regulated lane could:
- prefer fewer dependencies,
- weight maintenance/support evidence more heavily,
- point to Trust Signals / Lifecycle Ledger / Support Envelope / Safety Evidence artifacts,
- and explain why some popular choices are not default.

### Assistant integration
A derived assistant context should:
- be bounded in size,
- cite the lane and freshness status,
- expose slots + defaults + alternatives + important caveats,
- say which claims come from atlas artifacts versus imported commons/support/trust inputs,
- and avoid inventing recommendations that are not present in the canonical atlas artifacts.

## Adapters worth building first
- crates.io metadata and index `pubtime`
- crates.io Security tab presence
- Trusted Publishing posture
- docs.rs availability/build status
- Lifecycle Ledger artifacts
- Trust Signals artifacts
- Support Envelope artifacts
- Interop Commons artifacts (`interop-seam`, `commons-pack`) where shared seams exist
- community-curation import adapters (Blessed.rs / topic maps / org-local atlases) with explicit provenance labels

## Suggested phased execution
### Phase 1: Atlas core
- lock down domain / lane / slot / evidence / freshness artifacts
- ship one CLI domain and one web-service domain
- prove freshness and overlay handling

### Phase 2: Commons-aware atlas
- require interop seams to be named explicitly
- point to existing `http`/Tower-style shared layers where they exist
- record where missing commons are the real blocker instead of pretending the lane is fully coherent

### Phase 3: Tool-facing derivations
- emit bounded assistant contexts
- emit starter templates with provenance
- emit org overlays and drift reports

The key strategic point is that Atlas should become the **navigation layer** over the ecosystem, not a hidden ranking engine.

## Non-goals
This kit should **not**:
- become one official global crate leaderboard;
- replace crates.io search infrastructure;
- hide political subjectivity behind a fake objective score;
- turn generated prose or LLM output into canonical truth;
- absorb the deeper technical ownership of domain kits;
- or silently create pseudo-standards that should instead be expressed as Interop Commons artifacts.

## Overlap boundaries
- **Interop Commons Kit** owns shared building blocks and adoption/stewardship of cross-ecosystem seams.
- **Semantic Context Kit** owns machine-usable merged semantic inputs, not recommendation policy.
- **Trust Signals Kit** owns portable trust evidence.
- **Lifecycle Ledger Kit** owns lifecycle intent and succession truth.
- **Support Envelope Kit** owns support claims.
- **Policy Kit** owns org policy evaluation.
- **Public API / Runtime Capability / Service / Client App / Protocol / Database / Terminal / other domain kits** own deeper technical surfaces that Atlas references but does not replace.

Ecosystem Atlas Kit exists because **orientation itself** is a real ecosystem substrate. Rust’s problem is no longer that there are no good crates; it is that the ecosystem still lacks a first-class, reviewable way to publish “good starting lanes” without pretending one answer fits everyone.
