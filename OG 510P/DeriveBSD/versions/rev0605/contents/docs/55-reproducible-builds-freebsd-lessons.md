# Reproducible builds: FreeBSD lessons and DeriveBSD knobs

Reproducibility improves supply-chain assurance and helps detect compromised builders.

## v1 knobs
- optional `reproducible=true` policy mode
- `SOURCE_DATE_EPOCH` policy (auto or explicit)
- `TZ=UTC`, deterministic locale, pinned umask
- pinned toolchains and base jail filesystem digests

See RFC-0032 and ADR-0012.
Last updated: 2026-02-23
