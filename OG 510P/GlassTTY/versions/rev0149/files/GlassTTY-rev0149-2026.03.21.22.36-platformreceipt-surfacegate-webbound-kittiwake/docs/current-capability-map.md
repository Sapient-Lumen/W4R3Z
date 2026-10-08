# Current capability map

This file ties the existing repo to the future product model so implementers can evolve from what is already here.

## Generic bridge foundation already present

### Extension
Current areas:
- MV3 worker and side-panel flows
- probe and browser messaging surfaces
- receiver/content-script experiments

Future product relation:
- generic bridge
- diagnostics state
- operator surface
- action execution path

### Native host and broker
Current areas:
- persistent lane ownership
- native host diagnostics
- broker/runtime reports

Future product relation:
- generic transport
- diagnostics state
- action outcome plumbing
- evidence source for runtime health

### CLI and scripts
Current areas:
- doctor
- smoke
- readiness report
- operator handoff
- operator attempt
- profile capture and relaunch helpers

Future product relation:
- support-capture workflow
- evidence and ledgers
- release-gate artifacts
- drift investigation support

## Adapter and surface work already present

### Claude-oriented adapter lane
Current areas:
- adapter docs and implementation traces
- fixture captures and comparisons
- receiver resolution work

Future product relation:
- reference adapter
- source of shared workflow patterns
- first backfilled support record

## Evidence infrastructure already present

Current areas:
- fixtures
- validation outputs
- handoff bundles
- operator attempt bundles
- readiness and profile ledgers

Future product relation:
- evidence catalog
- support bundles
- drift baselines
- support-truth updates

## Where implementers should evolve rather than restart

- map current probe and doctor outputs into state families
- reinterpret current validation artifacts as support evidence
- backfill Claude support truth from existing artifacts
- reuse existing capture and comparison utilities as the drift program foundation
- keep the existing generic bridge while widening adapters and state contracts
