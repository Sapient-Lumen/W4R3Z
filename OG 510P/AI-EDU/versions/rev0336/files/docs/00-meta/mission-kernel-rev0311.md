# rev0311 mission kernel

`rev0311` keeps the cube focused on the same scarce event: a real owner-reviewed
`FT-0181` packet moving through `scratch/field/ft0181/` without local artifacts
turning into evidence, public support, lifecycle authority, or closure. The
archive still has no accepted owner packet, no accepted `SRC2+` evidence, no real
active-change window, no public-claim upgrade, and no closure.

## Heart of the work

The immediate mission is executable claim discipline after the post-readout rail,
not another doctrine layer. Rev0310 bound dispatch classes to the terminal
readout lane. The next risk was release-control drift: packaged post-readout
action and service-lifecycle examples could still look ready while allowing
closure or stronger public language in text fields that were outside the
field-lane JSON guard.

## rev0311 correction

`tools/check_post_readout_actions.py` now treats live `FT-0181` as a hard
non-closure condition for post-readout action examples. It also requires the
example `public_language_action` text to stay lane-bound and rejects public
promotion terms while the followthrough remains live.

`tools/check_service_lifecycle_decisions.py` now applies the same lane-bound
public-language regression to lifecycle examples, so lifecycle rows cannot
launder a stronger public claim after a post-readout action.

## Non-evidence boundary

This pass does not contact an owner, import a real CSV, accept `SRC2+`, record a
real live-window result, mutate a service record, publish or suppress public
language, or close `FT-0181`. It only makes the packaged release-control plane
match the executable field rail's public-claim and closure boundary.
