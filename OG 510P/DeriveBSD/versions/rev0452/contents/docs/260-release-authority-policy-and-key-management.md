# Release authority policy and key management

DeriveBSD already has:
- `trust.policy` (what a client trusts)
- `release.capsule` (what a release *is*)
- optional transparency evidence (`release.transparency.entry`, `log.checkpoint.receipt`, and monitor snapshots summarized via `transparency_verification`)
- optional workflow-verification evidence (`supplychain-verify-receipt` summarized via `supplychain_verification`)
- optional vulnerability-verification evidence (`vuln-gate-receipt` summarized via `vulnerability_verification`)

What this lane adds is a **first-class object that defines who is allowed to publish releases, under what thresholds, with what emergency controls, and with what supplemental evidence rules**.

This document introduces `release.authority.policy` and binds publication to explicit receipts.

## Lessons to steal (TUF-shaped)

TUF’s core operational lesson is role separation + thresholds:
- the **root** role defines which keys are trusted for which roles
- signature thresholds can require multiple signatures
- recovery from compromise requires explicit trust updates, not quiet key replacement

DeriveBSD should not require full TUF everywhere, but it should bake in the same ergonomics.

## DeriveBSD object model

Transparency is supplemental publication evidence only. `release.transparency.entry`, `log.checkpoint.receipt`, and `transparency.monitor.snapshot` may be required by policy, but they do not replace threshold signatures on `release.publish.receipt`.

### `release.authority.policy`

Defines:
- release scope (namespace/channel patterns)
- signing roles and thresholds for:
  - publish
  - halt
  - resume
  - key rotation
- required evidence attachments:
  - transparency entry required/optional
  - pinned `witness_policy_digest` (optional)
  - optional `identity_evidence` rules (ignored / optional / required; allowed issuers / methods; bundle-first requirements)
  - optional `supplychain_verification` rules (ignored / optional / required; allowed layout-policy digests; freshness requirements)
  - optional `vulnerability_verification` rules (ignored / optional / required; allowed `vuln.gate.policy` digests; freshness requirements)
- emergency controls:
  - kill switch for a channel (policy-bound)
  - “publish allowed only if monitors are clean” (optional)

The crucial rule is that `identity_evidence` is **supplemental**.
It may constrain publication review, but it does not replace role thresholds or publish signatures.

The same rule applies to `supplychain_verification`: a passing workflow-verification receipt can be required by policy, but it does not become publication authority.

The same rule also applies to `vulnerability_verification`: a passing `vuln-gate-receipt` can be required by policy, but scanner outputs, SBOMs, VEX statements, and gate receipts still do not become publication authority.

The same rule also applies to witness trust: `witness.policy` can be required by policy, but it does not become publication authority either.
It only defines which witnessed checkpoints count for the transparency lane.

### `release.publish.receipt`

A typed receipt emitted by the publisher that binds:
- `release_capsule_digest`
- `authority_policy_digest`
- optional `rollout_policy_digest`
- optional `transparency_verification` summary (`release.transparency.entry`, `log.checkpoint.receipt`, `transparency.monitor.snapshot`, `witness_policy_digest`)
- optional `identity_evidence` decision summary
- optional `supplychain_verification` decision summary (`supplychain-verify-receipt`)
- optional `vulnerability_verification` decision summary (`vuln-gate-receipt`, `vuln.query.receipt`, `vuln.gate.policy`)

Clients (or fleet controllers) can require a publish receipt in addition to capsule signatures.

The `identity_evidence` summary exists so one receipt can answer:
- was publisher identity evidence required?
- was it accepted, rejected, or unused?
- which `publisher.identity.receipt` digests were consulted?

The `vulnerability_verification` summary exists so one receipt can answer:

- was vulnerability verification required?
- which `vuln.gate.policy` and query/snapshot inputs were accepted?
- did publication proceed cleanly, with a warning, or not at all because of vulnerability posture?

The `transparency_verification` summary exists so one receipt can answer:
- whether transparency was required,
- which `witness.policy` digest governed the checkpoint quorum,
- whether the checkpoint `quorum_verdict` was satisfied,
- and which evidence digests were consulted.

Profile default boundary: A and D should treat publish/halt/key-rotation as digest-bound, role-separated high-risk approvals by default, with D preserving offline/OOB-capable ceremonies; B and C may still use these objects for chosen channels, but they must not turn ordinary local user update flows into mandatory reviewer theater (see `docs/474-high-risk-approval-posture-by-profile.md`).

### `release.halt.event`

A typed event used for emergency halts that can be:
- referenced by rollout halt conditions
- attached to incident bundles
- audited as a signed decision

## Why this is groundfloor-worthy

- Prevents release authority from turning into undocumented CI scripts.
- Makes emergency actions (halt/resume) mechanically explainable.
- Keeps identity evidence useful without letting it silently become authority.
- Keeps witness trust explicit without letting backend witness lists silently become authority.
- Makes multi-party publishing a first-class capability instead of a social process.

## Relationship to existing lanes

- `release.capsule` gains optional bindings:
  - `release_authority_policy_digest`
  - `release_publish_receipt_digest`

- Rollout decisions (`rollout.policy` / `rollout.receipt`) can pin a required authority-policy digest.

- Transparency monitors validate that logged publication events match the authority policy, but their outputs remain evidence/gating inputs rather than publication authority.

- `witness.policy` may be pinned by release policy and monitor policy, but it remains a reviewed witness-trust input rather than publication authority.

- Publisher identity evidence (`publisher.identity.receipt`) may be attached or required, but it remains supplemental and bundle-first for `sigstore-keyless`.

- Workflow-verification receipts (`supplychain-verify-receipt`) may likewise be attached or required, but they remain supplemental verifier outputs rather than publication authority.

## Related docs

- `docs/61-channel-metadata-tuf-inspired.md`
- `docs/203-full-tuf-metadata-adapter.md`
- `docs/257-release-capsules-and-transparency.md`
- `docs/259-transparency-monitors-and-witness-gossip.md`
- `docs/290-keyless-signing-and-publisher-identity-receipts.md`
- `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md`
- `docs/490-witness-policy-and-roster-quorum-boundary.md`

Last updated: 2026-03-07r220
See also: `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`.
