# Re-arm readiness review page: path, mode, peer, and placeholder reconciliation interface spec

## Purpose

The return contract carries the desired destination.
What the archive still needs before it executes the return is one comparison page answering:

> are we actually ready to re-arm, what structural mismatches remain, and which return route recreates the intended protection with the least semantic distortion?

## Core decision

AnonSync must expose one first-class **Re-arm readiness review** whenever more than one return route could plausibly restore motion or protection.

## Fixed page order

1. **Review header**
2. **Candidate-return lattice**
3. **Structural-mismatch card**
4. **Return-risk comparison**
5. **Requalification plan card**
6. **Approval sentence**

### 1) Review header

Show:

- target control or subject id
- source suspension id
- compared return candidates
- selected return candidate
- rejected cheaper candidates
- rejected more destructive candidates
- current recommendation

### 2) Candidate-return lattice

Each row compares one candidate route.
Required columns:

- candidate route
- motion restored how
- path outcome
- byte/materialization outcome
- permission/topology outcome
- structural reconciliation cost
- proof ceiling after activation

Supported `candidate_route` values:

- `resume-in-place`
- `resume-global-surface`
- `reconnect-original-path`
- `accept-new-default-path`
- `connect-existing-directory`
- `restore-permission-only`
- `recreate-from-scratch`
- `keep-partial-return`

Hard rule:

Candidates may not be sorted by convenience alone; they must be sorted by least-distorting route to the target protected state.

### 3) Structural-mismatch card

This card highlights the easiest false-friend returns.
Required rows:

- same-name but different path risk
- existing-directory merge risk
- placeholder versus full-byte mismatch
- permission restored but future updates still blocked risk
- lane/world mismatch risk
- witness removed versus witness preserved difference

Supported `structural_mismatch_flag` values:

- `looks-resumed-but-new-path`
- `looks-same-but-index-suffixed-directory`
- `looks-restored-but-placeholder-only`
- `looks-reconnected-but-merge-still-pending`
- `looks-permitted-but-peer-rights-not-symmetric`
- `looks-active-but-trust-still-pending`

### 4) Return-risk comparison

Required rows:

- risk of path fork
- risk of silent merge overwrite or timestamp winner
- risk of losing old witness or placeholders
- risk of returning in weaker mode than intended
- risk of overclaim after motion returns
- rollback or abort options

Hard rule:

A candidate that restarts activity quickly but worsens structural divergence must not be hidden.

### 5) Requalification plan card

Required rows:

- first required proof after activation
- reviewer / owner
- whether attestation is mandatory
- whether new baseline must be accepted
- blocked sentence until review closes
- when related case / control / rollout reopens automatically

Supported `requalification_plan_style` values:

- `direct-close-after-resume`
- `resume-then-verify-path`
- `resume-then-verify-merge`
- `resume-then-reattest-control`
- `resume-then-rebaseline`
- `do-not-return-blocked`

### 6) Approval sentence

The page ends with one sentence in this shape:

> `We choose <candidate route> instead of <rejected alternative> because it restores <target effect> with lower structural distortion; after motion returns, <remaining mismatch> still blocks <overclaim> until <requalification step>.`
