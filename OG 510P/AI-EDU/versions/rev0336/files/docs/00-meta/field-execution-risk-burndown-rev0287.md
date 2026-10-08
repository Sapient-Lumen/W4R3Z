# rev0288 field-execution risk burn-down

| Rank | Risk | rev0288 response |
|---|---|---|
| 1 | A terminal live-window readout becomes silent service expansion or public language. | Added `owner-post-readout-action` and a guard that converts the readout to one bounded action/recheck lane only. |
| 2 | A copied or edited dispatch references the wrong readout. | The dispatch records and revalidates the source readout path, SHA-256 hash, disposition, source-truth class, and non-closure state. |
| 3 | A `continue_bounded` readout quietly expands cohort/date/tool/scope. | Dispatch requires `no_expansion_confirmation` and a lane-specific owner action class; router stops after dispatch. |
| 4 | A `rerun_narrower` or `no_change` readout repeats the same broad ask. | Dispatch requires field-drop counts; rerun requires a bounded re-ask count. |
| 5 | The archive keeps growing doctrine rather than completing the field path. | The next move is executable: packet/send/reply/decision/activation/live/readout/dispatch. After dispatch, no more archive field command exists without new owner context. |

## Remaining live blocker

No real owner has been contacted in this cloudtainer session, no real CSV has been received, no accepted `SRC2+` packet exists, and no real live-window readout exists. `FT-0181` remains live.
