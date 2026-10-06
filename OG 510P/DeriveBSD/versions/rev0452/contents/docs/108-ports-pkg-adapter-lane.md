# Ports/pkg adapter lane (bootstrap breadth)

We want Nix-like breadth quickly, but we cannot inherit “ambient impurity” forever.

## Approach

- Treat ports/pkg as a **source ecosystem**.
- Translate a port/package into a Derive Plan:
  - pinned inputs (ports snapshot + distfiles)
  - declared build dependencies
  - sandbox policy (deny network by default)
  - reproducibility knobs recorded

- Use jail-backed builds (poudriere-style) as a pragmatic backend for early breadth.

## Graduation

Imported packages can become native Derive specs without breaking users, because:
- interface stays stable (closure + services)
- deployment objects stay explainable

This extends `docs/08-compat-ports.md`.
See RFC-0077.
Last updated: 2026-02-23
