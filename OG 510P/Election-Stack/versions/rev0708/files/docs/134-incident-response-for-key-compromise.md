# Incident response for key compromise (IR-KC)

**Track:** A (Deployable core)


Even the best crypto schemes rely on keys. When keys are compromised, the goal is:
- **contain** quickly,
- **preserve evidence**, and
- **restore trust** with replayable, independently verifiable artifacts.

This document aligns election-specific procedures with general incident response best practices (preparation, detection, containment, eradication, recovery, and lessons learned).

## Scope
- PBB signing keys
- witness keys
- trustee threshold shares / HSM roots
- eligibility issuer keys (token minting)
- verifier release keys
- ENR signing keys

## Requirements (normative)
1. **Compromise announcement**
   - Publish a signed `KeyCompromiseEvent` within a defined SLA:
     - what key(s), what component(s), detection time, scope,
     - immediate containment actions,
     - expected impact (what could be forged),
     - and next checkpoint boundary for remediation.

2. **Freeze rules**
   - If compromise impacts ballot integrity or parameter integrity, the system MUST **fail closed**:
     - stop accepting new ballots,
     - stop advancing critical checkpoints,
     - switch to supervised override / paper-of-record processes (policy-defined).

3. **Evidence preservation**
   - Every compromise event MUST produce an evidence bundle including:
     - relevant checkpoints,
     - logs (SP 1500-101 / CDF log extracts where applicable),
     - forensic hashes,
     - and external corroboration (multi-perspective availability evidence).

4. **Reconstitution ceremony**
   - Keys MUST be re-established via a formal ceremony:
     - generate new keys,
     - publish new EPB + witness policy,
     - anchor via KT/checkpoints,
     - and require increased witness/monitor scrutiny during the transition.

5. **Post-incident review**
   - Every incident MUST end with a signed After-Action Report and remediation plan.

## Outputs
- `schemas/KeyCompromiseEvent.json`
- Envelope kind: `hfv.incident.key_compromise_event`
- `artifacts/checklists/key-compromise-response-checklist.md`
## Sources (non-normative)
- NIST CSF 2.0 (risk management framing): `source: nist_csf2_0_pdf`.
- NIST SP 800-61r3 (incident response recommendations aligned to CSF 2.0): `source: nist_sp800_61r3_pdf`.
