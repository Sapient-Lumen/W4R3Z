# Research — Notification feedback lanes and session-service boundaries

## Takeaway

A Linux-native automation stack should treat passive desktop feedback as a session-service contract before it treats it as just another prompt or log line.

## What we learned

- The freedesktop desktop notifications spec defines one session-scoped D-Bus service for passive notifications, optional actions, and close signals.
- Dunst and `dunstctl` show that notification daemons can become a real operator surface with history, actions, rules, and runtime control instead of being disposable popups.
- The XDG Notification portal is intentionally narrower: sandboxed applications can send and withdraw notifications, but they should not expect round-trip visibility into whether a toast was actually shown.

## Product implication

`plan-project` should surface a dedicated notification feedback lane whenever the project already emits `Notify` steps or waits on `org.freedesktop.Notifications` signals. The right architecture is:

1. the session notification service / daemon owns presentation, history, and optional action signaling
2. VHK owns macro orchestration, prompts, diagnostics, and the larger action catalog
3. modal prompts remain for blocking input, while passive notification feedback stays a separate surface

## Honest gap

Planning is ahead of deployment here too: VHK now recognizes the lane, but `Notify` is still a thin wrapper. Replace ids, action ids, and richer reviewable notification artifacts still need explicit product work.
