# Cube deep audit rev0260

## Posture

The cube remains ready-but-not-closed. `FT-0181` is still live because no real
`SRC2+` owner-reviewed packet has been received, no accepted import exists, no
live-window readout exists, and no closure signoff exists. Rev0253 made the
outbound owner request packet executable. Rev0254 made sent/re-ask/no-owner-packet
status executable. Rev0255 made scratch-state routing executable. Rev0256 made
routed owner-contact commands dated and clock-valid. Rev0257 and rev0258 made
returned-CSV source firebreaks shared across the router and direct tools. Rev0260
removed fixed returned-CSV intake and seed-output collisions. Rev0260 fixes the
next operator-stall point: contact-status outputs and `RE-ASK-ONCE` intake routes.

## Priority change

The riskiest remaining failure was not another governance gap. It was a repeated
local execution problem. The field router still emitted fixed owner-contact output
paths such as `scratch/owner-contact-status/aiedu-sr-003-sent` and
`scratch/owner-contact-status/aiedu-sr-003-reask`. Those paths were safe once, but
stale scratch from a previous run could block or confuse a later attempt. This
was especially wasteful in a long cloudtainer session where each turn re-enters
the same field lane.

Rev0260 changes router-emitted owner-contact commands to date-keyed output paths:
`aiedu-sr-003-sent-YYYY-MM-DD`, `aiedu-sr-003-reask-YYYY-MM-DD`, and
`aiedu-sr-003-no-owner-packet-YYYY-MM-DD`. The commands still pass the same
contact-clock validator, but repeated attempts no longer collide with the earlier
status artifact by default.

## Audit/refactor change

The audit target was the post-intake `RE-ASK-ONCE` branch. Before rev0260, the
router treated non-`PROCEED-STAGED` intake bundles as a generic prose route. For
`RE-ASK-ONCE`, that meant the next action was no longer a dated executable command
and could push the operator back into manual interpretation. That contradicted
the field-next design.

Rev0260 splits that branch. If the latest local intake bundle has
`triage_outcome: RE-ASK-ONCE`, `owner-field-next` now emits a runnable dated
`make owner-contact-status STATUS=reask-awaiting-reply ...` command with a fresh
three-day clock and a date-keyed output directory. Other blocking intake outcomes
still point to the local outcome note without widening the request or pretending
that a block is evidence.

## What changed in tooling

- `tools/decide_ft0181_field_next_action.py` now builds owner-contact commands
  through one helper and emits date-keyed `OUT=` directories for sent, re-ask,
  and no-owner-packet statuses.
- The router now has a distinct `SEND-ONE-BOUNDED-REASK-FROM-INTAKE` outcome for
  `RE-ASK-ONCE` intake bundles.
- `tools/check_ft0181_field_next_action.py` validates date-keyed contact outputs,
  clock-valid commands, and the new post-intake re-ask route.
- Tool manifest versions were advanced to `rev0260` so local receipts, intake
  bundles, workbench seeds, and field-next dockets identify the current release.

## Current shortest path

In a clean release extract, ask for the next action:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003
```

Prepare the packet if routed:

```bash
make owner-request-packet OUT=scratch/owner-request-packets/aiedu-sr-003-first-contact
```

After a human sends or adapts the packet, rerun the router and execute the dated
sent-clock command it emits. The command now writes to a date-keyed contact-status
output path:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003-after-send
```

If a real CSV returns, route it through the router and execute the emitted intake
command:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/ft0181-field-next-action/returned-owner-reply
```

After intake creates a local bundle, rerun the router. If the latest bundle is
`PROCEED-STAGED`, the emitted workbench-seed command uses the seed tool's
manifest-hash default output path. If the latest bundle is `RE-ASK-ONCE`, the
router emits the one allowed dated clarification-clock command.

## What is still missing

The missing object is still external: one real owner-attested eight-row CSV, or a
recorded `NO_OWNER_PACKET` after a real first-contact attempt and one bounded
follow-up. No rev0260 output is evidence. A field-next docket, packet, contact
status note, receipt, intake bundle, staging note, or workbench seed does not
upgrade source truth, support a public claim, or close `FT-0181`.

## Waste corrected or still visible

Corrected: returned-CSV intake and workbench-seed commands no longer collide on
fixed output paths, and owner-contact commands now avoid the same fixed-output
pitfall. The `RE-ASK-ONCE` intake branch no longer falls back to prose when the
field path needs a single runnable action.

Still visible: the archive remains large because branch-history and release-control
surfaces are retained. That is acceptable only while new work keeps improving the
single live field path instead of expanding doctrine. A real block is progress; a
new control surface is justified only if a real owner packet exposes a failure
that the existing router, packet, contact, receipt, intake, staging, seed,
workbench, custody, acceptance, and closeout path cannot represent.

## Validation intent

Rev0260 should pass `make lint-owner-reply`, `make lint-fast`,
`make lint-release-controls`, and `make lint-full` before packaging. The narrow
release claim is this: the cube has a router-first field path whose source,
clock, output-collision, and archive-output firebreaks are enforced by router and
direct tools; it still has no real pilot evidence and no closure basis.
