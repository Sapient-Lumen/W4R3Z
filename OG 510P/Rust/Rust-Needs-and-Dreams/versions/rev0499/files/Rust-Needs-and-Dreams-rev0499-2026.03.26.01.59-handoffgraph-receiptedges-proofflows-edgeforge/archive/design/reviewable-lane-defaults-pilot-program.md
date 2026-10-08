# Design: Reviewable Lane Defaults pilot program

## Goal
Prove that Rust can publish **reusable scoped defaults** for recurring project classes without collapsing back into either of the two bad extremes:
- a neutral registry that refuses to say anything actionable; or
- a hidden blessing system that turns one recommendation into ecosystem dogma.

This pilot exists because the archive now has a strong **Adoption Navigation Bundle**, but it still needs the layer that answers:
> for this recurring project class, risk posture, team profile, and runtime family, what is the reusable default lane we are prepared to recommend right now, with alternatives, freshness, and bounded handoffs?

Read with:
- [`design/reviewable-lane-defaults.md`](./reviewable-lane-defaults.md)
- [`design/adoption-navigation-bundle.md`](./adoption-navigation-bundle.md)
- [`design/recommendation-posture-ladder.md`](./recommendation-posture-ladder.md)
- [`design/ecosystem-atlas-kit.md`](./ecosystem-atlas-kit.md)
- [`design/adoption-decision-stack.md`](./adoption-decision-stack.md)
- [`design/profiled-onramp-stack.md`](./profiled-onramp-stack.md)
- [`design/project-bootstrap-stack.md`](./project-bootstrap-stack.md)
- [`design/institutional-overlay-stack.md`](./institutional-overlay-stack.md)

## Why pilot this now
The official Rust signals are unusually aligned around a scoped-defaults seam:
- Rust’s March 20, 2026 challenges post says ecosystem navigation still suffers from **choice paralysis**, **tacit knowledge**, and uneven domain maturity.
- Rust’s December 2025 vision work says users need help getting oriented in crates.io and finding a good “starter set” of crates, while also noting the political risk of blessing crates too broadly.
- The 2025 State of Rust survey says online docs remain the canonical reference while learning and editor behavior continue shifting toward LLM/editor mediation.
- crates.io’s January 2026 update added `pubtime`, SLOC, and a docs.rs source link, making refresh and review inputs better than they used to be.
- Cargo’s February 2026 development-cycle note says Cargo cannot be everything to everyone and explicitly celebrates plugins, which argues for a companion layer rather than a cargo-core recommendation engine.
- The Rust Foundation’s 2026–2028 strategy pairs stable infrastructure, sustainable maintenance, and adoption growth, which means recommendation defaults are now ecosystem infrastructure rather than only community curation.

Those signals imply a specific next step.
The archive should not jump straight from **candidate space** to **project-specific briefs** every single time.
It should prove a reusable middle layer first.

## Candidate artifact family to exercise
A serious pilot should exercise at least this family:
- `lane-default-scope/v0`
- `lane-default-card/v0`
- `lane-slot-defaults/v0`
- `lane-default-evidence/v0`
- `lane-default-freshness/v0`
- `lane-default-handoff/v0`
- `lane-default-pack/v0`
- optional `lane-default-diff/v0`
- optional `lane-default-override-report/v0`

Pilot rule:
**every scoped default must keep scope, alternatives, freshness, and authority boundaries visible.**

## Ranked pilot lanes

### 1) Conservative internal CLI / automation default
**Why first**
- low coordination cost;
- common real-world Rust entry point;
- forces explicit parser/config/logging/testing/package/support defaults without distributed-systems sprawl.

**Success bar**
The pilot can publish one reusable default lane for an internal CLI / automation tool, name at least one serious alternative, link canonical references, and say when a project must escalate to a project-specific adoption brief.

### 2) Conservative HTTP / service baseline
**Why second**
- this is one of Rust’s strongest existing adoption lanes;
- the lane has real runtime, middleware, observability, background-work, and settings consequences;
- it stress-tests whether defaults can stay bounded instead of silently becoming “the Rust backend answer”.

**Success bar**
The pilot can publish a reusable service baseline with visible runtime-family assumptions, slot defaults, serious alternatives, renewal triggers, and bounded bootstrap/onramp handoffs.

### 3) Existing polyglot workspace / monorepo component default
**Why third**
- many teams adopt Rust inside an existing larger system rather than in a greenfield repo;
- this forces the default layer to name environment and integration assumptions instead of pretending every Rust project starts clean;
- it keeps local overlays and institutional constraints visible.

**Success bar**
The pilot can say what the reusable default is for “Rust inside a larger polyglot workspace”, what assumptions it makes, and when a local overlay or project-specific override is mandatory.

### 4) Script / tiny utility / repro default
**Why fourth**
- Rust’s 2026 flagship themes still include higher-level Rust via `cargo-script`;
- small one-file or tiny-workspace lanes are where recommendation guidance often gets overly casual or prestige-driven;
- this is the place to prove defaults can remain honest even when the answer is intentionally lightweight.

**Success bar**
The pilot can publish a tiny-utility default that keeps “repro / script / throwaway” assumptions explicit and does not silently promote itself to a long-lived application starter.

### 5) Safety-tilted / regulated conservative default
**Why fifth**
- strategically important;
- pressure-tests maintenance, evidence, compatibility, and policy imports;
- the wrong move here would be a popularity-driven default laundered into false safety posture.

**Success bar**
The pilot can publish a conservative default with visible evidence imports, narrower authority, and stronger escalation rules instead of pretending the reusable default is enough on its own.

## Pilots to defer
- a global crate ranking engine;
- a universal “best stack” page;
- automatic template generation from defaults alone;
- assistant-generated defaults with no human review owner;
- one giant default card that tries to cover all Rust domains.

## Immediate archive consequences
- Treat [`design/reviewable-lane-defaults.md`](./reviewable-lane-defaults.md) as an **execution seam**, not just a philosophy note.
- Future Atlas and Adoption-Navigation work should ask whether new evidence improves reusable defaults or only project-specific briefs.
- Profiled Onramp, Project Bootstrap, and Institutional Overlay work should import scoped defaults rather than silently inventing them.
- Do **not** widen this pilot until at least one lane proves that the default can stay reusable without becoming an ecosystem blessing.

## Why this would be a worthy contribution
Rust does not only need better one-off recommendations.
It needs a way to publish **reviewable reusable defaults** for recurring project classes while keeping:
- candidate space,
- scoped default,
- project override,
- local institutional overlay,
- and neutral shared common ground

as distinct truths.

That sounds modest.
But it would materially improve:
- team onboarding speed,
- recommendation freshness,
- starter-path quality,
- assistant boundedness,
- and long-term institutional memory around why a recurring project class starts from one lane instead of another.
