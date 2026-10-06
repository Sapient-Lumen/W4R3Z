# Build sandbox: jails-first (poudriere lessons)

DeriveBSD treats builders as hostile. Builds must run in a constrained sandbox with deterministic inputs.


Reference: FreeBSD Handbook notes that `poudriere` uses FreeBSD jails to set up isolated compilation environments. https://docs.freebsd.org/en/books/handbook/book/

## v1 stance
- Every build runs in a fresh jail derived from a pinned base.
- Network denied during build by default (ADR-0008).
- Fetching sources is a separate constrained phase (see `docs/48-fetch-phase-design.md`).

## Repro knobs
Determinism requires environment normalization:
- `TZ=UTC`, fixed locale, pinned umask
- optional SOURCE_DATE_EPOCH policy (`docs/55-reproducible-builds-freebsd-lessons.md`)

Last updated: 2026-02-23
