# RFC-0124: Capability graph linting + visualization

Status: **draft**

## Motivation

DeriveBSD’s security story depends on an explicit, reviewable authority graph.
We already have `caproute.json` as a routing manifest, but we need:
- a normalized graph representation for tooling
- stable lint rules that can be policy-gated
- standard visualization/diff outputs for human review

## Goals

- Define a canonical `capability.graph` representation.
- Enable lint rules that can be required by policy.
- Enable deterministic visualization/diff outputs.

## Non-goals

- Building a full-blown security policy language here.
- Replacing runtime enforcement mechanisms (jails/Capsicum/pf).

## Proposal

### Artifact: `capability.graph`

A graph binds:
- nodes: compartments (host services, jails, microVMs, brokers)
- edges: capabilities, each with:
  - type (fs/net/rpc/portal/identity/etc.)
  - rights (small enumerations)
  - scope (paths, ports, service names)
  - source/target node IDs
  - optional risk tags (e.g. `danger:net-egress`)

The object is derived deterministically from:
- Plan digest
- caproute manifest digest
- known capability type registry

### Lint rules (v0)

A small default ruleset (tooling), with policy able to strengthen:

- No `net:egress:any` edges unless tagged with an override receipt.
- No edges from “host admin” nodes into workload nodes.
- Any writable state mount requires a `state.version.contract` reference (future lane).

## References

- Fuchsia capability routing concepts: https://fuchsia.dev/fuchsia-src/concepts/components/v2/capabilities
- Fuchsia components intro: https://fuchsia.dev/fuchsia-src/concepts/components/v2/introduction
