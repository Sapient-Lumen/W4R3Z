# Priority-0 preanswer-clamped external replay responder bundle — 2026-06-16

Use this extracted bundle as the **only** pre-response material for `OQ-0266`. Keep the original responder ZIP available as a file; the helper hashes that exact ZIP.

## 1. Initialize a bound response draft

From the extracted responder-bundle root, before answering:

```bash
python -S tools/prepare_priority_zero_external_replay_response.py init \
  --bundle-file <original-responder-bundle.zip> \
  --responder-id <responder-id> \
  --out <response-draft.json>
```

The helper records the responder ID, local process-clock start time, exact original ZIP hash, and bundled responder-packet hash. It refuses to overwrite an existing output.

## 2. Fill only answer and cost fields

In the generated draft, edit only:

- every packet's seven answer fields;
- every packet's positive `operator_cost_minutes`;
- the top-level `responder_stage.operator_cost_minutes`, equal to the packet-cost sum within `0.05` minutes.

Treat each packet as its own bounded cue set. Do not import facts from another packet. A reasoned abstention is valid; an empty or placeholder field is not.

Do not hand-edit helper-owned identity, hash, timestamp, state, attestation, or `response_artifact` fields. Do not add `manual_metric_scores` or a scorer stage.

## 3. Validate and freeze before any post-response material opens

```bash
python -S tools/prepare_priority_zero_external_replay_response.py finalize \
  --draft <response-draft.json> \
  --bundle-file <same-original-responder-bundle.zip> \
  --exposure-notes "only this responder bundle was visible before finalization" \
  --attest-clean-preanswer \
  --out <frozen-response.json>
```

Finalization fails before custody is spent if an answer is blank, a packet cost is missing/invalid, costs do not reconcile, bundle or packet identity drifted, scorer fields leaked in, or tool-owned provenance fields were altered. It records the completion/finalization time from the local process clock, writes a new immutable candidate, and refuses overwrite.

Hand the exact frozen file to a custodian whose ID differs from the responder. Do not edit it after finalization, self-custody it, or score it.

Clean-preanswer rule: before finalization, do not open any custody kit, custody template, scorer kit/intake, score-sheet template, answer key, handoff manifest, expected digest, full archive, old submission kit, prior conversation, or prior response. Any such exposure contaminates the run even if hashes later match.

Timestamp boundary: helper-captured local process clocks reduce manual transcription and backfill. They are not trusted timestamp-service evidence, hardware clock attestation, or independent proof of wall-clock truth.

Scope rule: the four synthetic packet cues are co-visible, and `packet-delta` is a trace excerpt rather than a measured full archive. A clean triplet may test bounded semantic recovery, sham rejection, abstention, and reported effort; it cannot establish a causal compact-versus-full burden comparison or global compact default.

Non-claim: this bundle is not a completed response, independent certification, deletion authority, benchmark authority, global compact-cue confirmation, or a review court.
