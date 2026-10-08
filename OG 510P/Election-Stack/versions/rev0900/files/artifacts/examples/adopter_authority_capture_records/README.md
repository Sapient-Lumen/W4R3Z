# Adopter authority-capture record validator fixtures

These JSON files exercise the capture-record validator added in rev0870.
They are synthetic fixtures only. Shape-valid fixtures demonstrate that a
record can contain the required capture, hash, responsible-office, scope,
conflict-check, and human-approval fields while still **not** requesting or
authorizing public guidance in this archive. rev0873 adds a fuller
adopter-shaped in-custody routing fixture to exercise the completion path without
promoting any quarantined state/local source.

Negative fixtures intentionally omit or corrupt one promotion-critical field so
`tools/adopter_capture_record_validator.py` can prove that bad capture records
fail before any quarantined state/local route is promoted. Synthetic records that
request promotion are invalid even when they are used as negative controls.

Boundary: these fixtures are not current voter instruction, legal advice,
source-byte cache completeness, public-release authorization, or live-pilot
evidence.
