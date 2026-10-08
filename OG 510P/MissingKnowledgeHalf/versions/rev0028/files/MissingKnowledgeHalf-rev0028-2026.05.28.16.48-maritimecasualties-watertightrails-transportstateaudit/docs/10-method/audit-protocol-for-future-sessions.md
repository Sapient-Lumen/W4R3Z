# Audit protocol for future sessions

Before adding another batch of records, a future session may choose audit mode.

## Minimal audit pass

1. Run `make lint`.
2. Run `python tools/audit_cube.py`.
3. Read `CUBE-AUDIT-LEDGER.json`, `SCHEMA-DEBT-LEDGER.json`, `LOCATOR-DEBT-LEDGER.json`, and `REFACTOR-QUEUE.json`.
4. Pick exactly one repair surface: locator, schema, graph edges, pattern controls, source permanence, or second review.
5. Leave a revision receipt.

## Claim-level audit questions

- Does every claim cite a source or an explicitly typed supporting record?
- Is the locator durable enough for a future reader to re-find the evidence?
- Is the claim narrower than the story wants it to be?
- Does the claim confuse current status with final truth?
- Would an expert object that a missing caveat changes the conclusion?

## Pattern-level audit questions

- What records support this pattern?
- What would be a negative control?
- What would be a positive control?
- What counterexample would embarrass the pattern?
- What would demote, split, or narrow the pattern?

## Handoff audit questions

- Can a future worker tell what changed?
- Can they tell what did not change?
- Can they tell what remains unsafe to infer?
- Did this revision update `context-pack.json`, `SURFACE-STATUS.json`, and the receipt?

