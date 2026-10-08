# rev0328 QRF cross-route handoff and frame-transport audit

## Finding

The risky seam in the QRF lane was not lack of registry coverage. It was a cross-route handoff: `EU-0010-QRF-FRAME-TRANSPORT` named `ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE`, even though that empirical-delta row is FamilyC-route-local. The handoff was reciprocal, so the older handoff audit passed, but the route sets did not overlap.

That is a real authority leak. It lets FamilyC subregion-state pressure become visible from the QRF evidence unit, and it can make QRF witness-portability look supported by a source row that was not intended to bear the QRF route.

## Repair

rev0328 makes the handoff layer route-aware.

- `tools/evidence_delta_handoff_policy.py` now checks delta/evidence route overlap.
- `ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE` is restricted to `EU-0001-FAMILYC-EW-RECONSTRUCTION` and FamilyC route controls.
- `EU-0010-QRF-FRAME-TRANSPORT` no longer names `ED-0020`.
- `ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE` is introduced as the QRF route-local pressure row.
- `tools/qrf_frame_transport_policy.py` makes the split executable.

## Substantive QRF pressure added

The QRF route remains `S2`, but it now carries a sharper public-witness burden. A QRF frame-transport result must declare:

- source and target frames,
- operational equivalence relation,
- relational observable quotient,
- boundary/corner or edge-mode sector,
- large-gauge treatment,
- algebraic type or crossed-product convention,
- observer/clock convention,
- same-record rule,
- nonportable or nonlocalizable failure cases.

The new sources are treated as pressure only:

- `REF-0679` supports the large-gauge, boundary/corner, gluing, and QRF/spacetime-symmetry denominator.
- `REF-0680` supports the crossed-product and observer-dependent gravitational-entropy denominator.

They are intentionally absent from `EU-0010-QRF-FRAME-TRANSPORT.source_refs`, because they do not create acquired evidence-unit credit. They live on the forecast, decision, empirical-delta, protocol, quotient, gauge, algebraic-locality, edge-mode, factorization, and transportability rows.

## Non-promotion rule

Frame switching, large-gauge relativisation, and crossed-product entropy are not ToE identity. They are route-local witness-portability pressure. The maximum current effect remains `S2` unless a future route provides an independent public bridge, observed-sector recovery, failure-case replay, and nonrelational negative controls.
