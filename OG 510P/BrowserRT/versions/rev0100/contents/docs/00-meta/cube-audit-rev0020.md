# Cube audit — rev0025

Revision: rev0028

## Why this exists

The cube is now large enough that correctness is not only runtime correctness.
The artifact itself can drift: manifests can point at stale artifacts, docs can
claim the wrong revision, package scripts can generate old filenames, and browser
proofs can pass while reentry surfaces tell the next turn the wrong thing.

Rev0018 preserves the cheap audit task and extends it around the new spill
mailbox proof plus the browser-light release policy.

## Manifest id

`cube:audit-surfaces`

## Tool

`tools/audit_cube_surfaces.mjs`

## Artifact

`artifacts/audit/REV0044-CUBE-AUDIT.json`

## Audit scope

- top-level JSON revision alignment;
- package/runtime version alignment;
- stale currentness outside changelog;
- browser tasks serial-grouped when explicitly selected;
- generated artifact prefix visibility;
- external dependency drift;
- release-tier browser cost containment;
- spill mailbox artifact visibility.

## Non-claims

The audit is not a substitute for `make lint`, browser probes, proof scripts, or
release-manifest hash verification. It is a fast reentry/hygiene check that helps
catch cloudtainer-turn drift before packaging.

## Current audit concern

Browser tests are expensive and this turn again confirmed package-window risk.
The audit must remain cheap and must not start a browser. Browser behavior is
tested by named browser manifest tasks; cube coherence is tested here.

## Issues handled in rev0025

The release tier is now browser-light. Browser/CDP slices remain available in
`browser` and `full` tiers, but broad release validation no longer launches them
by default. The audit enforces `releaseBrowserTaskEstimateMs === 0` so a future
turn cannot accidentally reintroduce broad browser cost without making that
policy visible.
