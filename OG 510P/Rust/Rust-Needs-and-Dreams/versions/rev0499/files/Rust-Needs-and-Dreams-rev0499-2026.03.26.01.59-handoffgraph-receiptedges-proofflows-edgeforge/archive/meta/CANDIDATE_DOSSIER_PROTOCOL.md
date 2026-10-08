# Candidate-dossier protocol (rev0481)

Use this protocol when the archive needs to preserve the **current working posture** of a top-band candidate without writing a fresh broad synthesis note or a full live packet.
Read it with:
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `design/epic-contribution-review-packets-2026Q1.md`
- `design/epic-contribution-review-packet-specimens-2026Q1.md`
- `meta/PROGRAM_REVIEW_PACKET_PROTOCOL.md`
- `meta/REVIEW_PACKET_SPECIMEN_PROTOCOL.md`

## Default rule
A dossier is the archive's **live working card** for a real candidate.
It should be refreshed when the candidate's current posture matters, but the revision does not yet justify a new broad note or a new live packet.

If the archive keeps having to reconstruct a top candidate from scattered notes, the dossier layer is stale.

## Required dossier fields
Every dossier should say:
1. **identity** — candidate name and macro-program;
2. **current archive posture** — `advance`, `deepen`, `hold`, or stricter;
3. **why now** — current public signals that still make the seam load-bearing;
4. **next concrete move** — v0, packet, proving ground, or owner action;
5. **earned proof** — what the candidate has already earned;
6. **missing proof** — what still blocks a stronger verdict;
7. **owner shape / upkeep reality** — who could actually keep it alive;
8. **refused larger forms** — what empire the candidate must not become;
9. **reissue triggers** — what upstream or ecosystem change should force a refresh;
10. **source candor** — what each main source lane is and is not proving.

## When to refresh a dossier instead of adding a broad note
Prefer a dossier refresh when:
- the broad ladder is unchanged;
- the candidate is already in the top band;
- the revision is really about current posture, not new territory;
- a packet specimen already exists but the live posture moved;
- or fresh sources changed the candidate's near-term action, not the whole map.

## When a dossier is insufficient
A dossier is not enough when:
- the broad ranking changes;
- the candidate needs a new macro-program or charter model;
- the revision is making a real portfolio verdict now and needs a live packet;
- or the archive has discovered a new cross-cutting failure mode that needs design- or meta-level canon.

## Sync rule
If you add or materially refresh dossiers, also update:
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `RESEARCH_LOG.md`
- `STRATEGIC_FRONTIER.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/LATEST_REVISION_FILESET.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

If the sources became load-bearing, refresh `atlases/portfolio-source-atlas-v0/sources.json` too.

## Anti-drift rules
- Do not treat dossiers as permanent truth; they expire.
- Do not let a dossier silently inherit a specimen's verdict without fresh evidence.
- Do not widen the dossier corpus unless a real top-band candidate is missing.
- Do not let a dossier replace a packet when the repo is actually changing its mind.
