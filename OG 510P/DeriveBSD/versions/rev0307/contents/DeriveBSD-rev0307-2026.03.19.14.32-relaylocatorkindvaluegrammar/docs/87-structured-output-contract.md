# Structured output contract (LLM-friendly): `--json`, stable codes, canonical shapes

DeriveBSD must be “machine-readable by default” without becoming unreadable to humans.

FreeBSD’s base utilities have a precedent here: **libxo** enables emitting text/XML/JSON/HTML from one code path, and many tools support structured output via `--libxo`. (See `docs/32-curated-references.md`.)

## DeriveBSD contract (v1)

Every DeriveBSD CLI command MUST support:
- `--json` : emit a single JSON document to stdout
- `--pretty` : human-friendly formatting (no semantic changes)
- `--quiet` : suppress non-essential text
- `--trace` : optional evaluation/build/policy trace objects (never secrets)

JSON output MUST be:
- schema-versioned (`schema_version`)
- JCS-canonicalizable (RFC 8785; see `docs/80-canonical-json-hashing-jcs.md`)
- stable field names and stable ordering when rendered (key sort for canonicalization)


## Trace objects (typed by domain)

`--trace` output MUST be a schema-defined object for the domain being traced.

Examples:
- policy explain traces: `spec/policy.trace.schema.json` (see `docs/416-policy-trace-format-and-explain-surfaces.md`)

## Canonical domain outputs (typed)

When a command’s primary output is a domain artifact, `--json` MUST emit the schema-defined artifact directly (not wrapped).

Examples:
- `derive probe platform --json` → `spec/platform.report.schema.json`
- `derive plan fw-update --json` → `spec/fw.update.plan.schema.json`
- `derive apply fw-update --json` → `spec/fw.update.receipt.schema.json`
- `derive incident timeline --since 30m --json` → `spec/incident.timeline.schema.json`

## Error model (v1)

Errors are structured and stable:
- `error.code` : stable enum string (`LOCK_FETCH_FAILED`, `POLICY_DENIED`, …)
- `error.path` : JSON-pointer into the offending document when applicable
- `error.summary` : one-line human summary (safe)
- `error.detail[]` : optional structured facts (safe)
- `hint[]` : optional actionable hints (safe)

No secrets are ever emitted; secrets are referenced by digest only.

## Why this matters
- LLM patch loops stay deterministic (docs/81)
- conformance tests can compare golden JSON
- external tools can integrate without scraping text

## Non-goals (v1)
- supporting arbitrary output formats (JSON only; others via adapters)
- embedding a general templating language in output

See RFC-0057 and ADR-0028.

Last updated: 2026-02-27r128
