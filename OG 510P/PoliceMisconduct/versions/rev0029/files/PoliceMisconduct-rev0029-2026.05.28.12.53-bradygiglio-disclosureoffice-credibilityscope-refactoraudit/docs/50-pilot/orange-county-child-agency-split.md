# Orange County child-agency split

The DOJ SLS source row combines the Orange County District Attorney’s Office and the Orange County Sheriff’s Department. That is unsafe as a single status object.

Rev0006 adds two child status objects:

- `CHILD-STAT-REV0006-OCDA`
- `CHILD-STAT-REV0006-OCSD`

This prevents three bad collapses:

1. prosecutor-agency status flattening into sheriff status;
2. sheriff completion/closed signal overwriting OCDA enforcement/completion signals;
3. parent-row display implying a single legal state for two different agencies.

The child objects remain nonclaims.
