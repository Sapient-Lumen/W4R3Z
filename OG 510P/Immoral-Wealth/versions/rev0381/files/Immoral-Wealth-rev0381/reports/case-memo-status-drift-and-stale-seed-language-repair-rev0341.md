---
revision_current: rev0355
status: audit_report
claim_kind: case_front_door_refactor
route_role: case_work_core
canonical_anchor: false
route_refs:
- case_work_core
- evidence_lineage_core
source_refresh_due: 2026-09-30
---

# rev0341 case-memo status drift and stale seed-language repair

## Why this was risky

rev0332 closed true seed scoreboards, rev0337 closed active seed-calibration labels, and rev0340 repaired memo-source lineage. But the front-door prose still had a hidden contradiction: active case memos and active scoreboard notes could still call themselves `seed`, `seed/proxy`, `seed stress`, or `active seed`.

That is not just cosmetic. A reviewer opening the memo could treat a hardened active case as a disposable seed illustration, while the validator and scoreboards treated it as an active operational proof burden. The risk was highest for portfolio foundation cases, remedy-operability cases, and rental-market-power cases because those are often read directly as narrative memos before the JSON scoreboard is inspected.

## What changed

- Repaired stale seed-status language in active case memos.
- Repaired stale seed/proxy notes inside active scoreboards without changing verdicts, blocked gates, refresh dates, evidence-debt rows, or source IDs.
- Preserved the substantive caution by using `bounded active`, `bounded active proxy`, or `bounded active stress` language where a case is active but not a full jurisdictional certification.
- Added a validator invariant so stale seed-status phrases cannot return to active case memos or active scoreboard narratives.

## Counts

- Active files with stale seed-status language before repair: **39**
- Case memo files repaired: **11**
- Scoreboard files repaired: **28**
- Memo text replacements: **11**
- Scoreboard text replacements: **39**
- Remaining active files with stale seed-status language: **0**

## Substantive interpretation

This pass does not promote any verdict or relax any blocked gate. It repairs the opposite problem: active cases that remain blocked for evidence should say they are active-but-bounded, not seed. That preserves caution while preventing the cube from undermining its own completion work.
