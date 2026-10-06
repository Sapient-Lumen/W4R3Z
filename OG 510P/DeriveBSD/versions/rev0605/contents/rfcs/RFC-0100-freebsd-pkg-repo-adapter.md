# RFC-0100: FreeBSD pkg repository adapter (optional)

Status: **draft**

## Problem

Many FreeBSD operators rely on pkg repositories. DeriveBSD’s native cache model is different.
We want a compatibility lane that enables adoption without weakening verification.

## Proposal

Define an adapter:
- export a Derive artifact set (closure-selected) into a pkg repository layout
- include `derive.repo.manifest` mapping pkg names → Derive digests
- treat pkg repo signing as a crypto operation (split crypto compatible)

Consumption rules:
- pkg signatures are an additional check
- Derive digest + required attestations remain the source of truth

## References

- pkg.conf(5) signature modes: https://man.freebsd.org/cgi/man.cgi?query=pkg.conf
- pkg-repo(8): https://man.freebsd.org/pkg-repo%288%29

See: `docs/165-freebsd-pkg-repo-adapter.md`.
