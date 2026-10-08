# Current decision packet: Safety-Critical + Institutional Readiness Commons (`deepen`)

Status: **live current-decision packet**

## Identity
- candidate: **Safety-Critical + Institutional Readiness Commons**
- macro-program: **Safety-Critical + Institutional Readiness Commons**
- packet role: `live-decision-packet/v0`
- requested verdict now: `deepen`

## Why now
- The safety-critical writeup says Rust's compiler guarantees help, but ecosystem support thins out quickly as systems move beyond prototyping into higher-criticality work.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The same writeup highlights missing ecosystem support such as code generation, evidence-friendly tooling, dependency lifecycle guidance, async qualification posture, and interop patterns.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The March 2026 challenges framing still says the biggest issue for safety-critical developers is immature tooling for certification.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2026 goals overview keeps the goal process anchored in owner/champion/team agreements, which matters for any readiness commons that needs institutional hosts.
  https://rust-lang.github.io/rust-project-goals/2026/
- Rust in 2026 includes flagship work on sanitizer support and public/private dependencies, both relevant to evidence and qualification posture.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Practical decision improved
A stewarded consortium or institutional user could answer:
- what readiness checklist applies to a given target/runtime/profile,
- what evidence recipe exists,
- what dependency-lifecycle and interop posture is acceptable,
- and which areas remain explicitly unsupported for higher-assurance use.

## Bounded next move
Deepen toward one shared commons:
- target-profile readiness cards
- evidence-recipe bundles
- dependency-lifecycle playbooks
- async/runtime qualification posture notes
- interop/audit boundary cards

Do not widen into certification claims or one-size-fits-all compliance promises.

## Earned proof
- the need is repeatedly and explicitly articulated;
- real industrial interest exists;
- the right shape is clearly a commons/playbook/evidence-recipe family rather than a single crate.

## Missing proof / blockers
- the right long-term host and coalition shape still needs stronger evidence;
- evidence recipes and target profiles are still under-specified;
- the burden of maintaining qualification-friendly guidance remains high.

## Negative states and caveats
- readiness is domain-, target-, and assurance-level-specific;
- higher-criticality claims need much stronger evidence than this archive currently carries;
- some needed pieces live outside the Rust ecosystem entirely.

## Owner shape / upkeep
- best first owner: consortium, institutional alliance, or multi-company steward group
- upkeep tax: standard/profile tracking, evidence recipe maintenance, target-specific caveat renewal

## Refused larger forms
- certification theater
- one-crate “safety” answer
- pretending demand alone solves stewardship and evidence burden

## Reissue triggers
- stronger institutional host signals appear
- new flagship or ecosystem work materially changes the readiness substrate
- a credible target-profile evidence corpus appears

## Source candor
- safety-critical writeup: strongest current problem-shape evidence
- goals overview and flagships: program and substrate direction, not certification proof
- challenges post: broad framing only

## Decision rationale
`deepen` is the honest verdict because the seam is real and important, but the next step is still a stewarded evidence commons, not a stronger launch claim.
