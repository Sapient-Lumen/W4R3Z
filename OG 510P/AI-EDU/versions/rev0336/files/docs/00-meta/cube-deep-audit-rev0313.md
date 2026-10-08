# rev0313 cube deep audit

## Highest-risk seam audited

The audit focused on the place most likely to waste a future operator session:
local field-state discovery after validators have run in the same cloudtainer.
The prior firebreaks blocked checker/release/legacy scratch and hash/source
laundering, but positive fixtures were intentionally placed under
`scratch/field/ft0181/validation/...`.

That path is useful for tests and dangerous for live routing because it is under
the same broad field lane as real operator artifacts.

## Finding

A validation fixture could be structurally valid enough to appear in a live scan
if the operator later ran the router against `scratch/field/ft0181`. The release
package excludes `scratch/`, so this is a session/runtime contamination risk, not
a packaged evidence risk.

Severity: material execution waste risk; low evidence-acceptance risk because the
late-stage controls still block evidence and closure claims.

## Refactor

- Added a router ignore rule for field-lane validation fixture path parts.
- Applied the same rule to the local field-lane cleanliness report.
- Added regression coverage that a valid-looking validation contact/packet does
  not alter an empty live-lane route.
- Kept validators free to use validation lanes for positive fixtures.

## Remaining risk

The cube is still waiting on the only thing that matters: real owner-reviewed
`SRC2+` evidence. More doctrine or release metadata is lower value than executing
the bounded first owner contact and then routing the actual returned packet.
