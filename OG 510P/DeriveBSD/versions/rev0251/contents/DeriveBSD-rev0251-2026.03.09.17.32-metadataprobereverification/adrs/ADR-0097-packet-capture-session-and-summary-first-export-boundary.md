# ADR-0097: Packet capture session and summary-first export boundary

- Status: Accepted
- Date: 2026-03-08

## Context

`adrs/ADR-0096-packet-capture-raw-sockets-and-fast-packet-io-boundary.md` fixed the important authority decision:
raw packet visibility is a stronger lane than ordinary networking.

That narrowed the problem, but it still left a practical implementation gap:
**what is the canonical shape of packet capture when we do allow it?**

If the answer is merely "run tcpdump and save a pcap somewhere," several already-fixed boundaries regress:

- capture authority drifts away from the lease / receipt model,
- support and incident workflows silently start depending on raw packet blobs,
- export policy becomes an afterthought instead of a separate reviewed step,
- and profile differences collapse into ad-hoc operator habit.

DeriveBSD needs one narrower answer:
if packet capture exists, it should be a **bounded, typed capture session** with a **summary-first export posture**.

## Decision

1. Introduce `packet.capture.session` as the authoritative capture-session object for bounded packet capture.
   It records:
   - who/what the capture is for,
   - which host / interface / workload scope is targeted,
   - the capture backend and selector/filter posture,
   - and the time/packet/byte bounds that keep the session finite.

2. Keep packet capture aligned with the temporary-authority model from `adrs/ADR-0083-temporary-authority-grant-lease-and-use-boundary.md`:
   - the authoritative object is the session,
   - lease metadata / issue / use receipts may point at that session,
   - and later export / incident receipts remain evidence about what happened rather than the thing that granted capture authority.

3. Make **summary-first export** the default posture:
   - local packet material may exist inside the bounded maintenance / incident lane,
   - but the normal review/share surfaces are session metadata, bounded summaries, and existing `net-flow-summary` / incident-bundle evidence,
   - not ambient shipment of raw packet payloads.

4. Treat raw packet payload export as a stronger, explicit exception:
   - never the default incident/support bundle payload,
   - always subject to explicit export policy / approval when allowed,
   - and profile D production posture remains effectively "none unless approved maintenance/lab policy says otherwise."

5. Do **not** invent a new product-profile default key for packet capture.
   This posture is compiled from the already-existing boundaries:
   stronger packet authority (`docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`),
   evidence posture (`docs/478-evidence-collection-posture-by-profile.md`),
   export posture (`docs/466-export-boundary-posture-by-profile.md`),
   and temporary-authority leases (`docs/493-temporary-authority-grant-lease-and-use-boundary.md`).

## Consequences

- The packet-capture lane now has one typed session surface that implementation can target.
- Incident/support flows can stay explainable without quietly standardizing raw `.pcap` blobs as the default handoff format.
- Future CLI / broker / portal work can converge on a single session shape instead of capture-tool folklore.
- A small guardrail can keep packet-capture docs, export docs, evidence docs, and the new schema from drifting apart.

## Why this is narrow enough

This ADR does **not** standardize:

- the exact capture-helper daemon or CLI,
- the exact packet-file encoding (`pcap`, `pcapng`, or future alternatives),
- the exact redaction algorithm for packet payloads,
- the exact summary aggregation heuristic for every incident class,
- or the exact raw-socket / netmap / packet-injection workflows.

It only fixes the session + export boundary so future implementation has a coherent target.
