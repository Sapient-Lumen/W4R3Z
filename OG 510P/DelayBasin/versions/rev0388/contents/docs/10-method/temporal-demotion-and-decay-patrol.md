# Temporal demotion and decay patrol

## Claim

Promotion contracts are necessary but not sufficient.
A long-run archive also needs a compact **decay patrol**: a way to mark which canon-level claims are likely to go stale, when they should be re-reviewed, and what kind of failure should demote them.

The practical point is small and harsh:
**canon must not be allowed to stay trusted merely because it has survived in the repo.**

## Why this pressure appeared

Several recent memory / reliability papers converge on the same systems point from different directions:

- A-MAC treats retention as a structured admission problem using future utility, factual confidence, novelty, temporal recency, and content-type prior. It explicitly warns that retaining outdated information can propagate errors, and finds content-type prior especially influential. ([`REF-0040`](../00-meta/bibliography.md))
- MMA scores retrieved memory items by source credibility, temporal decay, and conflict-aware consensus, then reweights or abstains when support is weak. ([`REF-0044`](../00-meta/bibliography.md))
- The AI-assisted engineering temporal-validity paper reports that 20–25% of architectural decisions in its retrospective audit had stale evidence within two months and argues for automated evidence-decay tracking. ([`REF-0041`](../00-meta/bibliography.md))
- Continuum Memory Architectures argues that indefinite persistence and read-only retrieval are structural defects for long-horizon systems; memory must be able to mutate, decay, and consolidate. ([`REF-0045`](../00-meta/bibliography.md))

Taken together, these do not merely say “freshness matters.”
They say **indefinite unreviewed persistence is an architectural bug**.

## Archive-native translation

DelayBasin should distinguish at least three temporal postures:

1. **persistent-method**
   - low expected temporal drift
   - examples: house rules, invariant discipline, quarantine requirement
2. **medium-horizon mechanism**
   - may remain useful for weeks or months but is exposed to rapid literature motion
   - examples: specific memory-architecture syntheses, protocol analogies, admission-control imports
3. **short-horizon externality**
   - depends heavily on current products, current papers, or unstable ecosystem facts
   - examples: claims about which tools/models/protocol revisions are load-bearing right now

This does not mean every claim needs ceremony.
It means the archive should preserve which canon-level surfaces deserve a scheduled skeptical look.

## Minimal design

DelayBasin therefore adds a **decay watch registry**.
It is intentionally compact.
For each watched claim/surface, preserve only:

- target id,
- temporal posture,
- review horizon,
- what should trigger re-review or demotion,
- and where the review should land.

This is not a scheduling system.
It is a compact anti-amnesia surface for future re-entry.

## Why this belongs in canon

This is not only a speculation about transformers.
It is a direct design consequence for the repo.
Once canon includes live mechanism syntheses tied to recent literature, the archive needs a way to say:

- this is central,
- this is currently admissible,
- and this is exactly the kind of thing that may rot fastest.

Without that, promotion contracts still allow **temporal laundering**: something once promoted can masquerade as durable merely by remaining legible.

## Counterpressure

There is a real failure mode here:

- too much decay bookkeeping becomes ritual;
- the archive bloats;
- future sessions spend their time servicing timers rather than thinking.

So the right move is not a universal bureaucracy.
It is a **small watchlist for the hottest canon-level claims**.

## Current design consequence

This revision treats temporal demotion as a first-class continuation concern:

- promotion contracts say how trust rises;
- decay patrol says how trust should cool;
- quarantine remains the protected lane for ideas not ready for canon at all.
