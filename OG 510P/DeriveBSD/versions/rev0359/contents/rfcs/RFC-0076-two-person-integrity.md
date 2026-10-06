# RFC-0076: Two-person integrity (separate approvals)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Enable policy to require *separate* approvals for plan/policy decisions and artifact publication, with optional witness rebuild attestations.

## Motivation

A single compromised key/operator should not be enough to ship a malicious artifact.

## Goals / Non-goals

Goals:
- allow trust policy to express multi-step approvals
- keep it lightweight (no workflow engine)

Non-goals:
- implementing a full RBAC/approval product

## Proposal

- Extend trust policy to support:
  - `approvals.plan.threshold`
  - `approvals.publish.threshold`
  - optional `approvals.witness_rebuild.threshold`

- Bind approvals to:
  - Plan digest
  - policy decision record digest
  - artifact digest

- `derive verify` checks that required approvals exist.

## Alternatives considered

- single signing key for everything

## Backwards compatibility

Default policy can set thresholds to 1.

## Security considerations

- keys should be stored/used with separate operational boundaries

## Open questions

- how to represent approval bundles (DSSE envelopes vs bespoke)
