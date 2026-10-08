# Cube deep audit rev0237: post-readout action gap and next-ask minimization

## Audit question

Rev0236 made the end of a live window evidence-bearing: usage, satisfaction, or no-incident notes
could no longer become learning, safety, access, workload, compliance, or scale claims. The remaining
execution risk was one step later: a careful readout could still die as an archive artifact. A team
could record `rerun_narrower`, `continue_bounded`, `rolled_back`, or `no_change`, then proceed without
an owner, without a recheck date, and without shrinking the next evidence request.

That is real execution risk, not merely governance tidiness. If the next owner ask repeats the same
broad packet, the cube has not learned from the field. If a `continue_bounded` disposition allows new
users, dates, tools, schema fields, or public language, the live-window controls failed slowly rather
than loudly.

## What was missing

The cube had these concrete stages:

1. owner packet workbench;
2. first-packet decision board;
3. post-decision change ticket;
4. live-window stop/rollback card;
5. end-of-window readout and claim-family disposition.

It did not yet have a compact action dispatch that turns the readout into one of these owned next
moves: stop, rollback confirmed, rerun narrower, continue at the same ceiling, quarantine, no-change
trim, or return to the owner packet request.

The absence mattered most for two dispositions:

- `rerun_narrower`: without a dispatch, the next packet request can stay just as broad as the failed
  request;
- `continue_bounded`: without a dispatch, continuation can quietly become expansion.

## Rev0237 correction

Rev0237 adds `docs/30-operations/ft0181-post-readout-action-dispatch.md`, a schema, a validator, and
an example dispatch:

- `schemas/post-readout-action.schema.json`;
- `tools/check_post_readout_actions.py`;
- `examples/post-readout-actions/no-real-data-ft0181-post-readout-action.json`.

The new dispatch is intentionally narrow. It does not add another committee or approval surface. It
names the action owner, allowed actions, prohibited actions, next evidence ask, fields to re-ask,
fields to drop, public-language action, and recheck date. The checker rejects blocked readouts that
pretend to authorize real changes, source-truth upgrades, closure, or forbidden next-ask material.

## Audit/refactor performed

The lifecycle validation path now requires a `post_readout_action` reference after the
`end_window_readout` reference. This refactor makes the lifecycle row tell a complete execution story:
board decision -> change ticket -> live window -> readout -> dispatch. The dispatch must match the
readout disposition. For example-only rows, it must remain `blocked_no_real_readout`, `SRC0`, and
`blocked_no_real_packet`.

This is a small but useful refactor because it pulls the next action out of prose and into the same
machine-checkable lane as the lifecycle decision. The control plane still does not prove service
outcomes; it only prevents a readout from becoming an ownerless or overbroad next move.

## New negative fixture

Rev0237 adds `IFF10`:

`examples/import-failure-fixtures/iff-ft0181-orphaned-readout-action.json`

This fixture covers the failure where a readout exists but lacks an owner action, recheck date,
fields-to-reask/drop list, or public-language action. The expected disposition is return-to-owner, not
continuation, rerun, public change, lifecycle change, or closure.

## What still remains risky

The cube is now strong at preventing false closure from synthetic evidence, weak evidence, and broad
post-window claims. It is still gated on the same external fact: no real `SRC2+` owner packet exists.
The next practical move remains to get one minimized owner packet for one service, one owner route,
one short window, and one source system.

If another revision happens before a real packet arrives, the best use of time is not another broad
control family. The next useful work would be a field-facing owner email/form or a single filled mock
packet that uses realistic aggregate values without pretending to be real evidence, solely to test
whether the post-readout dispatch would trim the second ask.

## Boundary

Rev0237 does not close `FT-0181`, does not import real pilot evidence, does not make example records
real, and does not prove learning, safety, access, workload, compliance, or service effectiveness.
