# Scenario — material-change triggers define an explicit revalidation window

A maintainer-authored upgrade pack can have exact source heads, a frozen public surface, and an honest warning register while still becoming stale or expired when the underlying lane changes.

This scenario demonstrates that the pack should declare, in advance:

- which review clock turns a pack from `current` into `stale_but_usable` or `expired`,
- which material changes immediately invalidate a previously frozen/public pack,
- and whether a newer current pack automatically supersedes an older one.
