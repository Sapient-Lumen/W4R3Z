# Remedy-hardening-attestation-integrity proof page — seal basis, custody lineage, and verifier floor

## Purpose

This page is the proof bundle behind the claim that a case which already achieved independent verifier readiness may let a later verifier rely on the same exported bundle as tamper-evident and custody-preserved.
It exists so later readers can inspect sealing, custody, mutable-surface exposure, and integrity blockers directly rather than inferring them from ordinary operational traces.

## Proof bundle

The proof page must preserve evidence for:

- source remedy-hardening-attestation result
- triggering cause family
- current hardening class
- attestation bundle identifier
- seal identifier
- seal activation time
- seal algorithm or integrity basis
- custody-chain evidence
- export-medium evidence
- mutable-storage exposure evidence
- log-rotation exposure evidence
- config-edit exposure evidence
- service-world fork evidence
- unsupported-clone exposure evidence
- named integrity audience
- required verifier cohort
- highest honest current tamper-evident sentence
- strongest blocked stronger integrity sentence

## Proof sentence families

The page must support concise summaries such as:

- `the case is verifier-ready, but not yet tamper-evident`
- `seal integrity is honest only for named lanes or named custody hops`
- `the evidence exists, but mutable-surface exposure still blocks the stronger sentence`
- `handoff is documented, but custody remains too weak for required-cohort integrity`
- `the hardened baseline is now tamper-evident and verifier-ready for the required cohort`

## Stronger-sentence blockers

The page must explicitly name blockers such as:

- no seal basis
- weak or incomplete seal basis
- missing custody hop
- mutable storage remained open
- log rotation or discard risk unresolved
- config-edit exposure unresolved
- service-world fork unresolved
- unsupported clone-like handling unresolved
- named-lane coverage only
- required-cohort integrity floor unmet

## Evidence handling rules

The proof page must never let these substitute for stronger proof:

- one copied storage folder without seal evidence
- one collected log pack without custody lineage
- one config snapshot without immutable integrity basis
- one handoff note without seal-preserved receipt
- one calm verifier review without explicit integrity floor
