# Bonded witness incentives and penalties

**Track:** A (Deployable core)


## Goal
Reduce witness capture and “silent failure” by introducing **measurable incentives** and **credible penalties** that are enforceable via public evidence.

This is a governance layer. It does not replace cryptography.

## Concepts
- **Bond**: a posted commitment (financial, reputational, contractual) tied to witness obligations.
- **Slashing event**: an evidence-backed determination that a witness violated obligations (e.g., signed inconsistent checkpoints, failed liveness SLOs, or withheld cosigning).

## Requirements
- Each witness MUST publish a signed `WitnessBond` describing:
  - bond type (financial escrow, insurance, contract)
  - covered obligations
  - adjudication forum and appeal path

- The system MUST define `SlashingEvent` triggers that are objectively provable:
  - equivocation (signing incompatible checkpoints)
  - missed availability SLOs beyond tolerance
  - failure to publish required disclosures

- All `SlashingEvent` objects MUST be:
  - signed by the governance authority (or multi-party panel)
  - anchored into the evidence chain

## Election-specific caution

Financial bonding is not a panacea:
- a state actor (or politically connected adversary) may be able to **freeze, seize, or coerce** financial instruments, turning “slashing” into a weapon.

Therefore:
- bonds SHOULD be treated as **supplementary** to institutional diversity (`135`) and admission/removal policy (`139`),
- acceptable bond types SHOULD include **non-financial** commitments (insurance, professional credential risk, contractual penalties, public disclosure duties),
- adjudication MUST have an appeal lane and be resilient to unilateral political pressure.

## Anti-abuse
- Slashing must require multi-party approval and public evidence.
- Emergency removals MUST still produce a signed, anchored record.
