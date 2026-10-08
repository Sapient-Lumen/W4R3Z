# Official voter-information timeout recovery surface checklist

Use this quickcheck when an election office needs a bounded way to keep official voter-information routes workable when inactivity timers, security expirations, or other time limits can interrupt the task before completion.

## Inventory and review scope

- Identify public routes where inactivity or another time limit can interrupt progress before the voter reaches the answer, review state, or final confirmation.
- Distinguish this from generic multi-step review, post-submit confirmation, low-connectivity degradation, or public-read sign-in boundaries.
- Re-check routes where voters commonly need time to look up an address, ID, witness detail, upload, or deadline-related document.

## Timeout disclosure and warning posture

- State early in the route whether an inactivity timeout or other bounded time limit exists and how long it is.
- Say whether entered work, uploaded files, and current step/context are preserved, partially preserved, or lost after expiry.
- Where the time limit remains, warn before expiry in accessible text and provide a simple extension action when that posture is practical.
- Do not rely on a last-second toast, pointer-only gesture, or hard-to-read modal as the only timeout warning.

## Preservation and expiry recovery

- Preserve current task state whenever law, privacy, and security posture allow it; if full preservation is impossible, say so before the risky stage begins.
- When re-authentication is required, restore the user to the prior task state when feasible instead of dropping them onto a blank first step.
- Make the expired-state page explain what happened, what was kept, what was lost, and whether the voter should resume, restart, or use help.
- Clarify submit uncertainty when timeout occurs near a final action so voters do not create duplicates by guessing.

## Accessibility and reviewability

- Keep timeout disclosures, extension controls, and expired-state recovery text reviewable on mobile, at zoom, with keyboard navigation, and with screen readers.
- Ensure the extension action does not depend on hover-only, drag-only, or last-second choreography.
- Expose important warning and expiry updates in accessible text rather than only through decorative countdown chrome.
- Test timeout and recovery behavior in project context, not just the nominal happy path.

## Evidence posture

- Preserve only route labels, reviewed timeout paths, timeout/extension/preservation review state, and last review time.
- Do not preserve real voter drafts, session identifiers, resume secrets, exhaustive inactivity telemetry, or replayable per-user timelines when bounded policy reconstruction is sufficient.
