# Packaged base system lessons ("pkgbase" → DeriveBSD sets)

FreeBSD 15.0 makes the “base system” installable and upgradable via `pkg(8)` (packaged base system / “pkgbase”).
That is a strong operational lesson: **base is not magic**, it is an explicit, versioned set of artifacts.

The archive has now made the hard coherence cut too:
DeriveBSD keeps **native derived `base.set` artifacts** as the source of truth, while `pkgbase` remains an explicit adapter lane.
See: `docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md`, `adrs/ADR-0116-derived-base-sets-and-pkgbase-adapter-boundary.md`.

References:
- FreeBSD 15.0 release announcement (“Packaged base system”): https://www.freebsd.org/releases/15.0R/announce/
- FreeBSD `freebsd-base(7)` / `pkgbase(7)` manpage: https://man.freebsd.org/cgi/man.cgi?query=pkgbase
- FreeBSD `build(7)` (building base-package repositories from source): https://man.freebsd.org/build

Note: pkgbase is now important enough to learn from, but it still should not become DeriveBSD’s native deployment identity.
Treat it as an excellent **shape** to steal (base-as-packages / explicit sets), not as the archive’s source of truth.

## DeriveBSD direction

Introduce **base sets** as first-class artifact targets with a deliberately small native split:
- `kernel`
- `userland`
- `toolchain`

Each set is:
- derived from locked inputs (e.g., source tree + toolchain + policy)
- content-addressed and signed
- installable into a host generation (ZFS BE) or builder base
- explainable by digest rather than by package-manager folklore

The canonical contract now lives in `spec/base.set.schema.json`.

## Why this matters

- Updates become **set replacement** (transactional), not “mutate /usr”.
- `derive explain` can answer: *which base set put this file here and why?*
- Emergency patch mode can target a `base.set` digest without making base a special case.
- A–D keep one base story without forcing pkg tooling semantics into the center of the design.

## Boundary with adapter lanes

- Ports/pkg remains the ecosystem-breadth lane.
- Pkgbase import/export remains a bounded compatibility lane.
- Native `base.set` artifacts remain the source of truth for “TCB + upgrade core”.

## Minimal v0 plan worth implementing

- Keep `base.set` small and stable (`kernel`, `userland`, `toolchain`).
- Allow host generations and patchsets to bind to `base.set` digests.
- Preserve pkgbase interop only as explicit adapter metadata / receipts.

See RFC-0079 and ADR-0116.

Last updated: 2026-03-16r255
