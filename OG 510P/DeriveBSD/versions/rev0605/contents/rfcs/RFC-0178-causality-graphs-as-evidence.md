# RFC-0178: Causality graphs as evidence (causality.graph)

Status: Draft

## Problem

DeriveBSD’s evidence objects are individually strong, but incident response often needs:
- a compact explanation of **causality**
- a deterministic way to compute a **minimal evidence bundle**

Without a standard representation, every tool invents its own correlation conventions.

## Proposal

Introduce `causality.graph`:
- a typed graph over digests/ids of existing evidence objects
- edges have a small, stable vocabulary
- graph production is deterministic and policy-driven

Extend `incident.bundle` to optionally include one or more `causality_graph_digests`.

## Schema sketch

Nodes:
- `digest` (sha256/blake3/etc)
- `kind` (change-receipt, boot-bless-receipt, svc-event, event-segment, ...)

Edges:
- `from` digest
- `to` digest
- `rel` (derived-from | triggered | supersedes | rolled-back-to | references)

## Semantics

- Graphs may be partial.
- Graphs must not include secrets.
- Graphs should be stable under redaction (use digests and coarse metadata only).

## Open questions

- Should graphs permit cycles (e.g., retries)? If yes, treat as a multigraph and keep edges timestamped.
- Do we need a canonical topological ordering for deterministic serialization?

## Files

- New: `spec/causality.graph.schema.json`
- Example: `spec/examples/causality.graph.json`
- Modified: `spec/incident.bundle.schema.json`, `spec/examples/incident.bundle.json`

