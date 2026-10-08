# Cube deep audit rev0258

## Posture

The cube is still ready-but-not-closed. `FT-0181` remains live because there is
no real `SRC2+` owner-reviewed packet, no accepted import, no live-window
readout, and no closure signoff. Rev0253 made the outbound owner request packet
executable. Rev0254 made sent/re-ask/no-owner-packet status executable. Rev0255
made scratch-state routing executable. Rev0256 made routed owner-contact
commands dated and clock-valid. Rev0257 blocked archive-controlled or copied
smoke CSVs at the returned-CSV router. Rev0258 makes that source firebreak
router-independent.

## Priority change

The next risk was not another missing registry. It was an optionality gap: the
safe path said to use `make owner-field-next CSV=...`, but ordinary direct tools
still had their own partial source classification. Downstream smoke guards were
strong, yet a maintainer could bypass the router and ask receipt, intake, or
staging to look at a CSV under a controlled archive path. Most such cases would
not become accepted evidence, but they could still waste review time or create
local artifacts that appear to be part of the field path.

Rev0258 changes that boundary:

- `tools/ft0181_field_guards.py` now exposes shared returned-owner source
  blocking and source-truth classification helpers;
- `tools/triage_owner_reply_csv.py` blocks archive-controlled CSV sources as
  `BLOCK-EVIDENCE` with `source_truth_class: SRC0-CONTROLLED-ARCHIVE`;
- `tools/receipt_owner_reply_csv.py`, `tools/intake_owner_reply_csv.py`, and
  `tools/stage_owner_reply_csv.py` now block controlled returned-CSV sources
  before receipt, bundle creation, or staging;
- the explicit `SRC0-SMOKE` path remains available only for the smoke harness;
- `tools/record_ft0181_owner_contact_status.py` and the generated packet
  manifest now route returned CSVs and clock follow-up through
  `make owner-field-next` instead of preserving direct intake or stale placeholder
  commands;
- `tools/decide_ft0181_field_next_action.py` now recommends router-first handling
  while a contact clock is open, so a returned CSV goes through the same source
  firebreak before intake.

This is forward progress because it makes the real field path harder to misuse
without adding another policy layer. The operator still has one command to ask
for the next action, and the direct tools now refuse the same bad sources if the
operator skips that command.

## Audit/refactor change

The refactor target was duplicated source classification. Before this revision,
the router, triage, receipt, and staging paths each had partly overlapping ideas
of `fixture`, `smoke`, `controlled archive source`, and `real local field input`.
Rev0258 moves the common returned-owner source boundary into
`tools/ft0181_field_guards.py` and adds validators that exercise both router and
direct-command paths.

The important audit result: source firebreaks are now not dependent on operator
obedience to one preferred route. The preferred route is still router-first, but
direct triage, receipt, intake, and staging no longer treat archive-owned CSV
surfaces as plausible returned owner packets.

## What is still missing

The missing object is still external: one real owner-attested eight-row CSV, or a
recorded `NO_OWNER_PACKET` after a real first-contact attempt and one bounded
follow-up. The shortest current path is:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003
make owner-request-packet OUT=scratch/owner-request-packets/aiedu-sr-003-first-contact
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003-after-send
```

If a real CSV returns, route it through the router first and execute only the
emitted command:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/ft0181-field-next-action/returned-owner-reply
```

After intake creates a local bundle, rerun the router. It emits the workbench
seed command only when the latest bundle is `PROCEED-STAGED`:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/after-intake
```

If the first response clock lapses, rerun `make owner-field-next`; it emits a
valid dated re-ask status command. If the second clock lapses, rerun it again; it
emits a valid dated `NO_OWNER_PACKET` status command. A real block is progress. A
pretend import is not.

## Waste corrected or still visible

Corrected: returned-owner source blocking no longer lives only in the router.
The packet send checklist, packet manifest, and contact status manifest now send
operators back through `owner-field-next` instead of preserving direct intake,
workbench-seed, or placeholder contact-clock shortcuts.

Still visible: the archive has many branch-history and release-control surfaces.
They remain indexed and mostly harmless, but new revisions should not add another
long control surface unless a real owner packet exposes a failure that the
existing field-next, packet, contact, intake, receipt, re-ask, block, staging,
seed, workbench, custody, acceptance, and closeout path cannot represent.

## Validation intent

Rev0258 should pass `make lint-owner-reply`, `make lint-fast`,
`make lint-release-controls`, and `make lint-full` before packaging. The narrow
release claim is this: the cube has a router-first field path whose source
firebreak is enforced by direct triage, receipt, intake, staging, and router
commands; it still has no real pilot evidence and no closure basis.
