# rev0118 — transition choice-proof spine

## Audit finding

rev0117 created the first public `TransitionResult` surface for `NeedChoice / Rejected / Committed`, but the committed result still made callers chase the causal `ActionReceiptRecord` to recover the selected-choice proof chain. That was a small but important split in the mission spine: the transition API could tell a caller that one receipt was created, while the page proof and APNAP queue-entry proof still lived primarily behind the journal surface.

For search, agents, branch explorers, and replay UIs, the transition boundary itself should carry the proof that the selected `LegalAction` came from the same typed choice request and global APNAP queue entry the receipt claims. Otherwise the public reducer seam is thinner than the evidence it produces.

## Refactor

`TransitionResult` now carries:

- `LegalActionPageLocation page_location`
- `ChoiceQueueLocation queue_location`
- `choice_page_location_checked`
- `choice_queue_location_checked`
- `choice_queue_location_found`

Committed transitions populate these before semantic mutation and before appending the causal receipt. Preflight rejections keep the proof sentinels false, preserving the nonmutating rejection contract from rev0117.

The convenience predicates make the contract executable:

- `has_checked_page_location()`
- `has_checked_queue_location()`
- `committed_with_choice_proofs()`

A committed transition is now easy to audit without walking the journal: it must have one causal receipt and both checked proof surfaces. The receipt still remains the durable journal row, but `TransitionResult` is now a complete immediate response for the chosen transition.

## Guardrail

`tools/audit_datacube.py` gained `audit_transition_result_wiring(...)`. The probe ties together the public type surface, the mutation boundary, the new regression test, the rules ledger, and this architecture note so future revisions cannot accidentally strip the proof surfaces from the transition API while leaving receipts intact.

## Scope retained

This is not yet a full staged payment/cost transaction kernel. It deliberately keeps the rev0117 wrapper around the existing `LegalAction` mutation body. The next semantic step remains moving a paid cast or activated ability into a staged transaction result with explicit prepay, lock, pay, place-on-stack, and receipt phases.
