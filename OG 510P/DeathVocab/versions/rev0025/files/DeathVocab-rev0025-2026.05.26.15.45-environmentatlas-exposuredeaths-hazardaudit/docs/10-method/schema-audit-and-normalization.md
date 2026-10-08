# Schema audit and normalization notes

Rev0014 changed the schema posture from brittle enumeration to audited tag hygiene.

The old schema listed a small enum for `record_classes`, but the cube had already evolved beyond it. Strict validation would have made many actual records appear invalid even though the problem was the schema, not the record. Rev0014 therefore keeps `schema_version: deathvocab.record.schema.v2` in the records but updates `RECORD-SCHEMA.json` to require lower_snake_case, unique class tags rather than a fixed enum.

This is not a retreat from structure. It is a distinction between integrity and ontology. Integrity is enforced: records need IDs, sources, provenance, safety, review, links, source-card coverage, and duplicate-free class/axis arrays. Ontology remains provisional: future sessions can split or rename classes as the corpus learns.

Normalization performed in this revision:

- class-list deduplication;
- axis-list deduplication;
- `ICU`/`ED` setting values normalized to `icu`/`ed`;
- setting terms removed from `timeline_phase` when they had leaked there;
- missing review and links blocks added from existing safety/provenance context;
- linter rewritten to check invariants without asserting that all records after `DV-REC-000017` are practice records.
