# Rev0971 research and design notes

The relevant standards fact is encoding, not character count. RFC 8259 permits
control characters in JSON strings to be represented as six-byte `\u00XX`
escapes. A page budget based on source pathname length would therefore be an
unsafe approximation. Rev0971 counts the exact canonical bytes emitted by the
shipping encoder.

Cursor pagination remains the correct continuation model because the existing
source cutpoint binds the immutable causal operation set and the cursor names an
exact operation. A new offset or server-side page session would introduce
restart lifetime and mutation semantics without adding authority. Both the
entry-count and byte frontiers therefore reuse the same cursor.

The 256 KiB inventory budget reserves most of the 1 MiB owner socket envelope for
configuration, routes, readiness, integrity, quarantine, lifecycle, and failure
evidence. It is an internal presentation invariant, not a user scheduling knob.

Reference: RFC 8259, “The JavaScript Object Notation (JSON) Data Interchange
Format,” especially the string escaping grammar.
