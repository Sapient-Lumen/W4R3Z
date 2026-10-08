# Official voter-information processing / wait-state surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable while a lookup, request, or submission is still processing and the final outcome is not yet ready.

## Inventory and review scope

- Identify public routes where a voter can be held in an in-session processing, waiting, or queued state after taking an action.
- Distinguish this from blank-shell degradation, overload/waitroom posture, post-submit confirmation, or inactivity-timeout recovery.
- Re-check routes where deadline pressure makes duplicate clicks, refresh panic, or abandoned waiting especially risky.

## Waiting-state clarity

- State in ordinary language whether the route is processing now, waiting for a response, queued, or unable to finish.
- Do not rely on animation alone to communicate that the system is working.
- Use a determinate progress indicator only when the route can describe real progress; otherwise use an honest indeterminate waiting state.
- Batch multi-part updates into a coherent status change instead of announcing incomplete fragments.

## Duplicate-action prevention and long-wait recovery

- Make clear whether the original action is still in flight and whether repeating it could duplicate work.
- Bound the posture for refresh, back navigation, reopen, or multi-click retry while the request is still unresolved.
- Provide a visible next step when the wait stops being ordinary: keep waiting, retry after visible failure, use a status path, or switch to office help.
- Ensure long-wait recovery matches the underlying substantive surface and any confirmation/timeout posture.

## Accessibility and reviewability

- Keep waiting-state, progress, and completion/failure messages available in accessible text on mobile, at zoom, with keyboard navigation, and with screen readers.
- Do not steal focus merely because the route is busy.
- Expose meaningful in-flight updates as status messages rather than forcing users to hunt for a hidden spinner label.
- Test the waiting state in project context, not just the final confirmation page.

## Evidence posture

- Preserve only route labels, reviewed wait-state paths, progress/duplicate-action/long-wait review state, and last review time.
- Do not preserve real voter submissions, queue tokens, session secrets, per-user timing logs, replayable sessions, or back-end worker internals when bounded policy reconstruction is sufficient.
