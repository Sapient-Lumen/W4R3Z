# rev0175 — SBA Lookback Batch

## Mission fit

The project’s useful core is proof-carrying state transition, not breadth-first card emulation. rev0175 targets a risky semantic seam where the engine could have produced correct-looking per-object movement records while losing the simultaneous event context needed by leaves-the-battlefield triggers.

## Rule grounding, without bundling rules text

The online official rules page still points to the Comprehensive Rules as the consulted reference, and the observed current TXT rules file is effective 2026-06-19. The relevant seam is the combination of state-based actions being performed simultaneously and leaves-the-battlefield trigger evaluation using look-back information. The datacube keeps only metadata and local implementation notes here; official rules documents remain excluded from the package.

## What changed

Before rev0175, `move_object(...)` captured battlefield trigger-source snapshots per movement. That is sufficient for a single dying source, but it is fragile for a simultaneous SBA batch: once the first dying trigger source is moved, a later dying object can no longer be seen by that source if trigger discovery reads only the then-current battlefield.

rev0175 adds an internal movement helper, `move_object_with_precomputed_ltb_snapshots(...)`, and threads it through the creature-death SBA paths. `apply_state_based_actions(...)` now captures `pre_creature_sba_ltb_snapshots` once before moving or destroying any creatures in the batch, then reuses that same snapshot for all lethal-damage and nonpositive-toughness creature movements in that SBA pass.

The public `move_object(...)` and `destroy_permanent(...)` APIs remain stable. Their default path still captures a local snapshot for ordinary movement. The new helper is intentionally internal and narrow: it is a batch evidence/refactor hook, not a broad event-batch abstraction.

## Regression

`test_simultaneous_sba_dies_triggers_share_pre_batch_lki_snapshot` creates two dying creatures that each trigger on creature deaths. After simultaneous lethal-damage SBAs, the test requires four pending triggers and specifically checks that the left source sees the right death and the right source sees the left death using the sources’ pre-batch zone-change identities.

## Audit/refactor notes

This cut reduces a real semantic hazard without adding registry ceremony. The refactor also names the internal contract explicitly: callers that already know a simultaneous LTB source snapshot can pass it; all other movement uses the legacy local snapshot path. Audit probes now look for the helper, the pre-batch snapshot, the regression, and ledger rows for `603.10` and `704.3`.

## Known gaps

This is still not complete simultaneous event modeling. The engine still records individual movements, does not expose a first-class event-batch record, and the shared pre-batch snapshot is currently applied only to creature-death SBA movements. Future work should generalize the same idea to other simultaneous zone-change batches, replacement-created events, delayed/optional/intervening-if triggers, and batch-level receipt hashes.


## rev0185 pass-barrier follow-up

rev0175 protected simultaneous creature-death LKI snapshots. rev0185 tightens the adjacent timing seam: `apply_state_based_actions` now collects candidates at each pass boundary and annotates records with `check_index`, `pass_index`, and `pass_candidate_count`. Newly-created conditions, such as an Aura becoming unattached because its enchanted creature died, wait for the repeated SBA check instead of being folded into the same pass.
