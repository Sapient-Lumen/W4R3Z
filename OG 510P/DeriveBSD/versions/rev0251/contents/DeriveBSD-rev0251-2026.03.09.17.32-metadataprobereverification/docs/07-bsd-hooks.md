# BSD hooks (value multipliers)

This document lists BSD-specific leverage points that should be **interfaces** in the core, not hard-coded assumptions.

## High-value hooks

1. **Jails as the default build sandbox**
2. **ZFS boot environments** for system activation
3. **Capsicum** hardening for critical tooling (FreeBSD)
4. **pf anchors** for composable firewall modules
5. **Jails as deployable artifacts** (closure → jail image)

## Rule

FreeBSD hooks attach cleanly and should not compromise the Derive core's simplicity or auditability. Portability is not a v0 goal.


Last updated: 2026-02-23
