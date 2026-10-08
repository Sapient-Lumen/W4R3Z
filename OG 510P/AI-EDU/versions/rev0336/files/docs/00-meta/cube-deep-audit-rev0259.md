# Cube deep audit rev0259

## Posture

The cube remains ready-but-not-closed. `FT-0181` is still live because there is
no real `SRC2+` owner-reviewed packet, no accepted import, no live-window
readout, and no closure signoff. Rev0253 made the outbound owner request packet
executable. Rev0254 made sent/re-ask/no-owner-packet status executable. Rev0255
made scratch-state routing executable. Rev0256 made routed owner-contact
commands dated and clock-valid. Rev0257 and rev0258 made returned-CSV source
firebreaks shared across the router and direct tools. Rev0259 removes two more
operator-stall risks: fixed scratch output collisions and nonscratch archive
output leakage.

## Priority change

The riskiest remaining failure was small but practical. The field router could
recommend direct local intake or workbench-seed commands with fixed output
directories such as `scratch/owner-reply-intakes/aiedu-sr-003` and
`scratch/owner-reply-workbench-seeds/aiedu-sr-003`. That was runnable once, but
it was a poor field path for retries, multiple returned CSVs, or repeated local
checks. A maintainer could collide with a stale directory or mix old local files
into a new decision path.

Rev0259 changes the router so returned CSV intake and workbench seed commands use
the tools' digest-keyed default output directories. The emitted commands now let
`tools/intake_owner_reply_csv.py` and `tools/seed_owner_packet_workbench.py`
derive stable paths from the actual source content or bundle manifest. This is
not new evidence, but it makes the real field path harder to stall and easier to
repeat safely.

## Audit/refactor change

The refactor target was output-boundary drift. Packet prep, owner-contact status,
and the field router already used `tools/ft0181_field_guards.py`, while receipt,
intake, staging, and workbench-seed still had small local copies of archive-output
checks. Those copies blocked obvious controlled directories such as `docs/` and
`fixtures/`, but they did not share one rule for nonscratch archive paths.

Rev0259 moves those direct receipt/intake/staging/seed output checks onto the
shared guard. The guard now allows only `scratch/` or paths outside the archive
for local execution outputs. Any nonscratch path inside the release archive is
blocked, including otherwise unregistered top-level folders that `package_release`
would include by default. This closes a packaging-leakage class without adding a
new registry or surface family.

## What changed in tooling

- `tools/decide_ft0181_field_next_action.py` no longer emits fixed `OUT=...`
  directories for returned CSV intake or workbench seeding.
- `tools/ft0181_field_guards.py` now treats nonscratch in-archive local outputs
  as blocked, not merely unregistered.
- `tools/receipt_owner_reply_csv.py`, `tools/intake_owner_reply_csv.py`,
  `tools/stage_owner_reply_csv.py`, and `tools/seed_owner_packet_workbench.py`
  now use the shared output guard.
- `tools/check_ft0181_field_next_action.py`,
  `tools/check_owner_reply_receipt.py`,
  `tools/check_owner_reply_intake_bundle.py`,
  `tools/check_owner_reply_staging.py`, and
  `tools/check_owner_reply_workbench_seed.py` now exercise the digest-output and
  nonscratch-output leakage cases.

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
sent-clock command it emits:

```bash
make owner-field-next OUT=scratch/ft0181-field-next-action/aiedu-sr-003-after-send
```

If a real CSV returns, route it through the router and execute the emitted
command. The emitted intake command now uses the intake tool's digest-keyed
default output path:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/ft0181-field-next-action/returned-owner-reply
```

After intake creates a local bundle, rerun the router. If the latest bundle is
`PROCEED-STAGED`, the emitted workbench-seed command uses the seed tool's
manifest-hash default output path.

## What is still missing

The missing object is still external: one real owner-attested eight-row CSV, or a
recorded `NO_OWNER_PACKET` after a real first-contact attempt and one bounded
follow-up. No rev0259 output is evidence. A field-next docket, packet, contact
status note, receipt, intake bundle, staging note, or workbench seed does not
upgrade source truth, support a public claim, or close `FT-0181`.

## Waste corrected or still visible

Corrected: fixed local output directories and duplicated output guards are no
longer places for silent drift. The package boundary now matches the field-output
boundary: local execution artifacts belong in `scratch/` or outside the archive,
not in any nonscratch release path.

Still visible: the archive remains large because branch-history and release-control
surfaces are retained. That is acceptable only if new work keeps improving the
single live field path instead of expanding doctrine. A real block is progress; a
new control surface is justified only if a real owner packet exposes a failure
that the existing router, packet, contact, receipt, intake, staging, seed,
workbench, custody, acceptance, and closeout path cannot represent.

## Validation intent

Rev0259 should pass `make lint-owner-reply`, `make lint-fast`,
`make lint-release-controls`, and `make lint-full` before packaging. The narrow
release claim is this: the cube has a router-first field path whose source and
output firebreaks are enforced by router and direct tools; it still has no real
pilot evidence and no closure basis.
