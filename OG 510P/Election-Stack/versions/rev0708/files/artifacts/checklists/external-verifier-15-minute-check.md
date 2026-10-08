# External verifier 15-minute check (digest-first)

Goal: verify **integrity + time + scope** of a claim using *digest-first* artifacts.

Inputs (minimal):
- One or more digests (AuLD / ICLD / HoldCapsule summary) and an SDS.
- One time proof: TSR (RFC 3161) **or** transparency-log inclusion proof **or** independent witness corroboration.

## 1) Scope + boundary (2 minutes)
- Confirm the scope window (time range / subsystem / jurisdiction boundary) is explicitly stated.
- Confirm the claim is inside the archive’s “allowed claims” (`docs/166-*`) and not prohibited by `docs/167-*`.

## 2) Digest integrity (3 minutes)
- Recompute hashes over the disclosed digest payload(s) (no raw logs required).
- Ensure the digest format matches the referenced HFV template version.

## 3) Signature binding (3 minutes)
- Verify the **SDS** signature against the declared key (and key registry / rotation notice if applicable).
- Confirm SDS binds:
  - digest hash → signer identity → authority/policy reference → scope window.

## 4) Time evidence (4 minutes)
Choose one:
- **TSR:** verify TSA signature + that it timestamps the digest (or SDS) hash.
- **Transparency log:** verify inclusion proof (Merkle path) and that the entry commits to the digest (or SDS) hash.
- **Witness corroboration:** verify at least two independent signers or channels committed the same hash before the relevant deadline.

## 5) Triage sanity (2 minutes)
If present, read the optional `triage` block:
- `severity`, `confidence`, `pii_risk` must be plausible given the claim.
- If `pii_risk` is non-low, demand controlled disclosure discipline (`docs/282`) for any excerpts.

## 6) Output (1 minute)
Publish:
- Verified digest hash(es)
- SDS hash (or full SDS if safe)
- Time proof reference (TSR hash / log entry ID + proof hash)
- A short pass/fail statement + what was missing
