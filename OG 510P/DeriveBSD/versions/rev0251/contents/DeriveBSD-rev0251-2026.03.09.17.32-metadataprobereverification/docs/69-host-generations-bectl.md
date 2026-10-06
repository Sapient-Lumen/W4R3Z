# Host generations: ZFS boot environments via bectl(8)

DeriveBSD wants host updates to be:
- atomic
- rollbackable
- explainable

FreeBSD provides `bectl(8)` to manage ZFS boot environments.

(see `docs/32-curated-references.md`)

See also: `docs/284-bootenv-switching-as-evidence.md` (switch plan + receipt: `spec/bootenv.switch.plan.schema.json`, `spec/bootenv.switch.receipt.schema.json`).

## DeriveBSD stance

- Each realized host Plan produces a new boot environment (BE).
- Switching host state = making a BE active + rebooting (or equivalent).
- Rollback = selecting the prior BE.

Mile-high direction: treat BEs as **deployment objects** (“deployments are commits”), so status/diff/rollback can be expressed uniformly for hosts and workloads. See `docs/100-deployments-are-commits.md`.

## Minimal invariants (v1)

- Switching is **tentative by default**: activate for next boot, then commit only after health checks pass (see `docs/112-health-gated-updates.md`).

- BE name includes generation id (or references it deterministically).
- Activation emits a “boot manifest”:
  - generation id
  - BE name
  - boot artifacts digests (docs/51)
  - ZFS dataset snapshot ids (if available)

## Optional distribution lane (dataset-native)

If the host root and declared subdatasets are ZFS-native, DeriveBSD can optionally ship a generation as a **signed ZFS send stream** and receive it into a quarantine dataset before promotion.

See: `docs/126-zfs-send-distribution.md`.

## Why this matters

- reduces “mutable snowflake host” risk
- gives simple incident response:
  - `rollback instantly` becomes a first-class action
- makes host state auditable:
  - “what booted” maps to store digests

## Non-goals (v1)

- supporting non-ZFS root hosts as the primary platform
- live in-place mutation beyond controlled activation hooks

Last updated: 2026-02-23
