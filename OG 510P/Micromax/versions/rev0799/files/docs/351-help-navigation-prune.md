# Explicit prune for blocked local docs history

Rev408 deliberately kept stale missing-doc session/back/forward targets visible as
local witnesses. That was the right trust move: Micromax should not silently eat
history just because a docs file disappeared.

But one operator seam still remained: once a missing target sat at the head of the
session, back, or forward lane, the editor could name the blocker yet gave no exact
local disposition for clearing that stale head and continuing along deeper ready
history.

Rev409 keeps that follow-up deliberately small:

- `helpprune` / `ed.help-prune` prune only missing session/back/forward targets
- ready targets stay untouched
- `status_model()` / `help_navigation_model()` expose `help_prune_available`,
  `help_prune_count`, and `help_prune_command`
- plain `help_actions=` now names `helpprune` when blocked history is reviewable
  but cleanup is the next honest step

The goal is simple: blocked docs history should stay witnessable until the user
explicitly prunes it, not stay stuck behind a stale missing head forever.
