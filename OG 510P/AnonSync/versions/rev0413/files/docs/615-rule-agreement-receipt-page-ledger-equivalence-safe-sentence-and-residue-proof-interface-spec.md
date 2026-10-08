# Rule agreement receipt page — ledger equivalence, safe sentence, and residue-proof interface spec

## Purpose

The archive already treats serious mutations and reviews as receipted.
What it still lacked was one small durable artifact for the interpretive event:

> we decided what this exclusion rule really means across peers, and we want later readers to inherit that exact agreement ceiling instead of re-assuming it.

## Core decision

AnonSync must issue one **Rule agreement receipt** whenever an exclusion or ignore ledger is reviewed for cross-peer meaning.

## Receipt contents

The receipt must preserve:

- rule identity and selector snapshot at review time
- rule family and local-effect class
- compared peer set
- ledger-equivalence verdict
- strongest safe sentence adopted
- stronger invalidated sentence explicitly rejected
- drift or residue rows that blocked the upgrade
- next proof page, if any
- reviewer and timestamp

## Public object

### Rule agreement receipt page

Fields:

- `rule_agreement_receipt_id`
- `rule_ref`
- `selector_snapshot`
- `rule_family`
- `comparison_peer_set_ref`
- `ledger_equivalence_verdict`
- `safe_sentence`
- `invalidated_sentence`
- `blocking_residue_rows[]`
- `next_page_refs[]`
- `reviewed_at`
- `reviewed_by`

## Compact row contract

A compact receipt row should preserve this order:

1. rule label
2. selector snapshot
3. ledger-equivalence verdict
4. safe sentence
5. rejected stronger sentence

Example:

```text
Ignore PDFs     *.pdf     ambiguous     this seat ignores matching PDFs for local indexing and size accounting     every peer will ignore matching PDFs the same way
```
