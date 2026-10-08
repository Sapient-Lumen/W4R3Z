# Program charter protocol

## Goal
After the archive gained ranking notes, practical build-shape notes, macro-program grouping, and program-spec deepening, the next predictable failure mode became easy to name:

> a revision can describe a strong program technically, but still leave its **owner shape**, **residency**, **pilot partners**, **maintenance envelope**, and **narrow upstream asks** vague enough that the idea remains socially or operationally unreal.

This protocol exists to keep future revisions from calling a program “practical” while leaving the launch charter unwritten.

Read with:
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/portfolio-execution-sequencing-2026Q1.md`
- `design/epic-contribution-decision-rights-map-2026Q1.md`
- `design/epic-contribution-support-bundle-map-2026Q1.md`
- `design/epic-contribution-renewal-burden-map-2026Q1.md`
- `meta/PROGRAM_SPEC_DEEPENING_PROTOCOL.md`
- `meta/LATEST_REVISION_FILESET.md`

## Default rule
After the broad ladder, practical build menu, macro-program grouping, and reference architecture are already known, the default next move for a serious top program should often be **charter deepening**, not another broad summary.

A revision should add a new broad synthesis note only if a genuinely missing comparison layer exists.
Otherwise it should usually deepen an existing top program with a real launch charter.

## Required charter questions
Any serious charter-deepening note for a macro-program or top seam should answer all of these explicitly:
1. **Residency** — where does the first honest implementation live?
2. **Owner shape** — who is on point for shipping and renewal?
3. **Pilot-partner profile** — which proving partners make the first results believable?
4. **First shipset** — what artifact bundle actually ships in v0?
5. **Maintenance envelope** — what recurring care is assumed before widening?
6. **Narrow upstream asks** — what minimal hooks, reviews, or collaborations are justified later?
7. **Graduation / fold / kill rules** — what makes the program widen, fold under another layer, or stop?
8. **Wrong launch pattern to refuse** — what seductive organizational or product shape must be rejected early?

If one of those eight is missing, the note is incomplete even if the prose sounds concrete.

## Preferred section template
A healthy charter note should usually contain, in order:
- goal / question answered;
- why charter deepening is merited now;
- headline answer;
- cross-program charter rules;
- one section per program or seam with the eight required questions;
- what got folded, refused, and left unchanged;
- recommended next repo move.

## What counts as owner shape
Charter deepening should strongly prefer explicit owner forms such as:
- one technical lead plus one adjacent champion;
- one steward pair;
- one operator-plus-maintainer pair;
- one editorial steward plus maintainer-review network;
- one consortium with named company maintainers and a Rust Project liaison.

These do **not** count as owner shape on their own:
- “the community”
- “upstream”
- “the ecosystem”
- “someone should fund this”
- “the Foundation”
- “maintainers will figure it out later”

## What counts as residency
A charter should say whether the first honest home is:
- companion-first tool / command / schema repo;
- cross-tool commons;
- editorial corpus;
- operator bridge;
- consortium / readiness commons;
- or genuine upstream/stabilization work.

Do not answer residency with a vague aspiration like “wherever it makes sense”.

## What does not count
These do **not** count as sufficient charter work on their own:
- a rank rewrite;
- a reference architecture with no owner or proving partners;
- a funding ask with no maintenance envelope;
- a hosted product mockup;
- a broad portal or framework fantasy;
- a note that says “we should collaborate somehow later”.

## Routing rule
When a revision adds a new charter note, refresh at least:
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/LATEST_REVISION_FILESET.md`
- `RESEARCH_LOG.md`

Update `STRATEGIC_FRONTIER.md`, `meta/ACTIVE_FRONTIER.md`, `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, and `meta/AMNESIA_RESISTORS.md` when the charter note changes how future revisions should behave.

## Prohibited failure patterns
- adding a “practical” program note with no owner shape;
- pretending a coalition-grade seam can be launched by one unnamed maintainer;
- asking upstream to absorb a whole product before the companion-first version proves value;
- treating funding as a substitute for review lanes, pilot partners, or maintenance;
- letting a hosted portal, score surface, or dashboard become the default launch pattern;
- forgetting to say what conditions would fold or kill the program.

## Healthy revision heuristic
A charter-deepening revision is healthy if a later assistant can recover quickly:
- where the program should live first;
- who is supposed to maintain it;
- which pilot partners matter;
- what the v0 artifact bundle is;
- what recurring care the program assumes;
- what minimal upstream asks are justified later;
- what would make the program widen, fold, or stop;
- and what launch pattern was explicitly refused.

If those answers are hard to recover, the revision likely added rhetoric faster than execution realism.

