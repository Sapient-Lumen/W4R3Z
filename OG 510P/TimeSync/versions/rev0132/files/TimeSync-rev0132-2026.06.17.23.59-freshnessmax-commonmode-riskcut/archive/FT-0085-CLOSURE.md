# FT-0085 closure — rev0086

FT-0085 asked whether TimeSync should standardize portable canonicalization, semantic version negotiation, and byte-envelope digest bindings without becoming a credential system or transparency-log protocol.

rev0086 closes the ticket by adding:

- `schema/digest-binding-policy.schema.json`
- `schema/semantic-version-negotiation.schema.json`
- `spec/54-portable-canonicalization-and-byte-envelope-bindings.md`
- `spec/55-discovery-semantic-version-negotiation.md`
- discovery request/result negotiation metadata
- digest-binding metadata for returned discovery objects
- positive examples for canonical JSON and byte-envelope bindings
- negative examples for legacy-current digest binding, parse-before-verify byte envelopes, and unsafe unknown-newer semantic acceptance

The core rule is that TimeSync-owned current digest surfaces use RFC 8785-style canonical JSON and sha256, while external signed statements and receipts bind pre-existing bytes.  The validator now checks these as shared helper logic rather than bespoke fixture conditions.
