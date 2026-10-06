# RFC-0079: Packaged base system and base sets

Status: Draft

Decision note: the archive accepted the base-boundary cut in `adrs/ADR-0116-derived-base-sets-and-pkgbase-adapter-boundary.md`. This RFC remains the place for follow-on implementation detail (bootstrap sequence, finer split questions, builder workflow).

## Summary

Introduce **base sets** as first-class artifact targets (kernel/userland/toolchain split) to make the “base system” explicit, upgradable, and verifiable.

Motivation: FreeBSD 15.0’s packaged base system (pkgbase) shows the operational value of treating base as explicit packages/sets. https://www.freebsd.org/releases/15.0R/announce/

## Goals

- Base system is represented as derivable, signed artifacts.
- Host generations declare which base set digests they contain.
- Rollback remains ZFS BE-native.

## Non-goals

- Replacing FreeBSD `pkg(8)`.
- Requiring compatibility with pkg metadata formats.

## Design sketch

- New artifact target kind: `base.set`.
- `base.set` manifest includes:
  - input lock refs
  - build environment digest
  - file tree root digest
  - closure manifest digest
  - signatures + attestations

See: `docs/111-packaged-base-pkgbase.md`.

## Open questions

- Do we ever need optional native classes beyond `kernel`, `userland`, and `toolchain`, or should finer granularity stay adapter/backend-private?
- What is the bootstrap path for producing the first trusted toolchain/base sets?
- Should patchsets apply to sets, to host generations, or to both as different operational lanes?
