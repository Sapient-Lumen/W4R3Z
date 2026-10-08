# Design: Compatibility Claims execution blueprint 2026Q1

## Why this note exists now
The archive already had the right ingredients for **Compatibility Claims**:
- `design/compatibility-claims-2026Q1.md`
- `design/compatibility-claims-stack.md`
- `design/compatibility-claims-lane-map.md`
- `design/compatibility-claims-pilot-program.md`
- `design/support-envelope-execution-blueprint-2026Q1.md`
- `design/feedback-loop-debuggability-execution-blueprint-2026Q1.md`
- `design/public-api-execution-blueprint-2026Q1.md`

What it still lacked was the same thing Build-State Evidence, Feedback Loop, Async Capability Commons, Safety-Critical Readiness Commons, Cargo Artifact Contract, Distribution Contract, Workspace Environment, Publisher & Source Identity, Reviewable Edit, Toolchain Productization, Support Envelope, Canonical Learning, Public API, Benchmark Evidence, Defect Escalation, Observability, and Release Truth now have:

> one direct answer to **what the worthy contribution should actually ship in theory and practice**.

That absence matters because the current ecosystem pressure is no longer only “targets are complicated” or “support matrices get stale”.
It is that serious Rust teams increasingly need to answer **what they claim to support, what they claim to accept, what they claim to expose, what they only observed locally, what changed between releases or toolchains, and what downstream docs/release/support/policy/safety consumers may honestly say without flattening all of that into one word like "compatible"**.

The archive should therefore stop treating Compatibility Claims as only a stack or composition note.
It should describe a real contribution shape.

## Fresh signals that force the seam into focus
Primary sources now line up around the same missing middle:
- The rustc target-tier policy still distinguishes tier guarantees and host-tools support, which means “supported target” is formally more structured than most crates and products communicate.
  https://doc.rust-lang.org/rustc/target-tier-policy.html
- Platform-support and release surfaces keep changing in public: the docs.rs metadata and builds docs expose target-selection posture and docsrs-specific caveats, while the docs.rs October 2025 target-default change proved docs targets are part of the public support story rather than a hidden rendering detail.
  https://docs.rs/about/metadata
  https://docs.rs/about/builds
  https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- Cargo already has an explicit package-level support surface for toolchain compatibility through `package.rust-version`, and the resolver can prefer dependency versions compatible with the current Rust version. That means MSRV is no longer just README folklore; it is a machine-visible claim lane.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
  https://doc.rust-lang.org/cargo/reference/resolver.html
- The safety-critical adoption writeup explicitly asks for target-focused readiness checklists and ecosystem-wide MSRV conventions. That is unusually direct evidence that compatibility claims need to be reviewable, long-lived, and auditable rather than left to issue threads and maintainer memory.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Acceptance posture is also moving under real projects: the next-generation trait solver goal is headed toward stabilization work, and the 2026 flagships still center supply-chain boundaries such as public/private dependencies and SBOM support. That means a release can widen or narrow compatibility without changing the target list at all.
  https://rust-lang.github.io/rust-project-goals/2025h2/next-solver.html
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025 State of Rust survey still says online docs are canonical while editor- and LLM-mediated use is rising, which increases the value of attachable compatibility truth over prose-only caveats.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s machine-facing direction keeps strengthening through plumbing and report-oriented work. That matters because the missing contribution is not another hosted matrix, but a reviewable claim layer that tools can import without scraping screenshots or release prose.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

Taken together, those signals say the missing contribution is not another badge or compatibility portal.
It is a **reviewable compatibility-claims layer**.

## Headline answer
If one serious team wants to build the archive’s clearest remaining support-and-claim shaping contribution, the answer should now be:

> Build a **Compatibility Claims reference layer** that imports support-envelope truth, debugger/inner-loop capability truth, acceptance-surface truth, public-boundary truth, and MSRV/toolchain compatibility truth; emits reusable reports and packs; and proves the shape across release, docs, support, policy, and safety handoffs without collapsing them into one universal verdict.

That answer is deliberately broader than **Support Envelope**.
It is also deliberately narrower than “solve trust / support / quality / certification for everything”.

## What this contribution should be in theory

### Core thesis
A compatibility-claims system becomes real ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact subject is being claimed** — crate, workspace, package family, release, artifact family, or product lane;
2. **what claim family is in scope** — platform support, MSRV/toolchain compatibility, debugger tuple compatibility, advanced-pattern acceptance, public-boundary compatibility, or docs-surface compatibility;
3. **what evidence posture exists** — declared, imported, observed, diffed, waived, partial, or unknown;
4. **what changed since the prior release or prior toolchain** — widened, narrowed, reclassified, newly observed, newly unsupported, or still ambiguous;
5. **what downstream consumer is allowed to import** — docs, release notes, support pages, policy, safety review, adoption guidance, package intake, and assistants should all get bounded summaries rather than one flattened score;
6. **what remains explicitly out of scope** — e.g. certification, universal runtime portability, debugger quality on every host, or complete public-API verification.

If a project cannot answer those questions without stitching together target-tier docs, docs.rs settings, rust-version notes, issue trackers, CI matrices, release notes, and maintainer memory by hand, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable claim truth and handoff**.

It should include:
- subject and claim-family identity;
- imported support/acceptance/debugger/API/MSRV attachments;
- evidence-strength vocabulary;
- claim diffs and waivers;
- consumer-bounded exports and redactions.

It should not become:
- a hosted compatibility portal;
- a universal quality badge;
- a replacement for rustc target policy, docs.rs, Cargo, rustup, debugger tooling, or semver-check tooling;
- or a new CI control plane.

### Separation rule
A worthy contribution here must preserve at least six distinct truth classes:
- **subject truth** — which crate/workspace/release/artifact the claim is about;
- **claim-family truth** — support-envelope vs debugger-tuple vs acceptance-surface vs MSRV/toolchain vs public-boundary vs docs-surface;
- **evidence truth** — declared vs imported vs observed vs diffed vs waived;
- **drift truth** — what changed and why;
- **consumer truth** — what a specific docs/release/support/policy/safety/assistant consumer may import;
- **unknown/out-of-scope truth** — what the layer intentionally cannot conclude.

Without that separation, a green CI build, one docs.rs page, one `rust-version` field, one debugger anecdote, or one semver check silently becomes “compatible”, and the whole layer stops being honest.

### Shape rule
The primary contribution shape should now be:
- **reference layer + report/pack command + imported-claims corpus**.

Why this shape fits:
- **reference layer** because the seam is really about claim families, evidence vocabulary, and non-collapse rules;
- **report/pack command** because the missing piece is a portable output that teams can diff, publish, and import;
- **imported-claims corpus** because real compatibility stories are composed from several narrower seams and must not be redefined by one winner-take-all schema.

Wrong shapes to refuse first:
- compatibility badge program;
- one hosted matrix service;
- CI screenshot generator;
- README table expander;
- docs.rs helper pretending to prove compatibility;
- semver or MSRV checker pretending to own the whole answer.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo compattruth inspect`
- `cargo compattruth import`
- `cargo compattruth diff`
- `cargo compattruth handoff --to <docs|release|support|policy|safety|assistant>`
- `cargo compattruth pack`
- `cargo compattruth doctor`

The tool should **import** support-envelope, acceptance, debugger, public-API, and Cargo/rustup facts where possible rather than replacing those systems.

### Public artifact spine
A credible public artifact family would keep the current stack ideas but make the review spine explicit:
- `compat-claims/v0`
- `compat-claim-register/v0`
- `compat-import-report/v0`
- `compat-diff-report/v0`
- `compat-waiver/v0`
- `compat-handoff/v0`
- `compat-pack/v0`

### First proving lanes
A credible rollout should rank proving lanes instead of pretending every claim family lands at once.

#### Lane 1 — support + docs compatibility lane
Start where the compatibility question is clearest to downstream users.
This lane proves the archive can compose platform/runtime/docs facts without flattening them.

What to prove:
- separate dev-host, source-build, release-artifact, docs-surface, and runtime-floor claims;
- import docs.rs target posture without treating it as the full support story;
- preserve evidence strength and partial/unknown lanes;
- export bounded docs/release/support summaries.

#### Lane 2 — MSRV / toolchain compatibility lane
This lane proves compatibility claims are not only about targets.

What to prove:
- import `rust-version` and resolver posture explicitly;
- distinguish package-declared MSRV from actually observed toolchain lanes;
- keep stable/beta/nightly or path-toolchain observations separate from the declared package floor;
- render compatibility drift when the floor rises or observations narrow.

#### Lane 3 — acceptance-surface lane
This lane proves a release can change compatibility without changing the target matrix.

What to prove:
- import named advanced-pattern families and compiler-lane posture;
- distinguish supported, workaround-dependent, experimental, and rejected lanes;
- show diffs across solver or borrow-checker evolution without calling everything a regression;
- keep acceptance posture separate from platform support and public API posture.

#### Lane 4 — public-boundary + release-compat lane
This lane proves that compatibility claims can include API/release boundaries without swallowing the Public API seam.

What to prove:
- import witness-backed public-boundary or exposed-dependency diffs;
- express whether compatibility changed by support, acceptance, or release-boundary movement;
- keep proof imports and unknowns visible;
- export bounded release-note summaries.

#### Lane 5 — long-lived / safety-oriented handoff lane
Only after the earlier lanes work should the pack become a shared import layer for policy, safety, and adoption guidance.

What to prove:
- safety/policy lanes can import claim facts without over-claiming certification;
- readiness checklists can reference observed compatibility lanes and drift;
- assistants can summarize claims while preserving uncertainty and imported-owner boundaries;
- long-lived support diffs remain understandable across toolchain and release churn.

## What to refuse
A worthy contribution here must refuse the most tempting wrong shapes:
- another compatibility badge farm;
- flattening docs.rs success into support truth;
- flattening `rust-version` into actual observed support;
- flattening target-tier status into runtime-floor or debugger truth;
- flattening one semver/API result into “compatible release” truth;
- or making the pack depend on one CI vendor, one docs host, one debugger stack, or one assistant interface.

## Ranking and repo consequence
This revision does **not** rewrite the broad ladder.
It does **not** outrank **Build-State Evidence** overall.
It does **not** displace **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked day-to-day missing middle.

What it does do is make one repeatedly promoted seam explicit:
- **Compatibility Claims** is now the clearest current **claim-routing / import-boundary / handoff execution blueprint** above several narrower layers;
- its primary shape is now **reference layer + report/pack command + imported-claims corpus**;
- **Support Envelope** remains the clearest platform/runtime/docs execution layer beneath it;
- imported debugger-tuple, acceptance-surface, MSRV/toolchain, and public-boundary truths remain adjacent owners rather than being silently absorbed;
- and future release/support/adoption/safety/package-intake/policy/archive-summary work should import this layer rather than rediscovering compatibility truth privately.

That gives the archive a better answer to a pressure cluster that keeps surfacing in official Rust reality:
How should Rust let teams declare, import, diff, and hand off **compatibility claims** without smearing target support, runtime floors, docs surfaces, MSRV, debugger experience, acceptance drift, and release-boundary proof into one vague word like “compatible”?

