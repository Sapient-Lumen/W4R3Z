# rev0303 cube deep audit

## Audit focus

The audit target was the whole cloudtainer session rather than another late-stage
`FT-0181` bridge. The readout found that the cube's stated boundaries were strong,
but the live working directory had a practical contamination seam: tests and lints
create synthetic scratch artifacts, and the field router used default `scratch/` as
its scan root.

## Finding

After `make lint-owner-reply`, the default `make owner-field-work` route could see
checker-created artifacts. One observed example was a workbench review brief under
`scratch/owner-workbench-review-briefs/...` whose `source_seed.reference` pointed
back to `scratch/check-ft0181-live-window-terminal-brief/...`. That artifact was
useful to a checker, but it was not real field state. The router selected it as if
returned owner work already existed, producing a later-stage recommendation instead
of the correct first-contact packet route for a clean field session.

This was not a packaged-release leak because `scratch/` is excluded from release
zips. It was still severe inside the cloudtainer because the maintainer's next live
command can be based on the current filesystem, not the packaged archive.

## What changed

`tools/decide_ft0181_field_next_action.py` now has a scratch-state firebreak. For
any selected scratch root, the collector ignores subtrees whose relative path part
starts with `check-`, `smoke-`, `test-`, or `fixture-`. It also ignores artifacts
whose JSON provenance references point back into those non-field subtrees. The
field-next docket now records the firebreak rule alongside the manifest-clock
selection rule.

`tools/check_ft0181_field_next_action.py` includes a regression fixture that plants
both a check-subtree contact status and an outside artifact that links back to a
check seed. The expected route is still `PREPARE-FIRST-CONTACT-PACKET` with empty
field-state counts.

## Waste corrected

The waste was not the existence of tests; the waste was letting test byproducts
compete with field evidence-routing state. Without the firebreak, maintainers could
spend time interpreting a synthetic later-stage route, writing new explanatory
docs, or rerunning downstream commands when the real problem was only scratch
state contamination.

## Remaining risk

The next structural cleanup should split scratch into explicit lanes such as
`scratch/field/`, `scratch/checks/`, and `scratch/releases/`, then make the router
default to the field lane. `rev0303` is a lower-risk repair: it preserves existing
commands while excluding known non-field scratch. The evidence boundary is unchanged:
no local artifact, checker result, lint pass, registry, audit, or package can close
`FT-0181`.
