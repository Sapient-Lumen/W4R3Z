# Unikernels and “going for broke” security

Should DeriveBSD *be* a unikernel, or should it *produce* unikernels (or microVM/Wasm artifacts) as deployment targets?

## Recommendation

- Don’t replace DeriveBSD with a unikernel OS model (v1).
- Do design DeriveBSD to *target*:
  - sealed microVM images
  - unikernel images for narrow services
  - optional Wasm/WASI bundles

Treat these as **artifact targets** behind a stable interface.

## Target framework pointer

See `docs/73-artifact-target-framework.md` for unified target kinds (microVM/unikernel/wasm).


Last updated: 2026-02-23
