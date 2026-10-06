# Cache witness quorums (Trustix-style reproducibility tracking)

DeriveBSD’s baseline position is **untrusted mirrors, trusted verification**.
That already blocks most cache attacks, but there is still a pragmatic gap:

- public ecosystems want *fast substitution* from many caches
- high-assurance consumers want *confidence that the bytes are reproducible*
- maintainers want *early detection of non-reproducibility / compromise*

This document defines an **optional lane** that makes reproducibility a cache-time primitive,
inspired by Trustix’s “input hash → output hash across independent providers” model.

## Core idea

Treat “I built X from inputs Y and got output Z” as a **signed, publishable statement**.
Then define a *quorum acceptance rule*:

> An artifact may be accepted from a cache when **N independent witnesses** attest the same output for the same inputs.

This is not a substitute for verification; it’s a **second signal** that makes cache ecosystems safer and more diagnosable.

## What is the input?

For DeriveBSD, the “input hash” is not a loose bag of files.
It’s a strict tuple that already exists:

- `plan_digest` (the action key)
- `builder_abi` (compiler + OS ABI + sandbox contract)
- `target_kind` (host generation, package, microVM bundle, toolchain bundle)

Optional strengthening fields:

- `closure_proof_digest` (declared closure)
- `toolchain_bundle_digest` (prevents “different compilers” ambiguity)

## Evidence objects

### 1) `cache.witness.statement`

A signed statement by a builder/witness:

- **inputs**: the tuple above
- **output**: `artifact_digest`
- **builder identity**: key ID / provider
- optional: build record digest and/or log inclusion proof

Schema + example:
- `spec/cache.witness.statement.schema.json`
- `spec/examples/cache.witness.statement.json`

### 2) `cache.witness.quorum` (optional aggregator receipt)

Instead of every client fetching N statements, an *aggregator* (often the publish domain) may mint a receipt:

- binds `plan_digest` → `artifact_digest`
- lists witness statement digests that agree
- records `required_witnesses` and `matched_witnesses`
- is signed by an authority selected by trust policy

Schema + example:
- `spec/cache.witness.quorum.schema.json`
- `spec/examples/cache.witness.quorum.json`

## How it plugs into DeriveBSD

### Cache acceptance policy (optional)

Add trust policy knobs (conceptual):

- `cache.requiredWitnesses = 0|N` (0 disables the lane)
- `cache.allowedWitnessGroups = [...]`
- `cache.maxWitnessAge` (freshness)

The policy decision record (`docs/93-policy-decision-records.md`) can reference:

- a quorum receipt, or
- the set of witness statements directly

### Where it helps

- **detect non-reproducible builds early** (two builders disagree)
- **reduce cache poisoning blast radius** (poison must convince N witnesses)
- **allow softer trust bootstrap** for new public channels (grow trust over time)

### Failure modes

- Some packages will be inherently non-reproducible without stabilizers.
  This lane makes that visible and gives policy a lever.
- Quorum rules can reduce availability if N is too high.
  Start with `N=0` (off), then `N=1` (single witness), then `N=2` for high assurance.

## References

- Trustix docs (model overview): https://nix-community.github.io/trustix/
- Trustix announcement (motivations + approach): https://tweag.io/blog/2020-12-16-trustix-announcement/

Last updated: 2026-02-24
