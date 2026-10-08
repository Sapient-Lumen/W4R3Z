# Design: Epic contribution distortion-risk map (2026Q1)

## Goal
The archive now has:
- a broad ladder for what matters most;
- scorecards for comparing already-worthy contributions;
- a delivery matrix for what each candidate should ship;
- an incubation map for what vehicle each candidate should start in;
- a proof-burden map for what each candidate must prove;
- a bet-sizing map for what capital band each candidate honestly needs;
- a compounding map for what unlocks later work;
- a support-bundle map for what each candidate should ask from the ecosystem; and
- a renewal-burden map for what it costs to keep each one honest after launch.

What it still lacked was one sharper cross-seam answer to a different practical question:

> once we know a contribution is worthy, **how is it most likely to go wrong while still looking successful?**
> Where do Rust contributions overclaim on unstable surfaces, mistake one tuple for coverage, let best-effort provenance pose as verified truth, let dashboards or LLM summaries outrun canon, or confuse institutional motion with real receipts?

This note is the archive's answer to that question.
It does **not** rerank the broad ladder.
It does **not** promote a new frontier.
It does **not** replace seam-local blueprints.
It explains which worthy contributions face which **distortion risks**, what false-success patterns they are vulnerable to, what guardrails they need in theory and practice, and which apparently-successful outcomes should still count as failure.

Read with:
- `design/epic-contribution-renewal-burden-map-2026Q1.md`
- `design/epic-contribution-support-bundle-map-2026Q1.md`
- `design/epic-contribution-proof-burden-map-2026Q1.md`
- `design/epic-contribution-compounding-map-2026Q1.md`
- `design/shared-spine-execution-blueprint-2026Q1.md`
- `design/portfolio-exemplar-federation-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/adoption-navigation-execution-blueprint-2026Q1.md`
- `design/tooling-contract-execution-blueprint-2026Q1.md`
- `design/compatibility-claims-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`
- `design/safety-critical-readiness-commons-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`

## Why this note is needed now
The public Rust picture is no longer merely saying “here are some missing pieces.”
It is also saying something stricter:
**many ecosystem contributions fail not because they ship nothing, but because they can only look successful by overclaiming.**

The March 2026 challenges writeup is unusually relevant here for two separate reasons. First, it still clusters pain around recurring practical taxes such as compile/resource cost, debugging, and ecosystem guidance. Second, the author's note says the original version of the post was retracted because many readers felt the LLM voice bled through even after careful review. That is direct evidence that generated summaries and high-level dashboards can feel persuasive while still being too weak to count as canon.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey says resource usage remains one of the biggest productivity problems, debugging remains a notable pain point, and online documentation is still the preferred canonical reference even as editor/LLM mediation rises. That means the archive must now treat “projection becomes canon” as a live ecosystem risk, not only as an LLM hygiene preference.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Cargo's own documentation and goals make surface-overread risk concrete. `cargo metadata` is versioned, but consumers are told to pass `--format-version` explicitly and not rely on opaque implementation details. The external-tools chapter says Cargo wants third-party integration, but it routes that through specific machine-facing surfaces rather than through human-readable output scraping. The FAQ says human-readable output often has no compatibility guarantees. The `cargo package` docs say `.cargo_vcs_info.json` is only a best-effort VCS snapshot and does not verify provenance. Those are all signals that a lot of seemingly-helpful ecosystem tooling can become dishonest if it forgets the exact strength of the imported surface.
https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
https://doc.rust-lang.org/cargo/reference/external-tools.html
https://doc.rust-lang.org/cargo/faq.html
https://doc.rust-lang.org/cargo/commands/cargo-package.html

Cargo's build-dir and build-analysis work reinforce a second lesson: users and tools will build explanations on top of internals long before the surfaces are mature enough to bear them. The build-dir goal explicitly says users often cache or reason about implementation details of `target/`, and the build-analysis goal explicitly avoids user-facing stability guarantees during the prototype phase. That means “we have some data” is not the same as “we can safely infer this story”.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

The debugging survey says stellar debugger support would require several debugger versions across multiple operating systems, high-quality visualizers, first-class async support, and expression evaluation — and that keeping the experience working across new debugger versions and internal representation changes is itself hard. That means one convincing debugger demo is exactly the wrong proof shape.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

The `cargo-semver-checks` goal says false-positives and false-negatives are unacceptable, explains that more than 90% of real-world false-positives are traceable to cross-crate items, and notes that some checks must use witness programs compiled via `cargo check` because syntactic information alone is too weak. That is a strong reminder that “good enough approximation” can be the wrong posture for claim-routing layers.
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html

The March 2026 Cargo advisory shows that intake/security work sits at a live operational boundary: crates.io deployed an upload mitigation on March 13, audited the public registry, but alternate-registry users still had to check with their vendor. That means one public-registry status signal cannot silently become a universal package-safety verdict.
https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

The rustc-perf improvements goal says results should be compared **within a configuration, not between configurations**. This is exactly the kind of anti-Goodhart instruction the archive should generalize: a contribution can become strategically worse by inventing an easier but less honest summary metric.
https://rust-lang.github.io/rust-project-goals/2025h2/rustc-perf-improvements.html

The missing layer is therefore not another ranking rewrite.
It is a **distortion-risk map**.

## Headline answer
The archive should now assume:

> a worthy Rust contribution does not fail only by being absent.
> It can also fail by succeeding in the wrong way: by over-reading weak inputs, by hiding unsupported states, by flattening boundaries, by letting projections outrun canon, or by rewarding a metric that is easier to improve than the underlying reality.

That means future portfolio work must keep these distinct:
- **importance** — how strategically worthy the seam is;
- **proof burden** — what it must prove;
- **renewal burden** — what it costs to keep honest;
- **support bundle** — who must say yes and what they must provide;
- **distortion risk** — how the contribution can appear successful while actually becoming less truthful.

## The six distortion families

### 1) Surface-overread distortion
The contribution imports a real machine-facing surface, but quietly treats it as stronger or more stable than it is.

Typical signs:
- relying on implicit output format versions;
- reading opaque IDs or human-readable strings as if they were stable contracts;
- treating prototype or nightly surfaces as publication-grade canon;
- turning best-effort hints into verified facts.

Primary seams at risk:
- **Build-State Evidence**
- **Tooling Contract**
- **Semantic Context**
- **Compatibility Claims**
- parts of **Shared Spine**

### 2) Tuple-extrapolation distortion
The contribution demonstrates one lane and quietly implies cross-tool, cross-platform, or cross-version support.

Typical signs:
- one debugger + one OS + one project demo presented as “Rust debugging support”;
- one target or architecture presented as a portable build or docs answer;
- one editor or CI lane standing in for broader workflow acceptance.

Primary seams at risk:
- **Feedback Loop / Debuggability Acceptance**
- **Build-State Evidence**
- parts of **Adoption Navigation**
- parts of **Safety-Critical Readiness Commons**

### 3) Projection-becomes-canon distortion
The contribution's summaries, rankings, dashboards, or assistant slices become stronger than the canonical evidence they derive from.

Typical signs:
- generated summaries losing freshness, caveat, or local-fit markers;
- dashboards hiding unsupported and partial states;
- recommendation layers sounding definitive while the sources remain conditional;
- assistant-friendly renderings becoming the only thing people read.

Primary seams at risk:
- **Adoption Navigation + Ecosystem Atlas**
- **Shared Spine**
- **Tooling Contract**
- any future LLM-facing consumer layer

### 4) Boundary-collapse distortion
The contribution collapses package identity, source provenance, registry policy, operator posture, and local execution boundary into one fake trust verdict.

Typical signs:
- best-effort VCS hints treated as verified source identity;
- crates.io status treated as alternate-registry status;
- one upload rule treated as the whole intake story;
- one subject or route standing in for all package policy conclusions.

Primary seams at risk:
- **Package Intake Gateway**
- **Compatibility Claims**
- parts of **Semantic Context**
- parts of **Shared Spine**

### 5) Goodhart / scorecard distortion
The contribution chooses a metric that is easy to optimize and lets that metric stand in for the real problem.

Typical signs:
- one aggregate score hiding different claim strengths;
- comparison across incomparable configurations;
- “time improved” without causal or tuple context;
- recommendation or trust portals rewarding what is easiest to count rather than what is safest to conclude.

Primary seams at risk:
- **Build-State Evidence**
- **Adoption Navigation + Ecosystem Atlas**
- **Compatibility Claims**
- future public score portals of any kind

### 6) Stewardship-theater distortion
The contribution looks real because it has a sponsor, working group, or polished launch, but still lacks the owners, tuples, renewal receipts, or proving grounds needed to stay honest.

Typical signs:
- “the community will keep this updated” with no expiry or rerun rules;
- consortium language without shared fixtures or acceptance tuples;
- safety/readiness claims without maintained profiles and owners;
- one institutional host used as a substitute for live artifact discipline.

Primary seams at risk:
- **Safety-Critical Readiness Commons**
- **Feedback Loop / Debuggability Acceptance**
- **Adoption Navigation + Ecosystem Atlas**
- any large “foundation-backed commons” story

## Mapping the strongest current contributions to their highest distortion risks

### 1) Build-State Evidence
**Primary distortion families:** surface-overread + Goodhart / scorecard distortion

Why:
- Cargo's internals and machine-facing build surfaces are improving, but build-dir and build-analysis work are still in motion.
- The easiest bad version of this contribution is a dashboard that sounds causal while reading unstable or partial evidence.

What distortion-resistant design looks like:
- every imported fact names its source surface and version posture;
- implementation-detail observations from `target/` or build-dir internals never silently become contract claims;
- per-run, per-workspace, and per-configuration comparisons stay separate;
- “unknown”, “partial”, and “cannot attribute” are first-class outputs;
- no single speed score outranks explainability receipts.

What still counts as failure even if it looks impressive:
- a beautiful UI that cannot tell imported facts from derived guesses;
- one benchmark number with no lineaged cause graph;
- cross-configuration claims that hide collector, target, or profile differences.

### 2) Feedback Loop / Debuggability Acceptance
**Primary distortion families:** tuple-extrapolation + stewardship-theater distortion

Why:
- the debugging survey is explicit that the real problem spans debugger versions, operating systems, async support, visualizers, and ongoing breakage from internal-representation changes.

What distortion-resistant design looks like:
- an explicit acceptance matrix by debugger, debugger version, OS, target, and scenario class;
- separate states for accepted, partial, unsupported, regressed, and blocked;
- exported receipts for repros and routing, not just screenshots;
- one consortium tuple set before any “stellar support” language.

What still counts as failure even if it looks impressive:
- one polished VS Code or LLDB demo presented as “Rust debugging solved”;
- async support claims without preserved scenario classes;
- a working group with no shared fixtures, no matrix, and no regression receipts.

### 3) Adoption Navigation + Ecosystem Atlas
**Primary distortion families:** projection-becomes-canon + Goodhart / scorecard distortion

Why:
- this seam wants to reduce tacit knowledge, but it lives closest to summary, ranking, default, and recommendation pressure.
- the survey says docs remain canonical while LLM/editor mediation rises, which increases the temptation to let summaries outrun source posture.

What distortion-resistant design looks like:
- explicit source freshness, local-fit, and non-universality markers on every recommendation;
- bounded lane defaults instead of ecosystem-wide quality scores;
- review and expiry metadata preserved in every consumer slice;
- recommendation outputs tied back to exemplar classes and proofs, not vibes.

What still counts as failure even if it looks useful:
- a giant crate-score portal;
- “best library/framework for X” tables with no scope and no age markers;
- assistant-friendly summaries that have dropped source caveats, unsupported lanes, or conflict notes.

### 4) Tooling Contract + Shared Spine + Semantic Context + Compatibility Claims
**Primary distortion families:** surface-overread + projection-becomes-canon + boundary-collapse distortion

Why:
- these seams sit directly on machine-facing imports, adapters, witness programs, rustdoc JSON, metadata, or packaging/provenance hints.
- they are useful exactly because they compress complexity, which means they are also dangerous if they hide which parts are imported, inferred, or only best effort.

What distortion-resistant design looks like:
- imported-versus-inferred facts stay visibly separate all the way through the consumer artifact;
- adapters preserve version, format, and lossiness markers;
- provenance hints remain hints unless separately verified;
- canonical packs stay stronger than assistant slices and public summaries;
- witness-based checks outrank syntactic approximations when the latter are known to mislead.

What still counts as failure even if it unlocks integrations:
- one adapter that silently normalizes away uncertainty;
- a shared schema that erases source-surface strength differences;
- compatibility or provenance conclusions that a cautious reader could not reproduce from the attached evidence.

### 5) Package Intake Gateway
**Primary distortion families:** boundary-collapse distortion + stewardship-theater distortion

Why:
- this seam touches real execution and registry risk.
- the easiest wrong shape is a trust portal or score instead of a route/subject/policy boundary with clear fail-closed behavior.

What distortion-resistant design looks like:
- route, registry, subject, policy status, extraction boundary, and operator action stay separate;
- public crates.io posture never silently covers alternate registries or local sources;
- missing evidence fails closed where appropriate;
- incident and escalation lanes are part of the product, not ops folklore.

What still counts as failure even if it looks reassuring:
- one green badge pretending to summarize package safety;
- verified-on-crates.io claims applied to private or alternate registries without fresh operator evidence;
- provenance or tarball identity claims stronger than the underlying verified surface.

### 6) Safety-Critical Readiness Commons
**Primary distortion families:** stewardship-theater distortion + tuple-extrapolation distortion

Why:
- this seam becomes dishonest very quickly if one demonstrator, one whitepaper, or one regulated-user story is presented as a portable readiness threshold.

What distortion-resistant design looks like:
- named readiness profiles, explicit unsupported zones, and maintained qualification receipts;
- mixed-language, toolchain, and dependency-lifecycle constraints kept visible;
- consortium stewardship tied to real artifacts and renewal cadence;
- “readiness for this profile” language instead of universal safety halo language.

What still counts as failure even if it sounds serious:
- one impressive certification-adjacent example with no maintained profile corpus;
- an industry consortium without shared artifact obligations;
- a broad “Rust is ready for safety-critical” conclusion detached from domain/profile boundaries.

## Distortion-adjusted portfolio interpretation
The broad ladder is unchanged.
But the archive should now say something stronger about **how** to build the top candidates honestly:

1. **Build-State Evidence** remains the strongest broad first build **and** one of the ripest first anti-distortion builds, because its worst failure modes can be directly constrained by lineaged packs, explicit config boundaries, and exemplar reruns.
2. **Feedback Loop / Debuggability Acceptance** remains the clearest second serious build, but now with a sharper anti-goal: do not fund or widen it unless it is prepared to publish tuple truth rather than one-tool demos.
3. **Adoption Navigation + Ecosystem Atlas** remains highly valuable, but it is now the clearest place where a contribution can become popular while becoming less honest. It therefore requires the strictest projection/canon discipline.
4. **Tooling Contract**, **Shared Spine**, **Semantic Context**, and **Compatibility Claims** remain major multipliers, but they should be judged partly by whether they reduce overread and adapter lossiness rather than merely by how many integrations they enable.
5. **Package Intake Gateway** remains urgent and real, but only if it stays bridge-shaped and fail-closed instead of collapsing into trust-score theater.
6. **Safety-Critical Readiness Commons** remains worthy and rising, but only if it is treated as a profile-and-stewardship program rather than a halo narrative.

## What worthy contributions should ship to resist distortion
Every serious contribution in this band should now answer these seven design questions explicitly:

1. **What surface strength are we importing?**
   - stable/versioned contract
   - unstable prototype
   - best-effort hint
   - human-readable output
   - editorial summary

2. **What are our supported tuples?**
   - tool/version/OS/target/profile/scenario coverage
   - accepted / partial / unsupported / unknown / regressed states

3. **Where does canon live?**
   - canonical pack
   - brief/handoff
   - dashboard
   - assistant slice
   - public recommendation layer

4. **What is a hint versus verified fact?**
   - provenance hint
   - verified provenance
   - imported identity
   - inferred identity
   - route-local policy status

5. **What metric are we refusing to worship?**
   - one aggregate score
   - cross-configuration comparison
   - one benchmark hero number
   - recommendation popularity
   - sponsor count or committee size

6. **What does a false-success launch look like?**
   - list the specific launch pattern that would look good but still count as failure.

7. **What artifact proves we resisted distortion?**
   - lineage receipt
   - compatibility gate
   - tuple matrix
   - expiry/renewal receipt
   - incident/escalation receipt
   - witness program or replay pack

## Practical repo consequence
The archive should now prefer the question:

> “what false-success pattern is this proposal vulnerable to, and what artifact family prevents it?”

before it asks:
- should we fund this;
- should we widen this;
- should we make this the default;
- or should we let assistants summarize it.

That is not a side concern.
For several of the strongest Rust ecosystem contributions, it is the difference between a worthy contribution and a persuasive distortion machine.
