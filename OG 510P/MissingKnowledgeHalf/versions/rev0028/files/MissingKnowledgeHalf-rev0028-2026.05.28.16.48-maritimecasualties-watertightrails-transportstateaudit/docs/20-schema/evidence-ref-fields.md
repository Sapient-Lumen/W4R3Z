# Evidence reference fields

`evidence_refs` is the canonical claim-support surface introduced in rev0016.

| Field | Meaning |
| --- | --- |
| `ref_id` | ID of the supporting source, record, pattern, infrastructure, or claim. |
| `ref_kind` | Controlled kind of the target: source, engineering_record, negative_result_record, replication_record, genealogy_record, infrastructure_record, metaresearch_record, pattern_record, or claim. |
| `support_role` | Why the target is being used as support. |
| `confidence` | Locator/extraction confidence token, not a truth score. |
| `locator` | Page, line, section, DOI/PMID, or other locator when available. |
| `support_type` | Short mechanism-specific description, especially for pattern support. |
| `note` | Optional preservation of legacy or interpretive notes. |

## Backward compatibility

`source_support` and `sources_or_support` should now be treated as legacy fields. Lint fails if they reappear in promoted claim records or the claim ledger.
