# Governance, trusteeship, and legal evidence

**Track:** A (Deployable core)


## Why this exists
In real elections, disputes are resolved by **law and evidence**, not by crypto arguments.
This design must specify:
- who controls keys and how,
- what counts as evidence,
- how recounts and audits interact with cryptographic results.

## 1) Trusteeship model

### 1.1 Diversity requirements
Trustees SHOULD represent mutually distrustful stakeholders (e.g., parties, NGOs, courts, academia).
No single stakeholder class should control a threshold.

### 1.2 Public commitments
Before voting begins, publish:
- trustee roster and threshold parameters
- key ceremony transcript hash
- trustee operational policies

## 2) Evidence hierarchy (recommended)

If paper ballot of record exists:
1. **Paper + risk-limiting audit results** are ultimate outcome evidence.
2. Cryptographic artifacts are supporting evidence and early detection.

If no paper record exists:
- explicitly document which artifacts are authoritative and what failure modes remain.

## 3) Court-ready artifact bundle
The election authority MUST be able to export a signed bundle containing:
- final witness quorum checkpoint
- full log hash commitment
- tally proofs and trustee decryption proofs
- verifier reports and build hashes
- incident reports (if any)

## 4) Transparency and public observation
- Key ceremonies SHOULD be publicly observed (or recorded) with tamper-evident logs.
- Witnesses SHOULD publish transparency reports.
