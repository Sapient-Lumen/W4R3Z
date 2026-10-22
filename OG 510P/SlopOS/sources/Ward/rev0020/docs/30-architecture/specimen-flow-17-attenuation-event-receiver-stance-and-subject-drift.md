# Specimen flow 17 — attenuation event, receiver stance, and subject drift

Goal: keep real-time trust changes, local receiver policy, and subject continuity visibly separate.

## Scenario
A relying party has already admitted a subject, device, and session based on earlier proofs.
Later it receives a continuous signal saying the session was revoked, the device compliance changed, or the subject’s risk level increased.
The receiver must map the subject, decide whether the signal applies strongly enough to attenuate local access, and preserve a clear residue about whether it suspended, reduced, refreshed, or ignored the local consequence.

## Proposed Ward objects
1. **attenuation event**
   - signed outside signal that asks the receiver to narrow or revisit local consequence;
   - stronger than folklore and weaker than direct local spend.

2. **receiver stance**
   - explicit local posture about how this receiver interprets and acts on the signal;
   - stronger than raw event delivery and weaker than timeless trust policy.

3. **subject drift**
   - typed residue about ambiguity or mismatch in how the incoming subject maps to local identity state;
   - important because continuity problems can survive clean signatures.

4. **status receiver**
   - named local lane that accepts, queues, attenuates, or quarantines continuous status inputs.

## Why this specimen matters
It pressure-tests whether Ward can stay honest when:
- verification already succeeded earlier,
- later events narrow trust without replacing old evidence,
- subject mapping is imperfect,
- and local action depends on receiver policy rather than transmitter wishes alone.

## Promotion rule
Do not promote `attenuation event`, `receiver stance`, `subject drift`, or `status receiver` unless they improve:
- one session-revoked specimen,
- one device-compliance-change specimen,
- and one subject-mapping ambiguity specimen that refuses silent overreach.
