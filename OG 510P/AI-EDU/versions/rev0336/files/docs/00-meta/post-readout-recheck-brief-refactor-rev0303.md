# rev0303 post-readout recheck brief refactor status

`rev0303` preserves the `rev0302` post-readout recheck brief. No new recheck,
context receipt, intake, evidence, custody, service-record, public-claim,
lifecycle, or closure authority is added.

The due-date bridge still does one job: after a human-recorded post-readout action
dispatch reaches `due_or_recheck_date`, `owner-field-work` may prepare a minimized
post-readout recheck brief. A human must still choose and record exactly one
bounded recheck outcome before any context receipt or later intake path exists.

The rev0303 change is upstream of that bridge: the field router now ignores
checker/test scratch artifacts so a synthetic lint fixture cannot impersonate a
post-readout or workbench state and pull the operator away from the real next field
action.
