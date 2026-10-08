
# Quote-search and source receipts

A poem cannot become an evidence candidate until its strongest phrases and documentary claims have receipts.

## Quote-search receipt

Use `schemas/quote_search_receipt.schema.json` and append records to `registries/quote_search_receipts.json`.

A receipt should record:

- poem and draft ID;
- phrase searched;
- exact query used;
- search date and tool;
- result count or nearest-match summary;
- verdict: `no_exact_hits`, `near_collision`, `common_phrase`, `source_dependent`, `needs_rewrite`, or `not_checked`;
- reviewer notes.

## Source receipt

Use `schemas/source_receipt.schema.json` and `registries/source_registry.json`. For source-bound claims, record the claim, source ID, accessed date, authority level, and selector. When useful, model selectors after Web Annotation ideas: exact quote, prefix/suffix, and text-position-like offsets.

## Admission gate

No poem enters `evidence_candidate` unless:

1. all factual claims have source IDs;
2. all source IDs exist in the source registry;
3. all counted or lettered constraints have verification receipts;
4. all highlighted or potentially borrowed phrases have quote-search receipts;
5. authorship disclosure is explicit.
