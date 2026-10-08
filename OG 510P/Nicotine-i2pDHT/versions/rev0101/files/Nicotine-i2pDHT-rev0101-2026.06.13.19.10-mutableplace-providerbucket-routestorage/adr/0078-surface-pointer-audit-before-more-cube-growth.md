# ADR 0078 — surface pointer audit before more cube growth

## Decision

The cube needs a gentle JSON pointer audit in addition to the fail-closed public surface checker.

## Consequences

`surfaceaudit.py` can report missing public/head-registry pointers and revision drift without turning every historical wart into a build failure. The current public surface checker remains strict.
