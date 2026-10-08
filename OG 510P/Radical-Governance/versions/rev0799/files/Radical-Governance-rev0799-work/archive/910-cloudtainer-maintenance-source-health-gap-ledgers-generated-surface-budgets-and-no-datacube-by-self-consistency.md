# 910 — Cloudtainer maintenance, source health, gap ledgers, generated-surface budgets, and no datacube by self-consistency

## One-line thesis

A datacube that passes its own lint is only self-consistent; the next maintenance layer must track source health, external freshness, missing-case gaps, generated-surface budgets, package hygiene, and deletion or merge queues before it adds more case prose.

## Why this matters

The archive now has enough breadth that growth itself can become a governance failure. Rev0736 rebuilt cleanly and its numbered archive is continuous, but internal lint mostly proves that files agree with one another. It does not prove that source URLs still resolve, that sources are current, that generated files are proportionate, that stale holdings are marked, that important jurisdictions are missing for a reason, or that the package is free of local runtime residue. A cloudtainer pass should therefore treat the package as a living governance artifact, not only as a growing notebook.

The outside environment also changed in ways that make maintenance more valuable than another ordinary pattern note. Public AI inventories, algorithmic transparency registers, EU high-risk AI registration, digital identity standards, cloud switching rules, generative-AI management reviews, disaster-assistance risk reviews, and unemployment-insurance fraud / access postmortems are all moving targets. They are not just new examples. They are evidence that the archive needs clocks, source retrieval state, replacement-source routing, and gap ledgers.

## Pattern pack

### 1. Self-consistency is a floor, not a warrant

The current build proves that the archive directory, metadata spine, source catalog, generated indexes, and release surfaces can be regenerated together. That is valuable. It should not be treated as truth assurance. A note can be well-formed, tagged, linked, indexed, and still be obsolete, source-light, overbroad, missing the affected-party route, or based on a source that has been superseded.

The repair is to split checks into three layers:

- **shape checks**: numbering, headings, source keys, metadata fields, generated mirrors, no duplicate titles, and no package detritus;
- **health checks**: URL status, retrieval timestamp, content hash or ETag, publisher class, jurisdiction, supersession target, archive snapshot status, and affected claims;
- **substance checks**: currentness labels, opposition briefs, falsifiers, case comparator gaps, affected parties, and review clocks.

The archive already has much of the shape layer. It needs the health layer next.

### 2. Add a source-health ledger

Create `metadata/source_health.json` and a builder / auditor that can eventually write `generated/SOURCE_HEALTH.*`. The first schema should be boring and operational:

- `source_key`;
- canonical URL;
- publisher and jurisdiction;
- source class: statute, regulation, guidance, dashboard, register, audit report, court record, procurement record, news, academic, watchdog, civil-society, or archive snapshot;
- first added revision;
- last checked timestamp;
- HTTP status or retrieval result;
- redirect target;
- content hash, ETag, or last-modified header when available;
- expected volatility;
- supersedes / superseded-by fields;
- claims and notes depending on it;
- fallback source if it breaks;
- review owner / next check cadence.

This ledger should not replace `sources/source_keys.json`. The source-key registry says what the source is; the health ledger says whether the source still stands, whether it changed, and what breaks if it fails.

### 3. Add a gap ledger before adding another topical layer

Create `metadata/gap_ledger.json` for gaps that are known but not yet repaired. Each row should include the missing domain, reason it matters, current nearest note, affected parties, likely source anchors, severity, and the next artifact to build. This prevents the archive from looking complete simply because it is long.

High-value gaps after rev0736 include:

- disaster assistance and emergency relief payment delivery;
- pandemic unemployment insurance and the fraud-versus-access tradeoff;
- civil-facing AI inventory and algorithmic transparency register maintenance;
- public procurement realization gaps, especially cost, schedule, and actual-use tails;
- cyber incident disclosure, vulnerability remediation, and source-code / dependency provenance;
- law-enforcement, immigration, border, and watchlist automation beyond identity proofing;
- local-government and state/provincial use cases, not only central-government examples;
- non-English and Global South cases where official sources exist but are harder to keep current;
- deletion, merge, and retirement candidates inside the archive itself.

A gap ledger should include **why not now**. Otherwise it becomes another wish list.

### 4. Budget generated surfaces

Generated files are helpful as routing surfaces, but they can turn into a second archive. A large thread surface can be valuable for search while still being too bulky for first use. The repair is a budget rule:

- every generated long surface gets a compact companion;
- generated files must identify themselves as routing aids, not doctrine;
- a front-door reader should be able to answer “where do I start?” without opening multi-megabyte files;
- builders should report file sizes and top growth drivers;
- any generated surface above a set threshold should include a summary, table of contents, and truncation-safe section markers.

The purpose is not to delete the dense surfaces. It is to keep them from becoming the default reader path.

### 5. Keep cloudtainer residue out of the package

A source archive should not ship Python bytecode, `__pycache__` folders, editor residue, platform-specific metadata, or temporary run outputs. These files are small, but they are a symptom: the build package is mixing source and runtime state.

The correction is simple over time:

- set Python builds not to write bytecode during archive builds;
- make `make clean` remove generated files and runtime detritus;
- make lint fail if `__pycache__` or `.pyc` files are present;
- keep manifest categories source-oriented rather than runtime-oriented;
- create zips from a cleaned staging directory.

### 6. Do not force every revision to be an applied case

The previous lint rule treated a current revision as suspect if `metadata/case_packets.json` did not include a current revision case note. That is sensible for case-packet releases, but wrong for maintenance releases. It pressures the archive to add an applied case merely to satisfy the tool.

The better invariant is narrower: if a current note is declared as an `applied_case_packet`, then it must be registered in `metadata/case_packets.json`. If a current note is a self-audit, method note, source repair, or consolidation note, the case matrix should not force a fake case.

### 7. First repair sequence

The least-wasteful repair sequence is:

1. remove package detritus and block it from returning;
2. relax case-packet lint so maintenance revisions are possible;
3. add source-health metadata and URL / redirect checks;
4. add generated-surface size reports;
5. add a gap ledger;
6. add source-health fields to claims;
7. only then add the next major topical case packet.

### 8. Speculative thesis

The archive is at risk of becoming a “governance LLM context dump” unless it separates doctrine, evidence, generated routing, and maintenance state. The most dangerous failure is not that it has too little prose. It is that a reader may trust the datacube because it is systematic, even when a source has moved, a public register changed, a law phased in, a generated surface grew beyond navigability, or a missing domain was never entered into the docket.

## Findings table

| Finding | Current state | Repair |
|---|---|---|
| Numbered archive | Continuous and internally indexed | Keep shape lint |
| Metadata spine | Strong for note class, tags, sources, claims, and case packets | Add source health and gap ledgers |
| Source keys | Broad registry exists | Track URL health, retrieval dates, redirects, hashes, volatility, supersession, fallback |
| Claims ledger | Stronger than note-level authority | Add source-health impact and last-reviewed clocks |
| Generated surfaces | Useful, but heavy | Add compact companions and size budgets |
| Package hygiene | Runtime bytecode can enter the archive | Fail lint on `__pycache__` / `.pyc`; clean staging before zip |
| Case-packet rule | Maintenance revisions were disfavored | Require case registration only for current notes that are applied case packets |
| External change | AI, identity, cloud, disaster, and fraud sources are moving | Create scheduled freshness passes |

## Failure modes

- **Self-consistency theater**: every generated surface agrees with every metadata file, but a source is stale or a claim is obsolete.
- **Source-key theater**: a note has sources, but no one knows whether the URLs still resolve, redirect, or supersede prior guidance.
- **Generated-surface obesity**: generated routing files become so large that readers skip them or mistake them for canonical doctrine.
- **Runtime-contamination drift**: cloudtainer artifacts get zipped as if they were source.
- **Case-packet tyranny**: tooling pressures each revision to add a topical case even when the right work is maintenance.
- **Recency hallucination**: the archive talks about fast-changing registers, standards, model deployments, or payment backlogs without an explicit currentness clock.
- **Gap invisibility**: missing domains are hidden because the archive has many adjacent notes.
- **Deletion avoidance**: obsolete, overlapping, or weak notes remain because adding is emotionally easier than retiring.

## Anti-theater tests

1. Could a reader identify which sources were last checked this revision?
2. Could a broken or redirected source show which notes and claims are affected?
3. Could a maintenance-only revision pass without inventing a case packet?
4. Could a first-time reader find a compact route without opening the largest generated file?
5. Could the archive name its known gaps and explain why they were not repaired in this pass?
6. Could a claim be marked stale while the note remains active?
7. Could a generated surface be regenerated without including runtime bytecode in the zip?
8. Could a source be superseded without silently leaving old claims authoritative?
9. Could a note be retired, merged, or demoted without breaking the archive’s front door?
10. Could a future cloudtainer tell what changed because the package itself records maintenance changes?

## Reconstruction instruction

For the next maintenance turn, build `metadata/source_health.json`, `schema/source_health.schema.json`, and `tools/audit_source_health.py`. Do not make network health mandatory for offline lint; make it an explicit `make source_health` or `make audit` target whose results are committed only when intentionally refreshed. Add `generated/SOURCE_HEALTH.md` and `.json`, then add `metadata/gap_ledger.json`, `schema/gap_ledger.schema.json`, and `generated/GAP_LEDGER.*`. Extend claims so every volatile or supersession-risk claim can point to source-health rows. Keep `make lint` deterministic and offline, but make it fail for package detritus and impossible metadata states.

## Sources

Source anchors for this maintenance note include current public AI inventory practice, UK algorithmic transparency guidance, the EU AI Act high-risk-system database, NIST SP 800-63-4 digital identity guidance, EU Data Act cloud-switching implementation, GAO generative-AI and disaster-assistance reviews, pandemic unemployment-insurance fraud audits, and Department of Labor Inspector General unemployment-insurance oversight material. The exact source keys are registered in `sources/source_keys.json` and attached to this note in `sources/source_catalog.json`.
