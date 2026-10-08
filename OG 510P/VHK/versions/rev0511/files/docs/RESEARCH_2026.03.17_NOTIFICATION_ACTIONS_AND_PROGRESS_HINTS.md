# Research — notification actions and progress hints

## Takeaway

Linux desktop notifications are more than fire-and-forget toasts. Current CLI surfaces already expose two important contracts VHK can preserve directly:

1. replaceable/progress feedback
2. daemon-owned action prompts

## What we learned

- modern `notify-send` supports action buttons, wait semantics, `--print-id`, `--replace-id`, and generic typed hints
- modern `dunstify` supports action buttons, typed hints, replaceable ids, and a blocking mode that prints feedback to stdout
- Dunst documents the `int:value` hint as the progress-bar path for volume/brightness-style notifications
- Dunst also documents action ids as stdout-visible choices, which makes them a plausible low-friction runtime feedback lane

## Product implication

VHK should let macros keep this data declarative instead of shell-escaping it into one-off helper scripts. In practice that means:

- `Notify.progress` for progress/value hints
- `Notify.actions[]` for daemon-owned action ids and labels
- `Notify.out_action` for the selected action id when the backend can return one

That keeps the ownership split honest:

- the daemon owns presentation, interaction chrome, history, and close semantics
- VHK owns orchestration, branching, and reviewed action meaning

## Honest gap

This still does not mean all notification daemons behave identically. Remaining hard edges include:

- close reasons and timeout behavior differing by daemon/desktop
- action support that may exist in CLI tools but not feel identical across shells/desktops
- portal notification APIs that intentionally narrow the contract compared with session-daemon CLIs
