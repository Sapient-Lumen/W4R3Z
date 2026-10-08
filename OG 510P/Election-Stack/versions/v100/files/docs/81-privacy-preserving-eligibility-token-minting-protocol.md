# 81 — Privacy-preserving eligibility token minting protocol (detailed)

**Track:** B (Remote return / hard-mode research)


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

## Failure modes
- If CSP is down: allow in-person token issuance and/or supervised fallback.
- If ETI is down: voters can still cast paper-of-record ballots; remote casting must fail loudly.

## Security notes
- Tokens are not receipts; they must not enable vote selling.
- ETI signing keys are critical; store in HSM and consider threshold signing.

Schemas: see `schemas/TokenMintRequest.json`, `schemas/TokenMintResponse.json`.