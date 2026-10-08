# Live decision-packet protocol (rev0482)

Use this protocol when the archive needs a **current explicit verdict artifact** for a real candidate.
Read it with:
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `design/epic-contribution-review-packets-2026Q1.md`
- `design/epic-contribution-review-packet-specimens-2026Q1.md`
- `meta/CANDIDATE_DOSSIER_PROTOCOL.md`
- `meta/PROGRAM_REVIEW_PACKET_PROTOCOL.md`
- `meta/REVIEW_PACKET_SPECIMEN_PROTOCOL.md`

## Default rule
A live decision packet is the archive's **now-decision artifact** for a real candidate.
It should only be written when the repo wants to say what verdict it would stand behind now, using fresh evidence and bounded next steps.

If a revision is talking about a top candidate in present-tense verdict language but leaves no live packet, treat the revision as under-specified.

## Required fields
Every live decision packet should say:
1. **identity** — candidate, macro-program, packet role;
2. **requested verdict now** — the current decision the archive would endorse;
3. **why now** — fresh sources making the packet timely;
4. **practical decision improved** — what concrete decision gets better;
5. **bounded next move** — the exact step that follows if the verdict is accepted;
6. **earned proof** — what the candidate has already earned;
7. **missing proof / blockers** — what blocks a stronger verdict;
8. **negative states / caveats** — what remains partial, unstable, unsupported, or stale;
9. **owner shape / upkeep** — who could actually carry the next step;
10. **refused larger forms** — what empire or premature launch form is still out of bounds;
11. **reissue triggers** — what change should force a packet rewrite;
12. **source candor** — what each source family is and is not proving.

## Packet construction order
Default construction order:
1. read the nearest dossier;
2. read the nearest packet specimen with matching verdict posture;
3. import fresh source anchors;
4. write the live packet;
5. update the dossier only if the packet materially changed the current posture.

## When to write a live decision packet instead of only refreshing a dossier
Prefer a live decision packet when:
- the candidate is already in the top band;
- the archive wants to show the actual verdict artifact a maintainer should read now;
- the revision is making or preserving a current explicit verdict;
- or a future revision would otherwise need to reconstruct the verdict from several notes.

## When a live decision packet is too much
Do not write a live decision packet when:
- the revision is only doing broad ranking or macro-program synthesis;
- the candidate is still speculative and lacks a stable identity;
- the repo only needs a current working card and not a current verdict artifact;
- or the evidence is so stale that even a dossier refresh would be premature.

## Verdict discipline
A live packet must be explicit about why its verdict is **not** a stronger one.
Examples:
- if it says `advance`, it should say why the next move is bounded enough to avoid `deepen` or `hold`;
- if it says `deepen`, it should say what missing proof blocks `advance`;
- if it says `hold`, it should say what would have to change before movement becomes honest.

## Freshness discipline
A live packet should prefer the freshest authoritative source in each lane.
At minimum:
- stable docs for current stable contracts;
- goals pages and development-cycle posts for in-flight direction;
- survey/blog posts for current pain framing;
- advisory/update posts for supply-chain or operator reality.

If one source is known to have a caveat, the packet must say so.
This is especially important for broad framing posts whose own authors flagged limits or retractions.

## Corpus scope
The default corpus is the current top band only.
Do not create a sprawling packet forest.
A packet corpus should stay small enough that every file is plausibly refreshable.

## Required same-revision updates
A live decision-packet revision should usually also refresh:
- `packets/README.md`
- `packets/top-band-v0/README.md`
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `STRATEGIC_FRONTIER.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/LATEST_REVISION_FILESET.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`
- `RESEARCH_LOG.md`

If sources became load-bearing, refresh the source atlas too.

## Non-goals
This protocol does not authorize:
- silent reranking;
- replacing dossiers with packets;
- treating specimen packets as live packets;
- or claiming a verdict is evergreen after upstream conditions moved.
