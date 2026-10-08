# Broad synthesis dedup protocol

## Goal
The archive is now large enough that a weak failure mode is not bad ideas but **duplicate broad synthesis**:
new notes that restate the top band in slightly different words, create fresh continuity burden, and make future assistants diff too much prose before they can do useful work.

This note defines how to avoid that failure mode.
It is about **how to edit the archive**, not about which Rust contribution ranks first.

Read with:
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`
- `meta/LATEST_REVISION_FILESET.md`
- `design/territory-priority-refresh-2026Q1.md`
- `design/practical-epic-contribution-briefs-2026Q1.md`
- `design/epic-contribution-program-stack-2026Q1.md`

## Default rule
A revision should add a new broad synthesis note **only if a clearly missing comparison or construction layer exists**.
If the answer can be expressed by deepening an existing execution blueprint, refreshing routing, or extending an existing broad synthesis note, prefer that instead.

## Broad-note classes
Before creating or rewriting a broad synthesis note, classify the change as exactly one primary type:
- **ranking refresh**
- **comparative axis** (proof burden, decision rights, reversibility, renewal burden, learning clock, etc.)
- **practical build shape**
- **program-stack / pruning / repo-construction layer**
- **frontier promotion**
- **meta-hygiene / continuity**

Do not let one revision pretend to be all of them unless it truly changes all of them.

## The current front-door broad notes
For broad “what should ideal Rust build?” questions, the default front-door sequence is now:
1. `design/territory-priority-refresh-2026Q1.md`
2. `design/epic-contribution-scorecards-2026Q1.md`
3. `design/practical-epic-contribution-briefs-2026Q1.md`
4. `design/epic-contribution-program-stack-2026Q1.md`

Interpretation:
- use **territory priority refresh** for the broad portfolio answer;
- use **scorecards** for side-by-side comparison discipline;
- use **practical briefs** for honest contribution shape;
- use **program stack** for folding, pruning, and worthy-repo construction.

If a proposed new note does not clearly add a new layer beyond those four, it should usually not exist.

## Dedup rules
1. **One new broad synthesis note per revision is the default upper bound.**
   A second new broad note in the same revision should be rare and usually meta-only.
2. **If the change is seam-local, update the seam-local execution blueprint instead.**
3. **If the change is mostly pruning or merge guidance, update the program-stack note or routing, not the broad ladder.**
4. **If the change is mostly “what did we touch?”, update `meta/LATEST_REVISION_FILESET.md` and the research log, not the design canon.**
5. **If the change is only a new source or freshness anchor, update the source atlas or research log unless the interpretation truly changed.**

## Mandatory fold/refusal paragraph
Any new broad synthesis note must leave behind a short explicit statement of:
- what got folded under stronger parents;
- what got refused as wrong-shaped;
- and what stayed unchanged.

If those three things are missing, the note is incomplete even if the prose sounds smart.

## Mandatory routing updates when a broad note is added
When a new broad synthesis note is introduced, refresh at least:
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/LATEST_REVISION_FILESET.md`
- `RESEARCH_LOG.md`

That is the minimum continuity tax for adding another front-door answer surface.

## Prohibited failure patterns
- creating a new “top missing things in Rust” note that only rephrases existing rank order;
- creating a new “epic bets” note that forgets to say what was folded or refused;
- leaving a broad note un-routed, so only the author knows it exists;
- using assistant summaries or private context as a reason to skip changed-files continuity;
- treating “more comprehensive” as automatically “more canonical”.

## Healthy revision heuristic
A broad synthesis revision is healthy if a later assistant can answer all of these quickly:
- what new question this note answers that older notes did not;
- which older broad notes still matter;
- which seams were folded under stronger parents;
- which attractive ideas were refused; and
- which files changed because of the new note.

If those answers are hard to recover, the note likely should have been a routing refresh or blueprint deepening instead.

