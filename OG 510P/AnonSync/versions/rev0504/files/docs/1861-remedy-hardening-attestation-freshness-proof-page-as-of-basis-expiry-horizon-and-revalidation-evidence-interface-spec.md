# Remedy-hardening-attestation-freshness proof page — as-of basis, expiry horizon, and revalidation evidence

## Purpose

This page is the durable proof surface for the strongest honest claim about whether a sealed verifier bundle is still current enough to support a live sentence.
It exists so the product can preserve one explicit proof basis for freshness rather than making later readers infer that basis from timestamps, logs, history, fingerprints, or operator memory.

## Proof payload

The page must preserve at least:

- case identifier
- attestation bundle identifier
- seal identifier and seal standing status
- historical capture completion time
- explicit as-of claim time
- freshness horizon and expiry event
- history horizon actually available
- debug-log horizon actually available
- identity fingerprint basis used for currentness review
- whether identity recreation, unlink, relink, or version-lane change occurred after sealing
- approval carry-forward rule used for currentness review
- peer cache or routing cache verdict
- last revalidation event and actor
- current revocation or challenge status
- highest honest current freshness-aware sentence
- strongest blocked stronger sentence

## Mandatory proof distinctions

The proof must preserve these separate facts:

- `sealed as historical` versus `sealed and current as-of`
- `freshness near expiry` versus `freshness expired`
- `identity unchanged` versus `identity re-proven after change`
- `approval previously remembered` versus `approval revalidated now`
- `evidence horizon still present` versus `evidence horizon already rotated away`
- `revalidation not required` versus `revalidation completed`
- `no challenge seen` versus `revocation or challenge cleared`

## Proof ceiling

The page must visibly block stronger sentences when any of these remain true:

- the as-of basis is missing or too old
- history coverage no longer spans the required currentness horizon
- log evidence no longer spans the required currentness horizon
- identity continuity is only inferred, not re-proven
- linked-device approval carry-forward is still too broad
- peer cache ambiguity remains unresolved
- revalidation is pending or overdue
- revocation or challenge is still open
