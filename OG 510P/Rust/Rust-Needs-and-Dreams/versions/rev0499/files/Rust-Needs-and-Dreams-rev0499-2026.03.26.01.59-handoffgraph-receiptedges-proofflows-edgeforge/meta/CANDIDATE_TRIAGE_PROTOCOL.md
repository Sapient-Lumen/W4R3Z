# Candidate-triage protocol addendum (rev0426)

Use this protocol whenever a revision proposes a **new worthy contribution**, a new **frontier candidate**, or a large **portfolio reshuffle**.
Read it with `design/portfolio-selection-rubric-2026Q1.md`.

Default rule:
- every candidate must declare **ranking class**, **seam sentence**, **artifact-family sentence**, **pilot lane**, **imports / authority sources**, **steward story**, **anti-goals**, **fold trigger**, and **kill trigger**;
- if one of those is missing, the default outcome is **deepen existing seam**, **fold**, or **delay**, not promotion;
- and no candidate may enter the top band merely because it is timely, scary, or LLM-friendly.

# Candidate triage protocol

## Required candidate card
Every serious new proposal should answer these fields explicitly:

1. **Ranking class**
   One-project winner, portfolio component, specialist frontier, operational seam, or hidden multiplier.
2. **Seam sentence**
   One sentence naming the boundary and the adjacent imported layers.
3. **Artifact-family sentence**
   One sentence naming the canonical pack/report/receipt family or other bounded output.
4. **Pilot lane**
   One narrow workflow where the candidate proves itself.
5. **Imports / authority sources**
   The official or maintainer-authored inputs it relies on.
6. **Steward story**
   Who could plausibly keep it current.
7. **Anti-goals**
   What empire or adjacent layer it must not silently become.
8. **Fold trigger**
   What evidence would make it belong inside another seam.
9. **Kill trigger**
   What evidence would make the repo stop carrying it as a serious candidate.

## Default outcome policy
- Missing one or two fields: **delay**.
- Missing seam clarity or artifact family: **fold or kill**.
- Missing steward story: **delay** unless a sponsor-specific owner is explicit.
- Missing anti-goals or fold trigger: **deepen existing seam first**.

## Sync rule
If a candidate is promoted or materially re-ranked, update these together:
- `INDEX.md`
- `PRIORITIES.md`
- `STRATEGIC_FRONTIER.md`
- `RESEARCH_LOG.md`
- `AGENTS.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`
