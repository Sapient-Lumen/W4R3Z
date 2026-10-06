# ADR-0116: Derived base sets are canonical; pkgbase remains an adapter lane

- **Status:** Accepted
- **Date:** 2026-03-16
- **Deciders:** DeriveBSD archive maintainers

## Context

Open question 3 in `docs/266-open-questions-and-risk-register.md` kept one foundational ambiguity alive:
should DeriveBSD treat the FreeBSD base system as a native derived artifact, or should it grow around
`pkgbase` metadata and workflows?

That ambiguity was becoming expensive.
The archive already assumes all of the following in scattered places:

- patchsets may target a `base.set` digest,
- host generations should stay digest-bound and explainable,
- A–D must share one update / rollback story without forks,
- and adapters must remain killable rather than becoming the real product.

Meanwhile, upstream FreeBSD has now made packaged base concrete enough to matter operationally:
FreeBSD 15.0 offers a packaged-base installation path, ships `freebsd-base(7)` / `pkgbase(7)`, and can build
base-package repositories from source via `build(7)` / `release(7)`. That proves the *shape* is valuable,
but it does not mean DeriveBSD should make `pkg(8)` metadata its source of truth. See `docs/32-curated-references.md`.

If we leave this boundary undecided, “base” becomes a special snowflake lane:
not quite derivations, not quite adapters, and eventually the place where reproducibility and explainability go to die.

## Decision

DeriveBSD now fixes the base-system boundary as follows:

1. **`base.set` is the canonical base artifact.**
   DeriveBSD treats base as native, digest-bound derived artifacts rather than as a special install lane or as raw `pkgbase` metadata.

2. **`pkgbase` is an explicit adapter lane, not the source of truth.**
   Importing or exporting pkgbase-shaped repositories is allowed, but only through bounded adapter workflows that emit receipts and remain killable by policy.

3. **v0 keeps the native split intentionally small.**
   The only canonical base-set classes are:
   - `kernel`
   - `userland`
   - `toolchain`

   Finer-grained subpackages may exist inside an adapter or build backend, but they do not become the archive-wide deployment contract by default.

4. **Host generations and patchsets bind to `base.set` digests.**
   They may carry adapter metadata for interop, but deployment / rollback / explainability terminate in native `base.set` identities.

## Consequences

### Positive

- Base stops being a special case: it joins the same derivation-first, digest-bound review model as the rest of DeriveBSD.
- A and D get a stable auditable base-update object that works with offline promotion, rollback floors, and long-term rebuildability.
- B and C keep compatibility options because pkgbase interop remains available as an adapter instead of being forbidden.
- The archive now has a small concrete spec surface (`spec/base.set.schema.json`) that is worth implementing.

### Trade-offs

- The decision rejects a tempting path where the upstream package split becomes the native DeriveBSD contract “for free.”
  That means DeriveBSD must own its own typed `base.set` manifest.
- The v0 split is intentionally conservative; some users will want more granular native base subsets sooner.
  They must justify that later instead of inheriting upstream package names as archive law.

## What this does not decide

This ADR does **not** decide:

- the exact bootstrap sequence for building the first native toolchain and base sets,
- the final per-file ownership map inside each set,
- whether future optional native classes such as `debug`, `tests`, or `rescue` are worth the added entropy,
- or whether specific deployments consume native sets directly or through an image/bundle wrapper.

It only fixes the coherence cut:
DeriveBSD base identity is native and derivation-first; pkgbase remains a useful but subordinate adapter.
