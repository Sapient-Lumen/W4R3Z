# RFC-0044: Resource profile mapping to rctl + cpuset

- Status: draft
- Created: 2026-02-23

## Summary
Specify how DeriveBSD resource profiles are enforced using rctl and cpuset, including what is logged and what becomes Plan identity.

## Goals
- deterministic enforcement
- audit-friendly logs
- safe defaults (avoid hidden autoscaling)

## References
- rctl(4), rctl(8), rctl.conf(5)
- cpuset(1)
