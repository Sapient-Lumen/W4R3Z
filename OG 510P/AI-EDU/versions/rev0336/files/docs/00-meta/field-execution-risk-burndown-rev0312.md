# rev0312 field execution risk burndown

| Risk | rev0312 control | Residual boundary |
|---|---|---|
| Handoff lists obsolete lint commands and wastes the operator's next session. | `check_operator_handoffs.py` rejects `--mode` and requires the four current `--lane` commands. | The validator proves command shape, not that a human will run the commands. |
| Handoff skips the router and advertises dense downstream actions. | `allowed_next_actions` must include only the router/report-first actions and is checked for direct owner/import/closeout bypass terms. | A human still must execute only the emitted router command. |
| Root re-entry docs drift away from field work and back into doctrine. | `check_reentry_navigation.py` now requires the field-work, field-report, and CSV-router commands in root startup docs and blocks obsolete `--mode` syntax. | Root docs remain navigation only; they do not create owner evidence. |
| Release-control examples imply field completion. | Existing rev0311 public/closure guards remain in force. | No real owner packet, readout, context cycle, closeout, or signoff exists. |
| More docs substitute for owner contact. | This pass adds only focused audit notes and executable handoff checks. | The real next move is still `make owner-field-work` or a router-mediated returned CSV path. |
