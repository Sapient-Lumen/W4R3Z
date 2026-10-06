# Sandbox

The sandbox is the heart of determinism and safety. The Derive core should define a **sandbox interface** with multiple backends.

## Policies (first-class)

- network: never | fetch-only | allow
- filesystem: declared inputs only
- time: fixed | host
- env: normalized (locale, timezone)
- cpu features: baseline | native
- entropy: controlled mode (optional)

## Backends

- **FreeBSD jails** (default target): strongest hermeticity with familiar primitives.
- **chroot/namespace** fallback for non-BSD prototyping.
- **OpenBSD pledge/unveil** integration for hardening (where applicable).

## Principle: auditable impurity

Any deviation from the strict sandbox must be:
- explicit in the Plan
- included in the artifact identity and metadata
- visible in `derive explain`


Last updated: 2026-02-23
