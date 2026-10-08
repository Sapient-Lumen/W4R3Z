# Meta: Worthy Repo Buildout Protocol (rev0490)

## Purpose
Use this protocol when the task is not merely:
- “what is Rust still missing?”
- or “what does the latest archive plus latest official signals imply?”

but more specifically:
- continue researching and **construct the repo**;
- deepen what the strongest contributions should look like in theory and in practice;
- decide what should be ranked, folded, merged, or eliminated;
- or add meta-engineering so future assistants keep extending the archive without fragmenting it.

This protocol exists because a growing archive can fail in a new way:
not by forgetting the big map, but by growing too many almost-seams, almost-programs, and almost-frameworks that never resolve into a stewardable buildout order.

Read with:
- `design/epic-contribution-worthy-repo-buildout-2026Q1.md`
- `design/epic-contribution-live-ecosystem-refresh-2026Q1.md`
- `design/epic-contribution-live-decision-packets-2026Q1.md`
- `design/epic-contribution-candidate-dossiers-2026Q1.md`
- `meta/LIVE_ECOSYSTEM_REFRESH_PROTOCOL.md`
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Default rule
A healthy buildout revision keeps five things separate:
1. **broad strategic ranking** — what matters most in the long run;
2. **current packet posture** — what currently deserves `advance`, `deepen`, `hold`, `fold`, or `kill`;
3. **repo buildout order** — what deserves the most detailed theory/practice treatment next;
4. **fold-under-parent map** — which fresh tools, hooks, or upstream efforts belong inside stronger seams instead of becoming new seams;
5. **meta-hygiene** — what future assistants must preserve so the archive stays coherent.

If those are blurred together, the revision will sound productive while quietly increasing repo entropy.

## Required moves for a worthy-repo buildout revision

### 1) Re-open the current canon before inventing new structure
Minimum read set:
- `AGENTS.md`
- `INDEX.md`
- `PRIORITIES.md`
- `RESEARCH_LOG.md`
- `STRATEGIC_FRONTIER.md`
- `meta/ACTIVE_FRONTIER.md`
- `meta/CANONICAL_WORKING_SET.md`
- the nearest live-refresh note and live packets/dossiers
- the strongest current execution blueprints for any seam being deepened.

### 2) Prefer fresh primary sources that change practical shape
A source is especially valuable for a buildout pass when it changes one of these:
- import feasibility;
- service truth now available;
- operator decision boundaries;
- steward/host reality;
- or explicit capability requirements.

Do not add sources merely because they mention the seam in broad terms.
Add them when they help answer “what should this contribution look like in practice now?”

### 3) For every seam you deepen, answer four questions explicitly
For each major contribution, say:
- **theory** — what missing truth or shared function it should provide;
- **practice** — what artifacts, commands, receipts, or programs it should actually expose;
- **imports** — what current machine-usable or human-reviewed sources it should rely on;
- **wrong shape refused** — what tempting product or framework shape the archive still rejects.

### 4) Fold fresh side-bets under stronger parents by default
New upstream work should stay folded unless it clearly earns an independent seam.
Examples of the right instinct:
- capability analysis under package-intake;
- publish-time semver under compatibility/release boundary;
- libtest JSON under debug/tooling substrates;
- docs.rs rustdoc JSON under compatibility/navigation/tooling;
- interop mapping under safety-critical readiness.

A revision that produces many new seam names should be treated as suspicious.

### 5) Distinguish strategic importance from buildout order
A seam may be strategically huge and still deserve slower repo expansion.
A seam may be second-order strategically and still deserve immediate practical deepening because the imports, interfaces, and proof burden are now clearer.
Do not use one ranking for all questions.

### 6) Update the routing and continuity rails together
A non-trivial buildout revision should usually update:
- the new design note and any new meta protocol;
- `AGENTS.md`, `INDEX.md`, `PRIORITIES.md`, `RESEARCH_LOG.md`, and `STRATEGIC_FRONTIER.md`;
- `meta/ACTIVE_FRONTIER.md`, `meta/CANONICAL_WORKING_SET.md`, `meta/LATEST_REVISION_FILESET.md`;
- `meta/LLM_ARCHIVE_CONTINUITY_PROTOCOL.md`, `meta/REVISION_OPERATING_PROTOCOL.md`, and `meta/AMNESIA_RESISTORS.md`;
- and `atlases/portfolio-source-atlas-v0/sources.json` when a source becomes a repeated practical anchor.

### 7) Favor artifacts that make the repo more evaluable
Prefer additions such as:
- program briefs;
- import/export maps;
- fold-under-parent maps;
- sharper kernel or packet refreshes;
- steward-model notes;
- and explicit renewal or stale-state receipts.

Be suspicious of additions that only widen atmosphere:
- more slogans;
- more seam names;
- more wishlists with no import or refusal discipline;
- or more “ecosystem platform” talk with unclear decision rights.

## Failure modes to refuse
- treating every new official tool or service feature as its own independent epic;
- using one fresh source to silently rerank the whole archive;
- widening recommendation/atlas work without renewed editorial-capacity accounting;
- deepening a seam without saying what artifacts it should emit;
- adding substrate notes that never reconnect to user-visible operator pain;
- or continuing research without touching routing, continuity, and source-atlas rails.

## Minimum non-claims
A worthy-repo buildout revision must **not** claim that it:
- promoted a new frontier unless it actually did;
- changed the broad ladder unless it explicitly did;
- proved a final kernel shape from one current tool or goal page alone;
- or solved archive memory drift merely by adding another synthesis note.

## Suggested output grammar
A strong repo-buildout answer often has this shape:
1. what broad ranking is unchanged;
2. what practical buildout order is sharpened;
3. what each top seam should look like in theory and practice;
4. what fresh side-bets are folded rather than promoted;
5. what repo-hygiene changes preserve continuity.

## Why this file exists
The archive already had excellent broad synthesis and increasingly concrete build surfaces.
What it still lacked was one explicit protocol for the question:

> “keep researching, keep building the repo, and make it worthy.”

Without this protocol, future revisions risk either restating the same ranking forever or fragmenting the map every time the ecosystem gains a new tool, report, or service feature.
