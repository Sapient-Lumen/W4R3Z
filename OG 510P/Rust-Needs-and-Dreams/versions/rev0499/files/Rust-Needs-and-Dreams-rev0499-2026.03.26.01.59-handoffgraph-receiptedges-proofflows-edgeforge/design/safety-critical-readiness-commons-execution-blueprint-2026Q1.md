# Design: Safety-Critical Readiness Commons execution blueprint (2026 Q1)

## Goal
Turn one of the archive's clearest **program-shaped worthy contributions** into a sharper **buildable program**.

The missing contribution is not a certification badge, not a qualified Rust distro by itself, not one more lint bundle, and not a dashboard that flattens every high-assurance concern into green/red theater.
It is a disciplined companion layer that makes Rust's safety-critical reality **slice-aware, authority-aware, target-aware, dependency-aware, interface-aware, and reviewable** across toolchains, targets, async/runtime choices, mixed-language boundaries, and long-lived product programs.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team, consortium, lab, or funder wants to build the archive's current best safety-critical contribution, what should that project actually ship in theory and practice?

Read with:
- `design/ideal-rust-worthy-contributions-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/safety-critical-assurance-contract-2026Q1.md`
- `design/safety-critical-evidence-stack.md`
- `design/safety-critical-pilot-program.md`
- `design/native-edge-execution-blueprint-2026Q1.md`
- `design/async-capability-commons-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `proposals/epic-safety-critical-readiness-commons.md`

## Why this note is needed now
The archive already knew that **Safety-Critical Readiness Commons** mattered.
What it still lacked was a crisper answer to **what the worthy contribution should actually become**.

Fresh official and primary signals sharpen that answer:
- Rust's January 14, 2026 safety-critical writeup says the main pressure in these domains is not only language semantics but the growth of process, verification, and evidence demands with criticality; it also says teams are strongly incentivized to isolate the highest-criticality logic into the smallest surface area possible.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- That same writeup makes six concrete recommendations that already sketch the missing commons layer: support community-owned requirements, establish MSRV conventions, create target-focused readiness checklists, document dependency-lifecycle patterns, define requirements for safety-case-friendly async runtimes, and treat C/C++ interop as part of the safety story.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Rust's 2026 flagships page defines **Safety-Critical Rust** in terms of certified tooling, specifications, and evidence, with milestones for MC/DC, normative `unsafe` documentation, safety-critical lints in Clippy, and stable FLS release cadence. That is already a roadmap for reviewable readiness surfaces rather than a single feature.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The MC/DC goal says the earlier implementation was removed for maintenance reasons, says implementation outside rustc is infeasible because macro expansion makes post-expansion source reconstruction unrealistic, and now proposes a more sustainable architecture plus an explicit maintenance commitment.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- The normative-unsafe-docs goal says the Rustonomicon is incomplete, the Unsafe Code Guidelines Reference is largely abandoned, and safety-critical teams need authoritative guidance for common `unsafe` patterns drawn from real codebases.
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- The Clippy goal says safety-critical development may need 50 to 200 lints over one to two years, which is a strong signal that lint posture needs a durable home and durable review artifacts rather than bespoke side tooling.
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
- The FLS cadence goal says each FLS release should appear within six weeks of the corresponding stable Rust release so assessors and qualification consumers have a current specification surface.
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- Ferrocene's public documentation shows what real qualification boundaries look like in practice: many rustc flags are explicitly outside qualification scope, some options are only qualified in narrow forms, and experimental targets/features are shipped but not qualified for safety-critical use. That is exactly the kind of **qualified-scope truth** the ecosystem still lacks as a shared commons surface.
  https://public-docs.ferrocene.dev/main/user-manual/rustc/cli.html
  https://public-docs.ferrocene.dev/main/release-notes/25.11.0.html

Taken together, those signals say the archive should stop describing the safety-critical opportunity only as an evidence stack or assurance pack.
It should describe a real contribution shape.

## Headline answer
If one serious team or coalition wants to build the archive's strongest safety-critical contribution, the answer should now be:

> Build a **Safety-Critical Readiness Commons** that preserves critical-slice identity, authority/spec posture, qualified-scope truth, target/runtime readiness, dependency lifecycle posture, interface/interop posture, and evidence/waiver truth, then emits reviewable packs and handoffs for engineers, assessors, maintainers, and downstream integrators.

That answer is deliberately narrower than “make Rust certified”.
It is also deliberately stronger than “improve safety tooling”.

## What this contribution should be in theory

### Core thesis
A safety-readiness commons becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what critical slice or slice family is under review;**
2. **which authorities and requirement profiles govern that slice;**
3. **which part of the toolchain/command/target surface is actually within qualified or reviewable scope;**
4. **what target, runtime, and async posture are being assumed;**
5. **what dependency lifecycle and package-intake posture apply to the slice;**
6. **what mixed-language or interface boundaries are in play;**
7. **what evidence lanes ran, what residue remains, and what downstream consumers may honestly conclude.**

If a project cannot answer those questions without spreadsheets, hallway lore, vendor PDFs, and ad hoc assessor notes, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable readiness review**.

It should include:
- critical-slice identity;
- authority and requirement profiles;
- qualified-scope truth for toolchain / target / runtime / command posture;
- dependency-lifecycle and intake posture;
- interface / interop posture;
- evidence and waiver imports;
- consumer-specific handoffs.

It should not become:
- a universal certification generator;
- one vendor's distribution strategy presented as the entire answer;
- a badge site that hides unsupported areas;
- or a policy engine that pretends qualification is binary.

### Separation rule
The contribution must preserve at least seven distinct truth classes:
- **critical-slice truth** — what crate/module/binary/target/release slice or slice family is under review;
- **authority truth** — which requirements cite Rust Reference, std docs, FLS, normative unsafe docs, local rationale, coding rules, or project policy;
- **qualified-scope truth** — which compiler flags, cargo commands, targets, runtimes, and optional tools are within scope, out of scope, preview-only, or locally justified;
- **target/runtime truth** — which targets, OS/SDK bindings, scheduler/runtime assumptions, and async caveats are actually part of the readiness claim;
- **dependency lifecycle truth** — what crates are provisional, internalized, frozen, mirrored, replaced later, or forbidden in higher-criticality slices;
- **interface truth** — what C/C++/SDK/shared-memory/binding boundaries exist and what keeps them auditable;
- **evidence/consumer truth** — what evidence packs, waivers, residues, and downstream conclusions are allowed.

Without those separations, “Rust for safety-critical” turns into qualification theater.

### Shape rule
This contribution should begin as a **stewarded program + readiness commons + profile/acceptance corpus + report/pack command**.
That means:
- a **stewarded program** for requirement gathering, maintenance commitment, and renewal;
- a **commons** for reusable readiness profiles and qualified-scope vocabulary;
- a **profile / acceptance corpus** for real targets, toolchain profiles, dependency postures, and mixed-language boundaries;
- and a thin **command / pack layer** that imports evidence rather than replacing evidence tools.

It should not begin as a giant service, universal certification product, or mega-schema that tries to freeze every domain standard into Rust-owned ontology.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo readiness-critical scope`
- `cargo readiness-critical target`
- `cargo readiness-critical deps`
- `cargo readiness-critical boundary`
- `cargo readiness-critical assurance`
- `cargo readiness-critical diff`
- `cargo readiness-critical export --consumer <engineering|release|audit|qualification-prep|support>`
- `cargo readiness-critical pack`

The tool should **import** established evidence and vendor/project facts where possible rather than pretending it owns execution, verification, or certification.

### Public artifact spine

#### Imported/internal families
- `critical-slice-profile/v0`
- `safety-authority-profile/v0`
- `qualified-scope-profile/v0`
- `target-readiness-profile/v0`
- `dependency-lifecycle-profile/v0`
- `interface-boundary-profile/v0`
- `safety-assurance-import-index/v0`
- `readiness-waiver-ledger/v0`
- optional async/runtime, package-intake, maintenance, or distribution attachments

#### Public review families
- `safety-readiness-brief/v0`
- `safety-readiness-diff/v0`
- `safety-readiness-pack/v0`
- `safety-readiness-handoff/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — workspace/crate/binary/target/profile/features/toolchain/runtime/environment and release identity;
- **authority posture** — normative, project-policy, imported-vendor, inferred, unresolved, or local-rationale;
- **qualified-scope posture** — in-scope, out-of-scope, preview-only, experimental, or locally-justified;
- **target/runtime anchors** — target triple, OS/SDK version, `std`/`no_std`, async runtime assumptions, timing/scheduler caveats;
- **dependency anchors** — third-party/provisional/internalized/replacement-planned/mirrored/frozen/forbidden posture;
- **boundary anchors** — FFI/shared-memory/generated-binding/layout/ABI/process-boundary assumptions;
- **evidence anchors** — attached assurance/coverage/sanitizer/verification/conformance/package-intake/maintenance artifacts;
- **consumer limits** — what engineering, release, audit, or qualification-prep consumers may and may not claim.

## Commands and what they should emit

### `cargo readiness-critical scope`
Purpose:
- declare the critical slice;
- attach authority sources and requirement profile;
- emit `critical-slice-profile/v0`, `safety-authority-profile/v0`, and `qualified-scope-profile/v0`.

Important rule:
- toolchain or target scope must be explicit; do not let “uses Rust 1.x” impersonate a qualified command/flag/target posture.

### `cargo readiness-critical target`
Purpose:
- publish target class posture, OS/SDK binding assumptions, FLS/spec alignment, and runtime/async caveats;
- emit `target-readiness-profile/v0`.

Important rule:
- target tier, target availability, and target readiness are not interchangeable.

### `cargo readiness-critical deps`
Purpose:
- publish how dependencies are used across criticality levels;
- emit `dependency-lifecycle-profile/v0`.

Important rule:
- a dependency used in QM or prototype phases is not automatically acceptable in higher-integrity slices.

### `cargo readiness-critical boundary`
Purpose:
- record mixed-language and interface boundary posture;
- emit `interface-boundary-profile/v0`.

Important rule:
- “has bindings” is not the same fact as “has an auditable long-lived interop boundary”.

### `cargo readiness-critical assurance`
Purpose:
- import the existing assurance/evidence families under one readiness-oriented review boundary;
- emit `safety-assurance-import-index/v0`, `readiness-waiver-ledger/v0`, and `safety-readiness-brief/v0`.

Important rule:
- the readiness commons should import `assurance-pack` / `safety-pack` style evidence without flattening criterion, proof, waiver, or unsupported-state truth.

### `cargo readiness-critical diff`
Purpose:
- compare two readiness packs while preserving the difference between:
  - newly in-scope or out-of-scope toolchain surfaces,
  - newly supported or degraded targets,
  - changed dependency posture,
  - changed interface risk,
  - and changed evidence/waiver state.

### `cargo readiness-critical export`
Purpose:
- emit smaller consumer handoffs for engineering review, release review, audit prep, or qualification prep without making those slices canonical by themselves.

## Ranked feature set

### P0 — required for a worthy v0
- preserve critical-slice, authority, and qualified-scope truth explicitly;
- support one target-readiness profile lane;
- support one dependency-lifecycle lane;
- support one mixed-language/interface boundary lane;
- import the current assurance/evidence packs without flattening them;
- emit one portable brief plus one portable pack;
- surface `partial`, `unsupported`, `preview`, `out-of-scope`, and `waived` honestly.

### P1 — strong near-term extensions
- import FLS cadence/spec freshness posture and normative-unsafe-doc coverage posture;
- import async/runtime qualification caveats from Async Capability Commons rather than re-describing them ad hoc;
- import Package Intake Gateway artifacts for vendoring/mirroring/approval posture;
- import Maintainer Reality artifacts where long-lived stewardship is part of qualification risk.

### P2 — do later or fold elsewhere
- global badge programs;
- one-number readiness scores;
- hosted assessor portals before local truth exists;
- cross-domain compliance automation that claims to replace local standards work.

## Pilot lanes that best prove the idea

### 1) Target-readiness profile pilot
Prove:
- that a target-focused readiness checklist can be built from real target, SDK, and qualified-scope facts;
- that it distinguishes availability, readiness, and qualification posture;
- that it can emit a bounded handoff usable by an engineering or assessor-facing team.

### 2) Dependency-lifecycle pilot
Prove:
- that the commons can publish the real “use crates early, narrow or replace later” pattern without hand-waving;
- that it can separate prototype/QM posture from higher-criticality posture;
- that it composes with package-intake truth rather than duplicating it.

### 3) Mixed-language boundary pilot
Prove:
- that the commons can make C/C++/SDK/shared-memory boundaries auditable;
- that it can preserve generated-binding, ABI/layout, and shared-memory assumptions explicitly;
- that it works as a long-lived boundary story rather than one demo binding run.

### 4) Async/runtime caveat pilot
Prove:
- that the commons can say “watch” or “requirements still undefined” when async/runtime qualification is not ready;
- that it can import runtime/process-artifact expectations cleanly;
- and that it can distinguish language progress from readiness claims.

### 5) Assurance-import pilot
Prove:
- that `safety-critical-assurance-contract-2026Q1.md` remains a vital substrate but not the whole story;
- that evidence/waiver truth can be imported under slice/target/dependency/boundary posture;
- and that downstream consumers receive one honest readiness handoff instead of separate binders.

## What this contribution should import instead of reinventing
- **Safety-Critical Assurance Contract** for composed evidence and waiver truth.
- **Package Intake Gateway** for ingress, extraction, staging, mirroring, and policy-visible dependency posture.
- **Async Capability Commons** for runtime, capability, and adapter truth where async enters the critical slice.
- **Native Edge Contract** for mixed-language/build-boundary and SDK realities.
- **Maintainer Reality / Keystone Stewardship** for continuity risk where long-lived support posture matters.

This is not a weakness.
It is the reason the commons can stay honest and small enough to steward.

## Ranking decision
This promotion **does not** rewrite the broad ecosystem ladder.
It does **not** outrank Build-State Evidence, Feedback Loop, Semantic Context, Package Intake, or Migration as broad ecosystem bets.

What changes is the ideal-Rust and specialist map:
- the archive now has a clearly named **safety-critical readiness execution blueprint**;
- that blueprint is stronger than leaving safety-critical work split between evidence, target notes, async caveats, dependency lore, and interop anecdotes;
- and the sharper answer is now **stewarded program + readiness commons + profile/acceptance corpus + report/pack command** rather than one evidence stack or one qualified toolchain story.

## Anti-goals
Do not turn this into:
- a universal compliance dossier generator;
- a “Rust is certified” marketing surface;
- a distro-comparison dashboard;
- an attempt to standardize every domain's assurance process inside one Rust repo;
- or a substitute for local assessors, standards experts, or project-specific safety cases.

The winning contribution is a **reviewable readiness commons**, not a qualification theater machine.
