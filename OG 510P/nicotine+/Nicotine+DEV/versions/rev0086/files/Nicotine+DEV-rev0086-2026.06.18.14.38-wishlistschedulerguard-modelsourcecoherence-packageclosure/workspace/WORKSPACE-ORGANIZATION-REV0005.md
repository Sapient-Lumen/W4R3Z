# rev0005 workspace organization

The source bundle is kept external because embedding it made the cube too large. The compact cube stores hashes, lane IDs, source snippets, and evidence. The analysis workspace may keep extracted source trees locally at:

```text
/mnt/data/nicotine_dev_external_source_inventory/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/
```

The cube itself stores only compact derived evidence.

## Work areas

- `data/rev0005_ranked_audit_queue.csv`: current master queue with rev0005 public-overlap columns.
- `data/rev0005_public_overlap_status.csv`: per-finding public-overlap ledger for all 274 seed rows.
- `data/rev0005_hard_search_batch01.csv`: the batch touched this revision.
- `evidence/rev0005-web-public-overlap-batch01.md`: public search evidence and conclusions.
- `evidence/rev0005-source-shape-batch01.md`: compact source snippets from current/future source lanes.
- `docs/PUBLIC-OVERLAP-POLICY.md`: mandatory classification and promotion policy.
- `workspace/FINAL-DOC-CONSTRUCTION-MACHINE.md`: the repeatable construction pipeline for the two final documents.
