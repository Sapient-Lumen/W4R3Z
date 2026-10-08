# Dormant help state should still replay like current help state

Rev410 fixed one half of the dormant-help continuity problem.

If the user left the help buffer and opened a *different* docs page, Micromax now
branches from the dormant current page instead of silently overwriting it.

But one matching seam still remained.

If the user stayed outside the help buffer and ran `helpback` or `helpforward`
directly, the editor reopened the requested target but treated the replay as if
there were no current page to preserve on the opposite stack. The dormant
session-local current help target stayed witnessable enough to `helpresume`, but
direct replay quietly broke continuity unless the user resumed first.

Rev411 keeps the follow-up deliberately small:

- `helpback` now branches from the same local docs source whether it is active
  on-screen or dormant in the session, so off-screen replay pushes the dormant
  current target onto forward history before reopening the requested back target
- `helpforward` now mirrors that same rule in the other direction, pushing the
  dormant current target onto back history before reopening the requested
  forward target
- exact saved cursor positions still travel with those dormant entries, so
  direct off-screen replay preserves the same tiny witness trail that an active
  help buffer already had

The goal is simple: once Micromax witnesses a current docs target, direct replay
commands should continue that same local trail whether the current target is
visible or merely dormant.
