# Capability graph linting + visualization (keep caproute readable)

DeriveBSD’s “capability routing manifest” (`caproute.json`) is intentionally an **authority graph**.
The moment that graph becomes unreadable, review stops working and teams regress to ambient authority.

Fuchsia treats capability routing as an access-control mechanism and provides tooling/introspection around it.  
References:
- Fuchsia “Capabilities”: https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- Fuchsia components intro (capability routing): https://fuchsia.dev/fuchsia-src/concepts/components/v2/introduction

## DeriveBSD direction

Define a normalized, derived view:

`capability.graph` (canonical JSON)
- derived from Plan + `caproute.json`
- stored as an artifact (digestable, diffable)
- referenced by policy decisions and rollout tooling

This object exists so we can build tooling that is stable, predictable, and review-friendly.

### Tooling expectations (baked in early)

1) **Linting**
- deny obvious footguns:
  - “broad network egress” edges (e.g., `system.net` / `net-egress-grant` issuance; see `201-network-egress-as-capability.md`) without an explicit rationale tag
  - “host admin” capabilities routed into workload compartments
  - write access to mutable state without a versioned-state contract
- require justification metadata on “danger edges”
  - links to RFC/ADR, change ticket, or incident ID
  - examples of danger edges: `system.net`, `ui.screencast`, `ui.remotedesktop`, `ui.camera`, `ui.audio.capture`, `ui.location`, `ui.print`

2) **Visualization**
- generate DOT/SVG graphs for review
- compute summaries:
  - per-node authority budget (“what can this thing touch?”)
  - diff summaries (“what new edges were introduced?”)

3) **Policy integration**
- policy can require:
  - lint pass
  - no new danger edges in stable channel without explicit override receipt

## Why this matters

- Makes “least authority” operationally sustainable.
- Turns review into “graph diff review”, not “read 800-line jail config”.
- Creates a common substrate for:
- portals
- cap-RPC
- workload identity
- observability grants
- debug recording grants
- resource budgets
- rollout constraints

See:
- `docs/140-capability-routing-manifests.md`
- `docs/94-runtime-blast-radius-contract.md`
- `docs/192-observability-as-capability.md`
- `docs/193-resource-budget-capabilities.md`
- `docs/194-debugging-by-lease-and-replay-capsules.md`
