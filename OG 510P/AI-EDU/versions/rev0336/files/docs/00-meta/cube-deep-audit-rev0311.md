# rev0311 cube deep audit

## Highest-risk seam inspected

This pass audited the boundary between the scratch-local post-readout rail and
the packaged release-control examples. Earlier rev0304-rev0310 work made field
sources lane-local, date-stable, hash-anchored, and dispatch-lane mapped. That
still left a quieter control-plane risk: example JSON used by release checks
could describe a post-readout action or service lifecycle row with closure or
public-language text that was not as strict as the field recorder.

That would not accept evidence by itself, but it is precisely the kind of
wasteful drift that can make an operator believe the archive is closer to
closure than it is. It also turns the cube's vice back on itself: the docs say
`ready-but-not-closed`, while a loosely checked example row could imply public
claim promotion.

## Correction made

`tools/check_post_readout_actions.py` was refactored so its validator can also
run synthetic payload regressions without writing fixture files. It now proves
that a live `FT-0181` post-readout action cannot set `closure_permitted=true`
and cannot carry promotion language in `public_language_action`.

`tools/check_service_lifecycle_decisions.py` received the same lightweight
payload-regression pattern for lifecycle rows. This keeps lifecycle examples
from becoming the weaker path around the post-readout public-claim boundary.

## What was intentionally not added

No new schema, registry family, queue item, or broad doctrine surface was added.
The change is deliberately narrow: two validators now catch closure/public-claim
drift where the release-control examples already live.

## Next useful work

The next useful pass should keep looking for places where example/control JSON
has looser public-claim or closure semantics than the field rail. Priority should
remain executable validators and real owner-evidence flow over more prose.
