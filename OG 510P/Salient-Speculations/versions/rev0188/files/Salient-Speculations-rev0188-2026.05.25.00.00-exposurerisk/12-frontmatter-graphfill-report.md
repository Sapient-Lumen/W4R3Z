# Front Matter and Graphfill Report

rev0183 completes the first full minimal front-matter pass and adds decision-grade indexes.

## What changed in this revision

- Added YAML front matter to every remaining dossier that lacked it.
- Marked inferred metadata with `migration_status: inferred-rev0183-minimal`.
- Added five new dossiers with reviewed rev0183 front matter.
- Rebuilt `INDEX/dossier-index.csv` and `INDEX/dossier-index.json`.
- Expanded `INDEX/dossier-graph.tsv` with decisiongrade edges.
- Added `INDEX/decision-grade-scores.csv` and `.json`.
- Added `INDEX/evidence-audit.csv`, `INDEX/transfer-atlas.tsv`, `INDEX/taxonomy-merge-candidates.csv`, and `INDEX/research-watchlist.csv`.

## Migration counts

- Dossiers with YAML front matter before rev0183: 85.
- Older dossiers backfilled in rev0183: 113.
- New rev0183 dossiers: 5.
- Dossiers with YAML after rev0183: 203.

## Important caveat

Complete YAML coverage does not mean complete review. It means the archive can now be sorted, queried, and audited. The highest-value next task is to replace inferred metadata with reviewed metadata for the highest-scoring decision-grade dossiers.

## Recommended next revision

rev0184 should be either:

1. a pruning/consolidation revision; or
2. a deliberate outside-managed-legibility revision that tests whether the decision-grade rubric works on demography, biology, fiscal capacity, settlement geography, and care.
