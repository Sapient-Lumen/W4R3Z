# DelayBasin debt burn-down and decay audit — rev0378 working overlay

Source working overlay: `DelayBasin-rev0377-2026.06.17.18.24-riskrepair-lintreadonly-hotcue18-scorerkit.zip`  
Canonical state still named inside the cube: `rev0374` / `DelayBasin-rev0374-2026.06.16.13.45-preanswerclamp-scoretime-leakcut.zip`  
Status: **tested cloudtainer working overlay, not a canonical DelayBasin promotion**.

## Result

This pass spent its effort on live work rather than adding another registry family:

1. it semantically reviewed and closed sixteen old four-ledger waiting cohorts (`rev0178` through `rev0193`);
2. it completed the partially transitioned `rev0177` cohort and expired eleven older cooling retrospectives whose paired obligations were already retired;
3. it repaired contradictory duplicate-state fields and made those contradictions executable guard failures;
4. it replaced the zero-headroom tripwire with a sixteen-row admission reserve; and
5. it actually reviewed the three overdue decay-watch entries, narrowed their claims, renewed their horizons, and prevented `explicitly-overdue` from persisting indefinitely.

The live sets moved from `180 / 180 / 180 / 180` to:

| Surface | Before | After | Headroom | Admission reserve |
|---|---:|---:|---:|---:|
| `FOLLOWTHROUGH-QUEUE.json` | 180 queued | 164 queued | 16 | 16 |
| `ASSUMPTION-LEDGER.json` | 180 active | 164 active | 16 | 16 |
| `OBLIGATION-LEDGER.json` | 180 open | 163 open | 17 | 16 |
| `RETROSPECTIVE-QUEUE.json` | 180 cooling | 152 cooling | 28 | 16 |

This is a reduction of **77 live rows**. Historical rows and their candidate text remain in place; only their live state changed.

## 1. Bounded semantic burn-down

### Sixteen complete cohorts

The audited range was deliberately bounded to `rev0178`–`rev0193`. Each revision emitted a followthrough, assumption, obligation, and retrospective around a compact mechanism that was supposed either to remain sufficient or to be superseded by stronger machinery. The current tree now provides an explicit answer:

- claim ceiling, polarity, expectation, agreement, overlap, and verbosity remain compact GPUstorming contract controls rather than standing courts;
- successor-route, basis-anchor, receipt-freshness, and question-posture pressure is handled by direct executable checks;
- frontier ticket, validation index, innovation packet, compact surface bundle, and replay capsule remain bounded checked surfaces;
- the old “one receipt-level status witness is enough” assumption was superseded in the opposite direction: explicit status/currentness machinery was in fact adopted.

Those outcomes discharge the waiting loops. Keeping all sixty-four rows live after the answer was already visible was sediment, not caution.

### Partial and orphaned cohorts

`FT-0079` and `AS-0076` were retired in `rev0370`, but `OB-0072` and `RT-0069` remained live. This pass closes the remaining `rev0177` residue.

`RT-0058` through `RT-0068` remained `cooling` even though each same-origin obligation (`OB-0061` through `OB-0071`) had already been retired. All eleven are now expired. A new cross-ledger guard rejects this condition in future.

## 2. State truth is singular again

The audit found twelve stale compatibility fields across eleven already-transitioned rows:

- `followthrough_state` still said `queued` on two expired followthroughs;
- `assumption_state` still said `active` on two retired assumptions;
- `obligation_state` still said `open` on two retired obligations;
- `retrospective_state` and one `cooling_state` still said `cooling` on expired retrospectives.

The canonical `state` field had been correct, but public consumers could receive contradictory answers depending on which field they read. The rows are repaired, and `tools/check_ledger_debt_guard.py` now rejects any present mirror that disagrees with canonical state.

## 3. The debt guard now preserves working room

The previous guard failed only above 180 rows. That allowed every live set to sit at 180 with no room for the next legitimate tail. The policy now requires **minimum headroom of 16**:

- nominal historical budget: `180`;
- admission limit: `164`;
- a new live row must be paired with enough retirement work to preserve the reserve.

`tools/ledger_debt_policy_lib.py` is now the source for the budget, reserve, state mirrors, and live-state semantics. `tools/archive_economy_audit_lib.py` no longer carries a second hard-coded copy of the four `180` budgets.

This is not an instruction to retire rows mechanically. It is an executable refusal to let “we can clean it later” consume all operational headroom again.

## 4. Decay patrol was forced to perform a review

`DW-0001`, `DW-0002`, and `DW-0003` had remained `explicitly-overdue` after their April 2026 horizon. That exposed a design failure: the registry could advertise overdue work forever while still passing lint.

The review outcomes are now explicit:

- **DW-0001 / bounded constitutional state:** renewed to September 2026, but narrowed. Internal archive repairs support the utility of bounded reentry state; they do not establish minimality or prove prior-matching causation. OQ-0266 remains the external test.
- **DW-0002 / promotion contracts:** renewed to September 2026 only in compact form. A new per-revision promotion object without a real status change is now treated as bloat, not rigor.
- **DW-0003 / decay patrol:** renewed to September 2026 with a repaired mechanism. `explicitly-overdue` now has at most one calendar month of grace before review, renewal, demotion, or retirement is required.

After regeneration, `context-pack.json` carries no overdue decay-watch rows.

## 5. Focused refactor

The ledger guard and archive-economy audit now share more than the headline budget:

- state mirror keys live in `tools/ledger_debt_policy_lib.py`;
- live-retrospective / paired-obligation consistency is a shared helper;
- archive-economy evidence reports headroom, reserve, admission limit, mirror mismatch count, and orphaned retrospective count;
- risk flags fire when the admission reserve is breached, not only when the nominal maximum has already been consumed.

This closes a gap left in rev0377: the main live-debt snapshot used shared policy, but the completed-refactor summary still duplicated four hard-coded `180` values.

## Remaining highest risk

The central mission object is still absent: a genuinely clean OQ-0266 response, chronology-valid distinct-custodian record, and separate post-response score sheet. This pass deliberately did not simulate or manufacture that evidence.

The live ledgers are healthier, not solved. Their oldest remaining live cohort is still `rev0194`, 180 canonical revisions behind the current head. The next semantic burn-down should continue from that boundary only after checking current executable support, not by age alone.

## Non-claim

This overlay is not a clean external replay, independent certification, canonical release, proof that every retired row was false, authority to delete history, or proof that the sixteen-row reserve is globally optimal.
