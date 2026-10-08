# Current decision packet: Navigation / Defaults / Claims Commons (`hold`)

Status: **live current-decision packet**

## Identity
- candidate: **Navigation / Defaults / Claims Commons**
- macro-program: **Navigation / Defaults / Claims Commons**
- packet role: `live-decision-packet/v0`
- requested verdict now: `hold`

## Why now
- The March 2026 challenges framing still says developers struggle to know which crates they need, which they can trust, and which are the best fit, while some domains remain immature.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey still says the docs are the canonical reference even as some people appear to be shifting questions toward LLM tooling.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io continues to add security and provenance-facing signals, but those do not automatically answer recommendation or default-selection questions.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/

## Practical decision improved
In its strongest form, this seam would help teams answer:
- which conservative lane default to start from,
- what claim strength a recommendation is actually making,
- and when a default card is too stale to trust.

## Bounded next move
Hold the broad build.
Only continue:
- narrow lane-default cards,
- explicit claim grammar,
- freshness receipts,
- and renewal queues.

Do not widen into a public winner table, ecosystem portal, or generalized recommendation engine.

## Earned proof
- the problem is real;
- the archive already knows how a careful lane-default corpus should look;
- docs, atlas, and claim-grammar work remain useful internal substrate.

## Missing proof / blockers
- renewal burden is still the main blocker;
- the archive does not yet have evidence that it can keep a broader recommendation layer fresh enough to deserve more authority;
- public ranking claims would outrun current maintenance capacity.

## Negative states and caveats
- any recommendation layer drifts quickly;
- source signals help route attention but do not fully prove “best choice” status;
- LLM-mediated learning makes freshness and claim-strength labeling even more important.

## Owner shape / upkeep
- best first owner: small editorial/steward team willing to pay recurring renewal cost
- upkeep tax: freshness checks, claim-strength review, lane updates, deprecation receipts

## Refused larger forms
- crate winner tables
- portal or marketplace empire
- pretending provenance signals equal adoption guidance

## Reissue triggers
- the repo proves it can renew a meaningful defaults corpus over time
- crates.io or official docs grow a stronger default-selection substrate
- a narrower recommendation lane shows unusual leverage with sustainable upkeep

## Source candor
- challenges and survey sources: need framing, not recommendation proof
- crates.io update: provenance/security signal evidence, not fit-for-purpose ranking proof

## Decision rationale
`hold` is the honest verdict because the need is real, but the limiting factor is not missing insight. It is renewal capacity and claim discipline.
