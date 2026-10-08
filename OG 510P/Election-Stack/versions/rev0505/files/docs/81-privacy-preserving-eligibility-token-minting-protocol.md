# 81 — Privacy-preserving eligibility token minting protocol (detailed)

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

This document specifies a concrete *privacy-preserving* protocol for turning a citizen credential into **unlinkable eligibility tokens**.

## Requirements
- ETI MUST NOT learn voter identity or stable identifiers.
- CSP MUST NOT learn where/when tokens are spent.
- Tokens MUST be **one-time spend** and bound to a specific election.
- Minting MUST resist phishing and replay.
- Rate limiting MUST be possible without IP-based discrimination.

## Actors
- **Voter** with authenticator(s)
- **CSP** (credential portal)
- **ETI** (eligibility token issuer)
- **PBB** (public bulletin board / ballot log)

## Protocol overview
### Step 0 — Election context
Election publishes `ElectionParameterBundle` (EPB) with:
- `election_id`, `crypto_policy`, `eligibility_epoch_id`
- ETI public keys and token format version

### Step 1 — Authenticate to CSP
- Voter authenticates using WebAuthn (origin-bound, phishing-resistant) and obtains a short-lived **MintGrant**.
- MintGrant MUST:
  - expire quickly (minutes)
  - be bound to `election_id` and `eligibility_epoch_id`
  - contain no stable user identifier visible to ETI

### Step 2 — Blind token request (unlinkability)
- Voter generates random token seeds `t1..tk` and blinds them to `b1..bk`.
- Voter sends `TokenMintRequest{MintGrant, b1..bk}` to ETI.
- ETI verifies MintGrant (via CSP public key / federation) and signs the blinded values, returning `s1..sk`.
- Voter unblinds to obtain tokens `Tok1..Tokk`.

### Step 3 — Spending a token
- When casting, voter includes a token in ballot submission.
- PBB checks token validity (signature) and unspent status.

### Step 4 — Prevent double-minting and abuse
Options (choose one or layer):
- **Anonymous rate limiting tokens** (e.g., Privacy Pass style) to limit minting bursts.
- MintGrant contains a per-election “allowance” enforced by CSP, but MintGrant is unlinkable to voter at ETI.

## Privacy and metadata
- Minting SHOULD be performed over OHTTP or similar privacy partitioning.
- Token spending SHOULD use fixed-size envelopes where feasible.


## Privacy vs verifiability boundary (turnout surveillance risk)

Unlinkable minting does not automatically prevent **turnout surveillance**. Public spend logs, revocation epochs,
or fine‑grained publication (timing/geography/small batches) can leak who voted or when.

Track B does **not** claim to solve this (see `docs/167` and `docs/172.3.1`).
Experiment posture:

- define a **metadata budget** and batching rules for any public transparency surface,
- avoid publishing per‑person timing/geography that can be joined to identities,
- prefer private `VoterStatusProof` lanes for individual dispute resolution,
- treat deanonymization signals as incident triggers (hazard **HZ‑026**).
- run `CHECK:artifacts/checklists/turnout-oracle-risk-quickcheck.md` and log a bounded row in `artifacts/registries/turnout-oracle-risk-assessments.csv` when changing public transparency surfaces.

## Failure modes
- If CSP is down: allow in-person token issuance and/or supervised fallback.
- If ETI is down: voters can still cast paper-of-record ballots; remote casting must fail loudly.

## Security notes
- Tokens are not receipts; they must not enable vote selling.
- ETI signing keys are critical; store in HSM and consider threshold signing.

Schemas: see `schemas/TokenMintRequest.json`, `schemas/TokenMintResponse.json`.