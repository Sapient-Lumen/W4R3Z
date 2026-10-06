# Release capsules + transparency (ship a single verifiable handle)

DeriveBSD already produces many verifiable artifacts around “a release”:
closures, SBOMs, provenance/attestations, trust-policy decisions, bootchain policies, etc.

In most OS ecosystems these pieces exist, but **there is no single object** that answers:

> “What *exactly* did we ship, under which policies, and where is the durable evidence?”

Greenfield advantage: introduce a **release capsule** early, so everything downstream can
reference one stable digest.

## Goals

- Provide a **single content-addressed handle** for “this release”, bindable into channels.
- Make releases **portable** (offline / airgap) without losing verification metadata.
- Make releases optionally **transparent** via append-only logs + witness cosigning.
- Keep it minimal: a capsule is **references to digests**, not a new packaging format.

## Prior art to steal

- TUF’s separation of *what is current* (timestamp/snapshot/targets) from client policy decisions.
- Rekor-style transparency (append-only log + inclusion proofs) for publication evidence.
- Witness networks for split-view defense (clients can require witness cosigns).
- SCITT framing: signed statements made transparent with receipts.

See references in `docs/32-curated-references.md`.

## New artifact: `release.capsule`

A `release.capsule` is a small, canonicalized JSON object whose digest becomes the
stable identifier for a release.

It binds the core “what we meant” digests:

- `closure_digest` (+ optional `closure_manifest_digest`)
- `trust_policy_digest` and/or `policy_decision_digest` (what rules were used)
- optional `release_authority_policy_digest` + `release_publish_receipt_digest` (who is allowed to publish, and evidence that they did)
- `supplychain_verify_receipt_digest` / attestation references (what evidence we have)
- SBOM digests (inventory)
- optional `rollout_policy_digest` (how/when it is offered)
- optional `transparency_entry_digest` (proof it was published to a log)

Schema: `spec/release.capsule.schema.json`.
Example: `spec/examples/release.capsule.json`.

### Why a capsule instead of “just use TUF targets metadata”

TUF targets metadata is excellent for distribution and delegations, but it’s not the
right place for *everything DeriveBSD cares about*:

- Derive wants **policy + evidence receipts** first-class, not implicit.
- A capsule is **channel-agnostic**: it can be carried offline, included in incident bundles,
  or bridged through multiple repository adapters.
- A capsule’s digest can be pinned into ZFS-native “deployments are commits” flows.

## New artifact: `release.transparency.entry` (optional)

Just like `export.transparency.entry` logs *sharing events*, `release.transparency.entry`
logs **publication events** ("this release capsule was published").

- It includes the capsule digest and the governing `release.authority.policy` digest (`authority_policy_digest`).
- It may also point at a `log.checkpoint.receipt` digest for offline checkpoint / witness verification.
- It attaches a common log-proof shape: `spec/transparency.proof.schema.json`.

Schema: `spec/release.transparency.entry.schema.json`.
Example: `spec/examples/release.transparency.entry.json`.

### Why transparency for releases

Without transparency, a compromised publisher can:

- selectively show different clients different “latest” releases (split-view)
- publish a malicious release briefly and later deny it

With transparency + witnesses:

- the publisher must commit to an append-only history
- monitors can detect suspicious releases
- clients can require witnessed checkpoints before accepting “current”
- those checkpoints can now be evaluated against an explicit `witness.policy`

See also: `docs/187-witnessed-transparency-checkpoints.md`, `docs/490-witness-policy-and-roster-quorum-boundary.md`.

## Release authority (who may publish)

Transparency proves *that something was published*, not whether it was published by the right people.
DeriveBSD makes publication authority explicit via `release.authority.policy` and a `release.publish.receipt`. The transparency lane is evidence only: `release.transparency.entry`, `log.checkpoint.receipt`, and `transparency.monitor.snapshot` can gate completeness, but they do not replace threshold publish authority.

See: `docs/260-release-authority-policy-and-key-management.md`, `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`, RFC-0192.

## Monitoring (who is watching)

A log without monitors is an unattended camera.
Monitors validate checkpoints/consistency and flag unexpected publications as typed alert events that can halt rollouts.

See: `docs/259-transparency-monitors-and-witness-gossip.md`, RFC-0191.

## Integration sketch

1) Build/verify a candidate release:
   - `closure.manifest` / `closure.proof`
   - SBOM + attestations
   - `trust.policy` evaluation → policy decision record

2) Produce `release.capsule` (canonicalize + hash per `docs/80-canonical-json-hashing-jcs.md`).

3) Publish the capsule under `release.authority.policy` (emit `release.publish.receipt`).

4) Optional: publish a `release.transparency.entry` into a log (bundle proofs; witness cosigns) and, when policy requires it, record a `log.checkpoint.receipt` bound to a pinned `witness.policy` for offline checkpoint verification.

5) Channel metadata points to the capsule digest (not directly to dozens of digests).

6) Host applies capsule → change set → confirmable apply / boot assessment.

## Design constraints

- Capsules must remain **small** and must not embed raw secrets.
- Any optional metadata must be policy-bounded (hashes or redacted forms).
- Capsules should be signable by project keys (threshold signing where needed).

See: `rfcs/RFC-0189-release-capsules-and-transparency.md`.

Last updated: 2026-03-07r219

Publication gating should be summarized only in `transparency_verification` on the publish receipt.
