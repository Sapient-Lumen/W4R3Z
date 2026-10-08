# Design: Epic contribution operating surface (2026Q1)

## Goal
The archive already has the broad ladder, the live packet posture, the buildout order, the first kernels, the first contracts, witness packs, fixture packs, and schema packs.
What it still lacked was one explicit answer to the next implementation-family question:

> if the strongest worthy contributions are going to be built as a family rather than as seven separate dialects, what common operating surface should they expose in theory and in practice, what verbs and receipts should repeat across them, and what wrong shapes should be refused before the repo multiplies local grammars?

This note is an **operating-surface + control-grammar + artifact-role** pass.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It exists so the repo can keep compounding as a stewardable family of contributions rather than as a stack of unrelated excellent memos.

Read with:
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- the strongest current execution blueprints (`build-state-evidence`, `package-intake-gateway`, `feedback-loop-debuggability`, `safety-critical-readiness`, `compatibility-claims`, `tooling-contract`, `adoption-navigation`)
- `meta/OPERATING_SURFACE_PROTOCOL.md`
- `meta/WORTHY_REPO_BUILDOUT_PROTOCOL.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Why this layer is merited now
The latest official Rust signals still do not really say “the missing thing is one more framework.”
They say something more operational:
- Cargo build analysis is converging on recorded build facts and `cargo report`-style review commands.
- Cargo’s external-tools surface still treats custom subcommands, `cargo metadata`, and structured JSON streams as the intended extension path.
- `cargo clippy` still demonstrates a real middle shape: toolchain-distributed reach without pretending the feature lives in Cargo core.
- libtest JSON and docs.rs rustdoc JSON reinforce that machine-usable evidence layers are strategically important even when they are not the user-facing product themselves.
- crates.io keeps surfacing more service truth, but that truth still needs an intake/review surface above raw registry events.
- project/program leadership is explicitly naming capability analysis, interop, industrial adoption, and roadmap/application-area work as practical ecosystem priorities.
- the public “Rust challenges” writeup had to be rewritten after an earlier LLM-shaped version felt empty, which is a direct warning against archive prose that is not pinned to concrete verbs, receipts, and evidence-bearing interfaces.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-clippy.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://docs.rs/about/rustdoc-json
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/inside-rust/2026/03/25/project-director-update/
- https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/12/03/lessons-learned-from-the-rust-vision-doc-process/

## Headline answer
The repo should now standardize a **shared operator grammar** across its strongest worthy contributions.
Not one binary.
Not one hosted control plane.
Not one fake universal trust score.
A shared grammar.

That grammar should answer, for every serious seam:
1. **how an operator inspects or imports state**;
2. **how the tool captures and reports evidence**;
3. **how it explains or diffs change**;
4. **how it verifies, reviews, or waives a claim**;
5. **how it emits negative-state receipts** when truth is stale, unsupported, incomplete, experimental, route-specific, or untrusted; and
6. **how its outputs remain attachable to program, CI, or institutional workflows without requiring a central platform first**.

The archive should therefore treat the next worthy layer as a common family of verbs and receipt classes.
The immediate design target is not “build everything together.”
It is “make the best candidates feel interoperable, reviewable, and comparable because they speak a visibly related operator language.”

## Rank the missing operating-surface needs
These are the highest-value missing operating-surface moves, ranked by how much they would make the current top seams more stewardable in practice.

### 1. Shared report / diff / explain verbs
This is the most important common layer.
The build-analysis work is already moving toward `cargo report timings`, `cargo report rebuild`, and `cargo report sessions` patterns.
That should be treated as a family clue, not just a build-only clue.

What the repo should want:
- `report` for current state or summarized receipts;
- `diff` for comparison against a baseline, previous run, route, release, environment, or claim;
- `explain` for causal attribution rather than raw logs;
- stable receipt formats that survive CLI/UI reshaping.

Why first:
- Build-State Evidence needs this now.
- Compatibility Claims needs this immediately after.
- Debug Acceptance and Safety Readiness both benefit from compare/explain output rather than prose verdicts.

### 2. Negative-state receipt discipline
A worthy family must say “unknown”, “stale”, “unsupported”, “experimental”, “route-specific”, “waived”, and “degraded” in the same broad way across seams.
This is more important than a flashy happy path.

What the repo should want:
- explicit receipt kinds for unsupported or partial truth;
- expiration/renewal markers;
- provenance fields that distinguish imported upstream evidence from locally derived claims;
- refusal posture that prevents false closure.

Why second:
- Package Intake and Safety Readiness break without it.
- Debug tuple claims and compatibility claims become misleading without it.
- It is the cleanest antidote to LLM smoothing and archive amnesia.

### 3. Review / admit / quarantine / waive boundary grammar
The package-intake seam already wants a real boundary review surface, not just alerts.
But the deeper win is that the archive can reuse this grammar more widely: claim acceptance, readiness exceptions, experimental path allowances, and local institutional policy overlays all want related verbs.

What the repo should want:
- `review` for human/operator inspection;
- `admit` for allowed entry under known conditions;
- `quarantine` for bounded non-admission;
- `waive` for explicit, reviewable exception paths;
- `recheck` for renewal or expiry-triggered reevaluation.

Why third:
- It immediately strengthens Package Intake.
- It creates a reusable policy edge for Safety Readiness and Compatibility Claims.
- It avoids the wrong shape where every seam invents its own exception language.

### 4. Session / replay / probe grammar
The debugging seam especially needs session-aware, replayable evidence.
But build evidence and compatibility investigation also benefit from reproducible session packs and probes.

What the repo should want:
- `probe` for small bounded interrogations;
- `session` packs for captured evidence in context;
- `replay` for tuple re-execution or check re-run;
- attachable artifacts for bug reports, regressions, and institutional review.

Why fourth:
- It is critical, but less universal than report/diff/explain.
- It matters most for Debug Acceptance, then for Build-State and Compatibility.

### 5. Export / lineage / attachment grammar
The family needs one obvious answer to “what do I hand to CI, a code-review system, a bug, a compliance review, or a design note?”
That is not the same as report generation.
It is attachment and lineage.

What the repo should want:
- canonical export bundles;
- source/derivation lineage;
- compact summaries plus raw evidence handles;
- clear machine/human dual-use outputs.

Why fifth:
- It matters to all strong seams, but only after the core verbs above exist.

## The recommended shared verb family
Use these verbs as a family target.
Not every seam will expose every verb in v0, but any omission should be explicit.

### Inspect / import / discover
Pull in upstream truth or local state without inventing claims yet.
Examples:
- build metadata and build-session facts;
- registry/service data;
- rustdoc JSON;
- tuple/session capabilities;
- institutional policy overlays.

### Capture / report
Record or summarize current state in a stable, receiptable way.
Examples:
- build-session pack;
- intake receipt;
- readiness card;
- tuple card.

### Explain / diff / compare
Tell the operator what changed, why, or where the claim differs from a baseline.
Examples:
- rebuild explanation;
- compatibility diff;
- readiness drift summary;
- route delta.

### Review / admit / quarantine / waive / recheck
Model the boundary.
Examples:
- package intake review;
- policy exception handling;
- route-specific allowance;
- stale-claim recheck.

### Probe / session / replay
Model investigation, debugging, and tuple evidence.
Examples:
- debugger tuple replay;
- build probe pack;
- issue reproduction session.

### Verify / claim / renew / expire
Model long-lived assertions and their lifecycle.
Examples:
- compatibility claims;
- readiness claims;
- support-envelope cards;
- claim reissuance.

### Export / attach / lineage
Hand evidence to outside systems without losing provenance.
Examples:
- CI artifact export;
- review attachment bundle;
- human summary plus machine payload.

### Doctor / unsupported / unknown
Model negative state directly.
Examples:
- unsupported route;
- missing importer;
- stale upstream evidence;
- partially trusted registry context.

## Keep verbs separate from artifact roles
A major archive risk is mixing verbs, files, receipts, and ownership layers.
This revision should sharpen the distinction.

### Verbs are operator actions
Examples: `report`, `diff`, `review`, `waive`, `probe`, `renew`.

### Artifact roles are emitted objects
Examples:
- session pack
- review receipt
- waiver receipt
- tuple card
- readiness pack
- compatibility receipt
- stale/unsupported receipt
- lineage/export bundle

### Residency is where logic lives
Examples:
- external companion tool
- service-side feature
- toolchain-distributed optional component
- archive-only research/protocol layer

### Decision rights are who can bless the result
Examples:
- upstream Cargo team
- crates.io service owners
- debugger/toolchain owners
- institutional operator or steward
- local project/publisher owner

The repo should not let any one of these impersonate the others.

## What each top seam should look like under this family

### Build-State Evidence
The family target here is:
- `inspect/import` build metadata and session facts;
- `report` current build and cache evidence;
- `diff/explain` rebuild causes, layout drift, and contention shifts;
- `doctor` unsupported/unstable collection states;
- `export/attach` evidence packs to CI or issues.

Theory:
- machine-usable build evidence becomes a common observability substrate for Rust work.

Practice:
- companion-first CLI with stable receipt files, optional unstable enrichments, and an attachable session pack.

### Package Intake + Release Boundary Review
The family target here is:
- `discover/import` package/service/policy facts;
- `review` route-specific intake state;
- `admit/quarantine/waive` under explicit boundary conditions;
- `recheck/renew` when policy or upstream facts change;
- `export/attach` review receipts and drill artifacts.

Theory:
- the problem is not just finding facts; it is governing entry across routes and exceptions.

Practice:
- review kit above raw crates.io service data, trusted-publishing settings, advisories, capability analysis, and route profiles.

### Feedback / Debug Acceptance Commons
The family target here is:
- `probe` debugger/runtime/OS tuples;
- capture `session` evidence;
- `replay/compare` known cases;
- `report` acceptance cards;
- `doctor` unsupported tuples and missing evaluator/visualizer support.

Theory:
- debugger support becomes legible as an evidence commons rather than folklore.

Practice:
- tuple matrix plus replay packs and comparison output, not only survey rhetoric.

### Safety-Critical + Institutional Readiness Commons
The family target here is:
- `import` readiness evidence, policy overlays, lifecycle plans, and qualification-relevant notes;
- `claim/verify` readiness cards;
- `waive` or mark exceptions explicitly;
- `renew/expire` cards on schedule;
- `export/attach` packs for review.

Theory:
- this is evidence-bearing readiness governance, not one certification badge.

Practice:
- renewable cards with stale/unsupported posture first-class, plus route/institution overlays.

### Compatibility Claims
The family target here is:
- `inspect/import` support and API/interface facts;
- `claim/verify` compatibility statements;
- `diff/explain` compatibility regressions or widened support;
- `recheck/renew` over time;
- `doctor` unsupported or weakly evidenced claims.

Theory:
- compatibility should be an evidence family, not one badge.

Practice:
- compact receipts and compare output that can bind to release reviews or migration work.

### Tooling Contract / Semantic Context
The family target here is:
- `inspect/import` structured program context;
- `query/report` narrow machine-usable slices;
- `compare` API or symbol-level drift;
- `lineage/export` contexts for downstream tools or assistants.

Theory:
- this seam remains a substrate, not a user-facing empire.

Practice:
- typed importers and provenance-bearing outputs around rustdoc JSON and related machine surfaces.

### Adoption Navigation + Ecosystem Atlas
The family target here is softer but still real:
- `discover/import` current evidence and defaults;
- `report` routed briefs or fit profiles;
- `warn/doctor` where evidence is thin or stale;
- `renew` route cards over time.

Theory:
- it becomes the human-routing surface for the family.

Practice:
- do not try to universalize too early; keep it receipt-rich and scope-aware.

## What a first implementation family should share
A repo-worthy family does not require shared code first, but it should share a visible skeleton.

### 1. Subject resolver
Resolve the thing under inspection or review:
- workspace / crate / package route
- debugger tuple
- support claim target
- institutional readiness profile

### 2. Import adapters
Use primary sources and machine-facing feeds where possible:
- Cargo/build-analysis/build-session facts
- registry/service data
- rustdoc JSON
- tuple probe results
- local policy bundles

### 3. Canonical pack emitters
Emit stable receipt-like outputs with schema hygiene and provenance.

### 4. Compare/explain engines
Support baseline-vs-now, route-vs-route, release-vs-release, or tuple-vs-tuple reasoning.

### 5. Negative-state emitters
Return explicit unsupported/stale/unknown/experimental/waived receipts instead of silently falling back to prose.

### 6. Attachment/export adapters
Produce evidence bundles that external systems can consume without understanding the whole local tool.

### 7. Renewal hooks
Support recheck windows, expiry markers, and changed-upstream-source triggers.

## Strategic approaches the ecosystem is still missing
If the question is “what worthy or even epic thing is Rust still missing?”, this revision’s sharper answer is:

### Missing approach A: evidence-first companion families
Rust still lacks enough companion-first tools that expose reviewable, portable evidence surfaces rather than dashboards, wrappers, or promises.
This family should be the default strategic shape for Build-State, Package Intake, Debug Acceptance, and Compatibility Claims.

### Missing approach B: boundary-layer governance tools
The ecosystem has facts, surveys, and service features, but it still lacks enough tools that model entry, exception, and renewal boundaries directly.
That is why Package Intake and Safety Readiness remain so important.

### Missing approach C: renewable claim systems
Many Rust claims still age badly because they are asserted once and not reissued as upstream conditions change.
Compatibility and readiness work should be treated as renewable claim systems.

### Missing approach D: provenance-sensitive assistant surfaces
LLM-mediated learning is now normal enough that the ecosystem needs better provenance-bearing, machine-usable context exports.
That is still a substrate story, not a chatbot product story.

## Wrong shapes to refuse
The archive should refuse these default mistakes:
- a universal hosted control plane that tries to centralize every seam before the local receipts are mature;
- a Cargo-core maximalist story where every good companion tool is framed as incomplete until merged into Cargo;
- a single risk/trust/readiness score pretending to compress route-specific evidence into one number;
- a family of tools that share branding but not verbs, receipts, or negative-state posture;
- an LLM-generated “ecosystem summary” that does not say what can actually be imported, reported, diffed, reviewed, replayed, renewed, or attached.

## Archive decision
- The broad ladder is unchanged.
- The current packet posture is unchanged.
- The new missing layer is **shared operating surface and control grammar**.
- This layer belongs **under repo buildout and implementation-family discipline**, not as a new top-band seam.
- Future worthy-contribution deepening should prefer notes that specify **verbs, artifact roles, import surfaces, negative states, and residency shape** over notes that merely rename the same ambitions.
