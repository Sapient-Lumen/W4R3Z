# Remedy-hardening-attestation closure-proof page — link expiry, peer confirmation, residual unknowns, and closure sentence ceiling

## Purpose

This proof page preserves the evidence bundle for a closure claim.
It exists so the archive can distinguish `future access blocked` from `audience actually closed`.

## Minimum evidence families

The page must preserve at least these evidence families when applicable:

- peer-side confirmation of retirement or removal
- linked-device removal evidence
- unlinked-peer confirmation evidence
- single-file recipient retirement evidence
- link-expiry or click-budget exhaustion evidence
- approval revocation or share-right removal evidence
- residual local-share or local-folder evidence
- unknown-survivor ledger

## Evidence grading

Each evidence item must be graded as one of:

- proves byte retirement
- proves future access blocked only
- proves authority revoked only
- proves visibility changed only
- suggests but does not prove cleanup
- contradicts closure claim

## Required summary fields

The proof page must summarize at least:

- governed audience size in scope
- confirmed-closed slice count
- inferred-closed slice count
- unknown slice count
- known surviving residual-carrier count
- highest-severity unknown survivor class
- strongest honest closure sentence
- blocked stronger closure sentence

## Sentence ceiling rule

The page must never allow a stronger closure sentence than the weakest unresolved survivor fact permits.
For example:

- expired link without recipient proof must not justify `recipient closed`
- disconnect without filesystem retirement proof must not justify `device clean`
- linked-device removal without unlinked-peer evidence must not justify `audience closed`
- UI removal without local-byte retirement proof must not justify `residue retired`
