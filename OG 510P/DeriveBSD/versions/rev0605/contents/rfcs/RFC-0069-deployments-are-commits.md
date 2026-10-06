# RFC-0069: Deployments are commits (ZFS-native)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Define a **Deployment** object that represents a bootable host generation or runnable workload revision as an atomic, signed unit (“deployments are commits”).

## Motivation

Operational simplicity matters:
- status should show “what is deployed” clearly
- upgrades should be atomic
- rollbacks should be routine

OSTree/rpm-ostree demonstrate this UX: server composes → clients replicate; deployments are atomic, bootable units.

## Goals / Non-goals

Goals:
- unify host generation and workload revision as one concept
- bind deployment to evidence chain: Plan + policy record + closure proof
- enable `derive deploy status/rollback/diff`

Non-goals:
- replace the package story; this is about deployment units

## Proposal

### Deployment object (logical)

A deployment reference binds:
- `deployment_id` (digest)
- `plan_digest`
- `policy_decision_digest`
- `closure_digest` (manifest/proof reference)
- `root_tree_digest` (host BE root or microVM rootfs)
- `artifacts[]` (bundle digest(s), boot artifacts, SBOM, attestations)
- `signatures[]`

### Host materialization

- Activation creates a new ZFS BE.
- The BE name deterministically references `deployment_id` (or includes it).
- `derive deploy status` lists known deployments (like `rpm-ostree status`).

### Workload materialization

- A microVM bundle revision is labeled/linked to `deployment_id`.
- Rollout/rollback becomes switching the deployment ref.

## Alternatives considered

- continue treating host and workload as separate stories (higher cognitive load)
- treat “deployment” as a purely human label (loses verifiability)

## Backwards compatibility

- existing host generations remain valid; this adds a unifying layer.

## Security considerations

- deployment refs must be signed and covered by policy (two-person integrity may apply)
- rollback/freeze protection comes from channel metadata policy

## Open questions

- schema for deployment refs (do we add `spec/deployment.ref.schema.json` in v1?)
- how to represent ZFS snapshot lineage in the deployment object
