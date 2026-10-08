# Scenario family — payload-derived identifiers require hash or drop posture

This fixture family exists for crates whose signals may include user IDs, request parameters, message payload fragments, or other identifiers derived from input data.

It is meant to catch support drift such as:

- a crate advertises useful debug or audit signals,
- but leaves payload-derived identifiers marked as broadly safe,
- or relies on backend-side redaction without documenting the crate-side boundary,
- or silently changes a field from hashed/truncated to raw.

A good observability pack should make four things explicit:

1. which fields are payload-derived or identifier-shaped,
2. whether they are safe, hashed, truncated, dropped, or manual-review territory,
3. whether the route relies on collector-side redaction,
4. and whether the summary still overclaims “safe by default”.

This family keeps “the signal is useful” separate from “the field is safe to emit as-is”.
