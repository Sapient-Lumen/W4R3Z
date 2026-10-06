# ADR-0027: Use rc.d + rc.conf as activation backend (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD uses the native rc.d framework and rc.conf variables as the service orchestration backend for host generations, with service jails used where feasible.

## Consequences
- avoids inventing a new init/supervisor
- integrates with FreeBSD service-jail hardening
- must provide deterministic generation of rc knobs and scripts
