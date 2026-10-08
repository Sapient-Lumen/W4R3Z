# Rev0013 payload-intake envelope report

Rev0013 opens the payload-intake envelope layer for the DOJ SLS pilot.

The rule is: **a payload envelope is not a payload**.

The revision creates 21 envelope rows, one for each target in the rev0012 capture manifest. Each envelope states the expected carrier class, operator batch, privacy risk tier, required sidecars, and hard stops. It does not capture bytes, compute hashes, bundle payloads, summarize content, extract people, create incidents, or promote current-status claims.

The envelope layer exists because the project is now close enough to real source capture that custody and harm controls must precede content work. A future operator may fetch and hash source bytes privately, but public release remains blocked until privacy, redaction, rollback, and display gates pass.

## New surfaces

- `PAYLOAD-INTAKE-ENVELOPE-LEDGER.json`
- `data/source_graph/payload_intake_envelopes.rev0013.json`
- `data/source_graph/privacy_preflight_queue.rev0013.json`
- `data/source_graph/capture_operator_batches.rev0013.json`
- `data/source_graph/source_capture_order.rev0013.json`
- `data/source_graph/extractive_action_gates.rev0013.json`
- `data/source_graph/custody_sidecar_templates.rev0013.json`
- `data/source_graph/release_redaction_matrix.rev0013.json`
- `data/source_graph/capture_failure_modes.rev0013.json`

## Nonclaims

- No payload is preserved in the public bundle.
- No payload digest is computed in this revision.
- No PDF, HTML page, or linked attachment is summarized.
- No person or incident extraction is allowed.
- No DOJ source label, press release, motion, order, or attachment URL is promoted into a public current-status claim.

