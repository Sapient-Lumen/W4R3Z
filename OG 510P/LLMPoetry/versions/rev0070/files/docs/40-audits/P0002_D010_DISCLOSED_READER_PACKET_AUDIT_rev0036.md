# P0002-D010 disclosed-reader packet audit — rev0036

## Main finding

The riskiest incomplete step after rev0035 was not another draft. It was the lack of a portable, disclosed-first reader surface for `P0002-D010`.

Rev0036 creates that surface without claiming a test occurred:

- `anthology/candidates/P0002-D010_disclosed_reader_packet.md`
- `anthology/candidates/P0002-D010_disclosed_reader_packet.html`
- `anthology/candidates/P0002-D010_disclosed_reader_packet.json`
- `anthology/candidates/P0002-D010_reader_response_form.md`
- `anthology/candidates/P0002-D010_reader_responses.json`
- `anthology/candidates/P0002-D010_hostile_disclosed_reader_protocol.json`

## Substantive boundary

The packet shows machine/source/runtime disclosure before the poem. It asks a hostile reader whether the poem survives disclosure, whether the disclosure merely explains the poem, and whether the candidate still reads as a graceful receipt object.

The response log is intentionally empty. No external reader evidence is fabricated.

## Refactor

The legacy blind-first disclosure-test posture was refactored to a disclosed-first candidate packet posture. `make pilot-queue` also failed before this revision because the newest pilot rows had no registered `form_id`; rev0036 adds `FORM-disclosed-reader-candidate-packet` and attaches it to the current candidate-test pilots.

## New guard

`tools/check_candidate_reader_packet.py` validates the disclosed-reader packet, HTML fallback, response form, empty response log, active disclosure-test template, and candidate non-claim boundary.

## Non-claim

The packet is a launch surface for reader pressure, not reader pressure itself. `P0002-D010` remains not admitted and not evidence-ready.
