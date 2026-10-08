# Witness cosigning policies and compromise recovery

**Track:** A (Deployable core)


The core defense against **split-view / equivocation** is a **witness cosigning** model: a quorum of independent witnesses co-sign checkpoint statements after verifying append-only consistency and freshness.

This idea is well-studied (e.g., CoSi / witness cosigning) and appears in modern transparency systems, including Sigsum’s witness-cosigned tree heads.

## Threats addressed
- **Log operator compromise**: attacker forks the log and shows different histories.
- **Targeted split views**: different audiences see different checkpoints/bundles.
- **Witness key compromise**: attacker controls some witness keys to raise the split-view threshold.

## Witness cosigning (recap)
A witness SHOULD verify, before cosigning:
- the checkpoint is **fresh** relative to policy,
- the checkpoint is **append-only consistent** with previously seen checkpoints, and
- (optionally) the checkpoint includes required anchors (EPB hash, ATL hash).

End users accept a checkpoint only if it satisfies a **policy** such as:
- “require at least k-of-n witness cosignatures,” and/or
- “require k-of-n, including at least one witness from each stakeholder class.”

## Requirements (normative)
1. **Witness policy language**
   - The election MUST publish a `WitnessCosigningPolicy` inside the EPB:
     - threshold (k-of-n),
     - diversity constraints (classes/regions/independence sets),
     - freshness deadlines.
   - Clients/verifiers MUST enforce this policy when validating checkpoints.

2. **Witness set change ceremony**
   - Witness membership changes MUST be:
     - announced in advance where possible,
     - encoded as a signed `WitnessSetChange` object,
     - anchored into the PBB/ATL,
     - and become effective only at a defined checkpoint boundary.

3. **Compromise recovery for witness keys**
   - On suspected witness-key compromise, the system MUST:
     - publish a signed `KeyCompromiseEvent` with evidence pointers,
     - rotate the witness key (or remove the witness),
     - and publish an updated witness set + policy bound to a checkpoint boundary.
   - Clients/verifiers MUST treat compromised witnesses as invalid from the declared effective time.

4. **Safe shutdown**
   - The system MUST define a “safe shutdown mode” where:
     - checkpoints stop advancing,
     - no new ballots are accepted,
     - and verification remains possible for already-published artifacts.

## Implementation notes
- Prefer offline-protected witness keys (HSM/secure element).
- Use **gossip** among witnesses and monitors to amplify split-view detection.
- Treat “witness silence” as a signal; publish availability evidence into ATL.

## Outputs
- `schemas/WitnessSetChange.json`
- `schemas/KeyCompromiseEvent.json`
- `artifacts/checklists/witness-compromise-recovery-checklist.md`