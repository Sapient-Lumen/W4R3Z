# VRDB disinformation resilience & public communications

**Track:** A (Deployable core)


Attackers often aim for the *perception* of a hacked registration system. Plan to produce **public, cryptographic evidence** quickly.

## Threat
- False claims of hacked voter information (CISA/FBI have warned of disinfo intended to sow distrust).
- Real but limited incidents amplified into “everything is broken.”

## Requirements
1. **Signed public statements** with evidence bundle hash.
2. **Proof-first communications**: snapshot roots, log checkpoints, witness statements.
3. **Drift dashboards**: show whether VRDB snapshots changed unexpectedly.
4. **Pre-written playbooks**: what to say when, and what proofs to publish.

## Minimum evidence bundle for a VRDB incident
- current `EligibilityEpoch` (signed)
- last N snapshot roots + witness cosigns
- change-log segment covering the alleged window
- detector output (diffs) + hashes

## Public guidance
- Always label unofficial vs official
- Provide “how to verify” steps for third parties (journalists, observers, parties)