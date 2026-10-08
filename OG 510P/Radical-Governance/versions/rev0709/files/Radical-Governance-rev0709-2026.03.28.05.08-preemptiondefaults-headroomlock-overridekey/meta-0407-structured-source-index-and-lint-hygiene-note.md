# Meta — Structured source index and lint hygiene

This revision adds a compact `SOURCES.json` file plus a generator script so the continuation snapshot has a machine-readable source spine alongside the human-readable `SOURCES.md`.

Why this matters:

- compact archives are easier to merge back into a larger corpus when source provenance is structured,
- later comparison work becomes easier if a reviewer can map notes to source groups without scraping prose,
- the archive can now lint for the presence of a current revision entry in both markdown and JSON source records.

This revision also normalises the changelog back to a single top-level heading and teaches the linter to reject duplicate H1 headings in top-level archive files.

The result is still intentionally small. It is not a full provenance system, signed SBOM, or citation graph. It is just enough structure to keep the continuation bundle auditable and less fragile.
