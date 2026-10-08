# Crypto primer (one page, court-friendly)

**Track:** Shared (cross-cutting)

> Purpose: explain, in plain language, what the bundle’s cryptographic checks establish — and what they **do not**.
> Keep this to **one page**.

## What this verification establishes

- **Byte identity:** A SHA‑256 digest is a fingerprint of a file. If two digests match, the files are the same bytes.
- **Stable hashing:** Before hashing/signing JSON, the verifier converts it to a canonical form (JCS). This prevents “same meaning, different formatting” from changing the digest.
- **Authenticity of a statement:** A digital signature proves that someone with control of a specific private key signed the canonical bytes.
- **Completeness of a packet:** The bundle contains a `manifest.json` listing every object and its digest. The verifier checks that the listed objects match their digests.
- **Change history (if present):** Some feeds use hash‑chaining / supersession pointers so later statements can correct earlier ones without erasing history.

## What this verification does NOT establish (explicit boundaries)

- It does **not** prove that the signer is honest.
- It does **not** prove that a device was uncompromised.
- It does **not** prove that a paper ballot was marked as intended.
- It does **not** replace audits or recounts; it makes disputes about published evidence **checkable**.

## How an opposing party can reproduce the verification

1) Obtain the bundle (same bytes) and the signer’s public key.
2) Run the verifier identified in the admissibility worksheet (name + version + binary hash).
3) Confirm that:
   - object digests match the bytes,
   - signatures verify for the canonicalized bytes,
   - the verifier output matches the reported result.

## Key question for the tribunal

If verification fails, **which check failed** (digest mismatch, signature mismatch, missing object, invalid structure), and what additional evidence would resolve it?
