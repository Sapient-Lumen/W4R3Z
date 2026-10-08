# Source hierarchy, conflict, refresh, and current-law routing

## Question in one sentence

When sources conflict or become stale, how should the cube distinguish current law, official guidance, empirical evidence, news reports, advocacy claims, and speculative frontier work without citation theater?[S59][S594]

## Companion routes

Use this route with:

- [`decision-procedure.md`](decision-procedure.md)
- [`open-questions.md`](open-questions.md)
- [`cube-lifecycle-pruning-route-retirement-and-axis-hygiene-routing.md`](cube-lifecycle-pruning-route-retirement-and-axis-hygiene-routing.md)
- [`../20-calibration/cube-lifecycle-pruning-route-retirement-and-evidence-refresh-ladder.md`](../20-calibration/cube-lifecycle-pruning-route-retirement-and-evidence-refresh-ladder.md)
- [`../20-calibration/source-hierarchy-conflict-refresh-and-current-law-ladder.md`](../20-calibration/source-hierarchy-conflict-refresh-and-current-law-ladder.md)
- [`../../archive/252-source-hierarchy-and-current-law-refresh-rules-should-not-be-turned-into-stale-authority-or-citation-theater.md`](../../archive/252-source-hierarchy-and-current-law-refresh-rules-should-not-be-turned-into-stale-authority-or-citation-theater.md)

## Core rule

Current-law and evidence claims need a source hierarchy. Primary law, final agency guidance, authoritative statistics, and audited administrative records outrank news summaries; news can flag events; scholarship can frame mechanisms; speculation must be labeled and routed to review rather than treated as settled authority.[S59][S594]

## Routing table

| Signal | Start here | Default output |
|---|---|---|
| legal status changed after a memo | current-law gate | refresh with primary law or official source before relying on the archive statement. |
| news and official source disagree | hierarchy gate | use news to locate the event, then cite the official or primary source where available. |
| old source remains accurate but context shifted | staleness gate | mark stable doctrine, moved fact, or obsolete implementation. |
| source pile grows without changing route | pruning gate | compress citations and keep only load-bearing anchors. |
| frontier speculation used | label gate | flag speculative evidence and set a review trigger. |

## Rev0287 source-lineage rule

Do not confuse a source citation with a source-currentness dependency. A memo can cite a source for background, mechanism, or analogy without making that source a release-blocking currentness anchor. Promote a source into `source_currentness_refs` only when the route's answer depends on the source's current legal status, effective date, implementation posture, litigation posture, quarterly factor, official projection, or operational guidance. Every promoted source needs a local currentness claim and review reason.

This rule matters because broad, reused source clusters can create false freshness. Rev0287 repaired a case where a valid AI-energy source was treated as a currentness anchor for unrelated routes. The correct fix is not to delete useful citations; it is to keep currentness refs semantically narrow.

## Anti-patterns

- **citation theater** — many citations perform authority without changing the claim.
- **stale authority** — old rule or proposed text is treated as current law.
- **news as law** — coverage substitutes for the operative legal source.
- **source pileup** — new sources are added when one better primary source would do.
- **currentness taint** — a broad or repeated citation is promoted into a refresh-critical dependency even though the route would not change when that source updates.

## Source IDs only

[S59][S594]

[S59]: ../../SOURCES.md#S59
[S594]: ../../SOURCES.md#S594
