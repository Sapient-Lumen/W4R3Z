# rev0165 paid-action transaction journal export

## Mission-risk targeted

rev0164 made terminal paid-action transaction receipts internally self-checking, but the evidence was still mostly trapped inside C++ structs. That was the next risky seam for agents, fuzzers, branch explorers, and offline auditors: a verifier should be able to inspect the committed or rolled-back declaration/cost-lock payload without linking against private engine internals.

rev0165 therefore adds a stable line-oriented export surface named `MTGSim.PaidActionTransactionJournal.v1`. It is intentionally narrow: it exposes terminal paid-action transaction receipts, the linked committed declaration snapshot when a transaction commits, the speculative rollback declaration snapshot when payment fails, and recomputed declaration/transaction hashes. It does not claim to be a full replay bundle parser yet.

## Code-bearing changes

- Added `kPaidActionTransactionJournalSchemaVersion` and public engine APIs `serialize_paid_action_transaction_journal` plus `paid_action_transaction_journal_text_hash`.
- Exported transaction receipt rows with outcome, stack/declaration links, physical-state hashes, payment spans, speculative rollback counters, the sealed transaction hash, and a recomputed transaction hash.
- Exported `committed_snapshot.*` fields for successful paid actions and `speculative_snapshot.*` fields for rollback receipts, including mode/target anchors, total mana/sacrifice/tap/loyalty cost flags, placement links, declaration hashes, and recomputed declaration hashes.
- Added `mtgsim_cli --write-paid-action-journal-demo JOURNAL` so the surface can be emitted as a file artifact from the command line.
- Added `test_paid_action_transaction_journal_export_surfaces_commit_and_rollback_snapshots`, covering both a successful paid cast and a failed paid cast rollback.

## Audit/refactor notes

The refactor is deliberately not another registry layer. It pulls repeated snapshot text emission into a small serializer helper and gives the command-line harness a concrete paid-action journal writer. The export format is line-oriented so early users can diff it, hash it, and feed it into fuzz/replay experiments before a stricter parser lands.

The main remaining risk is parser-side verification: rev0165 proves the engine can emit enough challenge data, but a later revision should parse `MTGSim.PaidActionTransactionJournal.v1`, recompute the exported hashes, and attach the journal to replay-bundle manifests.

## Online research used

- Wizards' public rules page remains the authoritative surface for the Comprehensive Rules and states that the Comprehensive Rules are a reference for all rules and corner cases: https://magic.wizards.com/en/rules
- Wizards' WPN rules-document page was rechecked for tournament-document freshness; the local manifest still keeps the older packaged metadata pinned until a dedicated rules-refresh/diff revision: https://wpn.wizards.com/en/rules-documents
- OpenSpiel's state/action model remains a useful comparison point for the long-term agent surface: `LegalActions()`, `ApplyAction(action)`, `Child(action)`, and `chance_outcomes()` style APIs argue for stable action/journal artifacts rather than opaque engine-only state transitions: https://openspiel.readthedocs.io/en/latest/concepts.html and https://openspiel.readthedocs.io/en/latest/api_reference/state_chance_outcomes.html
- LLVM libFuzzer's in-process, coverage-guided design reinforces the need for compact deterministic text artifacts that can be generated and mutated cheaply: https://llvm.org/docs/LibFuzzer.html

## Evidence

- Targeted regression: `test_paid_action_transaction_journal_export_surfaces_commit_and_rollback_snapshots` passed.
- Release C++ smoke: `338/338` passed with 0 failures.
- CLI artifact smoke: `mtgsim_cli --write-paid-action-journal-demo` wrote a journal containing the header, summary hashes, and committed snapshot payload.
- Rule coverage, rules progress, and datacube audit were regenerated for rev0165.
