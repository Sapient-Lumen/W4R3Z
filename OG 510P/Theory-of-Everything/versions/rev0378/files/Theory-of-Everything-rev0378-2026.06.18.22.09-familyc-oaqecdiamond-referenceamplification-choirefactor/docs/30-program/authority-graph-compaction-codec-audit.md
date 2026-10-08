# Authority graph compaction / codec audit

## Revision

`rev0316` implements the active graph-weight repair opened in `rev0315`.

## What changed

The archive no longer stores `AUTHORITY-DEPENDENCY-GRAPH.json` as a 51,599-row pretty-printed `edge_rows` array. It stores the same logical graph as `columnar-dictionary-v1` JSON:

- `edge_ids` preserves row identity and order.
- `edge_row_fields` names the eight repeated value columns.
- `dictionaries` stores the unique strings for each column.
- `columns` stores integer dictionary codes for each row.
- `expanded_sha256` hashes the canonical expanded logical graph.

`tools/authority_graph_codec.py` is the canonical codec. Generated summaries and archive lint load the compact file through that codec and operate on logical `edge_rows`, so the storage refactor does not change route authority, dependency semantics, rollback propagation, or generated edge counts.

## Why this was the highest-risk repair

The prior representation made one generated artifact dominate the cloudtainer. In `rev0315`, `AUTHORITY-DEPENDENCY-GRAPH.json` was about 27.1 MB uncompressed, while most ledgers were below 0.2 MB. That created four problems:

1. ordinary search/diff work was dominated by generated audit exhaust;
2. the release looked larger than its conceptual payload;
3. future route-family additions would keep paying the same redundancy tax;
4. the active followthrough item could easily become another permanent queue entry if not executed immediately.

The fix is intentionally not another registry. It is a storage/code refactor with a roundtrip invariant.


## Measured result in this revision

- Logical dependency edges: `51599`
- Expanded pretty JSON size if materialized: `27,134,786` bytes
- Stored compact JSON size: `2,319,503` bytes
- Stored/expanded ratio: `0.085`
- Uncompressed-size reduction: `91.5%`

The authority graph remains the largest individual text object, but it no longer dominates the archive by an order of magnitude; after compaction it is in the same operational scale as the other large ledgers and tools.

## Integrity checks now enforced

`make lint` now rejects the following regressions:

- storing expanded `edge_rows` in the default authority-graph file;
- losing compact `edge_count` / `row_count` parity with the expanded logical graph;
- changing the expanded graph without updating `expanded_sha256`;
- emitting a compact payload that differs from deterministic codec output;
- regressing the compact file above 20% of the expanded pretty JSON size.

`schemas/authority-dependency-graph.schema.json` now accepts either the old expanded representation or the new compact representation, but lint requires the compact representation for the release payload.

## Scientific status

No route is promoted. This revision changes the archive's control-plane storage and replay reliability only. The logical dependency graph remains the same support/rollback object: surviving compaction cannot create `S4` or `S5` evidence, cannot repair a broken carrier, and cannot discharge any observed-sector obligation.
