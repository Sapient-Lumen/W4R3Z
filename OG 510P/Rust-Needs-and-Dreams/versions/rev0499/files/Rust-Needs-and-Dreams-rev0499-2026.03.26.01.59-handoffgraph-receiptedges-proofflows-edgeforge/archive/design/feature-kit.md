# Design: Feature Kit (`cargo feature`, feature-report/v0)

## Goal
Make Cargo feature behavior **explainable and governable** by defining:
- a reference CLI (`cargo feature`),
- portable artifacts (`feature-report/v0`, `feature-diff/v0`),
- a policy language for feature discipline (minimal sets, unification mode, risky feature denylist).

This kit is designed to complement, not replace, existing commands like `cargo tree`.

## References (signals)
- Features reference (unification): https://doc.rust-lang.org/cargo/reference/features.html
- Edition guide (why features enabled via cargo tree): https://doc.rust-lang.org/edition-guide/rust-2021/default-cargo-resolver.html
- RFC 2957 (resolver): https://rust-lang.github.io/rfcs/2957-cargo-features2.html
- Cargo unstable knobs: https://doc.rust-lang.org/cargo/reference/unstable.html
- RFC 3692 feature unification controls: https://github.com/rust-lang/rfcs/blob/master/text/3692-feature-unification.md
- Workspace opt-out discussion: https://internals.rust-lang.org/t/feature-unification-opt-out-in-workspace-crate/20507

## Core UX: `cargo feature`
- `cargo feature report [--target <triple>] [--profile <name>]`
  - compute the effective feature set per package for the selected build
  - include “why chains” (which dependency edge enabled which feature)
  - output `feature-report/v0`
- `cargo feature diff <A> <B>`
  - diff two reports and highlight:
    - newly enabled features
    - newly activated optional dependencies
    - new proc-macro/build-dep features (higher risk)
- `cargo feature minimize [--target <triple>]`
  - attempt to compute a minimal feature set that still builds/tests:
    - run a search (binary search + heuristic)
    - produce a recommended feature set for workspace members
  - output `feature-minset/v0` with confidence and caveats
- `cargo feature policy check`
  - enforce org policy:
    - allowlists/denylists
    - max “feature delta” per PR
    - required unification mode settings (where available)
- `cargo feature explain <pkg> <feature>`
  - show the exact edge(s) and condition(s) that enabled it.

## Artifact: `feature-report/v0`
- subject:
  - workspace hash + toolchain + resolver version
  - build selection (target/profile)
- per package:
  - enabled features
  - optional deps activated
  - “why” evidence:
    - list of enabling edges (pkgA -> pkgB with feature flags)
  - scope tagging:
    - runtime / dev / build / proc-macro
- summary:
  - “feature count” and top growth contributors
  - risk flags (build/proc-macro feature changes)

## Artifact: `feature-minset/v0`
- recommended features for workspace crates to build a given target/profile
- notes:
  - features that appear required due to build scripts/proc macros
  - nondeterministic or environment-dependent features
- reproducibility hints:
  - pin toolchain, isolate env vars

## Policy model (minimal)
YAML:
- per workspace member:
  - allowed features
  - denied features
- global:
  - deny features for build/proc-macro deps unless allowlisted
  - max new optional deps per PR
- baseline:
  - store last-known-good `feature-report` hash and diff against it in CI

## Shared stack note
Treat this kit plus [`design/resolution-doctor-kit.md`](./resolution-doctor-kit.md) as the shared **Dependency Control Stack**, with [`design/dependency-control-stack.md`](./dependency-control-stack.md) and [`design/dependency-control-pilot-program.md`](./dependency-control-pilot-program.md) as the synthesis / rollout layer above them.

Design rule: **Feature Kit owns activation / unification / minimization truth; Resolution Doctor owns chosen-graph truth; API-boundary or policy conclusions stay downstream and explicit.**

## Integration points
- Policy Kit: ingest `feature-report/v0` to unify policy gates.
- Compile-Time Capabilities Kit: treat build/proc-macro feature drift as a risk signal.
- Perf Labs: correlate feature growth with binary size and build time regressions.

## Evaluation plan
- Corpus:
  - large workspaces with many optional deps
  - “feature creep” regressions in the wild
- Success criteria:
  - CI diffs are short and actionable.
  - minimize mode finds smaller feature sets for common cases without excessive compute time.
