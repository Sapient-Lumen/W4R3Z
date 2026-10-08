# OCI descriptor verification / project containment excerpt — rev0069

Source: Open Container Initiative Image Specification v1.1.1, `descriptor.md`.  
Accessed: 2026-06-18T15:08:00-04:00.  
Web evidence reference: `turn766217view0`.

This is a bounded excerpt note, not a full or complete capture of the specification.

Bounded facts used:

- A descriptor requires a media type, digest, and raw byte size.
- Consumers should verify size before digest calculation and avoid heavy processing before verification.
- A SHA-256 descriptor encoding must be exactly 64 lowercase hexadecimal characters.
- OCI generally allows other digest algorithms; LLMPoetry intentionally constrains this poem artifact to SHA-256 before constructing any local blob path.

Project implication: malformed descriptor text is rejected before filesystem lookup or blob I/O. This snapshot supports a validator-safety claim only, not poetic quality.
