# Design: Portfolio Consumer Routing (2026 Q1)

## Goal
The archive now has:
- rankings;
- seam execution blueprints;
- shared artifact conventions;
- portfolio sequencing;
- candidate triage;
- pilot evaluation;
- and evidence renewal.

What it still lacked was one canonical answer to a narrower but now-urgent question:

> once the archive emits serious review artifacts, which downstream consumers should receive which slice, how lossy may that slice be, and when must the consumer escalate back to the canonical pack instead of pretending a brief is authoritative?

This note answers **consumer routing**, not frontier promotion.

Read with:
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `meta/CONSUMER_ROUTING_PROTOCOL.md`

## Why this note is needed now
Fresh official signals all point toward the same missing cut:
- Rust's March 2026 challenges writeup says the ecosystem tax is often **choice paralysis** and **tacit knowledge**, which means many ecosystem wins now depend on how truth reaches humans and tools, not just on whether the truth exists somewhere.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain canonical while editor/LLM-mediated learning is rising. That means the archive cannot stop at “emit a canonical artifact”; it must also say how weaker consumers should consume it without laundering summaries into canon.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo's plumbing goal says Cargo is still too porcelain-oriented for many advanced workflows and that its operations naturally decompose into explicit phases. That is a direct argument for consumer-specific imports rather than one universal human-facing output.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo's build-analysis goal and build-dir-layout work both push toward recorded build metadata, review commands, and more explicit machine-usable structure. That increases the number of plausible downstream consumers and raises the cost of leaving routing implicit.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The libtest JSON goal exists because people had come to rely on programmatic output. That is not just an output-format story; it is a consumer-routing story about which tool gets which truth and with what guarantees.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- docs.rs now hosts rustdoc JSON directly, but warns that `format_version` matters and that historical availability is incomplete. That makes “just feed the docs to everything” too loose; some consumers need a guarded slice with explicit freshness and parser posture.
  https://docs.rs/about/rustdoc-json
- StableMIR / `rustc_public` work is explicitly about giving tool developers a reliable compiler-facing interface for building analysis tools, development environments, and other applications. Again, that is a routing and contract problem, not merely an existence proof.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- crates.io's current trust/security work keeps widening the set of machine-usable trust and publishing signals, but those signals are not meant to be consumed identically by release operators, policy reviewers, editors, and assistants.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html

Taken together, those signals say the archive needed a note for **who consumes what, at what strength, and with what escalation path**.

## Headline answer
A strong portfolio should not assume that every downstream consumer gets either:
- the full canonical pack, or
- an informal summary that can quietly stand in for it.

The repo needs a third answer:

> canonical packs stay canonical, but each consumer class gets an explicitly weaker routed view with named lossiness, action limits, and a visible escalation path back to the source artifact.

In practice this means the portfolio should standardize five routing truths for every serious seam:
1. **consumer class** — who or what is using the artifact;
2. **decision class** — what decision that consumer is allowed to make from the slice;
3. **authority floor** — what minimum evidence / freshness / lineage the slice must preserve;
4. **lossiness budget** — what the routed view may omit without becoming dishonest;
5. **escalation target** — when the consumer must stop and open the canonical pack or attached receipts.

## The five routing truths

### 1) Consumer class
Every serious routed view should name one primary consumer class.
At minimum the archive should treat these as distinct:
- **reviewer / maintainer** — a human deciding whether a result is believable or worth merging;
- **CI / automation** — a machine deciding pass / fail / warn / upload / gate;
- **release / publish operator** — someone deciding what may be packaged, published, or shipped;
- **security / policy operator** — someone deciding allow / deny / investigate / contain;
- **editor / IDE / docs indexer** — a tool optimizing discovery or interactive guidance;
- **assistant / agent** — a consumer that can summarize, suggest, or ask follow-up questions but should not silently upgrade its own authority;
- **specialist orchestrator** — a downstream native-edge / interop / deployment consumer importing only a bounded slice.

Why this matters:
one slice that is safe for an IDE may be too weak for CI gating, and one slice that is safe for an assistant may be too lossy for release or security decisions.

### 2) Decision class
Each routed view should say what decisions it is allowed to support.
Examples:
- inspect / explain;
- warn / annotate;
- compare / diff;
- verify / gate;
- package / publish;
- approve / deny / quarantine;
- suggest / escalate.

Why this matters:
consumer routing is not just about presentation. It is about which actions the artifact may legitimately drive.
A PR annotation and a publish gate should not silently share the same truth standard.

### 3) Authority floor
Each routed view should carry a minimum honesty floor:
- subject identity;
- source lineage;
- freshness anchor;
- partiality or unsupported states;
- and a pointer back to the canonical pack.

Why this matters:
routed views are allowed to be smaller, but not allowed to become provenance-free.

### 4) Lossiness budget
Each routed view should say what it may omit.
Examples:
- compact CI summaries may omit large attachments but not fail/warn reasons or coverage gaps;
- IDE hints may omit raw receipts but not parser/version caveats;
- assistant briefs may omit machine-level payload detail but not uncertainty, unsupported states, or escalation guidance.

Why this matters:
most routing bugs are really **silent lossiness** bugs.

### 5) Escalation target
Each routed view should make it obvious when a consumer must escalate.
Examples:
- assistant summary → canonical pack;
- CI summary → verify receipt / attachment;
- editor hint → semantic-context pack / rustdoc JSON import details;
- package-intake brief → ingress receipt and route evidence;
- migration brief → witness receipt or canonical release-boundary pack.

Why this matters:
the archive should reward routed views that know when they are too weak, not punish them for refusing to overclaim.

## Default consumer families for the core portfolio

### A) Reviewer / maintainer consumers
Typical decisions:
- whether to believe a diagnosis;
- whether to merge or request more evidence;
- whether a downstream slice is honest enough.

Best input:
- canonical pack plus compact brief.

Must preserve:
- subject;
- imports;
- explicit partiality;
- and direct links or references to attachments.

Should not rely on:
- assistant-only prose;
- screenshot-only dashboards;
- or decontextualized verdict badges.

### B) CI / automation consumers
Typical decisions:
- warn / fail / upload / gate;
- attach annotations;
- persist receipts.

Best input:
- verify receipt or machine-readable brief derived from the canonical pack.

Must preserve:
- exact subject and revision;
- explicit exit status or gate posture;
- failure reason class;
- unsupported / fallback states;
- and lineage back to the canonical pack.

Should not rely on:
- freeform summaries;
- policy decisions baked into opaque tool output;
- or unstated freshness assumptions.

### C) Release / publish consumers
Typical decisions:
- may this crate or artifact ship;
- is the public boundary acceptable;
- what route/authority/publishing posture was used.

Best input:
- canonical pack plus verify receipts for migration/public-api or package-intake / publish-path subjects.

Must preserve:
- authority and route truth;
- waivers / overrides;
- explicit not-checked states;
- and escalation to canonical attachments.

Should not rely on:
- editor-oriented summaries;
- recommendation cards;
- or assistant rephrasings of semver or trust evidence.

### D) Security / policy consumers
Typical decisions:
- allow / deny / investigate / quarantine;
- what residual risk remains.

Best input:
- canonical pack with explicit receipts and policy-specific brief.

Must preserve:
- source lineage;
- route/authority posture;
- residual-risk / partiality states;
- and exact decision basis.

Should not rely on:
- popularity / recommendation signals;
- crate-score style composites;
- or language suggesting certainty that the evidence did not prove.

### E) Editor / IDE / docs consumers
Typical decisions:
- what hint or navigation to show;
- what context to preload;
- what related subject to surface.

Best input:
- thin imported slice or routed brief.

Must preserve:
- parser / format caveats;
- freshness anchor;
- exact symbol or subject identity;
- and an obvious path back to the canonical pack.

Should not rely on:
- stale cached semantic conclusions with no freshness signal;
- or publish/security verdicts that the consumer cannot explain.

### F) Assistant / agent consumers
Typical decisions:
- explain;
- summarize;
- suggest next actions;
- escalate to stronger artifacts.

Best input:
- brief plus explicit handoff metadata.

Must preserve:
- uncertainty;
- unsupported states;
- freshness;
- and a pointer to the canonical pack.

Should not rely on:
- silent paraphrase of canonical truth as if the assistant independently established it;
- or action claims stronger than the routed slice permits.

Default rule:
assistant consumers should remain the **weakest authority lane** unless they open stronger attachments and say so.

## What this means for the archive's strongest seams

### Build-State Evidence
Primary routed consumers:
- reviewers;
- CI;
- build doctors;
- selected assistant explainers.

Routing rule:
CI may gate on explicit receipts or bounded summaries, but broad diagnosis and remediation discussion should escalate back to the canonical pack.

### Semantic Context
Primary routed consumers:
- editor / IDE tools;
- docs/search/indexers;
- semver/public-api tools;
- assistant explainers.

Routing rule:
interactive consumers may use thinner slices, but any conclusion that depends on freshness, parser-version compatibility, or completeness must escalate to the canonical pack or import record.

### Migration / Public API
Primary routed consumers:
- reviewers;
- release operators;
- CI gates;
- support tooling.

Routing rule:
briefs may summarize affected boundaries and candidate actions, but publish or release decisions should only rely on canonical packs plus verify receipts or explicit waivers.

### Package Intake Gateway
Primary routed consumers:
- security / policy reviewers;
- package-admission tooling;
- release / install operators.

Routing rule:
risk summaries may be brief, but quarantine / allow decisions must preserve route, payload, extraction, and residual-risk posture.

### Adoption Navigation
Primary routed consumers:
- humans making starter-set or architecture choices;
- assistant explainers;
- docs-style recommendation surfaces.

Routing rule:
recommendation cards may be compact, but they must preserve local-fit residue and route back to the lane canon and imported evidence.

### Native Edge
Primary routed consumers:
- specialist orchestrators;
- build/release reviewers;
- assistant explainers for boundary context.

Routing rule:
thin summaries may explain boundary/provider/toolchain shape, but any action that changes provider, link, host/target, or foreign-build posture should escalate to canonical receipts.

## What a worthy shared contribution would look like
If a serious lab wanted to build the archive's missing **consumer-routing glue**, the worthy contribution would look like this:

1. a tiny consumer-class vocabulary;
2. a `brief_kind` / `consumer_class` / `allowed_decisions` / `escalation_to` routing convention layered on the shared envelope;
3. reference adapters for at least four seams;
4. fixture packs showing canonical pack → CI brief, reviewer brief, editor hint, and assistant brief derivations;
5. a fail-closed validator that rejects routed views whose lossiness budget would permit stronger claims than the slice can support.

That would be enough to make the portfolio **usable by many consumers** without pretending every consumer deserves the same authority.

## Recommended rollout order

### Phase 1 — core-portfolio routing
Apply routing rules first to:
1. **Build-State Evidence**
2. **Semantic Context**
3. **Migration/Public API**
4. **Package Intake Gateway**

Reason:
these four seams already form the archive's strongest multi-project answer and already produce the most obvious consumer pressure.

### Phase 2 — human guidance and assistant safety
Then add routing discipline to:
- **Adoption Navigation**
- reviewable defaults / receipts
- assistant-facing and docs-facing summaries

Reason:
this is where silent authority inflation is most likely.

### Phase 3 — specialist widening
Then extend the same routing rules to:
- **Native Edge**
- other specialist lanes whose consumers are highly technical but still heterogeneous.

## Failure modes this note is meant to prevent
- letting one assistant brief silently replace the canonical pack;
- letting CI gate on prose that omitted unsupported states;
- letting editor hints overclaim freshness or completeness;
- routing publish/security decisions through recommendation-style summaries;
- forcing every consumer to ingest the full canonical payload when a bounded routed slice would be more realistic;
- and building one mega-dashboard or mega-schema in the name of “serving all consumers”.

## What this note does **not** mean
It does **not** say:
- every seam should optimize for assistant consumers;
- every consumer needs a special bespoke artifact family;
- or the shared envelope should absorb seam-specific semantics.

It says something narrower and more practical:

> the archive should decide, explicitly, which weaker views are allowed for which consumers, and when those views must yield to the canonical pack.

## Archive-level conclusion
The broad portfolio answer is unchanged:
- **Build-State Evidence** remains the strongest one-project answer overall;
- the strongest multi-project answer remains **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**;
- **Native Edge Contract** remains the active specialist frontier;
- **Adoption Navigation Contract** remains the strongest anti-tacit-knowledge answer.

What changes is the archive's ability to make that portfolio **usable in practice**.
The repo now has a canonical answer for **consumer class, allowed decision class, authority floor, lossiness budget, and escalation target**.

That is the missing bridge between “good artifacts exist” and “real humans, CI systems, editors, release tools, security operators, and assistants can use them without corrupting their truth.”
