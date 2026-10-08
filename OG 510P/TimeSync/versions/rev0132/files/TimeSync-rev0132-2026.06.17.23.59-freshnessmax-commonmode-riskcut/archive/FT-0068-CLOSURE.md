# FT-0068 closure — redacted external evidence references / salted commitments

FT-0068 asked whether TimeSync needed a way to bind redacted evidence values to external retained material without leaking low-cardinality values or becoming a provenance graph.

rev0069 answers yes, narrowly:

- Added `schema/redacted-external-evidence-reference.schema.json`.
- Added `input_items[*].external_evidence_reference` to evaluator evidence summaries.
- Added `external_evidence_reference` as a non-satisfying evidence class.
- Added `summary_with_salted_commitments` as an evidence-summary redaction mode.
- Added a required non-provenance guard: `external_evidence_interpreted_as_provenance: false`.
- Added semantic rejection for bare unsalted redacted-input digests over hidden values.
- Added positive and negative fixtures for redacted references, short salts, pointer-only obligation use, and malformed discovery-returned summaries.

Preserved boundaries:

- TimeState core unchanged.
- External references do not satisfy profile obligations by themselves.
- TimeSync binds to external records but does not interpret external provenance.
- The salt/preimage disclosure workflow remains outside TimeSync.
