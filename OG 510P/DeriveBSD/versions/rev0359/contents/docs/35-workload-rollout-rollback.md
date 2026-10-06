# Workload rollout and rollback model (microVMs)

This doc defines how “system generations” relate to workloads in a VM-centric DeriveBSD.

## Desired state as data

A host generation references a set of workload descriptors:
- `artifact_digest`
- `manifest_digest`
- `config_digest` (non-secret)
- `instance_name` / `instance_id` template
- `state_policy` (ephemeral | persistent dataset)

Activation is: reconcile running state to desired state.

## Rollout strategies (v1)

- **Replace-image (default)**:
  - build new artifact
  - switch desired state pointer
  - restart VM
- **Blue/green** (optional):
  - run new instance alongside old
  - cut traffic by pf/bridge policy change
  - retire old

## Stateful workloads

- persistent state lives outside the image (ZFS dataset)
- image upgrades MUST NOT mutate state schema implicitly
- snapshot policy is explicit:
  - pre-upgrade snapshot (required)
  - retention policy (operator-controlled)
- if schema changes are required, they must be represented as artifacts/evidence:
  - `statedb` expectations
  - `state-migration-plan` steps
  - per-volume `state-migration-receipt`

See: `docs/217-state-datasets-and-migrations-as-evidence.md`.

## Host rollback

Host rollback (ZFS boot env) must also roll back the *desired state pointers* for workloads.
Running VMs are reconciled accordingly after reboot/switch.

See RFC-0017.

Fleet-wide staged rollout primitives (optional): `docs/177-fleet-coordinated-rollouts.md` (RFC-0112).

Last updated: 2026-02-24
