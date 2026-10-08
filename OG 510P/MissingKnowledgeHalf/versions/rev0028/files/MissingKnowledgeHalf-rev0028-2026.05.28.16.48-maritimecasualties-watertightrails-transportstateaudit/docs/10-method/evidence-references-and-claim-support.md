# Evidence references and claim support

Rev0016 replaces the legacy `source_support` / `sources_or_support` shape with `evidence_refs`.

The reason is simple: a claim may be supported by a source, a promoted case record, an infrastructure record, a pattern record's own scope caution, or another non-source object. Calling every such object `source_id` made the graph semantically false even when references resolved.

## Canonical claim support shape

Each claim should carry:

```json
{
  "evidence_refs": [
    {
      "ref_id": "MKH-SRC-0001",
      "ref_kind": "source",
      "support_role": "direct_source_support",
      "confidence": "source_locator_present",
      "locator": "PDF lines 472-484"
    }
  ]
}
```

For pattern candidates, non-source refs are legitimate, but they must not masquerade as source records:

```json
{
  "ref_id": "MKH-ENG-0002",
  "ref_kind": "engineering_record",
  "support_role": "supporting_record_for_pattern_candidate",
  "confidence": "derived_from_promoted_record",
  "support_type": "unit/scale mismatch across software-interface boundary"
}
```

## Rules

1. `source_support` is legacy and should not appear in promoted record claims.
2. `sources_or_support` is legacy and should not appear in claim-ledger entries.
3. `ref_id` must resolve to a promoted record or source.
4. `ref_kind` must truthfully describe the target object.
5. `support_role` explains why the target is being cited.
6. `confidence` describes locator/extraction state, not truth.
7. A non-source evidence reference is not a substitute for source re-extraction.

## What this earns

The cube can now distinguish:

- direct source support;
- derived support through a promoted record;
- infrastructure context;
- pattern self-scope/status support;
- weak locators that still need repair.

This is necessary before the cube can scale to thousands of records without quietly corrupting its evidence semantics.
