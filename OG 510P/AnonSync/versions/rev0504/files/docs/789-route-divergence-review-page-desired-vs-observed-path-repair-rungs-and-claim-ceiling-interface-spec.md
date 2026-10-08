# Route divergence review page — desired vs observed path, repair rungs, and claim ceiling interface spec

## Purpose

The archive already had recovery ladders and representativeness review.
What it still lacked was one fixed page for another ordinary question:

> if the observed route differs from the intended route, what exactly is the mismatch, how expensive is each repair rung, and what claim ceiling remains until the mismatch is resolved?

AnonSync should therefore expose a first-class **route divergence review page** whenever route posture and route evidence disagree or remain weakly matched.

## Core decision

Route mismatch must never collapse into a vague tip such as `check firewall` or `try predefined hosts`.
The page exists to turn desired-vs-observed divergence into a typed mismatch with an ordered repair ladder and a visible claim ceiling.

## Fixed review order

1. **Compared objects**
2. **Mismatch class**
3. **Cheapest honest repair rung**
4. **Rollback / semantic cost**
5. **Post-repair proof requirement**

## 1) Compared objects

Show the exact route-posture version and route-evidence version being compared.
Without those identities, the divergence verdict is not durable.

## 2) Mismatch class

The page must output one or more typed mismatch classes, for example:

- helper unavailable
- helper misconfigured
- direct expected but relay observed
- route unresolved because witness window too thin
- posture asymmetric across peers
- direct restored but provenance window still insufficient

Also show whether the mismatch is:

- `performance-relevant`
- `policy-relevant`
- `privacy-relevant`
- `availability-relevant`

## 3) Cheapest honest repair rung

Offer the repair ladder in least-widening order, for example:

1. widen the witness window only
2. verify listening-port reachability
3. verify tracker reachability / sync.conf reachability
4. verify predefined-host symmetry
5. verify LAN multicast conditions
6. allow relay temporarily
7. accept fail-closed posture

The ladder must never imply that enabling more helpers is always the best next move.

## 4) Rollback / semantic cost

Each rung must publish its cost, such as:

- temporary route widening
- privacy or policy downgrade
- topology change risk
- need to touch all peers
- may improve availability while weakening route guarantees

## 5) Post-repair proof requirement

For every repair rung, state what proof is still required before the claim can change, for example:

- stable direct witness for N-minute window
- no relay witness across tested cohort
- matching posture on all required peers
- route evidence fresh enough for current incident

## Compact rendering obligations

Any compact mismatch summary must still preserve:

- mismatch class
- cheapest repair rung
- cost class
- strongest safe current sentence
- proof needed to upgrade the sentence

## Anti-clone rule

Do not clone workflows where route mismatch advice is emitted from folklore without a typed mismatch, visible cost, and explicit proof requirement.
