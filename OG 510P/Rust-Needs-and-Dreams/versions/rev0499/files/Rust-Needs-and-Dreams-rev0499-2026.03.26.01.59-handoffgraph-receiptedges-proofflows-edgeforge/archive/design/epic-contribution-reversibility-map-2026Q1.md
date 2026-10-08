# Design: Epic contribution reversibility map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- scorecards for comparing already-worthy contributions;
- a delivery matrix for what each candidate should ship;
- an incubation map for what vehicle each candidate should start in;
- a proof-burden map for what each candidate must prove;
- a bet-sizing map for what capital band each candidate honestly needs;
- a compounding map for what unlocks later work;
- a support-bundle map for what each candidate should ask from the ecosystem;
- a renewal-burden map for what it costs to keep each one honest after launch;
- a distortion-risk map for how the best ideas most easily go wrong while still looking successful;
- a boundary map for where the value should live first; and
- a decision-rights map for who must agree before value appears.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **how reversible is its first deployment and how much blast radius does it create if we get it wrong?**
> Can it begin as an advisory replayable probe? Does it need to be opt-in? Can it become a default only with an escape hatch? Is it an operator-enforced boundary that must stage from monitor to gate? Or is it a governance-grade ratchet that should only exist after unusually strong proof and stewardship?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** claim that the most reversible work is always the most important work.
It does **not** say all valuable things must remain advisory forever.
It explains which worthy contributions can start as **safe reversible probes**, which need **escape hatches**, which create **route or policy blast radius**, and which should only ratchet after much stronger proof.

Read with:
- `design/epic-contribution-decision-rights-map-2026Q1.md`
- `design/epic-contribution-boundary-map-2026Q1.md`
- `design/epic-contribution-distortion-risk-map-2026Q1.md`
- `design/epic-contribution-proof-burden-map-2026Q1.md`
- `design/epic-contribution-renewal-burden-map-2026Q1.md`
- `design/epic-contribution-support-bundle-map-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/shared-spine-execution-blueprint-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
Current Rust signals are no longer just telling us “what is missing”, “where it should live”, or “who must agree”.
They are also telling us something stricter:
**several of the strongest bets differ mainly in how safely they can be introduced, rolled back, or narrowed if their first shape is wrong.**
That is not the same as rank, boundary fit, or consensus burden.

Cargo's own posture is the first reason. The external-tools chapter still routes integration through custom subcommands, versioned metadata, and JSON messages rather than through Cargo becoming every workflow. `cargo metadata` explicitly says compatibility is tied to an output-format version and warns that some opaque representations should not be relied on. Together, those sources imply a valuable pattern: a lot of ecosystem work can begin as **replayable companion tooling** whose blast radius is limited because its imports are bounded and its output can be ignored or replaced.
https://doc.rust-lang.org/cargo/reference/external-tools.html
https://doc.rust-lang.org/cargo/commands/cargo-metadata.html

The Cargo 1.94 development-cycle post makes the second reason explicit. It repeats that Cargo cannot be everything to everyone because of the compatibility guarantees it must uphold. That is not just a boundary argument. It is a reversibility argument: once a behavior becomes Cargo-core UX, changing it later is much more expensive than evolving a companion tool or an unstable report lane.
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

The Build Dir Layout v2 testing call sharpens the same point from the downside direction. The post explicitly asks downstream tools to test because the change may affect assumptions about artifact locations and tool integrations. That is exactly what blast radius looks like in practice: a seemingly local toolchain improvement can ripple into a wide companion ecosystem if the boundary is not staged and tested.
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

The docs.rs default-target change adds a third lesson: **defaults can change safely when they preserve an escape hatch**. The docs.rs team changed the default targets but let crate authors opt out by setting explicit targets in `Cargo.toml`. That is a concrete ecosystem model for “default with explicit escape hatch” rather than a one-way ratchet.
https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/

`cargo fix` adds a fourth lesson. Its model is to apply compiler-provided suggestions to source code while still leaving the user in control of review and commit history. That is a strong example of a high-value ecosystem feature whose first honest shape is **advisory automation with reviewability**, not silent mutation hidden behind one big “smart mode”.
https://doc.rust-lang.org/cargo/commands/cargo-fix.html

The `cargo-semver-checks` goal adds a fifth lesson. The current vision for integration into `cargo publish` is not “publish is now permanently blocked with no recourse”. It is closer to a **ratchet with an escape hatch**: default SemVer checking paired with an override flag analogous to `--allow-dirty`. That is an explicit model the archive should generalize: some worthy contributions are best introduced as **default-on checks with a visible override**, not as irreversible policy edicts.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

Finally, the March 2026 challenges writeup and the 2025 State of Rust survey remind us why this matters strategically. The pain is broad and real — compile/resource cost, debugging, tacit knowledge, crate choice, domain gaps — but that does not mean every answer should start as a hard default or official policy. Some of the best answers should begin as **low-blast-radius probes** precisely so the ecosystem can learn faster without paying premature compatibility or trust costs.
https://blog.rust-lang.org/2026/03/20/rust-challenges/
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

The missing layer is therefore not another ranking rewrite.
It is a **reversibility map**.

## Headline answer
The archive should now assume:

> a worthy Rust contribution needs an explicit **reversibility claim**:
> **advisory replayable probe**, **opt-in gate**, **default with escape hatch**, **operator-enforced boundary**, or **governance / standards ratchet**.
> If the archive cannot say how a contribution can be rolled back, bypassed, narrowed, or staged when it is wrong, it is still reasoning at the wrong level.

Reversible does **not** mean trivial.
Irreversible does **not** mean bad.
The right question is:
**what is the smallest blast-radius deployment shape that still creates truthful learning and real user value?**

## The five reversibility families

### 1) Advisory replayable probe
Use this when the contribution can create value through reports, packs, diffs, fixtures, or guidance that downstream users may adopt, compare, and ignore without changing core routes or defaults.

Typical shape:
- local report command;
- CI-importable receipt pack;
- reviewable assistant slice;
- replayable exemplar-backed comparison.

Typical reversal path:
- stop running it;
- keep old receipts for comparison;
- remove it from CI or local workflows without changing package or toolchain semantics.

Wrong shape:
- claiming the contribution has already become policy or canon simply because it emits useful evidence.

### 2) Opt-in gate or companion default
Use this when the contribution can block or rewrite something, but only for teams that deliberately enable it.

Typical shape:
- optional checker or linter profile;
- explicit `cargo` companion subcommand;
- optional toolchain-distributed component;
- “apply suggestions” tooling with visible review boundaries.

Typical reversal path:
- disable the feature or stop invoking the gate;
- preserve diffs or witness results;
- return to advisory mode without changing upstream defaults.

Wrong shape:
- silently treating enabled-on-one-team as good enough reason to standardize the behavior everywhere.

### 3) Default with explicit escape hatch
Use this when the ecosystem wants a stronger default, but still needs an override or opt-out while the shape matures or while local exceptions remain legitimate.

Typical shape:
- default checks with override flags;
- default target or policy choices with explicit metadata/config escape hatches;
- migration helpers that can be adopted widely while remaining reviewable and defeasible.

Typical reversal path:
- explicit project-level override;
- downgrade to advisory mode;
- documented exception receipt rather than unsupported silent divergence.

Wrong shape:
- calling something reversible when the only escape hatch is undocumented or socially disallowed.

### 4) Operator-enforced boundary
Use this when the value appears only when a route owner, registry operator, CI platform, or service owner actually enforces or quarantines behavior.

Typical shape:
- intake gateway;
- publish gate;
- extraction or provenance boundary;
- service-side route control.

Typical reversal path:
- staged rollout from observe → warn → require → quarantine;
- scoped exemptions with receipts;
- route-local rollback rather than ecosystem-wide truth claims.

Wrong shape:
- pretending a dashboard or local scanner already gives the operator control surface the seam requires.

### 5) Governance / standards ratchet
Use this when the contribution becomes real only when institutions, consortia, or standards-like processes bless it as a readiness baseline or long-horizon obligation.

Typical shape:
- safety or assurance readiness profiles;
- consortium-maintained checklists;
- procurement or certification-adjacent evidence families;
- language/toolchain policy shifts with long-tail downstream expectations.

Typical reversal path:
- very limited; reversal mainly means deprecation windows, successor profiles, or governance-led withdrawal.

Wrong shape:
- pretending one crate, one product, one badge, or one funded pilot is enough to justify a governance-grade ratchet.

## Reversibility-adjusted view of the strongest contributions
This is **not** a broad-importance rerank.
It is a “how safely should this begin?” ranking.

### 1) Build-State Evidence
**Reversibility family:** 1 → 2

Why:
- teams can gain immediate value from local build-state reports and CI receipts;
- the underlying Cargo surfaces are useful but still evolving;
- the contribution can create truthful learning before any official default or Cargo-core UX is needed.

What a worthy first move looks like:
- replayable local/CI evidence packs;
- explicit imported-versus-derived boundaries;
- exemplar-backed diffs across configurations;
- advisory receipts first, optional local gating later.

Strategic consequence:
- this remains the strongest broad first build and now also the clearest **low-blast-radius first build**.

### 2) Semantic Context / Tooling Contract / Shared Spine
**Reversibility family:** 1 → 2

Why:
- these layers mostly improve honesty and portability of later tools;
- they can start as validators, envelopes, fixtures, and import discipline;
- the cost of stopping or changing them is low if they stay companion-first and clearly bounded.

What a worthy first move looks like:
- validator/linter plus fixture corpus;
- explicit lineage envelope;
- import-strength markers;
- bounded assistant slices that stay weaker than canon.

Strategic consequence:
- these remain strong early multipliers precisely because their first honest shapes are reversible and testable.

### 3) Adoption Navigation + Ecosystem Atlas
**Reversibility family:** 1 → 3

Why:
- editorial/defaults work can begin as advisory briefs and source-grounded comparisons;
- it becomes more dangerous only when it hardens into perceived official doctrine;
- defaults may be useful, but they need freshness and local-fit escape hatches.

What a worthy first move looks like:
- advisory atlas and decision briefs;
- freshness receipts;
- explicit exception paths and “not-for-you” markers;
- no universal leaderboard.

Strategic consequence:
- still worthy, but it should spend a long time as an advisory/defaults commons before anyone treats it as a ratcheting canon surface.

### 4) Compatibility Claims
**Reversibility family:** 2 → 3

Why:
- checker-based compatibility work can begin as opt-in or advisory proof;
- it only deserves publish-path defaulting after a high false-positive/false-negative burden is paid;
- the `cargo-semver-checks` story is the model: stronger defaulting coupled to a visible override.

What a worthy first move looks like:
- witness-backed reports and explicit inconclusive states;
- opt-in CI gate first;
- only later, narrowly scoped default integration with override.

Strategic consequence:
- this is not anti-upstream; it is **ratchet discipline**.

### 5) Package Intake Gateway
**Reversibility family:** 3 → 4

Why:
- the seam is real only when route owners enforce it;
- but it should almost never begin as an immediate hard gate with ecosystem-wide truth claims;
- the honest rollout is staged: observe, classify, warn, require, then quarantine if warranted.

What a worthy first move looks like:
- route-aware monitor mode;
- explicit operator receipts and exemptions;
- fail-closed behavior only where the operator owns the route and the evidence is strong.

Strategic consequence:
- this remains urgent, but it should stage as an operator bridge with controlled blast radius, not a trust-score portal or sudden universal gate.

### 6) Feedback Loop / Debuggability Acceptance
**Reversibility family:** 1 locally, 4 at ecosystem-acceptance scale

Why:
- local debugger helpers and fixtures are reversible;
- but any claim that “Rust debugging is good now” has cross-tool tuple blast radius;
- acceptance promises therefore need shared fixtures and gradual widening, not one triumphant demo.

What a worthy first move looks like:
- fixture corpus and regression matrix first;
- tuple-specific receipts;
- local adapters and issue-routing packs;
- no broad default claim until the acceptance matrix justifies it.

Strategic consequence:
- this is a high-value seam whose **evidence can start reversible**, but whose **acceptance claims are expensive to widen**.

### 7) Safety-Critical Readiness Commons
**Reversibility family:** 5

Why:
- the seam becomes meaningful only when shared profiles, obligations, and maintenance commitments exist across organizations;
- false confidence here is worse than delay;
- one pilot or one crate should not ratchet the ecosystem into making readiness claims it cannot sustain.

What a worthy first move looks like:
- readiness corpus and shared-maintenance commitments;
- clear non-claims and scope bounds;
- consortium-grade ownership before any badge or baseline language hardens.

Strategic consequence:
- this remains real and important, but it should be treated as a governance-grade ratchet, not a fast first build.

## The practical portfolio rule
The archive should now prefer a sharper stage rule:

1. **advisory replayable probe first** when truthful value is possible without route mutation;
2. **opt-in gate second** when local teams want stronger enforcement;
3. **default with escape hatch third** when the false-positive and exception story is good enough;
4. **operator-enforced boundary fourth** when the route owner must actually control the seam;
5. **governance ratchet last** when long-horizon stewardship, shared maintenance, and sector legitimacy exist.

This is not a universal law.
Some upstream substrate work starts upstream immediately.
But for cross-ecosystem contribution design, it is the safest default interpretation the repo lacked.

## Wrong shapes this note should help refuse
Refuse these recurring mistakes:
- launching a worthiest contribution directly as hard policy when advisory evidence would teach faster;
- calling something “reversible” when its exceptions are undocumented or socially impossible;
- treating one local pilot as enough reason for default-on behavior across the ecosystem;
- introducing route-enforced gates before operator receipts and exemption flows exist;
- and using governance language to hide the absence of maintenance commitments.

## What future revisions should now say explicitly
When a future revision proposes or sharpens a worthy contribution, it should now state:
- the candidate's **reversibility family**;
- the first **rollback or escape-hatch path**;
- the first **staged rollout path** if enforcement is involved;
- the first **evidence artifact** that survives rollback;
- and the first **wrong ratchet** the contribution must refuse.

That is the missing portfolio layer this note supplies.
