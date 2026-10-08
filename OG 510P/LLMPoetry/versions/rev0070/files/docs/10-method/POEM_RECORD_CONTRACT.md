# Poem record contract

A poem is not just a text. A poem record contains the text, provenance, constraints, verification, sources, revisions, judgments, and disclosure behavior.

## Minimum files for a real poem

```text
poems/P0001/
  metadata.json
  draft_001.md
  metrics_001.json
  sources/
  judgments/
  verification/
```

## Minimum metadata fields

- `poem_id`, `title`, `status`, `created_revision`, `created_turn`
- `axis_coordinates`
- `authorship` and `generation_context`
- `constraint_claims` and `verification_receipts`
- `source_ids` and `quarry_notes`
- `drafts` and `revision_lineage`
- `judgments`
- `quote_search_status`
- `disclosure_test_status`
- `ethics_notes`

## Status ladder

`template` → `draft` → `graveyard` or `anthology_candidate` → `evidence_candidate` → `admitted` or `withdrawn`.

No poem may enter `evidence_candidate` without source gates, quote-search gates, constraint gates, and at least one cold evaluation.
