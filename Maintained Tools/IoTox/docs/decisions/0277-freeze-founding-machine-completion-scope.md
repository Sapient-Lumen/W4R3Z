# ADR 0277: Freeze founding-machine completion scope

Status: accepted, 2026-09-01

## Context

After ADR 0276, six roadmap checkboxes required evidence that the founding machine cannot itself
produce: a hosted remote CI observation, representative physical hardware selection and testing,
an independent safety/security review, a physical OTA target, and independently witnessed public
Tor time/operator diversity. The project owner has explicitly removed those obligations from the
IoTox repository's completion definition. This computer and its Sandwurm guests are the complete
qualification substrate for the tool the owner intends to build and use.

Leaving the items unchecked would incorrectly present intentionally unavailable work as unfinished
product work. Marking them complete would be worse: no such evidence exists.

## Decision

Permanently retire the six checkboxes from the roadmap. Render each original obligation struck
through and cite this ADR. They are out of scope, not passed gates.

The repository completion boundary is now:

- source-linked construction and tests on the founding machine;
- simultaneous isolated Sandwurm/KVM guests for network, restart, route, and lifecycle evidence;
- operator-owned local Tor/I2P fixtures and public-route observations where useful; and
- explicit nonclaims for physical diversity, external review, hosted service execution, independent
  builders, and independently witnessed public-network history.

No future change may silently restore one of the retired items as a release blocker. Restoring one
requires a new ADR that identifies the available substrate and supersedes this decision.

## Consequences

IoTox still reports exactly what its evidence proves. Sandwurm evidence is not renamed physical
hardware evidence, a local flake check is not renamed hosted CI, and repository analysis is not
renamed independent review. Those distinctions remain in threat-model and evidence nonclaims.

Four completion obligations remain after this scope change: M5A randomized/long-running route
policy, the M5C one-writer shadow, versioned selective-sync/metadata policy, and the comprehensive
M5C adversarial/scale campaign. Those are all work the founding machine can perform.
