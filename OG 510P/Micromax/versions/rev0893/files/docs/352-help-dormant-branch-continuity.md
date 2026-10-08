# Dormant help state should still branch like current help state

Rev406 made the current docs target explicit even after leaving the help buffer:
Micromax kept one tiny dormant session-local target and `helpresume` could reopen
it honestly.

But one continuity seam still remained.

If the user opened a *different* docs page from outside the help buffer, the
editor overwrote that dormant current target without first pushing it onto local
back history. The state stayed witnessable long enough to resume, but a normal
branching docs open quietly broke the replay trail.

Rev410 keeps the follow-up deliberately small:

- `open_help_doc(..., push_stack=True)` now branches from the same local docs
  source whether it is active on-screen or dormant in the session
- opening a different docs page from outside the help buffer pushes that dormant
  target onto back history with its exact saved cursor position
- dormant forward history still clears when the new docs open diverges from that
  local trail, just like an on-screen branch change

The goal is simple: once Micromax witnesses a current docs target, opening a new
page should continue that same local history whether the current target is
visible or merely dormant.
