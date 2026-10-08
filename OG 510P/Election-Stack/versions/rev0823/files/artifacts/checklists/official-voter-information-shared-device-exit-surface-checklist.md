# Official voter-information shared-device exit surface checklist

Use this quickcheck when an election office needs a bounded way to keep personalized or sensitive voter-information routes safe to leave on shared, borrowed, or public devices.

## Inventory and review scope

- Identify routes that expose personalized or sensitive voter-specific state, such as status dashboards, saved applications, or notification/account views.
- Distinguish this from ordinary public-read pages, timeout recovery, and post-submit confirmation posture.
- Re-check routes likely to be used on borrowed, family-shared, library, school, shelter, or clinic devices.

## Sign-out and safe-exit clarity

- Keep a visible sign-out or safe-exit action wherever personalized voter-specific state is exposed.
- Do not assume that closing the tab or navigating away is an adequate privacy control.
- Make it clear when the session has actually ended.
- Provide one clear next action if the voter still needs official help after exiting.

## Shared-device and local-data posture

- Acknowledge shared/public-device risk where it materially affects the route.
- Review whether logout ends only the authenticated session or also clears relevant local browser state.
- If save/resume or remembered state exists, explain that persistence boundary clearly enough for shared-device use.
- Do not let private status, draft, or history views silently reopen for the next device user without an intentional sign-in or recovery step.

## Accessibility and reviewability

- Keep sign-out, safe-exit, and shared-device guidance available in accessible text on mobile, at zoom, with keyboard navigation, and with screen readers.
- Do not rely only on a profile icon, hidden menu, hover disclosure, or tiny chrome control for the privacy-critical exit path.
- Make sure the finishing/exit moment is reviewable in project context, not only the happy-path account home page.
- Test the route after logout or safe exit to confirm the next visible state matches the promised privacy posture.

## Evidence posture

- Preserve only route labels, reviewed exit/clear paths, sign-out visibility review state, local-clearing review state, resume-privacy review state, and last review time.
- Do not preserve real cookies/tokens, local-storage dumps, browser histories, downloaded personal confirmations, or per-user session-end telemetry when bounded policy reconstruction is sufficient.
