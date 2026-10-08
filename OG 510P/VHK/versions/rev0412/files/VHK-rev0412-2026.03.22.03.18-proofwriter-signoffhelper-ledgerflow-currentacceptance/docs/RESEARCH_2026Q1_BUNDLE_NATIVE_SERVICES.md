# Research — bundle-native session services

This note captures the practical lessons behind VHK's bundle-state service
runner direction.

## Why explicit service directories matter

A Linux user service that needs helper scripts, extracted bundle state, and a
small amount of cache should name those roots directly instead of depending on a
checkout path or implicit shell cwd. That makes the runner understandable,
reviewable, and easier to rehearse.

## Why a bundle-state runner is better than a checkout-root runner

VHK already knows how to stage, bundle, publish, install, and optionally embed a
runtime. Letting the long-lived watcher plane ignore all of that and run from
the mutable repo checkout breaks the most important release truth in the tree:
*ship what was reviewed*.

The bundle-state runner is a conservative compromise:

- keep the reviewed zip as the source artifact
- materialize it into owned state when the service starts
- run `vhk busd` against that extracted project root
- keep helper daemons, portals, and raw-input permissions explicit as adjacent
  lifecycle concerns

## Related patterns worth borrowing

- systemd user services are strongest when configuration, state, and cache roots
  are explicit rather than smuggled through login shell assumptions
- pipx-style app installs reinforce the value of one isolated app/runtime root
  plus one exposed entrypoint instead of a mutable checkout as the product
- together they point toward a simple Linux-native rule for VHK: reviewed
  payloads first, helper boundaries explicit, and long-lived services rooted in
  owned per-user directories
