# P0002-D010 reader intake hardening audit — rev0039

## Finding

Rev0038 made reader-response intake possible, but two risks remained: a blank but correctly shaped response could be accepted as future reader pressure, and `tools/llmpoetry_validate.py` imported the reader-response-intake checker without actually running it.

## Corrections

Rev0039 keeps `P0002-D010` as the current internal anthology candidate and does not create D011. It adds a portable reader handoff directory, requires `boundary_acknowledged`, rejects blank text fields, rejects personal-data keys/text, rejects user-supplied response IDs/timestamps/status fields, and assigns provenance fields only inside `tools/record_reader_response.py`.

`tools/check_reader_response_intake.py` now performs synthetic dry-run tests: the shipped template fails, a blank shaped response fails, a PII/reserved-key payload fails, and a clean synthetic dry-run payload passes without being appended. `tools/llmpoetry_validate.py` now runs this checker as part of the main gate.

## Non-claim

No external reader response is recorded in rev0039. The synthetic dry-run payload is a tool test only, not reader evidence. P0002-D010 remains not admitted and not evidence-ready.
