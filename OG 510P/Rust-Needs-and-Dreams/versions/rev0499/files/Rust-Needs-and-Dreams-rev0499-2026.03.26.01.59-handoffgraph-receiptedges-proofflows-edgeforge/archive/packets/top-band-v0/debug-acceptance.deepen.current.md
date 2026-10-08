# Current decision packet: Feedback / Debug Acceptance Commons (`deepen`)

Status: **live current-decision packet**

## Identity
- candidate: **Feedback / Debug Acceptance Commons**
- macro-program: **Feedback / Debug Acceptance Commons**
- packet role: `live-decision-packet/v0`
- requested verdict now: `deepen`

## Why now
- The 2025 State of Rust survey still reports debugging as a meaningful productivity limiter.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 debugging survey frames the target explicitly: debugger support across multiple debuggers and OSes, quality visualizers, first-class async debugging, and Rust expression evaluation.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The March 2026 challenges writeup still keeps async and domain-specific debugging pain visible, especially for embedded and other constrained contexts.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/

## Practical decision improved
A team deciding whether Rust debugging support is good enough for a workflow can answer:
- which debugger/OS/toolchain tuples are actually supported,
- which tuples are partial or regressed,
- whether async and visualizer support is acceptable for the target workflow,
- and what support bundle should be exported when filing issues or comparing tools.

## Bounded next move
Deepen toward one explicit acceptance commons:
- tuple matrix receipts
- session/export pack format
- async-debug posture cards
- visualizer and expression-evaluation support ledgers

Do not widen past a cross-tool acceptance corpus yet.

## Earned proof
- the pain is public and current;
- the quality target is explicitly articulated by the Rust project;
- the problem clearly exceeds a single debugger fork or one blog post.

## Missing proof / blockers
- survey results were not yet published when this packet was written;
- tuple coverage data is still too scattered;
- the corpus needs real unsupported-state visibility before an `advance` verdict would be honest.

## Negative states and caveats
- this is a cross-debugger and cross-OS problem, not one tool problem;
- async support and Rust-expression evaluation are still acknowledged gaps;
- embedded and other constrained domains likely need stricter tuple labeling than general desktop/server workflows.

## Owner shape / upkeep
- best first owner: steward group spanning compiler/debug-info maintainers, debugger contributors, and heavy users
- upkeep tax: tuple refresh, regression tracking, support-pack maintenance, issue routing

## Refused larger forms
- one debugger fork as the whole answer
- generic “developer experience” umbrella with no tuple truth
- claiming `advance` before results and acceptance receipts exist

## Reissue triggers
- debugging survey results are published
- a debugger or compiler initiative materially changes tuple support
- a real cross-tool support-pack corpus appears

## Source candor
- survey launch post: target-state and acknowledged-gap evidence, not solution proof
- State of Rust survey: pain framing, not tuple matrix truth
- challenges writeup: broad framing only, especially given its author caveat

## Decision rationale
`deepen` is the honest verdict because the seam is real and strategically important, but the packet still lacks the results corpus and tuple receipts that would justify `advance`.
