# Witness network operations

**Track:** A (Deployable core)


## Goal
Turn “we have a witness quorum” into an operationally real property that resists capture and configuration drift.

This document defines:
- witness onboarding and configuration baselines
- witness liveness checks and alerting
- witness rotation execution
- safe shutdown when quorum integrity is in question

## Baseline requirements
- Witnesses MUST run hardened signing infrastructure with explicit key custody procedures.
- Witnesses MUST refuse to sign checkpoints that are inconsistent with previously signed checkpoints.
- Witnesses MUST publish signed status (healthy/degraded/down) at a defined cadence.

## Witness configuration distribution
- Witness configuration bundles MUST be content-addressed and signed.
- Configuration MUST be mirrored through multiple channels.

## Rotation and stale-state defenses
To prevent clients from accepting stale witness sets during partial partitions:
- witness set changes MUST include a tombstone marker for the prior set
- clients MUST refuse “fallback to older witness set” unless explicitly permitted by a pre-committed migration policy

## Community coordination
When possible, adopt a community configuration approach (e.g., witness network directories) to reduce bespoke misconfiguration.
