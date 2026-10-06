# Packaged base system lessons ("pkgbase" → DeriveBSD sets)

FreeBSD 15.0 makes the “base system” installable and upgradable via `pkg(8)` (packaged base system / “pkgbase”).
This is a strong operational lesson: **base is not magic**, it is an explicit, versioned set of artifacts.

References:
- FreeBSD 15.0 release announcement (“Packaged base system”): https://www.freebsd.org/releases/15.0R/announce/
- FreeBSD wiki: pkgbase project notes: https://wiki.freebsd.org/pkgbase
- `pkgbase(7)` manpage (repository + naming conventions): https://man.freebsd.org/cgi/man.cgi?query=pkgbase

Note: pkgbase appears to be evolving; treat it as an excellent **shape** to steal (base-as-packages), not a stability guarantee.

## DeriveBSD direction

Introduce **base sets** as first-class artifact targets, conceptually similar to:
- `set:kernel`
- `set:userland`
- `set:crypto`
- `set:toolchain`

Each set is:
- derived from a locked input (e.g., src tree + toolchain)
- content-addressed and signed
- installable into a host generation (ZFS BE) or builder base

## Why this matters

- Updates become **set replacement** (transactional), not “mutate /usr”.
- `derive explain` can answer: *which set put this file here and why?*
- Emergency patch mode becomes patching a set or overlaying a signed patchset artifact.

## Boundary with ports/pkg lane

- Ports/pkg lane remains for “ecosystem breadth”.
- Base sets remain for “TCB + upgrade core”.

## Minimal v1 plan

- Define a `base.set` manifest shape (not necessarily pkg-compatible).
- Allow a host generation to declare which base set digests it includes.
- Reuse existing signature + channel metadata machinery.

See RFC-0079.
