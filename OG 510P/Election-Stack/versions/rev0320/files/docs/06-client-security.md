# Client security (assume malware)

**Track:** A (Deployable core)

> **Read-first:** before treating anything here as deployment guidance, read `166-scope-and-claims-contract.md` and `167-non-claims-and-boundaries.md` (they are binding on interpretation).



## Why this is the core problem
If the voter’s device is compromised, an attacker can:
- change what the voter sees/chooses,
- change what gets encrypted and sent,
- lie about whether the ballot was recorded,
- exfiltrate secrets / credentials,
- target specific demographics at scale.

Public analyses of web-based voting workflows (e.g., Democracy Live/OmniBallot) emphasize this risk surface.  
See: xref: mit_omniballot_analysis_2020_pdf

---

## Defensive posture: layers, not one trick
**No single mitigation is sufficient.** Combine multiple layers and keep a safe fallback.

### Layer 0 (non-negotiable): safe fallback
- If remote casting exists, the election MUST support a **paper ballot of record** path (mail/in-person) and/or a supervised override vote.
- The UI MUST always allow a voter to abandon remote and complete via safe fallback without penalty.

### Layer 1: Cast-or-spoil challenges (Benaloh-style)
Mechanism: voter can “challenge” a constructed ballot to force the device to reveal encryption randomness so anyone can verify it encrypts the displayed selections.
- Pros: statistical detection of cheating clients
- Cons: UX complexity; requires real voter participation; attackers can still target those who don’t challenge

Implementation notes:
- default workflow should *encourage* challenges (e.g., “challenge 1 of 3 ballots”) while keeping accessibility.

### Layer 2: Second-device verification
Mechanism: vote on device A; verify receipt/inclusion on device B (different OS / app store / network).
- Pros: reduces single-device compromise
- Cons: does not solve coercion; does not help if both devices are compromised or the voter verifies poorly

### Layer 3: Out-of-band return codes / code sheets (strongest practical malware defense)
Mechanism: voter receives, via physical mail or in-person, a sheet of codes that confirm selections independently of the device.
- If malware changes the vote, the codes won’t match.
- Swiss designs have used return-code concepts (Prüfcodes) to mitigate malware risk, but operationalizing this is complex and verification logic becomes critical.

Reference discussion: xref: schneier_swiss_evoting_vulnerability_2023_post

### Layer 4: Supervised override vote (“escape hatch”)
Mechanism: a voter can cast an in-person supervised ballot that cancels any remote ballots.
- Pros: strongest coercion + malware safety valve; aligns with “paper ballot of record” recovery
- Cons: requires legal/policy support; introduces operational load

### Layer 5: Credential hygiene & theft recovery
- rapid credential revoke/reissue in-person,
- optional “freeze credential” self-service (with strong authentication),
- publish revocation to the log (so it’s publicly auditable).

---

## UI + receipt safety requirements (MUST)
1. **Never** produce a receipt that proves vote content (prevents direct vote-selling).
2. Receipts MUST be only:
   - log index + Merkle inclusion proof + STH reference (or)
   - a short-lived “pending token” that must become an inclusion proof quickly.
3. The client MUST display an unambiguous state:
   - RECORDED (with inclusion proof),
   - PENDING (time-bounded),
   - NOT RECORDED (fallback required).
4. The client MUST fetch STHs from multiple independent sources (node + mirror/witness) to reduce split-view deception.

---

## What we explicitly do NOT claim
- We do NOT claim to solve client malware for unsupervised remote voting.
- We do NOT claim coercion resistance without strong additional assumptions and mitigations (see `07-coercion.md`).
