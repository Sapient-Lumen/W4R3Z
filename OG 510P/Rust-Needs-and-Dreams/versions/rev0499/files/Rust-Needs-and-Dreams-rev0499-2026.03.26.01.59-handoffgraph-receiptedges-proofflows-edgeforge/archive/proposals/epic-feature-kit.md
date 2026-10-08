# Epic Proposal: Feature Kit (cargo feature)

## One-sentence pitch
Make Rust dependency features explainable, diffable, and governable—so feature creep becomes a reviewable change, not a surprise.

## Deliverables
- `cargo-feature` reference implementation
- Schemas:
  - `feature-report/v0`
  - `feature-minset/v0`
  - `feature-policy/v0`
- Algorithms:
  - efficient “why chain” extraction (from resolver/metadata)
  - minimization heuristics (search + caching)
- CI templates:
  - report + diff on PR
  - enforce policy gates
- Corpora + tests:
  - feature graph regression fixtures

## Why now
Cargo already documents feature unification and provides partial exploration tooling (cargo tree “why”).  
https://doc.rust-lang.org/cargo/reference/features.html  
https://doc.rust-lang.org/edition-guide/rust-2021/default-cargo-resolver.html

The resolver is an active design area (RFC 2957; feature unification controls proposed/under development).  
https://rust-lang.github.io/rfcs/2957-cargo-features2.html  
https://github.com/rust-lang/rfcs/blob/master/text/3692-feature-unification.md  
https://doc.rust-lang.org/cargo/reference/unstable.html

## Non-goals
- Replacing Cargo’s resolver
- Enforcing one feature policy for all crates
- Magic “minimal features” guarantees without testing (we provide best-effort + evidence)

## Milestones
1) v0: `feature-report/v0` + `diff` + `explain`
2) v0.2: policy gates + baseline workflow
3) v0.3: minimization mode + caching
4) v1: stable schemas + upstream integration proposal


## Stack posture
Treat this proposal as one half of the shared **Dependency Control Stack** with the companion kit. The synthesis and rollout layer lives in [`design/dependency-control-stack.md`](../design/dependency-control-stack.md) and [`design/dependency-control-pilot-program.md`](../design/dependency-control-pilot-program.md). The stack must keep chosen-graph truth, feature/unification truth, and downstream API/policy handoffs distinct instead of flattening them into one dependency-health verdict.
