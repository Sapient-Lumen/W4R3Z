# Live Class-Local Import Replay and Quorum Firewall

rev0200 closes a milestone gap in the receipt chain without pretending that a real counterparty has appeared. rev0199 proved that a non-host-looking institutional dry run remains zero-weight. The remaining risk is the opposite failure: once a future response finally looks live, a worker may let one class-local success upgrade the whole cross-critical packet.

The rev0200 rule is strict: **class-local replay is not cross-critical quorum**.

A replay may prove one receipt class in a scenario, but it cannot satisfy the cross-critical drill unless the recomputation report shows the required number of independent receipt classes, dependency separation, sealed/public parity, and failed-gate publication. A valid result-return receipt can be meaningful and still insufficient.

## What this pass adds

The new `live-class-local-import-replay` object is a scenario harness. It answers one narrow question: if a future result-return response passes provenance checks, what should the import chain do? The answer is not “close reliance.” The answer is “increment only that class in the scenario, keep unsatisfied classes visible, and preserve stayed reliance for the archive until an actual live artifact exists.”

This matters because the archive had strong blocks for dry runs, fixtures, defective responses, requests, and failed no-response branches. It did not yet have a positive-path firewall showing how a future valid class-local import should behave without becoming a global closure shortcut.

## Core rules

**Class-local replay is not cross-critical quorum.** A result-return class import does not imply first-touch, compute-floor, sealed/public, namespace, reserve, representative, witness, welfare, or independent-review satisfaction.

**Scenario delta is not archive delta.** A scenario projection may show `projected_live_floor_delta=1`; the archive live floor remains unchanged unless the underlying artifact is actual live evidence and a provenance gate imports it.

**Positive path must keep missing classes visible.** The public shell must name the classes still missing. A successful class-local replay that hides unsatisfied classes is a false closure event.

**Recompute beats narrative.** Quorum state is read from the recomputation report, not from prose, request packets, role rosters, or hand-edited ledger fields.

## Refactor effect

The receipt stack now has four gates that should not collapse into each other:

1. request packet,
2. response artifact envelope,
3. intake/import gate,
4. class-local replay and quorum recomputation.

rev0200 adds an audit that checks this stack from the front door as well as from the examples. It also adds a front-door revision-sync audit so stale README/START_HERE drift cannot recur silently.

## Reliance posture

No actual live external receipt exists in this archive. rev0200 advances readiness by proving the positive-path shape and the no-overclaim firewall. It does not improve the live receipt floor.
