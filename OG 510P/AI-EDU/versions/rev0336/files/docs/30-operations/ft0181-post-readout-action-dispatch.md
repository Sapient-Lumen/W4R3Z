# FT-0181 post-readout action dispatch

Rev0287 made the post-readout action executable. Rev0288 keeps that dispatch
bounded and adds the next firebreak: a dispatch with a `due_or_recheck_date` must
be rechecked on or after that date before anyone treats the owner-action lane as
complete, newly supplied, blocked, or eligible for downstream service/public/
lifecycle work.

Rev0301 adds a scratch-only bridge before the dispatch:

```bash
make owner-post-readout-action-brief \
  READOUT=scratch/path/to/live-window-readout.json
```

The brief validates the terminal readout and emits the bounded
`owner-post-readout-action` command skeleton. It is not the dispatch, not owner
action, not a recheck, not evidence, and not closure.

## Source

A post-readout action may only be generated from a valid terminal
`live-window-readout.json`. The preferred route is now:

```text
terminal live-window readout
→ owner-post-readout-action-brief
→ human-recorded owner-post-readout-action
→ wait until due_or_recheck_date or new real owner context
→ owner-post-readout-recheck
```

The human dispatch command remains:

```bash
make owner-post-readout-action \
  READOUT=scratch/path/to/live-window-readout.json \
  DISPATCH_LANE=<lane> \
  NEXT_EVIDENCE_ASK_CLASS=<class> \
  PUBLIC_LANGUAGE_ACTION=<action> \
  DUE_OR_RECHECK_DATE=YYYY-MM-DD \
  REVIEWER_ROLE_COUNT=<2-5> \
  CONFIRM=human-recorded-post-readout-action-no-closure \
  NO_EXPANSION_CONFIRMED=1 \
  OUT=scratch/field/ft0181/owner-post-readout-actions/aiedu-sr-003-action
```

The source readout is re-read and hash-checked. The action cannot copy raw owner
answers, live-window notes, protected facts, security payloads, contact details,
or public-claim text.

## Effect

The dispatch is local non-evidence. It may name an owner-action class, a bounded
next evidence ask, action/drop/reask counts, and a due/recheck date. It does not
edit service records, upgrade public claims, move lifecycle state, create custody/
acceptance, or close `FT-0181`.

## Rev0288 due-date rule

`owner-field-next` now behaves as follows:

- before `due_or_recheck_date`: wait with `AWAIT-POST-READOUT-ACTION-RECHECK`;
- on or after `due_or_recheck_date`: emit `owner-post-readout-recheck`;
- after a valid recheck with no new owner context, complete-but-not-closure, or
  route blocked: stop live with no further archive command;
- after a valid recheck saying new owner context exists: route the **actual
  returned owner context** back through `owner-field-next`, not through the
  recheck artifact.

## Boundary

A dispatch is not a stale closure substitute. If the due date arrives, record the
recheck or stop. Do not backfill completion from the original dispatch.
