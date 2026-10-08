## Operating-surface addendum (rev0491)
This note now has a direct companion for the next construction question.
When the user asks not only **how the repo should keep growing**, but also **what common operator grammar the strongest seams should share so the archive composes as a family in theory and in practice**, read `design/epic-contribution-operating-surface-2026Q1.md` immediately after this note.

Interpretation rule:
- the buildout order in this note is unchanged;
- the new note owns the sharper **shared operating-surface / repeated receipt-role / negative-state** layer, not a new buildout rerank.

# Design: Epic contribution worthy repo buildout (2026Q1)

## Goal
The archive already knows the broad ladder, the live packet posture, the first-build kernels, the first slices, the first contracts, witness packs, fixture packs, and schema packs.
What it still lacked was one explicit note for the next recurrent maintainer question:

> if we keep researching online, keep refining the map of what Rust is still missing, and keep constructing a repo worthy of the problem, what should the strongest contributions look like next **in theory and in practice**, what fresh side-bets should be folded under stronger parents, and what repo shape keeps the work compounding instead of fragmenting?

This note is a **repo-buildout order + theory/practice deepening + elimination/folding** pass.
It does **not** rewrite the broad ladder.
It does **not** promote a new frontier.
It exists so the archive can keep growing without mistaking every fresh upstream signal for a new top-band seam.

Read with:
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `meta/WORTHY_REPO_BUILDOUT_PROTOCOL.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Why a buildout note is merited now
The latest official Rust signals do not really say “invent five new top-band seams.”
They say something harder and more useful:
- Cargo is moving toward recorded build facts and `cargo report`-style machine-usable surfaces.
- crates.io is surfacing more boundary-state truth directly in the service and tightening publishing posture.
- project leadership is explicitly naming capability analysis, vulnerability surfacing, and interop mapping as current work rather than speculative dreams.
- debugger support still fails the “first-class across tuples” bar.
- safety-critical work still needs shared readiness, evidence slots, and lifecycle discipline.
- docs, editor assistance, and LLM-mediated learning are rising together, which increases the cost of archive amnesia and shape drift.

That is a recipe for a **worthy repo**, not just a worthy idea.
A worthy repo should:
- keep the strongest seams deep and stewardable;
- fold fresh side-bets under the right parents instead of exploding the ranking surface;
- say what a contribution should import, emit, refuse, and hand off;
- and keep archive hygiene strong enough that future assistants do not re-fragment the territory.

## Fresh signals that change the practical shape more than the ranking
The January/February 2026 Project Director update is especially useful because it turns several previously diffuse ideas into concrete fold-in signals.
It says the ecosystem now has `cargo-capslock` as a static and runtime capability-analysis tool, says vulnerability surfacing is now live on the crates.io Security tab, and says the newly accepted Rust Interop Initiative is mapping today’s interop story and producing a roadmap.
That is evidence for **stronger practical hooks** inside package-intake and safety-critical work, not proof that separate new top-band seams have earned independence.
https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/

Cargo’s build-analysis and build-dir-layout work still say the clearest missing thing is machine-usable build evidence rather than wrapper empires.
The 1.94 cycle update makes that more practical by naming `cargo report timings`, `cargo report rebuild`, and `cargo report sessions` work explicitly.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
https://blog.rust-lang.org/inside-rust/2026/02/15/this-development-cycle-in-cargo-1.94/

crates.io’s 2026 development update and the March 2026 Cargo advisory reinforce the package boundary story: there is now more service-level truth, but real intake, quarantine, waiver, route, and incident-drill work still belongs in a review layer above raw service events.
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

The libtest JSON goal and docs.rs rustdoc JSON support matter for a different reason: they show that several missing seams now have stronger machine-readable imports than they used to.
Those imports still do not define the contributions by themselves, but they make a bounded repo more believable.
https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
https://docs.rs/about/rustdoc-json

## Headline answer
The worthy repo should now deepen the strongest seams in this practical order:

1. **Build-State Evidence**
2. **Package Intake + Release Boundary Review**
3. **Feedback / Debug Acceptance Commons**
4. **Safety-Critical + Institutional Readiness Commons**
5. **Compatibility Claims**
6. **Tooling Contract / Semantic Context substrate**
7. **Adoption Navigation + Ecosystem Atlas**

That is **not** the same thing as the broad strategic ladder.
It is the archive’s best answer to:
- what should get the most detailed repo buildout next;
- what should absorb fresh upstream hooks right away;
- and what should remain strategically important without expanding the current kernel surface.

## The worthy-repo buildout order

### 1) Build-State Evidence should be the repo’s deepest first-class product surface
In theory, this contribution answers:
- what built;
- why it rebuilt;
- which resource/time/cache/layout facts explain the result;
- what changed since the last known-good state; and
- what evidence is still missing because an import is unstable, lossy, or unavailable.

In practice, the repo should keep making this seam look like:
- one portable `build-state-pack/v0` family;
- imports from `cargo report`-style outputs, timings, sessions, rebuild reasons, and structured logging rather than `target/` archaeology;
- `capture`, `explain`, `diff`, `doctor`, and `renewal` commands or equivalent contract surfaces;
- explicit unsupported-state receipts;
- exports consumable by CI, local support, IDEs, issue filing, package review, and debug handoff.

Features a serious implementation should eventually cover:
- workspace/session identity;
- target-dir/layout posture and cross-workspace cache facts;
- rebuild-reason trees or receipts;
- linker and codegen timing visibility;
- cache invalidation and contention diagnosis;
- stable and unstable import provenance;
- diffing between “fast enough” and “why is this rebuilding?” sessions.

Wrong shapes to keep refusing:
- a hidden daemon that becomes the real build system;
- a score dashboard with weak forensic value;
- a cache platform that treats evidence as a feature instead of the product.

### 2) Package Intake + Release Boundary Review should absorb capability analysis and service truth
In theory, this contribution answers:
- what package or release candidate is being admitted;
- from which route and with what publishing posture;
- what scripts, capabilities, advisories, waivers, quarantine actions, and drills apply;
- and what remains unknown or route-specific.

In practice, the repo should now model this seam as:
- route profiles;
- intake receipts;
- waiver, quarantine, and incident-drill reports;
- alternate-registry and mirror posture;
- capability imports from `cargo-capslock`-style analysis;
- vulnerability imports from RustSec and crates.io service surfaces;
- release-boundary links to semver/public-API review rather than a separate orphan publish tool.

Features a serious implementation should eventually cover:
- static and runtime capability classes;
- build-script and proc-macro exposure;
- trusted publishing posture and blocked-trigger state;
- advisory age, scope, and remediation posture;
- waiver expiration and reviewer identity;
- route-specific caveats for alternate registries and internal mirrors;
- drill receipts that prove teams can respond instead of only watch dashboards.

Wrong shapes to keep refusing:
- a universal package-trust score;
- a hosted portal that hides unknowns behind a green check;
- a separate “capability analysis commons” seam that forgets the decision point is package admission.

### 3) Feedback / Debug Acceptance Commons should become the strongest tuple-acceptance layer
In theory, this contribution answers:
- which debugger/runtime/OS/toolchain/program tuples are known-good, caveated, regressed, or unsupported;
- what replay evidence exists;
- and what developers, maintainers, docs authors, or tool builders can honestly claim today.

In practice, the repo should keep shaping this seam as:
- debugger tuple profiles;
- session packs and replay results;
- async-debug acceptance lanes;
- visualizer and expression-evaluation receipts;
- imports from build-state evidence, libtest JSON, and machine-readable test/session outputs;
- exports for support, issue filing, docs, and compatibility claims.

Features a serious implementation should eventually cover:
- debugger version and OS tuple matrices;
- async task/frame visibility;
- pretty-printer / visualizer availability;
- expression evaluation posture;
- attachable minimal repros and replay receipts;
- evidence of what changed between toolchain or debugger upgrades.

Wrong shapes to keep refusing:
- one IDE integration marketed as ecosystem closure;
- one debugger fork sold as the whole answer;
- a test-result format pretending to be the full acceptance commons.

### 4) Safety-Critical + Institutional Readiness Commons should stay program-shaped
In theory, this contribution answers:
- what readiness claims a target, stack, runtime, or organizational lane can honestly make;
- what evidence backs those claims;
- what lifecycle or replacement playbooks exist;
- and what interop boundaries, qualification requirements, and stewardship commitments remain unresolved.

In practice, the repo should keep shaping this seam as:
- readiness cards and packs;
- dependency lifecycle and replacement playbooks;
- target-tier and MSRV discipline lanes;
- async/runtime qualification requirement bundles instead of one blessed runtime;
- interop/FFI evidence maps that can import current work from the Rust Interop Initiative;
- attachable evidence from package review, compatibility, build-state, and debug layers.

Features a serious implementation should eventually cover:
- evidence slots for MC/DC, coverage, traceability, and toolchain constraints;
- target and environment assumptions;
- renewal cadence and stale-card receipts;
- required human sign-off and program governance;
- interop boundary classifications and audit posture.

Wrong shapes to keep refusing:
- “certified Rust” language without domain-specific receipts;
- a vendor-owned readiness portal sold as a commons;
- a separate “interop seam” that forgets interop matters because it changes high-assurance readiness.

### 5) Compatibility Claims should deepen as a routing layer, not a badge farm
In theory, this contribution answers whether a claim about support, MSRV, target posture, public API, debugger tuple, or docs/build assumptions is actually backed by evidence.

In practice, this seam should look like:
- explicit claim families;
- imports from build-state, package-intake, debug-acceptance, docs.rs/rustdoc JSON, and public-API/semver evidence;
- drift receipts and recheck triggers;
- release-boundary hooks that can absorb publish-time semver checks without turning into the full package-intake layer.

This is the right home for fresh semver/publish signals.
It is the wrong place to create one more free-floating “release correctness framework.”

### 6) Tooling Contract / Semantic Context remains a substrate, not the user-visible center
This seam matters because whole classes of honest tools depend on machine-usable surfaces.
The repo should keep treating it as a substrate fed by:
- Cargo report and metadata surfaces;
- libtest JSON;
- rustc JSON output;
- docs.rs rustdoc JSON;
- and any future public semantic/context contracts.

The right repo move is to bind those imports into stronger parents.
The wrong repo move is to mistake a semantic substrate for a standalone ecosystem answer unless and until it begins solving distinct operator pain on its own.

### 7) Adoption Navigation + Ecosystem Atlas should remain strategically huge but buildout-constrained
This seam still matters because crate choice, framework maturity, defaults, and recommendation drift remain expensive.
But the repo should keep its current discipline:
- continue atlas/default/renewal work only where it sharpens stronger parent seams;
- do not widen recommendation surfaces faster than the archive can renew them;
- and keep explicit receipts for freshness, derivation, and editorial burden.

## What should be folded instead of promoted
The buildout pass is strongest when it eliminates unnecessary seam proliferation.
Right now the archive should explicitly fold these fresh or tempting side-bets under stronger parents:

- **Capability analysis** folds under **Package Intake + Release Boundary Review**.
  It matters because it changes admission and waiver decisions.
- **Publish-time semver enforcement** folds under **Compatibility Claims** and the **release boundary** portion of package review.
  It matters because claims and releases need evidence, not because it deserves a separate empire.
- **libtest JSON** folds under **Feedback / Debug Acceptance** and **Tooling Contract**.
  It is a machine-readable import, not a new user-facing seam.
- **docs.rs modernization / rustdoc JSON availability** folds under **Compatibility Claims**, **Tooling Contract**, and selected **Navigation** work.
  It strengthens imports and docs truth; it does not automatically become an independent epic.
- **Interop mapping** folds under **Safety-Critical + Institutional Readiness Commons**.
  It matters because interop truth changes assurance posture and qualification arguments.

## What a worthy repo should add next
After this pass, future repo construction should prefer artifacts that make the strongest seams more evaluable instead of more atmospheric.
Good next additions would look like:
- program briefs that say steward model, proof burden, and refusal shape for each top seam;
- more explicit import/export maps for build-state, package-intake, debug, and readiness layers;
- scenario families that connect package review, build evidence, and debug acceptance instead of isolating them;
- refresh packets for current live posture when upstream work materially changes; and
- more source-atlas cards whenever one official source becomes a recurring anchor for practical shape decisions.

## Why this file exists
The archive already knew what seemed broadly worthy.
What it still needed was a way to keep continuing research and continuing repo construction pointed at the same few serious seams, while resisting the temptation to turn every new upstream tool, report, or service change into its own top-level dream.
