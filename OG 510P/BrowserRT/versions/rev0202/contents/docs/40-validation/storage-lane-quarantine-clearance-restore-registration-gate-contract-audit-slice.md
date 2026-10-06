# Storage-lane quarantine clearance restore registration gate contract audit

Revision: rev0086  
Task: `facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit`

## Purpose

The audit keeps the rev0086 restore registration gate wired through runtime, release-light proof, managed Chromium proof, docs, manifest, impact map, and surface inventory.

## Checks

The audit verifies that:

- runtime restore rejects when receipt registration rejects;
- wrong-lane restore is visible as a restore rejection, not a successful restore;
- release and browser proofs exercise rejected restore, stale import backpressure, valid restore, and stale replay rejection;
- first-read docs and package scripts point at the rev0086 current office;
- the manifest, impact map, and surface inventory contain the release proof, browser proof, and audit task.

## Non-claims

The audit only reads local files. It does not launch Chromium and does not make storage durability, cancellation, quota, eviction, cryptographic attestation, cross-browser, or production-readiness claims.


## rev0086 audit anchor

This restore registration gate slice records wrong-lane restore behavior: registration rejects before replay guard state installs, the valid restore path is lane-bound, and the Managed Chromium side proves the OPFS/Web Locks handoff. This is not cryptographic attestation and not production readiness.
