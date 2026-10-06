# rev0091 storage-lane quarantine receipt restore integrity contract audit slice

Current audit task: `facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit`.

This audit guards the runtime wiring for the restore-integrity slice. It checks that the adapter and type surfaces expose `verifyBeforeRestore`, `allowUnsafeUnverifiedRestore`, and `verifyOptions`, that the release-light and browser probes are registered, and that first-read surfaces point at the current rev0091 restore-integrity office instead of the previous receipt replay-key integrity slice.

The audit is intentionally not the proof itself. The release-light probe checks synthetic unverified restore opt-out rejection and block-integrity failure before `get()`, and the browser proof checks real OPFS/Web Lock behavior with a deliberately corrupted persisted clearance receipt block.


This rev0091 slice explicitly treats persisted quarantine ledger and clearance receipt **block integrity** as a restore gate before any maintenance state is imported or registered.

This is the current audit task for rev0091: `facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit`.

restore block integrity browser-light
