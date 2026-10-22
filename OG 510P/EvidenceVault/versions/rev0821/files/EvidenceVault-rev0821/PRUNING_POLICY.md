# Pruning / de-duplication policy (rev0012)

This unified archive is intended to replace several older working archives while staying publishable and reasonably sized.
The goal is that a reader can fetch *one* bundle and still have (i) referee-grade papers, and (ii) enough artifacts/tooling to reproduce the key claims.

## Kept
- Source text and specs: `.tex`, `.md`, `.txt`, etc.
- Tooling **source**: `.py`, `.sh`, `.go`, `.rs`, etc. (source only)
- Schemas and structured evidence: `.json`, `.yaml`, `.toml`, plus proof/receipt encodings where used as artifacts
- A small **canonical** set of PDFs (typically one per major work stream) for convenience
- Public keys / certificates (no private keys)

## Dropped (by default)
- LaTeX build byproducts: `.aux/.log/.out/.fls/.fdb_latexmk/.bcf/.run.xml/.synctex.gz`, bibliography build outputs (`.bbl/.blg`), transient build workdirs, and noncanonical convenience-PDF mirrors once the canonical `papers/*.pdf` set has been refreshed
- Compiled binaries and build directories (`dist/`, `build/`, `target/`, `node_modules/`, `venv/`, caches)
- Nested archives (zip-in-zip, tarballs), unless explicitly called out as a "repro pack" that is safer to keep unpacked
- Redundant intermediate PDFs (older draft renders, figure dumps) when the underlying TeX sources are present
- Exact curated artifact mirrors when the same bytes already live at a canonical retained source/cert path and the curated lookup point can be preserved by a small path index (`CANONICAL_PATHS.json`)

## Upstream traceability
The exact upstream input zips (with sha256) are listed in `UPSTREAM_INPUTS.sha256`.

## Redactions
Obvious secret signing keys / private keys are omitted. The removed upstream-relative paths are recorded in `REDACTIONS.paths`.
