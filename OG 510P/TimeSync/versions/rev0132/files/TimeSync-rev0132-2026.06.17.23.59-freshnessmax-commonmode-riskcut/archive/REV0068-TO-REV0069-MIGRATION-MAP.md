# Migration map — rev0068 to rev0069

## Additive changes

- Add optional `input_items[*].external_evidence_reference` to evaluator evidence summaries.
- Add `schema/redacted-external-evidence-reference.schema.json`.
- Add `external_evidence_reference` evidence class with `may_satisfy_profile_obligation: false`.
- Add `summary_with_salted_commitments` to evidence-summary redaction modes.
- Add `external_evidence_interpreted_as_provenance: false` to `non_provenance_guards`.

## Required updates for retained/evidence summaries

Existing rev0068 evidence summaries must add:

```json
"external_evidence_interpreted_as_provenance": false
```

inside `non_provenance_guards`.

If a redacted item exports a digest that binds `redacted_input_group`, it must either be replaced with a salted commitment in `external_evidence_reference.commitment` or omitted.

## Profile digest change

All P1-P6 profile digests changed because each profile evidence policy now lists `external_evidence_reference` among classes that cannot satisfy profile obligations.
