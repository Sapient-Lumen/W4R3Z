# 96 — Independent Notarization & Trusted Timestamping

**Track:** A (Deployable core)


## Problem
Even if the PBB is append-only, an adversary can claim:
- “the evidence bundle was created after the fact,” or
- “the official checkpoint was different at the time,”
especially during a contested window.

## Goal
Create **time-of-existence** evidence for:
- EPB hashes,
- checkpoint hashes,
- ResultsReleasePackage hashes,
- ObserverKit bundle hashes,
that is **independent** of the election operator and still verifiable years later.

## Approach (layered)
### A) Trusted timestamp tokens (RFC 3161)
Obtain a Time-Stamp Token (TST) over the SHA-256 hash of each high-value artifact or package.
Store:
- request hash,
- TSA identity,
- TST bytes,
- and verification metadata
inside the evidence bundle.

### B) Cross-log anchoring (transparency logs)
Publish the same hashes into one or more independent public transparency logs (e.g., software artifact transparency logs).
Store inclusion proofs.

### C) Community countersigning
Allow independent organizations to countersign:
- ObserverKit manifests
- ResultsReleasePackages
- checkpoint feeds
so independent parties can attest “this is what we saw at time T”.

## Operational notes
- Timestamping should be automatic and continuous during reporting windows.
- Publish a list of acceptable TSAs/logs *before* voting opens.
- Do not leak voter PII into timestamped materials.