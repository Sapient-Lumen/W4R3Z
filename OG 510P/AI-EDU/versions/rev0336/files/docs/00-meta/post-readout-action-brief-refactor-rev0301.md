# rev0301 post-readout action brief refactor

## What changed

`rev0301` compresses the next risky seam in `FT-0181`: after a human records a
terminal aggregate live-window readout, the archive previously emitted a dense
post-readout dispatch command directly. That command was safe, but it was still a
high-drop-off point because it mixed lane choice, due/recheck date, owner-action
class, next ask class, public-language action, and no-service/no-closure
firebreaks in one line.

New helper:

```bash
make owner-post-readout-action-brief   READOUT=scratch/.../live-window-readout.json
```

`make owner-field-work` may now safely prepare this brief when the router selects
`PREPARE-POST-READOUT-ACTION-BRIEF`. It reruns the router and stops at the
human-owned dispatch boundary.

## What the brief does

The brief validates only a scratch-local terminal `live-window-readout.json` and
maps its disposition to exactly one bounded dispatch lane:

| Readout disposition | Dispatch lane |
|---|---|
| `stopped` | `stop` |
| `rolled_back` | `rollback_confirmed` |
| `continue_bounded` | `continue_same_ceiling` |
| `rerun_narrower` | `rerun_narrower` |
| `quarantine` | `quarantine` |
| `no_change` | `no_change_trim` |

It writes a one-screen handoff with the `owner-post-readout-action` command
skeleton, a proposed seven-day due/recheck date, lane-matched owner-action class,
next-ask class, public-language action, source readout hash, reviewer-role
minimum, and all no-expansion/no-public/no-service/no-lifecycle/no-closure flags.

## Boundary

The brief is not a post-readout action dispatch. It is not owner-action
completion, a recheck, post-readout context receipt, evidence, SRC2+ acceptance,
custody evidence, public-summary support, lifecycle movement, service-record
mutation, or closure.

The refactor reduces operator drop-off at the point where a real readout must
become a bounded dispatch before any owner-held action lane or recheck clock can
start.
