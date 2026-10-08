# P0002-D010 adversarial candidate pressure audit — rev0041

Current head: `P0002-D010` — **A Ruler for Water**.

## Finding

The reader-handoff/intake apparatus was largely ready, but the candidate itself was at risk of false readiness. Rev0041 therefore does not create D011. It adds an internal adversarial candidate read and a fallback-only D011 brief, while preserving the reader-first gate.

## Substantive candidate pressure

The adversarial read keeps D010 held, not admitted. It identifies surviving hinges in the opening ruler/staff image and the compressed absence pair `No value came back. / Water did.`, while flagging that `Station Datum` and the closing concept pair may still import authority too neatly.

## Refactor/audit repair

A concrete integrity fault was found: candidate metadata had stale `draft_sha256` values for `poems/P0002/draft_010.md`. Rev0041 updates the candidate packet and P0002 metadata to the current draft hash and adds `tools/check_candidate_pressure.py` so future candidate packets cannot drift from the draft file silently.

## Boundary

The adversarial read is not a reader response, not evidence, and not admission. The fallback brief is not D011 and may only be used after real reader rejection/complication or project-owner override.

## New blocking gate

Run `make candidate-pressure`, or rely on `make validate` / `make doctor`, which now include the candidate-pressure guard.

## Validator refactor after audit

While verifying `make doctor`, the reader-response-intake checker proved non-reentrant when called after the main validator in the same Python process. Rev0041 refactors that checker to exercise the recorder's production append function in-process, still against a temporary clone for non-dry-run append tests. This preserves the transactional append check while allowing `make doctor` to rerun the gate without hanging.
