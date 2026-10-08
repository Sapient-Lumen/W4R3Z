# 967 — Cloudtainer source-health closure, catalog triage, retirement queue, and no completion by catalog posture

## One-line thesis

The riskiest unfinished work was no longer a giant generated file or a missing docket. It was the remaining class of source keys that still had no explicit posture, plus a retirement audit that named many possible overlaps but did not create a small actionable merge queue. This revision closes the unclassified source-health backlog while separating direct review from catalog triage, then adds a bounded merge-packet queue so maintenance can reduce route mass without pretending that overlap equals deletion readiness.

## Why this matters

Rev0768 cleared generated-surface warnings and separated leaf test matrices from first-reader route pressure. That fixed the archive's measurement problem, but it left a second risk: source-health completion could be faked by adding rows that look like live checks. The correction is to backfill every source key, but to name the kind of backfill honestly.

This revision therefore draws a line between two kinds of source-health evidence:

1. **Direct review** — a source was searched/opened or otherwise directly inspected in a review pass.
2. **Catalog triage** — a source was classified from the source-key registry, dependency graph, publisher, URL, title, and note use, but the offline build did not fetch the URL.

That difference matters more than the headline coverage percentage. A complete source-health ledger with catalog triage is useful because no key is invisible. It is still not proof that every live portal, dashboard, or guidance page is current today. The generated source-health surface now reports both manual coverage and direct-review coverage so the archive cannot declare victory by filling in forms.

The second risk is growth pressure. The retirement audit had an 80-item review-only queue, but that was still too broad for actual maintenance. A future maintainer needs a smaller zero-dependency merge-packet queue: notes that may be redundant enough to review first, while still protected from automatic deletion.


## Pattern pack

1. **Complete posture is not complete verification.** Every source key should have a role, volatility, jurisdiction, and review cadence; only directly reviewed rows should count as live or recently inspected evidence.
2. **Catalog triage is an honest queue, not a victory lap.** Backfilling source posture is valuable because it reveals what still needs direct refresh.
3. **Use dependency weight to order refresh work.** Live dashboards, implementation clocks, status-proof portals, redress clocks, and high-dependency case sources outrank stable background reports.
4. **Turn retirement pressure into merge packets.** A zero-dependency overlap candidate is an invitation to prove preservation, not a deletion permission slip.
5. **Close gaps only at their original scope.** Generated-surface warnings and unclassified source-health rows can be repaired while direct refresh remains a future operational queue.
6. **Never launder freshness through generated outputs.** Machine routes can sort and summarize source posture, but they do not make stale sources current.

## Priority source-health closure

The closure is intentionally conservative. It does not say that every source is current. It says every source now has at least a posture:

- official living source, implementation clock, live dashboard, periodic dataset, legal/order anchor, audit/oversight report, external historical anchor, supplier/procurement surface, redress clock, representative-authority route, status-proof surface, emergency waist, or stable background source;
- jurisdiction, publisher class, expected volatility, review cadence, and risk flags;
- a retrieval result that says whether the row came from direct review or catalog dependency backfill.

The most important practical effect is that high-consequence rows no longer disappear into an unchecked tail. FATF listing pages, SIS/eVisa status-proof surfaces, Phoenix/Dayforce pay transition evidence, GOV.UK Chat and MyCity chatbot evidence, Medicaid renewal snapshots, interoperability-assessment triggers, representative-authority pages, and redress clocks now carry explicit posture.

## Audit/refactor shipped

1. `metadata/source_health.json` now contains entries for all source keys.
2. `tools/build_source_health.py` now reports:
   - manual source-health coverage;
   - direct-review coverage;
   - catalog-triage coverage awaiting direct refresh;
   - a direct-refresh priority queue for catalog-triaged rows.
3. `tools/build_retirement_candidates.py` now exposes a bounded zero-dependency merge-packet priority queue, not just a broad review-only list.
4. `metadata/gap_ledger.json` closes `GAP-027` as repaired for generated-surface warnings and unclassified source-health backfill, while preserving a future direct-refresh queue in generated source health.

## Why this is substance rather than registry bureaucracy

The source-health closure changes what a reader can safely infer. Before this pass, an unchecked key could be mistaken for a reviewed source because it appeared in a note, claim, or case packet. After this pass, every source either carries a direct-review posture or explicitly admits that it is catalog triage awaiting direct refresh.

The retirement queue changes what a maintainer can safely do. Before this pass, the audit named many possible overlaps but did not prioritize a small, low-dependency merge lane. After this pass, the archive has a short merge-packet queue that can reduce route mass without sacrificing old source posture, test coverage, affected-party tails, opposition briefs, or dispatch function.

## Failure modes

- **Catalog posture theater:** claiming a source was live-checked because it has a health row.
- **Coverage percentage theater:** treating 100% manual coverage as 100% direct review.
- **Stale portal laundering:** using an implementation-clock source as if it were a stable legal anchor.
- **Historical-anchor overreach:** using a report, audit, news article, or paper as if it proved current service operation.
- **Merge-by-overlap:** deleting a note because tags and words overlap, without preserving tests, source keys, affected-party tails, and dispatch roles.
- **Retirement avoidance:** keeping every route forever because deletion is risky, instead of drafting bounded merge packets for zero-dependency candidates.

## Operational next move

The next pass should not create a new broad docket unless the archive has a genuinely missing domain. The highest-value maintenance options are now:

1. direct-refresh the catalog-triage queue, beginning with live dashboards, status-proof portals, redress clocks, benefit/eligibility pages, AI records, and financial-crime/watchlist waists;
2. write one human merge packet for the top zero-dependency retirement candidate and prove preservation before moving anything;
3. keep generated-surface budgets stable while monitoring reader-route growth.

## Rule of thumb

No completion by catalog posture.
