# Reader-state object audit — rev0024

Generated: `2026-06-14T19:47:00-04:00`

## What changed

Rev0024 did not draft D011. It built the missing reader-facing state object for `P0001-D010`:

- `poems/P0001/reader_state/reader_state_object_010.md`
- `poems/P0001/reader_state/reader_state_object_010.json`
- `poems/P0001/reader_state/reader_state_object_010.html`

The object pulls the scattered D010 apparatus into one readable sequence: closed state, open loss state, traversal route, and patched surface. Every visible transition is linked back to local receipts.

## Refactor performed

The cube previously made a reader assemble the experience from `draft_010.md`, branch packet, selector map/vector, state switch, ergodic traversal, return diff, and patch application. Rev0024 refactors that reading path into:

- `tools/build_reader_state_object.py`
- `tools/check_reader_state_object.py`
- `schemas/reader_state_object.schema.json`
- `make reader-state`

This is intentionally a substance refactor: it reduces the reader's assembly burden rather than creating a new poetic mechanism.

## Validation result

`check_reader_state_object.py` passed `241` checks with `0` failures.

The checker confirms that the reader object matches D010 receipts, includes all four states, links receipt paths, uses a no-script HTML disclosure surface plus Markdown fallback, and keeps `quality_claims` empty.

## Risk read

The surface risk has been corrected: `patch` is now visibly applied and readable as a transition. The remaining risk is not validation coverage. It is whether the vocabulary and perceptual pressure are alive enough for a reader. If the state object is still inert under later cold review, the honest next move is to freeze P0001 as a laboratory failure and fork P0002 around resistant external material.

## Sources used as design pressure

Research pulse `RP-0016` used `WEB-0099` for selector/addressability patterns, `WEB-0111` for accessibility fallback pressure, `WEB-0112` for disclosure-panel interaction pressure, and `WEB-0107` as a reminder that verse encoding can care about literary structure rather than only receipts.

## Non-claim

This audit is not a promotion, not a cold review, and not a literary-quality proof. D010 remains `revise_not_promote`.
