# Cube deep audit rev0248 — smoke/staging source-class separation

## What was riskiest

Rev0248 made the owner-reply path runnable with a SRC0 smoke fixture, but the normal staging utility
could still be invoked directly against that fixture. The resulting note looked structurally similar
to a real `PROCEED-STAGED` note, which created a quiet contamination risk: synthetic smoke output
could be copied into the owner packet workbench, release records, or evidence custody by an operator
who skipped the smoke harness context.

## What changed

Rev0248 separates smoke rehearsal from owner staging at the executable boundary:

- `tools/stage_owner_reply_csv.py` now classifies the source at staging time.
- normal staging refuses files under `fixtures/` or rows carrying smoke labels unless the caller uses
  the explicit internal `--allow-src0-smoke` flag;
- the generated staging note now states `Source truth class at staging` as either `SRC0-SMOKE` or
  `UNVERIFIED-OWNER-REPLY`;
- `tools/smoke_owner_reply_pipeline.py` is the only intended smoke path and opts into SRC0 staging
  only to compute the plumbing hash;
- smoke output cannot be written into archive-controlled directories such as `docs/`, `examples/`,
  `fixtures/`, `schemas/`, `templates/`, or `tools/`;
- existing staging and smoke validators now test the direct-smoke block, explicit smoke opt-in,
  scratch-output behavior, archive-output block, and blocked-overbroad refusal.

## Audit/refactor finding

The cube had a useful smoke path but not a hard enough source-class boundary at the exact point where
synthetic content becomes note-shaped. This is the same waste pattern in miniature: a helpful
rehearsal artifact can become new evidence-looking residue unless the tool makes the distinction for
the maintainer.

## Corrected invariant

Synthetic fixtures may test plumbing, but only a real owner reply may pass normal staging. A smoke
fixture can produce a hash or scratch note inside the smoke harness; it must not become a workbench
input, release artifact, custody item, closure record, or public claim support.

## What still is not done

No real owner has been contacted. No owner-filled CSV has been received. No `SRC2+` packet has been
custody-staged, normalized, accepted, rendered, signed off, or closed. `FT-0181` remains live.
