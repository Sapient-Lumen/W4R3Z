# Program spec deepening protocol

## Goal
The archive now has enough ranking, practical-shape, and macro-program notes that a new failure mode has become obvious:
future revisions can keep talking about strong programs without saying what those programs actually contain.

This protocol exists for a narrower question:

> when a revision deepens a serious macro-program or execution blueprint, what minimum spec-first fields must it answer so the result becomes more buildable instead of more rhetorical?

Read with:
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/epic-contribution-program-stack-2026Q1.md`
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-proving-grounds-2026Q1.md`
- `design/portfolio-anchor-corpus-2026Q1.md`
- `design/portfolio-exemplar-federation-2026Q1.md`
- `meta/BROAD_SYNTHESIS_DEDUP_PROTOCOL.md`
- `meta/LATEST_REVISION_FILESET.md`

## Default rule
After the broad ladder, practical build menu, and macro-program grouping are already known, the default next move should be **program-spec deepening**, not another broad summary.

A revision should add a new broad synthesis note only if a clearly missing comparison layer exists.
Otherwise it should usually deepen an existing macro-program or seam-local execution blueprint.

## Required program-spec questions
Any serious deepening note for a macro-program or top seam should answer all of these explicitly:
1. **Kernel** — what smallest artifact family or commons is being proposed?
2. **Import surfaces** — which upstream, service, or companion surfaces does it import, and with what caveats?
3. **Proof assets** — which specimens, fixtures, anchors, exemplars, or validators make the idea reviewable?
4. **Proving grounds** — what scenario families must it survive before widening?
5. **Bounded v0** — what does the first honest version do, and what does it deliberately not do?
6. **Exit criteria** — what must be true before the program widens or becomes default-looking?
7. **Wrong shape refusal** — what seductive build shape must be refused early?

If one of those seven is missing, the note is incomplete even if the prose sounds persuasive.

## Preferred section template
A healthy program-spec note should usually contain, in order:
- goal / question answered;
- why this deepening is merited now;
- headline answer;
- cross-program or cross-seam rules if any;
- one section per program or seam with the seven required questions;
- what got folded, refused, and left unchanged;
- recommended next repo move.

## What counts as proof assets
Program-spec deepening should strongly prefer explicit proof assets such as:
- `specimens/` examples;
- `fixtures/` invalid or lossy cases;
- `proofgrounds/` scenario matrices;
- anchor profiles;
- exemplar federations;
- validators or doctor/check scripts.

A note that says “we should validate this somehow later” is not yet a spec-first deepening.

## What does not count
These do **not** count as sufficient program specification on their own:
- a rank rewrite;
- a vibes-based framework suggestion;
- a hosted product mockup;
- a fresh top-ten list;
- an assistant summary that omits imports, proof assets, or refusal clauses.

## Routing rule
When a revision adds a new program-spec note, refresh at least:
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/LATEST_REVISION_FILESET.md`
- `RESEARCH_LOG.md`

Update `STRATEGIC_FRONTIER.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, and `meta/AMNESIA_RESISTORS.md` when the new note changes how future revisions should behave.

## Prohibited failure patterns
- adding a new macro-program note that still has no kernel artifact family;
- describing imports as if they were stable canon when they are prototypes or best-effort hints;
- widening from editorial confidence instead of proof assets;
- treating a cloud portal or dashboard as the first implementation by default;
- forgetting to say what wrong shape is being refused.

## Healthy revision heuristic
A program-spec deepening revision is healthy if a later assistant can recover quickly:
- what new question this note answers;
- which existing program or seam it deepens;
- what the v0 actually ships;
- what proof assets must exist;
- what proving grounds remain;
- and what build shape was explicitly refused.

If those answers are hard to recover, the revision likely added rhetoric faster than structure.

