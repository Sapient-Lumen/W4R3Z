# Cube deep audit rev0241: first-reply burden and stale startup repair

## Finding 1: the first owner ask was still too complete

Rev0240 correctly moved the first contact to the safer `AIEDU-SR-003` capped assignment-reminder
workflow. The next failure mode was smaller: the packet still looked like something a careful owner
might postpone until a technical export owner, analytics dashboard, or broader meeting existed.
That would recreate the archive's old vice: more control-plane activity while the only missing item
is a real owner-reviewed packet.

Rev0241 therefore compresses the first contact into a ten-minute core reply. The core asks only for
service/owner/source/date, aggregate counts, draft-only authority boundary, fallback/rollback/stop,
workload/training note if known, public claim ceiling, redaction assertion, and owner attestation.
Everything else is optional follow-up after a viable reply lands.

## Finding 2: technical owner dependency could block the first reply

The `AIEDU-SR-003` service record has an LMS integration owner, but the first contact should not
depend on that person. Requiring a technical owner too early turns a field request into an export
project. The revised `outreach_preflight` names only the course operations lead and course
coordinator for first contact. A technical owner appears later only if source meaning is ambiguous
after a viable core reply.

## Finding 3: root re-entry surfaces had drifted behind the packaged state

The rev0240 receipt described the reminder-first-contact change, but root startup surfaces and the
changelog still opened at rev0239. That was not cosmetic: `make lint` failed at receipt sync before
any substantive validators could run. Rev0241 treats this as the audit/refactor repair and moves the
root spine to the current revision.

## Current risk posture

The cube is still not missing another broad registry. It is missing a real owner answer. The highest
risk now is owner non-response, not false closure. The correct next result is one of three states:

- a ten-minute `SRC2+` core reply arrives and routes to the owner packet workbench;
- the owner can only supply overbroad/protected/raw data, and the archive records a block;
- no viable owner path responds after one follow-up, and the archive records `NO-OWNER-PACKET`
  without creating a new control.

## Refactor rule for the next pass

Do not add a new FT-0181 control unless a real packet exposes a failure that the current workbench,
decision board, change ticket, live-window card, readout gate, post-readout dispatch, closeout, or
claim lexicon cannot catch. If the first contact still feels hard to send, shrink it again.
