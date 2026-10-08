# Redaction log (hashes-first)

**Track:** Shared (cross-cutting)


> Ship as `redaction-log.md` alongside a bundle *only when* evidence-relevant artifacts were redacted/transformed.
> Keep it small. Never include removed secrets/PII.

## Purpose (1–2 lines)
- Why was redaction needed for this bundle?

## Entries

### RED-001
- source_path: `...` *(bundle-relative path or `TYPE:path` token)*
- source_sha256: `sha256:<64-hex>` *(OK if the source is sealed/private; publish digest only)*
- derived_path: `...` *(the published/redacted derivative)*
- derived_sha256: `sha256:<64-hex>`
- transformation: `...` *(bounded: crop/blur/remove-query-params/excerpt/etc)*
- tool: `...` *(e.g., `imagemagick 7.x`, `python 3.11 script`, `manual`)*
- reason: `remove_secret|remove_voter_identifier|remove_internal_endpoint|other`
- review: `self_reviewed|two_person|unknown`
- notes: `none|...` *(optional; bounded; no removed bytes)*

### RED-002
- *(repeat as needed; prefer one entry per published derivative)*


## Publishable lint exceptions (WARN-only; rare)

If the publishable lint emits a WARN that is **truly load-bearing** for a public bundle,
record the minimization + justification here and add one directive per suppressed code:

- lint-allow: `<code>`

This suppresses WARN-only findings for the packet. FAIL is never suppressed.
