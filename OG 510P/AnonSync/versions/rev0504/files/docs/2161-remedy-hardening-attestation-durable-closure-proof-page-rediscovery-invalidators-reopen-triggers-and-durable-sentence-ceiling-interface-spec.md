# Remedy-hardening-attestation durable-closure proof page — rediscovery invalidators, reopen triggers, and durable sentence ceiling

## Purpose

This proof page preserves the evidence bundle for a durable-closure claim.
It exists so the archive can distinguish `closed at the horizon` from `still honest if stale material resurfaces later`.

## Minimum evidence families

The page must preserve at least these evidence families when applicable:

- base closure-verdict evidence
- rediscovery-surface inventory evidence
- archive-retention and hidden-residue evidence
- disconnected-folder residue evidence
- placeholder/refetch posture evidence
- transfer-retention and expired-transfer evidence
- forwarded/reshared-survivor evidence
- invalidator and re-open policy evidence

## Evidence grading

Each evidence item must be graded as one of:

- proves durable retirement
- proves point-in-time closure only
- proves rediscovery surface remains latent
- proves only UI disappearance
- suggests but does not prove durable closure
- contradicts durable closure claim

## Required summary fields

The proof page must summarize at least:

- base closure verdict
- durability horizon class
- rediscovery surface count
- latent survivor class count
- automatic invalidator count
- maximum honest re-open lag
- strongest honest durable-closure sentence
- blocked stronger durable-closure sentence

## Sentence ceiling rule

The page must never allow a stronger durable-closure sentence than the weakest unresolved rediscovery fact permits.
For example:

- an expired transfer record without proof of local-byte retirement must not justify `rediscovery-safe`
- a disconnected folder that still remains in a filesystem must not justify `retired if rediscovered`
- an archive with indefinite retention must not justify `no latent survivors remain`
- a forwarded one-time copy must not justify `durably closed` without qualification
