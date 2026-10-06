# RFC-0095: Overlay transforms (deterministic patches)

## Summary
Introduce ordered, deterministic overlay transforms as a replacement for “Nix overlays” inside a canonical Spec/Lock/Plan pipeline.

## Motivation
Power users need to override and extend the package set without forking the world.

## Proposal
- define an overlay list in Spec (or adjacent file)
- each overlay is a schema-validated patch (merge-patch recommended)
- overlay digests are bound into the Plan digest
- `derive diff --json` attributes changes to overlay ids

## Open questions
- patch format: merge-patch only vs also json-patch
- where overlays apply: Spec-only vs allow Lock overrides

See: `docs/160-overlay-transforms.md`.
