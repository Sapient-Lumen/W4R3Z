# Coercion resistance: deeper landscape and design implications

**Track:** B (Remote return / hard-mode research)


This document is a more detailed companion to `07-coercion.md`.

## Key premise
Remote voting (unsupervised environments) creates unavoidable opportunities for:
- coercion / forced abstention,
- vote buying (proof-of-vote),
- "over-the-shoulder" monitoring.

End-to-end verifiability (E2E) addresses **integrity verifiability** but does not, by itself, solve coercion.

## Three main families (and what they imply)

### A) Revoting ("last vote counts")
**Mechanism:** Voter can re-vote later; coercer cannot be sure the final vote.

**What it assumes:** There exists a time/place where the coercer is not watching.

**Engineering implications (MUST if adopted):**
- Canonical ordering must be derived from the **public bulletin board** (PBB) total order.
- Proofs and audit artifacts MUST show that only the counted ballot per voter/token affected the tally.
- Receipts must be non-revealing and must not become a "proof-of-vote".

**Reference:** VoteAgain (USENIX Security 2020).

### B) Fake-credential / JCJ-style systems
**Mechanism:** Voters can provide a coercer with a plausible fake credential; only genuine credentials count.

**Reality check:** Modern analyses show subtleties and leakages around the cleansing/tally phases.
A recent CSF 2024 paper analyzes coercion-resistance limits and discusses how "cleansing leakage" and other effects can degrade guarantees.

**Engineering implications (if you attempt this):**
- You likely need **noise/dummy ballots** beyond honest-voter dummies; authorities may need to add unpredictable dummies.
- You must explicitly analyze (and ideally prove) what a coercer can infer from:
  - counts of invalidated ballots,
  - timing/order information,
  - partial tally outputs.

### C) Tracking-number / Selene-style mitigation
**Mechanism:** Voters receive a private tracker to find their vote in the published outcome; the voter can present a fake tracker to a coercer.

**Engineering implications:**
- Trackers must not create linkability that enables identity inference.
- Tracker-based disclosure interacts dangerously with complex ballots (pattern attacks); see `34-tally-hiding-and-pattern-attacks.md`.

## Pattern coercion ("Italian attacks") and the need for tally-hiding
Some coercion attacks do not rely on cryptographic receipts at all; they exploit high-dimensional ballots where voters can embed identifying patterns in low-stakes contests.

Mitigation typically requires **tally hiding**: avoid publishing full decrypted ballots; decrypt only what is necessary (often only totals or winners), while preserving verifiability.

See `34-tally-hiding-and-pattern-attacks.md`.

## Design stance (RECOMMENDED)
If you intend to deploy anything beyond constrained pilots:
- Prefer **paper ballot of record + RLAs** as the primary recovery anchor.
- If remote return is allowed at all, use **revoting + supervised override** plus explicit non-claims.
- Treat fake-credential systems as research-heavy unless you have a credible path to correctness, usability, and certification.

## Required honesty in claims
All public materials MUST clearly differentiate:
- what is guaranteed by cryptographic verification,
- what depends on voter environment assumptions,
- what is mitigated only by policy (e.g., override voting).