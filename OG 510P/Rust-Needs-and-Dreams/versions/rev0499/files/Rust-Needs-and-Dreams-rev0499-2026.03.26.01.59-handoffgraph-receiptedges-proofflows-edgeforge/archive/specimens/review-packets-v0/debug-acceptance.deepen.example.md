# Specimen: Feedback / Debug Acceptance Commons packet (`deepen`)

Status: **illustrative specimen, not a live portfolio verdict**

## Identity
- candidate: **Feedback / Debug Acceptance Commons**
- macro-program: **Feedback / Debug Acceptance Commons**
- specimen role: `review-packet/v0`
- requested verdict: `deepen`

## Why now
- Debugging remains a meaningful productivity limiter in the 2025 State of Rust survey.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The debugging survey defines a clear capability bar: multiple debuggers across multiple OSes, visualizers, async support, and Rust expression evaluation.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The same survey-launch post says survey results will be evaluated and key insights posted later; as of March 23, 2026, that public results post is not yet visible on the Rust blog index.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
  https://blog.rust-lang.org/
- The March 2026 challenges post still names async as a recurring pain, which increases the importance of honest async-debug posture.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/

## Kernel and artifact family
- kernel: **tuple acceptance records + session/support packs + negative-state fixtures**
- first artifact family:
  - `debug-acceptance-card/v0`
  - `debug-session-pack/v0`
  - `tuple-status-matrix/v0`

## Stage / proof status
- current stage: **kernel proof only**
- earned proof:
  - pain is broad enough to matter;
  - capability targets are now explicit;
  - cross-tuple framing is validated.
- missing proof:
  - there is no public survey-results synthesis yet;
  - broad acceptance claims still need more fixture-backed tuple evidence.

## Practical decision improved
A maintainer, tool author, or support engineer can answer:
- which debugger / OS / async / expression-eval tuple is accepted,
- what is merely partial,
- and what session pack should be requested before escalation.

## Proving grounds
- debugger × operating-system tuple matrix
- async-heavy and non-async fixtures
- visualizer checks for common Rust types
- session-pack replay on known problem reports

## Negative states
- one debugger working well is not ecosystem acceptance;
- async support is explicitly incomplete today;
- unsupported tuples must remain visible;
- this is not yet ready for ecosystem-wide “good debugging story” rhetoric.

## Owner shape / upkeep
- first owner shape: **cross-tool steward group or consortium of debugger/tool maintainers**
- upkeep reality: fixture drift, debugger-version churn, OS coverage churn, replay support, visualizer upkeep

## Adjacency / refused larger forms
- beats: anecdotal “debugging is bad” summaries with no tuple matrix
- remains adjacent to: tool-specific debugger improvements
- refuses:
  - a single preferred debugger story
  - an acceptance claim without explicit unsupported states
  - verdict inflation before results and fixtures mature

## Bounded v0
A worthy v0 is:
- one tuple-status matrix,
- one session-pack grammar,
- one replay path,
- and one negative-state corpus.

## Expiry / reissue triggers
Reissue this packet if:
- the debugging survey results are published;
- one debugger meaningfully improves async or expression evaluation;
- or tuple evidence shows the area is ready to move from `deepen` to `advance`.

## Source candor
- debugging survey launch: **target-capability evidence, not final prevalence proof**
- survey results post: **not yet available publicly at packet time**
- challenges writeup: **broad async pain framing only**

## Packet judgment
Why `deepen` instead of `advance`:
- the kernel is right, but the proof surface is still too incomplete for a stronger widening story.
Why not `hold`:
- the candidate is not merely plausible; it already has a clear kernel and clearly current pain.
