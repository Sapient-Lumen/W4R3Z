# Research — daemonized helper lanes and uinput service boundaries

## Question

What should VHK learn from current Linux input-helper tools beyond the already
documented “helper boundary” idea?

## Takeaway

The fresh lesson is that repeated helper-backed playback is usually not just a
command-line binary choice. It is a **deployment lane** with at least four
reviewable edges:

- helper family choice (`dotoold`/`dotoolc` vs `ydotoold`)
- user-service lifecycle
- socket ownership/path
- `/dev/uinput` policy

That is a stronger product lesson than “some helper exists.”

## Why this matters for VHK

VHK already had the low-level pieces:

- helper-aware setup recipes
- host/readiness packs that reason about uinput and sockets
- service generators for `dotoold` and `ydotoold`

But the main planner still made it too easy to think in vague helper terms. For a
Linux-native AHK analogue, that is not honest enough. The user experience of a
helper lane depends on whether a persistent virtual device is kept alive, where
the socket lives, and whether the host contract allows the helper to talk to
`/dev/uinput`.

## Product conclusion

So the planner should expose a persistent helper lane directly:

- candidate surface: `uinput-helper-daemon`
- reference pattern: `daemonized-uinput-helper-lane`
- ecosystem lesson: `daemonized-helper-lifecycle`

This keeps the hierarchy clear:

1. package/clipboard exports are the broad portable text lane
2. `wtype` is the narrow virtual-keyboard fast lane
3. daemonized uinput helpers are the repeated-playback fallback/escape lane

Those are not redundant. They are different product surfaces with different
operator costs.
