# Trust bootstrap

DeriveBSD’s core pipeline is only meaningful if a fresh node can obtain an initial trust root *without* creating an unbounded “first boot” hole.

This document defines a minimal, practical bootstrap story that preserves the project’s verifiability goals.

## Bootstrap goals

A newly provisioned node must be able to:

1. establish **host identity** (optionally hardware-backed)
2. obtain **policy authority** trust roots (keys/certs) or a delegated trust anchor
3. verify and install its **first acceptable generation**
4. record evidence sufficient to answer: *why did this node trust these roots?*

## Bootstrap modes

### Mode A: offline-root (most conservative)

- Operator has a sealed offline root (policy authority) and an enrollment bundle.
- Enrollment bundle contains:
  - `policy_root.json` (keys, thresholds, expiry)
  - `channel_metadata.json` (pinned channel, initial versions)
  - optional `node_policy.json` (role labels)
  - signatures + inclusion proofs (if a transparency log is used)
- Node verifies bundle offline, seals roots locally, then fetches/installs.

### Mode B: hardware-backed enrollment (TPM optional)

- Node generates a keypair and produces an **attestation** (TPM quote or software attestation).
- Enrollment service verifies the attestation and issues a signed `policy_root.json` scoped to this node/role.
- Node seals received roots.

### Mode C: preinstalled factory anchor

- For appliances: ship with a vendor anchor that can only delegate to organization policy roots, never directly sign artifacts.

## Evidence requirements

The first successful activation MUST produce a `bootstrap.evidence` bundle including:

- bootstrap mode used
- trust root digests + signatures
- optional attestation transcript (quote + verifier result)
- optional `attester.provision.receipt` digest (when hardware-backed enrollment is used)
- selected channel + initial version pin
- operator identity/approval if applicable

See: `docs/314-attester-provisioning-and-key-lifecycle-receipts.md`, `spec/attester.provision.receipt.schema.json`.

## Key-handling principles

- **Delegation over replacement**: rotate roots by delegating to new keys with overlap.
- **Separation**: policy authority keys are distinct from artifact signing keys.
- **Expiration is real**: boot and update paths must consider expiry (see trustworthy time).

## Open questions (explicitly tracked)

- Which bootloader path provides the cleanest place to enforce roots and rollback index?
- TPM optionality: what is the minimum acceptable software-only story?
