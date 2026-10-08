# Bundle gossip and anti–split-view defense

**Track:** A (Deployable core)


## Problem
Attackers often don’t need to change ballots or tallies. They can win by splitting reality:

- different observers receive **different evidence bundles** (or bundles appear/vanish by region), and
- the operator can later claim the “other” version is fake.

This is the same class of attack transparency-log ecosystems call **split-view / equivocation**.

## Goal
Make evidence distribution **self-checking**:

- If a portal/CDN/relay serves different evidence to different audiences, the mismatch becomes **provable and contagious**.

## Core objects
- `EvidenceBundleManifest` (content-addressed inventory of an evidence bundle)
- `Checkpoint` (witness-quorum signed PBB/ATL checkpoint)
- `BundleGossipMessage` (see `schemas/BundleGossipMessage.json`)

## High-level design

### 1) Every bundle is content-addressed
A bundle is identified by a canonical hash of its manifest (and recursively, of its contents).

### 2) Bundle publication is checkpointed
At each reporting interval, the operator publishes:
- bundle manifest hash
- parent checkpoint hash
- witness-quorum signatures

### 3) Gossip spreads “what I saw”
Any participant (witness/monitor/observer) exchanges compact digests:
- latest checkpoint hash they consider FINAL
- a bounded set of recent bundle manifest hashes
- optional divergence hints

### 4) Divergence is evidence
If two parties present incompatible views:
- store both signed views
- produce a `ForkProof` or a `BundleDivergence` record (implementation choice)
- anchor the divergence record into the PBB/ATL as soon as possible

## Normative requirements
- **MUST** publish bundles as content-addressed manifests.
- **MUST** bind each manifest to a witness-quorum checkpoint.
- **MUST** support gossip exchange between independent monitors.
- **MUST** define a Maximum Publication Delay (MPD) for bundles; missing MPD is itself evidence.
- **MUST NOT** allow unsigned “hotfix” bundles outside the manifest/checkpoint chain.

## Threats addressed
- CDN split delivery
- regional censorship of “bad news” artifacts
- operator post-hoc rewrite of what was “official”

## Non-goals
- Preventing all censorship (instead: make censorship detectable and litigable).

## Implementation notes
- Start with simple push/pull gossip over HTTPS between monitors.
- Add opportunistic piggybacking transports later (see `101-*`).