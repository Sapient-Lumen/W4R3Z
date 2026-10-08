# Adopter 60‑minute path smoke test (drift firewall)

**Track:** Shared (cross-cutting)


This checklist is a **bounded drift firewall** for NR‑02 (“humans adopt this under crisis”). If the 60‑minute entry path stops working,
the archive becomes a maintainer-only artifact.

**Recordkeeping:** After running this, append one row to:
`artifacts/registries/adopter-path-smoke-tests.csv` (store only short blockers + a pointer to the fix/ADR).

## Setup
- ☐ Start from a fresh machine/user (or a clean browser profile). No prior context.
- ☐ Start a 60‑minute timer.
- ☐ Use only the archive contents (no network assumptions).

## Execute the 60‑minute path
- ☐ Begin at `README.md` and follow the **60‑minute path** in order.
- ☐ Confirm every linked file exists in the archive and opens without “missing / moved” confusion.
- ☐ Confirm the path answers (in plain language):
  - what this project is for (portable evidence; dispute lanes),
  - what is **in scope** (Track A) vs research annex (Tracks B/C),
  - what not to read right now (`docs/242-audience-reading-paths-and-what-to-ignore.md`),
  - where to find adopter briefing artifacts (`artifacts/templates/adopter-briefing.md`, `.../adopter-slide-deck-outline.md`).

## Crisis usability (minimum)
- ☐ You can locate: the “what gets published” surface (`docs/PUBLIC_SURFACES.md`) and the court-proofing lane (`docs/43-...`).
- ☐ You can locate: the voter‑facing verification story + Person’s Path (`docs/track-a/VOTER_VERIFICATION.md`, `docs/track-a/PERSONS_PATH.md`) without needing cryptography background.
- ☐ You can locate: scope/claims + non-claims (`docs/166`, `docs/167`) without ambiguity about remote ballot return.
- ☐ You can locate: the maintainer/change protocol (`docs/150`) and the release gate (`docs/162`) without deep browsing.

## Pass/fail + logging
- ☐ PASS if the above is achievable in ≤60 minutes without guessing.
- ☐ FAIL if links are broken, the track boundary is unclear, or the reader can’t find the adopter briefing artifacts quickly.
- ☐ Log one row in `artifacts/registries/adopter-path-smoke-tests.csv` (include: time_minutes, blockers, and a pointer to the fix/ADR).
