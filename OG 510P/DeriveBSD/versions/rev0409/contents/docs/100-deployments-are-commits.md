# Deployments are commits (ZFS-native)

Goal: make “what is deployed” a *single, verifiable object* that is easy to status/diff/rollback.

This borrows the operational model from OSTree/rpm-ostree (“deployments are atomic units”, “vendor composes → clients replicate”), but implements it with FreeBSD-native primitives:
- ZFS boot environments for hosts
- microVM bundles for workloads

## Concept

A **Deployment** is a signed reference to:
- a root tree digest (host BE root or microVM rootfs)
- a Plan digest
- a closure digest/proof reference
- a policy decision record digest

Host deployment objects are materialized as ZFS BEs.
Workload deployment objects are materialized as microVM bundle revisions.

## Why it fits DeriveBSD

- switches are atomic
- rollbacks are constant-time
- “status” is just listing deployments
- “why is this here” flows through the evidence chain

## Non-goals (v1)

- reinventing a general package manager UX
- live mutation outside activation hooks

See RFC-0069.
Last updated: 2026-02-23
