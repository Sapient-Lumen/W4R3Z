# Redactions

This bundle is intended to be publishable.

## What gets removed
We remove *obvious private keys / secret signing material* when importing upstream trees.
In practice this means files that are explicitly named as secret keys (e.g., `*_private.pem`, `*_sk.pem`, `*_sk.hex`, `*_private.key`, etc.).

## What stays
- Public keys and certificates (e.g., `*_public.pem`)
- Signed statements / receipts / DSSE envelopes
- Non-secret example payloads

## Audit trail
- `REDACTIONS.paths` lists the upstream-relative paths of the removed items.
- Those paths are **recorded even though the files themselves are omitted**, so an auditor can check that the only deletions are key material.

If you need the exact removed key files for a private repro scenario, keep them out-of-band.
