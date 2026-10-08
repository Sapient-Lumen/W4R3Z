# Nicotine+ DEV research cube — rev0086

## Current mission

Turn source-backed Nicotine+ correctness and hardening observations into small,
reviewable research packets whose claims cannot outrun their evidence. Current
authority is machine-readable; historical filenames remain evidence, not truth.

## Rev0086 result

`WISHLIST-SCHED-01` confirms that an all-disabled wishlist scan still dispatches
the final disabled request on exact public-master content. The selected research
correction adds the missing final `search.auto_search` guard. It preserves the
bounded scan and all enabled/mixed round-robin behavior. See
`docs/WISHLIST-SCHED-01-CURRENT-DISPOSITION-REV0086.md`.

The deeper cube defect was a false-green model: downstream inbox code encoded
the intended disabled policy and hid source behavior. Scheduler eligibility and
inbox delivery are now separate layers with exact model/source parity enforced
by `data/current_model_source_differential_contract.json` and documented in
`docs/MODEL-SOURCE-DIFFERENTIAL-GATE-REV0086.md`.

The unchanged Search Again candidate remains at its immutable rev0085 origin
path. Rev0086 revalidates four lanes and 244 cases without claiming fresh test
execution or duplicating patch bytes. Candidate, source, scheduler, packet, and
package authorities are cross-bound by `tools/audit_current_contract_coherence.py`.

## Start here

Read `docs/START-HERE.md`, then the current packet ledger and revision contract:

```text
data/current_packet_dispositions.json
data/current_revision_contract.json
data/current_candidate_artifact_contract.json
data/current_contract_coherence_contract.json
```

All generated code, patches, tests, and prose are research-only and are not
upstream contribution material.
