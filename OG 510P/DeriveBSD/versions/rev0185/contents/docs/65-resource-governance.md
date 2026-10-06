# Resource governance (CPU/mem/disk/network)

DeriveBSD needs deterministic resource limits to reduce blast radius and prevent noisy neighbors.

## v1 targets
- CPU pinning / sets (cpuset)
- memory limits via bhyve config + host enforcement
- IO rate limits where available (policy-gated)
- process limits for builders and daemons

## FreeBSD knobs
- `rctl` can enforce resource limits on processes/jails
- jails already provide containment boundaries for builds

## Audit
Resource profiles must be recorded in Plan and in runtime logs for instances.

Optional lane:
- Resource budgets as delegable capability grants (subdivision + usage receipts): `docs/193-resource-budget-capabilities.md`.

See RFC-0041.
Last updated: 2026-02-24
