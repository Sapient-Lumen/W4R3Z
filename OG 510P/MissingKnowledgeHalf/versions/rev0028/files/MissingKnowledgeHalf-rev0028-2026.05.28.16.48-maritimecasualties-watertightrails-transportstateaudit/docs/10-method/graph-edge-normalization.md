# Graph-edge normalization

Rev0016 introduces `GRAPH-EDGES.json` as a normalized read surface over the cube.

Edges are extracted from:

- `record.sources[]`;
- `record.claims[].evidence_refs[]`;
- `record.links[]` arrays;
- compact `record.links{}` dictionaries;
- `type_payload.red_team_controls.supporting_records_currently_in_cube`.

## Current status

`GRAPH-EDGES.json` is not yet canonical. Records remain canonical.

The graph exists so future sessions can query cross-record structure without parsing every record by hand. It should eventually become generated, lossless, and lint-diffed.

## Important edge classes

- `declares_source_or_dependency`
- `record_contains_claim`
- `claim_supported_by_ref`
- `record_claim_supported_by_ref`
- compact link-derived edges such as `patterns`, `related_records`, `supports`, `qualifies`, and `recurs_with`
- `pattern_candidate_currently_supported_by_record`

## What future sessions should avoid

Do not treat edge count as importance. Do not treat an edge as stronger than the source surface that produced it. Do not turn graph density into epistemic certainty.
