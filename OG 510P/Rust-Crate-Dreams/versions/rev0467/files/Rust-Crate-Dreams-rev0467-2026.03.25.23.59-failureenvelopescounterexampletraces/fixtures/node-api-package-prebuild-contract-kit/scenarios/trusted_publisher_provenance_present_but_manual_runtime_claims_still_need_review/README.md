# Scenario: trusted publisher and provenance are present, but runtime claims still need review

The package is published through npm trusted publishing from GitHub Actions and should therefore carry provenance for a public package from a public repository.
However, the README also claims Bun and Deno support without matching artifact or loader evidence.

This scenario exists to keep the shipkit from flattening:
- “strong publish identity”
- and “strong runtime-support evidence”

into the same verdict.
