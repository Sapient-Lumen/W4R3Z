# Worked Example Address Integrity, Safe Contact, and Unit-Level Location

**Purpose:** distinguish mailing, residence, safe-contact, service-delivery, and unit-level location state so the institution stops treating one bad address field as permission to miss the person entirely.

**Person served:** someone whose life is organized across more than one valid location field, and who gets harmed when the system insists they must all be the same.

**From-below:** the institution should not make people choose between safety, reachability, and administrative legibility when those are often different locations.

---

## Use this memo when
- the person has a mailing address, residence address, safe-contact address, unit number, or service location that differ;
- the system uses the wrong address field for notice, route assignment, delivery, inspection, or jurisdiction checks;
- multi-unit properties or shared structures make unit-level precision materially important.

---

## Required artifacts
- **Address-role receipt (`ADR-*`)** showing which address is being used for notice, residence, service delivery, inspection, and jurisdiction.
- **Unit-level location packet** when the property has multiple units, buildings, or entrances.
- **Safe-contact override** so protective communications can route to a non-residence location without being treated as fraud.

## Safe defaults
- Do not assume mailing, residence, and safe-contact locations are interchangeable.
- Keep the last safe contact path live while address roles are disputed.
- Unit ambiguity pauses punitive action at the wrong door.

## Companion cases and memos
Use `WX-56`, `WX-58`, and `WX-59` in `235-worked-examples-and-trace-walkthroughs.md`. Pair with `47`, `109`, `136`, and `270`.
