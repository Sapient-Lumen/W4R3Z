# Worked Example Parcel, Geocoding, and Place-Resolution Fallbacks

**Purpose:** prevent wrong-place actions by making parcel, geocode, address, unit, structure, and place-resolution state contestable and reviewable.

**Person served:** someone harmed because the institution thinks the wrong parcel, geocode, structure, frontage, or unit is the relevant place.

**From-below:** wrong-place action is often treated as a minor data issue even when it is the whole reason the wrong person gets inspected, billed, denied, or displaced.

---

## Use this memo when
- parcel and street address do not resolve cleanly to the same place;
- geocoding, frontage, or structure-level inference is deciding enforcement, eligibility, or routing;
- the institution wants to act on a place it cannot identify with enough precision to find the right door.

## Required artifacts
- **Place-resolution packet** showing parcel, address, unit, geocode, and confidence class.
- **Wrong-place challenge lane** with a protective hold on high-consequence action.
- **Map/version trace** for any geocoder or parcel file that materially shaped the outcome.

## Safe defaults
- No punitive action where the institution cannot distinguish parcel-level from unit-level responsibility.
- Low-confidence place resolution should route to review, not automatic action.
- Wrong-place incidents become audit events.

## Companion cases and memos
Use `WX-56`, `WX-57`, and `WX-58` in `235-worked-examples-and-trace-walkthroughs.md`. Pair with `136`, `71`, `256`, and `268`.
