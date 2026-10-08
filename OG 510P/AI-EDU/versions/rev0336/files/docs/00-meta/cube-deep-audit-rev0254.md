# Cube deep audit rev0254

## Posture

The cube is still ready-but-not-closed. `FT-0181` remains live because there is
no real `SRC2+` owner-reviewed packet, no accepted import, no live-window
readout, and no closure signoff. Rev0253 made the outbound owner request packet
executable. Rev0254 addresses the next completion risk: after a human sends or
adapts that packet, the session can still drift into silence, memory, or another
doctrine branch unless the contact clock has an executable local state.

## Priority change

Rev0254 adds `tools/record_ft0181_owner_contact_status.py` and the make target
`make owner-contact-status`. The utility records exactly three local, non-evidence
states:

- `SENT_AWAITING_REPLY` after the first bounded owner request is sent;
- `REASK_AWAITING_REPLY` after the one allowed clarification is sent;
- `NO_OWNER_PACKET` after the response clock and no more than one clarification
  fail to produce a viable owner packet.

The output stays in `scratch/` or an external local directory. It is labelled
`not_evidence`, `does_not_close_ft0181`, and `public_claim_effect: none`. It also
carries an explicit no-widening confirmation and forbids creating a new registry
or doctrine surface to replace the missing owner packet.

This is a field-action repair, not a new theory. The next human action is still
to send the packet. The new status recorder makes the two legitimate outcomes
machine-visible: either a real CSV enters intake, or a bounded `NO-OWNER-PACKET`
keeps `FT-0181` live without pretending that silence is evidence.

## Audit/refactor change

The owner-reply field lane now covers first-contact packet prep, owner-contact
status, owner-reply triage, receipt, intake, staging, smoke, and workbench-seed
checks. `tools/check_ft0181_owner_contact_status.py` validates the status recorder
against five failure modes: archive-controlled output, forbidden raw/protected
argument terms, impossible dates, early no-packet closure, and more than the
allowed first ask plus one clarification.

I also corrected a stale audit sentence in the rev0253 deep audit that described
`run_lint_suite.py` as subprocess-based. The current runner reads registry-defined
lanes and executes selected validators in-process through `runpy`; owner-reply
validators also import their underlying receipt/intake/staging functions where
practical. The full lane is now fast enough in this cloudtainer that the remaining
risk is not validation time, but failing to exercise the field contact path.

A second packaging audit found that generated surface and JSON checks still saw
`scratch/` files in the working tree even though release packages intentionally
exclude `scratch/`. Rev0254 therefore excludes `scratch/` from `check_json.py`,
`gen_surface_map.py`, and `check_surfaces.py` so local smoke/status artifacts can
never change packaged counts or surface hashes.

## External-context refresh

Rev0254 adds `[B291]`, the European Commission high-risk AI systems classification
guidance, to the bibliography, education-risk crosswalk, watchlist, and evidence
refresh calendar. This does not change the `FT-0181` target row. It reinforces the
same boundary: `FT-0181` may only remain a bounded course-operations draft-reminder
workflow. If the owner reply reveals admissions, programme assignment, learning
outcome evaluation, level-of-education decisions, test-behaviour monitoring,
protected-route inference, automatic send/write, penalty, profiling, or durable
record action, the packet must leave the ordinary lane and block or retreat.

## What is still missing

The missing object is still external: one real owner-attested eight-row CSV, or a
recorded `NO_OWNER_PACKET` after a real first-contact attempt and one bounded
clarification. The cube now has executable commands for both sides of that fork:

```bash
make owner-request-packet OUT=scratch/owner-request-packets/aiedu-sr-003-first-contact
make owner-contact-status STATUS=sent-awaiting-reply SENT_DATE=YYYY-MM-DD RESPONSE_DUE_DATE=YYYY-MM-DD OUT=scratch/owner-contact-status/aiedu-sr-003-sent
make owner-reply-intake CSV=/path/to/returned-owner-reply.csv OUT=scratch/owner-reply-intakes/aiedu-sr-003
make owner-contact-status STATUS=no-owner-packet SENT_DATE=YYYY-MM-DD RESPONSE_DUE_DATE=YYYY-MM-DD STATUS_DATE=YYYY-MM-DD ATTEMPT_COUNT=2 OUT=scratch/owner-contact-status/aiedu-sr-003-no-owner-packet
```

Any future revision that adds more background doctrine without either a real CSV,
a sent-contact status, or a bounded no-packet status should be treated as drift.

## Validation intent

Rev0254 should pass `make lint-owner-reply`, `make lint-fast`,
`make lint-release-controls`, and `make lint-full` before packaging. The important
release claim is narrow: the cube has a safer executable contact-clock lane; it
still has no real pilot evidence and no closure basis.
