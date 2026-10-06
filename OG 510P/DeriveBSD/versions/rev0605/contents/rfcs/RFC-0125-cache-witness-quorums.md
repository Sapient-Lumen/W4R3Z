# RFC-0125: Cache witness quorums (Trustix-style)

Status: **draft**

## Motivation

DeriveBSD’s cache model is “untrusted mirrors, trusted verification”, which is correct.
But public ecosystems need an additional lever:

- detect non-reproducible builds early
- reduce cache poisoning blast radius without centralizing trust
- enable high-assurance consumers to require corroboration

Trustix demonstrates a useful pattern: track *input hash → output hash* across independent providers.

## Goals

- Define a signed witness statement that binds DeriveBSD’s action key (plan digest) to an output digest.
- Define an optional quorum receipt to make client consumption cheap.
- Allow trust policy to require N independent corroborations for specific channels/targets.

## Non-goals

- Replacing DeriveBSD’s baseline digest/signature verification.
- Solving irreproducible packages automatically.
- Specifying a global witness-discovery network.

## Proposal

### Evidence object: `cache.witness.statement`

Fields (v0):

- inputs:
  - `plan_digest`
  - `target_kind`
  - `builder_abi`
  - optional: `closure_proof_digest`, `toolchain_bundle_digest`
- output:
  - `artifact_digest`
- witness identity:
  - `witness_key_id`, `witness_group` (optional)
- metadata:
  - `issued_at`
  - signature over canonical JSON

### Evidence object: `cache.witness.quorum` (optional)

A signed receipt minted by an authority selected by trust policy (often the publish domain).

- binds the same input tuple to `artifact_digest`
- lists witness statement digests that agree
- records `required_witnesses` and `matched_witnesses`

### Policy integration

Add optional policy requirements:

- `cache.requiredWitnesses` per namespace/channel/target kind
- `cache.allowedWitnessGroups`
- `cache.maxWitnessAge`

The policy decision record MAY require:

- quorum receipt, or
- direct enumeration of witness statements

## References

- Trustix docs: https://nix-community.github.io/trustix/
- Trustix announcement: https://tweag.io/blog/2020-12-16-trustix-announcement/
