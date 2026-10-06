# Multiparty approvals and separation of duties (quorum as evidence)

DeriveBSD already uses **leases**, **portals**, and **receipts** to avoid ambient authority.
This document extends that posture to *organizational authority*: the system should make it easy to require **two-person / quorum approvals** for the most dangerous operations.

This is the “four-eyes principle” applied to OS operations:
- prevent a single compromised operator/key from shipping or enabling something catastrophic
- make approval *mechanically verifiable* (receipts bound to digests)
- keep workflows operable (offline approvals, timeboxed grants, and clear downgrade rules)

## What needs multiparty control

At minimum, require quorum approvals for:
- **publishing** to release channels (and for emergency halts/resumes)
- **trust root/key rotation** operations
- **breakglass** entry and high-risk recovery actions
- **network policy** changes that expand exposure (egress classes / inbound listen classes)
- **secrets policy evolution** (e.g., TPM unseal policy changes)

Optional (deployment-dependent):
- exporting sensitive bundles off-host
- enabling high-authority observability (tracing across compartments)

## Product-shape default boundary

Not every product shape should default to the same approval ceremony.

- **A (`fleet_host`)** defaults to digest-bound, distinct-principal approvals for shared-trust mutations such as publish, trust-root changes, and destructive breakglass.
- **B (`workstation`)** defaults to trusted-UI user consent for personal-risk actions; shared-trust or org-wide mutations must stay in an explicit admin lane instead of piggybacking on ordinary prompts.
- **C (`general_os`)** keeps single-principal local admin viable by default; quorum remains an explicit optional lane, not a hidden prerequisite.
- **D (`appliance_factory`)** defaults to digest-bound, role-separated quorum with offline/OOB-capable ceremonies for production-significant mutations.

See: `docs/474-high-risk-approval-posture-by-profile.md`.

## Core pattern: bind approvals to digests

Approvals must not be “approval of an idea”. They are approval of a *specific object*:
- a policy digest
- a plan digest
- an artifact digest

Otherwise, “approve this change” becomes a footgun where the executed bytes differ from what was reviewed.

## Use the existing consent objects as the approval substrate

DeriveBSD already defines:
- `consent.request` (what is being proposed; expiry; required quorum)
- `consent.receipt` (who approved; when; how; optional signatures)

We treat these as the generic **approval request/receipt** objects, used both for:
- end-user consent (desktop portals)
- operator quorum approvals (release, policy, breakglass)

See: `docs/256-consent-ux-contract.md`, `spec/consent.request.schema.json`, `spec/consent.receipt.schema.json`.

### Method is a *transport*, not a trust primitive

`method` can be `gui`, `tty`, `oob`, or `auto`.
Trust comes from:
- who the approver is (`actor.subject` / `approvals[].subject`)
- what keys/roles policy says are valid for that action
- what was approved (digests)

## Separation of duties (don’t just do “N approvals”)

The biggest win is not “two people clicked approve”, it’s **role separation**:

- **plan/policy approval**: “is this allowed and correctly constrained?”
- **publication/execution approval**: “is this exact digest what we will run/ship?”

In practice:
- a release publish workflow should require at least one approver from a “policy/quality” role
  and at least one approver from a “publish authority” role
- breakglass should require an approver *not* the requester (distinct principals)

Where possible, enforce this in policy:
- `trust.policy` / `release.authority.policy` express thresholds and roles
- `consent.request.approvals` lists the required quorum and expected principals/roles

## Avoid approval fatigue (the system must not train bypass)

If approvals are too frequent or too vague, operators will route around them.
DeriveBSD should bias toward:

- **timeboxed grants** rather than permanent exceptions
- **policy edits** as the stable landing spot (so repeated approvals become a reviewed policy change)
- **clear degradation rules** (e.g. “halt if quorum unavailable” vs “allow with audit-only”) that are explicit and receipted
- **high-signal prompts**: always show the key digests and the blast-radius summary

## Where this composes elsewhere in the archive

- Two-person integrity overview: `docs/107-two-person-integrity.md`
- Release authority thresholds and emergency halts: `docs/260-release-authority-policy-and-key-management.md`
- Breakglass lane: `docs/236-breakglass-and-recovery-mode.md`, `spec/breakglass.grant.schema.json`, `spec/breakglass.receipt.schema.json`, `spec/breakglass.event.schema.json`
- Lease envelope (unified metadata for temporary authority): `docs/252-lease-envelope-and-cross-lane-joins.md`

Last updated: 2026-03-06r203
