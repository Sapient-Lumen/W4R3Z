# Official voter-information web push surface checklist

Use this checklist when an election office offers **browser-origin web push notifications** for public voter-information routes after an explicit opt-in.

## Scope and optionality review

- [ ] Record which voter-information routes or alert classes may use browser-origin web push.
- [ ] Distinguish browser-origin web push from generic social/broadcast alerts, permission-prompt review, native mobile-app notifications, or installed-web-app shell identity.
- [ ] Keep web push explicitly optional and preserve the ordinary current official page/help lane for users who never subscribe, later unsubscribe, or lose subscription state.

## Opt-in and lifecycle review

- [ ] Review whether public copy tells the truth about permission state, subscription state, and the fact that subscriptions may expire, be revoked, or otherwise change outside the office’s control.
- [ ] Keep a clear unsubscribe or settings/help path for each reviewed subscription entrypoint.
- [ ] Do not describe browser-origin web push as guaranteed receipt across browsers, devices, or time.
- [ ] Re-check any route whose browser/platform support or rate-limit posture changes materially.

## Message and landing-path review

- [ ] Review whether each notification class points back to a current, durable, official landing route rather than to a brittle or stale deep link.
- [ ] Review cold-open behavior from a notification click when the original tab no longer exists.
- [ ] Keep the notification body subordinate to the current page/help lane when the message alone is not enough to act safely.
- [ ] Verify that secret-bearing, personalized, or highly stateful routes are not used as public notification landing targets.

## Stale / superseding review

- [ ] Review replacement, grouping, expiration, or correction posture for time-sensitive notification classes.
- [ ] Review whether a delayed or stale notification can still be visible after hours, locations, deadlines, or operational status changed.
- [ ] Keep a fail-open path from stale alerts back to the current official page/help lane.
- [ ] Do not let corrected or superseded notifications quietly masquerade as the current official rule.

## Evidence and minimization review

- [ ] Preserve a small public digest of reviewed notification classes, landing-route posture, lifecycle posture, superseding posture, and last review time.
- [ ] Do not preserve raw push endpoints, individualized delivery/open telemetry, or subscriber-level histories merely to prove that web push was reviewed.
