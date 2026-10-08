# 286. Key management and rotation for digest evidence

**Track:** Shared / Evidence surfaces  
**Status:** Draft (tight)

This note hardens `docs/285` (Signed Digest Statement, SDS) and `docs/284` (transparency anchoring) by specifying a **minimal, auditable key lifecycle** for signing digest-first evidence surfaces (AuLD, ICLD, HoldCapsule summaries, Disclosure Packets).

## Goals

- Preserve the **verifiability** of signed digests over time (including after key rotation).
- Keep signing keys **separable** from the systems that generate raw logs.
- Provide a **compromise playbook** that does not require disclosure of raw evidence.

## Minimal key roles

Use a small “ladder” of roles; do not over-engineer.

1. **Root / policy key (offline, rarely used)**  
   - Signs the public policy statements that define what constitutes a valid SDS for this program (schemas + required fields + allowed key roles).
2. **Operational signing key (online, rotated)**  
   - Signs SDS objects (digest bindings). Prefer hardware-backed storage (HSM, TPM, secure enclave) when available.
3. **Timestamp / receipt key (optional)**  
   - If you use receipts (transparency log inclusion proofs, notarization), treat those as *separate* trust paths; do not multiplex them with the operational signing key.

## Rotation and continuity

Rotation should keep old SDS verifiable without “trusting the old key forever”.

- Each new operational signing key publishes a **rotation statement** (can be an SDS whose `payload_type = "key_rotation"`), signed by:
  - the **old operational key**, and/or
  - the **root/policy key** (preferred when the old key is suspected compromised).
- Maintain a **key registry**: key id → validity window → role → revocation status.
- SDS objects SHOULD include:
  - `signer.key_id`
  - `signer.role`
  - `signer.valid_from` / `signer.valid_to` (or a reference to registry entry)
  - `verification_hint` (how auditors obtain the public key material)

## Compromise response (digest-first)

If an operational signing key is suspected compromised:

1. **Freeze** issuance of new SDS with that key (do not delete old SDS).
2. Publish a **revocation statement** signed by the root/policy key.
3. Switch to a new operational key and publish a **rotation statement**.
4. For affected time windows, require **receipt reinforcement** (e.g., transparency-log inclusion proofs) for SDS credibility.
5. If disputes arise, escalate via `docs/282` (Controlled Disclosure Packet): disclose only what is necessary to validate the disputed digests.

This pattern aligns with general key-management guidance and avoids re-issuing raw logs. (xref: nist_sp800_57_pt1_r5_pdf)

## Separation guidance

- Do not let the system that **writes raw logs** hold the private key that **signs SDS** for those logs.
- Prefer a *signing service* with:
  - narrow API (sign only allowed payload types),
  - rate limits,
  - mandatory audit logs (and those audit logs can themselves produce AuLD/ICLD digests).

## Implementation notes

- Use stable key identifiers (e.g., hash of public key) to avoid ambiguity.
- Keep signatures and receipts **outside** raw evidence bundles by default; only include them via controlled disclosure.
- When using transparency logs, ensure you log **digests**, not raw artifacts. (xref: rfc6962_html; xref: sigstore_rekor_overview; xref: ietf_scitt_about)

## Minimal checklist

- [ ] Root/policy key stored offline; audited access procedure.
- [ ] Operational signing key rotated on a fixed cadence or on personnel change.
- [ ] Key registry published (or available under disclosure rules).
- [ ] Rotation + revocation statements are themselves tamper-evident (logged/anchored).
- [ ] Compromise playbook documented and exercised.
