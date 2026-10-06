# Sandbox hardening (BSD-first)

## Jail backend requirements (v1)

- declared inputs mounted read-only
- writable build dir only
- network modes:
  - none (default)
  - fetch-only (only fetcher has network)
  - allow (explicit; logged)
- log capture + environment summary
- per-build UID/GID isolation

## Defense in depth (later)

- Capsicum hardening for fetcher/store/activation tools
- optional VNET for integration tests with constrained egress


Last updated: 2026-02-23
