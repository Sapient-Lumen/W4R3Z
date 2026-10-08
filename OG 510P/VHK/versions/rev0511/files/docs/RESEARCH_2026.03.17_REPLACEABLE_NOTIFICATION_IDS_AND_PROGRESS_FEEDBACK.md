# Research — replaceable notification ids and progress-feedback loops

## Takeaway

The Linux notification stack already has a real contract for replaceable progress/status toasts. VHK should treat notification ids as first-class runtime data instead of pretending every `Notify` call is a disposable one-shot popup.

## What we learned

- The freedesktop Desktop Notifications spec defines `replaces_id` directly in the `Notify` call and says the returned value is the new notification id, or the same id when an existing notification is replaced.
- Current `notify-send` supports app name, actions, urgency, timeout, icon, category, `--print-id`, `--replace-id`, and `--transient`.
- Current `dunstify` supports app name, urgency, hints, actions, timeout, icon, category, `--printid`, and `--replace`, and Dunst documentation still treats the `transient` hint as meaningful client-side input.

## Product implication

VHK should let macros:

1. emit a notification and keep the returned id
2. feed that id into later `Notify` steps for atomic replacement/update
3. preserve app/category/icon/timeout/transient intent as reviewable macro data instead of hiding it in shell glue

That keeps the ownership split clean:

- the notification daemon owns display, persistence, and action presentation
- VHK owns macro orchestration and the reviewed notification semantics

## Honest gap

Actions are still the next hard boundary. The freedesktop spec defines `ActionInvoked` and `NotificationClosed` signals, and modern `notify-send`/`dunstify` expose action-related CLI surfaces, but VHK still needs a clean cross-daemon model for selected actions, close reasons, and capability-aware fallbacks.
