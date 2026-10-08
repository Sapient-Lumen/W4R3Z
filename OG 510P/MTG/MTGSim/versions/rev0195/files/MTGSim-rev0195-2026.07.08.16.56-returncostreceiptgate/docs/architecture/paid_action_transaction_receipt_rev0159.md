# rev0159 Paid Action Transaction Receipt

## Mission fit

The mission remains trusted transitions. A consumer should not have to infer whether a paid action committed by scanning declaration records, payment records, stack-placement records, and generic log events. rev0159 adds an explicit terminal row: `PaidActionTransactionRecord`.

## Executable shape

The modeled paid stack-action path now has this causal shape:

1. move/announce into the staged stack context;
2. lock modeled choices and declaration/cost payload;
3. pay modeled mana and deterministic nonmana costs;
4. record stack placement as the phase receipt;
5. record a terminal committed `PaidActionTransactionRecord`.

The committed transaction receipt links to the stack-placement row and, for paid spells, the declaration/cost-lock row. It copies the declaration hash, stack-object entry sequence, choice-lock sequence, payment phase ranges, and ordering flags, then seals the transaction identity with `paid_action_transaction_record_hash`.

Rollback rows are emitted for direct paid-cast failures inside the staged transaction body. They do not link committed placement/declaration rows. Instead, they preserve speculative event/record counts, `physical_state_hash_before`, `physical_state_hash_after`, and a boolean proof that the caller's physical state was restored.

## Why this was higher priority than more doctrine

rev0158 made declaration/cost lock visible, but left success as an inference: if a stack placement existed and a declaration backlink matched, the caller could guess the paid action committed. That is brittle for replay, agent training data, and future branch trimming. The riskiest missing piece was one terminal causal receipt per modeled paid-action transaction.

## Audit/refactor

`test_stack_placement_record_retains_priority_and_links_spell_and_ability` used to assert that the last typed event was `StackPlacement`. rev0159 intentionally breaks that assumption. The test now locates stack placement as a phase receipt and separately requires the final typed event to be `PaidActionTransaction`.

## Online research note

Wizards' official rules page identifies the Comprehensive Rules as the reference document for Magic's rules and corner cases, and links DOCX/PDF/TXT downloads. The observed current TXT download in this session is effective 2026-06-19:

- https://magic.wizards.com/en/rules
- https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.txt

The datacube still does not bundle official rules text. The local metadata ledger remains pinned to the packaged 2026-04-17 source until a dedicated rules-refresh/diff revision.

## Remaining risk

The next risky seam is not a bigger registry. It is broadening the same transaction receipt model to variable costs, alternate/additional costs, X costs, player-chosen payment plans, and rollback receipts for activated/loyalty paths that currently fail at preflight before entering the staged body.
