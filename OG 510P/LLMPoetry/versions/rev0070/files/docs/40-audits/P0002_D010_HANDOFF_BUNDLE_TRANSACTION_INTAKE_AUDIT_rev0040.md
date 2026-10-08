# P0002-D010 handoff bundle / transactional intake audit — rev0040

## Finding

The riskiest unfinished work is still the missing real reader response. Rev0040 does not fabricate that response and does not draft D011. Instead it removes two practical blockers that could have made the next reader handoff fail or become misleading.

First, rev0039 had a handoff folder but no validated reader-only ZIP. A folder inside the cube is easy to expose with evaluator/source/tool context by accident. Rev0040 adds a deterministic handoff bundle and sidecar hash.

Second, rev0039 tested dry-run intake but did not transaction-test the real append path. Rev0040 runs a non-dry-run append in an isolated temporary clone, verifies response/log/packet count updates there, rejects a duplicate append, and confirms the real response log remains unchanged.

## Refactor

New tools:

- `tools/build_reader_handoff_bundle.py`
- `tools/check_reader_handoff_bundle.py`

Changed tools:

- `tools/record_reader_response.py`
- `tools/check_reader_response_intake.py`
- `tools/llmpoetry_validate.py`
- `tools/doctor.py`
- `tools/check_pilot_queue.py`

New current bundle:

- `anthology/candidates/P0002-D010_reader_handoff_bundle.zip`
- `anthology/candidates/P0002-D010_reader_handoff_bundle.zip.sha256`

## Correction

The response-log checker no longer scans tool-managed timestamps, response IDs, or fingerprints for phone-like patterns. It scans reader-supplied fields only. This avoids a future false failure where a legitimate recorded timestamp could look like a phone number.

## Duplicate guard

The intake tool now assigns `content_fingerprint` and rejects duplicate response content. This prevents repeated appends of the same reader text from masquerading as multiple reader pressures.

## Boundary

No external reader response is recorded in rev0040. The synthetic append happens only inside a temporary clone and is deleted. Handoff-bundle readiness is not reader evidence, poem quality, admission, or evidence-ready status.
