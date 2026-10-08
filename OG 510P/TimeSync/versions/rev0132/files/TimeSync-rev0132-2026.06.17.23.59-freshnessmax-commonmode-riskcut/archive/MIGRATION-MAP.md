# Migration map

The original rev0060 archive is preserved in `archive/original-rev0060/`.

## Old flat files to reconstructed locations

| Original focus | Reconstructed location |
|---|---|
| `CHARTER.md`, `PROBLEM-FRAME.md`, `TRACKS.md`, `SCENARIOS.md` | `spec/00-charter.md`, `spec/01-problem-frame.md` |
| `TIMESTATE.md`, `INVARIANT-CORE.md` | `spec/02-timestate.md`, `schema/timestate.schema.json` |
| `CONTROL-SURFACES.md`, `SEMANTIC-BOUNDARIES.md` | `spec/03-control-surfaces.md` |
| `PROFILES.md`, `PROFILE-BOUNDARY.md`, `P4-LANES.md`, `P4-COHESION.md` | `spec/04-profiles.md`, `profiles/` |
| `EXTENSION-HOOKS.md`, traceability/sync/holdover/validity tests | `spec/05-extension-hooks.md` |
| `GREENFIELD-RESPONSE-SKETCH.md`, `GREENFIELD-TRACEABILITY.md` | `spec/06-wire-claim-and-local-assessed-state.md` |
| Discovery/request tests | `spec/07-discovery-request-results.md`, `schema/discovery-request.schema.json` |
| Relay/boundary/reason tests | `spec/08-relay-boundary-context.md`, `schema/boundary-context.schema.json` |
| Required/default, conformance, fallback tests | `spec/09-profile-conformance.md`, `schema/profile-assessment.schema.json` |
| Profile identity/reference tests | `spec/10-profile-reference-strength.md`, `schema/profile-reference.schema.json` |
| `frontier-ticket.json` from rev0060 | `spec/11-lifecycle-and-stale-assessments.md`, `archive/FT-0060-CLOSURE.md` |
| All old `*-TEST.md` notes | `tests/acceptance-tests.yaml` plus preserved originals |

## Preservation rule

No original rev0060 file was edited in place. The reconstruction is a new layer above the preserved archive.
