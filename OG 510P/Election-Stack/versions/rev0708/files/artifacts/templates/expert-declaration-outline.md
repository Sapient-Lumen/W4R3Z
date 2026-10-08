# Expert declaration outline (crypto + verifier provenance)

**Track:** Shared (cross-cutting)

> This is a **structure** (not legal advice). Use only where a venue requires expert testimony.
> Keep it bounded: authenticate the tool + explain the checks performed.

## 1) Declarant
- Name:
- Qualifications (1–3 bullets):
- Relationship to parties (disclose conflicts):

## 2) Materials reviewed
- Bundle name + digest:
- Manifest signature key id + public key source:
- Verifier name + version:
- Verifier binary hash:
- Relevant schemas / profiles (digests):

## 3) Method
- How the bundle was obtained and preserved:
- Steps performed to verify:
  - canonicalization method (JCS) used for JSON objects,
  - digest checks (SHA‑256),
  - signature verification steps,
  - any log/chain checks (if applicable).

## 4) Results (bounded)
- What checks passed / failed:
- If failures: what failure mode (digest mismatch, signature mismatch, missing object, structural invalidity):

## 5) Limitations (explicit)
- What these cryptographic checks do **not** establish (signer honesty, device integrity, etc.).

## 6) Declaration
- Statement that the above is true to the best of declarant’s knowledge.
- Signature block.
