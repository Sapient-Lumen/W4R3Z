# RFC-0089: SCITT ledger receipts lane (optional)

Status: Draft

## Summary

Add an optional lane for publishing DeriveBSD statements (provenance/attestations) into
SCITT-style transparent registries and recording **receipts** as evidence.

References:
- IETF SCITT WG: https://datatracker.ietf.org/group/scitt/about/
- SCITT architecture draft: https://datatracker.ietf.org/doc/draft-ietf-scitt-architecture/

## Goals

- Make supply-chain statements tamper-evident and monitorable.
- Keep receipts small and content-addressed.
- Allow multiple registries; verification remains “receipt binds to statement digest”.

## Non-goals

- Mandating SCITT for all users.
- Replacing signatures/attestations; SCITT is additional evidence.

## Design sketch

- Evidence object: `transparency.scitt.receipt.v1`
  - `statement_digest`
  - `registry_id`
  - `receipt`
- Publication happens in a least-authority publisher role (builders remain hostile).
- Policy can require receipts for promotion/consumption.

See: `docs/132-scitt-ledger-receipts.md`.
