# Threat model (paranoid, scoped)

**Track:** A (Deployable core)


This threat model assumes **real election** adversaries, not “normal web app” attackers.

## Adversaries

### A1: Nation-state / APT
Capabilities: supply-chain compromise, 0-days, long-term persistence, strategic DDoS/partition, targeted disinformation, insider recruitment.

### A2: Malicious insider / colluding vendor
Capabilities: access to management plane and build systems; influence over procedures; ability to skew operations (selective drops, “accidental” misconfigurations).

### A3: Malware on voter device
Capabilities: modify UI, alter ciphertext, suppress challenges/verification, exfiltrate credentials, target specific voters/demographics.

### A4: Coercer / vote buyer
Capabilities: observe voting, demand “proof,” demand abstention, confiscate credentials, monitor devices over time.

### A5: Network attacker / censor
Capabilities: block endpoints, partition witnesses, replay traffic, selective throttling by region/ISP.

### A6: Verifier ecosystem attacker (subtle but real)
Capabilities: exploit bugs in verifiers/clients so that invalid proofs appear valid, or valid proofs appear invalid, creating chaos or cover for manipulation.

---

## Security objectives (ranked)
1. **Correct outcome with evidence.** If a result is declared, sufficient public evidence must exist for independent verification and adjudication.
2. **Software independence / recovery.** No software fault/compromise can cause an undetectable outcome change; recovery must be possible (paper + audits).
3. **Public auditability.** Anyone can verify: “recorded as cast” and “tallied as recorded.”
4. **Ballot secrecy.** Prevent linking voter ↔ choices (within stated assumptions).
5. **Availability with safe failure.** Outages must not silently corrupt outcomes; system fails safe to fallback.

---

## Key abuse cases (non-exhaustive)
- UC1: Server accepts some ballots but selectively drops others (censorship).
- UC2: Server shows different log histories to different observers (equivocation/split view).
- UC3: Compromised client changes votes while pretending everything is fine (malware).
- UC4: Coercer forces voters to vote a certain way or abstain; monitors compliance.
- UC5: Credential theft enables fraudulent voting or revote suppression.
- UC6: Build/update compromise ships a backdoored client/server release.
- UC7: Verifier bug causes false acceptance/rejection of proofs (security-critical correctness).
- UC8: Privacy failure reveals turnout or links ballots to voters (surveillance risk).
- UC9: DDoS/partition on election day disenfranchises targeted regions.

---

## Design invariants implied by this model
- The PBB must be **tamper-evident** (Merkle log + witnesses + gossip).
- No single party holds decryption power (threshold).
- Verifiers must be independently implementable; proofs must be testable with public vectors.
- Remote return must always have a safe fallback and an emergency “fail closed” posture.
