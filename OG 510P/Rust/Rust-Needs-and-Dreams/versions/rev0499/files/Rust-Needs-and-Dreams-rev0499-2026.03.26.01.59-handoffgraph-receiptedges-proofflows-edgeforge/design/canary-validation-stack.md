# Design: Canary Validation Stack (Preview Adoption + Baseline Ratchet + Cargo Report + Migration Truth)

## Goal
Treat **continuous advance warning** as a first-class Rust ecosystem seam.

Rust projects increasingly know they should watch more than one thing before users hit a failure:
- stable for the contract they actually ship today,
- beta for the next stable release,
- nightly for preview-dependent or edge-case breakage,
- `rust-version` / MSRV verification for declared floor honesty,
- latest-compatible dependencies for dependency-drift exposure,
- and future-incompatibility reports for warnings that will harden later.

But in practice those signals are usually smeared across CI YAML, scheduled jobs, `allow_failure` folklore, bot PRs, terminal notices, release notes, and maintainer memory.
The missing contribution is therefore **not** another CI-template repo, another dashboard, another dependency-update bot, or another generic “test stable, beta, and nightly” essay.
It is a thin `cargo canary` / `canary-pack/v0` layer that keeps these truths separate:
- **baseline-and-policy truth** — what support floor, branch policy, and preview posture the project currently intends to uphold;
- **canary-lane truth** — which watch lanes are selected (`stable`, `beta`, `nightly`, `msrv`, `latest-deps`, `future-incompat`, optional platform slices), with what cadence and freshness rules;
- **gating-and-notification truth** — which lanes are blocking, soft-fail, scheduled-only, advisory-only, or escalation-only;
- **observed-canary truth** — what actually happened in each run, with exact coverage slices and known blind spots;
- **escalation truth** — which failures route into Preview Adoption, Baseline Ratchet, Migration Truth, Dependency Review, or Defect Escalation rather than being hand-waved away;
- **consumer-handoff truth** — what support, release, policy, or docs consumers may honestly conclude from those watch lanes.

The point is to stop treating “our CI watches the future” as one blob.

## Why this seam matters now
Official Rust/Cargo signals are unusually aligned here:
- The Rust book’s release-train appendix says Rust ships on a six-week train model, with changes flowing from nightly to beta to stable, and explicitly says beta exists so people can catch regressions before they hit stable. That makes beta canaries a designed part of Rust’s operating model, not optional folklore.
  https://doc.rust-lang.org/book/appendix-07-nightly-rust.html
- Cargo’s CI guide is unusually explicit that watch lanes have different semantics. It shows nightly lanes as `allow_failure` in some examples, separately documents **verifying latest dependencies**, and separately documents **verifying `rust-version`**. It also notes that higher-risk projects may need more combinations. That is direct evidence that lane selection, cadence, and gating are first-class policy choices.
  https://doc.rust-lang.org/cargo/guide/continuous-integration.html
- Cargo’s `rust-version` docs say projects should choose and document a support policy, say changing `rust-version` is assumed to be a minor incompatibility, and explicitly discuss dev-branch versus release-branch policy drift. That means canary lanes should be parameterized by policy rather than copied from one universal matrix.
  https://doc.rust-lang.org/cargo/reference/rust-version.html
- Cargo’s resolver docs say MSRV-aware dependency selection is heuristic in mixed-policy workspaces, and the CI guide’s “latest dependencies” example explicitly sets `CARGO_RESOLVER_INCOMPATIBLE_RUST_VERSIONS=allow` so a latest-deps lane does not silently inherit the project’s floor constraint. That means “latest graph watch” and “declared floor watch” must stay separate.
  https://doc.rust-lang.org/cargo/reference/resolver.html
  https://doc.rust-lang.org/cargo/guide/continuous-integration.html
- Cargo’s future-incompatibility docs say Cargo checks dependencies for warnings that may become hard errors later, emits a notice, and supports replaying the full report later with `cargo report future-incompat`. Build/test/check commands also expose `--future-incompat-report`. That gives Rust a real native early-warning lane above console ephemera.
  https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
  https://doc.rust-lang.org/cargo/commands/cargo-report.html
  https://doc.rust-lang.org/cargo/commands/cargo-build.html
- Cargo config exposes `future-incompat-report.frequency`, confirming that future-incompat reporting already has explicit notification policy rather than being only transient terminal noise.
  https://doc.rust-lang.org/cargo/reference/config.html
- Rust 1.94 cycle work continues to make Cargo-native evidence more machine-usable with `cargo report sessions`, `cargo report rebuild`, and related timing/report work. That means canary outcomes can increasingly attach to native evidence rather than ad hoc summaries.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The 2025 State of Rust survey says most developers use stable and keep up with releases, while nightly is mostly used out of necessity. That combination makes early-warning lanes more important: most projects want to stay stable-first, but they still need structured ways to see incoming breakage before users absorb it.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, ideal Rust now needs a **reviewable canary-validation layer** above raw CI jobs and below migration/support/release conclusions.

## What belongs in the canary-lane set
Not every project needs every lane, but the stack should be able to name them explicitly:
- **stable required lane** — the contract users rely on now;
- **beta canary lane** — the next stable Rust release before it lands;
- **nightly preview lane** — especially for preview-dependent projects or projects that want early signal on upcoming breakage without claiming support;
- **MSRV / `rust-version` lane** — verifies declared floor honesty;
- **latest-compatible-deps lane** — watches dependency-drift risk separately from lockfile determinism;
- **future-incompat lane** — warnings that will become errors later, especially in dependencies;
- **optional platform or feature slices** — only when project risk or policy makes them necessary.

A project does not become more honest by pretending these all mean the same thing.

## What each neighboring stack owns
### Preview Adoption Stack
[`design/preview-adoption-stack.md`](./preview-adoption-stack.md) owns:
- what unstable or pre-stable capability is being used,
- how it is activated and pinned,
- what support boundary and exit posture apply.

Its question is:
> what preview subject are we intentionally adopting?

### Baseline Ratchet Stack
[`design/baseline-ratchet-stack.md`](./baseline-ratchet-stack.md) owns:
- the current baseline vector,
- the proposed floor change,
- workspace variance,
- verification and release-line consequences.

Its question is:
> what supported Rust floor or branch policy are we intentionally changing?

### Migration Truth Stack
[`design/migration-truth-stack.md`](./design/migration-truth-stack.md) owns:
- the concrete transition program,
- selected edits,
- checked downstream consequences,
- final outcome receipts.

Its question is:
> what transition program actually ran?

### Cargo Report Kit
[`design/cargo-report-kit.md`](./design/cargo-report-kit.md) owns:
- native Cargo report identity,
- future-incompat imports,
- unstable build-analysis sessions,
- replay/copy/projection truth.

Its question is:
> what did Cargo itself observe and retain?

### Defect Escalation Stack
[`design/defect-escalation-stack.md`](./design/defect-escalation-stack.md) owns:
- minimized repro lineage,
- routing/dedup posture,
- issue or regression-test handoff.

Its question is:
> how does a detected breakage become an actionable upstream artifact?

### Compatibility Claims Stack
[`design/compatibility-claims-stack.md`](./design/compatibility-claims-stack.md) owns:
- what support claims are declared and observed,
- platform/debugger/acceptance lane truth,
- support diffs and consumer summaries.

Its question is:
> what may we now claim publicly?

The Canary Validation Stack sits **between** those layers.
It does not own preview policy, baseline policy, migration execution, Cargo-native report storage, defect routing, or public support claims.
It owns the **watch program** that notices when one of those layers needs to move.

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these quickly:
1. What baseline/support policy are the canaries supposed to defend?
2. Which canary lanes exist, and why these lanes rather than others?
3. Which lanes are blocking, soft-fail, scheduled, or advisory-only?
4. What did each lane actually observe, with what coverage slice and freshness?
5. Which failures are merely watchpoints versus which ones should trigger preview review, ratchets, migrations, dependency refresh, or upstream escalation?
6. What release/support/docs/policy consumers may now honestly import from the watch program?

If the stack cannot answer those six questions, it is still just CI folklore.

## Recommended execution posture
The archive should prefer a ranked rollout like this:

### 1. Stable + beta + nightly watch policy
Prove the stack on the release-train lanes first, with explicit blocking versus advisory posture.

### 2. MSRV + latest-deps split
Prove that declared-floor honesty and latest-graph exposure are different watch jobs with different semantics.

### 3. Future-incompat import lane
Prove that dependency warnings which harden later can be tracked as first-class canary outcomes instead of pasted console logs.

### 4. Workspace/package variance lane
Prove that workspaces can watch different packages or branches differently without laundering those exceptions into one fake global policy.

### 5. Escalation and ratchet handoff
Only after the above are reviewable should canary results drive preview exit, baseline ratchets, migration programs, release notes, or defect escalation automatically.

That order matters.
The archive should not jump straight to one magical “future breakage dashboard” or one universal GitHub Actions snippet.

## Design principles
1. **Watch lanes are policy, not decoration.** Stable, beta, nightly, MSRV, latest-deps, and future-incompat lanes mean different things.
2. **Gating stays separate from observation.** A soft-fail nightly job can still contain highly actionable evidence.
3. **Cadence matters.** Per-PR, per-merge, scheduled, and manual watch jobs should not be collapsed.
4. **Coverage slices stay explicit.** Which packages, targets, features, platforms, and dependency modes were watched must remain visible.
5. **Observed canary truth is not public support truth.** Seeing one nightly failure does not mean a platform is unsupported; seeing one beta pass does not prove a complete support claim.
6. **Escalation paths stay named.** A canary hit should say whether it points toward preview review, baseline ratchet, migration work, dependency refresh, or upstream defect filing.
7. **Cargo-native evidence should be imported when possible.** Prefer future-incompat reports and Cargo report/session imports over terminal folklore.
8. **One matrix does not fit all.** The right watch program depends on branch policy, preview posture, workspace variance, and project risk.

## Core artifact family
### 1. `canary-subject/v0`
Records:
- crate / workspace / branch / release-line identity;
- current baseline vector reference;
- preview-adoption references where relevant;
- support-policy or consumer-class context;
- explicit non-goals and out-of-scope surfaces.

### 2. `canary-lane-set/v0`
Defines which watch lanes exist.

Should record:
- lane ids and kinds (`stable`, `beta`, `nightly`, `msrv`, `latest-deps`, `future-incompat`, `platform-slice`, `other`);
- selected packages / targets / features / dependency modes;
- cadence (`per-pr`, `per-merge`, `scheduled`, `manual`, `other`);
- freshness expectations;
- required inputs and imported lower-layer artifacts.

### 3. `canary-policy/v0`
Records the governance for the watch program.

Should record:
- which lanes are blocking, soft-fail, advisory-only, or escalation-only;
- notification routes and review ownership;
- expiry or renewal expectations;
- allowed temporary waivers;
- explicit escalation destinations.

Design rule: **policy truth is not run truth**.

### 4. `canary-run-report/v0`
What a particular canary run actually observed.

Should record:
- lane id and run identity;
- toolchain/channel/version used;
- package/target/feature/dependency slice exercised;
- pass/fail/warn/inconclusive/interrupted status;
- imported Cargo-native evidence references when available (`future-incompat`, timings, sessions, rebuild evidence, etc.);
- summarized reasons and bounded uncertainty.

### 5. `canary-alert/v0`
Escalation-oriented interpretation of observed canary outcomes.

Should record:
- triggering run(s);
- class of concern (`incoming-stable-regression`, `preview-breakage`, `declared-floor-drift`, `dependency-drift`, `future-hard-error`, `other`);
- urgency and freshness;
- suggested next stack (`preview-adoption`, `baseline-ratchet`, `migration-truth`, `defect-escalation`, `dependency-review`, `none-yet`);
- required follow-up evidence.

### 6. `canary-handoff/v0`
Bounded summaries for downstream consumers such as:
- release managers,
- support/policy owners,
- adoption overlays,
- docs/maintenance notes,
- assistant/editor views.

### 7. `canary-pack/v0`
Portable bundle containing:
- `canary-subject/v0`
- `canary-lane-set/v0`
- `canary-policy/v0`
- one or more `canary-run-report/v0`
- optional `canary-alert/v0`
- optional `canary-handoff/v0`
- raw attachments or pointers to imported CI/Cargo artifacts

### 8. `canary-diff/v0`
Diff artifact for comparing two watch programs or two runs over time.

Should record:
- added/removed lanes;
- gating or cadence drift;
- coverage-slice drift;
- alert-state drift;
- unresolved watchpoints.

## Reference UX
A reference implementation could expose:
- `cargo canary plan` — emit `canary-lane-set/v0`
- `cargo canary policy` — emit `canary-policy/v0`
- `cargo canary run --lane <id>` — emit `canary-run-report/v0`
- `cargo canary alert` — synthesize `canary-alert/v0` from recent runs
- `cargo canary diff --against <ref|path>` — compare watch posture and recent outcomes
- `cargo canary pack` — bundle `canary-pack/v0`

This should sit above raw CI and native Cargo reports.
It should not try to replace either of them.

## What an epic contribution would look like in practice
A serious contribution here would publish a thin `cargo canary` / `canary-pack/v0` layer that:
- makes release-train, MSRV, dependency-drift, and future-incompat watch lanes explicit rather than buried in CI files;
- imports Cargo-native evidence where possible instead of re-scraping terminal output;
- preserves blocking versus advisory semantics rather than flattening them into one “CI red/green” bit;
- and hands failures off cleanly into preview review, baseline ratchets, migration programs, or upstream defect escalation.

The bar is **not**:
- a hosted dashboard,
- a universal CI matrix,
- a dependency bot with nicer branding,
- or a magical early-warning score.

The bar is a **portable canary-validation contract layer**.

## Anti-goals
Do not turn this stack into:
- one more CI starter repo,
- one universal stable/beta/nightly policy,
- one support badge that pretends watch coverage equals support coverage,
- one release-train replacement process,
- or one dashboard that silently picks winners from contradictory evidence.

The stack is a **review boundary for advance warning**, not a replacement for CI, Cargo reports, release engineering, or stabilization.
