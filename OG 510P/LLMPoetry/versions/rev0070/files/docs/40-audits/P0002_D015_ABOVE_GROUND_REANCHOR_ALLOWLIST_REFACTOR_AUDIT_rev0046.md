# P0002-D015 above-ground reanchor / allowlist refactor audit — rev0046

Current head: `P0002-D015` — **Above Ground**.  
Created: 2026-06-17T02:42:00-04:00.

## Main risk addressed

D014 had found a smaller source object, but the stamped mark `NO 7 1975` became too available as a pun and thesis. The revision pressure now comes from the NOAA benchmark placement itself: the mark for water is fixed in concrete above ground, outside the water.

## Substantive change

D015 removes the stamped-name body display and tests a smaller contradiction:

```text
The mark for water
is not in the water.
```

It keeps the staff / first-zero / no-value hinge, but does not print NOAA, API, station metadata, or datum-table numbers in the body.

## Refactor

The audit found a recurring waste path: multiple validators allowed `P0002-D011` through `P0002-D014` explicitly. That would force another low-value code edit every time P0002 advanced. Rev0046 changes those gates to recognize preserved-candidate successor heads dynamically for `P0002-D011` and later, while still preserving D010 candidate-reader boundaries.

Changed validators include:

- `tools/check_candidate_reader_packet.py`
- `tools/check_reader_response_intake.py`
- `tools/check_reader_handoff_bundle.py`
- `tools/check_candidate_pressure.py`
- `tools/check_fallback_subtraction.py`
- `tools/check_pilot_queue.py`

Non-claim: this is not a poem-quality claim, not admission, not reader evidence, and not a live NOAA water-level value.
