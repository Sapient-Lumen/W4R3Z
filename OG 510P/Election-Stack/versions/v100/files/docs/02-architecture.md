# Architecture (paranoia revision)

**Track:** A (Deployable core)


## Core principle: the “server” is a Public Bulletin Board (PBB), not a tally authority
The networked layer is a **federated transparency system** whose job is to:
1) **accept only well-formed encrypted ballots**, and  
2) **publish cryptographic evidence** (Merkle commitments + proofs + witness gossip) so that
   any attempt to alter, fork, drop, or reorder ballots becomes publicly detectable.

In other words: **assume the servers are compromised** and design so compromise becomes *evident*.

This follows the “append-only transparency log” pattern used in Certificate Transparency (Merkle log + inclusion/consistency proofs).

## Track framing
This architecture is shared across the archive’s three tracks (Deployable Core / Remote Return Annex / North Star). For scope and claims, see `154-project-scope-and-track-map.md`.


## System variants (choose what you are actually building)
You cannot get the same security properties from these three scopes:

A. **In-person voting + paper ballot of record + E2E verification** (most defensible)  
B. **Remote ballot marking + paper return** (network helps accessibility; paper remains record)  
C. **Remote ballot return** (highest risk: coercion + client malware + disruption)

This spec focuses on the common infrastructure A/B/C can share: **PBB + verification + threshold tally**.

## Roles
- **RA (Registration Authority):** issues credentials; publishes revocations.
- **Eligibility Token Service (optional):** issues unlinkable, spend-once eligibility tokens (privacy upgrade).
- **PBB entrypoints:** accept submissions, validate, and queue for ordering.
- **Sequencer / Log operator(s):** produce canonical append order and Signed Tree Heads (STHs).
- **Witnesses/Monitors:** fetch STHs, verify proofs, gossip, and publish fork evidence.
- **Trustees/Guardians:** hold threshold shares for decrypting tally outputs and signing key-ceremony transcripts.
- **Auditors/Public:** verify public artifacts; run independent verifiers.

## Trust boundaries (explicit)
- **Voter device is untrusted** (assume malware and UI deception).
- Any single PBB node / sequencer can be hostile.
- Some trustees may be corrupt (but below threshold).
- Network can be partitioned; endpoints can be DDoS’d; routing can be manipulated.
- Build systems, update channels, and dependency graphs are first-class attack surfaces.

## Key paranoia upgrades (what changes vs “standard” E2E designs)

### 1) Receipt state machine (fail-safe UX)
A “receipt” is not one thing. Clients MUST distinguish:
- **PENDING:** signed intake receipt only (not yet in the log)
- **RECORDED:** inclusion proof against an STH
- **FINAL:** inclusion proof against a *quorum-witness-cosigned* checkpoint (or BFT-finalized checkpoint)
- **TALLIED:** ballot is proven included in tally (or properly eliminated by revote rule)
- **AUDITED (paper mode):** cryptographic record matches paper audit evidence

UI MUST treat anything less than RECORDED as **NOT RECORDED** and present fallback.

### 2) Admission control that cannot be used for targeted censorship
If eligibility is checked online, the checker can censor voters.
Mitigations:
- make eligibility proofs **unlinkable** (tokens / anonymous creds), and
- require multiple independent entrypoints + public monitoring to detect selective drops.

### 3) Two-phase “acceptance with deadline” (optional anti-censorship evidence)
Entry points MAY issue a short-lived **IntakeReceipt** that commits to:
- `ballot_hash`, `deadline`, and `reason_codes` on failure.
If the ballot is not included by deadline, the voter can publish the IntakeReceipt as censorship evidence.

(Warning: any receipt can be used to prove participation; decide if that matters for your coercion model.)

### 4) Override channel (essential for remote voting risk)
If remote return is allowed, the system SHOULD support a **supervised override** (e.g., in-person vote)
that cancels any prior remote ballot. This is the strongest practical mitigation against coercion and malware.

## High-level data flow
1. **Setup:** trustees run DKG → publish election public key `PK`; publish parameters via multiple channels.
2. **Cast:** client encrypts ballot + ZK proof → submit to any entrypoint.
3. **Record:** log commits entries → return inclusion proof + STH.
4. **Verify:** voter & monitors verify inclusion and consistency; witnesses gossip STHs.
5. **Tally:** mixnet or homomorphic tally + threshold decryption → publish proofs.
6. **Audit:** (recommended) risk-limiting audits against paper ballot of record.
