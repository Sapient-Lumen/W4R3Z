# RFC-0028: Capsicum/Casper hardening

Status: Draft

## Summary

Use Capsicum capability mode and Casper services to reduce ambient authority in DeriveBSD components.

See `docs/49-capsicum-casper-hardening.md`.

## Goals

- Make least authority the default for:
  - fetchers
  - builders
  - runtime control plane components

## Non-goals

- Inventing new kernel primitives.
