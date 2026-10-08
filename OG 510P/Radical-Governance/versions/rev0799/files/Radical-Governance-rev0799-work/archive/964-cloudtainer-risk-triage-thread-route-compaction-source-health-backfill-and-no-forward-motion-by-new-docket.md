# 964 — Cloudtainer risk triage, thread-route compaction, source-health backfill, and no forward motion by new docket

## One-line thesis

The riskiest unfinished work is not another broad domain packet; it is the archive's operating spine: unchecked high-dependency sources, megabyte-scale thread/source-health surfaces, and weak pressure to turn maintenance debt into smaller reader routes. This revision moves substance by checking the top source-health queue, compacting the thread and source-health machine surfaces, and adopting **no forward motion by new docket**.

## Why this matters

The archive's ordinary vice is to mistake a new named doctrine for progress. The harder work is to remove reader friction, verify the sources already carrying old claims, and make the generated layer smaller without deleting evidence. A cube that can always add another case packet but cannot keep its current source posture clear is drifting toward the same administrative theater it criticizes.

The highest-risk queue in this pass was not hidden. `generated/SOURCE_HEALTH.md` already sorted unchecked source keys by dependency, volatility, claims, and case-packet use. The top rows were AI governance, chatbot, identity, benefit-migration, interoperability, and platform-migration sources that many existing notes depend on. Leaving those rows unchecked would make the archive's mature packets look more grounded than their source-currentness posture allowed.

The second risk was thread bloat. `generated/THREADS.md` was meant as a compact crosswalk, but it still rendered every tag-to-note edge and exceeded the generated Markdown warning budget. A thread route should help a reader choose where to go; it should not become a duplicate archive index with longer filenames.

## Pattern pack

### 1. No forward motion by new docket

A new policy topic counts as progress only when it reduces a proof-substitution failure that the current archive cannot already test. When the maintenance queue says source-health and route mass are the blocking risks, adding another domain packet is avoidance.

### 2. Source-health first, source-key second

A source key identifies a source; it does not prove that the source is live, current, superseded, retired, or safe to use as a continuing authority. High-dependency unchecked keys should be reviewed before low-dependency new material is added.

### 3. Live register means live volatility

The UK algorithmic-transparency records hub is a useful live register, but its record count, phases, and record contents can change. It should be treated as a volatile evidence lane, not a fixed citation.

### 4. Retired surface means transition evidence, not service proof

The NYC chatbot beta-ended page is valuable because it proves a transition state. It does not prove the successor service is safe, complete, accessible, or governed.

### 5. Audit report means repair trigger, not repair

NYC MyCity, ArriveCAN, and Canada pay-system modernization audit surfaces are high-value because they name cost, oversight, testing, procurement, and continuity failures. They should feed repair queues rather than serve as closure.

### 6. Current guidance means cadence

IRS identity-access guidance, UK eVisa view/prove guidance, AI playbooks, NIST AI RMF pages, GOV.UK Chat findings, DWP managed-migration statistics, and Interoperable Europe assessment guidance are living or supersession-prone enough to need review cadence. They are not safe forever because they resolved once.

### 7. Compact reader, complete machine lineage

Human route files should answer first-reader questions. Machine surfaces should preserve rebuildable detail where needed. A generated Markdown file that republishes every edge can become a denial-of-service attack on its own readers.

## Failure modes

- **Docket-addition avoidance.** The archive keeps widening the map while the existing map grows stale.
- **Unchecked high-dependency source.** A source used by many claims and case packets remains registry-backed but unreviewed.
- **Retired surface ambiguity.** A maintenance or ended-beta page is read as evidence that the underlying service was repaired.
- **Live-register freezing.** A changing AI or administrative register is cited as if record counts and phases are stable.
- **Audit-as-closure.** A published audit is treated as remedy rather than a trigger for follow-through evidence.
- **Generated route sprawl.** Thread and source-health files become so large that readers stop using them.
- **Machine/debug duplication.** Generated JSON duplicates titles, URLs, prose, and dependent lists already available in canonical source files.

## Anti-theater tests

1. Did the revision reduce the highest-ranked unchecked source-health debt before adding a new substantive domain?
2. Can a reader identify current threads without opening a megabyte-scale tag dump?
3. Does `SOURCE_HEALTH.json` sort risk without duplicating every source title, URL, manual note, and dependent edge?
4. Are live registers and current guidance assigned short review cadence rather than one-time trust?
5. Are retired/beta-ended pages labeled as transition evidence, not service proof?
6. Are audit reports connected to follow-through checks rather than treated as final repair?
7. Does lint now fail when the compact reader surfaces regress over budget?

## Corrections shipped in this revision

- Backfilled manual source-health rows for twelve high-priority unchecked source keys: UK AI Playbook, UK algorithmic-transparency records, NYC MyCity audit, Interoperable Europe assessment guidelines, NYC chatbot beta-ended page, NIST AI RMF, Canada ArriveCAN audit, DWP Move to Universal Credit statistics, GOV.UK Chat pilot findings, IRS account/ID.me guidance, Canada pay-system modernization audit, and UK eVisa view/prove guidance.
- Refactored `tools/build_threads.py` so the thread Markdown route renders a summary, current-revision tags, largest-thread rows, and recent examples instead of every tag-to-note edge.
- Refactored `tools/build_source_health.py` so `SOURCE_HEALTH.json` stores sortable summaries while canonical titles/URLs stay in `sources/source_keys.json`, manual prose stays in `metadata/source_health.json`, and dependency detail remains derivable from source catalogs and claims/cases.
- Compacted machine/debug JSON for archive index, control surfaces, and lifecycle gates so generated-route mass falls without deleting machine-rebuildability.
- Added lint budgets for the refactored generated surfaces so thread/source-health/index/control/lifecycle compaction cannot silently regress.
- Marked `GAP-027` further repaired while leaving remaining large generated surfaces and lower-priority source-health backfill visible.

## Audit/refactor result

This pass changes the maintenance economics. It does not create a new policy-docket family. It tightens the surfaces that determine whether old policy dockets remain usable. That is forward motion because the archive's existing claims become more trustworthy, cheaper to enter, and less dependent on stale unchecked rows.

The source-health audit also exposed a substantive rule for future sessions: prioritize sources by public consequence and dependency count, not by which new topic is easiest to write about. Benefit-migration statistics, identity gates, immigration-status portals, AI registers, and chatbot withdrawal pages are all places where a stale source can directly distort the archive's account of harm and remedy.

## What should change next

Continue with fewer additions and harder repairs. The next useful pass should either finish another top source-health tranche or compact another large generated/debug surface. If a new substantive domain is added, it should be because the gap ledger points to an urgent continuity failure, not because the archive can name one more administrative row.

The remaining source-health work should stay boring: open the next highest unchecked rows, mark volatility, assign cadence, label retired or superseded surfaces, and leave uncertainty visible. The remaining generated-surface work should stay conservative: compact reader routes first, preserve canonical source data, and avoid deleting machine surfaces until another file proves it can rebuild the same evidence.

## Source posture

This revision uses only existing source keys. The online checks prioritized official or primary pages and did not import PDFs into the archive. Where a source is live or likely to change, the metadata now marks it with short cadence; where it is an audit or ended-beta page, the metadata treats it as historical or transition evidence rather than continuing operational proof.
