# Design: Build-State Evidence Pilot Program (`cargo cache pilot`, `cargo impact pilot`, `cargo builddoctor pilot`, `build-state-pilot-pack/v0`)

## Goal
Make the archive treat **Build Cache Kit**, **Change Impact Kit**, and **Build Doctor Kit** as a shared **Build-State Evidence Stack** without collapsing them into one mega-tool.

The missing contribution is not merely “better build tooling”.
It is a disciplined rollout that proves Rust projects can publish **portable build-state evidence** for a few concrete lanes before widening the scope.

## References (signals)
- The 2025 State of Rust survey still lists resource usage — especially slow compile times and storage usage — among the biggest productivity problems.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2025 compiler-performance survey results say users want better explanations of slow builds and mention editor latency and rust-analyzer performance as blockers.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The Cargo build-analysis goal explicitly aims to record build metadata across invocations and introduce `cargo report` subcommands for rebuild reasons and timings.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The **Relink don’t Rebuild** goal explicitly targets avoiding reverse-dependency rebuilds when a crate’s public interface has not changed.
  https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- The build-dir-layout goal explicitly targets smaller self-contained units, finer-grained locking, rust-analyzer coexistence, GC, and a cross-workspace shared build cache.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Cargo’s build-cache docs now distinguish final artifacts in `target-dir` from intermediate artifacts in `build-dir`.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo 1.93 says build-dir work is being organized around build units so Cargo can lock them individually.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/

## Why this needs its own design layer
The archive already ranked the **Build-State Evidence Stack** very highly, but it was still missing the execution discipline needed to keep the stack honest.

Without a shared pilot program, this seam is vulnerable to three bad outcomes:
1. **cache theater** — everything becomes a fake hit/miss story;
2. **impact theater** — every rebuild becomes either “Cargo is dumb” or “the compiler is conservative” without attachable evidence;
3. **doctor theater** — suggestions float above prose heuristics without grounded inputs.

A worthy contribution here should prove a smaller and stronger claim:
> Rust projects can attach enough build-state evidence that humans and tools can distinguish layout/locking truth, semantic change truth, and workflow diagnosis truth.

## Design principles
1. **Pilot lanes, not the whole universe.** Each pilot must have one clear build-state subject.
2. **Keep fact layers distinct.** Cache/layout facts, impact facts, and diagnostic suggestions must not silently overwrite one another.
3. **Prefer everyday developer pain first.** Editor contention, incremental rebuild churn, and CI cache waste beat giant hypothetical architecture work.
4. **Use Cargo-native signals whenever available.** Import `cargo report` and official build-cache/build-dir facts first.
5. **Treat relink opportunities as explicit opportunities, not as already-realized behavior.**
6. **Scorecards must allow `INCONCLUSIVE`.** Missing evidence or mismatched lanes should degrade honestly.

## Shared artifact posture
### 1. `build-state-pilot-brief/v0`
Why this pilot exists.

Should record:
- pilot id and summary
- primary lane
- intended users and consumer tools
- why the lane matters now
- why the lane is tractable now

### 2. `build-state-evidence-profile/v0`
What evidence counts for the pilot.

Should record:
- accepted raw inputs (`cargo report timings`, `cargo report rebuild`, cache-layout reports, lock reports, impact reports, optional extra traces)
- which inputs are required
- which are advisory only
- freshness rules
- how missing evidence renders (`unknown`, `partial`, `not-run`, `inconclusive`)

### 3. `build-state-lane-profile/v0`
The operational lane being tested.

Should record:
- command class (`check`, `build`, `clippy`, docs, release build, editor background run)
- package/workspace scope
- host/target posture
- local vs CI vs remote-cache posture
- editor/tool coexistence assumptions
- whether relink opportunity is in scope

### 4. `build-state-pilot-scorecard/v0`
Did the pilot actually work?

Should ask:
- did the pilot keep lane identity explicit?
- did it preserve build-cache facts, impact facts, and diagnosis facts separately?
- could it explain duplication, blocking, rebuild scope, or missed reuse honestly?
- did a real consumer use the result?
- were inconclusive zones rendered visibly?

### 5. `build-state-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- evidence profile
- lane profile
- linked `build-state-pack`, `impact-pack`, or `build-doctor-pack`
- scorecard
- optional raw attachments

## Ranked first pilots

### 1) Editor / CLI coexistence lane
**Why first**
- This is one of the most legible current pain points.
- The build-dir-layout goal explicitly names Cargo / rust-analyzer contention.
- It exercises layout, lock scope, duplication-by-policy, and workflow identity without waiting for future optimization work.

**Must prove**
- shared target/build-dir vs editor-private lane remains explicit;
- lock reports can distinguish blocking from intentional isolation;
- duplication is represented as policy or layout consequence, not just as a cache miss;
- Build Doctor can explain the tradeoff without inventing new facts.

**Primary consumers**
- local developers
- editor integrations
- build-triage issues

### 2) Private-change / relink-opportunity lane
**Why second**
- The Relink don’t Rebuild goal makes this strategically timely.
- It stress-tests the distinction between semantic interface change and observed rebuild scope.
- It gives the archive a way to talk about smarter future builds without pretending they already exist.

**Must prove**
- change slices and semantic classifications stay explicit;
- observed reverse-dependency rebuild scope can be attached;
- relink opportunity stays an opportunity report, not a success claim;
- private-item / comment / formatting changes are represented honestly.

**Primary consumers**
- maintainers evaluating build churn
- public-API / semver work
- change-impact / cache / doctor consumers

### 3) Workspace / CI exchange lane
**Why third**
- The build-dir-layout and user-wide-cache direction make cross-workspace and CI reuse strategically important.
- This is where coarse tarball cache stories should give way to entry-aware evidence.
- It helps keep storage cost, exchange policy, and reuse truth from collapsing into one blob.

**Must prove**
- local vs user-wide vs CI-remote lanes remain explicit;
- reuse rejection reasons are attachable;
- retention or exchange policy is reviewable;
- build-state evidence can explain why a CI cache felt stale or over-broad.

**Primary consumers**
- CI maintainers
- shared-cache experiments
- build-cache and policy tooling

### 4) Workflow-aware diagnosis lane
**Why fourth**
- Build Doctor becomes strategically valuable only once the lower layers are stable enough to ground it.
- This pilot proves suggestions can be evidence-backed instead of folklore-backed.

**Must prove**
- workflow profiles stay explicit;
- diagnoses cite imported cache and impact evidence instead of re-inventing it;
- suggestions render tradeoffs (debugger friendliness, coverage cost, isolation choices, nightly requirements) honestly;
- scorecards can say `INCONCLUSIVE` when observation quality is too weak.

**Primary consumers**
- build-triage docs/issues
- CI and local workflow tuning
- future build-performance education surfaces

### 5) Federated consumer lane
**Why fifth**
- High leverage, but only after the lower-level truth boundaries are proven.
- This is where release review, perf/resource review, semantic/editor consumers, and policy tooling can ingest the stack.

**Must prove**
- consumers can import linked packs without flattening them;
- dashboards or summaries remain visibly derived;
- conflicting evidence can stay conflicting.

**Primary consumers**
- perf/resource tooling
- policy/release stacks
- semantic/editor overlays

## Immediate archive consequences
Read this file together with:
- [`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md)
- [`design/build-cache-kit.md`](./build-cache-kit.md)
- [`design/change-impact-kit.md`](./change-impact-kit.md)
- [`design/build-doctor-kit.md`](./build-doctor-kit.md)
- [`design/cargo-report-kit.md`](./cargo-report-kit.md)
- [`design/perf-labs.md`](./perf-labs.md)
- [`design/resource-evidence-pilot-program.md`](./resource-evidence-pilot-program.md)
- [`design/repo-composition-stack.md`](./repo-composition-stack.md)

## Archive decision
Future build-state revisions should prefer:
- ranked pilots over universal build-health dashboards,
- reason-coded reports over cache folklore,
- linked packs over mega-schemas,
- and honest `INCONCLUSIVE` states over overconfident optimization stories.
