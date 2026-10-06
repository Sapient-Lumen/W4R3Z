# Causality graphs and minimal evidence bundles

DeriveBSD already emits rich receipts, snapshots, and event segments.

The remaining failure mode is **"I have the evidence, but I can't quickly prove what caused what"**.

A small additional primitive makes support bundles dramatically more useful:

> compute and ship a **causality graph** that links change-sets → receipts → events → rollbacks.

## What is a causality graph?

A `causality.graph` is a DAG (or near-DAG) over **evidence objects**, with edges that mean:
- *derived-from* (this receipt was computed from these inputs)
- *triggered* (this change-set triggered these service transitions)
- *supersedes* (this activation replaced a previous generation)
- *rolled-back-to* (this rollback selected a previous BE)

This graph is not the whole story; it is the **index** that makes the story navigable.

## Why bake this in now

- Humans need a "one-page" explanation surface.
- Automation needs a mechanically-checkable minimal bundle.
- Without a standard graph, incident bundles drift into ad-hoc spreadsheets.

## Integration points

- Change pipeline: `change.set` and `change.receipt` already form a natural spine.
- Boot lane: `boot-bless-receipt` and boot health reports anchor success/failure.
- Service lane: `svc.event` transitions can be attributed to a specific activation/change.
- Attestation lane: `attestation-receipt` can link to the change id/trace id.

## Minimal evidence bundles

The causality graph enables a deterministic "bundle-min" operation:
- start from a trigger (crash id / fault id / rollback receipt)
- walk edges to collect only the required digests
- attach those objects + graph to the incident bundle

This reduces bundle size while increasing explanatory power.

## Timeline view (human-scale orientation)

A causality graph is an **index**; humans still want a fast orientation surface.

DeriveBSD therefore treats an export-safe incident timeline as a first-class derived artifact:
- `incident.timeline` is computed from bounded `event.segment` ranges (and optionally `causality.graph`).
- incident bundles can carry the timeline digest as the “one page” incident summary.

See: `docs/419-incident-timelines-as-derived-artifacts.md`.

## Files

- New schema: `spec/causality.graph.schema.json`
- New example: `spec/examples/causality.graph.json`
- Extend incident bundles to optionally include `causality_graph_digests`.

