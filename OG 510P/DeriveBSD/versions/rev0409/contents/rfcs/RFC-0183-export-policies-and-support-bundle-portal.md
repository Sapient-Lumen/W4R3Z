# RFC-0183: Export policies and support-bundle portal

Status: Draft

## Problem

DeriveBSD can produce rich evidence bundles, but most ecosystems fail at the last mile:
**sharing diagnostics** becomes an ad-hoc, high-privilege act (scp a tarball, paste logs).

Without a first-class export surface, we cannot reliably answer:
- what bytes were shared?
- under what policy?
- were redaction transforms applied?
- was user consent/approval obtained?

## Goals

- Separate “collect evidence” from “export evidence”.
- Make exporting a **policy-bound** and **receipted** action.
- Preserve least-authority: exporting should not require ambient root access.

## Proposal

1) Introduce `export.policy` as a share contract:
   - allowed artifact kinds
   - required transforms (redaction)
   - recipient/transport constraints
   - optional consent + two-person requirements

2) Introduce `export.receipt` as evidence of an export:
   - exported artifact digest(s)
   - policy digest
   - transform digest (if applied)
   - lease id used to authorize
   - adapter metadata (destination/ticket id)

3) Add a Support Bundle Export Portal concept:
   - request export → obtain a scoped lease → perform export → emit receipt

References:
- `docs/251-export-policies-and-support-bundle-portal.md`

