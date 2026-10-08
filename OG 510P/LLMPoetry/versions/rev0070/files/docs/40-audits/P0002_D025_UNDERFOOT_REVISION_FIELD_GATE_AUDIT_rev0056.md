# P0002-D025 Underfoot / Revision-Field Gate Audit — rev0056

## Literary action

D024 was cold-reviewed and not promoted. Its fifth-step/chiseled-square object was real, but its close — `A dry cut / for a wet count` — turned the mark into a tidy thesis. D025 keeps the NOAA fifth-step pressure but follows the more vulnerable body-scale hinge: a foot can cross a water-reference mark without reading it.

## New current head

`poems/P0002/draft_025.md` — **Underfoot**

Status: same-turn unjudged; not admitted; not evidence-ready; not an anthology candidate; not a reader response; no live/current NOAA water-level value claimed.

## Source pressure

NOAA's benchmark sheet supplies the fifth granite step, south entrance of the U.S. Customs House, State Street, above-sidewalk setting, chiseled-square mark, and tide gage/staff behind the Inspection Office. NOAA datum/API sources remain in packet context for the first-zero and no-live-value boundaries.

## Audit/refactor

The incoming rev0055 package exposed a compact but serious drift fault: `STATE.json` had `revision: rev0055` while `current_revision` still said `rev0054`; `RELEASE_MANIFEST.json` could also preserve stale `current_draft` / `current_packet` fields while still passing headline validation.

Rev0056 repairs those fields and adds blocking gates: `state_current_revision_matches_revision`, `release_manifest_current_draft_field_matches_state`, `release_manifest_current_packet_field_matches_state`, and `shoe_passage_reanchor_policy`.

These checks are not poem-quality checks. They prevent a future operator from trusting a compact current/release surface that points to the wrong revision or packet.

## Non-claim

This audit records source traceability and drift prevention only. It is not poem quality evidence.
