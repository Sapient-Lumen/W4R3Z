# External verification protocol for digest-first evidence (bounded)

**Track:** Shared

This is a *thin bridge* for third parties (auditors, courts, media verifiers, watchdogs, cross-jurisdiction peers) to verify
**digest-first** evidence surfaces **without** requiring raw logs, PII, or operationally sensitive detail.

This protocol composes with:
- `281` (kit), `282` (controlled disclosure), `283` (triage tags), `284` (transparency anchoring),
  `285` (Signed Digest Statements / SDS), `287` (timestamp receipts), `288` (integrity drills).

## Inputs an external verifier may request (minimal set)

1. **Digest artifacts** (one or more):
   - Audit Log Digest (AuLD) (`279`) and/or Incident Command Log Digest (ICLD) (`280`)
2. **Signed Digest Statement (SDS)** (`285`) binding:
   - `digest` → `issuer` → `policy/authority reference` → `scope window`
3. **Time evidence** (pick one):
   - Timestamp Receipt (TSR) (`287`, e.g., RFC 3161), or
   - Transparency-log inclusion proof (`284`), or
   - Witness corroboration (multiple signers / cross-posted commitments)
4. *(Optional)* **Disclosure Packet** (`282`) only when excerpts must be shared.

## 15-minute verification flow (digest-first)

Use `artifacts/checklists/external-verifier-15-minute-check.md`.

If any check fails, the correct outcome is:
- **“Cannot verify”** (not “fraud”), plus a concrete list of missing items (SDS / time proof / scope mismatch).

## What this protocol deliberately does *not* require

- Raw system logs or full incident channels
- Voter PII, ballot images, CVRs, or precinct mappings
- Secrets (credentials, network topology, internal hostnames)
- “Trust us” screenshots (unless bound to digests and then treated as *untrusted* evidence)

## Minimal outputs a verifier may publish (safe)

- The **digest(s)** being verified
- The **SDS** (or its hash) and signer identity
- The **time proof** reference (TSR hash / log entry + inclusion proof)
- The **scope window** and declared system boundary (as asserted)
- A statement of **which checks were performed** + any failures

## Escalation (when more is needed)

If verification requires details that might expose PII or sensitive operations:
1. Request a **Disclosure Packet** (`282`) for *only* the needed excerpt(s),
2. Ensure it maps back to the digest(s) and SDS,
3. Require a redaction log and authority basis (why disclosure is lawful and non-harmful).
