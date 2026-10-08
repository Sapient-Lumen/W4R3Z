# rev0181 — Paid Action Commit State Hash Audit

## Mission pressure

The heart of MTGSim remains trusted transitions: one authoritative state plus one explicit legal choice should produce one deterministic next state and enough typed evidence to validate, replay, branch, fuzz, search, and explain it. The riskiest remaining surface after rev0180 was the paid-action transaction seam: rollback rows already proved that failed staged mutations did not leak, but committed rows did not prove the actual physical transition they represented.

## Online research used

This pass rechecked the official Wizards rules surface online. The current observed Comprehensive Rules metadata remains effective 2026-06-19. The relevant pressure comes from the casting and activation procedures, plus the illegal-action reversal rule: spells and activated abilities are announced/put on the stack through ordered substeps, and an action that cannot legally complete is reversed with payments canceled. The revision records URLs and observations only; official rules documents remain excluded from the datacube.

External anchors recorded for future private refresh/diff work:

- Official rules page: https://magic.wizards.com/en/rules
- Current observed TXT: https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.txt
- Current observed PDF: https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.pdf

## Code-bearing change

rev0181 turns a quiet audit hole into a fail-closed transaction receipt:

- `PaidActionTransactionRecord` advances to schema version 5.
- Committed paid-action rows now bind `physical_state_hash_before` to the caller StateCore hash captured before the staged paid-action body, and `physical_state_hash_after` to the adopted post-action StateCore hash.
- Rollback rows preserve the existing equality proof: both physical hashes bind to the unchanged committed branch after the failed staged attempt.
- `paid_action_transaction_record_hash` now uses the v5 domain tag so stale v4 rows cannot masquerade as current evidence.
- Game-state validation rejects committed paid-action records with missing, zero, or equal pre/post physical hashes.
- The paid-action journal verifier now rejects stale transaction schemas and committed rows that do not expose a distinct nonzero physical transition.
- C++ tests corrupt both in-memory validation records and exported journal text to prove the new guard fails closed.

## Refactor/audit substance

The refactor makes the transaction helper carry the pre-action StateCore hash into the staged commit path rather than sampling only after mutation. This matters because the most important question for a committed paid action is not merely whether there is a terminal receipt; it is whether that receipt proves the actual state transition that was adopted. A committed spell/activation now has a before/after StateCore bridge. A failed spell/activation still has a no-leak rollback bridge.

This revision also corrected a cloudtainer waste pattern in the test-matrix planner: full matrix plans were being appended wholesale into `reports/harness/test_matrix_plan_history.jsonl`, duplicating case/rule/tag/work-unit inventories on every run. The planner now appends compact history rows while preserving full latest plans in normal report JSON files.

## Remaining risk

This does not complete the full announcement/cost system. Variable costs, cost increases/reductions, spending restrictions, alternate costs, interactive cancellation choices, and broader APNAP/replacement interaction around payments remain future work. The valuable step here is that the existing staged paid-action boundary now has a truthful commit proof before those harder semantics are expanded.

## Validation evidence

- C++ release tests: 347/347
- Scenario suite: 93/93 with 566 assertions
- Broad fuzz: 12/12
- Risk-seam fuzz: 12/12
- Rule coverage: 0 errors / 0 warnings
- Card catalog: 56 cards

Datacube: `MTGSim-rev0181-2026.07.08.05.23-paidstatehashaudit.zip`
