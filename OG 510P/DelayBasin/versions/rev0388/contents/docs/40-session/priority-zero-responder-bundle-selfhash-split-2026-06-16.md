# Priority-0 responder-bundle self-hash split — 2026-06-16

## Why this revision exists

`rev0372` correctly split the frozen responder artifact from the post-response score sheet, but a fresh audit found a concrete handoff defect: the response template carried a `responder_bundle_sha256` value even though that template is a member of the responder bundle whose digest it attempted to name.

That is not just a stale hash. It is a self-reference bug. Updating the template changes the bundle; rebuilding the bundle changes the hash the template would need to contain. The observed `rev0372` template digest for the bundle therefore drifted behind the actual responder bundle, and the checker did not catch it.

## Change made

`rev0373` repairs the handoff boundary rather than claiming external replay success. The expected bundle hash is absent from responder-visible files; expected digest verification lives only in post-freeze scorer/custody/manifest material.


- responder-visible files no longer embed an expected SHA256 for the responder bundle that contains them;
- the responder records the observed bundle digest by computing the SHA256 of the bundle file they were handed;
- scorer/custody/manifest material, opened only after response freeze, holds the expected responder-bundle digest;
- the current checker rejects responder-visible bundle members that carry a 64-hex `responder_bundle_sha256` field or the actual bundle digest;
- the score tool now requires the separate score sheet to bind to the custody evidence record hash, not merely to the response hash;
- the `score-external-response` Make target can pass both `EVIDENCE` and `SCORE_SHEET`, so the documented score-separated path is actually invokable.

This is a workbench repair. No clean external/operator-independent response exists yet.

## Audit / refactor

The concrete audit target was the `rev0372` score-separated handoff. The failure mode was self-hash drift: a responder-visible template advertised an expected bundle hash that could not remain stable inside its containing ZIP. The refactor moves expected-bundle-hash authority out of responder-visible files and into post-freeze scorer/custody material.

The scoring path was also tightened. A strict clean score sheet now must name the custody evidence record hash and match the provided custody file. That closes a small but real chain-of-custody gap in which a score sheet could bind to the response but omit the custody-record hash.

## Current command

After a clean responder has completed and a distinct custodian has frozen the response and evidence record, the scorer should run:

```bash
make score-external-response \
  RESPONSE=<frozen-response.json> \
  EVIDENCE=<completed-custody-record.json> \
  SCORE_SHEET=<completed-score-sheet.json>
```

or directly:

```bash
python -S tools/score_priority_zero_external_replay_response.py \
  --scorer-intake assays/priority-zero-selfhash-split-external-replay-scorer-intake-2026-06-16.json \
  --evidence-record <completed-custody-record.json> \
  --score-sheet <completed-score-sheet.json> \
  --summary-out <score-summary.json> \
  <frozen-response.json>
```

## Stopgate

`OQ-0264` is resolved only as: the prior score-separated workbench had a self-referential bundle-hash defect and a too-permissive score-sheet custody binding. `OQ-0265` carries the actual external replay collection and scoring work using the selfhash-split submission kit and scorer kit.

Forbidden shortcuts remain unchanged: bundle existence, corrected hashes, custody template existence, score-sheet template existence, negative canaries, scorer-kit existence, same-session dry-runs, and further internal repairs do not count as clean external replay success.
