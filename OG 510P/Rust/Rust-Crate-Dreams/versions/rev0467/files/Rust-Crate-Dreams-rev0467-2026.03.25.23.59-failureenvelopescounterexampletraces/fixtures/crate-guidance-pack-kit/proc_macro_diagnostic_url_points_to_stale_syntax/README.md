# Scenario — proc-macro diagnostic URL points to stale syntax

A proc-macro crate emits a helpful diagnostic code or URL, but the linked example still shows an older invocation form or feature gate.

Why it matters:
- the emitted diagnostic is real,
- the anchor exists,
- but the claimed smallest-good-path is stale,
- so recovery origin and recipe fidelity must stay separate review objects.
