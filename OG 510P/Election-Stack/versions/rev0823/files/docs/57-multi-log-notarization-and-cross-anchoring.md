# 57 — Multi-Log Notarization & Cross-Anchoring

**Track:** A (Deployable core)


## Why this exists (paranoid assumption)
Even if the PBB is federated, a motivated attacker may attempt a **history rewrite** via:
- coordinated compromise of quorum operators
- legal/administrative seizure
- catastrophic operational failure

A strong countermeasure is to **anchor key election artifacts into multiple independent transparency systems**.

## Concept
A transparency log provides:
- an append-only record
- cryptographic inclusion proofs
- consistency proofs

Cross-anchoring means publishing the hash of the *same* artifact into multiple logs operated by independent parties.

## What to notarize
At minimum:
- final ElectionParameterBundle (EPB) hash
- each witness-quorum checkpoint hash (FINAL checkpoints)
- final tally proof bundle hash
- post-election RLA report hash

## Where to notarize (examples)
- One or more **public transparency logs** used in software supply chain contexts.
- Partner-run independent “observer logs” (universities, NGOs, parties).

## Normative requirements
1. The system MUST define a **NotarizationPolicy** ahead of time (in EPB).
2. For each notarized artifact, the system MUST retain:
   - the log entry identifier
   - inclusion proof
   - log checkpoint/tree head used
3. Notarization MUST be verifiable offline from an Evidence Bundle.
4. Failure to notarize during an incident MUST be surfaced as an availability/legitimacy defect.

## Artifact: `NotarizationRecord`
A NotarizationRecord includes:
- artifact_type
- artifact_hash
- log_system_id
- log_entry_id
- inclusion_proof
- checkpoint
- timestamp (local) + secure time proof if available

## Cross-checkpointing back into the PBB
Each NotarizationRecord MUST itself be posted to the PBB, so observers can track that notarization happened.

## Open question
How to ensure notarization endpoints do not become censorship chokepoints? Recommend multiple providers and client-side retry logic with bounded delays.