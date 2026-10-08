# rev0292 field-execution risk burn-down

| Rank | Risk | rev0292 response |
|---|---|---|
| 1 | The first owner-contact step remains undone because packet prep is still a two-command copy/paste seam. | Added `make owner-field-work`, which runs the router, prepares the packet only when safe, reruns the router, and leaves the human-send or route-block fork visible. |
| 2 | The cube keeps producing valid local artifacts instead of owner movement. | The new mode automates only local packet prep and explicitly forbids send logs, contact clocks, intake, custody, acceptance, public support, live-window movement, and closure. |
| 3 | Maintainers respond to field friction by adding more doctrine or registries. | No schema, registry family, branch surface, or validator family was added; the refactor extends the existing router and validator. |
| 4 | A prepared packet is mistaken for evidence because it was produced by a higher-level target. | `SAFE-LOCAL-FIELD-SESSION.md`, packet manifests, and post-prep dockets all preserve `not_evidence` and `does_not_close_ft0181`. |
| 5 | Post-readout context receipt work gets weakened while first-contact friction is fixed. | The rev0290/rev0291 context receipt reroute remains unchanged: receipt is provenance/reroute only, not intake, evidence, custody, acceptance, public support, or closure. |

## Remaining live blocker

No real owner has been contacted in this release archive, no real CSV has been
received, no accepted `SRC2+` packet exists, no real live window has run, no
owner-held post-readout action has occurred, and no real post-readout context
receipt/intake cycle has occurred. `FT-0181` remains live.

## Correct next move

Use the compressed local field-work target:

```bash
make owner-field-work OUT=scratch/ft0181-field-work/aiedu-sr-003
```

After the packet is prepared, the post-prep docket should route to either a
human send/adaptation followed by `owner-send-log`, or a local `owner-route-block`
if no accountable owner route exists. Do not add another control surface unless
a real returned packet breaks the current lane.
