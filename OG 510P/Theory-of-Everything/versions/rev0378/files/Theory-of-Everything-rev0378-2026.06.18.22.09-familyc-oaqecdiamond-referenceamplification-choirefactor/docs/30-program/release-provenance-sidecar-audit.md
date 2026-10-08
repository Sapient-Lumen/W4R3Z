# Release provenance sidecar audit

Revision: `rev0365`

## Scope

This audit implements the highest-risk missing control from the rev0364 mission-heart scan: a small interoperability/provenance bridge that external tools can inspect without treating it as a second source of archive truth.

## Implemented change

- Added `tools/release_provenance_sidecar.py`.
- Generated `ro-crate-metadata.json` as a minimal RO-Crate / JSON-LD release description.
- Generated `RELEASE-BUILD-PROVENANCE.json` as an unsigned local material/build-provenance sidecar.
- Added `tools/release_provenance_sidecar.py --check` to the timed lint path and package smoke path.

## Design rule

The sidecars are **derived metadata**, not owners. They point at existing owner surfaces:

- `RELEASE-MANIFEST.json` owns release identity;
- `REVISION-RECEIPT.json` owns revision rationale;
- `SOURCE-SNAPSHOT-MANIFEST.json` owns compact public-source custody;
- `tools/package_release.py` owns deterministic package construction;
- the final zip SHA-256 remains an external package result printed by the packager, because recording a final zip digest inside the zip would be self-referential.

## Why this was prioritized

This closes a real external-interoperability gap without widening the scientific registry stack. The archive already has careful internal custody, but an external reader had no compact standards-facing way to ask: what is this bundle, what generated it, which files are release-critical, and what digest summarizes the material tree?

## What it deliberately does not do

- It does not sign an attestation.
- It does not assert SLSA compliance.
- It does not assert Software Heritage identifiers.
- It does not vendor raw data, maps, likelihoods, chains, or code checkouts.
- It does not promote any scientific route or credit state.

## Followthrough

A future pass should add signed provenance only outside the self-contained bundle or by using a two-object release pattern: in-bundle material provenance plus out-of-bundle final artifact attestation.
