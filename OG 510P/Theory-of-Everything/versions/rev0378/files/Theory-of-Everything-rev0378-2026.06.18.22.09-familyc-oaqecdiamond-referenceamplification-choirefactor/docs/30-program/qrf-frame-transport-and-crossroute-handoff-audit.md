# QRF frame-transport and cross-route handoff audit

Revision: `rev0328` (`qrf-frame-transport-crossroute-handoff-audit`)

## Risk targeted

The QRF route was under substantive pressure compared with the other active lanes, but its evidence handoff was also too porous. `EU-0010-QRF-FRAME-TRANSPORT` still named FamilyC-only subregion-state pressure, which made a FamilyC entanglement-wedge/subregion-state delta appear as if it also supported the QRF/relational frame route. That is not safe: QRF witness portability, large-gauge/corner semantics, and crossed-product observer-dependence are adjacent to FamilyC subregion algebra, but they are not the same evidence unit.

## Substantive repair

`rev0328` adds `ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE` as a route-local QRF pressure row. The row requires explicit frame system, frame group, operational equivalence relation, localizability/invertibility domain, relative-observable algebra, boundary/corner/large-gauge convention, clock/observer spectrum, public witness comparison, and failure cases before frame-transport language can be spent.

The revision also removes `ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE` from the QRF evidence unit. FamilyC subregion-state pressure remains available to the FamilyC EW/code route, while QRF pressure is carried by the QRF delta and control rows.

## Source-role boundary

Refs `REF-0679` and `REF-0680` are route-local pressure only. They are intentionally kept out of `EU-0010-QRF-FRAME-TRANSPORT.source_refs`, so current QRF/large-gauge/crossed-product work cannot be spent as acquired evidence-unit support or route promotion.

## Refactor / audit change

`tools/evidence_delta_handoff_policy.py` now rejects empirical-delta/evidence-unit handoffs whose route sets do not overlap. `tools/qrf_frame_transport_policy.py` adds an explicit QRF source-role and handoff audit. Together these checks prevent pressure from being laundered through adjacent but distinct route families.

## Non-promotion rule

The QRF route remains current `S2` with promotion ceiling `S2`. This revision strengthens operational witness-portability denominators and handoff hygiene only; it does not create ToE identity, observer-independent entropy closure, or candidate-native public-record closure.
