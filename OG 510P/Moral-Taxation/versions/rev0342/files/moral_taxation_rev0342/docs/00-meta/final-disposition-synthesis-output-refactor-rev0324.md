# Final-disposition synthesis output refactor — rev0324

Rev0324 targets the highest-risk unfinished layer after precedence resolution: final output. Rev0323 could order selected routes, but an answer could still stop at a well-cited packet. This revision adds a checked synthesizer that turns ordered packets into a minimal disposition: what is blocked, what default move is available, who must be assigned, which sources/current laws must be refreshed, which quantitative checks remain, and why the answer cannot yet be finalized.

## What changed

- Added `tools/synthesize_disposition.py`.
- Added `tools/audit_disposition_synthesis.py`.
- Refactored `tools/answer_case.py` so final disposition is a delegated runtime layer, not inline prose.
- Added the disposition audit to `tools/run_semantic_audits.py` and the release audit target.
- Added `disposition_synthesis_audit_report_path` and disposition metrics to `cube-index.json`.

## Runtime guarantee

Disposition runtime status: final_disposition_synthesizer_invoked
Disposition answer packets: 122
Disposition packets: 122/122
Disposition ordered packets: 122/122
Disposition sequence-complete packets: 122/122
Hard-block recall: 897/897
Default-move route recall: 610/610
Actor-assignment route recall: 610/610
Source recall: 3311/3311
Currentness-check recall: 281/281
Quantitative-check recall: 401/401
No-go gate recall: 39/39
Cannot-finalize recall: 606/606

Dominant disposition counts: assign_real_actor_controller_or_beneficiary_before_liability: 9, block_pricing_or_offset_until_no_go_harm_is_resolved: 39, calibrate_revenue_or_compensation_after_gates: 1, check_current_sources_before_final_answer: 46, classify_and_apply_profile_default_moves_with_guardrails: 1, protect_floor_access_or_due_process_before_collection: 26.

## Substantive effect

The cube now has a runtime chain:

`facts → candidate routes → selected profiles → claim packets → precedence order → final disposition packet`

The final packet is deliberately not a legal answer. It is the archive's disciplined pre-answer: block prohibited shortcuts, apply route-backed defaults, assign the real accountable actor, refresh volatile law/source state, run quantitative checks where amounts or enforcement are being considered, and mark anything that cannot be finalized.

## Audit/refactor note

This was a runtime/refactor pass, not a registry expansion. No new routes, sources, axes, or policy families were added. The refactor removes final-output responsibility from `answer_case.py` and puts it behind a dedicated synthesizer plus an independent audit.


The audit target now removes Python bytecode/cache artifacts before manifest generation, preserving the release rule that runtime imports must not contaminate the package.

Answer-dependent semantic audits now share a single cached answer-packet payload during `tools/run_semantic_audits.py`, so the new final-output check does not multiply expensive answer generation across the release suite.

## Remaining frontier

The next riskiest work is to attach live jurisdiction/current-law and quantitative model adapters to the disposition packet. The packet now has explicit slots for those checks, but it does not perform them.
