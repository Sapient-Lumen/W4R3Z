# rev0294 field execution risk burndown

## Current burn-down table

| Risk | rev0294 treatment | Remaining boundary |
|---|---|---|
| Packet prep stalls before first contact | `owner-field-work` prepares the first-contact packet locally | Human must send/adapt or route-block |
| Post-send bookkeeping is missed | `owner-after-human-send` records send log plus active clock | It cannot prove delivery or owner receipt |
| Returned CSV stalls before workbench seed | `owner-returned-reply-work` runs intake and seeds only `PROCEED-STAGED` bundles | It cannot perform human review or accept evidence |
| Non-proceed replies get laundered into progress | New helper stops non-proceed outcomes at the intake note | Re-ask/block/no-owner routes remain bounded |
| Post-readout context bypasses receipt | Router still requires context receipt before returned-reply work | Receipt is provenance only, not intake or evidence |
| Doctrine growth substitutes for field work | Re-entry docs now point to executable commands first | New surfaces require a real packet failure mode |

## Next real action

If no packet has been prepared, run:

```bash
make owner-field-work OUT=scratch/ft0181-field-work/aiedu-sr-003
```

If a real returned owner CSV exists, do not run direct intake. Run the router:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv \
  OUT=scratch/ft0181-field-next-action/returned-owner-reply
```

Then execute only the emitted `owner-returned-reply-work` command.

## Stop rule

Do not add a new registry or lint because the returned reply is missing,
non-proceeding, overbroad, protected, security-sensitive, or ambiguous. Use the
existing bounded route: outcome note, one re-ask, route block, or keep `FT-0181`
live without closure.
