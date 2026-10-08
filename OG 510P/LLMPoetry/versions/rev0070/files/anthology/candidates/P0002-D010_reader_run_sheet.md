# P0002-D010 reader run sheet — rev0040

## Use this order

1. Give the reader the portable handoff one-sheet: `anthology/candidates/P0002-D010_reader_handoff/reader_one_sheet.md` or `anthology/candidates/P0002-D010_reader_handoff/reader_one_sheet.html`.
2. Do not show the evaluator rubric, source packets, or cube paths before the first response.
3. Ask the reader to answer the first-response fields and acknowledge the no-personal-identifiers boundary.
4. Copy the answer content into a new JSON file shaped like `anthology/candidates/P0002-D010_response_intake_template.json`.
5. Run `python3 tools/record_reader_response.py --root . --input <response.json> --dry-run`.
6. Append only if the dry run passes. A passing response still does not admit the poem or make it evidence-ready.

## Why this changed in rev0040

Rev0038 made response intake possible. Rev0040 hardens it: blank responses fail, boundary acknowledgement is required, response IDs/timestamps are assigned by the tool, and the handoff can be copied from one small directory.

## Non-claim

Run-sheet, portable handoff, and intake readiness are not reader evidence. No external response is recorded in rev0040.
