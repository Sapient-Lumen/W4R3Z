# Meta: Program Stage-Gate Protocol (rev0478)

## Purpose
Use this protocol when a revision claims to make a top worthy Rust ecosystem program **more practical over time**, **closer to launch**, or **ready to widen beyond its current lane**.

This protocol is **not** the same as:
- broad ranking of seams;
- reference-architecture work that says what a program contains;
- charter work that says who owns it and where it lives first;
- or pilot scorecard work that judges a completed pilot after the fact.

It exists for a narrower question:

> what stage is this program actually in, what proof budget has it earned, what must happen before it widens, and what larger promises are still premature?

Read with:
- `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`

## Required stage-gate fields
Any new deepening note or major refresh that claims practical progression for a top macro-program should say all of the following explicitly:

1. **Current stage**
   - `stage0_kernel_proof`
   - `stage1_local_decision_proof`
   - `stage2_cross_lane_widening`
   - `stage3_stewarded_contract`

2. **Current allowed promises**
   - what narrow claims the program is allowed to make now;
   - what broad claims it is still forbidden to make.

3. **Current artifact burden**
   - what canonical artifact family must exist now;
   - what validator/doctor/checker path exists now;
   - what unsupported or partial states must be explicit now.

4. **Current proving grounds**
   - exact lane(s), tuple(s), or scenario(s) that are in scope now;
   - which nearby lanes are intentionally out of scope now.

5. **Current proof budget**
   - import budget;
   - promise budget;
   - consumer budget;
   - steward budget;
   - upstream-ask budget.

6. **Next gate**
   - what exact new evidence earns promotion;
   - what exact failure would cause fold, delay, or kill instead.

7. **Premature promises to refuse**
   - the most tempting larger build shape or claim that should still be rejected.

## Default interpretation
- Prefer `stage0_kernel_proof` when the program has a real kernel but no proven downstream decision yet.
- Prefer `stage1_local_decision_proof` when a real decision improved on one lane but broad widening would still be premature.
- Prefer `stage2_cross_lane_widening` when the work is now about accepted/partial/unsupported posture across multiple lanes or tuples.
- Prefer `stage3_stewarded_contract` only when the work has already left durable receipts and now honestly merits broader defaults, upstream asks, or institutional support.

## Minimum anti-cheating rules
- A good charter is **not** a stage gate.
- A good reference architecture is **not** a stage gate.
- A polished demo is **not** a stage gate.
- “Users would probably like this” is **not** a next gate.
- “We should standardize this eventually” is **not** proof that the upstream-ask budget has been earned.
- “This seems broadly useful” is **not** permission to skip explicit unsupported states.

## Preferred failure verbs
When a stage does not earn promotion, prefer one of these explicit outcomes:
- `deepen` — the program is right but the proof is not yet enough;
- `fold` — the useful part belongs under a stronger parent seam;
- `delay` — substrate motion or owner reality makes promotion dishonest right now;
- `kill` — the shape is wrong or the upkeep burden is too high for the leverage gained.

## Why this protocol exists
The repo already knew how to rank worthy contributions and how to describe their kernels and owners.
What it still needed was one small rule that future revisions can apply whenever a note starts sounding like “this is now ready to become bigger.”
This protocol is that rule.
