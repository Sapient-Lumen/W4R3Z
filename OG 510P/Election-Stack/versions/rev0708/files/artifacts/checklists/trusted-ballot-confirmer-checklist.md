# Trusted ballot confirmer checklist (hardware-wallet pattern)

**Track:** Shared (cross-cutting)


- [ ] Confirmer has a **trusted display** that shows full selections without ambiguity.
- [ ] Confirmer key is hardware-backed, non-exportable; PIN/biometric protects use.
- [ ] Confirmer authorization binds to:
  - [ ] election_id
  - [ ] ballot definition hash
  - [ ] ciphertext commitment
  - [ ] revote_counter
- [ ] No unique device identifiers leaked in attestations (use device-class proofs if needed).
- [ ] Manufacturing/audit governance documented (supply chain, firmware signing, reproducible builds).
- [ ] Accessibility and assisted-voting procedures documented.
- [ ] Coercion limitations explicitly documented (does not prevent observation).
- [ ] Independent security review of confirmer firmware and interface protocol.

