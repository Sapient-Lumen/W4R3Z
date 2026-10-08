# Evidence catalog

This file describes the artifact types GlassTTY should preserve and how they should be named conceptually.

## Artifact families and what they should contain

### state snapshot
Should contain:
- surface key
- browser lane
- one or more state families
- timestamp

### probe capture
Should contain:
- bridge status
- browser/worker/native-lane diagnostics
- warnings and hints

### fixture capture
Should contain:
- captured page or subtree inputs
- route and frame context
- extraction notes where relevant

### smoke run
Should contain:
- workflow under test
- attempted action summary
- pass/fail or partial result
- direct evidence refs

### support bundle
Should contain:
- manifest
- surface key
- browser lane
- workflows touched
- main state snapshots
- relevant probe or fixture refs
- result summary
- next-action hint when useful

### operator handoff
Should contain:
- current environment and support context
- recent relevant artifact refs
- recommended next steps

### operator attempt
Should contain:
- before state
- attempted action
- after state
- result classification
- related evidence refs

### comparison bundle
Should contain:
- compared artifact refs
- changed cues
- likely affected workflows
- drift severity

### release-gate artifact
Should contain:
- support claim under review
- supporting evidence refs
- caveats
- promote/hold/demote recommendation

## Naming guidance

Names should make it easy to recover:
- surface
- lane
- workflow or artifact family
- time
- run or comparison identity

The exact file-path convention may evolve, but the naming should always keep those dimensions visible.
