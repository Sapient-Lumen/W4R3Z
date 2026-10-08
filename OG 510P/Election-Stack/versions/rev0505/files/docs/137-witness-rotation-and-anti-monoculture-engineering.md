# Witness rotation and anti-monoculture engineering

**Track:** A (Deployable core)


This document specifies engineering tactics that make witness capture and monoculture harder **even if governance fails**.

## Core idea

A witness policy is only as good as its enforcement. The system must make it technically difficult to accept checkpoints that are cosigned by a captured, homogeneous set.

## Engineering requirements

### ROT-1 Policy DAGs and operator grouping
Witness policy SHOULD be expressed in a structured way that can represent:

* k-of-n overall thresholds
* per-operator groups (e.g., "any 1 of 3 instances run by operator X")
* category constraints

### ROT-2 Split-view resistance with incomplete cosignatures
If policy allows flexible selection (e.g., 3-of-10 operators), monitors MUST be able to reconstruct enough cosignatures across time to detect split views caused by different subsets signing different forks.

### ROT-3 Mandatory periodic full-coverage windows
At defined intervals (e.g., daily during election week), the system MUST publish a **Full Coverage Window**: cosignatures from a supermajority of operators (e.g., 8-of-10), so monitors can re-stitch the signing graph.

### ROT-4 Multi-stack deployment diversity
Witnesses SHOULD NOT share common failure domains:

* cloud provider, region, CDN, DNS host
* operating system / runtime stack
* managed service provider

The `StakeholderDiversityReport` MUST include these dimensions.

## Outputs

* Witness policy + verifier test vectors
* Full coverage window proofs
* Rotation schedule and executed rotation events