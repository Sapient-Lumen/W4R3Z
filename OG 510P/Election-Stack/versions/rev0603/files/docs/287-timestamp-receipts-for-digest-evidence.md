# 287 — Timestamp receipts for digest evidence (RFC 3161 + witnesses)

**Track:** Shared

This doc adds a *tight* missing bridge for `281–286`: a standard way to attach **time** to a digest **without** publishing raw artifacts.

It composes with:

- **Digest surfaces**: AuLD (`279`), ICLD (`280`), HoldCapsule (`278`), Disclosure Packet (`282`)
- **Anchoring**: transparency logs (`284`)
- **Identity binding**: Signed Digest Statements (SDS) (`285`)
- **Key lifecycle**: rotation & compromise handling (`286`)
- **Proof packaging**: canonicalize → hash → sign → timestamp (`265`)

---

## Why timestamp receipts exist (and what they do *not* do)

A timestamp receipt is evidence that **a specific digest existed no later than a certain time** (subject to the trust model of the timestamp source).

It does **not** prove:

- the *truth* of the underlying content (only existence of the digest),
- that the content was complete or non-selectively collected (pair with `283` scope + `281` deployment rules),
- that the timestamp source is honest (mitigate with multi-source time and/or transparency anchoring).

---

## Threat model notes (bounded)

We assume:

- internal clocks can be wrong, manipulated, or disputed (`38`, `31`);
- adversaries may claim “this digest was created after-the-fact”;
- we must avoid producing new high-risk public data releases (no raw logs, no PII).

Goal: provide a **portable, court-friendly** “time envelope” that travels with digest-first evidence.

---

## The pattern: Timestamp Receipt (TSR)

A **Timestamp Receipt (TSR)** is a small envelope that binds:

1) the **digest** (e.g., sha256 of an AuLD / ICLD JSON),  
2) the **timestamp source** identity/policy,  
3) the **returned receipt token** (or a digest of it),  
4) optional **witness corroboration** and/or **transparency anchoring** pointers.

### Minimal data model (HFV-ish)

Use the canonical template:

- `artifacts/templates/hfv.timestamp_receipt.v1.json`

Key fields:

- `subject.digest` — the digest being timestamped (sha256, hex)
- `method` — `rfc3161` | `transparency_log` | `witness_cosign`
- `issuer` — TSA/log/witness identity (organization + key/cert fingerprint reference)
- `receipt` — receipt token payload (or hash of token, if token is stored sealed)
- `references` — sealed pointers to raw tokens/certs (never inline by default)
- optional `triage` — severity/confidence/PII risk (`283`)

---

## RFC 3161 TSA receipts (recommended baseline)

A RFC 3161 Time-Stamp Authority (TSA) receipt is a common “external time” primitive.

Operational posture:

- Prefer **at least two independent TSAs** (diverse operators/jurisdictions).
- Store the full timestamp token in sealed storage; publish only:
  - the digest of the token,
  - the TSA identity reference,
  - the TSA policy OID (if applicable),
  - the claimed `gen_time` as metadata.

Reference: `rfc3161_txt` (see `docs/214-external-sources-index.md`).

### Anti-footgun rules

- Never timestamp **raw logs**; timestamp only the **digest surface** (AuLD / ICLD / HoldCapsule / Disclosure Packet).
- Treat TSA receipt tokens as evidence objects: hash, seal, retain (`43`, `98`, `278`).
- If the TSA is later disputed, you still have:
  - SDS signatures (`285`),
  - optional transparency anchoring (`284`),
  - witness corroboration (`99`, `132`).

---

## Multi-source time (best practice, still small)

For contested elections, prefer **two-of-three** corroboration:

1) **SDS signature time** (issuer claims a time; strongest when tied to audited key operations) (`285/286`)
2) **RFC 3161** TSA receipt (external time)
3) **Transparency log** anchoring for the digest hash (`284`) *(optional)*

This creates a robust “time lattice” without publishing sensitive content.

---

## Witness corroboration (optional)

Where a witness set exists (`23`, `99`), witnesses can countersign:

- the SDS statement (`285`), and/or
- the TSR envelope itself.

Use this when you need social/legal resilience (“multiple independent observers saw this digest before deadline”).

Do **not** force witnesses to handle raw artifacts; only digests and minimal envelopes.

---

## Disclosure posture

Default public posture is **digest-only**:

- Public: digest, receipt token hash, issuer identity reference, and minimal time metadata.
- Controlled disclosure (`282`): the full RFC 3161 token, TSA certificate chain, and verification artifacts.

Stop conditions: if a receipt would reveal operational topology, staff identities, or anything that enables targeting, keep it sealed and publish only the digest references (`22`, `39`, `225`).

---

## Implementation notes (minimal)

- Canonicalize the digest surface (`265`) → compute digest.
- Emit SDS over the digest (`285`) and record signer key id (`286`).
- Obtain one or more timestamp receipts (RFC 3161).
- (Optional) anchor digest hash to a transparency log and store inclusion proof in controlled storage (`284`).
- Publish the **TSR envelope** alongside the digest surface index entry.

