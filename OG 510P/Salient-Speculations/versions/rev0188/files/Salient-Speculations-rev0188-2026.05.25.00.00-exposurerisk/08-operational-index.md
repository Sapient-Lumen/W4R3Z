# Operational Index

rev0180 created the schema bones. rev0181 makes the schema usable without forcing a risky full rewrite of 180+ dossiers.

This file explains the new `INDEX/` layer and the editorial policy for moving from archive-as-reading-list to archive-as-queryable-model.

## What was added

- `INDEX/dossier-index.csv` — one row per dossier file, with title, slug, size, rough maturity, schema status, likely constellations, and keyword-derived flags.
- `INDEX/dossier-index.json` — the same index in machine-readable form for scripts, embeddings, dashboards, or future linting.
- `INDEX/dossier-graph.tsv` — seed graph edges for the newly promoted and recently central dossiers.
- `INDEX/schema-values.json` — the controlled vocabulary copied out of the schema as machine-readable values.
- `INDEX/migration-priority.csv` — a practical queue for YAML/front-matter migration and relationship cleanup.

These are not meant to replace the prose. They are the first bridge between prose dossiers and a navigable datacube.

## Why not front-matter every dossier at once?

The archive is not a uniform dataset. Older dossiers use different formats, many include broad civilizational framing, and some are primitive ancestors rather than current operating units. A blind migration would create false precision. rev0181 therefore takes the safer path:

1. add full front matter to newly promoted dossiers;
2. backfill front matter for the most recent reliance-object dossiers where the lifecycle is already clear;
3. generate an external index for all dossiers;
4. mark the remaining files by priority rather than pretending all metadata is equally certain.

The rule is: **index broadly, annotate carefully, migrate incrementally.**

## Index fields

The index has deliberately boring fields:

- `slug` — filename without `.md`.
- `title` — first H1 if present.
- `bytes` — rough size signal.
- `has_yaml` — whether the file begins with YAML front matter.
- `revision_promoted` — parsed from YAML when present.
- `maturity_guess` — rough heuristic; not authoritative.
- `likely_constellations` — keyword-derived; useful for triage, not final classification.
- `artifact_flags` — whether the dossier appears to contain packets, registries, notices, appeals, credentials, queues, scorecards, passports, proofs, etc.
- `lifecycle_flags` — source, transform, publish, route, rely, dispute, stay, correct, supersede, non-rely, retire.
- `abuse_burden_sections` — whether the file appears to include the newer “who pays / how abused / near misses” style checks.
- `source_refs` — extracted source IDs.

## New editorial tests enabled by the index

### 1. Overcrowding test

If too many new dossiers cluster around the same lifecycle stage and artifact type, the archive should stop promotion and consolidate. This protects against packet-governance overfit.

### 2. Missing-lifecycle test

For any major constellation, ask which lifecycle stages are missing. Example: product passports have source, publish, and rely; they still need dispute, correction, non-reliance, successor, and forgery states.

### 3. Abuse/burden coverage test

A dossier should eventually expose who pays, who saves, who captures, and how the artifact gets gamed. The index makes it easy to find files without those sections.

### 4. Source-density test

Dossiers with many claims and few source references should either be marked speculative or assigned to research queue.

### 5. Graph-isolation test

A dossier with no graph edges is probably under-integrated. It may still be good, but it is not yet part of the cube.

## How to use this layer

For reading, start with `README.md`, `04-constellations.md`, and the latest dossiers.

For analysis, start with:

1. `INDEX/dossier-index.csv` — find clusters and omissions.
2. `INDEX/migration-priority.csv` — choose metadata cleanup work.
3. `07-graph-backbone.md` and `INDEX/dossier-graph.tsv` — inspect lifecycle chains.
4. `09-research-signal-ledger.md` — see which outside signals currently support or pressure the archive.

## Next index improvements

- Add stable IDs for every dossier, not only front-matter files.
- Replace heuristic constellation guesses with reviewed values.
- Add explicit `depends_on`, `weakens`, `anti_abuse_layer_for`, and `privacy_layer_for` arrays.
- Add a `near_miss` index to identify overloaded or fuzzy theses.
- Add a small lint script that flags dossiers lacking abuse, burden, falsifier, and source sections.
- Create a graph visualization once edges reach sufficient coverage.

## Operating principle

A datacube is useful only if each axis remains finite enough to query. The prose can remain rich, but the metadata should stay disciplined.


## rev0183 index expansion

rev0183 adds decision-grade index artifacts:

- `INDEX/decision-grade-scores.csv`
- `INDEX/decision-grade-scores.json`
- `INDEX/evidence-audit.csv`
- `INDEX/transfer-atlas.tsv`
- `INDEX/taxonomy-merge-candidates.csv`
- `INDEX/research-watchlist.csv`

The score files are heuristic. They are meant to answer: where should a reader spend attention first?

The archive now has complete minimal YAML coverage. Files marked `migration_status: inferred-rev0183-minimal` should be treated as navigational metadata, not as fully reviewed classification.
## rev0184 index additions

rev0184 adds four index artifacts:

- `freshness-family-audit.csv` — affected dossiers, roles, and consolidation treatment.
- `freshness-family-map.tsv` — dossier-to-model role map for the evidence-freshness cluster.
- `freshness-state-lexicon.json` — normalized state vocabulary used by the refactor.
- `refactor-actions.csv` — mechanical changes made during the rev0184 audit/refactor.


## rev0186 authority-index additions

Added `authority-family-audit.csv`, `authority-lifecycle-map.tsv`, `authority-state-lexicon.json`, and `authority-refactor-actions.csv`. The main dossier index now includes `authority_role` and `authority_stage`.


## rev0187 lineage-index additions

Added `lineage-family-audit.csv`, `lineage-lifecycle-map.tsv`, `lineage-state-lexicon.json`, `lineage-refactor-actions.csv`, and `custody-break-risk-register.csv`. The main dossier index now includes `lineage_role` and `lineage_stage`.
