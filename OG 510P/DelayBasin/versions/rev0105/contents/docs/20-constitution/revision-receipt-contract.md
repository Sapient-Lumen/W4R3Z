# Revision receipt contract

This surface defines the minimum contract for `REVISION-RECEIPT.json`.

## Required fields

- `project`
- `revision`
- `previous_revision`
- `summary`
- `move_classes`
- `canon_additions`
- `quarantine_additions`
- `refs_used`
- `checks_passed`
- `touched_surfaces`
- `packaged_release`
- `basis_witness`
- `scope_witness`
- `authorship_witness`
- `reentry_cue_witness`
- `retrospective_write_witness`
- `followthrough_witness`
- `assumption_witness`
- `foreign_pressure_witness`
- `resolution_witness`
- `reasoning_firebreak_witness`
- `counterfactual_shadow`

## Contract discipline

The receipt is not a second changelog.
It is the smallest machine-readable object that says:
- what transition happened,
- what status moved,
- what basis the transition honestly depended on,
- what evidence pressure mattered,
- and which checks made the transition admissible.
- what still-live remainder, if any, was explicitly queued, handed off, or expired rather than merely implied.
- what live supporting assumption, if any, the revision was still spending and what would invalidate it.
- what hot-path candidate, if any, was preserved into cooled queue state rather than admitted directly, how it is cooling, and what colder adjudication still governs it.
- what exact neighboring datacubes and source packets, if any, materially shaped the admitted import and what bounded take or non-take followed from them.
- what object, if any, just stopped being live, why it closed, what replaced it if anything, and what would reopen it.
- what public extract, if any, was admitted while a larger trace or scratch surface stayed withheld, what role that withheld surface is still allowed to play, and what would force thicker exposure.

## Failure modes

A revision receipt fails if it:
- omits the move classes that made the revision admissible,
- hides canon or quarantine status changes,
- lists refs with no corresponding archive-native consequence,
- or bloats into narrative recap.
- or omits the expected basis, observed basis, or fail-closed repair posture when current-head grounding mattered.
- or omits the active request, exact target, ambient exclusions, or fail-closed repair posture when exact scope mattered.
- or omits the initiating lane, draft-authorship posture, approval lane, execution lane, review or compensating-control lane, autonomy posture, lane-collapse state, or fail-closed repair posture when collaborative authority separation mattered.
- or omits the surface lineage, primary landing surface, supporting durable cues, excluded stale or broken paths, cue-state classification, or fail-closed repair posture when latest-path landing mattered.
- or omits the candidate surface, cooldown window, off-path adjudication family, supersession link, cooling-state classification, or admission/expiry posture when a hot-path candidate is being preserved but not directly admitted.
- or omits the blocked or handed-off objective, local surface, followthrough-state classification, blocker or boundary, next proof surface, receiving surface, or expiry/reclaim repair posture when live remainder work was narrowed, deferred, or handed off.
- or omits the live assumption, governing scope, supporting surfaces, invalidation triggers, assumption-state classification, or fail-closed repair posture when the revision still depended on an undischarge assumption.
- or omits the exact neighboring datacubes or source packets, extracted pressure, local gap, bounded take, explicit non-take, assimilation-state classification, or fail-closed repair posture when the revision materially depended on foreign datacube pressure.
- or omits the closed object, prior state, closure reason, successor surface or explicit absence, reopen trigger, closure-state classification, or fail-closed repair posture when the revision is also establishing that something stopped being live.
- or omits the judged property, public extract, withheld trace surface, allowed role, exposure or reinclusion consequence, trace-state classification, or fail-closed repair posture when the revision is explicitly relying on reasoning-firebreak / public-extract discipline.
- or omits the nearby rejected move when a substantial revision actually had one.

## Current governing move

- `MV-0011` — `issue-receipt`
- `MV-0012` — `shadow-compare`
