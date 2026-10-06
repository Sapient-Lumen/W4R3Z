# Revision receipt contract

This surface defines the minimum contract for `REVISION-RECEIPT.json`.

## Required fields

- `project`
- `revision`
- `previous_revision`
- `summary`
- `move_classes`
- `canon_additions`
- `hot_current_supports`
  - must be a non-empty, unique, exact-order subset of `canon_additions`, contain no more than 18 surfaces, and carry the compact landing-path support set rather than the full trace
- `quarantine_additions`
- `refs_used`
- `checks_passed`
- `touched_surfaces`
- `packaged_release`
- `basis_witness`
  - must include `expected_head`, `observed_head`, `basis_surfaces`, `session_provenance`, `basis_state`, `basis_anchor_precision`, `basis_omission_basis`, and `repair`
- `scope_witness`
- `authorship_witness`
- `status_witness`
- `reentry_cue_witness`
- `retrospective_write_witness`
- `followthrough_witness`
- `assumption_witness`
- `obligation_witness`
- `applicability_witness`
- `foreign_pressure_witness`
- `transfer_witness`
- `resolution_witness`
- `reasoning_firebreak_witness`
- `vocabulary_witness`
- `counterfactual_shadow`
- `receipt_freshness_witness`
- `question_posture_witness`

## Contract discipline

The receipt is not a second changelog.
It is the smallest machine-readable object that says:
- what transition happened,
- which bounded support set belongs on the default landing path while fuller trace remains in receipts and ledgers,
- what status moved,
- what exact lane mapping distinguished admitted decision, materialized execution, and frozen public citation posture for the current revision,
- what basis the transition honestly depended on,
- what evidence pressure mattered,
- and which checks made the transition admissible.
- what still-live remainder, if any, was explicitly queued, handed off, or expired rather than merely implied.
- what live supporting assumption, if any, the revision was still spending and what would invalidate it.
- what support debt, if any, still remained open before a tolerated move should inherit stronger authority and what discharge path would retire that debt.
- what reusable carry or import pattern, if any, was actually fit to fire here, what nearby non-fit slice stayed live, and what negative-transfer budget or gate-closure rule kept reuse authority narrow.
- what hot-path candidate, if any, was preserved into cooled queue state rather than admitted directly, how it is cooling, and what colder adjudication still governs it.
- what exact neighboring datacubes and source packets, if any, materially shaped the admitted import and what bounded take or non-take followed from them.
- what broad comparison pass, if any, already decided across several datacubes, what was taken, what stayed supporting-only or rejected, where any admitted result landed, and what transfer question remains open.
- what object, if any, just stopped being live, why it closed, what replaced it if anything, and what would reopen it.
- what public extract, if any, was admitted while a larger trace or scratch surface stayed withheld, what role that withheld surface is still allowed to play, and what would force thicker exposure.
- what controlled witness-state families, if any, materially governed the revision, what exact tokens are allowed for those families, what surfaces those tokens govern, and what fail-closed repair follows if the vocabulary starts to drift.
- what terse current-revision receipt keys, if any, are supposed to summarize the current packaged bundle or current comparison rows, and what freshness witness keeps those short keys from silently carrying forward stale bundle stems, timestamps, or comparison ids.
- what already-resolved open questions, if any, had to be synchronized across registry, trajectory, and frontier-selection surfaces so stale unresolved posture did not remain operator-visible after durable closure.

## Failure modes

A revision receipt fails if it:
- omits the move classes that made the revision admissible,
- hides canon or quarantine status changes,
- regrows `hot_current_supports` beyond the 18-surface burden budget, points it outside canon, or lets landing cues differ from it,
- lists refs with no corresponding archive-native consequence,
- or bloats into narrative recap.
- or omits the expected basis, observed basis, basis-anchor precision, basis-omission basis when stronger underliers were not reread, or fail-closed repair posture when current-head grounding mattered.
- or labels `basis_witness.basis_state` as `current` even though the expected head and observed reread head no longer match exactly.
- or omits the active request, exact target, ambient exclusions, or fail-closed repair posture when exact scope mattered.
- or omits the initiating lane, draft-authorship posture, approval lane, execution lane, review or compensating-control lane, autonomy posture, lane-collapse state, or fail-closed repair posture when collaborative authority separation mattered.
- or omits the candidate-or-explicit-absence surface, decision surface and decision-state token, execution surface and execution-state token, frozen-public surface and public-state token, durable status surface, or mismatch consequence when admitted/executed/frozen-public lane separation materially mattered.
- or omits the surface lineage, primary landing surface, supporting durable cues, excluded stale or broken paths, cue-state classification, or fail-closed repair posture when latest-path landing mattered.
- or omits the candidate surface, cooldown window, off-path adjudication family, supersession link, cooling-state classification, or admission/expiry posture when a hot-path candidate is being preserved but not directly admitted.
- or omits the blocked or handed-off objective, local surface, followthrough-state classification, blocker or boundary, next proof surface, receiving surface, or expiry/reclaim repair posture when live remainder work was narrowed, deferred, or handed off.
- or omits the live assumption, governing scope, supporting surfaces, invalidation triggers, assumption-state classification, or fail-closed repair posture when the revision still depended on an undischarge assumption.
- or omits the target surface, missing support, current support family, discharge path, obligation-state classification, or fail-closed repair posture when the revision keeps a move live under explicit support debt.
- or omits the carry object, fit conditions, baseline family, non-fit slice, matched budget, negative-transfer budget, applicability-state classification, or fail-closed repair posture when the revision is granting standing reuse authority to a carry object or import pattern beyond one vivid local payoff.
- or omits the exact neighboring datacubes or source packets, extracted pressure, local gap, bounded take, explicit non-take, assimilation-state classification, or fail-closed repair posture when the revision materially depended on foreign datacube pressure.
- or omits the reviewed datacubes, reviewed pattern, disposition, local gap, bounded take if any, explicit non-take, anchor surfaces, open transfer question, or fail-closed repair posture when the revision materially depended on a multi-datacube comparison pass.
- or omits the closed object, prior state, closure reason, successor surface or explicit absence, reopen trigger, closure-state classification, or fail-closed repair posture when the revision is also establishing that something stopped being live.
- or omits the judged property, public extract, withheld trace surface, allowed role, exposure or reinclusion consequence, trace-state classification, or fail-closed repair posture when the revision is explicitly relying on reasoning-firebreak / public-extract discipline.
- or omits the witness vocabulary surface, the controlled state families, the governed target surfaces, the excluded near-synonym family, the comparability budget, the vocabulary-state classification, or the fail-closed repair posture when the revision materially depends on compact public state tokens staying stable across receipt and durable-ledger surfaces.
- or omits the nearby rejected move when a substantial revision actually had one.
- or omits the current packaged bundle filename, manifest timestamp token, receipt timestamp token, bundle-stem suffix relation, current comparison ids when present, freshness-state classification, or fail-closed repair posture when terse receipt currentness keys materially matter.
- or omits the resolution surface, registry surface, trajectory surface, synced resolved-question ids, frontier selection rule, posture-state classification, or fail-closed repair posture when already-resolved open questions had to stop appearing as unresolved or current frontier on operator-facing discovery surfaces.

## Current governing move

- `MV-0011` — `issue-receipt`
- `MV-0012` — `shadow-compare`
