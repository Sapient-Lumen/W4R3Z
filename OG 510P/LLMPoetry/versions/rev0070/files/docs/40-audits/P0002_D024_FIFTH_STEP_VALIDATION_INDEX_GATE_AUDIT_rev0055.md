# P0002-D024 Fifth Step / Validation-Index Gate Audit — rev0055

## Literary action

D023 was cold-reviewed and not promoted. Its failure was over-neat absence: the blank official stamping field became a solved concept. D024 moves the pressure to the physical mark named by the same NOAA benchmark sheet: a chiseled square cut into the fifth granite step at the south entrance of the U.S. Customs House, above the sidewalk, while the tide staff remains elsewhere behind the office.

## New current head

`poems/P0002/draft_024.md` — **Cut in the Fifth Step**

Status: same-turn unjudged; not admitted; not evidence-ready; not an anthology candidate; not a reader response; no live/current NOAA water-level value claimed.

## Source pressure

The NOAA benchmark sheet supplies the blank-stamping/designation context, chiseled square, fifth granite step, south entrance, above-sidewalk setting, and staff behind the Inspection Office. NOAA datum definitions keep the first-staff Station Datum pressure below the surface. The local runtime gap remains absence-of-capture only.

## Audit/refactor

Incoming rev0054 had a compact drift fault: `VALIDATION_INDEX.json` still had a `description` describing P0002-D022 as current even though P0002-D023 was current. Rev0055 updates that surface and adds a blocking `validation_index_description_mentions_current_head` check in `tools/check_release_surfaces.py`. `tools/check_surface_freshness.py` now also treats `VALIDATION_INDEX.json` as a current-facing surface.

`tools/check_external_material_pressure.py` now supports `fifth_step_reanchor_policy`, which requires the fifth-step/chiseled-square anchors, blocks D023 designation/blank-field thesis regression, and caps body numerics at zero.

## Non-claim

This audit records source traceability and drift prevention only. It is not poem quality evidence.
