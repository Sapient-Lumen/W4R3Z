# TimeSync rev0121 focused audit: mission, exact time, release integrity

rev0121 is a corrective release rather than an ontology release. It repairs two false-assurance paths—submicrosecond timestamp collapse and stale release identity—then redirects the open frontier toward external proof.

The six-field core remains unchanged. The new exact parser is an evaluator implementation correction, not a new timestamp format. It accepts the RFC 3339 forms used by the schemas, preserves supplied fractional precision, normalizes explicit offsets, accepts lower-case `t`/`z`, and fails closed on leap seconds until a deliberate arithmetic policy exists.

The release builder is deterministic for a fixed source tree, receipt, and filename. It normalizes ZIP member order, timestamps, and permissions and writes manifest v2 before packaging. This is reproducible packaging, not authenticated provenance; signing/builder attestation remains future work.

FT-0090 is archived as closed because its marginal work had become internal hardening without an end-to-end implementation. FT-0121 requires a real observation capture, parser, evaluator, explanation, and failure corpus before new assurance concepts are added.
