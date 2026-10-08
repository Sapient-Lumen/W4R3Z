# rev0310 mission kernel

`rev0310` keeps the cube pointed at the same scarce event: one real
owner-reviewed `FT-0181` packet moving through `scratch/field/ft0181/` without
local helper output turning into evidence, action authority, public support, or
closure. The archive still has no accepted owner packet, no accepted `SRC2+`
evidence, no real active-change window, no public-claim upgrade, and no closure.

## Heart of the work

The mission is now execution discipline, not more doctrine. The cube already has
enough surfaces to describe the field rail. The live risk is that an operator
will reach a later handoff and accidentally let a locally valid-looking record
carry an action class that is wider than the source readout actually permits.

Rev0304 through rev0309 split field/check scratch, fixed operator-local dates,
blocked fake returned CSV/source-packet lanes, and anchored source hashes. The
next riskiest seam sits after a terminal live-window readout: post-readout
dispatch chooses the owner-action lane, the next evidence ask, and the public
language action. If those three classes drift apart, the rail can still look
bounded while asking the wrong next thing or narrowing/suppressing public
language without the matching readout disposition.

## rev0310 correction

`rev0310` makes the post-readout action dispatch lane atomic. A dispatch record
must now keep these three values locked to the source readout disposition:

- `owner_action_class`
- `next_evidence_ask_class`
- `public_language_action`

The recorder rejects mismatched overrides before writing scratch output, and the
shared integrity guard rejects tampered records that try to preserve the lane
while swapping a more aggressive next ask or public-language action.

## Non-evidence boundary

The patch only tightens the route from terminal readout to post-readout action.
It does not contact an owner, import a real CSV, accept `SRC2+`, record a real
live-window result, mutate a service record, publish or suppress public language,
or close `FT-0181`.
