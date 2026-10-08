# Review packet specimen protocol

## Goal
Use this protocol when the repo is changing the **reference review-packet specimens** that teach future revisions what an honest filled-out packet looks like.

This protocol exists because the archive already has:
- packet theory (`meta/PROGRAM_REVIEW_PACKET_PROTOCOL.md`),
- broad specimen rules (`meta/SPECIMEN_CORPUS_PROTOCOL.md`),
- stage gates, charters, and reference architectures,
- and many strong seam-local notes.

The next failure mode is smaller and more dangerous:
> future revisions claim to use review packets while silently changing verdict burden, source candor, or packet shape from one revision to the next.

Read with:
- `design/epic-contribution-review-packet-specimens-2026Q1.md`
- `design/epic-contribution-review-packets-2026Q1.md`
- `meta/PROGRAM_REVIEW_PACKET_PROTOCOL.md`
- `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- `specimens/review-packets-v0/README.md`

## Use this protocol when
Use this protocol when a revision:
- adds a new review-packet specimen;
- refreshes an existing specimen verdict posture;
- changes the standard packet sections a specimen must show;
- or updates packet-source-candor rules after new ecosystem evidence or archive hygiene lessons.

Do not use this protocol for:
- live candidate verdicts in the current revision;
- routine citation refreshes that do not change specimen behavior;
- or generic archive prose edits that leave the specimen corpus untouched.

## Current specimen corpus (rev0480)
1. `specimens/review-packets-v0/build-state-evidence.advance.example.md`
2. `specimens/review-packets-v0/debug-acceptance.deepen.example.md`
3. `specimens/review-packets-v0/navigation-defaults.hold.example.md`
4. `specimens/review-packets-v0/package-intake.advance.example.md`

## Required truths for every packet specimen
Every specimen packet must make these things obvious:

1. **Packet identity**
   - reviewed candidate;
   - macro-program / seam;
   - specimen role;
   - requested verdict;
   - explicit non-live / illustrative status.

2. **Standard packet spine**
   - why-now signals;
   - kernel and artifact family;
   - stage / proof status;
   - decision improved;
   - proving grounds;
   - negative states;
   - owner shape / upkeep;
   - adjacency / refused larger forms;
   - bounded v0;
   - expiry / reissue triggers.

3. **Source candor**
   - which sources are operational or contractual;
   - which are prototype / roadmap signals;
   - which are surveys or syntheses;
   - which are governance or support-lane realism;
   - and what those source classes are *not* strong enough to prove.

4. **Inference boundaries**
   - what the packet imports directly from sources;
   - what the archive infers from those sources;
   - what remains uncertain or unpublished;
   - and what stronger evidence would change the verdict.

5. **Verdict honesty**
   - why the chosen verdict is justified;
   - why adjacent stronger or weaker verdicts were refused;
   - and what next event would cause re-issue.

## Provenance rule
If a source itself carries a material caveat about how it was produced, scoped, or later revised, the specimen must surface that caveat where it materially affects packet trust.

Current live example:
- the March 2026 Rust challenges writeup includes an author's note that the original version was retracted because readers felt the LLM-assisted draft sounded empty and uncomfortable.
- if a specimen leans on that source for broad pain framing, it must keep the source in the **synthesis / framing** lane and must not silently upgrade it into quote-grade proof for exact prevalence or operational claims.

## Minimum anti-cheating rules
A packet specimen fails this protocol if it:
- presents itself as a live verdict rather than an example;
- hides missing proof just because the candidate is strategically important;
- omits negative states or unsupported tuple states to make the packet cleaner;
- reuses current-source language without carrying the source's caveats;
- uses prototype-goal text as if it were a stable interface contract;
- or smooths over uncertainty with generic confident prose.

## When to update the corpus
Update the packet-specimen corpus only when one of these is true:
- the packet spine changed materially;
- a verdict posture now needs a different canonical example;
- a current specimen would now teach the wrong inference boundary or source-candor habit;
- or a major archive hygiene lesson makes the old specimen misleading.

Do **not** add a new specimen merely because a new top-band idea appeared.
Prefer deepening existing specimens unless a genuinely new verdict posture or evidence class is required.

## Required maintenance in the same revision
If a specimen packet changes, the same revision should also update:
- `specimens/README.md`
- `meta/SPECIMEN_CORPUS_PROTOCOL.md` if corpus scope changed materially
- `meta/LATEST_REVISION_FILESET.md`
- `RESEARCH_LOG.md`
- `meta/ARCHIVE_MANIFEST.md`
- mirror copies under `archive/`

## Default routing rule
If a future revision asks “what should a *real* packet for this candidate look like?” it should start from the nearest packet specimen before inventing new local packet grammar.
