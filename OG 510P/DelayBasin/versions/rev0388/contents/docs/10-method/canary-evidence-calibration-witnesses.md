# Canary-evidence calibration witnesses, bounded scorecards, ledger-audit refactor, and tail-ordinal guards

This is the compact successor surface for `OQ-0219`.

`rev0325` resolves `OQ-0219` by making scored reentry canaries count as evidence only when their scope, packet inputs, negative canaries, and differential gain are explicit.  A canary score may increase confidence in self-sufficiency, reveal false green, or trigger an ordinary followthrough item; it may not become a continuation review court, authority tribunal, or proof of minimality.

## Governed exact-token family

Family: `canary_evidence_state` / `WVF-0124`.

Allowed tokens:

- `baseline-failure-detected` — the null, stale, or landing-only baseline fails a currentness or boundary canary and therefore exposes real signal rather than ceremonial scoring.
- `packet-fit-sufficient` — the tested packet answers the current head, resolved question, live successor, derivative/canon boundary, and forbidden machinery questions within its declared scope.
- `negative-canary-clean` — the scorecard explicitly checks wrong-head, wrong-live-question, derivative-as-canon, review-court invention, quarantine loss, and minimality-overclaim failures.
- `differential-gain-observed` — a richer input packet improves evidence depth over a thinner packet without letting the richer packet become canonical by itself.
- `evidence-weighted-not-authority` — scorecards are admissible evidence for reentry sufficiency but do not adjudicate continuation authority or reopen closed history.
- `ledger-audited` — continuity ledger health is summarized by generated counts and latest-id witnesses so backlog pressure is visible without creating a ledger court.
- `tail-ordinal-guarded` — the open-question tail has a local heading/id continuity check so successor insertion errors cannot hide behind general registry validity.
- `mixed-canary-evidence` — several evidence channels are load-bearing and must remain bounded evidence, not governance.

Excluded synonyms:

- `continuation-review-court`
- `canary-authority-board`
- `minimality-certification-tribunal`
- `scorecard-canonization`
- `ledger-review-court`
- `ordinal-succession-senate`
- `behavioral-eval-sovereign`
- `self-sufficiency-notary`

## Evidence rule

A scored canary counts only inside its declared packet boundary.  The score is evidence when it names the input surfaces, expected answers, observed answers, score scale, and negative canaries.  It stops being evidence and becomes suspect if it claims archive minimality, canonical authority, or the right to reopen history without a separate open question and ordinary receipt.

## Protocol surface

`CANARY-PROTOCOL.json` records the admitted packet classes, required questions, score interpretation, and forbidden promotions.  The protocol is intentionally small: it tells an operator how to score reentry behavior, not who wins an authority dispute.

## Ledger-audit refactor

`LEDGER-AUDIT.json` and `docs/00-meta/ledger-audit.md` summarize the root continuity ledgers, latest IDs, state counts, and receipt-witness alignment.  This is an audit/refactor of the continuity-ledger subsystem: it makes the backlog legible without editing the semantic content of every historical ledger row.

## Tail-ordinal repair

The previous tail inserted `OQ-0219` under heading `175` after heading `168`.  `rev0325` repairs that to `169` and adds `tools/check_open_question_tail_ordinal_contract.py`, a deliberately local guard that checks the latest open-question tail rather than pretending to validate every historical heading convention.

## Guard set

- `tools/check_canary_evidence_witness_contract.py` ties this method, vocabulary family, current witness slot, receipt, protocol, ledger audit, and self-sufficiency assay together.
- `tools/check_canary_protocol_contract.py` verifies `CANARY-PROTOCOL.json` is current and non-authoritative.
- `tools/gen_ledger_audit.py` generates the ledger audit surfaces from the root ledgers.
- `tools/check_ledger_audit_contract.py` verifies latest-id, revision, state-count, and receipt-witness alignment.
- `tools/check_open_question_tail_ordinal_contract.py` catches tail heading jumps and latest OQ successor mistakes.
- `tools/check_llm_runbook_current_cue_alignment.py` keeps the practical reentry cue aligned with the current receipt.
- `tools/check_current_witness_receipt_slot.py` keeps the current witness family explicit in the receipt.

## Successor

`OQ-0220` asks when generated ledger-audit summaries should refactor continuity memory without becoming a ledger review court.
