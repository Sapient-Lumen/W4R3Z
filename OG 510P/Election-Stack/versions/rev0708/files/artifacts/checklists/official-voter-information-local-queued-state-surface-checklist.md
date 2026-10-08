# Official voter-information local-only / queued state surface checklist

Use this quickcheck when an election office needs a bounded way to keep browser/app/device-local progress, queued send/repair, and actual office acknowledgment from collapsing into one misleading status.

## Inventory and review scope

- Identify public routes that may save meaningful progress locally, queue later send/repair, or show optimistic progress before the office has actually accepted the action.
- Distinguish this from generic low-connectivity review, generic confirmation review, or later pending-review/status governance.
- Re-check routes where weak connectivity, background operation, or restart/device-change pressure makes local-only or queue-pending state plausible.

## State-class honesty

- Keep local-only state, queued/repair-pending state, and office-acknowledged state visibly distinct when those differences matter.
- Do not label a device-local draft, browser save, or volatile optimistic clear as though it were an official receipt.
- Do not let queued-for-send or background-repair posture skip directly to “submitted” or “received” language unless the authoritative service has actually acknowledged acceptance.
- Ensure any locally generated token, reference, or draft marker is not mistaken for office-side acceptance.

## Continuity, retry, and follow-up

- Preserve enough continuity after restart, hidden return, or resume that the voter can still tell what kind of state previously existed.
- Make retry guidance depend on the true state class: local resume, queue reattempt, duplicate-risk boundary, or already-landed/no-retry-needed.
- Keep one visible authoritative status/help lane for cases where device-local or queue-pending state has not yet become office-side truth.
- Ensure portable records or save/print artifacts distinguish device-local state from actual office acknowledgment.

## Accessibility and reviewability

- Keep the state-class cues available in accessible text rather than only in icons, color chips, or transient UI.
- Ensure local-only, queue-pending, and office-acknowledged transitions remain understandable on mobile, at zoom, with keyboard navigation, and with screen readers.
- Test restart/return continuity in project context instead of assuming optimistic UI alone is sufficient.
- Verify that weak-network or resume behavior does not silently rewrite local or queued state into fake confirmed state.

## Evidence posture

- Preserve only route labels, reviewed state-transition paths, state-class visibility posture, retry/follow-up posture, restart/return continuity posture, and last review time.
- Do not preserve per-user sync-event histories, service-worker debug logs, device identifiers, raw draft contents, or exhaustive replay traces when bounded policy reconstruction is sufficient.
