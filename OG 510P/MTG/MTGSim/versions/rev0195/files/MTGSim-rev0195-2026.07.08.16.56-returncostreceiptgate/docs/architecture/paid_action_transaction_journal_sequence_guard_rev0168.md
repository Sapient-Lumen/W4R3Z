# Paid-Action Transaction Journal Sequence Guard — rev0168

## Mission seam

The paid-action transaction journal is now an external verifier boundary. rev0167 made the ordered row payload hash-sealed, but a future multi-row journal still needed explicit causal-order semantics so an offline auditor can reject a journal that is internally well-formed but temporally scrambled or downgraded.

## Change

rev0168 bumps newly emitted journals to `MTGSim.PaidActionTransactionJournal.v3` and adds header-level sequence bounds:

- `first_transaction_sequence`
- `last_transaction_sequence`

The verifier now requires the current v3 schema, rejects older v1/v2 journals as unsupported, rejects zero transaction sequences, requires strictly increasing row sequences, and checks the parsed first/last row sequence against the header bounds. The existing `record_payload_hash` remains the ordered row payload seal.

## Why this is the risky slice

A journal verifier that validates hashes but does not explicitly validate causal row order can still be dangerous once exports contain more than one paid-action transaction. A generated artifact could appear complete while hiding a row splice or downgrade that changes what a downstream agent believes happened first. This slice makes the order contract typed and executable before adding broader replay-manifest integration.

## Executable evidence

- `test_paid_action_transaction_journal_parse_verify_rejects_tampering` now covers sequence tamper, first-sequence header tamper, schema downgrade, payload tamper, unknown fields, blank lines, stale state binding, and mixed-row splicing.
- `mtgsim_cli_paid_action_journal_roundtrip` is now a CTest release case, making the public CLI writer/verifier path part of the release surface.
- `reports/harness/paid_action_transaction_journal_rev0168_verify.stdout.txt` exposes the verifier's `record_payload_hash`, `first_sequence`, and `last_sequence` echoes.

## Remaining edge

The sequence guard is a journal-local proof. The next trust boundary is replay-bundle integration: paid-action journals should be attached to replay manifests and verified alongside snapshots, action traces, and prefix/resume diagnostics.
