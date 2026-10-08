# Official voter-information browser-permission surface checklist

Use this quickcheck when an election office needs a bounded way to keep geolocation, notifications, camera/microphone, clipboard, or similar permission-gated helpers from blocking the public answer lane.

## Inventory and classification

- Identify the critical public-answer routes that invoke browser or device permissions.
- Classify which capabilities are involved (for example geolocation, notifications, camera, microphone, clipboard, or share helpers).
- Keep this separate from sign-in walls, CAPTCHA/challenge walls, and ordinary first-load overlays.

## Prompt timing and explanation

- Confirm that permission prompts follow a clear user action rather than page load.
- Explain in plain language what the capability helps the voter accomplish.
- Do not fire a browser prompt just because the API exists on the device.

## Public-read boundary and fallback

- Confirm that a voter can still read the current official answer and reach the ordinary help lane without granting a capability.
- Keep manual/list/browse/help fallbacks visible when the capability is denied, blocked, unsupported, or policy-restricted.
- Treat denied or unavailable capability states as normal public states, not as hard errors.

## Notification and geolocation discipline

- Do not request notification permission on page load.
- Keep reminder or alert opt-in behind a deliberate enable/settings action.
- For geolocation helpers, preserve visible manual address, ZIP, or browsable-list alternatives.

## Policy and dependency boundaries

- Review Permissions-Policy and embed boundaries for routes that use powerful capabilities.
- Avoid letting a third-party widget or embedded frame become the main reason a browser/device prompt appears.
- Re-check the route with the capability denied and with supporting code or embeds blocked.

## Evidence posture

- Preserve only route labels, capability classes, public-read boundary state, prompt-timing state, fallback/fail-open state, notification-boundary state, permissions-policy scope state, and last review time.
- Do not preserve raw permission-event telemetry, device identifiers, precise location histories, notification subscription endpoints, or media captures when bounded policy reconstruction is sufficient.
